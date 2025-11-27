// dashboard/assets/js/api.js

const API_BASE = "http://localhost:8000";

// Generic GET request
async function apiGet(endpoint) {
    const url = API_BASE + endpoint;
    const res = await fetch(url);
    return res.json();
}

// Build query strings
function qs(params) {
    return (
        "?" +
        Object.entries(params)
            .filter(([_, v]) => v !== null && v !== undefined && v !== "")
            .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
            .join("&")
    );
}
