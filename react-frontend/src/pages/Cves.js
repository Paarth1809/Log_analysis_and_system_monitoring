import React, { useEffect, useState } from "react";
import { getCves } from "../api";

export default function Cves() {
  const [items, setItems] = useState([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);

  function fetch(qstr = "") {
    setLoading(true);
    getCves({ q: qstr, limit: 50 }).then(data => setItems(data.items || [])).catch(e => alert(e.message)).finally(() => setLoading(false));
  }

  useEffect(() => { fetch(); }, []);

  const getSeverityBadgeClass = (severity) => {
    if (!severity) return 'badge-info';
    const s = severity.toLowerCase();
    if (s.includes('critical')) return 'badge-danger';
    if (s.includes('high')) return 'badge-warning';
    if (s.includes('medium')) return 'badge-info';
    return 'badge-success';
  };

  return (
    <div className="page">
      <h1 className="page-title">Vulnerabilities</h1>
      <p className="page-subtitle">Database of known CVE vulnerabilities and threat vectors.</p>

      <div className="chart-container" style={{ padding: "20px", marginBottom: "20px" }}>
        <div style={{ display: "flex", gap: "10px" }}>
          <input 
            placeholder="Search product or vendor..." 
            value={q} 
            onChange={e => setQ(e.target.value)}
            style={{ flex: 1 }}
          />
          <button className="btn-primary" onClick={() => fetch(q)} disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      </div>

      <div className="table-container">
        <table className="table-custom">
          <thead>
            <tr>
              <th>CVE ID</th>
              <th>VENDOR</th>
              <th>PRODUCT</th>
              <th>CVSS</th>
              <th>SEVERITY</th>
              <th>SUMMARY</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ textAlign: "center", padding: "40px" }}>
                  No CVEs found. Try a different search.
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr key={item.cve_id}>
                  <td><span style={{ color: "var(--primary-light)", fontWeight: "600" }}>{item.cve_id}</span></td>
                  <td>{item.vendor || "N/A"}</td>
                  <td>{item.product || "N/A"}</td>
                  <td>
                    <span style={{ fontWeight: "600", color: item.cvss_score > 7 ? "var(--danger)" : "var(--warning)" }}>
                      {item.cvss_score || "N/A"}
                    </span>
                  </td>
                  <td><span className={`badge ${getSeverityBadgeClass(item.severity)}`}>{item.severity || "Unknown"}</span></td>
                  <td style={{ maxWidth: "400px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {item.description || "No description"}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
