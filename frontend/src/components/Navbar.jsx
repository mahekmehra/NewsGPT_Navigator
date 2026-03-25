export default function Navbar({ activePage, onNavigate }) {
  return (
    <nav className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">🧠</div>
        <div>
          <h1>NewsGPT</h1>
          <span>11-Agent Intelligence</span>
        </div>
      </div>

      <div className="sidebar-nav">
        <div className="nav-section-label">Core</div>
        <button
          className={`nav-link ${activePage === "dashboard" ? "active" : ""}`}
          onClick={() => onNavigate("dashboard")}
        >
          <span className="nav-icon">🏠</span>
          Dashboard
        </button>

        <button
          className={`nav-link ${activePage === "results" ? "active" : ""}`}
          onClick={() => onNavigate("results")}
        >
          <span className="nav-icon">📊</span>
          Results
        </button>

        <div className="nav-section-label">Analysis</div>
        <button
          className={`nav-link ${activePage === "entities" ? "active" : ""}`}
          onClick={() => onNavigate("entities")}
        >
          <span className="nav-icon">🔬</span>
          Entity Map
        </button>

        <button
          className={`nav-link ${activePage === "angles" ? "active" : ""}`}
          onClick={() => onNavigate("angles")}
        >
          <span className="nav-icon">🔄</span>
          Angles
        </button>

        <button
          className={`nav-link ${activePage === "conflicts" ? "active" : ""}`}
          onClick={() => onNavigate("conflicts")}
        >
          <span className="nav-icon">⚡</span>
          Conflicts
        </button>

        <div className="nav-section-label">Intelligence</div>
        <button
          className={`nav-link ${activePage === "persona" ? "active" : ""}`}
          onClick={() => onNavigate("persona")}
        >
          <span className="nav-icon">⚖️</span>
          Persona Compare
        </button>

        <button
          className={`nav-link ${activePage === "knowledge" ? "active" : ""}`}
          onClick={() => onNavigate("knowledge")}
        >
          <span className="nav-icon">🧠</span>
          Knowledge Delta
        </button>

        <button
          className={`nav-link ${activePage === "video" ? "active" : ""}`}
          onClick={() => onNavigate("video")}
        >
          <span className="nav-icon">🎬</span>
          Video
        </button>

        <button
          className={`nav-link ${activePage === "storyarc" ? "active" : ""}`}
          onClick={() => onNavigate("storyarc")}
        >
          <span className="nav-icon">📈</span>
          Story Arc
        </button>

        <div className="nav-section-label">System</div>
        <button
          className={`nav-link ${activePage === "audit" ? "active" : ""}`}
          onClick={() => onNavigate("audit")}
        >
          <span className="nav-icon">🔍</span>
          Audit Trail
        </button>

        <button
          className={`nav-link ${activePage === "settings" ? "active" : ""}`}
          onClick={() => onNavigate("settings")}
        >
          <span className="nav-icon">⚙️</span>
          Settings
        </button>
      </div>

      <div className="sidebar-footer">
        <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
          <span className="status-dot"></span>
          11 Agents Online
        </div>
        <div
          style={{
            fontSize: "0.7rem",
            color: "var(--text-muted)",
            marginTop: "0.3rem",
          }}
        >
          LangGraph Orchestrator v2.0
        </div>
      </div>
    </nav>
  );
}
