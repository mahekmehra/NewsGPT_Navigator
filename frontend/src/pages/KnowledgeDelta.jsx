/**
 * KnowledgeDelta — Known vs New chips, changed entities in amber
 * Visualizes what's genuinely new vs already known to the user
 */
export default function KnowledgeDelta({ knowledgeDiff = [] }) {
  const statusConfig = {
    new: { icon: "🆕", color: "#3b82f6", bg: "rgba(59, 130, 246, 0.12)", label: "New" },
    changed: { icon: "🔄", color: "#f59e0b", bg: "rgba(245, 158, 11, 0.12)", label: "Changed" },
    known: { icon: "✅", color: "#10b981", bg: "rgba(16, 185, 129, 0.12)", label: "Known" },
    removed: { icon: "❌", color: "#ef4444", bg: "rgba(239, 68, 68, 0.12)", label: "Removed" },
  };

  if (!knowledgeDiff.length) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1 className="page-title"><span className="title-accent">🧠</span> Knowledge Delta</h1>
          <p className="page-subtitle">Run an analysis with a session ID to track your knowledge</p>
        </div>
        <div className="glass-card" style={{ textAlign: "center", padding: "3rem" }}>
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📚</div>
          <p style={{ color: "var(--text-secondary)" }}>No knowledge data available. Analyze a topic to see what's new vs what you already know.</p>
        </div>
      </div>
    );
  }

  const newItems = knowledgeDiff.filter(d => d.status === "new");
  const changedItems = knowledgeDiff.filter(d => d.status === "changed");
  const knownItems = knowledgeDiff.filter(d => d.status === "known");
  const removedItems = knowledgeDiff.filter(d => d.status === "removed");

  const renderChips = (items, status) => {
    const config = statusConfig[status];
    if (!items.length) return null;
    return (
      <div style={{ marginBottom: "1.5rem" }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "0.5rem",
          marginBottom: "0.75rem",
        }}>
          <span style={{ fontSize: "1.1rem" }}>{config.icon}</span>
          <h3 style={{ margin: 0, color: config.color, fontSize: "1rem" }}>
            {config.label} ({items.length})
          </h3>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
          {items.map((item, idx) => (
            <div key={idx} style={{
              padding: "0.6rem 1rem",
              borderRadius: "0.75rem",
              background: config.bg,
              border: `1px solid ${config.color}30`,
              maxWidth: "300px",
              animation: `fadeIn 0.3s ease ${idx * 0.05}s both`,
            }}>
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: "0.4rem",
                marginBottom: "0.3rem",
              }}>
                <strong style={{ color: config.color, fontSize: "0.85rem" }}>
                  {item.entity}
                </strong>
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", lineHeight: 1.4 }}>
                {item.detail}
              </div>
              {status === "changed" && item.previous_value && (
                <div style={{
                  marginTop: "0.4rem",
                  fontSize: "0.7rem",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.3rem",
                }}>
                  <span style={{ color: "#ef4444", textDecoration: "line-through" }}>{item.previous_value}</span>
                  <span style={{ color: "var(--text-secondary)" }}>→</span>
                  <span style={{ color: "#10b981" }}>{item.current_value}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title"><span className="title-accent">🧠</span> Knowledge Delta</h1>
        <p className="page-subtitle">
          {newItems.length} new · {changedItems.length} changed · {knownItems.length} known · {removedItems.length} removed
        </p>
      </div>

      {/* Summary cards */}
      <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
        {[
          { status: "new", items: newItems },
          { status: "changed", items: changedItems },
          { status: "known", items: knownItems },
          { status: "removed", items: removedItems },
        ].map(({ status, items }) => {
          const config = statusConfig[status];
          return (
            <div key={status} className="glass-card" style={{
              flex: 1,
              minWidth: "120px",
              padding: "0.75rem 1rem",
              borderBottom: `3px solid ${config.color}`,
              textAlign: "center",
            }}>
              <div style={{ fontSize: "1.5rem" }}>{config.icon}</div>
              <div style={{ fontSize: "1.5rem", fontWeight: 700, color: config.color }}>{items.length}</div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>{config.label}</div>
            </div>
          );
        })}
      </div>

      {/* Knowledge chips by category */}
      <div className="glass-card">
        {renderChips(newItems, "new")}
        {renderChips(changedItems, "changed")}
        {renderChips(knownItems, "known")}
        {renderChips(removedItems, "removed")}
      </div>
    </div>
  );
}
