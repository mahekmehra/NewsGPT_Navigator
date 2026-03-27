"""
NewsGPT Navigator — Shared State Schema

All 10 agents read/write this shared TypedDict state.
Audit trail appended at every step for full provenance.
"""

from typing import TypedDict, Optional, List, Dict, Any
import operator
from typing import Annotated


def _last_value(existing, new):
    return new


class NewsArticle(TypedDict, total=False):
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
    timestamp: str
    agent: str
    action: str
    inputs: dict
    outputs: dict


# 🔥 UPDATED ANALYSIS STRUCTURE
class AnalysisResult(TypedDict, total=False):
    summary: str
    concise_summary: str
    timeline: list
    prediction: str
    key_entities: list
    sentiment: str

    # NEW INTELLIGENCE
    market_impact: str
    risks: str
    opportunities: str
    expert_opinion: str

    sources_used: list
    model_used: str
    complexity_class: str


# 🔥 UPDATED BRIEFING STRUCTURE
class BriefingOutput(TypedDict, total=False):
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

    # 🔥 MULTIMODAL
    videos: List[Dict[str, str]]
    audio_url: str


# ── Other TypedDicts unchanged ──

class EntitySentiment(TypedDict, total=False):
    entity: str
    entity_type: str
    sentiment: str
    score: float
    mentions: int
    articles: list


class AngleCluster(TypedDict, total=False):
    angle_id: int
    label: str
    article_ids: list
    summary: str
    article_count: int


class UserProfile(TypedDict, total=False):
    persona_preset: str
    interests: list
    knowledge_level: str
    risk_appetite: str
    jargon_comfort: str
    preferred_depth: str


class ConflictItem(TypedDict, total=False):
    conflict_type: str
    claim_a: str
    source_a: str
    claim_b: str
    source_b: str
    entity: str
    severity: str
    explanation: str


class EmotionalRegister(TypedDict, total=False):
    register: str
    intensity: float
    tone_guidance: str
    crisis_signals: list
    opportunity_signals: list
    uncertainty_signals: list


class KnowledgeDiffItem(TypedDict, total=False):
    entity: str
    status: str
    detail: str
    previous_value: str
    current_value: str


class StoryArcEntry(TypedDict, total=False):
    entity: str
    entity_type: str
    trend: list
    shift: str
    first_seen: str
    latest_update: str


class VideoOutput(TypedDict, total=False):
    script_hindi: str
    script_english: str
    script_language: str
    audio_path: str
    video_path: str
    duration_seconds: float
    generation_time: float
    jargon_cleaned: bool


class PipelineState(TypedDict, total=False):
    topic: str
    persona: str
    custom_persona: str
    language: str

    articles: list
    quality_scores: list
    verified_articles: list
    fetch_success: bool

    entity_sentiments: list
    entities_extracted: bool

    angle_clusters: list
    angle_indexes_built: bool

    embeddings_built: bool
    analysis: dict
    analysis_success: bool

    bias_score: float
    bias_details: dict
    compliance_passed: bool

    user_profile: dict
    ranked_articles: list
    persona_template: str

    conflicts: list
    conflicts_detected: bool

    emotional_register: dict
    emotion_calibrated: bool

    briefing: dict

    knowledge_diff: list
    knowledge_session_id: str
    knowledge_updated: bool

    video_output: dict
    video_generated: bool

    # 🔥 NEW FIELDS
    videos: Annotated[list, _last_value]
    audio_url: Annotated[str, _last_value]

    story_arc: list

    persona_context: Annotated[str, _last_value]

    retry_count: int
    max_retries: int
    current_agent: Annotated[str, _last_value]
    error: Annotated[str, _last_value]
    pipeline_status: Annotated[str, _last_value]

    audit_trail: Annotated[list, operator.add]


def create_initial_state(
    topic: str,
    persona: str = "General",
    language: str = "en",
    knowledge_session_id: str = "",
    custom_persona: str = "",
) -> PipelineState:

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

        knowledge_diff=[],
        knowledge_session_id=knowledge_session_id,
        knowledge_updated=False,

        video_output={},
        video_generated=False,

        # 🔥 NEW INITIALIZATION
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