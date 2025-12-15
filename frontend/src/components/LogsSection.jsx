import React, { useEffect, useState } from 'react';
import { getLogs } from '../api';
import { Clock, Server, Search, ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';
import { motion } from 'framer-motion';

export default function LogsSection() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [category, setCategory] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(100);

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      fetchLogs();
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [searchTerm, severityFilter, category, page, limit]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const skip = (page - 1) * limit;
      const res = await getLogs({
        limit,
        skip,
        q: searchTerm || undefined,
        severity: severityFilter !== 'all' ? severityFilter : undefined,
        category: category !== 'all' ? category : undefined
      });

      if (res.data) {
        setLogs(res.data.items || []);
        setTotal(res.data.total || 0);
      }
    } catch (err) {
      console.error('Error fetching logs:', err);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    setPage(1); // Reset to first page on search
  };

  const totalPages = Math.ceil(total / limit);
  const startRange = (page - 1) * limit + 1;
  const endRange = Math.min(page * limit, total);

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'bg-red-500/10 border-red-500/30 text-red-400';
      case 'high': return 'bg-orange-500/10 border-orange-500/30 text-orange-400';
      case 'medium': return 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400';
      case 'low': return 'bg-blue-500/10 border-blue-500/30 text-blue-400';
      default: return 'bg-slate-500/10 border-slate-500/30 text-slate-400';
    }
  };

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 shadow-2xl"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Clock className="w-6 h-6 text-blue-400" />
          <h2 className="text-2xl font-bold text-white">System Logs</h2>
        </div>
        <button
          onClick={fetchLogs}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors text-sm flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Controls */}
      <div className="flex flex-col md:flex-row gap-4 mb-6 justify-between items-center">
        <div className="flex gap-4 w-full md:w-auto flex-1">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search logs..."
              value={searchTerm}
              onChange={handleSearch}
              className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>

          <select
            value={category}
            onChange={(e) => {
              setCategory(e.target.value);
              setPage(1);
            }}
            className="px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-colors"
          >
            <option value="all">All Categories</option>
            <option value="Network">Network Logs</option>
            <option value="Windows">Windows Logs</option>
            <option value="Web">Web Server Logs</option>
            <option value="Authentication">Auth Logs</option>
            <option value="System">System Logs</option>
          </select>

          <select
            value={severityFilter}
            onChange={(e) => {
              setSeverityFilter(e.target.value);
              setPage(1);
            }}
            className="px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-colors"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
            <option value="info">Info</option>
          </select>
        </div>

        <div className="flex items-center gap-4 text-sm text-slate-300">
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
      </div>

      {/* Logs Table */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
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
                  <tr
                    key={log._id || idx}
                    className="border-b border-slate-700/50 hover:bg-slate-800/30 transition-colors"
                  >
                    <td className="px-4 py-3 whitespace-nowrap text-slate-400">
                      {log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A'}
                    </td>
                    <td className="px-4 py-3 font-medium text-white">
                      <div className="flex items-center gap-2">
                        <Server className="w-3 h-3 text-slate-500" />
                        {log.host || 'Unknown'}
                      </div>
                    </td>
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
                    <td className="px-4 py-3 max-w-md truncate" title={log.message}>
                      {log.message || 'N/A'}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" className="py-8 text-center text-slate-500">
                    No logs found
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
