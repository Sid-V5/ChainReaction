import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import GraphView from './components/GraphView';
import BlastRadiusModal from './components/BlastRadiusModal';
import MongoAnalytics from './components/MongoAnalytics';
import BreakingChangeSimulator from './components/BreakingChangeSimulator';
import LiveAlertsTicker from './components/LiveAlertsTicker';
import RepoTable from './components/RepoTable';
import {
  fetchHealth,
  fetchGraph,
  fetchRepositories,
  scanRepository,
  triggerZeroDay,
  reseedDatabase
} from './api';
import { Target, BarChart3, GitPullRequest, FolderGit2, Radio } from 'lucide-react';

export default function App() {
  const [isDark, setIsDark] = useState(true);
  const [health, setHealth] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [repos, setRepos] = useState([]);
  const [activeTab, setActiveTab] = useState('blast'); // 'blast', 'analytics', 'simulator', 'repos', 'ticker'
  const [highlightedChains, setHighlightedChains] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const loadData = async (retries = 0) => {
    try {
      const [h, g, r] = await Promise.all([
        fetchHealth().catch(() => null),
        fetchGraph().catch(() => null),
        fetchRepositories().catch(() => [])
      ]);
      if (h) setHealth(h);
      if (g && g.nodes && g.nodes.length > 0) {
        setGraphData(g);
      } else if (retries < 3) {
        setTimeout(() => loadData(retries + 1), 1000);
      }
      if (r && r.length > 0) setRepos(r);
    } catch (err) {
      console.error("Failed to load initial data", err);
      if (retries < 3) {
        setTimeout(() => loadData(retries + 1), 1000);
      }
    }
  };

  // Load data on mount with auto-retry if backend is warming up
  useEffect(() => {
    loadData();
  }, []);

  // Update HTML root element class when isDark changes
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  const handleScanRepo = async (url) => {
    setIsScanning(true);
    try {
      const res = await scanRepository(url);
      showToast(`Scanned ${res.data?.repository}: updated graph and document store.`, 'success');
      loadData();
    } catch (err) {
      showToast(`Scan error: ${err.message}`, 'error');
    } finally {
      setIsScanning(false);
    }
  };

  const handleSimulateZeroDay = async () => {
    setIsSimulating(true);
    try {
      const res = await triggerZeroDay();
      showToast(`Injected alert: ${res.alert?.cve_id} via Redis Pub/Sub`, 'danger');
      loadData();
      setHighlightedChains([['psf/requests', 'requests']]);
    } catch (err) {
      showToast(`Simulation error: ${err.message}`, 'error');
    } finally {
      setIsSimulating(false);
    }
  };

  const handleReseed = async () => {
    try {
      await reseedDatabase();
      showToast('Database reset and seeded with benchmark dataset.', 'success');
      loadData();
    } catch (err) {
      showToast(`Reseed error: ${err.message}`, 'error');
    }
  };

  return (
    <div className={`flex flex-col h-screen w-screen ${isDark ? 'dark bg-zinc-950 text-zinc-100' : 'bg-zinc-100 text-zinc-900'} overflow-hidden font-sans select-none transition-colors duration-200`}>
      {/* Header */}
      <Header
        health={health}
        nodeCount={graphData.nodes?.length}
        edgeCount={graphData.edges?.length}
        onScanRepo={handleScanRepo}
        onSimulateZeroDay={handleSimulateZeroDay}
        onRefresh={() => {
          loadData();
          showToast('Refreshed graph and database telemetry.', 'info');
        }}
        onReseed={handleReseed}
        isScanning={isScanning}
        isSimulating={isSimulating}
        isDark={isDark}
        onToggleTheme={() => setIsDark(!isDark)}
      />

      {/* Main Workspace */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden p-3 gap-3">
        {/* Left: Cytoscape Graph Canvas */}
        <div className="flex-1 h-[55%] lg:h-full rounded-xl border border-zinc-200 dark:border-zinc-800 overflow-hidden relative shadow-sm bg-white dark:bg-zinc-900">
          <GraphView
            graphData={graphData}
            highlightedChains={highlightedChains}
            isDark={isDark}
            onNodeSelect={(node) => {
              if (node.type === 'package') {
                setActiveTab('blast');
              }
            }}
          />
        </div>

        {/* Right: Tabbed Feature Panels */}
        <div className="w-full lg:w-[520px] xl:w-[560px] h-[45%] lg:h-full flex flex-col bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl shadow-sm overflow-hidden">
          {/* Navigation Tab Bar (Clean segmented control, zero yellow underlines/highlights) */}
          <div className="flex items-center border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/60 p-1.5 gap-1 text-xs">
            <button
              onClick={() => setActiveTab('blast')}
              className={`flex-1 py-1.5 px-2 rounded-md font-medium flex items-center justify-center gap-1.5 transition-colors ${
                activeTab === 'blast'
                  ? 'bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-sm border border-zinc-200/80 dark:border-zinc-700/80'
                  : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200 hover:bg-zinc-200/50 dark:hover:bg-zinc-800/50'
              }`}
            >
              <Target className="w-3.5 h-3.5" />
              <span>Blast Radius</span>
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`flex-1 py-1.5 px-2 rounded-md font-medium flex items-center justify-center gap-1.5 transition-colors ${
                activeTab === 'analytics'
                  ? 'bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-sm border border-zinc-200/80 dark:border-zinc-700/80'
                  : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200 hover:bg-zinc-200/50 dark:hover:bg-zinc-800/50'
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              <span>Analytics</span>
            </button>

            <button
              onClick={() => setActiveTab('simulator')}
              className={`flex-1 py-1.5 px-2 rounded-md font-medium flex items-center justify-center gap-1.5 transition-colors ${
                activeTab === 'simulator'
                  ? 'bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-sm border border-zinc-200/80 dark:border-zinc-700/80'
                  : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200 hover:bg-zinc-200/50 dark:hover:bg-zinc-800/50'
              }`}
            >
              <GitPullRequest className="w-3.5 h-3.5" />
              <span>Simulations</span>
            </button>

            <button
              onClick={() => setActiveTab('repos')}
              className={`flex-1 py-1.5 px-2 rounded-md font-medium flex items-center justify-center gap-1.5 transition-colors ${
                activeTab === 'repos'
                  ? 'bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-sm border border-zinc-200/80 dark:border-zinc-700/80'
                  : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200 hover:bg-zinc-200/50 dark:hover:bg-zinc-800/50'
              }`}
            >
              <FolderGit2 className="w-3.5 h-3.5" />
              <span>Repositories</span>
            </button>

            <button
              onClick={() => setActiveTab('ticker')}
              className={`flex-1 py-1.5 px-2 rounded-md font-medium flex items-center justify-center gap-1.5 transition-colors ${
                activeTab === 'ticker'
                  ? 'bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-sm border border-zinc-200/80 dark:border-zinc-700/80'
                  : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200 hover:bg-zinc-200/50 dark:hover:bg-zinc-800/50'
              }`}
            >
              <Radio className="w-3.5 h-3.5" />
              <span>Incidents</span>
            </button>
          </div>

          {/* Active Tab Content Area */}
          <div className="flex-1 overflow-hidden">
            {activeTab === 'blast' && (
              <BlastRadiusModal
                onHighlightChains={(chains) => setHighlightedChains(chains)}
              />
            )}
            {activeTab === 'analytics' && <MongoAnalytics />}
            {activeTab === 'simulator' && <BreakingChangeSimulator />}
            {activeTab === 'repos' && (
              <RepoTable
                repos={repos}
                onSelectRepo={(fullName) => {
                  setHighlightedChains([[fullName]]);
                }}
              />
            )}
            {activeTab === 'ticker' && (
              <LiveAlertsTicker
                onNewAlert={(alert) => {
                  setHighlightedChains([['psf/requests', alert.package]]);
                }}
              />
            )}
          </div>
        </div>
      </div>

      {/* Floating Notification Toast */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 z-50 px-4 py-2.5 rounded-lg border text-xs font-semibold shadow-lg backdrop-blur-md animate-in fade-in duration-200 ${
            toast.type === 'danger'
              ? 'bg-rose-950/90 border-rose-800 text-rose-200'
              : toast.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-800 text-emerald-200'
              : 'bg-zinc-900/90 border-zinc-700 text-zinc-200'
          }`}
        >
          {toast.message}
        </div>
      )}
    </div>
  );
}
