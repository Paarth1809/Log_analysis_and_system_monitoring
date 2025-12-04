import React, { useEffect, useState } from 'react';
import { getCVEs } from '../api';
import { AlertTriangle, Package, ChevronLeft, ChevronRight, X, ExternalLink, Calendar, Shield } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function VulnerabilitiesSection() {
  const [vulns, setVulns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [selectedVuln, setSelectedVuln] = useState(null);

  // Pagination State
  const [page, setPage] = useState(1);
  const [limit] = useState(100);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchVulns();
  }, [page, filter]);

  const fetchVulns = async () => {
    try {
      setLoading(true);
      const skip = (page - 1) * limit;
      const res = await getCVEs({ limit, skip });

      if (res.data && res.data.items) {
        setVulns(res.data.items);
        setTotal(res.data.total);
      } else if (Array.isArray(res.data)) {
        setVulns(res.data);
        setTotal(res.data.length);
      }
    } catch (err) {
      console.error('Error fetching vulnerabilities:', err);
      setVulns([]);
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(total / limit);

  const getSeverityStats = () => {
    const stats = { critical: 0, high: 0, medium: 0, low: 0 };
    vulns.forEach(v => {
      const severity = v.severity?.toLowerCase() || 'low';
      if (stats.hasOwnProperty(severity)) stats[severity]++;
    });
    return stats;
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'bg-red-500/10 border-red-500/30 text-red-400';
      case 'high': return 'bg-orange-500/10 border-orange-500/30 text-orange-400';
      case 'medium': return 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400';
      case 'low': return 'bg-blue-500/10 border-blue-500/30 text-blue-400';
      default: return 'bg-slate-500/10 border-slate-500/30 text-slate-400';
    }
  };

  const filteredVulns = filter === 'all'
    ? vulns
    : vulns.filter(v => v.severity?.toLowerCase() === filter);

  const stats = getSeverityStats();

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="bg-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 shadow-2xl relative"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-orange-400" />
          <h2 className="text-2xl font-bold text-white">Vulnerabilities (CVEs)</h2>
          <span className="text-sm text-slate-400 bg-slate-800 px-2 py-1 rounded-md">
            Total: {total.toLocaleString()}
          </span>
        </div>
        <button
          onClick={fetchVulns}
          className="px-4 py-2 bg-orange-600 hover:bg-orange-500 text-white rounded-lg font-medium transition-colors text-sm"
        >
          Refresh
        </button>
      </div>

      {/* Severity Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Critical', value: stats.critical, color: 'text-red-400' },
          { label: 'High', value: stats.high, color: 'text-orange-400' },
          { label: 'Medium', value: stats.medium, color: 'text-yellow-400' },
          { label: 'Low', value: stats.low, color: 'text-blue-400' }
        ].map((stat, idx) => (
          <div key={idx} className="bg-slate-800/50 border border-slate-700 rounded-lg p-3">
            <div className="text-xs text-slate-400 mb-1">{stat.label}</div>
            <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
          </div>
        ))}
      </div>

      {/* Filters & Pagination */}
      <div className="mb-6 flex flex-wrap gap-2 items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors text-sm ${filter === 'all' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
          >
            All
          </button>
          {['critical', 'high', 'medium', 'low'].map(sev => (
            <button
              key={sev}
              onClick={() => setFilter(sev)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors text-sm capitalize ${filter === sev ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              {sev}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1 || loading}
            className="p-2 bg-slate-800 text-slate-300 rounded-lg hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-sm text-slate-400">
            Page {page} of {totalPages || 1}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages || loading}
            className="p-2 bg-slate-800 text-slate-300 rounded-lg hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Vulnerabilities List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500" />
        </div>
      ) : (
        <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
          {filteredVulns.length > 0 ? (
            filteredVulns.map((vuln, idx) => (
              <motion.div
                key={idx}
                onClick={() => setSelectedVuln(vuln)}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.02 }}
                className="bg-slate-800/30 border border-slate-700/50 rounded-lg p-4 hover:bg-slate-800/50 transition-colors cursor-pointer group"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-start gap-3 flex-1">
                    <Package className="w-5 h-5 text-slate-500 mt-1 flex-shrink-0 group-hover:text-blue-400 transition-colors" />
                    <div>
                      <div className="font-bold text-white group-hover:text-blue-400 transition-colors">{vuln.cve_id || vuln.id || 'Unknown CVE'}</div>
                      <div className="text-xs text-slate-400 mt-1 line-clamp-2">
                        {vuln.description || 'No description available'}
                      </div>
                    </div>
                  </div>
                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold border flex-shrink-0 ${getSeverityColor(vuln.severity)}`}>
                    {vuln.severity || 'Unknown'}
                  </span>
                </div>
                <div className="flex gap-4 text-xs text-slate-400 mt-3">
                  {vuln.cvss_score && <div>CVSS: <span className="text-slate-300 font-semibold">{vuln.cvss_score}</span></div>}
                  {vuln.source && <div>Source: <span className="text-slate-300">{vuln.source}</span></div>}
                  {vuln.last_updated && <div>Updated: <span className="text-slate-300">{new Date(vuln.last_updated).toLocaleDateString()}</span></div>}
                </div>
              </motion.div>
            ))
          ) : (
            <div className="py-8 text-center text-slate-500">
              No vulnerabilities found on this page.
            </div>
          )}
        </div>
      )}

      {/* Detail Modal */}
      <AnimatePresence>
        {selectedVuln && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
            onClick={() => setSelectedVuln(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto shadow-2xl"
            >
              <div className="p-6 space-y-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <Shield className="w-8 h-8 text-blue-500" />
                    <div>
                      <h2 className="text-2xl font-bold text-white">{selectedVuln.cve_id}</h2>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold border ${getSeverityColor(selectedVuln.severity)}`}>
                          {selectedVuln.severity}
                        </span>
                        <span className="text-slate-400 text-sm flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {selectedVuln.last_updated ? new Date(selectedVuln.last_updated).toLocaleDateString() : 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedVuln(null)}
                    className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-slate-400" />
                  </button>
                </div>

                <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                  <h3 className="text-sm font-semibold text-slate-300 mb-2">Description</h3>
                  <p className="text-slate-400 leading-relaxed text-sm">
                    {selectedVuln.description || 'No description available.'}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-800/30 p-4 rounded-xl border border-slate-700/50">
                    <div className="text-sm text-slate-400 mb-1">CVSS Score</div>
                    <div className="text-3xl font-bold text-white">{selectedVuln.cvss_score || 'N/A'}</div>
                  </div>
                  <div className="bg-slate-800/30 p-4 rounded-xl border border-slate-700/50">
                    <div className="text-sm text-slate-400 mb-1">Source</div>
                    <div className="text-xl font-medium text-white">{selectedVuln.source || 'NVD'}</div>
                  </div>
                </div>

                <div className="flex justify-end pt-4 border-t border-slate-800">
                  <a
                    href={`https://nvd.nist.gov/vuln/detail/${selectedVuln.cve_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors text-sm"
                  >
                    View on NVD <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.section>
  );
}
