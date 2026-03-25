import { useState } from "react";
import BriefingCard from "../components/BriefingCard";
import Timeline from "../components/Timeline";
import SourceList from "../components/SourceList";
import BiasIndicator from "../components/BiasIndicator";

export default function Results({ result }) {
  const [activeTab, setActiveTab] = useState("briefing");

  if (!result || !result.briefing) {
    return (
      <div>
        <div className="page-header">
          <h2>📊 Analysis Results</h2>
          <p>Run an analysis from the dashboard to see results here.</p>
        </div>
        <div className="glass-card">
          <div className="empty-state">
            <div className="empty-icon">📊</div>
            <div className="empty-title">No Results Yet</div>
            <div className="empty-text">
              Go to the Dashboard, enter a topic, and let the 5-agent pipeline generate your briefing.
            </div>
          </div>
        </div>
      </div>
    );
  }

  const briefing = result.briefing;

  return (
    <div>
      <div className="page-header">
        <h2>📊 Analysis Results</h2>
        <p>
          {briefing.title || "Intelligence Briefing"} • Generated{" "}
          {briefing.generated_at ? new Date(briefing.generated_at).toLocaleString() : "recently"}
        </p>
      </div>

      {/* Stats Row */}
      <div className="stat-row">
        <div className="glass-card stat-card">
          <div className="stat-value">{result.articles_fetched || 0}</div>
          <div className="stat-label">Articles Fetched</div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-value">{result.articles_verified || 0}</div>
          <div className="stat-label">Verified</div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-value">{briefing.bias_score?.toFixed(2) || "0.00"}</div>
          <div className="stat-label">Bias Score</div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-value">{result.audit_trail?.length || 0}</div>
          <div className="stat-label">Agent Actions</div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-nav">
        <button
          className={`tab-btn ${activeTab === "briefing" ? "active" : ""}`}
          onClick={() => setActiveTab("briefing")}
        >
          Briefing
        </button>
        <button
          className={`tab-btn ${activeTab === "timeline" ? "active" : ""}`}
          onClick={() => setActiveTab("timeline")}
        >
          Timeline
        </button>
        <button
          className={`tab-btn ${activeTab === "sources" ? "active" : ""}`}
          onClick={() => setActiveTab("sources")}
        >
          Sources
        </button>
        <button
          className={`tab-btn ${activeTab === "compliance" ? "active" : ""}`}
          onClick={() => setActiveTab("compliance")}
        >
          Compliance
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === "briefing" && (
        <div>
          <BriefingCard briefing={briefing} />

          {/* Key Entities */}
          {briefing.key_entities && briefing.key_entities.length > 0 && (
            <div className="glass-card" style={{ marginTop: "1rem" }}>
              <div className="card-header">
                <h3>🏷️ Key Entities</h3>
              </div>
              <div className="entity-tags">
                {briefing.key_entities.map((entity, idx) => (
                  <span key={idx} className="entity-tag">{entity}</span>
                ))}
              </div>
            </div>
          )}

          {/* Prediction */}
          {briefing.prediction && (
            <div className="prediction-box" style={{ marginTop: "1rem" }}>
              <h4>🔮 What Next?</h4>
              <p>{briefing.prediction}</p>
            </div>
          )}
        </div>
      )}

      {activeTab === "timeline" && (
        <Timeline events={briefing.timeline} />
      )}

      {activeTab === "sources" && (
        <SourceList sources={briefing.sources} />
      )}

      {activeTab === "compliance" && (
        <BiasIndicator
          biasScore={briefing.bias_score || 0}
          complianceStatus={briefing.compliance_status || "unknown"}
        />
      )}
    </div>
  );
}
