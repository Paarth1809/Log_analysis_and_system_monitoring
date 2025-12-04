import React from 'react';
import { motion } from 'framer-motion';
import { Activity } from 'lucide-react';
import JobControl from '../components/JobControl';

const Operations = () => {
    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: {
            y: 0,
            opacity: 1,
            transition: { type: 'spring', stiffness: 100 }
        }
    };

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
            <motion.div variants={itemVariants} className="flex items-center gap-3 mb-6">
                <Activity className="w-6 h-6 text-blue-500" />
                <h2 className="text-2xl font-bold text-white">Automation Control Center</h2>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <JobControl
                    title="Log Parser"
                    jobName="parser"
                    description="Ingest and normalize raw security logs"
                    color="blue"
                />
                <JobControl
                    title="Vuln Matcher"
                    jobName="matching"
                    description="Correlate logs with CVE database"
                    color="purple"
                />
                <JobControl
                    title="Alert Engine"
                    jobName="alerts"
                    description="Dispatch notifications for critical findings"
                    color="red"
                />
                <JobControl
                    title="Report Gen"
                    jobName="reports"
                    description="Compile and export compliance reports"
                    color="green"
                />
            </div>
        </motion.div>
    );
};

export default Operations;
