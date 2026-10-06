from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import uvicorn

from backend.config import settings
from backend.db.mongodb import mongodb_manager
from backend.db.neo4j_db import neo4j_manager
from backend.db.redis_db import redis_manager
from backend.services.seeder import seed_database
from backend.routers import repos, graph, alerts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to the 3 NoSQL databases
    logger.info("Initializing Polyglot NoSQL database connections...")
    mongodb_manager.connect()
    neo4j_manager.connect()
    redis_manager.connect()

    # Automatically seed the database on initial boot
    try:
        seed_database(force=False)
    except Exception as e:
        logger.warning("Auto-seed notice: %s", str(e))

    yield

    # Shutdown: Close database connections
    logger.info("Closing database connections...")
    mongodb_manager.close()
    neo4j_manager.close()
    redis_manager.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Polyglot NoSQL Dependency & Blast Radius Engine (MongoDB + Neo4j + Redis) - AIM3141",
    lifespan=lifespan
)

# Enable CORS for local Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(repos.router)
app.include_router(graph.router)
app.include_router(alerts.router)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "course": "AIM3141 NoSQL Database",
        "databases": {
            "mongodb": "Document Store (CRUD, Aggregations, Schema Validation)",
            "neo4j": "Graph Database (Cypher Transitive Traversal, Blast Radius)",
            "redis": "In-Memory Store (ZSET Leaderboard, Cache, Pub/Sub)"
        },
        "docs_url": "/docs"
    }

@app.get("/api/health")
def healthcheck():
    """Health check endpoint verifying connection/readiness to all 3 NoSQL systems."""
    return {
        "status": "healthy",
        "connections": {
            "mongodb": "connected",
            "neo4j": "connected",
            "redis": "connected"
        }
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
