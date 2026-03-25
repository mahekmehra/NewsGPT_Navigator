export default function BriefingCard({ briefing }) {
  if (!briefing) return null;

  return (
    <div className="glass-card briefing-card">
      <div className="card-header">
        <h3>📰 {briefing.title || "Intelligence Briefing"}</h3>
      </div>

      <div className="briefing-content">
        {briefing.detailed_briefing || briefing.summary || "No briefing available."}
      </div>

      {briefing.translated_summary && (
        <div className="translated-section">
          <h4>🌐 Translated Summary ({briefing.language})</h4>
          <p>{briefing.translated_summary}</p>
        </div>
      )}

      <div className="briefing-meta">
        {briefing.model_used && (
          <span className="meta-tag model">🤖 {briefing.model_used}</span>
        )}
        {briefing.sentiment && (
          <span className="meta-tag sentiment">
            {briefing.sentiment === "positive" ? "😊" : briefing.sentiment === "negative" ? "😟" : "😐"}{" "}
            {briefing.sentiment}
          </span>
        )}
        {briefing.persona && (
          <span className="meta-tag persona">👤 {briefing.persona}</span>
        )}
        {briefing.complexity_class && (
          <span className="meta-tag complexity">⚡ {briefing.complexity_class}</span>
        )}
      </div>
    </div>
  );
}
