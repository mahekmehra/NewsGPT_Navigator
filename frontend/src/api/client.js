/**
 * NewsGPT Navigator — API Client
 *
 * Handles all communication with the FastAPI backend.
 */

const API_BASE = "http://localhost:8000";

/**
 * Run the full analysis pipeline on a topic.
 */
export async function analyzeTopic(topic, persona = "General", language = "en", customPersona = "") {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, persona, language, custom_persona: customPersona }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Get audit trail for a session.
 */
export async function getAuditTrail(sessionId) {
  const response = await fetch(`${API_BASE}/audit/${sessionId}`);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

/**
 * Health check.
 */
export async function healthCheck() {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}

/**
 * Get supported languages.
 */
export async function getLanguages() {
  const response = await fetch(`${API_BASE}/languages`);
  return response.json();
}

/**
 * Get available personas.
 */
export async function getPersonas() {
  const response = await fetch(`${API_BASE}/personas`);
  return response.json();
}

/**
 * List all sessions.
 */
export async function getSessions() {
  const response = await fetch(`${API_BASE}/sessions`);
  return response.json();
}
