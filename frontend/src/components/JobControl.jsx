import React, { useState, useEffect } from 'react';
import { runJob, getTaskStatus } from '../api';
import { Play, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function JobControl({ title, jobName, description, color = "blue" }) {
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState(null);
    const [taskId, setTaskId] = useState(null);

    const startJob = async () => {
        setLoading(true);
        setStatus(null);
        try {
            const res = await runJob(jobName);
            setTaskId(res.data.task_id);
            pollStatus(res.data.task_id);
        } catch (err) {
            console.error(err);
            setLoading(false);
            setStatus({ state: 'failed', msg: 'Failed to start' });
        }
    };

    const pollStatus = (id) => {
        const interval = setInterval(async () => {
            try {
                const res = await getTaskStatus(id);
                const s = res.data;
                setStatus(s);
                if (s.state === 'success' || s.state === 'failed') {
                    clearInterval(interval);
                    setLoading(false);
                }
            } catch (err) {
                clearInterval(interval);
                setLoading(false);
            }
        }, 1000);
    };

    const colors = {
        blue: "from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 shadow-blue-500/25",
        green: "from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 shadow-emerald-500/25",
        red: "from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-400 shadow-rose-500/25",
        purple: "from-violet-600 to-violet-500 hover:from-violet-500 hover:to-violet-400 shadow-violet-500/25",
    };

    const statusColors = {
        success: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
        failed: "text-rose-400 bg-rose-400/10 border-rose-400/20",
        running: "text-blue-400 bg-blue-400/10 border-blue-400/20",
        pending: "text-slate-400 bg-slate-400/10 border-slate-400/20"
    };

    return (
        <motion.div
            whileHover={{ y: -8, transition: { duration: 0.3 } }}
            className="bg-slate-900/30 backdrop-blur-xl border border-slate-700/40 p-6 rounded-2xl shadow-2xl flex flex-col h-full overflow-hidden relative group"
            style={{
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
                background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.3) 100%)',
                backdropFilter: 'blur(16px)',
                WebkitBackdropFilter: 'blur(16px)'
            }}
        >
            {/* Glass shine effect */}
            <div className="absolute inset-0 rounded-2xl pointer-events-none overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white to-transparent opacity-20" />
                <div className="absolute top-0 left-0 w-32 h-32 bg-gradient-to-br from-blue-400/10 to-transparent rounded-full blur-2xl -translate-x-1/2 -translate-y-1/2 group-hover:scale-150 transition-transform duration-500" />
            </div>

            <div className="flex-1 relative z-10">
                <h3 className="text-xl font-bold mb-2 text-white flex items-center gap-2">
                    {title}
                    {loading && <span className="flex h-2 w-2 rounded-full bg-blue-500 animate-pulse shadow-lg shadow-blue-500/50" />}
                </h3>
                <p className="text-slate-400 mb-6 text-sm leading-relaxed">{description}</p>
            </div>

            <div className="mt-auto space-y-4 relative z-10">
                <button
                    onClick={startJob}
                    disabled={loading}
                    className={`w-full py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 text-white font-semibold transition-all duration-300 bg-gradient-to-r shadow-lg transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none relative overflow-hidden group/btn ${colors[color]}`}
                    style={{
                        boxShadow: `0 8px 20px ${color === 'red' ? 'rgba(244, 63, 94, 0.3)' : color === 'green' ? 'rgba(34, 197, 94, 0.3)' : color === 'purple' ? 'rgba(168, 85, 247, 0.3)' : 'rgba(59, 130, 246, 0.3)'}`,
                        backdropFilter: 'blur(8px)',
                    }}
                >
                    <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity duration-300" />
                    {loading ? <Loader2 className="animate-spin w-5 h-5" /> : <Play className="w-5 h-5 fill-current" />}
                    {loading ? 'Processing...' : 'Run Task'}
                </button>

                <AnimatePresence>
                    {status && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className={`p-3 rounded-lg border text-sm backdrop-blur-md ${statusColors[status.state] || statusColors.pending}`}
                            style={{
                                boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
                                backdropFilter: 'blur(12px)',
                                WebkitBackdropFilter: 'blur(12px)'
                            }}
                        >
                            <div className="flex items-center gap-2 mb-2">
                                {status.state === 'success' && <CheckCircle className="w-4 h-4" />}
                                {status.state === 'failed' && <XCircle className="w-4 h-4" />}
                                {status.state === 'running' && <Loader2 className="w-4 h-4 animate-spin" />}
                                <span className="capitalize font-semibold">{status.state}</span>
                            </div>

                            {status.msg && <div className="text-xs opacity-80 mb-2">{status.msg}</div>}

                            {status.progress !== undefined && (
                                <div className="w-full bg-slate-700/50 h-1.5 rounded-full overflow-hidden backdrop-blur-md border border-slate-600/30">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: `${status.progress}%` }}
                                        transition={{ duration: 0.5 }}
                                        className={`h-full rounded-full shadow-lg ${color === 'red' ? 'bg-gradient-to-r from-rose-500 to-rose-400' : color === 'green' ? 'bg-gradient-to-r from-emerald-500 to-emerald-400' : color === 'purple' ? 'bg-gradient-to-r from-violet-500 to-violet-400' : 'bg-gradient-to-r from-blue-500 to-blue-400'}`}
                                    />
                                </div>
                            )}
                        </motion.div>
                    )}

                    {status && status.logs && status.logs.length > 0 && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            className="mt-2 p-3 bg-slate-950/50 rounded-lg border border-slate-800 font-mono text-xs text-slate-400 max-h-32 overflow-y-auto"
                        >
                            {status.logs.map((log, i) => (
                                <div key={i} className="whitespace-pre-wrap mb-1">
                                    <span className="text-slate-600">[{new Date(log.time * 1000).toLocaleTimeString()}]</span> {log.message}
                                </div>
                            ))}
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </motion.div>
    );
}
