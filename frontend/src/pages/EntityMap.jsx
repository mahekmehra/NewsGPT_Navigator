import { useState } from "react";

/**
 * EntityMap — Entity chips with sentiment colour coding
 * Green = positive, Red = negative, Grey = neutral
 * Click to expand and see article mentions
 */
export default function EntityMap({ entitySentiments = [] }) {
  const [expandedEntity, setExpandedEntity] = useState(null);

  const sentimentColor = (sentiment) => {
    switch (sentiment) {
      case "positive": return { bg: "rgba(16, 185, 129, 0.15)", border: "#10b981", text: "#10b981", glow: "0 0 12px rgba(16, 185, 129, 0.3)" };
      case "negative": return { bg: "rgba(239, 68, 68, 0.15)", border: "#ef4444", text: "#ef4444", glow: "0 0 12px rgba(239, 68, 68, 0.3)" };
      default: return { bg: "rgba(148, 163, 184, 0.15)", border: "#94a3b8", text: "#94a3b8", glow: "0 0 12px rgba(148, 163, 184, 0.2)" };
    }
  };

  const typeIcon = (type) => {
    const icons = { PERSON: "👤", ORG: "🏢", GPE: "🌍", PRODUCT: "📦", EVENT: "📅", POLICY: "📜", METRIC: "📊" };
    return icons[type] || "🔹";
  };

  if (!entitySentiments.length) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1 className="page-title"><span className="title-accent">🔬</span> Entity Map</h1>
          <p className="page-subtitle">Run an analysis to see entity sentiment mapping</p>
        </div>
        <div className="glass-card" style={{ textAlign: "center", padding: "3rem" }}>
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🧬</div>
          <p style={{ color: "var(--text-secondary)" }}>No entity data available yet. Analyze a topic to see entity sentiment mapping.</p>
        </div>
      </div>
    );
  }

  const positive = entitySentiments.filter(e => e.sentiment === "positive");
  const negative = entitySentiments.filter(e => e.sentiment === "negative");
  const neutral = entitySentiments.filter(e => e.sentiment === "neutral");

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title"><span className="title-accent">🔬</span> Entity Map</h1>
        <p className="page-subtitle">{entitySentiments.length} entities extracted with sentiment analysis</p>
      </div>

      {/* Summary stats */}
      <div className="entity-stats">
        <div className="glass-card entity-stat-card" style={{ borderLeft: "3px solid #10b981" }}>
          <div className="stat-number" style={{ color: "#10b981" }}>{positive.length}</div>
          <div className="stat-label">Positive</div>
        </div>
        <div className="glass-card entity-stat-card" style={{ borderLeft: "3px solid #ef4444" }}>
          <div className="stat-number" style={{ color: "#ef4444" }}>{negative.length}</div>
          <div className="stat-label">Negative</div>
        </div>
        <div className="glass-card entity-stat-card" style={{ borderLeft: "3px solid #94a3b8" }}>
          <div className="stat-number" style={{ color: "#94a3b8" }}>{neutral.length}</div>
          <div className="stat-label">Neutral</div>
        </div>
      </div>

      {/* Entity chips */}
      <div className="glass-card">
        <h3 style={{ marginBottom: "1rem", color: "var(--text-primary)" }}>All Entities</h3>
        <div className="entity-chips-container">
          {entitySentiments.map((entity, idx) => {
            const colors = sentimentColor(entity.sentiment);
            const isExpanded = expandedEntity === idx;
            return (
              <div key={idx}>
                <button
                  className="entity-chip"
                  onClick={() => setExpandedEntity(isExpanded ? null : idx)}
                  style={{
                    background: colors.bg,
                    border: `1px solid ${colors.border}`,
                    color: colors.text,
                    boxShadow: isExpanded ? colors.glow : "none",
                    cursor: "pointer",
                    padding: "0.5rem 1rem",
                    borderRadius: "2rem",
                    fontSize: "0.85rem",
                    fontWeight: 500,
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "0.4rem",
                    transition: "all 0.2s ease",
                    margin: "0.25rem",
                  }}
                >
                  <span>{typeIcon(entity.entity_type)}</span>
                  <span>{entity.entity}</span>
                  <span style={{ opacity: 0.7, fontSize: "0.75rem" }}>
                    ({(entity.score * 100).toFixed(0)}%)
                  </span>
                </button>
                {isExpanded && (
                  <div className="entity-detail-card glass-card" style={{
                    marginTop: "0.5rem",
                    marginBottom: "0.5rem",
                    padding: "1rem",
                    borderLeft: `3px solid ${colors.border}`,
                    animation: "fadeIn 0.3s ease",
                  }}>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem", fontSize: "0.85rem" }}>
                      <div><strong>Type:</strong> {entity.entity_type}</div>
                      <div><strong>Sentiment:</strong> {entity.sentiment}</div>
                      <div><strong>Confidence:</strong> {(entity.score * 100).toFixed(1)}%</div>
                      <div><strong>Mentions:</strong> {entity.mentions} article(s)</div>
                    </div>
                    {entity.articles && entity.articles.length > 0 && (
                      <div style={{ marginTop: "0.5rem", fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                        Found in articles: {entity.articles.join(", ")}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
