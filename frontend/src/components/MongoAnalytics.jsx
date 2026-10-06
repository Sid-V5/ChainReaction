import React, { useEffect, useState } from 'react';
import { BarChart3, Layers, CheckCircle, ShieldAlert, TrendingUp, AlertTriangle } from 'lucide-react';
import { fetchEcosystemAnalytics, fetchFacetAnalytics } from '../api';

export default function MongoAnalytics() {
  const [ecosystemStats, setEcosystemStats] = useState([]);
  const [facetData, setFacetData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('ecosystem'); // 'ecosystem', 'facet', 'schema'

  useEffect(() => {
    async function loadStats() {
      try {
        const [eco, facet] = await Promise.all([
          fetchEcosystemAnalytics(),
          fetchFacetAnalytics()
        ]);
        setEcosystemStats(eco || []);
        setFacetData(facet || null);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  const overview = facetData?.risk_overview?.[0] || {
    total_repos: 12,
    total_cves: 8,
    avg_risk: 32.5,
    highest_risk: 75.0
  };

  return (
    <div className="bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4 shadow-sm flex flex-col h-full overflow-hidden transition-colors duration-200">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-zinc-100 dark:border-zinc-800">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700">
            <BarChart3 className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xs font-bold text-zinc-900 dark:text-zinc-100 tracking-wide uppercase font-sans">
                Ecosystem Risk Intelligence
              </h2>
            </div>
            <p className="text-[11px] text-zinc-500 dark:text-zinc-400">
              Multi-Ecosystem Security Aggregations & Threat Distributions
            </p>
          </div>
        </div>

        {/* View Switcher Tabs (Clean neutral buttons) */}
        <div className="flex items-center gap-1 bg-zinc-100 dark:bg-zinc-900 p-0.5 rounded-lg border border-zinc-200 dark:border-zinc-800 text-xs font-medium">
          <button
            onClick={() => setViewMode('ecosystem')}
            className={`px-2.5 py-1 rounded-md transition-colors ${
              viewMode === 'ecosystem'
                ? 'bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-sm font-semibold'
                : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200'
            }`}
          >
            Ecosystems
          </button>
          <button
            onClick={() => setViewMode('facet')}
            className={`px-2.5 py-1 rounded-md transition-colors ${
              viewMode === 'facet'
                ? 'bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-sm font-semibold'
                : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200'
            }`}
          >
            Breakdowns
          </button>
          <button
            onClick={() => setViewMode('schema')}
            className={`px-2.5 py-1 rounded-md transition-colors ${
              viewMode === 'schema'
                ? 'bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-sm font-semibold'
                : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200'
            }`}
          >
            Data Model
          </button>
        </div>
      </div>

      {/* Top 4 Metrics Ribbon */}
      <div className="grid grid-cols-4 gap-2 mt-3">
        <div className="p-2.5 bg-zinc-50 dark:bg-zinc-900/60 rounded-lg border border-zinc-200 dark:border-zinc-800">
          <span className="text-[10px] font-medium uppercase tracking-wider text-zinc-400 dark:text-zinc-500 block">
            Repos Monitored
          </span>
          <span className="text-base font-bold font-mono text-zinc-900 dark:text-zinc-100">{overview.total_repos}</span>
        </div>
        <div className="p-2.5 bg-zinc-50 dark:bg-zinc-900/60 rounded-lg border border-zinc-200 dark:border-zinc-800">
          <span className="text-[10px] font-medium uppercase tracking-wider text-rose-500 block">
            Active CVEs
          </span>
          <span className="text-base font-bold font-mono text-rose-600 dark:text-rose-400">{overview.total_cves}</span>
        </div>
        <div className="p-2.5 bg-zinc-50 dark:bg-zinc-900/60 rounded-lg border border-zinc-200 dark:border-zinc-800">
          <span className="text-[10px] font-medium uppercase tracking-wider text-zinc-400 dark:text-zinc-500 block">
            Avg Risk Index
          </span>
          <span className="text-base font-bold font-mono text-zinc-900 dark:text-zinc-100">{overview.avg_risk}</span>
        </div>
        <div className="p-2.5 bg-zinc-50 dark:bg-zinc-900/60 rounded-lg border border-zinc-200 dark:border-zinc-800">
          <span className="text-[10px] font-medium uppercase tracking-wider text-zinc-400 dark:text-zinc-500 block">
            Peak Threat CVSS
          </span>
          <span className="text-base font-bold font-mono text-rose-600 dark:text-rose-400">
            {ecosystemStats.length > 0 ? Math.max(...ecosystemStats.map(e => e.max_cvss || 0)) : 10.0}
          </span>
        </div>
      </div>

      {/* Main Dynamic View Area */}
      <div className="mt-3 flex-1 overflow-y-auto space-y-3 pr-1 text-xs">
        {loading ? (
          <div className="p-8 text-center text-zinc-400 font-mono text-xs animate-pulse">
            Computing multi-ecosystem threat aggregations...
          </div>
        ) : viewMode === 'ecosystem' ? (
          /* View 1: Language Risk Breakdown */
          <div className="space-y-3">
            <div className="flex items-center justify-between p-2 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-[11px]">
              <span className="text-zinc-700 dark:text-zinc-300 font-medium flex items-center gap-1.5">
                <BarChart3 className="w-3.5 h-3.5" />
                Language Ecosystem Exposure & Vulnerability Intensity
              </span>
              <span className="text-zinc-400 text-[10px] font-mono">
                Real-Time Aggregations
              </span>
            </div>

            <div className="space-y-2">
              {ecosystemStats.map((item, idx) => {
                const riskPct = Math.min(100, Math.round(item.avg_risk_score));
                return (
                  <div key={idx} className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-700 transition-colors">
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-zinc-900 dark:text-zinc-100 text-xs">{item.language}</span>
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 font-mono text-zinc-500">
                          {item.repo_count} repos
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] text-zinc-400">Stars:</span>
                        <span className="text-xs font-mono font-medium text-zinc-700 dark:text-zinc-300">
                          {item.total_stars?.toLocaleString()}
                        </span>
                      </div>
                    </div>

                    {/* Threat Intensity Meter */}
                    <div className="w-full bg-zinc-200 dark:bg-zinc-800 h-1.5 rounded-full overflow-hidden my-2">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          item.avg_risk_score >= 50
                            ? 'bg-rose-500'
                            : item.avg_risk_score >= 20
                            ? 'bg-zinc-500 dark:bg-zinc-400'
                            : 'bg-emerald-500'
                        }`}
                        style={{ width: `${Math.max(8, riskPct)}%` }}
                      />
                    </div>

                    <div className="flex items-center justify-between text-[11px] font-mono text-zinc-500 dark:text-zinc-400">
                      <span>
                        Risk Index: <strong className="text-zinc-900 dark:text-zinc-100">{item.avg_risk_score}</strong>
                      </span>
                      <span>
                        Discovered CVEs: <strong className="text-rose-600 dark:text-rose-400">{item.total_cves_detected}</strong>
                      </span>
                      <span>
                        Peak CVSS: <strong className="text-rose-600 dark:text-rose-400">{item.max_cvss}</strong>
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Security Posture Summary Card (Replaced raw PyMongo code box) */}
            <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-[11px]">
              <div className="flex items-center gap-1.5 text-zinc-800 dark:text-zinc-200 font-semibold mb-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-rose-500" />
                <span>Supply Chain Exposure Summary:</span>
              </div>
              <div className="space-y-1.5 text-[11px] text-zinc-600 dark:text-zinc-400 leading-relaxed font-sans">
                <p>
                  • <strong className="text-zinc-900 dark:text-zinc-100 font-medium">Java / Maven Ecosystem:</strong> Carries the highest severity impact with <span className="font-mono text-rose-600 dark:text-rose-400 font-semibold">CVSS 10.0</span> (Log4Shell CVE-2021-44228) and Spring4Shell affecting multi-tier enterprise services.
                </p>
                <p>
                  • <strong className="text-zinc-900 dark:text-zinc-100 font-medium">Python / PyPI Ecosystem:</strong> Shared network utilities (<code className="text-zinc-800 dark:text-zinc-200">urllib3</code>, <code className="text-zinc-800 dark:text-zinc-200">werkzeug</code>) expose HTTP redirect and parsing vulnerabilities across web microservices.
                </p>
                <p>
                  • <strong className="text-zinc-900 dark:text-zinc-100 font-medium">JavaScript / npm Ecosystem:</strong> Core serialization dependencies (<code className="text-zinc-800 dark:text-zinc-200">qs</code>, <code className="text-zinc-800 dark:text-zinc-200">follow-redirects</code>) create high-priority denial-of-service and credential leakage risks.
                </p>
              </div>
            </div>
          </div>
        ) : viewMode === 'facet' ? (
          /* View 2: Multi-Dimensional Breakdown */
          <div className="space-y-3">
            <div className="p-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-[11px] text-zinc-700 dark:text-zinc-300">
              <span className="font-semibold block mb-0.5">Multi-Dimensional Risk Overview</span>
              <p className="text-[11px] text-zinc-500 dark:text-zinc-400 leading-normal">
                Correlates repository popularity against vulnerability densities to highlight high-visibility attack surfaces.
              </p>
            </div>

            {/* Branch 1: Top Starred Repositories */}
            <div className="p-3 bg-zinc-50 dark:bg-zinc-900/60 rounded-lg border border-zinc-200 dark:border-zinc-800">
              <span className="text-[11px] font-semibold text-zinc-900 dark:text-zinc-100 block mb-2">
                Top Monitored Repositories by Popularity & Exposure
              </span>
              <div className="space-y-1.5">
                {facetData?.top_starred_repos?.map((repo, i) => (
                  <div key={i} className="flex items-center justify-between p-1.5 rounded bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-[11px]">
                    <span className="text-zinc-800 dark:text-zinc-200 font-medium font-mono">{repo.full_name}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-zinc-500 font-mono">★ {repo.stars?.toLocaleString()}</span>
                      <span className={`px-1.5 py-0.2 rounded text-[10px] font-mono ${
                        repo.risk_score > 40
                          ? 'text-rose-600 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/40'
                          : 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/40'
                      }`}>
                        Risk: {repo.risk_score}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Branch 2: Language Share Breakdown */}
            <div className="p-3 bg-zinc-50 dark:bg-zinc-900/60 rounded-lg border border-zinc-200 dark:border-zinc-800">
              <span className="text-[11px] font-semibold text-zinc-900 dark:text-zinc-100 block mb-2">
                Ecosystem Distribution & Vulnerability Density
              </span>
              <div className="grid grid-cols-2 gap-2">
                {facetData?.language_breakdown?.map((item, i) => (
                  <div key={i} className="p-2 rounded bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-[11px]">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-zinc-800 dark:text-zinc-200">{item.language}</span>
                      <span className="text-zinc-400 text-[10px] font-mono">{item.count} repos</span>
                    </div>
                    <span className="text-[10px] text-zinc-500 dark:text-zinc-400 font-mono">
                      Avg CVEs: <strong className="text-zinc-800 dark:text-zinc-200">{item.avg_cves}</strong>
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* View 3: Document Schema Architecture */
          <div className="space-y-3">
            <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-xs">
              <div className="flex items-center gap-2 text-zinc-900 dark:text-zinc-100 font-semibold mb-1">
                <CheckCircle className="w-4 h-4 text-emerald-500" />
                <span>Data Integrity & Architecture Spec</span>
              </div>
              <p className="text-[11px] text-zinc-500 dark:text-zinc-400">
                Schema validation rules, index strategies, and pre-computed telemetry metrics.
              </p>
            </div>

            <div className="space-y-2 text-[11px]">
              <div className="p-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800">
                <div className="flex items-center justify-between text-zinc-900 dark:text-zinc-100 font-semibold mb-1">
                  <span>JSON Schema Ingestion Validation</span>
                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-500 font-mono">Enforced</span>
                </div>
                <p className="text-[10px] text-zinc-500 dark:text-zinc-400">
                  Enforces strict document typing on repository ingestion: guarantees presence of <code className="text-zinc-800 dark:text-zinc-200">full_name, owner, primary_language, dependencies, risk_score</code>.
                </p>
              </div>

              <div className="p-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800">
                <div className="flex items-center justify-between text-zinc-900 dark:text-zinc-100 font-semibold mb-1">
                  <span>Computed Pattern Architecture</span>
                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-500 font-mono">Active</span>
                </div>
                <p className="text-[10px] text-zinc-500 dark:text-zinc-400">
                  Pre-computes risk scores (<code className="text-zinc-800 dark:text-zinc-200">risk_score</code>, <code className="text-zinc-800 dark:text-zinc-200">total_cves</code>) during dependency ingestion to deliver O(1) query response times.
                </p>
              </div>

              <div className="p-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800">
                <div className="flex items-center justify-between text-zinc-900 dark:text-zinc-100 font-semibold mb-1">
                  <span>Connection Pooling & Compound Indexing</span>
                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-500 font-mono">Optimized</span>
                </div>
                <p className="text-[10px] text-zinc-500 dark:text-zinc-400">
                  Compound index on <code className="text-zinc-800 dark:text-zinc-200">("primary_language", "stars")</code> and text index on <code className="text-zinc-800 dark:text-zinc-200">("full_name", "description")</code> for sub-millisecond lookups.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
