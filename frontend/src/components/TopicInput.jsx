import { useState } from "react";

export default function TopicInput({ onAnalyze, isLoading }) {
  const [topic, setTopic] = useState("");
  const [persona, setPersona] = useState("General");
  const [customPersona, setCustomPersona] = useState("");
  const [language, setLanguage] = useState("en");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (topic.trim() && !isLoading) {
      onAnalyze(topic.trim(), persona, language, persona === "Custom" ? customPersona : "");
    }
  };

  return (
    <div className="topic-input-section">
      <div style={{ textAlign: "center", marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "2rem", fontWeight: 800, marginBottom: "0.5rem" }}>
          <span style={{ background: "var(--gradient-hero)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>
            Intelligent News Analysis
          </span>
        </h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "1rem" }}>
          Enter any topic. Eleven AI agents will fetch, analyze, verify, and deliver your briefing.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="topic-input-wrapper">
          <input
            id="topic-input"
            type="text"
            className="topic-input"
            placeholder="e.g. AI regulation, climate change, semiconductor industry..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={isLoading}
          />
          <span className="input-icon">🔍</span>
        </div>

        <div className="select-row">
          <div className="select-group">
            <label htmlFor="persona-select">Persona</label>
            <select
              id="persona-select"
              className="select-input"
              value={persona}
              onChange={(e) => setPersona(e.target.value)}
              disabled={isLoading}
            >
              <option value="General">General</option>
              <option value="Student">Student</option>
              <option value="Investor">Investor</option>
              <option value="Beginner">Beginner</option>
              <option value="CFO">CFO</option>
              <option value="FirstGen">First-Gen Investor</option>
              <option value="Custom">Custom…</option>
            </select>
          </div>

          {persona === "Custom" && (
            <div className="select-group" style={{ flex: 2 }}>
              <label htmlFor="custom-persona-input">Describe Your Persona</label>
              <input
                id="custom-persona-input"
                type="text"
                className="select-input"
                placeholder="e.g. Startup founder, Journalist, Policy analyst..."
                value={customPersona}
                onChange={(e) => setCustomPersona(e.target.value)}
                disabled={isLoading}
                style={{ padding: "0.6rem 0.8rem" }}
              />
            </div>
          )}

          <div className="select-group">
            <label htmlFor="language-select">Language</label>
            <select
              id="language-select"
              className="select-input"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              disabled={isLoading}
            >
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="ta">Tamil</option>
              <option value="bn">Bengali</option>
              <option value="te">Telugu</option>
              <option value="kn">Kannada</option>
              <option value="mr">Marathi</option>
              <option value="pa">Punjabi</option>
            </select>
          </div>
        </div>

        <button
          id="analyze-btn"
          type="submit"
          className="btn btn-primary btn-full"
          disabled={!topic.trim() || isLoading}
        >
          {isLoading ? (
            <>
              <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }}></span>
              Pipeline Running...
            </>
          ) : (
            <>🚀 Analyze Topic</>
          )}
        </button>
      </form>

      {/* Feature Cards */}
      <div className="feature-grid">
        <div className="glass-card feature-card">
          <div className="feature-icon">🤖</div>
          <h4>11 AI Agents</h4>
          <p>Fetch, analyze, rank, verify, detect conflicts, and deliver</p>
        </div>
        <div className="glass-card feature-card">
          <div className="feature-icon">📈</div>
          <h4>Story Arc Tracker</h4>
          <p>Track entity sentiment evolution across analysis sessions</p>
        </div>
        <div className="glass-card feature-card">
          <div className="feature-icon">🛡️</div>
          <h4>Compliance</h4>
          <p>Built-in bias detection & content guardrails</p>
        </div>
        <div className="glass-card feature-card">
          <div className="feature-icon">🎬</div>
          <h4>Multilingual Video</h4>
          <p>Auto-generated news video in Hindi, Tamil, Telugu & Bengali</p>
        </div>
      </div>
    </div>
  );
}
