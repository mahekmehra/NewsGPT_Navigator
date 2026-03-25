"""
NewsGPT Navigator — Shared State Schema

All 11 agents read/write this shared TypedDict state.
Audit trail appended at every step for full provenance.
"""

from typing import TypedDict, Optional
import operator
from typing import Annotated


class NewsArticle(TypedDict, total=False):
    """Single news article from fetch agent."""
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
    """Single audit trail entry."""
    timestamp: str
    agent: str
    action: str
    inputs: dict
    outputs: dict


class AnalysisResult(TypedDict, total=False):
    """Structured analysis output."""
    summary: str
    timeline: list
    prediction: str
    key_entities: list
    sentiment: str
    sources_used: list
    model_used: str
    complexity_class: str


class BriefingOutput(TypedDict, total=False):
    """Final delivery output."""
    title: str
    summary: str
    detailed_briefing: str
    timeline: list
    prediction: str
    sources: list
    persona: str
    language: str
    translated_summary: str
    bias_score: float
    compliance_status: str
    generated_at: str


# ── New TypedDicts for expanded agents ──


class EntitySentiment(TypedDict, total=False):
    """Per-entity sentiment tag from entity_sentiment agent."""
    entity: str
    entity_type: str        # PERSON, ORG, GPE, etc.
    sentiment: str          # positive / negative / neutral
    score: float            # confidence 0-1
    mentions: int           # how many articles mention this entity
    articles: list          # article indices that mention this entity


class AngleCluster(TypedDict, total=False):
    """A narrative angle cluster from angle_decomposition agent."""
    angle_id: int
    label: str              # e.g. "fiscal impact", "market reaction"
    article_ids: list       # indices into verified_articles
    summary: str            # LLM-generated per-angle summary
    article_count: int


class UserProfile(TypedDict, total=False):
    """Deep user profile built by profile_ranking agent."""
    persona_preset: str     # "CFO" or "first_gen_investor"
    interests: list         # domain interest tags
    knowledge_level: str    # expert / intermediate / beginner
    risk_appetite: str      # conservative / moderate / aggressive
    jargon_comfort: str     # high / medium / low
    preferred_depth: str    # brief / standard / detailed


class ConflictItem(TypedDict, total=False):
    """A narrative conflict detected by the conflict agent."""
    conflict_type: str      # factual / interpretive / predictive
    claim_a: str
    source_a: str
    claim_b: str
    source_b: str
    entity: str             # entity or topic at conflict
    severity: str           # high / medium / low
    explanation: str


class EmotionalRegister(TypedDict, total=False):
    """Emotional tone register from the emotional calibration agent."""
    register: str           # crisis / opportunity / uncertainty / neutral
    intensity: float        # 0-1 scale
    tone_guidance: str      # guidance string for downstream agents
    crisis_signals: list    # specific signals detected
    opportunity_signals: list
    uncertainty_signals: list


class KnowledgeDiffItem(TypedDict, total=False):
    """A single knowledge delta item."""
    entity: str
    status: str             # new / changed / known / removed
    detail: str             # what changed or what's new
    previous_value: str     # what user previously knew
    current_value: str      # what the new data says


class StoryArcEntry(TypedDict, total=False):
    """Temporal sentiment trend for a single entity."""
    entity: str
    entity_type: str
    trend: list             # [{"period": "...", "sentiment": "...", "score": 0.8}, ...]
    shift: str              # e.g. "negative→neutral"
    first_seen: str         # ISO timestamp
    latest_update: str      # ISO timestamp


class VideoOutput(TypedDict, total=False):
    """Video generation output from the video agent."""
    script_hindi: str       # Hindi script text (legacy name, actually script in any lang)
    script_english: str     # Original English script
    script_language: str    # Language the script was generated in
    audio_path: str         # Path to TTS audio file
    video_path: str         # Path to generated MP4
    duration_seconds: float # Video duration
    generation_time: float  # Wall time to generate (target < 60s)
    jargon_cleaned: bool    # Whether jargon map was applied


class PipelineState(TypedDict, total=False):
    """
    Shared state for the entire NewsGPT pipeline.
    All 11 agents read/write to this single TypedDict.
    """
    # ── Input ──
    topic: str
    persona: str          # Student / Investor / Beginner / General / CFO / FirstGen
    custom_persona: str   # Free-text custom persona description
    language: str         # Target language code (default "en")

    # ── Fetch Agent ──
    articles: list        # List[NewsArticle]
    quality_scores: list  # Per-article quality scores
    verified_articles: list  # Articles passing quality threshold
    fetch_success: bool

    # ── Entity Sentiment Agent (NEW) ──
    entity_sentiments: list   # List[EntitySentiment]
    entities_extracted: bool

    # ── Angle Decomposition Agent (NEW) ──
    angle_clusters: list      # List[AngleCluster]
    angle_indexes_built: bool

    # ── Analysis Agent ──
    embeddings_built: bool
    analysis: dict        # AnalysisResult
    analysis_success: bool

    # ── Compliance Agent ──
    bias_score: float
    bias_details: dict
    compliance_passed: bool

    # ── Profile Ranking Agent (NEW) ──
    user_profile: dict        # UserProfile
    ranked_articles: list     # Articles reordered by profile relevance
    persona_template: str     # Selected prompt template for delivery

    # ── Narrative Conflict Agent (NEW — UNIQUE) ──
    conflicts: list           # List[ConflictItem]
    conflicts_detected: bool

    # ── Emotional Calibration Agent (NEW — UNIQUE) ──
    emotional_register: dict  # EmotionalRegister
    emotion_calibrated: bool

    # ── Delivery Agent ──
    briefing: dict        # BriefingOutput

    # ── Knowledge Diff Agent (NEW — UNIQUE) ──
    knowledge_diff: list      # List[KnowledgeDiffItem]
    knowledge_session_id: str # Session ID for knowledge store
    knowledge_updated: bool

    # ── Video Agent (NEW — UNIQUE) ──
    video_output: dict        # VideoOutput
    video_generated: bool

    # ── Story Arc Tracker ──
    story_arc: list           # List[StoryArcEntry]

    # ── Control Flow ──
    retry_count: int
    max_retries: int
    current_agent: str
    error: str
    pipeline_status: str  # "running" | "completed" | "failed"

    # ── Audit Trail (append-only) ──
    audit_trail: Annotated[list, operator.add]  # List[AuditEntry]


def create_initial_state(
    topic: str,
    persona: str = "General",
    language: str = "en",
    knowledge_session_id: str = "",
    custom_persona: str = "",
) -> PipelineState:
    """Create a fresh pipeline state with defaults."""
    return PipelineState(
        topic=topic,
        persona=persona,
        custom_persona=custom_persona,
        language=language,
        # Fetch
        articles=[],
        quality_scores=[],
        verified_articles=[],
        fetch_success=False,
        # Entity Sentiment
        entity_sentiments=[],
        entities_extracted=False,
        # Angle Decomposition
        angle_clusters=[],
        angle_indexes_built=False,
        # Analysis
        embeddings_built=False,
        analysis={},
        analysis_success=False,
        # Compliance
        bias_score=0.0,
        bias_details={},
        compliance_passed=False,
        # Profile Ranking
        user_profile={},
        ranked_articles=[],
        persona_template="",
        # Conflicts
        conflicts=[],
        conflicts_detected=False,
        # Emotional Calibration
        emotional_register={},
        emotion_calibrated=False,
        # Delivery
        briefing={},
        # Knowledge Diff
        knowledge_diff=[],
        knowledge_session_id=knowledge_session_id,
        knowledge_updated=False,
        # Video
        video_output={},
        video_generated=False,
        # Story Arc
        story_arc=[],
        # Control
        retry_count=0,
        max_retries=3,
        current_agent="orchestrator",
        error="",
        pipeline_status="running",
        audit_trail=[],
    )
