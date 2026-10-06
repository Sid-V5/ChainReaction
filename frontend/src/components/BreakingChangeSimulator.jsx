import React, { useState } from 'react';
import { GitPullRequest, AlertOctagon, ShieldAlert, Terminal, RefreshCw, Layers } from 'lucide-react';
import { simulateBreakingChange } from '../api';

export default function BreakingChangeSimulator() {
  const [targetPackage, setTargetPackage] = useState('body-parser');
  const [simulationResult, setSimulationResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const samplePackages = ['body-parser', 'werkzeug', 'log4j-core', 'requests', 'follow-redirects'];

  const handleSimulate = async (pkg = targetPackage) => {
    if (!pkg.trim()) return;
    setLoading(true);
    try {
      const res = await simulateBreakingChange(pkg);
      setSimulationResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4 shadow-sm flex flex-col h-full overflow-hidden transition-colors duration-200">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-zinc-100 dark:border-zinc-800">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700">
            <GitPullRequest className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xs font-bold text-zinc-900 dark:text-zinc-100 tracking-wide uppercase">
                Breaking Change Simulator
              </h2>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-700">
                Severance Engine
              </span>
            </div>
            <p className="text-[11px] text-zinc-500 dark:text-zinc-400">
              Graph Severance: Simulate Dependency Deprecation & Cascades
            </p>
          </div>
        </div>
      </div>

      {/* Target Package Selector Box */}
      <div className="mt-3 p-3 bg-zinc-50 dark:bg-zinc-900/60 rounded-lg border border-zinc-200 dark:border-zinc-800/80 space-y-2.5">
        <label className="text-[11px] font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider block">
          Target Dependency to Sever
        </label>
        <div className="flex gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={targetPackage}
              onChange={(e) => setTargetPackage(e.target.value)}
              placeholder="e.g. body-parser or werkzeug"
              className="w-full bg-white dark:bg-zinc-950 border border-zinc-300 dark:border-zinc-800 rounded-lg px-3 py-1.5 text-xs font-mono text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:border-zinc-500 transition-colors"
              onKeyDown={(e) => e.key === 'Enter' && handleSimulate()}
            />
          </div>
          <button
            onClick={() => handleSimulate()}
            disabled={loading || !targetPackage.trim()}
            className="px-3.5 py-1.5 bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-white text-white dark:text-zinc-900 rounded-lg text-xs font-semibold transition-colors disabled:opacity-50 flex items-center gap-1.5 shadow-sm"
          >
            {loading ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Simulating...</span>
              </>
            ) : (
              <span>Simulate Sever</span>
            )}
          </button>
        </div>

        {/* Quick select buttons (clean neutral pills) */}
        <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
          <span className="text-[11px] text-zinc-400">Presets:</span>
          {samplePackages.map((pkg) => (
            <button
              key={pkg}
              onClick={() => {
                setTargetPackage(pkg);
                handleSimulate(pkg);
              }}
              className={`px-2 py-0.5 rounded text-[11px] font-mono transition-colors ${
                targetPackage === pkg
                  ? 'bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 font-semibold'
                  : 'bg-white dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-700'
              }`}
            >
              {pkg}
            </button>
          ))}
        </div>
      </div>

      {/* Results View Area */}
      <div className="mt-3 flex-1 overflow-y-auto space-y-3 pr-1 text-xs">
        {simulationResult ? (
          <div className="space-y-3">
            {/* Impact Metric Header Card */}
            <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-900 dark:text-zinc-100">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <AlertOctagon className="w-4 h-4 text-rose-500" />
                  <span className="font-semibold text-xs">
                    Impact Analysis for "{simulationResult.package}"
                  </span>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-900">
                  {simulationResult.total_impacted} Impacted Repos
                </span>
              </div>
              <p className="text-[11px] text-zinc-600 dark:text-zinc-400 leading-relaxed">
                Removing this dependency severs <strong className="text-rose-600 dark:text-rose-400 font-semibold">{simulationResult.direct_impact_count}</strong> direct build pipelines and cascades into <strong className="text-zinc-800 dark:text-zinc-200 font-semibold">{simulationResult.transitive_impact_count}</strong> transitive downstream services.
              </p>
            </div>

            {/* Direct Impact Ledger */}
            <div className="p-3 bg-zinc-50 dark:bg-zinc-900/60 rounded-lg border border-zinc-200 dark:border-zinc-800">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-rose-600 dark:text-rose-400 flex items-center gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  Direct Dependents (Immediate Build Failure):
                </span>
                <span className="text-[10px] font-mono text-zinc-400">
                  {simulationResult.direct_repositories?.length || 0} Repos
                </span>
              </div>

              {simulationResult.direct_repositories?.length === 0 ? (
                <div className="p-2 text-center text-zinc-400 font-mono text-[11px] bg-white dark:bg-zinc-950 rounded border border-zinc-200 dark:border-zinc-800">
                  No direct consumers found in current scan scope.
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                  {simulationResult.direct_repositories.map((repo, i) => (
                    <div
                      key={i}
                      className="px-2.5 py-1.5 bg-white dark:bg-zinc-950 text-rose-600 dark:text-rose-400 rounded font-mono text-[11px] border border-rose-200 dark:border-rose-900/40 flex items-center justify-between"
                    >
                      <span className="truncate">{repo}</span>
                      <span className="text-[9px] uppercase font-bold text-rose-500 ml-1">BREAK</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Transitive Impact Ledger */}
            <div className="p-3 bg-zinc-50 dark:bg-zinc-900/60 rounded-lg border border-zinc-200 dark:border-zinc-800">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-zinc-700 dark:text-zinc-300 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5" />
                  Transitive Dependents (Multi-Hop Cascade):
                </span>
                <span className="text-[10px] font-mono text-zinc-400">
                  {simulationResult.transitive_repositories?.length || 0} Repos
                </span>
              </div>

              {simulationResult.transitive_repositories?.length === 0 ? (
                <div className="p-2 text-center text-zinc-400 font-mono text-[11px] bg-white dark:bg-zinc-950 rounded border border-zinc-200 dark:border-zinc-800">
                  No multi-hop downstream dependencies affected.
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                  {simulationResult.transitive_repositories.map((repo, i) => (
                    <div
                      key={i}
                      className="px-2.5 py-1.5 bg-white dark:bg-zinc-950 text-zinc-700 dark:text-zinc-300 rounded font-mono text-[11px] border border-zinc-200 dark:border-zinc-800 flex items-center justify-between"
                    >
                      <span className="truncate">{repo}</span>
                      <span className="text-[9px] uppercase font-bold text-zinc-500 ml-1">CASCADE</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Cypher Traversal Query Inspection */}
            <div className="p-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-[11px]">
              <div className="flex items-center gap-1.5 text-zinc-700 dark:text-zinc-300 font-mono font-medium mb-1">
                <Terminal className="w-3.5 h-3.5" />
                <span>Graph Traversal Query:</span>
              </div>
              <pre className="font-mono text-[10px] text-zinc-600 dark:text-zinc-400 bg-white dark:bg-zinc-950 p-2 rounded border border-zinc-200 dark:border-zinc-800/80 overflow-x-auto leading-relaxed">
{`// 1. Direct dependencies:
MATCH (p:Package {name: "${simulationResult.package}"})<-[:DEPENDS_ON]-(r:Repository)
RETURN r.fullName

// 2. Transitive dependents (depth 2 to 5):
MATCH (p:Package {name: "${simulationResult.package}"})<-[:DEPENDS_ON*2..5]-(r:Repository)
RETURN DISTINCT r.fullName`}
              </pre>
            </div>
          </div>
        ) : (
          <div className="p-8 text-center text-zinc-400 dark:text-zinc-500 font-mono text-xs flex flex-col items-center justify-center gap-2 border border-dashed border-zinc-200 dark:border-zinc-800 rounded-lg">
            <GitPullRequest className="w-6 h-6 text-zinc-400" />
            <span>Select a package above and execute a breaking change simulation.</span>
          </div>
        )}
      </div>
    </div>
  );
}
