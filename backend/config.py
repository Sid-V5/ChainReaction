import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file from project root or current working dir
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "ChainReaction"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # MongoDB Settings (Document Model - AIM3141)
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "chainreaction")

    # Neo4j Settings (Graph Model - AIM3141)
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "chainreaction123")

    # Redis Settings (Key-Value & Pub/Sub - AIM3141)
    REDIS_URI: str = os.getenv("REDIS_URI", "redis://localhost:6379/0")

    # Optional GitHub Token
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")

    # Server Settings
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8001"))

settings = Settings()
