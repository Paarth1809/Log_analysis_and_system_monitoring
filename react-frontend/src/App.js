// src/App.js
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import NavbarTop from "./components/NavbarTop";

import "./App.css";

import Home from "./pages/Home";
import Logs from "./pages/Logs";
import Cves from "./pages/Cves";
import Alerts from "./pages/Alerts";
import Reports from "./pages/Reports";
import Charts from "./pages/Charts";
import RunJobs from "./pages/RunJobs";
import PythonScripts from "./pages/PythonScripts";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-root">

        <div className="main-content">
          <NavbarTop />
          <div style={{ flex: 1, overflow: "visible", minHeight: "100vh" }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/logs" element={<Logs />} />
              <Route path="/cves" element={<Cves />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/charts" element={<Charts />} />
              <Route path="/jobs" element={<RunJobs />} />
              <Route path="/scripts" element={<PythonScripts />} />
            </Routes>
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
}
