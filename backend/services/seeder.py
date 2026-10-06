import logging
from typing import Dict, Any, List
from backend.db.mongodb import mongodb_manager
from backend.db.neo4j_db import neo4j_manager
from backend.db.redis_db import redis_manager

logger = logging.getLogger(__name__)

# Curated dataset of 12 popular enterprise repositories across Java, Python, and JavaScript
SEED_REPOSITORIES = [
    {
        "full_name": "expressjs/express",
        "owner": "expressjs",
        "stars": 63400,
        "primary_language": "JavaScript",
        "ecosystem": "npm",
        "description": "Fast, unopinionated, minimalist web framework for node.",
        "direct_deps": ["body-parser", "cookie", "debug", "send", "safe-buffer"],
        "transitive_deps": [("body-parser", "qs")]
    },
    {
        "full_name": "axios/axios",
        "owner": "axios",
        "stars": 104000,
        "primary_language": "JavaScript",
        "ecosystem": "npm",
        "description": "Promise based HTTP client for the browser and node.js",
        "direct_deps": ["follow-redirects", "form-data", "proxy-from-env", "qs"],
        "transitive_deps": []
    },
    {
        "full_name": "facebook/react",
        "owner": "facebook",
        "stars": 226000,
        "primary_language": "JavaScript",
        "ecosystem": "npm",
        "description": "The library for web and native user interfaces.",
        "direct_deps": ["loose-envify", "object-assign", "scheduler", "prop-types"],
        "transitive_deps": [("loose-envify", "chalk")]
    },
    {
        "full_name": "babel/babel",
        "owner": "babel",
        "stars": 43200,
        "primary_language": "JavaScript",
        "ecosystem": "npm",
        "description": "The compiler for next generation JavaScript.",
        "direct_deps": ["semver", "chalk", "source-map"],
        "transitive_deps": []
    },
    {
        "full_name": "pallets/flask",
        "owner": "pallets",
        "stars": 67800,
        "primary_language": "Python",
        "ecosystem": "PyPI",
        "description": "The Python micro framework for building web applications.",
        "direct_deps": ["werkzeug", "jinja2", "itsdangerous", "click", "blinker"],
        "transitive_deps": [("werkzeug", "markupsafe"), ("jinja2", "markupsafe")]
    },
    {
        "full_name": "psf/requests",
        "owner": "psf",
        "stars": 51200,
        "primary_language": "Python",
        "ecosystem": "PyPI",
        "description": "A simple, yet elegant, HTTP library for Python.",
        "direct_deps": ["urllib3", "certifi", "idna", "charset-normalizer"],
        "transitive_deps": []
    },
    {
        "full_name": "tiangolo/fastapi",
        "owner": "tiangolo",
        "stars": 76500,
        "primary_language": "Python",
        "ecosystem": "PyPI",
        "description": "FastAPI framework, high performance, easy to learn, fast to code.",
        "direct_deps": ["starlette", "pydantic", "typing-extensions", "anyio", "urllib3"],
        "transitive_deps": [("starlette", "jinja2")]
    },
    {
        "full_name": "django/django",
        "owner": "django",
        "stars": 78900,
        "primary_language": "Python",
        "ecosystem": "PyPI",
        "description": "The Web framework for perfectionists with deadlines.",
        "direct_deps": ["asgiref", "sqlparse", "pytz", "certifi"],
        "transitive_deps": []
    },
    {
        "full_name": "aio-libs/aiohttp",
        "owner": "aio-libs",
        "stars": 14900,
        "primary_language": "Python",
        "ecosystem": "PyPI",
        "description": "Asynchronous HTTP client/server framework for asyncio and Python.",
        "direct_deps": ["multidict", "yarl", "frozenlist", "async-timeout"],
        "transitive_deps": [("yarl", "idna")]
    },
    {
        "full_name": "spring-projects/spring-boot",
        "owner": "spring-projects",
        "stars": 74100,
        "primary_language": "Java",
        "ecosystem": "Maven",
        "description": "Spring Boot helps you to create stand-alone, production-grade Spring based Applications.",
        "direct_deps": ["spring-core", "spring-web", "spring-context"],
        "transitive_deps": [("spring-web", "log4j-core")]
    },
    {
        "full_name": "apache/kafka",
        "owner": "apache",
        "stars": 28400,
        "primary_language": "Java",
        "ecosystem": "Maven",
        "description": "Mirror of Apache Kafka, distributed event store and stream-processing platform.",
        "direct_deps": ["slf4j-api", "snappy-java", "zstd-jni", "lz4-java"],
        "transitive_deps": [("slf4j-api", "log4j-core")]
    },
    {
        "full_name": "apache/logging-log4j2",
        "owner": "apache",
        "stars": 3100,
        "primary_language": "Java",
        "ecosystem": "Maven",
        "description": "Apache Log4j 2 is an upgrade to Log4j that provides significant improvements.",
        "direct_deps": ["log4j-core", "log4j-api"],
        "transitive_deps": []
    }
]

# Real known vulnerabilities (CVEs) mapped to shared packages
SEED_CVES = [
    {
        "cve_id": "CVE-2021-44228",
        "package": "log4j-core",
        "ecosystem": "Maven",
        "severity": "CRITICAL",
        "cvss_score": 10.0,
        "summary": "Log4Shell: Remote Code Execution in Apache Log4j via JNDI lookup vulnerability.",
        "fixed_version": "2.17.1"
    },
    {
        "cve_id": "CVE-2023-45803",
        "package": "urllib3",
        "ecosystem": "PyPI",
        "severity": "MEDIUM",
        "cvss_score": 5.3,
        "summary": "urllib3 does not remove Cookie header on cross-origin redirects from HTTPS to HTTP.",
        "fixed_version": "2.0.7"
    },
    {
        "cve_id": "CVE-2017-1000048",
        "package": "qs",
        "ecosystem": "npm",
        "severity": "HIGH",
        "cvss_score": 7.5,
        "summary": "qs library is vulnerable to denial of service due to memory exhaustion in query string parsing.",
        "fixed_version": "6.5.1"
    },
    {
        "cve_id": "CVE-2023-25577",
        "package": "werkzeug",
        "ecosystem": "PyPI",
        "severity": "HIGH",
        "cvss_score": 7.5,
        "summary": "High resource consumption parsing multipart form data in Pallets Werkzeug.",
        "fixed_version": "2.2.3"
    },
    {
        "cve_id": "CVE-2024-28849",
        "package": "follow-redirects",
        "ecosystem": "npm",
        "severity": "HIGH",
        "cvss_score": 7.4,
        "summary": "follow-redirects leaks Proxy-Authorization headers to destination servers.",
        "fixed_version": "1.15.6"
    },
    {
        "cve_id": "CVE-2022-22965",
        "package": "spring-web",
        "ecosystem": "Maven",
        "severity": "CRITICAL",
        "cvss_score": 9.8,
        "summary": "Spring4Shell: Remote Code Execution in Spring Framework via Data Binding parameter binding.",
        "fixed_version": "5.3.18"
    }
]

def seed_database(force: bool = False):
    """
    Populates MongoDB, Neo4j, and Redis with the foundational dataset
    if MongoDB 'repositories' collection is empty or force=True.
    """
    if mongodb_manager.db is None:
        logger.warning("MongoDB not connected. Skipping seeding.")
        return

    existing_count = mongodb_manager.db.repositories.count_documents({})
    if existing_count > 0 and not force:
        logger.info("Database already seeded with %d repositories. Skipping.", existing_count)
        return

    logger.info("Starting initial NoSQL database seeding (12 repos, real CVEs)...")

    # 1. Seed CVE Advisories in MongoDB
    cve_lookup = {}
    for cve in SEED_CVES:
        mongodb_manager.upsert_cve(cve)
        cve_lookup[cve["package"]] = cve

    # 2. Seed Repositories and build Graph
    for repo in SEED_REPOSITORIES:
        full_name = repo["full_name"]
        direct_deps = repo["direct_deps"]

        # Neo4j: Add Repository Node
        neo4j_manager.add_repository(
            full_name=full_name,
            owner=repo["owner"],
            stars=repo["stars"],
            language=repo["primary_language"]
        )

        detected_cves = []
        highest_cvss = 0.0

        # Neo4j: Add Direct Dependencies
        for dep in direct_deps:
            neo4j_manager.add_dependency(
                repo_full_name=full_name,
                package_name=dep,
                ecosystem=repo["ecosystem"],
                is_direct=True
            )
            if dep in cve_lookup:
                cve_info = cve_lookup[dep]
                detected_cves.append(cve_info["cve_id"])
                if cve_info["cvss_score"] > highest_cvss:
                    highest_cvss = cve_info["cvss_score"]
                neo4j_manager.link_vulnerability(
                    package_name=dep,
                    cve_id=cve_info["cve_id"],
                    severity=cve_info["severity"],
                    cvss_score=cve_info["cvss_score"],
                    summary=cve_info["summary"]
                )

        # Neo4j: Add Transitive Dependencies
        for parent_pkg, child_pkg in repo.get("transitive_deps", []):
            neo4j_manager.add_package_dependency(parent_pkg, child_pkg, ecosystem=repo["ecosystem"])
            if child_pkg in cve_lookup:
                cve_info = cve_lookup[child_pkg]
                detected_cves.append(cve_info["cve_id"])
                if cve_info["cvss_score"] > highest_cvss:
                    highest_cvss = cve_info["cvss_score"]
                neo4j_manager.link_vulnerability(
                    package_name=child_pkg,
                    cve_id=cve_info["cve_id"],
                    severity=cve_info["severity"],
                    cvss_score=cve_info["cvss_score"],
                    summary=cve_info["summary"]
                )

        # Computed Pattern in MongoDB (Lecture 15)
        total_cves = len(detected_cves)
        risk_score = min(100.0, round((total_cves * 15.0) + (highest_cvss * 5.5), 1))

        repo_doc = {
            "full_name": full_name,
            "owner": repo["owner"],
            "primary_language": repo["primary_language"],
            "ecosystem": repo["ecosystem"],
            "description": repo["description"],
            "stars": repo["stars"],
            "dependencies": direct_deps,
            "total_cves": total_cves,
            "highest_cvss": highest_cvss,
            "risk_score": risk_score,
            "vulnerabilities": detected_cves
        }

        # MongoDB: Upsert Document
        mongodb_manager.upsert_repository(repo_doc)

        # Redis: Update ZSET Leaderboard
        redis_manager.update_repo_risk_score(full_name, risk_score)

    logger.info("Database seeding successfully completed for 12 repositories.")
