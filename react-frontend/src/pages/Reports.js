import React, { useEffect, useState } from "react";

export default function Reports() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch("http://localhost:8000/reports/list").then(r => r.json()).then(setReports).catch(() => setReports([])).finally(() => setLoading(false));
  }, []);

  return (
    <div className="page">
      <h1 className="page-title">Compliance Reports</h1>
      <p className="page-subtitle">Generated documentation and audit logs.</p>

      <div style={{ marginBottom: "20px" }}>
        <button className="btn-primary">Generate New Report</button>
      </div>

      <div>
        <h3 className="chart-title">Recent Reports</h3>
        {loading && <div className="card">Loading reports...</div>}
        {!loading && reports.length === 0 && (
          <div className="card" style={{ textAlign: "center", padding: "40px" }}>
            <p style={{ color: "var(--text-muted)" }}>No reports found yet. Generate one to get started.</p>
          </div>
        )}
        {reports.length > 0 && (
          <div className="table-container">
            <table className="table-custom">
              <thead>
                <tr>
                  <th>REPORT NAME</th>
                  <th>DATE GENERATED</th>
                  <th>TYPE</th>
                  <th>STATUS</th>
                  <th>ACTION</th>
                </tr>
              </thead>
              <tbody>
                {reports.map(r => (
                  <tr key={r.file}>
                    <td><strong>{r.host || "Aggregate Report"}</strong><br /><small style={{ color: "var(--text-muted)" }}>{r.file}</small></td>
                    <td>{r.date || "N/A"}</td>
                    <td><span className="badge badge-info">{r.type || "PDF"}</span></td>
                    <td><span className="badge badge-success">Ready</span></td>
                    <td>
                      <a className="btn-action" href={`/reports/output/${r.file}`} target="_blank" rel="noreferrer">📥 Download</a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
