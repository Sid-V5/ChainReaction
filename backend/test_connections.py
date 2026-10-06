import sys
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestVerifier")

from backend.db.mongodb import mongodb_manager
from backend.db.neo4j_db import neo4j_manager
from backend.db.redis_db import redis_manager
from backend.services.seeder import seed_database

def run_tests():
    print("=" * 60)
    print("CHAINREACTION: NOSQL SYSTEM VERIFICATION SUITE")
    print("=" * 60)

    # 1. Test MongoDB
    print("\n[1/5] Testing MongoDB Connection & Schema Setup...")
    mongodb_manager.connect()
    assert mongodb_manager.db is not None, "MongoDB connection failed!"
    print("  -> MongoDB connection: OK")
    print("  -> Database:", mongodb_manager.db.name)

    # 2. Test Redis
    print("\n[2/5] Testing Redis Connection & ZSET Operations...")
    redis_manager.connect()
    assert redis_manager.client is not None, "Redis connection failed!"
    redis_manager.client.ping()
    print("  -> Redis PING: PONG (OK)")
    redis_manager.update_repo_risk_score("test/repo", 88.5)
    top = redis_manager.get_top_vulnerable_repos(limit=1)
    assert len(top) > 0 and top[0]["repository"] == "test/repo", "Redis ZSET test failed!"
    print("  -> Redis ZSET Leaderboard (ZREVRANGE): OK ->", top[0])

    # 3. Test Neo4j
    print("\n[3/5] Testing Neo4j Bolt Connection...")
    # Neo4j might take a few seconds to finish initial startup
    for attempt in range(10):
        try:
            neo4j_manager.connect()
            if neo4j_manager.driver:
                break
        except Exception:
            pass
        print(f"  ...waiting for Neo4j Bolt engine (attempt {attempt+1}/10)...")
        time.sleep(3)

    assert neo4j_manager.driver is not None, "Neo4j connection failed!"
    print("  -> Neo4j Bolt Driver: OK")

    # 4. Run Full Database Seeder
    print("\n[4/5] Executing Polyglot Seeder (12 Repos, Multi-hop Graph, Real CVEs)...")
    seed_database(force=True)
    repo_count = mongodb_manager.db.repositories.count_documents({})
    print(f"  -> MongoDB Repositories Document Count: {repo_count} (Expected: 12)")
    assert repo_count >= 12, "MongoDB did not seed 12 repositories!"

    # 5. Verify Cypher Multi-Hop Graph Traversal (AIM3141.5)
    print("\n[5/5] Testing Cypher Blast Radius Variable-Length Traversal (*1..5)...")
    blast_log4j = neo4j_manager.get_blast_radius("log4j-core", max_depth=5)
    print(f"  -> Blast Radius for 'log4j-core': {blast_log4j['total_affected']} repositories affected")
    for r in blast_log4j["affected_repositories"]:
        print(f"     • {r['repository']} ({r['depth']} hops) -> {' -> '.join(r['chain'])}")
    assert blast_log4j["total_affected"] >= 2, "Transitive blast radius traversal did not find expected repos!"

    # Verify MongoDB Aggregation Pipeline ($group & $facet)
    print("\n[Bonus] Testing MongoDB Aggregation Pipelines ($match, $group, $facet)...")
    eco = mongodb_manager.get_ecosystem_risk_summary()
    print(f"  -> Ecosystem $group Summary: {len(eco)} language groups returned")
    for e in eco:
        print(f"     • {e['language']}: {e['repo_count']} repos, avg risk: {e['avg_risk_score']}, max CVSS: {e['max_cvss']}")

    facet = mongodb_manager.get_advanced_analytics_facet()
    print("  -> Multi-stage $facet Aggregation: OK ->", list(facet.keys()))

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! POLYGLOT NOSQL ARCHITECTURE FULLY OPERATIONAL!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
