import React from "react";
import PythonScriptsSection from "../components/PythonScriptsSection";
import "../styles.css";

export default function PythonScripts() {
  return (
    <div className="page-container" style={{ padding: "2rem" }}>
      <div className="page-header" style={{ marginBottom: "2rem" }}>
        <h1 style={{ 
          fontSize: "2rem", 
          fontWeight: "700", 
          color: "#fff",
          margin: "0 0 0.5rem 0"
        }}>
          Python Scripts Automation
        </h1>
        <p style={{ 
          fontSize: "1rem", 
          color: "#94a3b8",
          margin: 0
        }}>
          Execute security automation scripts with real-time progress tracking and result monitoring
        </p>
      </div>
      
      <PythonScriptsSection />
    </div>
  );
}
