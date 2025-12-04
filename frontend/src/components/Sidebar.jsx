import React from 'react';
import { NavLink } from 'react-router-dom';

export default function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 w-64 bg-gradient-to-b from-slate-900/70 to-slate-800/50 backdrop-blur-lg border-r border-slate-800 p-6 z-40">
      <div className="mb-6">
        <div className="text-white font-bold text-lg">VulnGuard AI</div>
        <div className="text-slate-400 text-xs mt-1">Vulnerability Core</div>
      </div>

      <nav className="space-y-4 mt-6">
        <div className="text-xs text-slate-400 uppercase font-semibold mb-2">Main</div>
        <NavLink to="/" end className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800/50">Overview</NavLink>
        <NavLink to="/logs" className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800/50">System Logs</NavLink>
        <NavLink to="/cves" className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800/50">Vulnerabilities</NavLink>
        <NavLink to="/alerts" className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800/50">Security Alerts</NavLink>

        <div className="mt-6 text-xs text-slate-400 uppercase font-semibold mb-2">Analysis</div>
        <NavLink to="/charts" className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800/50">Analytics</NavLink>
        <NavLink to="/reports" className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800/50">Compliance</NavLink>
        <NavLink to="/jobs" className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800/50">Operations</NavLink>
        <NavLink to="/scripts" className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800/50">Python Scripts</NavLink>
      </nav>

      <div className="absolute bottom-6 left-6 right-6">
        <div className="text-xs text-slate-400">Status</div>
        <div className="mt-2 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-sm text-slate-200">Backend Online</span>
        </div>
      </div>
    </aside>
  );
}
