import React, { useEffect, useState } from 'react';
import { getAlerts } from '../api';
import { Bell, AlertTriangle, ShieldAlert, Info, Clock } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Alerts() {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAlerts();
    }, []);

    const fetchAlerts = async () => {
        try {
            const res = await getAlerts({ limit: 50 });
            setAlerts(res.data.items || []);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const getSeverityColor = (sev) => {
        switch (sev?.toLowerCase()) {
            case 'critical': return 'text-rose-400 bg-rose-400/10 border-rose-400/20';
            case 'high': return 'text-orange-400 bg-orange-400/10 border-orange-400/20';
            case 'medium': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
            default: return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Bell className="w-6 h-6 text-blue-400" />
                    <h2 className="text-2xl font-bold text-white">System Alerts</h2>
                </div>
                <button
                    onClick={fetchAlerts}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-medium transition-colors"
                >
                    Refresh
                </button>
            </div>

            {loading ? (
                <div className="flex justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
                </div>
            ) : alerts.length === 0 ? (
                <div className="text-center py-12 text-slate-400 bg-slate-900/50 rounded-2xl border border-slate-800">
                    <ShieldAlert className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No alerts generated yet.</p>
                    <p className="text-sm mt-2">Go to "Python Scripts" and run "Send Alerts".</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {alerts.map((alert, idx) => (
                        <motion.div
                            key={alert._id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.05 }}
                            className="bg-slate-900/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4 hover:bg-slate-800/50 transition-colors"
                        >
                            <div className="flex items-start gap-4">
                                <div className={`p-2 rounded-lg ${getSeverityColor(alert.severity)}`}>
                                    <AlertTriangle className="w-5 h-5" />
                                </div>

                                <div className="flex-1">
                                    <div className="flex items-center justify-between mb-1">
                                        <h3 className="font-bold text-white flex items-center gap-2">
                                            {alert.rule_name || alert.cve_id}
                                            <span className={`text-xs px-2 py-0.5 rounded-full border ${getSeverityColor(alert.severity)}`}>
                                                {alert.severity}
                                            </span>
                                            {alert.rule_type && (
                                                <span className="text-xs px-2 py-0.5 rounded-full border border-slate-600 text-slate-400">
                                                    {alert.rule_type}
                                                </span>
                                            )}
                                        </h3>
                                        <span className="text-xs text-slate-400 flex items-center gap-1">
                                            <Clock className="w-3 h-3" />
                                            {new Date(alert.alert_generated_at).toLocaleString()}
                                        </span>
                                    </div>

                                    <p className="text-slate-300 text-sm mb-2">
                                        {alert.description}
                                    </p>

                                    <p className="text-slate-400 text-xs mb-2">
                                        Detected on <span className="text-blue-400 font-mono">{alert.host}</span>
                                    </p>

                                    {alert.details && (
                                        <div className="bg-slate-950/50 p-2 rounded border border-slate-800 text-xs font-mono text-slate-400 overflow-x-auto">
                                            {JSON.stringify(alert.details, null, 2)}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
}
