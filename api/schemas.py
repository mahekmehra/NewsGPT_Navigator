"""
NewsGPT Navigator — Pydantic Schemas

Request/response models for the FastAPI backend.
Supports all 11 agents.
"""

from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    """Request to analyze a news topic."""
    topic: str = Field(..., description="News topic to analyze", min_length=2, max_length=200)
    persona: str = Field(default="General", description="User persona: Student, Investor, Beginner, General, CFO, FirstGen")
    custom_persona: str = Field(default="", description="Free-text custom persona description (e.g. 'startup founder', 'journalist')")
    language: str = Field(default="en", description="Target language code (e.g., 'en', 'hi', 'ta', 'te', 'bn')")
    knowledge_session_id: str = Field(default="", description="Session ID for knowledge state tracking")


class SourceInfo(BaseModel):
    """A news source reference."""
    title: str = ""
    source: str = ""
    url: str = ""


class TimelineEvent(BaseModel):
    """A timeline event."""
    date: str = ""
    event: str = ""


class EntitySentimentResponse(BaseModel):
    """Per-entity sentiment data."""
    entity: str = ""
    entity_type: str = ""
    sentiment: str = "neutral"
    score: float = 0.0
    mentions: int = 0
    articles: list = []


class AngleClusterResponse(BaseModel):
    """A narrative angle cluster."""
    angle_id: int = 0
    label: str = ""
    article_ids: list = []
    summary: str = ""
    article_count: int = 0


class ConflictResponse(BaseModel):
    """A narrative conflict."""
    conflict_type: str = ""
    claim_a: str = ""
    source_a: str = ""
    claim_b: str = ""
    source_b: str = ""
    entity: str = ""
    severity: str = "medium"
    explanation: str = ""


class EmotionalRegisterResponse(BaseModel):
    """Emotional register data."""
    register: str = "neutral"
    intensity: float = 0.0
    tone_guidance: str = ""
    crisis_signals: list = []
    opportunity_signals: list = []
    uncertainty_signals: list = []


class KnowledgeDiffResponse(BaseModel):
    """A knowledge diff item."""
    entity: str = ""
    status: str = ""
    detail: str = ""
    previous_value: str = ""
    current_value: str = ""


class VideoOutputResponse(BaseModel):
    """Video generation output."""
    script_hindi: str = ""
    script_english: str = ""
    script_language: str = "Hindi"
    audio_path: str = ""
    video_path: str = ""
    duration_seconds: float = 0.0
    generation_time: float = 0.0
    jargon_cleaned: bool = False


class StoryArcResponse(BaseModel):
    """A story arc entry showing temporal sentiment trend."""
    entity: str = ""
    entity_type: str = ""
    trend: list = []
    shift: str = ""
    first_seen: str = ""
    latest_update: str = ""


class UserProfileResponse(BaseModel):
    """User profile data."""
    persona_preset: str = ""
    interests: list = []
    knowledge_level: str = ""
    risk_appetite: str = ""
    jargon_comfort: str = ""
    preferred_depth: str = ""


class BriefingResponse(BaseModel):
    """Full briefing response."""
    title: str = ""
    summary: str = ""
    detailed_briefing: str = ""
    timeline: list = []
    prediction: str = ""
    key_entities: list = []
    sentiment: str = "neutral"
    sources: list = []
    persona: str = "General"
    language: str = "en"
    translated_summary: str = ""
    bias_score: float = 0.0
    compliance_status: str = ""
    model_used: str = ""
    complexity_class: str = ""
    generated_at: str = ""


class AnalyzeResponse(BaseModel):
    """Complete pipeline response with all 11 agents' output."""
    success: bool
    briefing: Optional[BriefingResponse] = None
    # New agent outputs
    entity_sentiments: list = []
    angle_clusters: list = []
    user_profile: Optional[UserProfileResponse] = None
    conflicts: list = []
    emotional_register: Optional[EmotionalRegisterResponse] = None
    knowledge_diff: list = []
    video_output: Optional[VideoOutputResponse] = None
    story_arc: list = []
    # Metadata
    audit_trail: list = []
    error: str = ""
    pipeline_status: str = ""
    articles_fetched: int = 0
    articles_verified: int = 0


class AuditResponse(BaseModel):
    """Audit trail response."""
    topic: str = ""
    audit_trail: list = []
    total_entries: int = 0


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str = "2.0.0"
    agents: list = [
        "orchestrator", "fetch", "entity_sentiment", "angle_decomposition",
        "analysis", "compliance", "profile_ranking", "conflict",
        "emotional_calibration", "delivery", "knowledge_diff", "video"
    ]


class LanguageInfo(BaseModel):
    """Supported language info."""
    code: str
    name: str
