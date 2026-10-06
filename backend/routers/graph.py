from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
from backend.db.neo4j_db import neo4j_manager
from backend.db.redis_db import redis_manager

router = APIRouter(prefix="/api/graph", tags=["Graph & Blast Radius"])

class BreakingChangeRequest(BaseModel):
    package: str

@router.get("", response_model=Dict[str, Any])
def get_graph_elements():
    """
    Returns the complete node and edge topology from Neo4j
    formatted for interactive Cytoscape.js rendering.
    """
    try:
        cache_key = "cache:graph:full"
        cached = redis_manager.get_cache(cache_key)
        if cached:
            return cached
    except Exception:
        pass

    try:
        graph_data = neo4j_manager.get_full_graph()
    except Exception:
        graph_data = neo4j_manager._build_fallback_graph()

    try:
        redis_manager.set_cache(cache_key, graph_data, ttl_seconds=60)
    except Exception:
        pass

    return graph_data

@router.get("/blast-radius")
def query_blast_radius(
    package: str = Query(..., description="Target open-source package name e.g. log4j-core, requests, qs"),
    depth: int = Query(5, ge=1, le=10)
):
    """
    AIM3141 Graph Traversal & Redis Caching (Lecture 35):
    Executes a Cypher variable-length path traversal query (*1..depth) in Neo4j.
    Results are cached in Redis to achieve sub-millisecond repeat latency.
    """
    cache_key = f"cache:blast:{package.lower()}:{depth}"
    cached = redis_manager.get_cache(cache_key)
    if cached:
        cached["cache_hit"] = True
        return cached

    result = neo4j_manager.get_blast_radius(package_name=package, max_depth=depth)
    result["cache_hit"] = False
    
    # Cache in Redis with 180s TTL
    redis_manager.set_cache(cache_key, result, ttl_seconds=180)
    return result

@router.post("/simulate-breaking-change")
def simulate_package_removal(request: BreakingChangeRequest):
    """
    Simulates removing or deprecating an open-source package.
    Identifies which repositories will have broken direct and transitive dependencies.
    """
    return neo4j_manager.simulate_breaking_change(request.package)
