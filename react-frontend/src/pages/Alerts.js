import React, { useEffect, useState } from "react";
import { getAlerts } from "../api";

export default function Alerts() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  function fetch() {
    setLoading(true);
    getAlerts().then(data => setItems(data.items || [])).catch(e => alert(e.message)).finally(() => setLoading(false));
  }

  useEffect(() => { fetch(); }, []);

  const getSeverityClass = (severity) => {
    if (!severity) return 'low';
    const s = severity.toLowerCase();
    if (s.includes('critical')) return 'critical';
    if (s.includes('high')) return 'high';
    if (s.includes('medium')) return 'medium';
    return 'low';
  };

  const getSeverityIcon = (severity) => {
    const sev = getSeverityClass(severity);
    if (sev === 'critical') return '⚠';
    if (sev === 'high') return '⚠';
    if (sev === 'medium') return 'ℹ';
    return 'ℹ';
  };

  return (
    <div className="page">
      <h1 className="page-title">Security Alerts</h1>
      <p className="page-subtitle">Active incidents requiring attention.</p>

      <div style={{ marginBottom: "20px", display: "flex", gap: "10px" }}>
        <button className="btn-primary" onClick={fetch} disabled={loading}>
          {loading ? "Loading..." : "Refresh Alerts"}
        </button>
        <button className="btn-action" style={{ color: "var(--danger)" }}>Silence All</button>
      </div>

      {items.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "40px" }}>
          <p style={{ color: "var(--text-muted)" }}>No active alerts at this time</p>
        </div>
      ) : (
        items.map((alert, idx) => (
          <div key={idx} className={`alert-card ${getSeverityClass(alert.severity || 'low')}`}>
            <div className="alert-content-wrapper">
              <div className="alert-icon">{getSeverityIcon(alert.severity)}</div>
              <div className="alert-content">
                <div className="alert-title">
                  {alert.summary || "Security Event"}
                  <span className="alert-severity">{alert.severity || "Unknown"}</span>
                </div>
                <div className="alert-message">
                  {alert.description || "CVE: " + (alert.cve_id || "N/A")}
                </div>
                <div className="alert-meta">
                  <span>Host: {alert.host || "N/A"}</span>
                  <span>Time: {alert.timestamp?.$date ? new Date(alert.timestamp.$date).toLocaleString() : alert.timestamp || "N/A"}</span>
                </div>
              </div>
            </div>
            <div className="alert-actions">
              <button className="btn-action">Acknowledge</button>
              <button className="btn-action">Dismiss</button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
