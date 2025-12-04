import React, { useEffect, useState } from 'react';
import { getMatches } from '../api';
import { ShieldAlert, Server, Activity, Search } from 'lucide-react';
import { motion } from 'framer-motion';

export default function MatchesSection() {
    const [matches, setMatches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchMatches();
    }, []);

    const fetchMatches = async () => {
        try {
            setLoading(true);
            const res = await getMatches({ limit: 50 });
            setMatches(Array.isArray(res.data) ? res.data : res.data.items || []);
        } catch (err) {
            console.error('Error fetching matches:', err);
            setMatches([]);
        } finally {
            setLoading(false);
        }
    };

    const filteredMatches = matches.filter(m => {
        if (!searchTerm) return true;
        const term = searchTerm.toLowerCase();
        return (
            m.host?.toLowerCase().includes(term) ||
            m.cve_id?.toLowerCase().includes(term) ||
            m.software?.toLowerCase().includes(term)
        );
    });

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
                    <ShieldAlert className="w-6 h-6 text-red-400" />
                    <h2 className="text-2xl font-bold text-white">Vulnerability Matches</h2>
                </div>
                <button
                    onClick={fetchMatches}
                    className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg font-medium transition-colors text-sm"
                >
                    Refresh
                </button>
            </div>

            {/* Search */}
            <div className="relative mb-6">
                <Search className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                <input
                    type="text"
                    placeholder="Search matches by host, CVE, or software..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-red-500 transition-colors"
                />
            </div>

            {/* Matches List */}
            {loading ? (
                <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500" />
                </div>
            ) : (
                <div className="space-y-3">
                    {filteredMatches.length > 0 ? (
                        filteredMatches.map((match, idx) => (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.05 }}
                                className="bg-slate-800/30 border border-slate-700/50 rounded-lg p-4 hover:bg-slate-800/50 transition-colors"
                            >
                                <div className="flex items-start justify-between mb-2">
                                    <div className="flex items-start gap-4 flex-1">
                                        <div className={`p-2 rounded-lg ${getSeverityColor(match.severity)}`}>
                                            <Activity className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="font-bold text-white text-lg">{match.cve_id}</span>
                                                <span className={`text-xs px-2 py-0.5 rounded-full border ${getSeverityColor(match.severity)}`}>
                                                    {match.severity}
                                                </span>
                                            </div>
                                            <div className="flex items-center gap-4 text-sm text-slate-400">
                                                <div className="flex items-center gap-1">
                                                    <Server className="w-4 h-4 text-slate-500" />
                                                    <span className="text-slate-300">{match.host}</span>
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    <span className="text-slate-500">Software:</span>
                                                    <span className="text-slate-300">{match.software}</span>
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    <span className="text-slate-500">Version:</span>
                                                    <span className="text-slate-300">{match.version || match.kernel_version || 'N/A'}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-xs text-slate-500">
                                        {match.matched_at ? new Date(match.matched_at).toLocaleString() : ''}
                                    </div>
                                </div>
                            </motion.div>
                        ))
                    ) : (
                        <div className="py-8 text-center text-slate-500">
                            No matches found
                        </div>
                    )}
                </div>
            )}
        </motion.section>
    );
}
