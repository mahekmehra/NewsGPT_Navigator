"""
NewsGPT Navigator — Orchestrator Agent (LangGraph StateGraph)

The brain. Builds the directed acyclic graph, manages conditional edges,
decides retry vs abort, routes between all 11 agents.
Runs the full pipeline with a single `pipeline.invoke(initial_state)` call.
No human needed at any point.
"""

from langgraph.graph import StateGraph, END
from agents.state import PipelineState, create_initial_state
from agents.fetch_agent import fetch_agent
from agents.entity_sentiment_agent import entity_sentiment_agent
from agents.angle_agent import angle_agent
from agents.analysis_agent import analysis_agent
from agents.compliance_agent import compliance_agent
from agents.profile_ranking_agent import profile_ranking_agent
from agents.conflict_agent import conflict_agent
from agents.emotional_agent import emotional_agent
from agents.delivery_agent import delivery_agent
from agents.knowledge_diff_agent import knowledge_diff_agent
from agents.video_agent import video_agent
from core.config import settings


# ── Conditional Edge Functions ──

def should_retry_fetch(state: PipelineState) -> str:
    """
    After fetch: check if we got enough quality articles.
    If not and retries remain, retry fetch. Otherwise, proceed.
    """
    fetch_success = state.get("fetch_success", False)
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", settings.MAX_RETRIES)

    if not fetch_success and retry_count < max_retries:
        return "retry_fetch"
    elif not fetch_success:
        return "abort"
    return "entity_sentiment"


def should_retry_analysis(state: PipelineState) -> str:
    """
    After compliance: if compliance failed and retries remain,
    loop back to analysis with stricter prompt. Otherwise proceed.
    """
    compliance_passed = state.get("compliance_passed", False)
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", settings.MAX_RETRIES)

    if not compliance_passed and retry_count < max_retries:
        return "reanalyze"
    elif not compliance_passed:
        return "deliver_with_warning"
    return "profile_ranking"


def post_delivery_router(state: PipelineState) -> str:
    """
    After delivery: branch to knowledge_diff.
    Video runs as a parallel step from delivery.
    """
    return "knowledge_diff"


# ── Wrapper nodes for retry logic ──

def retry_fetch_node(state: PipelineState) -> dict:
    """Increment retry counter and re-run fetch."""
    return {
        "retry_count": state.get("retry_count", 0) + 1,
        "current_agent": "orchestrator",
        "audit_trail": [{
            "timestamp": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
            "agent": "orchestrator",
            "action": "retry_fetch",
            "inputs": {"retry_count": state.get("retry_count", 0) + 1},
            "outputs": {"reason": "Low quality articles, retrying"},
        }],
    }


def reanalyze_node(state: PipelineState) -> dict:
    """Increment retry counter for compliance re-analysis."""
    return {
        "retry_count": state.get("retry_count", 0) + 1,
        "current_agent": "orchestrator",
        "audit_trail": [{
            "timestamp": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
            "agent": "orchestrator",
            "action": "reanalyze",
            "inputs": {"retry_count": state.get("retry_count", 0) + 1},
            "outputs": {"reason": "Compliance failed, rerunning analysis with stricter prompt"},
        }],
    }


def abort_node(state: PipelineState) -> dict:
    """Abort pipeline after max retries exhausted."""
    return {
        "pipeline_status": "failed",
        "current_agent": "orchestrator",
        "error": "Pipeline aborted: max retries exhausted",
        "audit_trail": [{
            "timestamp": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
            "agent": "orchestrator",
            "action": "abort",
            "inputs": {},
            "outputs": {"reason": "Max retries exhausted"},
        }],
    }


def deliver_with_warning_node(state: PipelineState) -> dict:
    """Mark that delivery will proceed despite compliance concerns."""
    return {
        "current_agent": "orchestrator",
        "audit_trail": [{
            "timestamp": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
            "agent": "orchestrator",
            "action": "deliver_with_warning",
            "inputs": {},
            "outputs": {"warning": "Delivering despite compliance concerns after max retries"},
        }],
    }


# ── Build the Graph ──

def build_pipeline() -> StateGraph:
    """
    Build the LangGraph StateGraph pipeline with 11 agent nodes.

    Graph structure (11 agents):
        fetch → [retry_fetch → fetch] or [entity_sentiment]
        entity_sentiment → angle_decomposition
        angle_decomposition → analysis
        analysis → compliance
        compliance → [reanalyze → analysis] or [profile_ranking]
        profile_ranking → conflict
        conflict → emotional_calibration
        emotional_calibration → delivery
        delivery → knowledge_diff → END
        delivery → video → END  (parallel branch)
    """
    graph = StateGraph(PipelineState)

    # ── Add all 11 agent nodes + control nodes ──
    graph.add_node("fetch", fetch_agent)
    graph.add_node("retry_fetch", retry_fetch_node)
    graph.add_node("entity_sentiment", entity_sentiment_agent)
    graph.add_node("angle_decomposition", angle_agent)
    graph.add_node("analysis", analysis_agent)
    graph.add_node("compliance", compliance_agent)
    graph.add_node("reanalyze", reanalyze_node)
    graph.add_node("profile_ranking", profile_ranking_agent)
    graph.add_node("conflict", conflict_agent)
    graph.add_node("emotional_calibration", emotional_agent)
    graph.add_node("delivery", delivery_agent)
    graph.add_node("deliver_with_warning", deliver_with_warning_node)
    graph.add_node("knowledge_diff", knowledge_diff_agent)
    graph.add_node("video", video_agent)
    graph.add_node("abort", abort_node)

    # ── Set entry point ──
    graph.set_entry_point("fetch")

    # ── Conditional edge after fetch ──
    graph.add_conditional_edges(
        "fetch",
        should_retry_fetch,
        {
            "retry_fetch": "retry_fetch",
            "entity_sentiment": "entity_sentiment",
            "abort": "abort",
        }
    )

    # Retry fetch loops back to fetch
    graph.add_edge("retry_fetch", "fetch")

    # ── New agent chain: entity_sentiment → angle → analysis ──
    graph.add_edge("entity_sentiment", "angle_decomposition")
    graph.add_edge("angle_decomposition", "analysis")

    # Analysis → Compliance
    graph.add_edge("analysis", "compliance")

    # ── Conditional edge after compliance ──
    graph.add_conditional_edges(
        "compliance",
        should_retry_analysis,
        {
            "reanalyze": "reanalyze",
            "profile_ranking": "profile_ranking",
            "deliver_with_warning": "deliver_with_warning",
        }
    )

    # Reanalyze loops back to analysis
    graph.add_edge("reanalyze", "analysis")

    # ── New agent chain: profile → conflict → emotional → delivery ──
    graph.add_edge("profile_ranking", "conflict")
    graph.add_edge("conflict", "emotional_calibration")
    graph.add_edge("emotional_calibration", "delivery")

    # Deliver with warning → delivery
    graph.add_edge("deliver_with_warning", "delivery")

    # ── Post-delivery: knowledge_diff + video ──
    graph.add_edge("delivery", "knowledge_diff")
    graph.add_edge("delivery", "video")

    # ── Terminal nodes ──
    graph.add_edge("knowledge_diff", END)
    graph.add_edge("video", END)
    graph.add_edge("abort", END)

    return graph


# ── Compile the pipeline ──
pipeline = build_pipeline().compile()


def run_pipeline(
    topic: str,
    persona: str = "General",
    language: str = "en",
    knowledge_session_id: str = "",
    custom_persona: str = "",
) -> dict:
    """
    Run the full NewsGPT pipeline with all 11 agents.

    Args:
        topic: News topic to analyze
        persona: User persona (Student/Investor/Beginner/General/CFO/FirstGen)
        language: Target language code
        knowledge_session_id: Session ID for knowledge state tracking
        custom_persona: Free-text custom persona description

    Returns:
        Final pipeline state with briefing, entities, conflicts, video, and audit trail
    """
    initial_state = create_initial_state(
        topic=topic,
        persona=persona,
        language=language,
        knowledge_session_id=knowledge_session_id,
        custom_persona=custom_persona,
    )

    result = pipeline.invoke(initial_state)
    return dict(result)
