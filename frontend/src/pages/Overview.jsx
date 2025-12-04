import React from 'react';
import { motion } from 'framer-motion';
import { Server, Shield, Zap, AlertTriangle, LayoutDashboard } from 'lucide-react';
import StatsChart from '../components/StatsChart';
import { useOutletContext } from 'react-router-dom';

const StatCard = ({ icon: Icon, label, value, color, gradient }) => (
    <motion.div
        variants={{
            hidden: { y: 20, opacity: 0 },
            visible: {
                y: 0,
                opacity: 1,
                transition: { type: 'spring', stiffness: 100 }
            }
        }}
        whileHover={{ y: -5, transition: { duration: 0.2 } }}
        className="relative overflow-hidden bg-slate-800/50 backdrop-blur-md p-6 rounded-2xl border border-slate-700/50 shadow-xl group"
    >
        <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-500`} />
        <div className="flex items-center gap-4 relative z-10">
            <div className={`p-3 rounded-xl ${color} bg-opacity-20 group-hover:scale-110 transition-transform duration-300`}>
                <Icon className={`w-6 h-6 ${color.replace('bg-', 'text-')}`} />
            </div>
            <div>
                <div className="text-slate-400 text-sm font-medium">{label}</div>
                <div className="text-3xl font-bold text-white tracking-tight">{value || 0}</div>
            </div>
        </div>
    </motion.div>
);

const Overview = () => {
    const { stats } = useOutletContext();

    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: {
            y: 0,
            opacity: 1,
            transition: { type: 'spring', stiffness: 100 }
        }
    };

    const severityData = stats ? Object.entries(stats.severity_counts).map(([k, v]) => ({ name: k, value: v })) : [];
    const topHostsData = stats ? stats.top_hosts.map(h => ({ name: h.host, value: h.count })) : [];

    return (
        <motion.div
            initial="hidden"
            animate="visible"
            variants={{
                hidden: { opacity: 0 },
                visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
            }}
            className="space-y-8"
        >
            <motion.div variants={itemVariants} className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Security Overview</h1>
                    <p className="text-slate-400">Real-time vulnerability monitoring and automated response system.</p>
                </div>
                <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors shadow-lg shadow-blue-500/20 flex items-center gap-2">
                    <LayoutDashboard className="w-4 h-4" />
                    Customize Dashboard
                </button>
            </motion.div>

            {/* Active Monitoring Card */}
            <motion.div variants={itemVariants} className="bg-slate-800/50 backdrop-blur-md border border-slate-700/50 rounded-2xl p-6 shadow-xl">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h3 className="text-xl font-bold text-white flex items-center gap-2">
                            <Zap className="w-5 h-5 text-green-400" />
                            Active Monitoring
                        </h3>
                        <p className="text-slate-400 text-sm mt-1">
                            Automatic engines are running in the background (24/7).
                        </p>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full text-green-400 text-sm font-mono">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                        </span>
                        System Online
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                        { name: 'Log Ingestion', status: 'Auto (Real-time)', color: 'text-blue-400' },
                        { name: 'Vulnerability Matcher', status: 'Auto (Every 5m)', color: 'text-purple-400' },
                        { name: 'Alert Engine', status: 'Auto (Every 1m)', color: 'text-orange-400' }
                    ].map((item) => (
                        <div key={item.name} className="bg-slate-950/50 border border-slate-800 p-4 rounded-lg flex items-center gap-3">
                            <div className={`w-2 h-2 rounded-full ${item.color.replace('text-', 'bg-')}`} />
                            <div>
                                <div className="text-slate-200 font-medium">{item.name}</div>
                                <div className="text-xs text-slate-500 font-mono">{item.status}</div>
                            </div>
                        </div>
                    ))}
                </div>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    icon={Server}
                    label="Total Logs Processed"
                    value={stats?.totals?.logs}
                    color="bg-blue-500"
                    gradient="from-blue-500 to-cyan-500"
                />
                <StatCard
                    icon={Shield}
                    label="CVE Definitions"
                    value={stats?.totals?.cves}
                    color="bg-purple-500"
                    gradient="from-purple-500 to-pink-500"
                />
                <StatCard
                    icon={Zap}
                    label="Active Threats"
                    value={stats?.totals?.matches}
                    color="bg-orange-500"
                    gradient="from-orange-500 to-yellow-500"
                />
                <StatCard
                    icon={AlertTriangle}
                    label="Critical Alerts"
                    value={stats?.totals?.alerts}
                    color="bg-red-500"
                    gradient="from-red-500 to-rose-500"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <motion.div variants={itemVariants}>
                    <StatsChart
                        data={severityData}
                        title="Vulnerability Severity Distribution"
                        color="#f59e0b"
                        type="bar"
                    />
                </motion.div>
                <motion.div variants={itemVariants}>
                    <StatsChart
                        data={topHostsData}
                        title="Top Vulnerable Hosts"
                        color="#ef4444"
                        type="area"
                    />
                </motion.div>
            </div>
        </motion.div>
    );
};

export default Overview;
