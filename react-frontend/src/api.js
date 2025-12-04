// src/api.js
import { API_BASE } from "./config";

async function request(path, opts = {}) {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, opts);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`${response.status} ${response.statusText} - ${text}`);
  }
  return response.json();
}

export function health() {
  return request("/health");
}

export function getLogs({ limit = 50, skip = 0, host, software, q, start, end } = {}) {
  const params = new URLSearchParams();
  if (limit) params.set("limit", limit);
  if (skip) params.set("skip", skip);
  if (host) params.set("host", host);
  if (software) params.set("software", software);
  if (q) params.set("q", q);
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  return request(`/logs?${params.toString()}`);
}

export function getCves({ q = "", limit = 50, skip = 0 } = {}) {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  params.set("limit", limit);
  params.set("skip", skip);
  return request(`/cves?${params.toString()}`);
}

export function getAlerts({ limit = 50, skip = 0 } = {}) {
  return request(`/alerts?limit=${limit}&skip=${skip}`);
}

export function getStats() {
  return request("/stats");
}

export function runParser() {
  return fetch(`${API_BASE}/run/parser`, { method: "POST" }).then(r => r.json());
}
export function runMatching() {
  return fetch(`${API_BASE}/run/matching`, { method: "POST" }).then(r => r.json());
}
export function runAlerts() {
  return fetch(`${API_BASE}/run/alerts`, { method: "POST" }).then(r => r.json());
}
export function runReports() {
  return fetch(`${API_BASE}/run/reports`, { method: "POST" }).then(r => r.json());
}

export function listJobs() {
  return request("/run/list");
}
export function getJobStatus(taskId) {
  return request(`/run/status/${taskId}`);
}
export function listSchedules() {
  return request(`/jobs/list`);
}

export function scheduleJob(name, minutes, enabled = true) {
  return fetch(`${API_BASE}/jobs/schedule`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, minutes, enabled }),
  }).then(r => r.json());
}

export function unscheduleJob(name) {
  return fetch(`${API_BASE}/jobs/unschedule/${encodeURIComponent(name)}`, { method: "POST" }).then(r => r.json());
}

export function runJobNow(name) {
  return fetch(`${API_BASE}/jobs/run/${encodeURIComponent(name)}`, { method: "POST" }).then(r => r.json());
}

export function getLastRun(name) {
  return request(`/jobs/last-run/${encodeURIComponent(name)}`);
}
