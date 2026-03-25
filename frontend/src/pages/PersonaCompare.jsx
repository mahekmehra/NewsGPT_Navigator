import { useState } from "react";

/**
 * PersonaCompare — Side-by-side CFO vs First-Gen Investor split screen
 */
export default function PersonaCompare({ result = null }) {
  const [leftPersona] = useState("CFO");
  const [rightPersona] = useState("FirstGen");

  const briefing = result?.briefing || {};
  const entitySentiments = result?.entity_sentiments || [];
  const emotionalRegister = result?.emotional_register || {};
  const userProfile = result?.user_profile || {};

  const personaConfig = {
    CFO: {
      icon: "👔",
      label: "Chief Financial Officer",
      color: "#3b82f6",
      focus: ["P&L impact", "Regulatory changes", "Risk exposure", "Tax implications"],
      tone: "Formal, data-driven, actionable",
      depth: "Detailed with metrics",
    },
    FirstGen: {
      icon: "🌱",
      label: "First-Gen Investor",
      color: "#10b981",
      focus: ["Personal savings impact", "Simple explanations", "Should I buy/sell?", "FD rates"],
      tone: "Friendly, Hindi-English mix, analogies",
      depth: "Brief with real-world examples",
    },
  };

  const renderPersonaCard = (personaKey, side) => {
    const config = personaConfig[personaKey];
    return (
      <div className="glass-card" style={{
        flex: 1,
        borderTop: `3px solid ${config.color}`,
        minWidth: 0,
      }}>
        {/* Persona header */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "0.75rem",
          marginBottom: "1.25rem",
          paddingBottom: "1rem",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
        }}>
          <span style={{ fontSize: "2rem" }}>{config.icon}</span>
          <div>
            <h3 style={{ margin: 0, color: config.color }}>{config.label}</h3>
            <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>{config.tone}</span>
          </div>
        </div>

        {/* Focus areas */}
        <div style={{ marginBottom: "1.25rem" }}>
          <h4 style={{ fontSize: "0.8rem", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "0.5rem" }}>
            Focus Areas
          </h4>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
            {config.focus.map((f, i) => (
              <span key={i} style={{
                padding: "0.3rem 0.75rem",
                borderRadius: "1rem",
                background: `${config.color}18`,
                border: `1px solid ${config.color}40`,
                color: config.color,
                fontSize: "0.75rem",
                fontWeight: 500,
              }}>
                {f}
              </span>
            ))}
          </div>
        </div>

        {/* Briefing content adapted to persona */}
        <div style={{ marginBottom: "1.25rem" }}>
          <h4 style={{ fontSize: "0.8rem", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "0.5rem" }}>
            Briefing ({config.depth})
          </h4>
          <div style={{
            padding: "1rem",
            borderRadius: "0.75rem",
            background: "rgba(255,255,255,0.03)",
            fontSize: "0.85rem",
            lineHeight: 1.7,
            color: "var(--text-primary)",
            maxHeight: "200px",
            overflowY: "auto",
          }}>
            {personaKey === "CFO" ? (
              briefing.summary ? (
                <div>
                  <p><strong>Executive Summary:</strong> {briefing.summary}</p>
                  {briefing.prediction && <p><strong>Forward Outlook:</strong> {briefing.prediction}</p>}
                </div>
              ) : "Run analysis to see CFO-tailored briefing."
            ) : (
              briefing.summary ? (
                <div>
                  <p><strong>सरल भाषा में:</strong> {briefing.summary}</p>
                  {briefing.prediction && <p><strong>आगे क्या?</strong> {briefing.prediction}</p>}
                </div>
              ) : "Run analysis to see beginner-friendly briefing."
            )}
          </div>
        </div>

        {/* Key entities for this persona */}
        <div>
          <h4 style={{ fontSize: "0.8rem", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "0.5rem" }}>
            Key Entities
          </h4>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.3rem" }}>
            {(entitySentiments.length > 0 ? entitySentiments.slice(0, personaKey === "CFO" ? 8 : 5) : []).map((ent, i) => (
              <span key={i} style={{
                padding: "0.25rem 0.6rem",
                borderRadius: "0.5rem",
                background: ent.sentiment === "positive" ? "rgba(16,185,129,0.15)" : ent.sentiment === "negative" ? "rgba(239,68,68,0.15)" : "rgba(148,163,184,0.15)",
                color: ent.sentiment === "positive" ? "#10b981" : ent.sentiment === "negative" ? "#ef4444" : "#94a3b8",
                fontSize: "0.75rem",
              }}>
                {ent.entity}
              </span>
            ))}
            {entitySentiments.length === 0 && (
              <span style={{ color: "var(--text-secondary)", fontSize: "0.8rem" }}>No entities yet</span>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title"><span className="title-accent">⚖️</span> Persona Compare</h1>
        <p className="page-subtitle">Side-by-side view of how different personas receive the same news</p>
      </div>

      {/* Emotional register banner */}
      {emotionalRegister.register && (
        <div className="glass-card" style={{
          padding: "0.75rem 1.25rem",
          marginBottom: "1.5rem",
          display: "flex",
          alignItems: "center",
          gap: "0.75rem",
          borderLeft: `3px solid ${
            emotionalRegister.register === "crisis" ? "#ef4444" :
            emotionalRegister.register === "opportunity" ? "#10b981" :
            emotionalRegister.register === "uncertainty" ? "#f59e0b" : "#94a3b8"
          }`,
        }}>
          <span style={{ fontSize: "1.2rem" }}>
            {emotionalRegister.register === "crisis" ? "🚨" :
             emotionalRegister.register === "opportunity" ? "🚀" :
             emotionalRegister.register === "uncertainty" ? "⚠️" : "📰"}
          </span>
          <div>
            <strong style={{ color: "var(--text-primary)" }}>
              Emotional Register: {emotionalRegister.register?.toUpperCase()}
            </strong>
            <span style={{ marginLeft: "0.5rem", fontSize: "0.8rem", color: "var(--text-secondary)" }}>
              Intensity: {((emotionalRegister.intensity || 0) * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      )}

      {/* Split screen */}
      <div style={{
        display: "flex",
        gap: "1.5rem",
        alignItems: "flex-start",
      }}>
        {renderPersonaCard(leftPersona, "left")}
        
        {/* Divider */}
        <div style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "200px",
          gap: "0.5rem",
        }}>
          <div style={{ width: "2px", height: "80px", background: "linear-gradient(to bottom, transparent, rgba(255,255,255,0.2), transparent)" }} />
          <span style={{ fontSize: "1.2rem", color: "var(--text-secondary)" }}>VS</span>
          <div style={{ width: "2px", height: "80px", background: "linear-gradient(to bottom, transparent, rgba(255,255,255,0.2), transparent)" }} />
        </div>

        {renderPersonaCard(rightPersona, "right")}
      </div>
    </div>
  );
}
