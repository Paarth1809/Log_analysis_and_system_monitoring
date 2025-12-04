import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { BarChart3, AlertCircle, FileText, Zap, Settings, Play, Loader2, ShieldAlert } from 'lucide-react';
import { runScript, api } from '../api';

const tabs = [
  { path: '/', label: 'Overview', icon: BarChart3 },
  { path: '/logs', label: 'System Logs', icon: FileText },
  { path: '/cves', label: 'Vulnerabilities', icon: AlertCircle },
  { path: '/matches', label: 'Matches', icon: ShieldAlert },
  { path: '/charts', label: 'Analytics', icon: BarChart3 },
  { path: '/reports', label: 'Reports', icon: FileText },
  { path: '/alerts', label: 'Alerts', icon: AlertCircle },
  { path: '/operations', label: 'Operations', icon: Settings },
];

export default function NavbarTop() {
  const [running, setRunning] = useState(false);

  const runScriptAndWait = async (scriptName) => {
    console.log(`Starting ${scriptName}...`);
    const { data } = await runScript(scriptName);
    const taskId = data.task_id;

    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        try {
          // Use the shared api instance to avoid CORS/port issues
          const res = await api.get(`/scripts/status/${taskId}`);
          const status = res.data;

          if (status.state === 'success') {
            clearInterval(interval);
            resolve(status);
          } else if (status.state === 'failed') {
            clearInterval(interval);
            reject(new Error(status.msg));
          }
        } catch (err) {
          // If polling fails (e.g. network timeout), log it but don't abort the whole process.
          // The script might still be running.
          console.warn(`Polling status failed for ${scriptName}:`, err);
          // We could add a max retry count here if needed, but for now just keep trying.
        }
      }, 1000);
    });
  };

  const handleDiagnostics = async () => {
    try {
      setRunning(true);

      // Run full diagnostic suite sequentially
      await runScriptAndWait('parse_logs');
      await runScriptAndWait('insert_logs');
      await runScriptAndWait('run_matching');
      await runScriptAndWait('send_alerts');
      await runScriptAndWait('generate_reports');
      await runScriptAndWait('validate_data');

      // Artificial delay to show completion
      setTimeout(() => {
        setRunning(false);
        alert("Diagnostics Complete! Please refresh the Reports and Alerts tabs.");
      }, 1000);
    } catch (err) {
      console.error("Diagnostics failed", err);
      setRunning(false);
      alert("Diagnostics Failed. Check console for details.");
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-gradient-to-r from-slate-900 via-slate-900 to-slate-800 backdrop-blur-xl border-b border-slate-700/50">
      <div className="max-w-full px-6 h-[72px] flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <div className="w-6 h-6 text-white font-bold flex items-center justify-center">⚡</div>
          </div>
          <div className="hidden md:block">
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent leading-none mb-1">Cyart Dashboard</h1>
            <div className="text-[10px] text-slate-400 font-medium tracking-wide uppercase">Vulnerability Core</div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex items-center gap-1 overflow-x-auto px-4 hide-scrollbar">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <NavLink
                key={tab.path}
                to={tab.path}
                end={tab.path === '/'}
                className={({ isActive }) => `
                  flex items-center gap-2 px-3 py-2 rounded-lg font-medium text-sm transition-all whitespace-nowrap
                  ${isActive
                    ? 'bg-gradient-to-r from-blue-600/90 to-cyan-500/90 text-white shadow-lg shadow-blue-500/25 ring-1 ring-white/10'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'}
                `}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </NavLink>
            );
          })}
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-4 shrink-0">
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 bg-slate-800/40 rounded-full border border-slate-700/50">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse shadow-[0_0_8px_rgba(74,222,128,0.5)]" />
            <span className="text-xs font-medium text-slate-300">System Online</span>
          </div>
          <button
            onClick={handleDiagnostics}
            disabled={running}
            className="hidden sm:flex px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-600/50 text-white text-sm rounded-lg font-medium transition-colors shadow-lg shadow-blue-500/20 items-center gap-2"
          >
            {running ? <Loader2 className="w-4 h-4 animate-spin" /> : <span>▶</span>}
            {running ? 'Running...' : 'Run Diagnostics'}
          </button>
          <div className="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-blue-400 font-bold text-sm shadow-inner">
            AD
          </div>
        </div>
      </div>
    </header>
  );
}
