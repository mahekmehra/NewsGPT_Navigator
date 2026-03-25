/**
 * ConflictMap — Narrative conflicts visualized with ≠ connectors
 * Cards for factual / interpretive / predictive conflicts
 */
export default function ConflictMap({ conflicts = [] }) {
  const typeConfig = {
    factual: { icon: "📊", color: "#ef4444", label: "Factual Conflict", desc: "Different numbers, dates, or stated facts" },
    interpretive: { icon: "🔍", color: "#f59e0b", label: "Interpretive Conflict", desc: "Different framings of the same event" },
    predictive: { icon: "🔮", color: "#8b5cf6", label: "Predictive Conflict", desc: "Different forecasts about outcomes" },
  };

  const severityBadge = (severity) => {
    const colors = { high: "#ef4444", medium: "#f59e0b", low: "#94a3b8" };
    return (
      <span style={{
        padding: "0.15rem 0.5rem",
        borderRadius: "1rem",
        background: `${colors[severity] || colors.medium}22`,
        color: colors[severity] || colors.medium,
        fontSize: "0.7rem",
        fontWeight: 600,
        textTransform: "uppercase",
        letterSpacing: "0.3px",
      }}>
        {severity}
      </span>
    );
  };

  if (!conflicts.length) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1 className="page-title"><span className="title-accent">⚡</span> Conflict Map</h1>
          <p className="page-subtitle">Run an analysis to detect narrative conflicts</p>
        </div>
        <div className="glass-card" style={{ textAlign: "center", padding: "3rem" }}>
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🤝</div>
          <p style={{ color: "var(--text-secondary)" }}>No conflicts detected. Analyze a topic with multiple sources to find disagreements.</p>
        </div>
      </div>
    );
  }

  const factual = conflicts.filter(c => c.conflict_type === "factual");
  const interpretive = conflicts.filter(c => c.conflict_type === "interpretive");
  const predictive = conflicts.filter(c => c.conflict_type === "predictive");

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title"><span className="title-accent">⚡</span> Conflict Map</h1>
        <p className="page-subtitle">{conflicts.length} narrative conflicts detected across sources</p>
      </div>

      {/* Summary bar */}
      <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
        {[
          { type: "factual", count: factual.length },
          { type: "interpretive", count: interpretive.length },
          { type: "predictive", count: predictive.length },
        ].map(({ type, count }) => {
          const config = typeConfig[type];
          return (
            <div key={type} className="glass-card" style={{
              flex: 1,
              minWidth: "150px",
              padding: "0.75rem 1rem",
              borderLeft: `3px solid ${config.color}`,
              display: "flex",
              alignItems: "center",
              gap: "0.75rem",
            }}>
              <span style={{ fontSize: "1.5rem" }}>{config.icon}</span>
              <div>
                <div style={{ fontSize: "1.25rem", fontWeight: 700, color: config.color }}>{count}</div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>{config.label}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Conflict cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {conflicts.map((conflict, idx) => {
          const config = typeConfig[conflict.conflict_type] || typeConfig.interpretive;
          return (
            <div key={idx} className="glass-card" style={{
              borderLeft: `3px solid ${config.color}`,
              animation: `fadeIn 0.3s ease ${idx * 0.1}s both`,
            }}>
              {/* Header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <span>{config.icon}</span>
                  <strong style={{ color: config.color }}>{config.label}</strong>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  {conflicttag(conflict.entity)}
                  {severityBadge(conflict.severity)}
                </div>
              </div>

              {/* Conflict visualization with ≠ connector */}
              <div style={{
                display: "flex",
                alignItems: "stretch",
                gap: "0",
                margin: "0.5rem 0",
              }}>
                {/* Claim A */}
                <div style={{
                  flex: 1,
                  padding: "1rem",
                  borderRadius: "0.75rem 0 0 0.75rem",
                  background: "rgba(59, 130, 246, 0.08)",
                  borderRight: "none",
                }}>
                  <div style={{ fontSize: "0.7rem", color: "#3b82f6", fontWeight: 600, marginBottom: "0.4rem", textTransform: "uppercase" }}>
                    {conflict.source_a}
                  </div>
                  <div style={{ fontSize: "0.85rem", color: "var(--text-primary)", lineHeight: 1.5 }}>
                    "{conflict.claim_a}"
                  </div>
                </div>

                {/* ≠ connector */}
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: "0 0.75rem",
                  background: `${config.color}15`,
                  borderTop: `1px solid ${config.color}30`,
                  borderBottom: `1px solid ${config.color}30`,
                }}>
                  <span style={{
                    fontSize: "1.5rem",
                    fontWeight: 800,
                    color: config.color,
                    textShadow: `0 0 10px ${config.color}50`,
                  }}>≠</span>
                </div>

                {/* Claim B */}
                <div style={{
                  flex: 1,
                  padding: "1rem",
                  borderRadius: "0 0.75rem 0.75rem 0",
                  background: "rgba(239, 68, 68, 0.08)",
                  borderLeft: "none",
                }}>
                  <div style={{ fontSize: "0.7rem", color: "#ef4444", fontWeight: 600, marginBottom: "0.4rem", textTransform: "uppercase" }}>
                    {conflict.source_b}
                  </div>
                  <div style={{ fontSize: "0.85rem", color: "var(--text-primary)", lineHeight: 1.5 }}>
                    "{conflict.claim_b}"
                  </div>
                </div>
              </div>

              {/* Explanation */}
              {conflict.explanation && (
                <div style={{
                  marginTop: "0.75rem",
                  padding: "0.75rem",
                  borderRadius: "0.5rem",
                  background: "rgba(255,255,255,0.03)",
                  fontSize: "0.8rem",
                  color: "var(--text-secondary)",
                  lineHeight: 1.5,
                }}>
                  💡 {conflict.explanation}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function conflicttag(entity) {
  if (!entity) return null;
  return (
    <span style={{
      padding: "0.2rem 0.6rem",
      borderRadius: "0.4rem",
      background: "rgba(255,255,255,0.08)",
      fontSize: "0.75rem",
      color: "var(--text-primary)",
      fontWeight: 500,
    }}>
      {entity}
    </span>
  );
}
