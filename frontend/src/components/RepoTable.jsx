import React, { useState } from 'react';
import { FolderGit2, Star, ShieldAlert, Search } from 'lucide-react';

export default function RepoTable({ repos, onSelectRepo }) {
  const [filter, setFilter] = useState('');

  const filteredRepos = repos.filter((r) =>
    r.full_name?.toLowerCase().includes(filter.toLowerCase()) ||
    r.primary_language?.toLowerCase().includes(filter.toLowerCase())
  );

  const formatStars = (stars) => {
    if (!stars && stars !== 0) return '0';
    if (stars >= 1000) {
      return `${(stars / 1000).toFixed(stars >= 10000 ? 0 : 1)}k`;
    }
    return stars.toString();
  };

  const getRiskBadge = (score) => {
    if (score >= 60) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded font-mono text-[10px] font-bold bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-900 whitespace-nowrap shadow-xs">
          <span>{score}</span>
          <span className="text-[8px] uppercase tracking-wider font-sans font-extrabold text-rose-600 dark:text-rose-400">CRIT</span>
        </span>
      );
    } else if (score >= 30) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded font-mono text-[10px] font-medium bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-800 whitespace-nowrap">
          <span>{score}</span>
          <span className="text-[8px] uppercase tracking-wider font-sans font-bold text-amber-600 dark:text-amber-400">ELEV</span>
        </span>
      );
    } else if (score > 0) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded font-mono text-[10px] font-medium bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-700 whitespace-nowrap">
          <span>{score}</span>
          <span className="text-[8px] uppercase tracking-wider font-sans font-bold">LOW</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded font-mono text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900 whitespace-nowrap shadow-xs">
        <span>0</span>
        <span className="text-[8px] uppercase tracking-wider font-sans font-bold">CLEAN</span>
      </span>
    );
  };

  return (
    <div className="bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4 shadow-sm flex flex-col h-full overflow-hidden transition-colors duration-200">
      {/* Table Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-3 border-b border-zinc-100 dark:border-zinc-800 gap-2">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700">
            <FolderGit2 className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xs font-bold text-zinc-900 dark:text-zinc-100 tracking-wide uppercase font-sans">
                Monitored Repositories
              </h2>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-700">
                {repos.length} Ingested
              </span>
            </div>
            <p className="text-[11px] text-zinc-500 dark:text-zinc-400">
              Dependency Inventory, CVE Exposures & Risk Telemetry
            </p>
          </div>
        </div>

        {/* Search Filter Input */}
        <div className="relative">
          <input
            type="text"
            placeholder="Filter repos..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-40 sm:w-44 bg-zinc-50 dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 outline-none focus:border-zinc-500 transition-colors"
          />
          <Search className="w-3.5 h-3.5 text-zinc-400 absolute left-2.5 top-2.5" />
        </div>
      </div>

      {/* Repositories Monospace Table */}
      <div className="mt-3 flex-1 overflow-y-auto overflow-x-hidden pr-0.5">
        <div className="border border-zinc-200 dark:border-zinc-800 rounded-lg overflow-hidden bg-white dark:bg-zinc-900/40">
          <table className="w-full text-left text-xs table-fixed">
            <colgroup>
              <col className="w-[38%]" />
              <col className="w-[15%]" />
              <col className="w-[15%]" />
              <col className="w-[10%]" />
              <col className="w-[10%]" />
              <col className="w-[22%]" />
            </colgroup>
            <thead className="bg-zinc-50 dark:bg-zinc-900 text-zinc-500 dark:text-zinc-400 border-b border-zinc-200 dark:border-zinc-800 font-semibold text-[11px]">
              <tr>
                <th className="py-2.5 px-3">Repository</th>
                <th className="py-2.5 px-1.5">Lang</th>
                <th className="py-2.5 px-1.5">Stars</th>
                <th className="py-2.5 px-1 text-center">Deps</th>
                <th className="py-2.5 px-1 text-center">CVEs</th>
                <th className="py-2.5 px-3 text-right">Risk Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800/80 text-[11px]">
              {filteredRepos.map((repo, idx) => (
                <tr
                  key={idx}
                  onClick={() => onSelectRepo(repo.full_name)}
                  className="hover:bg-zinc-50 dark:hover:bg-zinc-900/60 transition-colors cursor-pointer group"
                >
                  <td className="py-2 px-3 font-medium font-mono text-zinc-900 dark:text-zinc-100 group-hover:text-zinc-600 dark:group-hover:text-zinc-300 transition-colors">
                    <span className="truncate block" title={repo.full_name}>
                      {repo.full_name}
                    </span>
                  </td>
                  <td className="py-2 px-1.5 whitespace-nowrap">
                    <span className="px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-600 dark:text-zinc-400 text-[10px] font-mono">
                      {repo.primary_language === 'JavaScript' ? 'JS' : repo.primary_language}
                    </span>
                  </td>
                  <td className="py-2 px-1.5 whitespace-nowrap">
                    <span className="text-zinc-700 dark:text-zinc-300 flex items-center gap-0.5 font-mono text-[11px]">
                      <Star className="w-2.5 h-2.5 text-zinc-400 shrink-0" />
                      {formatStars(repo.stars)}
                    </span>
                  </td>
                  <td className="py-2 px-1 text-center text-zinc-500 dark:text-zinc-400 font-mono text-[11px]">
                    {repo.dependencies?.length || 0}
                  </td>
                  <td className="py-2 px-1 text-center whitespace-nowrap">
                    {repo.total_cves > 0 ? (
                      <span className="font-semibold text-rose-600 dark:text-rose-400 inline-flex items-center gap-0.5 font-mono text-[11px]">
                        <ShieldAlert className="w-2.5 h-2.5 shrink-0" />
                        {repo.total_cves}
                      </span>
                    ) : (
                      <span className="text-zinc-400 font-mono text-[11px]">0</span>
                    )}
                  </td>
                  <td className="py-2 px-3 text-right whitespace-nowrap">
                    {getRiskBadge(repo.risk_score)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
