export default function BiasIndicator({ biasScore, complianceStatus }) {
  const level = biasScore <= 0.3 ? "low" : biasScore <= 0.6 ? "medium" : "high";
  const percentage = Math.round(biasScore * 100);

  return (
    <div className="glass-card">
      <div className="card-header">
        <h3>🛡️ Compliance & Bias</h3>
        <span className={`compliance-badge ${complianceStatus === "passed" ? "passed" : "failed"}`}>
          {complianceStatus === "passed" ? "✓ Passed" : "✗ Failed"}
        </span>
      </div>

      <div className="bias-indicator">
        <span style={{ fontSize: "0.82rem", color: "var(--text-secondary)", minWidth: "4rem" }}>
          Bias Score
        </span>
        <div className="bias-meter">
          <div
            className={`bias-fill ${level}`}
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
        <span className={`bias-score ${level}`}>
          {biasScore.toFixed(2)}
        </span>
      </div>

      <div style={{ padding: "0 1rem 0.5rem", fontSize: "0.78rem", color: "var(--text-muted)" }}>
        {level === "low" && "✅ Content is well-balanced and factual."}
        {level === "medium" && "⚠️ Some potential bias detected. Review recommended."}
        {level === "high" && "🚨 Significant bias detected. Content may need revision."}
      </div>
    </div>
  );
}
