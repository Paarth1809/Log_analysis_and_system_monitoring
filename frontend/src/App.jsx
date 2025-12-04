import React, { useEffect, useState } from 'react';
import { Routes, Route, Outlet } from 'react-router-dom';
import { getStats } from './api';
import NavbarTop from './components/NavbarTop';

// Pages
import Overview from './pages/Overview';
import Logs from './pages/Logs';
import Vulnerabilities from './pages/Vulnerabilities';
import Analytics from './pages/Analytics';
import Operations from './pages/Operations';
import Reports from './pages/Reports';
import Alerts from './pages/Alerts';
import Matches from './pages/Matches';

function Layout({ stats }) {
  return (
    <div className="min-h-screen text-slate-200 font-sans selection:bg-blue-500/30 bg-slate-900">
      <NavbarTop />
      <main className="max-w-7xl mx-auto px-6 py-8">
        <Outlet context={{ stats }} />
      </main>
    </div>
  );
}

function App() {
  const [stats, setStats] = useState({
    totals: { logs: 0, cves: 0, matches: 0, alerts: 0 },
    severity_counts: { critical: 0, high: 0, medium: 0, low: 0 },
    top_hosts: [],
    activity_trend: []
  });

  const fetchStats = async () => {
    try {
      const res = await getStats();
      if (res.data) {
        setStats(res.data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Routes>
      <Route path="/" element={<Layout stats={stats} />}>
        <Route index element={<Overview />} />
        <Route path="logs" element={<Logs />} />
        <Route path="cves" element={<Vulnerabilities />} />
        <Route path="matches" element={<Matches />} />
        <Route path="charts" element={<Analytics />} />
        <Route path="reports" element={<Reports />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="operations" element={<Operations />} />
      </Route>
    </Routes>
  );
}

export default App;
