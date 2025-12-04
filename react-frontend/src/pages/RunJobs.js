import React, { useEffect, useState } from "react";
import { runParser, runMatching, runAlerts, runReports, listJobs, listSchedules, scheduleJob, runJobNow, getLastRun } from "../api";

export default function RunJobs() {
  const [jobs, setJobs] = useState([]);
  const [busy, setBusy] = useState(false);

  function refresh() {
    listJobs().then(setJobs).catch(() => setJobs([]));
  }

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 2000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    // fetch schedules once
    listSchedules().then(s => setSchedules(s)).catch(() => setSchedules({}));
  }, []);

  async function run(fn) {
    try {
      setBusy(true);
      const res = await fn();
      refresh();
      alert(res.message || "Task started");
    } catch (e) {
      alert(e.message);
    } finally {
      setBusy(false);
    }
  }

  const getJobStatus = (status) => {
    const s = status?.toLowerCase() || '';
    if (s.includes('running')) return 'running';
    if (s.includes('completed') || s.includes('success')) return 'completed';
    if (s.includes('failed') || s.includes('error')) return 'failed';
    return 'idle';
  };

  const jobDefinitions = [
    {
      name: "Vulnerability Scan",
      desc: "Full system scan for known CVEs across all connected nodes.",
      fn: runMatching,
      color: "primary"
    },
    {
      name: "Log Normalization",
      desc: "Process and index raw logs from the last 24 hours.",
      fn: runParser,
      color: "primary"
    },
    {
      name: "Alert Generation",
      desc: "Generate security alerts based on vulnerability matches.",
      fn: runAlerts,
      color: "warning"
    },
    {
      name: "Report Generation",
      desc: "Create incremental backup of the main security database.",
      fn: runReports,
      color: "success"
    }
  ];

  const [schedules, setSchedules] = useState({});
  const [lastRunDisplay, setLastRunDisplay] = useState({});

  function mapNameToKey(name) {
    return name === 'Vulnerability Scan' ? 'matching'
      : name === 'Log Normalization' ? 'parser'
      : name === 'Alert Generation' ? 'alerts'
      : name === 'Report Generation' ? 'reports'
      : name.toLowerCase();
  }

  function formatLastRun(task) {
    if (!task) return 'never';
    if (task.started_at) {
      const t = Number(task.started_at) * 1000;
      try {
        return new Date(t).toLocaleString();
      } catch (e) {
        return String(task.started_at);
      }
    }
    return 'unknown';
  }

  // populate last run info for each job
  useEffect(() => {
    jobDefinitions.forEach(j => {
      const key = mapNameToKey(j.name);
      getLastRun(key).then(res => {
        setLastRunDisplay(prev => ({ ...prev, [j.name]: formatLastRun(res?.last_run) }));
      }).catch(() => {});
    });
  }, []);

  return (
    <div className="page">
      <h1 className="page-title">Operations Center</h1>
      <p className="page-subtitle">Execute and monitor system tasks and maintenance jobs.</p>

      <div style={{ marginBottom: "30px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "20px" }}>
          {jobDefinitions.map((job) => (
            <div key={job.name} className="job-card">
              <div className="job-info">
                <h3>{job.name}</h3>
                <div className="job-meta">Last run: {lastRunDisplay[job.name] || 'never'}</div>
                <div className="job-description">{job.desc}</div>
              </div>
              <div className="job-actions">
                <button
                  className="btn-primary"
                  onClick={async () => {
                    setBusy(true);
                    try {
                      // map display names to internal job keys
                      const key = mapNameToKey(job.name);
                      await runJobNow(key);
                      // refresh jobs and last-run
                      refresh();
                      const lr = await getLastRun(key);
                      setLastRunDisplay(prev => ({ ...prev, [job.name]: formatLastRun(lr?.last_run) }));
                    } catch (e) {
                      alert(e.message || e);
                    } finally {
                      setBusy(false);
                    }
                  }}
                  disabled={busy}
                  style={{ width: "100%" }}
                >
                  ▶ Run Now
                </button>
                <div style={{ height: 8 }} />
                <div style={{ display: 'flex', gap: 8 }}>
                  <input type="number" min={1} defaultValue={schedules[mapNameToKey(job.name)]?.minutes || 10} style={{ width: 80, padding: '6px 8px', borderRadius: 6, border: '1px solid var(--border)', background: 'transparent', color: 'var(--text-light)' }} id={`interval-${job.name}`} />
                  <button className="btn-secondary" onClick={async () => {
                    const val = document.getElementById(`interval-${job.name}`).value || 10;
                    try {
                      const key = mapNameToKey(job.name);
                      await scheduleJob(key, parseInt(val, 10), true);
                      const s = await listSchedules();
                      setSchedules(s);
                      alert('Scheduled');
                    } catch (e) { alert(e.message || e); }
                  }}>Schedule</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h2 style={{ fontSize: "18px", fontWeight: "600", color: "var(--text-light)", marginBottom: "15px", display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ width: "4px", height: "16px", background: "var(--primary)", borderRadius: "2px" }}></span>
          Job Execution Log
        </h2>

        {jobs.length === 0 ? (
          <div className="card" style={{ textAlign: "center", padding: "40px" }}>
            <p style={{ color: "var(--text-muted)" }}>No jobs executed yet</p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {jobs.map(j => {
              const statusClass = getJobStatus(j.status);
              return (
                <div key={j.id} className="job-card" style={{ gridTemplateColumns: "1fr auto", display: "grid", gap: "20px" }}>
                  <div className="job-info">
                    <h3>{j.name}</h3>
                    <div className="job-meta">{j.started_at}</div>
                    {j.message && <div className="job-description">{j.message}</div>}
                  </div>
                  <div className="job-actions" style={{ alignItems: "center" }}>
                    <span className={`job-status ${statusClass}`}>
                      {statusClass === 'running' ? '⟳ Running' : statusClass === 'completed' ? '✓ Completed' : '✗ Failed'}
                    </span>
                    {j.progress !== undefined && (
                      <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                        {j.progress}% complete
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
