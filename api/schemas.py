"""
NewsGPT Navigator — Pydantic Schemas

Request/response models for the FastAPI backend.
Supports all 10 agents.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class AnalyzeRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200)
    persona: str = "General"
    custom_persona: str = ""
    language: str = "en"
    knowledge_session_id: str = ""


# ─────────────────────────────
# COMMON STRUCTURES
# ─────────────────────────────

class SourceInfo(BaseModel):
    title: str = ""
    source: str = ""
    url: str = ""


class TimelineEvent(BaseModel):
    date: str = ""
    event: str = ""


class VideoItem(BaseModel):
    title: str = ""
    url: str = ""
    thumbnail: str = ""


# ─────────────────────────────
# AGENT RESPONSES
# ─────────────────────────────

class EntitySentimentResponse(BaseModel):
    entity: str = ""
    entity_type: str = ""
    sentiment: str = "neutral"
    score: float = 0.0
    mentions: int = 0
    articles: List[Any] = []


class AngleClusterResponse(BaseModel):
    angle_id: int = 0
    label: str = ""
    article_ids: List[Any] = []
    summary: str = ""
    article_count: int = 0


class ConflictResponse(BaseModel):
    conflict_type: str = ""
    claim_a: str = ""
    source_a: str = ""
    claim_b: str = ""
    source_b: str = ""
    entity: str = ""
    severity: str = "medium"
    explanation: str = ""


class EmotionalRegisterResponse(BaseModel):
    register: str = "neutral"
    intensity: float = 0.0
    tone_guidance: str = ""
    crisis_signals: List[str] = []
    opportunity_signals: List[str] = []
    uncertainty_signals: List[str] = []


class KnowledgeDiffResponse(BaseModel):
    entity: str = ""
    status: str = ""
    detail: str = ""
    previous_value: str = ""
    current_value: str = ""


class VideoOutputResponse(BaseModel):
    # kept for backward compatibility
    script_hindi: str = ""
    script_english: str = ""
    script_language: str = "Hindi"
    audio_path: str = ""
    video_path: str = ""
    duration_seconds: float = 0.0
    generation_time: float = 0.0
    jargon_cleaned: bool = False


class StoryArcResponse(BaseModel):
    entity: str = ""
    entity_type: str = ""
    trend: List[Any] = []
    shift: str = ""
    first_seen: str = ""
    latest_update: str = ""


class UserProfileResponse(BaseModel):
    persona_preset: str = ""
    interests: List[str] = []
    knowledge_level: str = ""
    risk_appetite: str = ""
    jargon_comfort: str = ""
    preferred_depth: str = ""


# ─────────────────────────────
# 🔥 UPDATED BRIEFING (IMPORTANT)
# ─────────────────────────────

class BriefingResponse(BaseModel):
    title: str = ""
    summary: str = ""

    # 🔥 NEW (CORE EXPERIENCE)
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

    # Extra intelligence
    bias_score: float = 0.0
    compliance_status: str = ""

    # Model info
    model_used: str = ""
    complexity_class: str = ""
    generated_at: str = ""

    # 🔥 MULTIMODAL FEATURES
    videos: List[VideoItem] = []
    audio_url: Optional[str] = None


# ─────────────────────────────
# MAIN RESPONSE
# ─────────────────────────────

class AnalyzeResponse(BaseModel):
    success: bool

    briefing: Optional[BriefingResponse] = None

    # Agent outputs
    entity_sentiments: List[Any] = []
    angle_clusters: List[Any] = []
    user_profile: Optional[UserProfileResponse] = None
    conflicts: List[Any] = []
    emotional_register: Optional[EmotionalRegisterResponse] = None
    knowledge_diff: List[Any] = []
    video_output: Optional[VideoOutputResponse] = None
    story_arc: List[Any] = []

    # Metadata
    audit_trail: List[Any] = []
    error: str = ""
    pipeline_status: str = ""

    # Stats
    articles_fetched: int = 0
    articles_verified: int = 0
    verified_articles: List[Any] = []




class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "2.1.0"
    agents: List[str] = []


class LanguageInfo(BaseModel):
    code: str
    name: str
