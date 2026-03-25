import { useState } from "react";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import Results from "./pages/Results";
import AuditPage from "./pages/AuditPage";
import Settings from "./pages/Settings";
import EntityMap from "./pages/EntityMap";
import AngleBriefing from "./pages/AngleBriefing";
import PersonaCompare from "./pages/PersonaCompare";
import ConflictMap from "./pages/ConflictMap";
import KnowledgeDelta from "./pages/KnowledgeDelta";
import VideoPlayer from "./pages/VideoPlayer";
import StoryArc from "./pages/StoryArc";
import { analyzeTopic } from "./api/client";

export default function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loadingStep, setLoadingStep] = useState("");

  const handleAnalyze = async (topic, persona, language, customPersona) => {
    setIsLoading(true);
    setError("");
    setLoadingStep("Starting 11-agent pipeline...");

    try {
      const data = await analyzeTopic(topic, persona, language, customPersona);
      setResult(data);
      setActivePage("results");
    } catch (err) {
      setError(err.message || "An error occurred");
    } finally {
      setIsLoading(false);
      setLoadingStep("");
    }
  };

  const renderPage = () => {
    switch (activePage) {
      case "dashboard":
        return (
          <div>
            <Dashboard onAnalyze={handleAnalyze} isLoading={isLoading} />

            {/* Loading State */}
            {isLoading && (
              <div className="glass-card spinner-container" style={{ marginTop: "2rem", maxWidth: "700px", marginLeft: "auto", marginRight: "auto" }}>
                <div className="spinner"></div>
                <div className="spinner-text">{loadingStep || "11 AI agents are working..."}</div>
                <div className="pipeline-steps">
                  <span className="pipeline-step active">Fetch</span>
                  <span className="pipeline-arrow">→</span>
                  <span className="pipeline-step">Entity</span>
                  <span className="pipeline-arrow">→</span>
                  <span className="pipeline-step">Angles</span>
                  <span className="pipeline-arrow">→</span>
                  <span className="pipeline-step">Analysis</span>
                  <span className="pipeline-arrow">→</span>
                  <span className="pipeline-step">Compliance</span>
                  <span className="pipeline-arrow">→</span>
                  <span className="pipeline-step">Profile</span>
                  <span className="pipeline-arrow">→</span>
                  <span className="pipeline-step">Conflict</span>
                  <span className="pipeline-arrow">→</span>
                  <span className="pipeline-step">Emotion</span>
                  <span className="pipeline-arrow">→</span>
                  <span className="pipeline-step">Delivery</span>
                  <span className="pipeline-arrow">→</span>
                  <span className="pipeline-step">K-Diff</span>
                  <span className="pipeline-arrow">+</span>
                  <span className="pipeline-step">Video</span>
                </div>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="glass-card error-container" style={{ marginTop: "1.5rem", maxWidth: "700px", marginLeft: "auto", marginRight: "auto" }}>
                <div className="error-icon">⚠️</div>
                <div className="error-message">{error}</div>
                <button className="btn btn-outline" onClick={() => setError("")}>
                  Dismiss
                </button>
              </div>
            )}
          </div>
        );

      case "results":
        return <Results result={result} />;

      case "entities":
        return <EntityMap entitySentiments={result?.entity_sentiments || []} />;

      case "angles":
        return <AngleBriefing angleClusters={result?.angle_clusters || []} articles={result?.verified_articles || []} />;

      case "persona":
        return <PersonaCompare result={result} />;

      case "conflicts":
        return <ConflictMap conflicts={result?.conflicts || []} />;

      case "knowledge":
        return <KnowledgeDelta knowledgeDiff={result?.knowledge_diff || []} />;

      case "video":
        return <VideoPlayer videoOutput={result?.video_output || {}} />;

      case "storyarc":
        return <StoryArc storyArc={result?.story_arc || []} />;

      case "audit":
        return <AuditPage auditTrail={result?.audit_trail || []} />;

      case "settings":
        return <Settings />;

      default:
        return <Dashboard onAnalyze={handleAnalyze} isLoading={isLoading} />;
    }
  };

  return (
    <div className="app-layout">
      <Navbar activePage={activePage} onNavigate={setActivePage} />
      <main className="main-content">{renderPage()}</main>
    </div>
  );
}
