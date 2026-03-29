"""
NewsGPT Navigator — Shared Pipeline State Schema

Defines the TypedDict state shared across all 10 agents in the
LangGraph pipeline. Each agent reads from and writes to this state.
An audit trail is appended at every step for full provenance.
"""

from typing import TypedDict, Optional, List, Dict, Any
import operator
from typing import Annotated


def _last_value(existing, new):
    """Reducer that keeps only the latest value (used by Annotated fields)."""
    return new


# ── Article & Audit Structures ──────────────────────────────────────

class NewsArticle(TypedDict, total=False):
    """A single news article with quality and credibility metadata."""
    title: str
    description: str
    content: str
    source: str
    source_domain: str
    url: str
    published_at: str
    quality_score: float
    credibility_verified: bool


class AuditEntry(TypedDict):
    """One step in the pipeline audit trail."""
    timestamp: str
    agent: str
    action: str
    inputs: dict
    outputs: dict


# ── Analysis & Briefing Structures ──────────────────────────────────

class AnalysisResult(TypedDict, total=False):
    """Structured output from the Analysis agent."""
    summary: str
    concise_summary: str
    timeline: list
    prediction: str
    key_entities: list
    sentiment: str
    market_impact: str
    risks: str
    opportunities: str
    expert_opinion: str
    sources_used: list
    model_used: str
    complexity_class: str


class BriefingOutput(TypedDict, total=False):
    """Final briefing payload assembled by the Delivery agent."""
    title: str
    summary: str

    persona_brief: Dict[str, Any]
    angles: Dict[str, str]
    follow_up_questions: List[str]

    timeline: list
    prediction: str

    key_entities: list
    sentiment: str
    sources: list

    persona: str
    language: str
    translated_summary: str

    bias_score: float
    compliance_status: str

    model_used: str
    complexity_class: str
    generated_at: str

    # Multimodal outputs
    videos: List[Dict[str, str]]
    audio_url: str


# ── Agent-Specific Structures ───────────────────────────────────────

class EntitySentiment(TypedDict, total=False):
    """Entity extracted by the Entity Sentiment agent."""
    entity: str
    entity_type: str
    sentiment: str
    score: float
    mentions: int
    articles: list


class AngleCluster(TypedDict, total=False):
    """A narrative angle cluster from the Angle Decomposition agent."""
    angle_id: int
    label: str
    article_ids: list
    summary: str
    article_count: int


class UserProfile(TypedDict, total=False):
    """User profile built by the Profile Ranking agent."""
    persona_preset: str
    interests: list
    knowledge_level: str
    risk_appetite: str
    jargon_comfort: str
    preferred_depth: str


class ConflictItem(TypedDict, total=False):
    """A narrative conflict detected by the Conflict agent."""
    conflict_type: str
    claim_a: str
    source_a: str
    claim_b: str
    source_b: str
    entity: str
    severity: str
    explanation: str


class EmotionalRegister(TypedDict, total=False):
    """Emotional calibration output from the Emotion agent."""
    emotion_type: str
    intensity: float
    tone_guidance: str
    crisis_signals: list
    opportunity_signals: list
    uncertainty_signals: list


class StoryArcEntry(TypedDict, total=False):
    """Temporal sentiment trend for a single entity across sessions."""
    entity: str
    entity_type: str
    trend: list
    shift: str
    first_seen: str
    latest_update: str


# ── Pipeline State ──────────────────────────────────────────────────

class PipelineState(TypedDict, total=False):
    """Shared state passed through all 10 agents in the LangGraph DAG."""

    # Input parameters
    topic: str
    persona: str
    custom_persona: str
    language: str

    # Fetch agent outputs
    articles: list
    quality_scores: list
    verified_articles: list
    fetch_success: bool
    source_quality_summary: str

    # Entity Sentiment agent outputs
    entity_sentiments: list
    entities_extracted: bool

    # Angle Decomposition agent outputs
    angle_clusters: list
    angle_indexes_built: bool

    # Analysis agent outputs
    embeddings_built: bool
    analysis: dict
    analysis_success: bool

    # Compliance agent outputs
    bias_score: float
    bias_details: dict
    compliance_passed: bool

    # Profile Ranking agent outputs
    user_profile: dict
    ranked_articles: list
    persona_template: str

    # Conflict agent outputs
    conflicts: list
    conflicts_detected: bool

    # Emotional Calibration agent outputs
    emotional_register: dict
    emotion_calibrated: bool

    # Delivery agent outputs
    briefing: dict

    # Video agent outputs
    video_output: dict
    video_generated: bool
    videos: Annotated[list, _last_value]
    audio_url: Annotated[str, _last_value]

    # Story arc (cross-session entity trends)
    story_arc: list

    # Persona context for delivery
    persona_context: Annotated[str, _last_value]

    # Pipeline control
    retry_count: int
    max_retries: int
    current_agent: Annotated[str, _last_value]
    error: Annotated[str, _last_value]
    pipeline_status: Annotated[str, _last_value]

    # Audit trail (append-only across all agents)
    audit_trail: Annotated[list, operator.add]


def create_initial_state(
    topic: str,
    persona: str = "General",
    language: str = "en",
    knowledge_session_id: str = "",
    custom_persona: str = "",
) -> PipelineState:
    """
    Create a fresh pipeline state with all fields initialized to defaults.

    Args:
        topic: News topic to analyze
        persona: Persona preset name (e.g. "Investor", "Student")
        language: ISO language code for translation (e.g. "en", "hi")
        knowledge_session_id: Optional session ID for story arc persistence
        custom_persona: Optional free-text persona description
    """
    return PipelineState(
        topic=topic,
        persona=persona,
        custom_persona=custom_persona,
        language=language,

        articles=[],
        quality_scores=[],
        verified_articles=[],
        fetch_success=False,

        entity_sentiments=[],
        entities_extracted=False,

        angle_clusters=[],
        angle_indexes_built=False,

        embeddings_built=False,
        analysis={},
        analysis_success=False,

        bias_score=0.0,
        bias_details={},
        compliance_passed=False,

        user_profile={},
        ranked_articles=[],
        persona_template="",

        conflicts=[],
        conflicts_detected=False,

        emotional_register={},
        emotion_calibrated=False,

        briefing={},

        video_output={},
        video_generated=False,
        videos=[],
        audio_url="",

        story_arc=[],

        persona_context="",

        retry_count=0,
        max_retries=3,
        current_agent="orchestrator",
        error="",
        pipeline_status="running",

        audit_trail=[],
    )