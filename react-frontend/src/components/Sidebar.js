import React from "react";
import { NavLink } from "react-router-dom";
import "./Sidebar.css";

const Sidebar = () => {
  return (
    <div className="sidebar">
      <div className="sidebar-title">CyArt SOC</div>
      <div className="sidebar-subtitle">VULNERABILITY CORE</div>

      <div className="sidebar-menu">
        <div className="sidebar-section">
          <div className="sidebar-section-title">Main Menu</div>
          <NavLink to="/" end>
            <span>◆</span>
            Overview
          </NavLink>
          <NavLink to="/logs">
            <span>◆</span>
            System Logs
          </NavLink>
          <NavLink to="/cves">
            <span>◆</span>
            Vulnerabilities
          </NavLink>
          <NavLink to="/alerts">
            <span>◆</span>
            Security Alerts
          </NavLink>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-section-title">Analysis</div>
          <NavLink to="/charts">
            <span>◆</span>
            Analytics
          </NavLink>
          <NavLink to="/reports">
            <span>◆</span>
            Compliance
          </NavLink>
          <NavLink to="/jobs">
            <span>◆</span>
            Operations
          </NavLink>
          <NavLink to="/scripts">
            <span>◆</span>
            Python Scripts
          </NavLink>
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="system-status">
          <div className="status-indicator">
            <span className="status-dot"></span>
            System Online
          </div>
          <div className="status-label">FastAPI Backend</div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
