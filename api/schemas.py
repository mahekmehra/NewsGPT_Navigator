"""
NewsGPT Navigator — Pydantic Schemas

Request and response models for the FastAPI backend.
Covers all 10 agents in the intelligence pipeline.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# ── Request ─────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """Request body for the /analyze endpoint."""
    topic: str = Field(..., min_length=2, max_length=200)
    persona: str = "General"
    custom_persona: str = ""
    language: str = "en"
    knowledge_session_id: str = ""


# ── Shared Sub-Models ───────────────────────────────────────────────

class SourceInfo(BaseModel):
    """A news source reference."""
    title: str = ""
    source: str = ""
    url: str = ""


class TimelineEvent(BaseModel):
    """A single timeline event extracted from articles."""
    date: str = ""
    event: str = ""
    source_title: str = ""
    url: str = ""


class VideoItem(BaseModel):
    """A YouTube video link with thumbnail."""
    title: str = ""
    url: str = ""
    thumbnail: str = ""


# ── Agent Output Models ─────────────────────────────────────────────

class EntitySentimentResponse(BaseModel):
    """Entity with sentiment tagging from the Entity Sentiment agent."""
    entity: str = ""
    entity_type: str = ""
    sentiment: str = "neutral"
    score: float = 0.0
    mentions: int = 0
    articles: List[Any] = []


class AngleClusterResponse(BaseModel):
    """A narrative angle cluster from the Angle Decomposition agent."""
    angle_id: int = 0
    label: str = ""
    article_ids: List[Any] = []
    summary: str = ""
    article_count: int = 0


class ConflictResponse(BaseModel):
    """A detected narrative conflict from the Conflict agent."""
    conflict_type: str = ""
    claim_a: str = ""
    source_a: str = ""
    claim_b: str = ""
    source_b: str = ""
    entity: str = ""
    severity: str = "medium"
    explanation: str = ""


class EmotionalRegisterResponse(BaseModel):
    """Emotional calibration output from the Emotion agent."""
    emotion_type: str = "neutral"
    intensity: float = 0.0
    tone_guidance: str = ""
    crisis_signals: List[str] = []
    opportunity_signals: List[str] = []
    uncertainty_signals: List[str] = []


class StoryArcResponse(BaseModel):
    """Temporal sentiment trend for a single entity."""
    entity: str = ""
    entity_type: str = ""
    trend: List[Any] = []
    shift: str = ""
    first_seen: str = ""
    latest_update: str = ""


class UserProfileResponse(BaseModel):
    """User profile built by the Profile Ranking agent."""
    persona_preset: str = ""
    interests: List[str] = []
    knowledge_level: str = ""
    risk_appetite: str = ""
    jargon_comfort: str = ""
    preferred_depth: str = ""


# ── Briefing Response ───────────────────────────────────────────────

class BriefingResponse(BaseModel):
    """Complete intelligence briefing assembled by the Delivery agent."""
    title: str = ""
    summary: str = ""

    # Persona-specific intelligence
    persona_brief: Dict[str, Any] = {}
    angles: Dict[str, str] = {}
    follow_up_questions: List[str] = []

    # Content
    timeline: List[TimelineEvent] = []
    prediction: str = ""

    # Metadata
    key_entities: List[str] = []
    sentiment: str = "neutral"
    sources: List[SourceInfo] = []

    # Personalization
    persona: str = "General"
    language: str = "en"
    translated_summary: str = ""

    # Compliance
    bias_score: float = 0.0
    compliance_status: str = ""

    # Model info
    model_used: str = ""
    complexity_class: str = ""
    generated_at: str = ""

    # Multimodal outputs
    videos: List[VideoItem] = []
    audio_url: Optional[str] = None
    entities_metadata: List[Any] = []


# ── Main Response ───────────────────────────────────────────────────

class AnalyzeResponse(BaseModel):
    """Full response from the /analyze endpoint."""
    success: bool

    briefing: Optional[BriefingResponse] = None

    # Agent outputs
    entity_sentiments: List[Any] = []
    angle_clusters: List[Any] = []
    user_profile: Optional[UserProfileResponse] = None
    conflicts: List[Any] = []
    emotional_register: Optional[EmotionalRegisterResponse] = None
    story_arc: List[Any] = []

    # Metadata
    audit_trail: List[Any] = []
    error: str = ""
    pipeline_status: str = ""

    # Article stats
    articles_fetched: int = 0
    articles_verified: int = 0
    verified_articles: List[Any] = []


# ── Utility Models ──────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Response from the /health endpoint."""
    status: str = "ok"
    version: str = "2.1.0"
    agents: List[str] = []


class LanguageInfo(BaseModel):
    """A supported language entry."""
    code: str
    name: str
