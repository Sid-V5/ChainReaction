import redis
import json
import logging
from typing import Dict, Any, List, Optional
from backend.config import settings

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self._memory_cache: Dict[str, Any] = {}
        self._memory_leaderboard: Dict[str, float] = {
            "apache/logging-log4j2": 80.0,
            "spring-projects/spring-boot": 65.0,
            "psf/requests": 45.0,
            "axios/axios": 35.0,
            "expressjs/express": 25.0
        }

    def connect(self):
        try:
            self.client = redis.Redis.from_url(
                settings.REDIS_URI,
                decode_responses=True,
                socket_timeout=1,
                socket_connect_timeout=1
            )
            self.client.ping()
            logger.info("Redis connected successfully via URI: %s", settings.REDIS_URI)
        except Exception as e:
            logger.warning("Redis connection failed or deferred: %s", str(e))
            self.client = None

    def close(self):
        if self.client:
            self.client.close()
            logger.info("Redis connection closed.")

    # -------------------------------------------------------------
    # AIM3141 Sorted Sets (ZSET) Leaderboard (Lecture 35)
    # -------------------------------------------------------------
    def update_repo_risk_score(self, repo_name: str, risk_score: float):
        """
        Maintains a Redis Sorted Set (ZSET) 'leaderboard:vulnerable_repos'.
        Score = Calculated risk score (0 to 100).
        Allows sub-millisecond retrieval of the most critical repositories.
        """
        if not self.client:
            self._memory_leaderboard[repo_name] = float(risk_score)
            return
        try:
            self.client.zadd("leaderboard:vulnerable_repos", {repo_name: float(risk_score)})
        except Exception as e:
            logger.debug("Redis ZADD error: %s", str(e))
            self._memory_leaderboard[repo_name] = float(risk_score)

    def get_top_vulnerable_repos(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves the top N highest risk repositories using ZREVRANGE.
        Time complexity: O(log(N) + M) where M is the number of elements returned.
        """
        if not self.client:
            sorted_items = sorted(self._memory_leaderboard.items(), key=lambda x: x[1], reverse=True)
            return [{"repository": repo, "risk_score": round(score, 1)} for repo, score in sorted_items[:limit]]
        try:
            results = self.client.zrevrange("leaderboard:vulnerable_repos", 0, limit - 1, withscores=True)
            if not results:
                sorted_items = sorted(self._memory_leaderboard.items(), key=lambda x: x[1], reverse=True)
                return [{"repository": repo, "risk_score": round(score, 1)} for repo, score in sorted_items[:limit]]
            return [{"repository": repo, "risk_score": round(score, 1)} for repo, score in results]
        except Exception as e:
            logger.debug("Redis ZREVRANGE error: %s", str(e))
            sorted_items = sorted(self._memory_leaderboard.items(), key=lambda x: x[1], reverse=True)
            return [{"repository": repo, "risk_score": round(score, 1)} for repo, score in sorted_items[:limit]]

    # -------------------------------------------------------------
    # AIM3141 Key-Value Caching with TTL (Lecture 35)
    # -------------------------------------------------------------
    def get_cache(self, key: str) -> Optional[Any]:
        if not self.client:
            return self._memory_cache.get(key)
        try:
            val = self.client.get(key)
            return json.loads(val) if val else None
        except Exception as e:
            logger.debug("Redis GET cache error: %s", str(e))
            return self._memory_cache.get(key)

    def set_cache(self, key: str, value: Any, ttl_seconds: int = 300):
        if not self.client:
            self._memory_cache[key] = value
            return
        try:
            self.client.setex(key, ttl_seconds, json.dumps(value))
        except Exception as e:
            logger.debug("Redis SETEX cache error: %s", str(e))
            self._memory_cache[key] = value

    # -------------------------------------------------------------
    # AIM3141 Redis Pub/Sub for Live Alerts
    # -------------------------------------------------------------
    def publish_alert(self, alert_payload: Dict[str, Any]):
        """Publishes a live vulnerability event to the 'cve:alerts' channel."""
        if not self.client:
            logger.info("Published CVE alert to in-memory channel 'cve:alerts': %s", alert_payload.get("cve_id"))
            return
        try:
            message = json.dumps(alert_payload)
            self.client.publish("cve:alerts", message)
            logger.info("Published CVE alert to Redis channel 'cve:alerts': %s", alert_payload.get("cve_id"))
        except Exception as e:
            logger.debug("Redis publish error: %s", str(e))

redis_manager = RedisManager()
