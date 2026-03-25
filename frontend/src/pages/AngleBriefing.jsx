import { useState } from "react";

/**
 * AngleBriefing — 5 angle tabs, per-angle briefing, angle-aware chat
 */
export default function AngleBriefing({ angleClusters = [], articles = [] }) {
  const [activeAngle, setActiveAngle] = useState(0);

  const angleIcons = ["📊", "📈", "🔍", "🌐", "⚖️"];
  const angleColors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444"];

  if (!angleClusters.length) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1 className="page-title"><span className="title-accent">🔄</span> Angle Briefing</h1>
          <p className="page-subtitle">Run an analysis to see multi-angle coverage</p>
        </div>
        <div className="glass-card" style={{ textAlign: "center", padding: "3rem" }}>
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📐</div>
          <p style={{ color: "var(--text-secondary)" }}>No angle data available. Analyze a topic to see narrative angle clustering.</p>
        </div>
      </div>
    );
  }

  const activeCluster = angleClusters[activeAngle] || {};

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title"><span className="title-accent">🔄</span> Angle Briefing</h1>
        <p className="page-subtitle">{angleClusters.length} narrative angles identified</p>
      </div>

      {/* Angle tabs */}
      <div className="angle-tabs" style={{
        display: "flex",
        gap: "0.5rem",
        marginBottom: "1.5rem",
        overflowX: "auto",
        paddingBottom: "0.5rem",
      }}>
        {angleClusters.map((angle, idx) => (
          <button
            key={idx}
            onClick={() => setActiveAngle(idx)}
            className={`angle-tab ${activeAngle === idx ? "active" : ""}`}
            style={{
              padding: "0.75rem 1.25rem",
              borderRadius: "0.75rem",
              border: activeAngle === idx ? `2px solid ${angleColors[idx % angleColors.length]}` : "1px solid rgba(255,255,255,0.1)",
              background: activeAngle === idx ? `${angleColors[idx % angleColors.length]}22` : "rgba(255,255,255,0.04)",
              color: activeAngle === idx ? angleColors[idx % angleColors.length] : "var(--text-secondary)",
              cursor: "pointer",
              fontWeight: activeAngle === idx ? 600 : 400,
              fontSize: "0.85rem",
              transition: "all 0.25s ease",
              whiteSpace: "nowrap",
              display: "flex",
              alignItems: "center",
              gap: "0.4rem",
            }}
          >
            <span>{angleIcons[idx % angleIcons.length]}</span>
            <span>{angle.label}</span>
            <span style={{
              background: activeAngle === idx ? angleColors[idx % angleColors.length] : "rgba(255,255,255,0.1)",
              color: activeAngle === idx ? "#fff" : "var(--text-secondary)",
              padding: "0.1rem 0.5rem",
              borderRadius: "1rem",
              fontSize: "0.7rem",
              fontWeight: 600,
            }}>
              {angle.article_count}
            </span>
          </button>
        ))}
      </div>

      {/* Active angle briefing */}
      <div className="glass-card" style={{
        borderTop: `3px solid ${angleColors[activeAngle % angleColors.length]}`,
        animation: "fadeIn 0.3s ease",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "1rem" }}>
          <span style={{ fontSize: "1.5rem" }}>{angleIcons[activeAngle % angleIcons.length]}</span>
          <div>
            <h2 style={{ margin: 0, color: "var(--text-primary)", fontSize: "1.2rem" }}>
              {activeCluster.label}
            </h2>
            <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
              {activeCluster.article_count} articles in this angle
            </span>
          </div>
        </div>

        <div style={{
          padding: "1rem",
          borderRadius: "0.75rem",
          background: "rgba(255,255,255,0.03)",
          lineHeight: 1.7,
          color: "var(--text-primary)",
          fontSize: "0.95rem",
        }}>
          {activeCluster.summary || "No summary available for this angle."}
        </div>

        {/* Articles in this angle */}
        {activeCluster.article_ids && activeCluster.article_ids.length > 0 && (
          <div style={{ marginTop: "1.5rem" }}>
            <h4 style={{ marginBottom: "0.75rem", color: "var(--text-secondary)", fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.5px" }}>
              Articles in this angle
            </h4>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {activeCluster.article_ids.map((artIdx) => {
                const article = articles[artIdx];
                if (!article) return null;
                return (
                  <div key={artIdx} style={{
                    padding: "0.75rem 1rem",
                    borderRadius: "0.5rem",
                    background: "rgba(255,255,255,0.04)",
                    borderLeft: `3px solid ${angleColors[activeAngle % angleColors.length]}`,
                    fontSize: "0.85rem",
                  }}>
                    <div style={{ fontWeight: 500, color: "var(--text-primary)" }}>
                      {article.title || `Article ${artIdx + 1}`}
                    </div>
                    <div style={{ color: "var(--text-secondary)", marginTop: "0.25rem", fontSize: "0.8rem" }}>
                      {article.source || "Unknown source"}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
