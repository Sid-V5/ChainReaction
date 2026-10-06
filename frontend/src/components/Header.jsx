import React, { useState } from 'react';
import { ShieldAlert, RefreshCw, Search, Activity, Sun, Moon, Database } from 'lucide-react';

export default function Header({
  health,
  nodeCount,
  edgeCount,
  onScanRepo,
  onSimulateZeroDay,
  onRefresh,
  onReseed,
  isScanning,
  isSimulating,
  isDark,
  onToggleTheme
}) {
  const [repoInput, setRepoInput] = useState('');

  const handleScanSubmit = (e) => {
    e.preventDefault();
    if (!repoInput.trim()) return;
    onScanRepo(repoInput.trim());
    setRepoInput('');
  };

  const isConnected = (status) => status === 'connected';

  return (
    <header className="border-b border-zinc-200 dark:border-zinc-800 bg-white/95 dark:bg-zinc-950/95 backdrop-blur-md px-5 py-3 z-30 sticky top-0 transition-colors duration-200">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
        {/* Brand & Platform Identifier */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 flex items-center justify-center font-bold text-sm shadow-sm">
            CR
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-sans font-bold text-base tracking-tight text-zinc-900 dark:text-zinc-100">
                ChainReaction
              </span>
            </div>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 font-normal">
              Software Supply Chain & Blast Radius Telemetry
            </p>
          </div>
        </div>

        {/* Real-time Telemetry Counters */}
        <div className="flex items-center gap-2 text-xs">
          <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-md bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-400 font-mono text-[11px]">
            <Activity className="w-3.5 h-3.5 text-zinc-500" />
            <span>NODES: <strong className="text-zinc-900 dark:text-zinc-100">{nodeCount || 0}</strong></span>
            <span className="text-zinc-300 dark:text-zinc-700">|</span>
            <span>EDGES: <strong className="text-zinc-900 dark:text-zinc-100">{edgeCount || 0}</strong></span>
          </div>
        </div>

        {/* Actions & Target Ingestion */}
        <div className="flex items-center gap-2">
          {/* Target Ingestion Form */}
          <form onSubmit={handleScanSubmit} className="relative flex-1 sm:w-72">
            <input
              type="text"
              placeholder="Ingest repo, e.g. pallets/flask"
              value={repoInput}
              onChange={(e) => setRepoInput(e.target.value)}
              className="w-full bg-zinc-50 dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-800 rounded-lg pl-8 pr-16 py-1.5 text-xs text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 outline-none focus:border-zinc-500 dark:focus:border-zinc-500 transition-colors"
            />
            <Search className="w-3.5 h-3.5 text-zinc-400 absolute left-2.5 top-2.5" />
            <button
              type="submit"
              disabled={isScanning || !repoInput.trim()}
              className="absolute right-1 top-1 px-2.5 py-0.5 rounded-md bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-white text-white dark:text-zinc-900 text-xs font-semibold transition-colors disabled:opacity-40"
            >
              {isScanning ? 'Scanning...' : 'Scan'}
            </button>
          </form>

          {/* Zero-Day Simulation Trigger (Clean Crimson Action Button) */}
          <button
            onClick={onSimulateZeroDay}
            disabled={isSimulating}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold transition-colors shadow-sm disabled:opacity-50"
            title="Inject real-time Zero-Day advisory through Redis Pub/Sub"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>{isSimulating ? 'Injecting...' : 'Simulate Zero-Day'}</span>
          </button>

          {/* Refresh Telemetry & Graph */}
          <button
            onClick={onRefresh}
            className="p-1.5 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors"
            title="Refresh graph and database telemetry"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          {/* Light / Dark Mode Toggle Switch */}
          <button
            onClick={onToggleTheme}
            className="p-1.5 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors"
            title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
            aria-label="Toggle theme"
          >
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </header>
  );
}
