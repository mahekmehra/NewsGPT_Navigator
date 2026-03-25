import { useState, useRef, useEffect } from "react";

/**
 * VideoPlayer — 60-second countdown + MP4 player + script view
 */
export default function VideoPlayer({ videoOutput = {} }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [showScript, setShowScript] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [countdown, setCountdown] = useState(null);
  const videoRef = useRef(null);

  const {
    script_hindi = "",
    script_english = "",
    video_path = "",
    duration_seconds = 0,
    generation_time = 0,
    jargon_cleaned = false,
  } = videoOutput;

  const hasVideo = !!video_path;

  // Countdown effect for generation time display
  useEffect(() => {
    if (countdown !== null && countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  if (!hasVideo && !script_hindi) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1 className="page-title"><span className="title-accent">🎬</span> Video Player</h1>
          <p className="page-subtitle">Generate a Hindi news video from your analysis</p>
        </div>
        <div className="glass-card" style={{ textAlign: "center", padding: "3rem" }}>
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📹</div>
          <p style={{ color: "var(--text-secondary)" }}>No video generated yet. Run an analysis to create a Hindi news video.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title"><span className="title-accent">🎬</span> Video Player</h1>
        <p className="page-subtitle">
          Hindi news video • {formatTime(duration_seconds)} duration
          {generation_time > 0 && ` • Generated in ${generation_time.toFixed(1)}s`}
        </p>
      </div>

      {/* Generation time ring */}
      <div style={{
        display: "flex",
        gap: "1rem",
        marginBottom: "1.5rem",
        flexWrap: "wrap",
      }}>
        <div className="glass-card" style={{
          padding: "1rem",
          display: "flex",
          alignItems: "center",
          gap: "1rem",
          flex: 1,
          minWidth: "200px",
        }}>
          {/* Countdown ring */}
          <div style={{
            position: "relative",
            width: "70px",
            height: "70px",
            flexShrink: 0,
          }}>
            <svg width="70" height="70" style={{ transform: "rotate(-90deg)" }}>
              <circle cx="35" cy="35" r="30" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="4" />
              <circle
                cx="35" cy="35" r="30"
                fill="none"
                stroke={generation_time <= 60 ? "#10b981" : "#ef4444"}
                strokeWidth="4"
                strokeDasharray={`${(Math.min(generation_time, 60) / 60) * 188.5} 188.5`}
                strokeLinecap="round"
                style={{ transition: "stroke-dasharray 1s ease" }}
              />
            </svg>
            <div style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -50%)",
              fontSize: "0.85rem",
              fontWeight: 700,
              color: generation_time <= 60 ? "#10b981" : "#ef4444",
            }}>
              {generation_time.toFixed(0)}s
            </div>
          </div>
          <div>
            <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>Generation Time</div>
            <div style={{ fontSize: "0.8rem", color: generation_time <= 60 ? "#10b981" : "#ef4444" }}>
              {generation_time <= 60 ? "✅ Under 60s target" : "⚠️ Exceeded 60s target"}
            </div>
          </div>
        </div>

        <div className="glass-card" style={{
          padding: "1rem",
          display: "flex",
          alignItems: "center",
          gap: "1rem",
          flex: 1,
          minWidth: "200px",
        }}>
          <span style={{ fontSize: "2rem" }}>📏</span>
          <div>
            <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>{formatTime(duration_seconds)}</div>
            <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>Duration</div>
          </div>
        </div>

        <div className="glass-card" style={{
          padding: "1rem",
          display: "flex",
          alignItems: "center",
          gap: "1rem",
          flex: 1,
          minWidth: "200px",
        }}>
          <span style={{ fontSize: "2rem" }}>{jargon_cleaned ? "✨" : "📝"}</span>
          <div>
            <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>
              {jargon_cleaned ? "Jargon Cleaned" : "Original Text"}
            </div>
            <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
              Hindi financial terms applied
            </div>
          </div>
        </div>
      </div>

      {/* Video player */}
      {hasVideo && (
        <div className="glass-card" style={{ padding: "0", overflow: "hidden", borderRadius: "1rem", marginBottom: "1.5rem" }}>
          <video
            ref={videoRef}
            src={`http://localhost:8000/video/${video_path.split("/").pop()?.split("\\").pop()}`}
            controls
            onTimeUpdate={handleTimeUpdate}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            style={{ width: "100%", display: "block", borderRadius: "1rem" }}
          />
          {/* Progress bar */}
          <div style={{
            padding: "0.5rem 1rem",
            background: "rgba(0,0,0,0.4)",
            display: "flex",
            justifyContent: "space-between",
            fontSize: "0.8rem",
            color: "var(--text-secondary)",
          }}>
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration_seconds)}</span>
          </div>
        </div>
      )}

      {/* Script toggle */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        <button
          onClick={() => setShowScript(false)}
          className="btn"
          style={{
            background: !showScript ? "var(--accent-primary)" : "rgba(255,255,255,0.05)",
            color: !showScript ? "#fff" : "var(--text-secondary)",
            border: "none",
            padding: "0.5rem 1rem",
            borderRadius: "0.5rem",
            cursor: "pointer",
          }}
        >
          🇮🇳 Hindi Script
        </button>
        <button
          onClick={() => setShowScript(true)}
          className="btn"
          style={{
            background: showScript ? "var(--accent-primary)" : "rgba(255,255,255,0.05)",
            color: showScript ? "#fff" : "var(--text-secondary)",
            border: "none",
            padding: "0.5rem 1rem",
            borderRadius: "0.5rem",
            cursor: "pointer",
          }}
        >
          🇬🇧 English Source
        </button>
      </div>

      {/* Script content */}
      <div className="glass-card" style={{
        borderLeft: showScript ? "3px solid #3b82f6" : "3px solid #f59e0b",
      }}>
        <h3 style={{ marginBottom: "1rem", color: "var(--text-primary)" }}>
          {showScript ? "📄 English Source Script" : "📄 Hindi Script (हिंदी)"}
        </h3>
        <div style={{
          padding: "1.25rem",
          borderRadius: "0.75rem",
          background: "rgba(255,255,255,0.03)",
          lineHeight: 1.8,
          fontSize: "0.95rem",
          color: "var(--text-primary)",
          whiteSpace: "pre-wrap",
          fontFamily: showScript ? "inherit" : "'Noto Sans Devanagari', sans-serif",
          maxHeight: "400px",
          overflowY: "auto",
        }}>
          {showScript ? (script_english || "No English script available.") : (script_hindi || "No Hindi script available.")}
        </div>
      </div>
    </div>
  );
}
