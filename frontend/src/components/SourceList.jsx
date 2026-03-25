export default function SourceList({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="glass-card">
      <div className="card-header">
        <h3>📚 Sources ({sources.length})</h3>
      </div>
      <div className="source-list">
        {sources.map((source, idx) => (
          <div key={idx} className="source-item">
            <div className="source-icon">📄</div>
            <div className="source-info">
              <div className="source-title">{source.title || "Untitled"}</div>
              <div className="source-domain">{source.source || "Unknown"}</div>
            </div>
            {source.url && (
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="source-link"
              >
                Open ↗
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
