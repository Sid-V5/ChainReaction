from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any, List
import json
import logging
from datetime import datetime, timezone
from backend.db.redis_db import redis_manager
from backend.db.neo4j_db import neo4j_manager
from backend.db.mongodb import mongodb_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/alerts", tags=["Live Alerts & Leaderboard"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

ws_manager = ConnectionManager()

@router.get("/leaderboard")
def get_vulnerability_leaderboard(limit: int = 10):
    """
    AIM3141 Sorted Sets (ZSET) Leaderboard (Lecture 35):
    Returns the top most vulnerable repositories ranked by risk score.
    """
    return redis_manager.get_top_vulnerable_repos(limit=limit)

@router.post("/simulate-zero-day")
async def trigger_simulated_zero_day():
    """
    Presentation Feature:
    Fires an emergency zero-day vulnerability alert into Redis Pub/Sub,
    links the CVE in Neo4j, updates MongoDB, and pushes live to all connected WebSockets.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    zero_day_payload = {
        "event": "ZERO_DAY_DETECTED",
        "cve_id": f"CVE-2026-{datetime.now().strftime('%M%S')}",
        "package": "requests",
        "ecosystem": "PyPI",
        "severity": "CRITICAL",
        "cvss_score": 9.8,
        "summary": "CRITICAL ZERO-DAY: Unauthenticated Remote Code Execution flaw discovered in requests SSL verification handshake.",
        "timestamp": now_iso
    }

    # 1. Update Neo4j graph with new critical vulnerability node
    neo4j_manager.link_vulnerability(
        package_name="requests",
        cve_id=zero_day_payload["cve_id"],
        severity="CRITICAL",
        cvss_score=9.8,
        summary=zero_day_payload["summary"]
    )

    # 2. Store advisory in MongoDB
    mongodb_manager.upsert_cve({
        "cve_id": zero_day_payload["cve_id"],
        "package": "requests",
        "ecosystem": "PyPI",
        "severity": "CRITICAL",
        "cvss_score": 9.8,
        "summary": zero_day_payload["summary"]
    })

    # 3. Increase affected repo risk score in Redis ZSET
    redis_manager.update_repo_risk_score("psf/requests", 98.5)

    # 4. Publish to Redis Pub/Sub
    redis_manager.publish_alert(zero_day_payload)

    # 5. Broadcast to connected WebSocket clients
    await ws_manager.broadcast(zero_day_payload)

    return {"status": "broadcasted", "alert": zero_day_payload}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Send initial welcome packet
        await websocket.send_json({
            "event": "CONNECTED",
            "message": "Connected to ChainReaction live vulnerability stream via Redis Pub/Sub"
        })
        while True:
            # Keep-alive loop
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
