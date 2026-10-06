from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from backend.db.mongodb import mongodb_manager
from backend.services.scanner import repo_scanner
from backend.services.seeder import seed_database

router = APIRouter(prefix="/api/repos", tags=["Repositories"])

class ScanRequest(BaseModel):
    url: str

@router.get("", response_model=List[Dict[str, Any]])
def list_repositories(limit: int = Query(50, ge=1, le=100)):
    """Fetches all tracked repositories sorted by stars from MongoDB."""
    return mongodb_manager.get_all_repositories(limit=limit)

@router.get("/analytics/ecosystem")
def get_ecosystem_analytics():
    """
    AIM3141 Aggregation Framework (Lecture 16-17):
    Pipeline: $match -> $group -> $project -> $sort
    """
    return mongodb_manager.get_ecosystem_risk_summary()

@router.get("/analytics/facet")
def get_advanced_facet_analytics():
    """
    AIM3141 Advanced Aggregation (Lecture 18):
    Multi-stage analytical pipeline using $facet operator.
    """
    return mongodb_manager.get_advanced_analytics_facet()

@router.post("/scan")
async def scan_repository_endpoint(request: ScanRequest):
    """
    Ingests and scans any public GitHub repository.
    Extracts dependencies, queries OSV.dev for CVEs, and updates MongoDB, Neo4j, and Redis.
    """
    try:
        result = await repo_scanner.scan_repository(request.url)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{owner}/{repo_name}")
def get_repository_details(owner: str, repo_name: str):
    """Fetches full repository metadata document from MongoDB."""
    full_name = f"{owner}/{repo_name}"
    doc = mongodb_manager.get_repository(full_name)
    if not doc:
        raise HTTPException(status_code=404, detail="Repository not found")
    return doc

@router.post("/reseed")
def trigger_database_reseed():
    """Forces a database reset and re-seeds the 12 default repositories."""
    seed_database(force=True)
    return {"status": "success", "message": "Database reseeded successfully"}
