import React, { useEffect, useState } from 'react';
import { getReports, downloadReport } from '../api';
import { FileText, Download, Clock, File } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Reports() {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchReports();
    }, []);

    const fetchReports = async () => {
        try {
            const res = await getReports();
            setReports(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const formatSize = (bytes) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <FileText className="w-6 h-6 text-blue-400" />
                    <h2 className="text-2xl font-bold text-white">Generated Reports</h2>
                </div>
                <button
                    onClick={fetchReports}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-medium transition-colors"
                >
                    Refresh
                </button>
            </div>

            {loading ? (
                <div className="flex justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
                </div>
            ) : reports.length === 0 ? (
                <div className="text-center py-12 text-slate-400 bg-slate-900/50 rounded-2xl border border-slate-800">
                    <File className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No reports generated yet.</p>
                    <p className="text-sm mt-2">Go to "Python Scripts" and run "Generate Reports".</p>
                </div>
            ) : (
                <div className="grid gap-4">
                    {reports.map((report, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.05 }}
                            className="flex items-center justify-between p-4 bg-slate-900/50 backdrop-blur-sm border border-slate-700/50 rounded-xl hover:bg-slate-800/50 transition-colors group"
                        >
                            <div className="flex items-center gap-4">
                                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${report.format === 'pdf' ? 'bg-red-500/10 text-red-400' : 'bg-blue-500/10 text-blue-400'
                                    }`}>
                                    <FileText className="w-5 h-5" />
                                </div>
                                <div>
                                    <h3 className="font-medium text-white group-hover:text-blue-400 transition-colors">
                                        {report.name}
                                    </h3>
                                    <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                                        <span className="flex items-center gap-1">
                                            <Clock className="w-3 h-3" />
                                            {new Date(report.created_at).toLocaleString()}
                                        </span>
                                        <span>•</span>
                                        <span>{formatSize(report.size)}</span>
                                        <span>•</span>
                                        <span className="uppercase bg-slate-800 px-1.5 py-0.5 rounded text-[10px]">
                                            {report.type}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <a
                                href={downloadReport(report.path)}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
                                title="Download"
                            >
                                <Download className="w-5 h-5" />
                            </a>
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
}
