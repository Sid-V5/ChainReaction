import React, { useEffect, useState } from 'react';
import { Radio, Trophy, AlertTriangle, Clock, Terminal, Zap, ShieldAlert } from 'lucide-react';
import { WS_URL, fetchLeaderboard } from '../api';

export default function LiveAlertsTicker({ onNewAlert }) {
  const [alerts, setAlerts] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    // 1. Fetch initial Redis ZSET Leaderboard
    async function loadLeaderboard() {
      try {
        const lb = await fetchLeaderboard();
        setLeaderboard(lb || []);
      } catch (err) {
        console.error(err);
      }
    }
    loadLeaderboard();

    // 2. Connect to WebSocket stream powered by Redis Pub/Sub
    let socket;
    try {
      socket = new WebSocket(WS_URL);

      socket.onopen = () => {
        setWsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.event === 'ZERO_DAY_DETECTED') {
            setAlerts((prev) => [data, ...prev.slice(0, 15)]);
            if (onNewAlert) onNewAlert(data);
            loadLeaderboard(); // refresh leaderboard
          }
        } catch (e) {
          console.error(e);
        }
      };

      socket.onclose = () => {
        setWsConnected(false);
      };
    } catch (e) {
      console.warn("WebSocket connection deferred:", e);
    }

    return () => {
      if (socket) socket.close();
    };
  }, []);

  return (
    <div className="bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4 shadow-sm flex flex-col h-full overflow-hidden transition-colors duration-200">
      {/* Header Banner */}
      <div className="flex items-center justify-between pb-3 border-b border-zinc-100 dark:border-zinc-800">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700">
            <Radio className={`w-4 h-4 ${wsConnected ? 'animate-pulse text-emerald-500' : 'text-zinc-400'}`} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xs font-bold text-zinc-900 dark:text-zinc-100 tracking-wide uppercase font-sans">
                Incident Telemetry
              </h2>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-700">
                Live Stream
              </span>
            </div>
            <p className="text-[11px] text-zinc-500 dark:text-zinc-400">
              Real-time Incident Stream & Exposure Leaderboard
            </p>
          </div>
        </div>

        {/* Live status badge */}
        <div className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-[10px] font-mono">
          <span
            className={`w-2 h-2 rounded-full ${
              wsConnected ? 'bg-emerald-500 animate-pulse' : 'bg-zinc-400'
            }`}
          />
          <span className={wsConnected ? 'text-emerald-600 dark:text-emerald-400 font-semibold' : 'text-zinc-400'}>
            {wsConnected ? 'LIVE FEED' : 'CONNECTING'}
          </span>
        </div>
      </div>

      <div className="mt-3 flex-1 overflow-y-auto space-y-3 pr-1 text-xs">
        {/* Exposure Leaderboard */}
        <div className="p-3 bg-zinc-50 dark:bg-zinc-900/60 rounded-lg border border-zinc-200 dark:border-zinc-800">
          <div className="flex items-center justify-between mb-2">
            <span className="flex items-center gap-1.5 text-xs font-semibold text-zinc-900 dark:text-zinc-100">
              <Trophy className="w-3.5 h-3.5 text-zinc-500" />
              Exposure Leaderboard
            </span>
            <span className="text-[10px] font-mono text-zinc-400">
              Live Ranking
            </span>
          </div>

          <div className="space-y-1.5">
            {leaderboard.length === 0 ? (
              <div className="p-2 text-center text-zinc-400 font-mono text-[11px]">
                Loading exposure ranking...
              </div>
            ) : (
              leaderboard.slice(0, 5).map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2 rounded-md bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800/80 hover:border-zinc-300 dark:hover:border-zinc-700 transition-colors"
                >
                  <div className="flex items-center gap-2.5">
                    <span
                      className={`w-5 text-center font-bold font-mono text-xs ${
                        idx === 0
                          ? 'text-zinc-900 dark:text-zinc-100 font-extrabold'
                          : 'text-zinc-400'
                      }`}
                    >
                      #{idx + 1}
                    </span>
                    <span className="font-mono font-medium text-zinc-800 dark:text-zinc-200 text-xs truncate max-w-[220px]">
                      {item.repository}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-zinc-400">Score:</span>
                    <span
                      className={`font-mono font-bold text-xs px-2 py-0.5 rounded ${
                        item.risk_score >= 60
                          ? 'bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-900'
                          : item.risk_score >= 30
                          ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-200 border border-zinc-200 dark:border-zinc-700'
                          : 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900'
                      }`}
                    >
                      {item.risk_score}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Live Ticker Alerts Feed */}
        <div className="p-3 bg-zinc-50 dark:bg-zinc-900/60 rounded-lg border border-zinc-200 dark:border-zinc-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-rose-600 dark:text-rose-400 flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5" />
              Emergency Broadcast Channel (<code className="font-mono text-zinc-800 dark:text-zinc-200">cve:alerts</code>)
            </span>
            <span className="text-[10px] font-mono text-zinc-400">
              {alerts.length} Incidents
            </span>
          </div>

          {alerts.length === 0 ? (
            <div className="p-4 text-center text-zinc-400 text-[11px] bg-white dark:bg-zinc-950 rounded-lg border border-dashed border-zinc-200 dark:border-zinc-800 flex flex-col items-center gap-1.5">
              <Zap className="w-4 h-4 text-zinc-400" />
              <span>Monitoring live incident channel... No active zero-days reported.</span>
              <span className="text-[10px] text-zinc-400">
                Click "Simulate Zero-Day" in the header to broadcast an instant emergency advisory.
              </span>
            </div>
          ) : (
            <div className="space-y-2">
              {alerts.map((al, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-white dark:bg-zinc-950 border border-rose-200 dark:border-rose-900/40 text-xs shadow-sm"
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-mono font-bold text-rose-600 dark:text-rose-400 text-xs flex items-center gap-1">
                      <ShieldAlert className="w-3.5 h-3.5" />
                      {al.cve_id}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-600 text-white uppercase">
                      {al.severity} • CVSS {al.cvss_score}
                    </span>
                  </div>
                  <p className="text-[11px] text-zinc-700 dark:text-zinc-300 line-clamp-2 leading-relaxed">
                    {al.summary}
                  </p>
                  <div className="mt-2 flex items-center justify-between text-[10px] text-zinc-400 font-mono pt-1.5 border-t border-zinc-100 dark:border-zinc-800">
                    <span>
                      Target: <strong className="text-zinc-800 dark:text-zinc-200">{al.package}</strong>
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      Live Incident Stream
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Telemetry Architecture Info */}
        <div className="p-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-[11px]">
          <div className="flex items-center gap-1.5 text-zinc-700 dark:text-zinc-300 font-mono font-medium mb-1">
            <Terminal className="w-3.5 h-3.5" />
            <span>Telemetry Pipeline Engine:</span>
          </div>
          <div className="font-mono text-[10px] text-zinc-500 dark:text-zinc-400 space-y-1">
            <div>• <strong className="text-zinc-700 dark:text-zinc-300">Fast Cache Layer:</strong> Sub-millisecond TTL-bound cache for blast radius traversals.</div>
            <div>• <strong className="text-zinc-700 dark:text-zinc-300">Exposure Index:</strong> High-throughput score ranking across all monitored repositories.</div>
            <div>• <strong className="text-zinc-700 dark:text-zinc-300">Event Stream:</strong> Real-time zero-day broadcast to active clients via WebSockets.</div>
          </div>
        </div>
      </div>
    </div>
  );
}
