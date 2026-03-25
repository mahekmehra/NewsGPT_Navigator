export default function Timeline({ events }) {
  if (!events || events.length === 0) return null;

  return (
    <div className="glass-card">
      <div className="card-header">
        <h3>📅 Event Timeline</h3>
      </div>
      <div className="timeline">
        {events.map((event, idx) => (
          <div key={idx} className="timeline-item">
            <div className="timeline-date">{event.date || "N/A"}</div>
            <div className="timeline-event">{event.event || ""}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
