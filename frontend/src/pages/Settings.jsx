import { useState } from "react";

export default function Settings() {
  const [persona, setPersona] = useState("General");
  const [language, setLanguage] = useState("en");
  const [biasThreshold, setBiasThreshold] = useState("0.3");
  const [apiUrl, setApiUrl] = useState("http://localhost:8000");

  return (
    <div>
      <div className="page-header">
        <h2>⚙️ Settings</h2>
        <p>Configure your NewsGPT Navigator preferences.</p>
      </div>

      <div className="settings-grid">
        {/* Persona Settings */}
        <div className="glass-card settings-card">
          <h3>👤 Default Persona</h3>
          <div className="setting-item">
            <label htmlFor="settings-persona">Preferred persona for analysis</label>
            <select
              id="settings-persona"
              value={persona}
              onChange={(e) => setPersona(e.target.value)}
            >
              <option value="General">General — Balanced briefing</option>
              <option value="Student">Student — Simple language</option>
              <option value="Investor">Investor — Market-focused</option>
              <option value="Beginner">Beginner — No jargon</option>
            </select>
          </div>
        </div>

        {/* Language Settings */}
        <div className="glass-card settings-card">
          <h3>🌍 Default Language</h3>
          <div className="setting-item">
            <label htmlFor="settings-language">Translation language</label>
            <select
              id="settings-language"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              <option value="en">English</option>
              <option value="hi">Hindi (हिन्दी)</option>
              <option value="ta">Tamil (தமிழ்)</option>
              <option value="bn">Bengali (বাংলা)</option>
              <option value="te">Telugu (తెలుగు)</option>
              <option value="kn">Kannada (ಕನ್ನಡ)</option>
              <option value="mr">Marathi (मराठी)</option>
              <option value="pa">Punjabi (ਪੰਜਾਬੀ)</option>
            </select>
          </div>
        </div>

        {/* Compliance Settings */}
        <div className="glass-card settings-card">
          <h3>🛡️ Compliance</h3>
          <div className="setting-item">
            <label htmlFor="settings-threshold">Bias threshold (0-1)</label>
            <input
              id="settings-threshold"
              type="number"
              min="0"
              max="1"
              step="0.05"
              value={biasThreshold}
              onChange={(e) => setBiasThreshold(e.target.value)}
            />
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
            Lower values = stricter compliance. Default: 0.3
          </div>
        </div>

        {/* Connection Settings */}
        <div className="glass-card settings-card">
          <h3>🔌 API Connection</h3>
          <div className="setting-item">
            <label htmlFor="settings-api">Backend URL</label>
            <input
              id="settings-api"
              type="text"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
            />
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
            Default: http://localhost:8000
          </div>
        </div>

        {/* System Info */}
        <div className="glass-card settings-card">
          <h3>ℹ️ System Info</h3>
          <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
            <div style={{ marginBottom: "0.5rem" }}>
              <strong>LLM Provider:</strong> Groq (Free Tier)
            </div>
            <div style={{ marginBottom: "0.5rem" }}>
              <strong>Fast Model:</strong> llama-3.1-8b-instant
            </div>
            <div style={{ marginBottom: "0.5rem" }}>
              <strong>Power Model:</strong> llama-3.3-70b-versatile
            </div>
            <div style={{ marginBottom: "0.5rem" }}>
              <strong>Embeddings:</strong> all-MiniLM-L6-v2
            </div>
            <div>
              <strong>Vector Store:</strong> FAISS (local)
            </div>
          </div>
        </div>

        {/* Agent Pipeline */}
        <div className="glass-card settings-card">
          <h3>🤖 Agent Pipeline</h3>
          <div className="pipeline-steps" style={{ justifyContent: "flex-start" }}>
            <span className="pipeline-step done">Orchestrator</span>
            <span className="pipeline-arrow">→</span>
            <span className="pipeline-step done">Fetch</span>
            <span className="pipeline-arrow">→</span>
            <span className="pipeline-step done">Analysis</span>
            <span className="pipeline-arrow">→</span>
            <span className="pipeline-step done">Compliance</span>
            <span className="pipeline-arrow">→</span>
            <span className="pipeline-step done">Delivery</span>
          </div>
          <div style={{ marginTop: "0.75rem", fontSize: "0.78rem", color: "var(--text-muted)" }}>
            All agents active. Auto-retry on failure. Audit trail enabled.
          </div>
        </div>
      </div>
    </div>
  );
}
