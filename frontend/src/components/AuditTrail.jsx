import { useState } from "react";

export default function AuditTrail({ auditTrail }) {
  const [expandedIdx, setExpandedIdx] = useState(null);

  if (!auditTrail || auditTrail.length === 0) {
    return (
      <div className="glass-card">
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <div className="empty-title">No Audit Trail Yet</div>
          <div className="empty-text">
            Run an analysis to see the full provenance log of every agent action.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="audit-list">
      {auditTrail.map((entry, idx) => (
        <div
          key={idx}
          className="audit-entry"
          onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
        >
          <div className="audit-header">
            <span className={`audit-agent-badge ${entry.agent || ""}`}>
              {entry.agent || "unknown"}
            </span>
            <span className="audit-action">{entry.action || ""}</span>
            <span className="audit-time">
              {entry.timestamp
                ? new Date(entry.timestamp).toLocaleTimeString()
                : ""}
            </span>
          </div>

          {expandedIdx === idx && (
            <div className="audit-details">
              <div style={{ marginBottom: "0.5rem" }}>
                <strong>Inputs:</strong>
                {"\n"}
                {JSON.stringify(entry.inputs || {}, null, 2)}
              </div>
              <div>
                <strong>Outputs:</strong>
                {"\n"}
                {JSON.stringify(entry.outputs || {}, null, 2)}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
