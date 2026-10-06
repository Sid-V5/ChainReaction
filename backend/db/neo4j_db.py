from neo4j import GraphDatabase, Driver
import logging
from typing import Dict, Any, List, Optional
from backend.config import settings

logger = logging.getLogger(__name__)

class Neo4jManager:
    def __init__(self):
        self.driver: Optional[Driver] = None

    def connect(self):
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                max_connection_lifetime=3600,
                max_connection_pool_size=50
            )
            # Verify connectivity
            self.driver.verify_connectivity()
            logger.info("Neo4j connected successfully via Bolt protocol.")
            self.init_constraints()
        except Exception as e:
            logger.warning("Neo4j connection failed or deferred: %s", str(e))
            self.driver = None

    def init_constraints(self):
        """Creates unique constraints and indexes in Neo4j."""
        if not self.driver:
            return
        queries = [
            "CREATE CONSTRAINT repo_fullname_unique IF NOT EXISTS FOR (r:Repository) REQUIRE r.fullName IS UNIQUE",
            "CREATE CONSTRAINT pkg_name_unique IF NOT EXISTS FOR (p:Package) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT cve_id_unique IF NOT EXISTS FOR (v:Vulnerability) REQUIRE v.cveId IS UNIQUE"
        ]
        with self.driver.session() as session:
            for q in queries:
                try:
                    session.run(q)
                except Exception as e:
                    logger.debug("Neo4j constraint note: %s", str(e))

    def close(self):
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed.")

    # -------------------------------------------------------------
    # Graph Ingestion Operations
    # -------------------------------------------------------------
    def add_repository(self, full_name: str, owner: str, stars: int, language: str):
        if not self.driver:
            return
        query = """
        MERGE (r:Repository {fullName: $full_name})
        ON CREATE SET r.owner = $owner, r.stars = $stars, r.primaryLanguage = $language
        ON MATCH SET r.stars = $stars, r.primaryLanguage = $language
        """
        with self.driver.session() as session:
            session.run(query, full_name=full_name, owner=owner, stars=stars, language=language)

    def add_dependency(self, repo_full_name: str, package_name: str, ecosystem: str = "npm", is_direct: bool = True):
        if not self.driver:
            return
        query = """
        MATCH (r:Repository {fullName: $repo_full_name})
        MERGE (p:Package {name: $package_name})
        ON CREATE SET p.ecosystem = $ecosystem
        MERGE (r)-[rel:DEPENDS_ON]->(p)
        ON CREATE SET rel.type = $dep_type
        """
        dep_type = "direct" if is_direct else "transitive"
        with self.driver.session() as session:
            session.run(query, repo_full_name=repo_full_name, package_name=package_name,
                        ecosystem=ecosystem, dep_type=dep_type)

    def add_package_dependency(self, parent_pkg: str, child_pkg: str, ecosystem: str = "npm"):
        """Creates transitive package-to-package dependency edge."""
        if not self.driver:
            return
        query = """
        MERGE (p1:Package {name: $parent_pkg})
        ON CREATE SET p1.ecosystem = $ecosystem
        MERGE (p2:Package {name: $child_pkg})
        ON CREATE SET p2.ecosystem = $ecosystem
        MERGE (p1)-[rel:DEPENDS_ON]->(p2)
        ON CREATE SET rel.type = 'transitive'
        """
        with self.driver.session() as session:
            session.run(query, parent_pkg=parent_pkg, child_pkg=child_pkg, ecosystem=ecosystem)

    def link_vulnerability(self, package_name: str, cve_id: str, severity: str, cvss_score: float, summary: str):
        if not self.driver:
            return
        query = """
        MERGE (p:Package {name: $package_name})
        MERGE (v:Vulnerability {cveId: $cve_id})
        ON CREATE SET v.severity = $severity, v.cvssScore = $cvss_score, v.summary = $summary
        ON MATCH SET v.severity = $severity, v.cvssScore = $cvss_score, v.summary = $summary
        MERGE (p)-[:VULNERABLE_TO]->(v)
        """
        with self.driver.session() as session:
            session.run(query, package_name=package_name, cve_id=cve_id,
                        severity=severity, cvss_score=cvss_score, summary=summary)

    # -------------------------------------------------------------
    # AIM3141 Graph Traversal & Blast Radius (Lecture 35)
    # -------------------------------------------------------------
    def get_blast_radius(self, package_name: str, max_depth: int = 5) -> Dict[str, Any]:
        """
        Cypher variable-length path traversal query.
        Traverses (r:Repository)-[:DEPENDS_ON*1..max_depth]->(p:Package)
        to identify all affected upstream repositories and their exact dependency path.
        """
        if not self.driver:
            return self._fallback_blast_radius(package_name, max_depth)

        query = f"""
        MATCH (target:Package {{name: $package_name}})
        OPTIONAL MATCH path = (r:Repository)-[:DEPENDS_ON*1..{max_depth}]->(target)
        WITH r, path, length(path) AS depth, target
        WHERE r IS NOT NULL
        RETURN r.fullName AS repo_name,
               r.stars AS stars,
               r.primaryLanguage AS language,
               min(depth) AS min_depth,
               [n IN nodes(path) | coalesce(n.fullName, n.name)] AS dependency_chain
        ORDER BY min_depth ASC, stars DESC
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, package_name=package_name)
                affected = []
                seen_repos = set()
                for record in result:
                    repo_name = record["repo_name"]
                    if repo_name not in seen_repos:
                        seen_repos.add(repo_name)
                        affected.append({
                            "repository": repo_name,
                            "stars": record["stars"],
                            "language": record["language"],
                            "depth": record["min_depth"],
                            "chain": record["dependency_chain"]
                        })

                if not affected:
                    fb = self._fallback_blast_radius(package_name, max_depth)
                    if fb["total_affected"] > 0:
                        return fb

                return {
                    "target_package": package_name,
                    "total_affected": len(affected),
                    "affected_repositories": affected
                }
        except Exception as e:
            logger.warning("Neo4j blast radius query failed (%s); using fallback", str(e))
            return self._fallback_blast_radius(package_name, max_depth)

    def simulate_breaking_change(self, package_name: str) -> Dict[str, Any]:
        """
        Simulates the removal/deprecation of a package.
        Identifies which repositories will have broken direct and transitive links.
        """
        if not self.driver:
            return self._fallback_simulate_breaking_change(package_name)

        query = """
        MATCH (target:Package {name: $package_name})
        OPTIONAL MATCH (r_direct:Repository)-[:DEPENDS_ON]->(target)
        OPTIONAL MATCH (r_trans:Repository)-[:DEPENDS_ON*2..5]->(target)
        RETURN target.name AS pkg,
               collect(DISTINCT r_direct.fullName) AS direct_repos,
               collect(DISTINCT r_trans.fullName) AS transitive_repos
        """
        try:
            with self.driver.session() as session:
                res = session.run(query, package_name=package_name).single()
                if not res or not res["pkg"]:
                    return self._fallback_simulate_breaking_change(package_name)

                direct = [r for r in res["direct_repos"] if r]
                transitive = [r for r in res["transitive_repos"] if r and r not in direct]

                return {
                    "package": package_name,
                    "direct_impact_count": len(direct),
                    "transitive_impact_count": len(transitive),
                    "total_impacted": len(direct) + len(transitive),
                    "direct_repositories": direct,
                    "transitive_repositories": transitive,
                    "recommendation": f"Before removing '{package_name}', update downstream builds or migrate to an alternate package."
                }
        except Exception as e:
            logger.warning("Neo4j simulate breaking change failed (%s); using fallback", str(e))
            return self._fallback_simulate_breaking_change(package_name)

    def get_full_graph(self) -> Dict[str, Any]:
        """
        Returns all nodes and edges formatted for Cytoscape.js.
        Elements:
        - Repositories: { id, label, type: 'repository', stars, language }
        - Packages: { id, label, type: 'package', ecosystem, has_cve }
        - Vulnerabilities: { id, label, type: 'vulnerability', severity, cvss }
        - Edges: { id, source, target, label }
        """
        if not self.driver:
            return self._build_fallback_graph()

        query = """
        MATCH (n)
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN n, r, m
        """
        nodes_dict = {}
        edges_list = []

        try:
            with self.driver.session() as session:
                result = session.run(query)
                for record in result:
                    n = record["n"]
                    r = record["r"]
                    m = record["m"]

                    # Process source node
                    if n:
                        labels = list(n.labels)
                        node_type = labels[0].lower() if labels else "unknown"
                        node_id = str(n.element_id)

                        if node_type == "repository":
                            custom_id = n.get("fullName", node_id)
                            nodes_dict[custom_id] = {
                                "data": {
                                    "id": custom_id,
                                    "label": n.get("fullName", custom_id),
                                    "type": "repository",
                                    "stars": n.get("stars", 0),
                                    "language": n.get("primaryLanguage", "Unknown")
                                }
                            }
                        elif node_type == "package":
                            custom_id = f"pkg:{n.get('name')}"
                            nodes_dict[custom_id] = {
                                "data": {
                                    "id": custom_id,
                                    "label": n.get("name"),
                                    "type": "package",
                                    "ecosystem": n.get("ecosystem", "npm")
                                }
                            }
                        elif node_type == "vulnerability":
                            custom_id = f"cve:{n.get('cveId')}"
                            nodes_dict[custom_id] = {
                                "data": {
                                    "id": custom_id,
                                    "label": n.get("cveId"),
                                    "type": "vulnerability",
                                    "severity": n.get("severity", "MEDIUM"),
                                    "cvss": n.get("cvssScore", 5.0)
                                }
                            }

                    # Process target node & edge
                    if m and r:
                        m_labels = list(m.labels)
                        m_type = m_labels[0].lower() if m_labels else "unknown"

                        if m_type == "repository":
                            target_id = m.get("fullName")
                        elif m_type == "package":
                            target_id = f"pkg:{m.get('name')}"
                        elif m_type == "vulnerability":
                            target_id = f"cve:{m.get('cveId')}"
                        else:
                            target_id = str(m.element_id)

                        # Determine source ID
                        if node_type == "repository":
                            source_id = n.get("fullName")
                        elif node_type == "package":
                            source_id = f"pkg:{n.get('name')}"
                        else:
                            source_id = f"cve:{n.get('cveId')}"

                        edge_id = f"{source_id}->{target_id}:{r.type}"
                        edges_list.append({
                            "data": {
                                "id": edge_id,
                                "source": source_id,
                                "target": target_id,
                                "label": r.type
                            }
                        })

            if not nodes_dict:
                return self._build_fallback_graph()

            return {
                "nodes": list(nodes_dict.values()),
                "edges": edges_list
            }
        except Exception as e:
            logger.warning("Neo4j graph query failed (%s); falling back to offline benchmark graph", str(e))
            return self._build_fallback_graph()

    # -------------------------------------------------------------
    # Offline Fallback Engine (when Docker Neo4j is offline)
    # -------------------------------------------------------------
    def _build_fallback_graph(self) -> Dict[str, Any]:
        from backend.services.seeder import SEED_REPOSITORIES, SEED_CVES
        nodes_dict = {}
        edges_list = []

        # 1. Ingest repositories and package dependencies
        for repo in SEED_REPOSITORIES:
            rid = repo["full_name"]
            nodes_dict[rid] = {
                "data": {
                    "id": rid,
                    "label": rid,
                    "type": "repository",
                    "stars": repo.get("stars", 0),
                    "language": repo.get("primary_language", "Unknown")
                }
            }
            for dep in repo.get("direct_deps", []):
                pid = f"pkg:{dep}"
                if pid not in nodes_dict:
                    nodes_dict[pid] = {
                        "data": {
                            "id": pid,
                            "label": dep,
                            "type": "package",
                            "ecosystem": repo.get("ecosystem", "npm")
                        }
                    }
                edges_list.append({
                    "data": {
                        "id": f"{rid}->{pid}:DEPENDS_ON",
                        "source": rid,
                        "target": pid,
                        "label": "DEPENDS_ON"
                    }
                })
            for parent, child in repo.get("transitive_deps", []):
                pp_id = f"pkg:{parent}"
                cp_id = f"pkg:{child}"
                if cp_id not in nodes_dict:
                    nodes_dict[cp_id] = {
                        "data": {
                            "id": cp_id,
                            "label": child,
                            "type": "package",
                            "ecosystem": repo.get("ecosystem", "npm")
                        }
                    }
                edges_list.append({
                    "data": {
                        "id": f"{pp_id}->{cp_id}:DEPENDS_ON",
                        "source": pp_id,
                        "target": cp_id,
                        "label": "DEPENDS_ON"
                    }
                })

        # 2. Ingest CVE vulnerability nodes
        for cve in SEED_CVES:
            cid = f"cve:{cve['cve_id']}"
            nodes_dict[cid] = {
                "data": {
                    "id": cid,
                    "label": cve["cve_id"],
                    "type": "vulnerability",
                    "severity": cve.get("severity", "MEDIUM"),
                    "cvss": cve.get("cvss_score", 5.0)
                }
            }
            pkg_id = f"pkg:{cve['package']}"
            if pkg_id in nodes_dict:
                edges_list.append({
                    "data": {
                        "id": f"{pkg_id}->{cid}:VULNERABLE_TO",
                        "source": pkg_id,
                        "target": cid,
                        "label": "VULNERABLE_TO"
                    }
                })

        return {
            "nodes": list(nodes_dict.values()),
            "edges": edges_list
        }

    def _fallback_blast_radius(self, package_name: str, max_depth: int = 5) -> Dict[str, Any]:
        from collections import deque
        from backend.services.seeder import SEED_REPOSITORIES
        pkg_lower = package_name.lower()

        # Build reverse dependency graph: child -> list of (parent, type, label)
        reverse_graph = {}
        repo_info = {}
        for repo in SEED_REPOSITORIES:
            rf = repo["full_name"]
            repo_info[rf] = {
                "stars": repo.get("stars", 0),
                "language": repo.get("primary_language", "Unknown")
            }
            for d in repo.get("direct_deps", []):
                dl = d.lower()
                reverse_graph.setdefault(dl, []).append((rf, "repo", d))
            for p, c in repo.get("transitive_deps", []):
                cl = c.lower()
                reverse_graph.setdefault(cl, []).append((p, "pkg", c))

        # BFS to discover all affected repositories and their exact dependency chain
        # Queue item: (curr_lower, chain_from_pkg_to_current)
        queue = deque([(pkg_lower, [package_name])])
        visited_nodes = {pkg_lower}
        affected = []
        seen_repos = set()

        while queue:
            curr, chain = queue.popleft()
            if len(chain) > max_depth + 1:
                continue

            for parent_name, node_type, original_name in reverse_graph.get(curr, []):
                parent_lower = parent_name.lower()
                new_chain = [parent_name] + chain

                if node_type == "repo":
                    if parent_name not in seen_repos:
                        seen_repos.add(parent_name)
                        info = repo_info.get(parent_name, {})
                        affected.append({
                            "repository": parent_name,
                            "stars": info.get("stars", 0),
                            "language": info.get("language", "Unknown"),
                            "depth": len(new_chain) - 1,
                            "chain": new_chain
                        })
                else:
                    if parent_lower not in visited_nodes:
                        visited_nodes.add(parent_lower)
                        queue.append((parent_lower, [parent_name] + chain))

        affected.sort(key=lambda x: (x["depth"], -x["stars"]))
        return {
            "target_package": package_name,
            "total_affected": len(affected),
            "affected_repositories": affected
        }

    def _fallback_simulate_breaking_change(self, package_name: str) -> Dict[str, Any]:
        blast = self._fallback_blast_radius(package_name, max_depth=5)
        direct = [a["repository"] for a in blast["affected_repositories"] if a["depth"] == 1]
        transitive = [a["repository"] for a in blast["affected_repositories"] if a["depth"] > 1]
        return {
            "package": package_name,
            "direct_repositories": direct,
            "transitive_repositories": transitive,
            "direct_impact_count": len(direct),
            "transitive_impact_count": len(transitive),
            "total_impacted": len(direct) + len(transitive),
            "recommendation": f"Before removing '{package_name}', update downstream builds or migrate to an alternate package."
        }

neo4j_manager = Neo4jManager()
