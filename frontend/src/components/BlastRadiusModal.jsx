import React, { useState } from 'react';
import { Target, Zap, ArrowRight, ShieldAlert, CheckCircle2, Flame, Layers } from 'lucide-react';
import { queryBlastRadius } from '../api';

export default function BlastRadiusModal({ onHighlightChains }) {
  const [packageName, setPackageName] = useState('log4j-core');
  const [depth, setDepth] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const quickPackages = ['log4j-core', 'requests', 'qs', 'werkzeug', 'follow-redirects', 'urllib3'];

  const handleQuery = async (pkgToQuery = packageName) => {
    setLoading(true);
    try {
      const data = await queryBlastRadius(pkgToQuery, depth);
      setResult(data);
      if (data.affected_repositories && data.affected_repositories.length > 0) {
        const chains = data.affected_repositories.map(r => r.chain);
        onHighlightChains(chains);
      } else {
        onHighlightChains([]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-zinc-950 p-4 flex flex-col h-full overflow-hidden text-xs transition-colors duration-200">
      {/* Header telemetry */}
      <div className="pb-3 mb-3 border-b border-zinc-100 dark:border-zinc-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 flex items-center justify-center text-rose-600 dark:text-rose-400">
            <Flame className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-xs font-bold uppercase tracking-wider text-zinc-900 dark:text-zinc-100 font-sans">
              Transitive Blast Radius
            </h2>
            <p className="text-[11px] text-zinc-500 dark:text-zinc-400">
              Dependency Graph Traversal: Multi-Hop Upstream Impact Analysis
            </p>
          </div>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded font-mono font-medium bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300">
          Max Depth: {depth} Hops
        </span>
      </div>

      {/* Input query form */}
      <div className="space-y-3">
        <div>
          <label className="text-[11px] text-zinc-500 dark:text-zinc-400 uppercase font-medium block mb-1">
            Target Package Identifier
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={packageName}
              onChange={(e) => setPackageName(e.target.value)}
              placeholder="e.g. log4j-core"
              className="flex-1 bg-zinc-50 dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:border-zinc-500 transition-colors font-mono"
              onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
            />
            <button
              onClick={() => handleQuery()}
              disabled={loading || !packageName.trim()}
              className="px-3.5 py-1.5 bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs rounded-lg transition-colors shadow-sm disabled:opacity-50 flex items-center gap-1.5"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>{loading ? 'Traversing...' : 'Trace Impact'}</span>
            </button>
          </div>
        </div>

        {/* Quick select pills */}
        <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
          <span className="text-[11px] text-zinc-400">Presets:</span>
          {quickPackages.map(pkg => (
            <button
              key={pkg}
              onClick={() => {
                setPackageName(pkg);
                handleQuery(pkg);
              }}
              className="px-2 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 border border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 text-[11px] font-mono transition-colors"
            >
              {pkg}
            </button>
          ))}
        </div>

        {/* Traversal depth slider */}
        <div className="flex items-center justify-between text-xs pt-1 border-t border-zinc-100 dark:border-zinc-800">
          <span className="text-zinc-500 dark:text-zinc-400">Max Hop Traversal Limit:</span>
          <div className="flex items-center gap-2">
            <input
              type="range"
              min="1"
              max="6"
              value={depth}
              onChange={(e) => setDepth(Number(e.target.value))}
              className="w-28 accent-zinc-900 dark:accent-zinc-100 cursor-pointer"
            />
            <span className="font-mono font-semibold text-zinc-900 dark:text-zinc-100">{depth} Hops</span>
          </div>
        </div>
      </div>

      {/* Traversal Output Results */}
      <div className="mt-3 flex-1 overflow-y-auto space-y-2.5 pr-1">
        {result && (
          <div>
            {/* Engine Telemetry Card */}
            <div className="flex items-center justify-between p-2 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-xs mb-2.5">
              <span className="text-zinc-500 dark:text-zinc-400 font-medium">Execution Engine:</span>
              {result.cache_hit ? (
                <span className="text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1 font-mono text-[11px]">
                  ⚡ Fast Cache Hit (&lt;1ms)
                </span>
              ) : (
                <span className="text-zinc-700 dark:text-zinc-300 font-semibold flex items-center gap-1 font-mono text-[11px]">
                  Live Graph Traversal
                </span>
              )}
            </div>

            {/* Summary Blast Scope */}
            <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-xs mb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-zinc-900 dark:text-zinc-100">
                  Target Component: <span className="font-mono">{result.target_package}</span>
                </span>
                <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] ${
                  result.total_affected > 0
                    ? 'bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-900'
                    : 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900'
                }`}>
                  {result.total_affected} Services Exposed
                </span>
              </div>
              <p className="text-[11px] text-zinc-500 dark:text-zinc-400 leading-relaxed">
                {result.total_affected > 0
                  ? `Vulnerabilities in ${result.target_package} propagate transitively to ${result.total_affected} upstream microservices.`
                  : `No repositories in the current topology depend on ${result.target_package}.`}
              </p>
            </div>

            {/* Affected Repositories List */}
            {result.affected_repositories && result.affected_repositories.length > 0 && (
              <div className="space-y-2">
                <span className="text-[11px] font-semibold text-zinc-700 dark:text-zinc-300 uppercase tracking-wider block">
                  Exposed Microservices:
                </span>
                {result.affected_repositories.map((repo, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-lg bg-white dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800 text-xs shadow-sm hover:border-zinc-300 dark:hover:border-zinc-700 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-zinc-900 dark:text-zinc-100">{repo.repository}</span>
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 font-mono text-zinc-500">
                          {repo.language}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-900/40">
                        Hop Depth: {repo.depth}
                      </span>
                    </div>

                    {/* Step by step dependency chain */}
                    <div className="mt-1 flex items-center gap-1.5 overflow-x-auto text-[10px] font-mono text-zinc-500 dark:text-zinc-400 py-1">
                      {repo.chain?.map((step, sIdx) => (
                        <React.Fragment key={sIdx}>
                          <span className={`px-1.5 py-0.5 rounded ${
                            sIdx === 0
                              ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 font-semibold'
                              : sIdx === repo.chain.length - 1
                              ? 'bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 font-semibold'
                              : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400'
                          }`}>
                            {step}
                          </span>
                          {sIdx < repo.chain.length - 1 && (
                            <ArrowRight className="w-2.5 h-2.5 text-zinc-400 flex-shrink-0" />
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
