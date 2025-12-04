import React, { useEffect, useState } from "react";
import { Pie, Line, Bar } from "react-chartjs-2";
import { getStats } from "../api";
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement } from "chart.js";
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement);

export default function Charts() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    getStats().then(setStats).catch(console.error);
  }, []);

  if (!stats) return (
    <div className="page">
      <h1 className="page-title">Analytics Dashboard</h1>
      <p className="page-subtitle">Deep dive into system metrics and threat vectors.</p>
      <div className="card">Loading analytics...</div>
    </div>
  );

  const severityCounts = stats.severity_counts || {};
  const pieData = {
    labels: Object.keys(severityCounts),
    datasets: [{
      data: Object.values(severityCounts),
      backgroundColor: ['#ef4444', '#f97316', '#3b82f6', '#10b981'],
      borderColor: 'var(--bg-card)',
      borderWidth: 2
    }]
  };

  const lineData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Threats',
        data: [120, 290, 180, 240, 150, 200, 180],
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Blocked',
        data: [80, 200, 120, 150, 90, 140, 120],
        borderColor: '#06b6d4',
        backgroundColor: 'rgba(6, 182, 212, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  };

  const barData = {
    labels: ['Web', 'DNS', 'Mail', 'Auth', 'Proxy'],
    datasets: [
      {
        label: 'PV',
        data: [8000, 4000, 3000, 2000, 3000],
        backgroundColor: '#3b82f6'
      },
      {
        label: 'UV',
        data: [4000, 3000, 2000, 1500, 2500],
        backgroundColor: '#06b6d4'
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        labels: {
          color: 'var(--text-muted)',
          font: { size: 12 }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: 'var(--border)' },
        ticks: { color: 'var(--text-muted)' }
      },
      x: {
        grid: { display: false },
        ticks: { color: 'var(--text-muted)' }
      }
    }
  };

  return (
    <div className="page">
      <h1 className="page-title">Analytics Dashboard</h1>
      <p className="page-subtitle">Deep dive into system metrics and threat vectors.</p>

      <div className="chart-grid">
        <div className="chart-container">
          <div className="chart-title">Threat Trends</div>
          <Line data={lineData} options={chartOptions} />
        </div>

        <div className="chart-container">
          <div className="chart-title">Traffic by Service</div>
          <Bar data={barData} options={chartOptions} />
        </div>
      </div>

      <div style={{ marginBottom: "30px" }}>
        <div className="chart-container">
          <div className="chart-title">Distribution Metrics</div>
          <div style={{ height: "300px", display: "flex", justifyContent: "center", alignItems: "center" }}>
            <div style={{ width: "300px" }}>
              <Pie data={pieData} options={{
                responsive: true,
                plugins: {
                  legend: {
                    labels: { color: 'var(--text-muted)' }
                  }
                }
              }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
