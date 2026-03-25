import AuditTrail from "../components/AuditTrail";

export default function AuditPage({ auditTrail }) {
  return (
    <div>
      <div className="page-header">
        <h2>🔍 Audit Trail</h2>
        <p>
          Full provenance log — every agent action with timestamps, inputs, and outputs.
          {auditTrail && auditTrail.length > 0 && (
            <span style={{ marginLeft: "0.5rem", color: "var(--accent-primary)" }}>
              {auditTrail.length} entries
            </span>
          )}
        </p>
      </div>

      <AuditTrail auditTrail={auditTrail} />
    </div>
  );
}
