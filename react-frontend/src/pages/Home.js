import React, { useEffect, useState } from "react";
import { API_BASE } from "../config";
import PythonScriptsSection from "../components/PythonScriptsSection";

const Home = () => {
  const [stats, setStats] = useState({
    logs: 0,
    cves: 0,
    matches: 0,
    alerts: 0
  });
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/stats`)
      .then((res) => res.json())
      .then((data) => setStats(data.totals))
      .catch(() => setError("Failed to fetch stats"));
  }, []);

  // Removed blocking error and loading states to prevent flickering


  return (
    <div className="page">
      <h1 className="page-title">System Overview</h1>
      <p className="page-subtitle">Real-time security monitoring and vulnerability assessment status.</p>

      {error && (
        <div className="card" style={{ background: "rgba(239, 68, 68, 0.1)", borderColor: "#ef4444", color: "#ef4444", padding: "10px", marginBottom: "20px" }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="dashboard-grid">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-value">{(stats.logs || 0).toLocaleString()}</div>
          <div className="stat-label">TOTAL LOGS</div>
          <div className="stat-subtitle">Events processed today</div>
          <div className="stat-change positive">▲ +12.5%</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🔐</div>
          <div className="stat-value">{(stats.cves || 0).toLocaleString()}</div>
          <div className="stat-label">ACTIVE CVEs</div>
          <div className="stat-subtitle">Database definitions</div>
          <div className="stat-change neutral">→ 0%</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⚡</div>
          <div className="stat-value">{(stats.matches || 0)}</div>
          <div className="stat-label">VULNERABILITIES</div>
          <div className="stat-subtitle">Matches found</div>
          <div className="stat-change negative">▼ -100%</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🚨</div>
          <div className="stat-value">{(stats.alerts || 0)}</div>
          <div className="stat-label">SECURITY ALERTS</div>
          <div className="stat-subtitle">Active incidents</div>
          <div className="stat-change positive">▲ Stable</div>
        </div>
      </div>

      <div className="chart-grid">
        <div className="chart-container">
          <div className="chart-title">Network Activity</div>
          <div style={{ height: "300px", background: "rgba(59, 130, 246, 0.05)", borderRadius: "8px", padding: "20px" }}>
            <p style={{ textAlign: "center", color: "var(--text-muted)" }}>Chart visualization coming soon</p>
          </div>
        </div>

        <div className="chart-container">
          <div className="chart-title">Vulnerability Severity</div>
          <div style={{ height: "300px", background: "rgba(59, 130, 246, 0.05)", borderRadius: "8px", padding: "20px" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--danger)" }}></span>
                <span style={{ color: "var(--text-muted)" }}>Critical: 1</span>
              </div>
              <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--warning)" }}></span>
                <span style={{ color: "var(--text-muted)" }}>High: 2</span>
              </div>
              <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--primary)" }}></span>
                <span style={{ color: "var(--text-muted)" }}>Medium: 5</span>
              </div>
              <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--success)" }}></span>
                <span style={{ color: "var(--text-muted)" }}>Low: 12</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Python Scripts Automation Section */}
      <PythonScriptsSection />
    </div>
  );
};

export default Home;
