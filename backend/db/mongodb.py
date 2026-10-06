from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import CollectionInvalid, OperationFailure
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from backend.config import settings

logger = logging.getLogger(__name__)

class MongoDBManager:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(
                settings.MONGO_URI,
                serverSelectionTimeoutMS=1000,
                maxPoolSize=50
            )
            # Ping database to verify connection
            self.client.admin.command('ping')
            self.db = self.client[settings.MONGO_DB_NAME]
            logger.info("MongoDB connected successfully to '%s'", settings.MONGO_DB_NAME)
            self.init_schema_and_indexes()
        except Exception as e:
            logger.warning("MongoDB connection failed or deferred: %s", str(e))
            self.client = None
            self.db = None

    def init_schema_and_indexes(self):
        """
        Implements AIM3141 Syllabus Concepts:
        1. Lecture 20: Schema Validation using JSON Schema ($jsonSchema)
        2. Lecture 13: Compound and Text Indexes
        3. Lecture 15: Computed Pattern support
        """
        if self.db is None:
            return

        # 1. JSON Schema Validation for 'repositories' collection
        repo_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["full_name", "owner", "primary_language"],
                "properties": {
                    "full_name": {
                        "bsonType": "string",
                        "description": "must be a string and is required e.g. expressjs/express"
                    },
                    "owner": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "primary_language": {
                        "bsonType": "string",
                        "description": "must be a string (JavaScript, Python, Java, etc.)"
                    },
                    "stars": {
                        "bsonType": ["int", "long", "double"],
                        "minimum": 0,
                        "description": "must be a non-negative number"
                    },
                    "risk_score": {
                        "bsonType": ["int", "long", "double"],
                        "description": "Computed Pattern: aggregated risk score (0 to 100)"
                    },
                    "total_cves": {
                        "bsonType": ["int", "long"],
                        "description": "Computed Pattern: total active CVEs detected"
                    }
                }
            }
        }

        try:
            self.db.create_collection("repositories", validator=repo_validator)
            logger.info("Created 'repositories' collection with JSON Schema Validator.")
        except CollectionInvalid:
            # Collection exists; update validator
            try:
                self.db.command("collMod", "repositories", validator=repo_validator)
                logger.info("Updated 'repositories' JSON Schema Validator.")
            except Exception as e:
                logger.debug("Validator update note: %s", str(e))
        except Exception as e:
            logger.debug("Schema validator setup note: %s", str(e))

        # 2. Indexes (Lecture 13)
        repos = self.db.repositories
        try:
            # Compound index for filtering by language and sorting by stars
            repos.create_index([("primary_language", ASCENDING), ("stars", DESCENDING)], name="idx_lang_stars")
            # Unique index on full_name
            repos.create_index([("full_name", ASCENDING)], unique=True, name="idx_repo_fullname_unique")
            # Text index for search functionality
            repos.create_index([("full_name", TEXT), ("description", TEXT)], name="idx_repo_text_search")
            logger.info("MongoDB indexes verified on 'repositories'.")
        except Exception as e:
            logger.warning("Index creation note: %s", str(e))

        # Indexes on cve_advisories
        cves = self.db.cve_advisories
        try:
            cves.create_index([("cve_id", ASCENDING)], unique=True, name="idx_cve_id_unique")
            cves.create_index([("package", ASCENDING), ("ecosystem", ASCENDING)], name="idx_pkg_ecosystem")
            cves.create_index([("cvss_score", DESCENDING)], name="idx_cve_cvss")
        except Exception as e:
            logger.debug("CVE index creation note: %s", str(e))

    def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")

    # -------------------------------------------------------------
    # Repository CRUD & Computed Pattern Operations
    # -------------------------------------------------------------
    def upsert_repository(self, repo_data: Dict[str, Any]) -> str:
        """Upserts a repository document using Computed Pattern values."""
        if self.db is None:
            raise ConnectionError("MongoDB is not connected")
        
        repo_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        if "created_at" not in repo_data:
            repo_data["created_at"] = repo_data["updated_at"]

        # Ensure numeric types conform to schema
        if "stars" in repo_data:
            repo_data["stars"] = int(repo_data["stars"])
        if "total_cves" in repo_data:
            repo_data["total_cves"] = int(repo_data["total_cves"])
        if "risk_score" in repo_data:
            repo_data["risk_score"] = float(repo_data["risk_score"])

        self.db.repositories.update_one(
            {"full_name": repo_data["full_name"]},
            {"$set": repo_data},
            upsert=True
        )
        return repo_data["full_name"]

    def get_all_repositories(self, limit: int = 50) -> List[Dict[str, Any]]:
        if self.db is None:
            return self._fallback_get_all_repositories(limit)
        try:
            cursor = self.db.repositories.find({}, {"_id": 0}).sort("stars", DESCENDING).limit(limit)
            repos = list(cursor)
            return repos if repos else self._fallback_get_all_repositories(limit)
        except Exception as e:
            logger.warning("MongoDB get_all_repositories failed (%s); using fallback", str(e))
            return self._fallback_get_all_repositories(limit)

    def get_repository(self, full_name: str) -> Optional[Dict[str, Any]]:
        if self.db is None:
            return None
        try:
            return self.db.repositories.find_one({"full_name": full_name}, {"_id": 0})
        except Exception:
            return None

    # -------------------------------------------------------------
    # CVE Advisory Operations
    # -------------------------------------------------------------
    def upsert_cve(self, cve_data: Dict[str, Any]):
        if self.db is None:
            return
        try:
            cve_data["saved_at"] = datetime.now(timezone.utc).isoformat()
            self.db.cve_advisories.update_one(
                {"cve_id": cve_data["cve_id"]},
                {"$set": cve_data},
                upsert=True
            )
        except Exception as e:
            logger.warning("MongoDB upsert_cve note: %s", str(e))

    def get_cve(self, cve_id: str) -> Optional[Dict[str, Any]]:
        if self.db is None:
            return None
        try:
            return self.db.cve_advisories.find_one({"cve_id": cve_id}, {"_id": 0})
        except Exception:
            return None

    # -------------------------------------------------------------
    # AIM3141 Aggregation Framework Implementation (Lectures 16-18)
    # -------------------------------------------------------------
    def get_ecosystem_risk_summary(self) -> List[Dict[str, Any]]:
        """
        Aggregation Pipeline 1:
        Stages: $match -> $group -> $project -> $sort
        Groups repositories by language and calculates aggregate vulnerability metrics.
        """
        if self.db is None:
            return self._fallback_ecosystem_summary()

        pipeline = [
            {
                "$match": {
                    "primary_language": {"$exists": True, "$ne": None}
                }
            },
            {
                "$group": {
                    "_id": "$primary_language",
                    "repo_count": {"$sum": 1},
                    "total_stars": {"$sum": "$stars"},
                    "avg_risk_score": {"$avg": "$risk_score"},
                    "total_cves_detected": {"$sum": "$total_cves"},
                    "max_cvss": {"$max": "$highest_cvss"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "language": "$_id",
                    "repo_count": 1,
                    "total_stars": 1,
                    "avg_risk_score": {"$round": ["$avg_risk_score", 2]},
                    "total_cves_detected": 1,
                    "max_cvss": {"$round": ["$max_cvss", 1]}
                }
            },
            {
                "$sort": {"avg_risk_score": -1}
            }
        ]
        try:
            res = list(self.db.repositories.aggregate(pipeline))
            return res if res else self._fallback_ecosystem_summary()
        except Exception as e:
            logger.warning("MongoDB aggregation failed (%s); using fallback", str(e))
            return self._fallback_ecosystem_summary()

    def get_advanced_analytics_facet(self) -> Dict[str, Any]:
        """
        Aggregation Pipeline 2 (Lecture 18: $facet Stage):
        Executes multi-dimensional analytics in a single database round-trip:
        - Sub-pipeline A: Severity Distribution ($bucket or $group)
        - Sub-pipeline B: Top 5 Most Starred Repositories
        - Sub-pipeline C: Language Share Breakdown
        """
        if self.db is None:
            return self._fallback_facet_analytics()

        pipeline = [
            {
                "$facet": {
                    "language_breakdown": [
                        {
                            "$group": {
                                "_id": "$primary_language",
                                "count": {"$sum": 1},
                                "avg_cves": {"$avg": "$total_cves"}
                            }
                        },
                        {
                            "$project": {
                                "_id": 0,
                                "language": "$_id",
                                "count": 1,
                                "avg_cves": {"$round": ["$avg_cves", 1]}
                            }
                        }
                    ],
                    "top_starred_repos": [
                        {"$sort": {"stars": -1}},
                        {"$limit": 5},
                        {
                            "$project": {
                                "_id": 0,
                                "full_name": 1,
                                "stars": 1,
                                "primary_language": 1,
                                "risk_score": 1,
                                "total_cves": 1
                            }
                        }
                    ],
                    "risk_overview": [
                        {
                            "$group": {
                                "_id": None,
                                "total_repos": {"$sum": 1},
                                "total_cves": {"$sum": "$total_cves"},
                                "avg_risk": {"$avg": "$risk_score"},
                                "highest_risk": {"$max": "$risk_score"}
                            }
                        },
                        {
                            "$project": {
                                "_id": 0,
                                "total_repos": 1,
                                "total_cves": 1,
                                "avg_risk": {"$round": ["$avg_risk", 2]},
                                "highest_risk": 1
                            }
                        }
                    ]
                }
            }
        ]
        results = list(self.db.repositories.aggregate(pipeline))
        return results[0] if results else {}

    # -------------------------------------------------------------
    # Offline Fallback Engine (when Docker MongoDB is offline)
    # -------------------------------------------------------------
    def _fallback_get_all_repositories(self, limit: int = 50) -> List[Dict[str, Any]]:
        from backend.services.seeder import SEED_REPOSITORIES, SEED_CVES
        cve_map = {c["package"]: c for c in SEED_CVES}
        result = []
        for r in SEED_REPOSITORIES:
            doc = dict(r)
            deps = doc.get("direct_deps", [])
            doc["dependencies"] = deps
            detected_cves = [cve_map[d] for d in deps if d in cve_map]
            doc["total_cves"] = len(detected_cves)
            doc["highest_cvss"] = max([c.get("cvss_score", 0.0) for c in detected_cves], default=0.0)
            doc["risk_score"] = round(doc["highest_cvss"] * 7.5 + len(detected_cves) * 5.0, 1)
            result.append(doc)
        result.sort(key=lambda x: x.get("stars", 0), reverse=True)
        return result[:limit]

    def _fallback_ecosystem_summary(self) -> List[Dict[str, Any]]:
        repos = self._fallback_get_all_repositories()
        lang_groups = {}
        for r in repos:
            lang = r.get("primary_language", "Unknown")
            if lang not in lang_groups:
                lang_groups[lang] = {
                    "language": lang,
                    "repo_count": 0,
                    "total_stars": 0,
                    "risk_scores": [],
                    "total_cves_detected": 0,
                    "max_cvss": 0.0
                }
            g = lang_groups[lang]
            g["repo_count"] += 1
            g["total_stars"] += r.get("stars", 0)
            g["risk_scores"].append(r.get("risk_score", 0.0))
            g["total_cves_detected"] += r.get("total_cves", 0)
            g["max_cvss"] = max(g["max_cvss"], r.get("highest_cvss", 0.0))

        summary = []
        for g in lang_groups.values():
            avg_risk = round(sum(g["risk_scores"]) / len(g["risk_scores"]), 2) if g["risk_scores"] else 0.0
            summary.append({
                "language": g["language"],
                "repo_count": g["repo_count"],
                "total_stars": g["total_stars"],
                "avg_risk_score": avg_risk,
                "total_cves_detected": g["total_cves_detected"],
                "max_cvss": g["max_cvss"]
            })
        summary.sort(key=lambda x: x["avg_risk_score"], reverse=True)
        return summary

    def _fallback_facet_analytics(self) -> Dict[str, Any]:
        repos = self._fallback_get_all_repositories()
        total_repos = len(repos)
        total_cves = sum(r.get("total_cves", 0) for r in repos)
        avg_risk = round(sum(r.get("risk_score", 0.0) for r in repos) / total_repos, 2) if total_repos else 0.0
        max_risk = max((r.get("risk_score", 0.0) for r in repos), default=0.0)

        # Language breakdown
        lang_counts = {}
        for r in repos:
            l = r.get("primary_language", "Unknown")
            if l not in lang_counts:
                lang_counts[l] = {"count": 0, "cves": []}
            lang_counts[l]["count"] += 1
            lang_counts[l]["cves"].append(r.get("total_cves", 0))

        lang_breakdown = [
            {
                "language": l,
                "count": data["count"],
                "avg_cves": round(sum(data["cves"]) / len(data["cves"]), 1) if data["cves"] else 0.0
            }
            for l, data in lang_counts.items()
        ]

        top_repos = [
            {
                "full_name": r["full_name"],
                "stars": r["stars"],
                "primary_language": r["primary_language"],
                "risk_score": r["risk_score"],
                "total_cves": r["total_cves"]
            }
            for r in repos[:5]
        ]

        return {
            "language_breakdown": lang_breakdown,
            "top_starred_repos": top_repos,
            "risk_overview": [{
                "total_repos": total_repos,
                "total_cves": total_cves,
                "avg_risk": avg_risk,
                "highest_risk": max_risk
            }]
        }

mongodb_manager = MongoDBManager()
