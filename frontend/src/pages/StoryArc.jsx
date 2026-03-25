import { useState } from "react";

export default function StoryArc({ storyArc = [] }) {
  const [filter, setFilter] = useState("all");

  if (!storyArc || storyArc.length === 0) {
    return (
      <div className="glass-card" style={{ textAlign: "center", padding: "3rem" }}>
        <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📈</div>
        <h3>Story Arc Tracker</h3>
        <p style={{ color: "var(--text-secondary)" }}>
          Run the same topic across multiple sessions to see how entity sentiments evolve over time.
        </p>
        <p style={{ color: "var(--text-tertiary)", fontSize: "0.85rem", marginTop: "0.5rem" }}>
          Example: Track "Adani" sentiment shifting from negative to neutral over weeks.
        </p>
      </div>
    );
  }

  const shifts = [...new Set(storyArc.map(e => e.shift))];
  const filteredArc = filter === "all" ? storyArc : storyArc.filter(e => e.shift === filter);

  const sentimentColor = (sentiment) => {
    switch (sentiment) {
      case "positive": return "#10b981";
      case "negative": return "#ef4444";
      case "neutral": return "#6b7280";
      default: return "#8b5cf6";
    }
  };

  const shiftBadge = (shift) => {
    const colors = {
      "new": { bg: "rgba(59, 130, 246, 0.15)", color: "#3b82f6" },
      "stable": { bg: "rgba(107, 114, 128, 0.15)", color: "#6b7280" },
    };
    if (shift.includes("→")) {
      return { bg: "rgba(245, 158, 11, 0.15)", color: "#f59e0b" };
    }
    return colors[shift] || { bg: "rgba(139, 92, 246, 0.15)", color: "#8b5cf6" };
  };

  return (
    <div>
      <div style={{ textAlign: "center", marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.8rem", fontWeight: 800, marginBottom: "0.5rem" }}>
          <span style={{ background: "var(--gradient-hero)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            📈 Story Arc Tracker
          </span>
        </h2>
        <p style={{ color: "var(--text-secondary)" }}>
          How entity sentiments evolve across analysis sessions
        </p>
      </div>

      {/* Filter chips */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem", flexWrap: "wrap", justifyContent: "center" }}>
        <button
          className={`btn ${filter === "all" ? "btn-primary" : "btn-outline"}`}
          onClick={() => setFilter("all")}
          style={{ fontSize: "0.85rem", padding: "0.4rem 1rem" }}
        >
          All ({storyArc.length})
        </button>
        {shifts.map(s => (
          <button
            key={s}
            className={`btn ${filter === s ? "btn-primary" : "btn-outline"}`}
            onClick={() => setFilter(s)}
            style={{ fontSize: "0.85rem", padding: "0.4rem 1rem" }}
          >
            {s} ({storyArc.filter(e => e.shift === s).length})
          </button>
        ))}
      </div>

      {/* Arc cards */}
      <div style={{ display: "grid", gap: "1rem", gridTemplateColumns: "repeat(auto-fill, minmax(350px, 1fr))" }}>
        {filteredArc.map((arc, i) => {
          const badge = shiftBadge(arc.shift);
          return (
            <div key={i} className="glass-card" style={{ padding: "1.5rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                <div>
                  <h4 style={{ margin: 0, fontSize: "1.1rem" }}>{arc.entity}</h4>
                  <span style={{ color: "var(--text-tertiary)", fontSize: "0.8rem" }}>{arc.entity_type}</span>
                </div>
                <span style={{
                  background: badge.bg,
                  color: badge.color,
                  padding: "0.25rem 0.75rem",
                  borderRadius: "20px",
                  fontSize: "0.8rem",
                  fontWeight: 600,
                }}>
                  {arc.shift}
                </span>
              </div>

              {/* Trend visualization */}
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
                {(arc.trend || []).map((point, j) => (
                  <div key={j} style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
                    {j > 0 && <span style={{ color: "var(--text-tertiary)" }}>→</span>}
                    <div style={{
                      background: `${sentimentColor(point.sentiment)}20`,
                      border: `1px solid ${sentimentColor(point.sentiment)}40`,
                      borderRadius: "8px",
                      padding: "0.35rem 0.6rem",
                      fontSize: "0.8rem",
                    }}>
                      <span style={{ color: sentimentColor(point.sentiment), fontWeight: 600 }}>
                        {point.sentiment}
                      </span>
                      <span style={{ color: "var(--text-tertiary)", marginLeft: "0.3rem" }}>
                        ({point.score})
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Timestamps */}
              <div style={{ marginTop: "0.75rem", fontSize: "0.75rem", color: "var(--text-tertiary)" }}>
                First seen: {arc.first_seen ? new Date(arc.first_seen).toLocaleDateString() : "N/A"} |
                Updated: {arc.latest_update ? new Date(arc.latest_update).toLocaleDateString() : "N/A"}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
