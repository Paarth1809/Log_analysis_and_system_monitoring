import React, { useState, useEffect } from 'react';
import './PythonScriptsSection.css';

const ScriptRunner = ({ script, onExecute }) => {
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleExecute = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/scripts/${script.name}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      setTaskId(data.task_id);
      pollStatus(data.task_id);
    } catch (err) {
      console.error('Error executing script:', err);
      setLoading(false);
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
        }
      } catch (err) {
        console.error('Error polling status:', err);
      }
    }, 500);
  };

  const getStatusColor = () => {
    if (!status) return '#3b82f6';
    if (status.state === 'running') return '#f59e0b';
    if (status.state === 'success') return '#10b981';
    if (status.state === 'failed') return '#ef4444';
    return '#6b7280';
  };

  const getStatusText = () => {
    if (!status) return 'Ready';
    return status.state.charAt(0).toUpperCase() + status.state.slice(1);
  };

  return (
    <div className="script-card" style={{ borderLeft: `4px solid ${getStatusColor()}` }}>
      <div className="script-header">
        <div>
          <h3 className="script-title">{script.name.replace(/_/g, ' ')}</h3>
          <p className="script-description">{script.description}</p>
        </div>
      </div>

      {status && (
        <div className="script-status">
          <div className="status-badge" style={{ backgroundColor: getStatusColor() }}>
            {getStatusText()}
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${status.progress || 0}%` }}
            />
          </div>
          {status.msg && <p className="status-message">{status.msg}</p>}
          {status.error && <p className="error-message">{status.error}</p>}
        </div>
      )}

      <button
        onClick={handleExecute}
        disabled={loading}
        className="execute-button"
        style={{
          opacity: loading ? 0.6 : 1,
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Executing...' : 'Run Script'}
      </button>
    </div>
  );
};

const PythonScriptsSection = () => {
  const [scripts, setScripts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchScripts();
  }, []);

  const fetchScripts = async () => {
    try {
      const response = await fetch('http://localhost:8000/scripts/list');
      const data = await response.json();
      setScripts(data.scripts || []);
    } catch (err) {
      console.error('Error fetching scripts:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="python-scripts-container">Loading scripts...</div>;
  }

  return (
    <div className="python-scripts-container">
      <div className="section-header">
        <h2 className="section-title">⚙️ Python Scripts Automation</h2>
        <p className="section-subtitle">Execute security automation scripts with real-time progress tracking</p>
      </div>

      <div className="scripts-grid">
        {scripts.map((script) => (
          <ScriptRunner key={script.name} script={script} />
        ))}
      </div>
    </div>
  );
};

export default PythonScriptsSection;
