import React, { useState, useEffect } from 'react';
import { Play, Loader2, CheckCircle, XCircle, Download, RefreshCw, Eye } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ScriptRunner({ title, scriptName, description, color = "blue", icon: Icon }) {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [results, setResults] = useState(null);
  const [showResults, setShowResults] = useState(false);

  const runScript = async () => {
    setLoading(true);
    setStatus(null);
    setResults(null);
    try {
      const response = await fetch(`http://localhost:8000/scripts/${scriptName}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      
      if (response.ok) {
        setTaskId(data.task_id);
        pollStatus(data.task_id);
      } else {
        setStatus({ state: 'failed', msg: data.detail || 'Failed to start script' });
        setLoading(false);
      }
    } catch (err) {
      console.error(err);
      setLoading(false);
      setStatus({ state: 'failed', msg: 'Failed to start script' });
    }
  };

  const pollStatus = (id) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/scripts/status/${id}`);
        const data = await response.json();
        setStatus(data);
        
        if (data.state === 'success' || data.state === 'failed') {
          clearInterval(interval);
          setLoading(false);
          if (data.result) {
            setResults(data.result);
          }
        }
      } catch (err) {
        clearInterval(interval);
        setLoading(false);
      }
    }, 1000);
  };

  const colors = {
    blue: "from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 shadow-blue-500/25",
    purple: "from-violet-600 to-violet-500 hover:from-violet-500 hover:to-violet-400 shadow-violet-500/25",
    green: "from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 shadow-emerald-500/25",
    orange: "from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 shadow-orange-500/25",
    red: "from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-400 shadow-rose-500/25",
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
      <div className="absolute inset-0 rounded-2xl pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white to-transparent opacity-20" />
        <div className="absolute top-0 left-0 w-32 h-32 bg-gradient-to-br from-blue-400/10 to-transparent rounded-full blur-2xl -translate-x-1/2 -translate-y-1/2 group-hover:scale-150 transition-transform duration-500" />
      </div>

      <div className="flex-1 relative z-10">
        <div className="flex items-center gap-3 mb-2">
          {Icon && <Icon className="w-6 h-6 text-blue-400" />}
          <h3 className="text-xl font-bold text-white">
            {title}
            {loading && <span className="flex h-2 w-2 rounded-full bg-blue-500 animate-pulse shadow-lg shadow-blue-500/50 ml-2 inline-block" />}
          </h3>
        </div>
        <p className="text-slate-400 mb-6 text-sm leading-relaxed">{description}</p>
      </div>

      <div className="mt-auto space-y-4 relative z-10">
        <button
          onClick={runScript}
          disabled={loading}
          className={`w-full py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 text-white font-semibold transition-all duration-300 bg-gradient-to-r shadow-lg transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none relative overflow-hidden group/btn ${colors[color]}`}
          style={{
            boxShadow: `0 8px 20px ${color === 'red' ? 'rgba(244, 63, 94, 0.3)' : color === 'green' ? 'rgba(34, 197, 94, 0.3)' : color === 'purple' ? 'rgba(168, 85, 247, 0.3)' : 'rgba(59, 130, 246, 0.3)'}`,
            backdropFilter: 'blur(8px)',
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity duration-300" />
          {loading ? <Loader2 className="animate-spin w-5 h-5" /> : <Play className="w-5 h-5 fill-current" />}
          {loading ? 'Running...' : 'Run Script'}
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
                    className={`h-full rounded-full shadow-lg bg-gradient-to-r ${color === 'red' ? 'from-rose-500 to-rose-400' : color === 'green' ? 'from-emerald-500 to-emerald-400' : color === 'purple' ? 'from-violet-500 to-violet-400' : 'from-blue-500 to-blue-400'}`}
                  />
                </div>
              )}

              {status.state === 'success' && results && (
                <motion.button
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  onClick={() => setShowResults(!showResults)}
                  className="mt-3 w-full flex items-center justify-center gap-2 px-3 py-2 bg-blue-500/20 hover:bg-blue-500/30 rounded-lg text-xs font-medium transition-colors"
                >
                  <Eye className="w-3 h-3" />
                  {showResults ? 'Hide Results' : 'View Results'}
                </motion.button>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {showResults && results && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-slate-800/50 border border-slate-700 rounded-lg p-3 max-h-48 overflow-y-auto text-xs text-slate-300 font-mono"
          >
            <pre>{JSON.stringify(results, null, 2)}</pre>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
