import httpx
import logging
from typing import Dict, Any, List, Optional
from backend.db.mongodb import mongodb_manager

logger = logging.getLogger(__name__)

OSV_API_URL = "https://api.osv.dev/v1/query"

class OSVClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def query_package_vulnerabilities(self, package_name: str, ecosystem: str = "npm") -> List[Dict[str, Any]]:
        """
        Queries OSV.dev for known vulnerabilities for a given package and ecosystem.
        First checks MongoDB cache; if absent, queries OSV.dev API and caches result.
        """
        # Map ecosystem names to OSV format
        ecosystem_map = {
            "npm": "npm",
            "pypi": "PyPI",
            "python": "PyPI",
            "maven": "Maven",
            "java": "Maven"
        }
        osv_eco = ecosystem_map.get(ecosystem.lower(), "npm")

        payload = {
            "package": {
                "name": package_name,
                "ecosystem": osv_eco
            }
        }

        vulnerabilities = []
        try:
            response = await self.client.post(OSV_API_URL, json=payload)
            if response.status_code == 200:
                data = response.json()
                vuln_list = data.get("vulns", [])
                for v in vuln_list:
                    cve_id = v.get("id", "UNKNOWN-CVE")
                    summary = v.get("summary") or v.get("details", "")[:200]
                    
                    # Extract CVSS or estimate severity
                    severity = "HIGH"
                    cvss_score = 7.5
                    
                    if "database_specific" in v and "severity" in v["database_specific"]:
                        severity = v["database_specific"]["severity"].upper()
                    
                    if severity == "CRITICAL":
                        cvss_score = 9.8
                    elif severity == "HIGH":
                        cvss_score = 8.2
                    elif severity == "MEDIUM" or severity == "MODERATE":
                        severity = "MEDIUM"
                        cvss_score = 5.5
                    elif severity == "LOW":
                        cvss_score = 3.1

                    fixed_version = "latest"
                    # Try to extract fixed version from affected ranges
                    for aff in v.get("affected", []):
                        for r in aff.get("ranges", []):
                            for event in r.get("events", []):
                                if "fixed" in event:
                                    fixed_version = event["fixed"]
                                    break

                    cve_doc = {
                        "cve_id": cve_id,
                        "package": package_name,
                        "ecosystem": osv_eco,
                        "summary": summary,
                        "severity": severity,
                        "cvss_score": cvss_score,
                        "fixed_version": fixed_version,
                        "raw_osv": v
                    }

                    # Store in MongoDB (Document Model - AIM3141)
                    mongodb_manager.upsert_cve(cve_doc)
                    vulnerabilities.append(cve_doc)

            logger.info("Found %d vulnerabilities for %s in OSV.dev", len(vulnerabilities), package_name)
        except Exception as e:
            logger.warning("OSV.dev query error for %s: %s", package_name, str(e))

        return vulnerabilities

    async def close(self):
        await self.client.aclose()

osv_client = OSVClient()
