import React, { useEffect, useState } from "react";
import { API_BASE } from "../config";

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [host, setHost] = useState("");
  const [software, setSoftware] = useState("");
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  const fetchLogs = () => {
    let url = `${API_BASE}/logs?limit=100`;

    if (host) url += `&host=${host}`;
    if (software) url += `&software=${software}`;
    if (search) url += `&q=${search}`;

    fetch(url)
      .then((r) => r.json())
      .then((data) => setLogs(data.items || []))
      .catch(() => setError("Failed to fetch logs"));
  };

  useEffect(() => {
    fetchLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="page">
      <h1 className="page-title">System Logs</h1>
      <p className="page-subtitle">Real-time event stream and security auditing.</p>

      <div className="chart-container" style={{ padding: "20px", marginBottom: "20px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "15px" }}>
          <div>
            <label style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", fontWeight: "600", display: "block", marginBottom: "8px" }}>Filter by Host</label>
            <input placeholder="Host name..." value={host} onChange={(e) => setHost(e.target.value)} />
          </div>
          <div>
            <label style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", fontWeight: "600", display: "block", marginBottom: "8px" }}>Filter by Software</label>
            <input placeholder="Software..." value={software} onChange={(e) => setSoftware(e.target.value)} />
          </div>
          <div>
            <label style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", fontWeight: "600", display: "block", marginBottom: "8px" }}>Search raw log messages</label>
            <input placeholder="Search..." value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
        </div>
        <button className="btn-primary" onClick={fetchLogs} style={{ marginTop: "15px" }}>Fetch</button>
      </div>

      {error && (
        <div className="card" style={{ background: "rgba(239, 68, 68, 0.1)", borderColor: "#ef4444", color: "#ef4444" }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="table-container">
        <table className="table-custom">
          <thead>
            <tr>
              <th>TIMESTAMP</th>
              <th>HOST</th>
              <th>OS</th>
              <th>SOFTWARE</th>
              <th>EVENT</th>
              <th>MESSAGE</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ textAlign: "center", padding: "40px" }}>
                  No logs found. Try adjusting your filters.
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log._id || log.timestamp}>
                  <td><code style={{ fontSize: "11px" }}>{typeof log.timestamp === 'object' && log.timestamp.$date ? new Date(log.timestamp.$date).toISOString() : log.timestamp}</code></td>
                  <td><span className="badge badge-info">{log.host}</span></td>
                  <td>{log.os}</td>
                  <td><span style={{ color: "var(--primary-light)", fontWeight: "600" }}>{log.software}</span></td>
                  <td>{log.event_type}</td>
                  <td style={{ maxWidth: "300px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{log.message}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Logs;
