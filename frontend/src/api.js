import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,
});

export const getStats = () => api.get('/stats');
export const getLogs = (params) => api.get('/logs', { params });
export const getCves = (params) => api.get('/cves', { params });
export const getCVEs = (params) => api.get('/cves', { params }); // Alias
export const getAlerts = (params) => api.get('/alerts', { params });
export const getMatches = (params) => api.get('/matches', { params });
export const runJob = (jobName) => api.post(`/run/${jobName}`);
export const getTaskStatus = (taskId) => api.get(`/run/status/${taskId}`);
export const getTaskList = () => api.get('/run/list');

// Script execution endpoints
export const executeScript = (scriptName) => api.post(`/scripts/${scriptName}`);
export const getScriptStatus = (taskId) => api.get(`/scripts/status/${taskId}`);
export const listScripts = () => api.get('/scripts/list');
export const getScriptTasks = () => api.get('/scripts/tasks');

export const getReports = () => api.get('/reports/list');
export const downloadReport = (path) => `${API_URL}/reports/download/${path}`;
export const runScript = (scriptName) => api.post(`/scripts/${scriptName}`); // Alias for executeScript
