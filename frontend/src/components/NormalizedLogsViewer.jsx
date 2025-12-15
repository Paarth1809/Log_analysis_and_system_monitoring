import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { FileText, Download, Filter, ChevronDown, ChevronUp, ChevronLeft, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function NormalizedLogsViewer() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [expandedId, setExpandedId] = useState(null);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(100);
  const [filters, setFilters] = useState({
    source: 'all',
    severity: 'all',
    host: 'all'
  });

  useEffect(() => {
    fetchNormalizedLogs();
  }, [page, limit, filters]);

  const fetchNormalizedLogs = async () => {
    try {
      setLoading(true);
      const skip = (page - 1) * limit;

      const params = new URLSearchParams({
        limit,
        skip,
      });

      if (filters.source !== 'all') params.append('source', filters.source); // Note: backend needs to support source if not already
      if (filters.severity !== 'all') params.append('severity', filters.severity);
      if (filters.host !== 'all') params.append('host', filters.host);

      const response = await api.get('/logs', { params });
      const data = response.data;

      if (data) {
        setLogs(Array.isArray(data) ? data : data.items || []);
        setTotal(data.total || 0);
      }
    } catch (err) {
      console.error('Error fetching normalized logs:', err);
    } finally {
      setLoading(false);
    }
  };

  // We need to fetch unique values for filters. 
  // Ideally this should be a separate API call, but for now we can't easily get all unique values from paginated API.
  // We'll just hardcode common ones or use what we have loaded (which is imperfect).
  // Let's hardcode severities.
  const uniqueSeverities = ['info', 'low', 'medium', 'high', 'critical'];
  // For hosts and sources, we might need a separate aggregation endpoint, but let's just show what's in current view or generic input?
  // Let's stick to what we have or just text input for host? 
  // The previous version derived from `logs` which was only 100 items. That's fine for now.
  const uniqueSources = [...new Set(logs.map(l => l.source))];
  const uniqueHosts = [...new Set(logs.map(l => l.host))];

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'bg-red-500/20 border-red-500/30 text-red-400';
      case 'high': return 'bg-orange-500/20 border-orange-500/30 text-orange-400';
      case 'medium': return 'bg-yellow-500/20 border-yellow-500/30 text-yellow-400';
      case 'low': return 'bg-blue-500/20 border-blue-500/30 text-blue-400';
      default: return 'bg-slate-500/20 border-slate-500/30 text-slate-400';
    }
  };

  const downloadJSON = () => {
    const dataStr = JSON.stringify(logs, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `normalized_logs_${Date.now()}.json`;
    link.click();
  };

  const downloadCSV = () => {
    if (logs.length === 0) return;

    const headers = ['Timestamp', 'Host', 'OS', 'Software', 'Version', 'Event Type', 'Severity', 'Message'];
    const rows = logs.map(log => [
      log.timestamp || '',
      log.host || '',
      log.os || '',
      log.software || '',
      log.version || '',
      log.event_type || '',
      log.severity || '',
      (log.message || '').replace(/"/g, '""')
    ]);

    let csv = headers.join(',') + '\n';
    rows.forEach(row => {
      csv += row.map(cell => `"${cell}"`).join(',') + '\n';
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `normalized_logs_${Date.now()}.csv`;
    link.click();
  };

  const totalPages = Math.ceil(total / limit);
  const startRange = (page - 1) * limit + 1;
  const endRange = Math.min(page * limit, total);

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 shadow-2xl"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <FileText className="w-6 h-6 text-green-400" />
          <h2 className="text-2xl font-bold text-white">Normalized Logs Viewer</h2>
        </div>
        <div className="flex gap-2">
          <button
            onClick={downloadJSON}
            disabled={logs.length === 0}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors text-sm"
          >
            <Download className="w-4 h-4" />
            JSON
          </button>
          <button
            onClick={downloadCSV}
            disabled={logs.length === 0}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors text-sm"
          >
            <Download className="w-4 h-4" />
            CSV
          </button>
          <button
            onClick={fetchNormalizedLogs}
            className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors text-sm"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <select
          value={filters.source}
          onChange={(e) => {
            setFilters({ ...filters, source: e.target.value });
            setPage(1);
          }}
          className="px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-colors text-sm"
        >
          <option value="all">All Sources</option>
          {uniqueSources.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select
          value={filters.severity}
          onChange={(e) => {
            setFilters({ ...filters, severity: e.target.value });
            setPage(1);
          }}
          className="px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-colors text-sm"
        >
          <option value="all">All Severities</option>
          {uniqueSeverities.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select
          value={filters.host}
          onChange={(e) => {
            setFilters({ ...filters, host: e.target.value });
            setPage(1);
          }}
          className="px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-colors text-sm"
        >
          <option value="all">All Hosts</option>
          {uniqueHosts.map(h => <option key={h} value={h}>{h}</option>)}
        </select>
      </div>

      {/* Pagination Controls */}
      <div className="flex flex-col md:flex-row gap-4 mb-4 justify-between items-center text-sm text-slate-300">
        <div className="flex items-center gap-2">
          <span>Rows per page:</span>
          <select
            value={limit}
            onChange={(e) => {
              setLimit(Number(e.target.value));
              setPage(1);
            }}
            className="bg-slate-800 border border-slate-600 rounded px-2 py-1 focus:outline-none focus:border-blue-500"
          >
            <option value={20}>20</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
            <option value={200}>200</option>
          </select>
        </div>
        <div className="flex items-center gap-2">
          <span>
            {total > 0 ? `${startRange} - ${endRange} of ${total}` : '0 of 0'}
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1 || loading}
              className="p-1 rounded hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages || loading || total === 0}
              className="p-1 rounded hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Logs Table */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500" />
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-700/50">
          <table className="w-full text-sm text-left text-slate-300">
            <thead className="text-xs uppercase bg-slate-800/50 text-slate-400">
              <tr>
                <th className="px-4 py-3">Timestamp</th>
                <th className="px-4 py-3">Host</th>
                <th className="px-4 py-3">OS</th>
                <th className="px-4 py-3">Software</th>
                <th className="px-4 py-3">Version</th>
                <th className="px-4 py-3">Event Type</th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Message</th>
              </tr>
            </thead>
            <tbody>
              {logs.length > 0 ? (
                logs.map((log, idx) => (
                  <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3 whitespace-nowrap text-slate-400">
                      {log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A'}
                    </td>
                    <td className="px-4 py-3 font-medium text-white">{log.host || 'Unknown'}</td>
                    <td className="px-4 py-3">{log.os || 'N/A'}</td>
                    <td className="px-4 py-3 text-blue-400">{log.software || 'N/A'}</td>
                    <td className="px-4 py-3">{log.version || 'N/A'}</td>
                    <td className="px-4 py-3">
                      <span className="bg-slate-800 px-2 py-1 rounded text-xs font-mono">
                        {log.event_type || 'N/A'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-block px-2 py-1 rounded text-xs font-semibold border ${getSeverityColor(log.severity)}`}>
                        {log.severity || 'info'}
                      </span>
                    </td>
                    <td className="px-4 py-3 max-w-xs truncate" title={log.message}>
                      {log.message || 'N/A'}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" className="px-4 py-8 text-center text-slate-500">
                    No normalized logs found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </motion.section>
  );
}
