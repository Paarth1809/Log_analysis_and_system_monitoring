import React, { useEffect, useState } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Activity, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';

export default function ChartsSection({ stats }) {
  const [activeChart, setActiveChart] = useState('severity');

  if (!stats) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    );
  }

  const severityData = Object.entries(stats.severity_counts || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value: value
  }));

  const topHostsData = (stats.top_hosts || []).slice(0, 8).map(h => ({
    name: h.host || 'Unknown',
    count: h.count
  }));

  const trendData = stats.activity_trend || [
    { time: '00:00', logs: 0, alerts: 0 }
  ];

  const COLORS = ['#ef4444', '#f97316', '#eab308', '#10b981'];

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="space-y-6"
    >
      <div className="flex items-center gap-3">
        <Activity className="w-6 h-6 text-blue-400" />
        <h2 className="text-2xl font-bold text-white">Analytics Dashboard</h2>
      </div>

      {/* Chart Tabs */}
      <div className="flex gap-2 bg-slate-800/50 border border-slate-700 rounded-lg p-1 w-fit">
        {[
          { id: 'severity', label: 'Severity Distribution' },
          { id: 'hosts', label: 'Top Hosts' },
          { id: 'trend', label: 'Activity Trend' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveChart(tab.id)}
            className={`px-4 py-2 rounded-md font-medium transition-colors text-sm ${activeChart === tab.id
                ? 'bg-blue-600 text-white'
                : 'text-slate-400 hover:text-slate-300'
              }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Main Chart */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 shadow-2xl"
        >
          <h3 className="text-lg font-bold text-white mb-4">
            {activeChart === 'severity' && 'Vulnerability Severity'}
            {activeChart === 'hosts' && 'Most Vulnerable Hosts'}
            {activeChart === 'trend' && 'Activity Timeline'}
          </h3>

          <ResponsiveContainer width="100%" height={300}>
            {activeChart === 'severity' && (
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            )}

            {activeChart === 'hosts' && (
              <BarChart
                data={topHostsData}
                margin={{ top: 20, right: 30, left: 0, bottom: 60 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
                <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
              </BarChart>
            )}

            {activeChart === 'trend' && (
              <LineChart
                data={trendData}
                margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
                <Legend />
                <Line type="monotone" dataKey="logs" stroke="#3b82f6" strokeWidth={2} name="Logs" />
                <Line type="monotone" dataKey="alerts" stroke="#ef4444" strokeWidth={2} name="Alerts" />
              </LineChart>
            )}
          </ResponsiveContainer>
        </motion.div>

        {/* Stats Cards */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="space-y-4"
        >
          <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-400" />
              Quick Stats
            </h3>

            <div className="space-y-4">
              {[
                { label: 'Total Hosts Monitored', value: stats.totals?.hosts || 0, color: 'bg-blue-500' },
                { label: 'Processed Logs', value: stats.totals?.logs || 0, color: 'bg-purple-500' },
                { label: 'CVE Definitions', value: stats.totals?.cves || 0, color: 'bg-orange-500' },
                { label: 'Active Threats', value: stats.totals?.matches || 0, color: 'bg-red-500' },
                { label: 'Critical Alerts', value: stats.totals?.alerts || 0, color: 'bg-rose-500' }
              ].map((stat, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="flex items-center justify-between p-3 bg-slate-800/50 border border-slate-700 rounded-lg hover:bg-slate-800 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${stat.color}`} />
                    <span className="text-slate-300 text-sm">{stat.label}</span>
                  </div>
                  <span className="font-bold text-white text-lg">{stat.value.toLocaleString()}</span>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Severity Breakdown */}
          <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-4">Severity Breakdown</h3>
            <div className="space-y-2">
              {severityData.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full`} style={{ backgroundColor: COLORS[idx] }} />
                    <span className="text-slate-300">{item.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-slate-700 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r h-2 rounded-full"
                        style={{
                          width: `${(item.value / Math.max(...severityData.map(d => d.value))) * 100}%`,
                          backgroundColor: COLORS[idx]
                        }}
                      />
                    </div>
                    <span className="font-bold text-white w-12 text-right">{item.value}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </motion.section>
  );
}
