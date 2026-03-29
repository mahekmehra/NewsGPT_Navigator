"""
NewsGPT Navigator — Orchestrator (LangGraph StateGraph)

Builds the directed acyclic graph that connects all 10 agents,
manages conditional retry/abort edges, and exposes a single
`run_pipeline()` entry point that drives the full analysis flow.
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
from agents.video_agent import video_agent
from core.config import settings


# ── Conditional Edge Functions ──────────────────────────────────────

def should_retry_fetch(state: PipelineState) -> str:
    """Decide whether to retry fetch, proceed, or abort."""
    fetch_success = state.get("fetch_success", False)
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", settings.MAX_RETRIES)

    if not fetch_success and retry_count < max_retries:
        return "retry_fetch"
    elif not fetch_success:
        return "abort"
    return "entity_sentiment"


def should_retry_analysis(state: PipelineState) -> str:
    """Decide whether to re-analyze, proceed, or deliver with warning."""
    compliance_passed = state.get("compliance_passed", False)
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", settings.MAX_RETRIES)

    if not compliance_passed and retry_count < max_retries:
        return "reanalyze"
    elif not compliance_passed:
        return "deliver_with_warning"
    return "profile_ranking"


# ── Control-Flow Nodes ──────────────────────────────────────────────

def retry_fetch_node(state: PipelineState) -> dict:
    """Increment retry counter before looping back to fetch."""
    return {
        "retry_count": state.get("retry_count", 0) + 1,
        "current_agent": "orchestrator",
    }


def reanalyze_node(state: PipelineState) -> dict:
    """Increment retry counter before looping back to analysis."""
    return {
        "retry_count": state.get("retry_count", 0) + 1,
        "current_agent": "orchestrator",
    }


def abort_node(state: PipelineState) -> dict:
    """Terminate the pipeline after exhausting retries."""
    return {
        "pipeline_status": "failed",
        "current_agent": "orchestrator",
        "error": "Pipeline aborted: max retries exhausted",
    }


def deliver_with_warning_node(state: PipelineState) -> dict:
    """Continue to delivery despite compliance failure (with warning flag)."""
    return {
        "current_agent": "orchestrator",
    }


# ── Graph Construction ──────────────────────────────────────────────

def build_pipeline() -> StateGraph:
    """
    Build the 10-agent LangGraph pipeline.

    Flow:
        Fetch → Entity/Sentiment → Angle → Analysis → Compliance
        → Profile/Ranking → Conflict → Emotion → Video → Delivery
    """
    graph = StateGraph(PipelineState)

    # Register agent nodes
    graph.add_node("fetch", fetch_agent)
    graph.add_node("retry_fetch", retry_fetch_node)
    graph.add_node("entity_sentiment", entity_sentiment_agent)
    graph.add_node("angle", angle_agent)
    graph.add_node("analysis", analysis_agent)
    graph.add_node("compliance", compliance_agent)
    graph.add_node("reanalyze", reanalyze_node)
    graph.add_node("profile_ranking", profile_ranking_agent)
    graph.add_node("conflict", conflict_agent)
    graph.add_node("emotion", emotional_agent)
    graph.add_node("delivery", delivery_agent)
    graph.add_node("video", video_agent)
    graph.add_node("deliver_with_warning", deliver_with_warning_node)
    graph.add_node("abort", abort_node)

    # Entry point
    graph.set_entry_point("fetch")

    # Fetch → retry / entity_sentiment / abort
    graph.add_conditional_edges(
        "fetch",
        should_retry_fetch,
        {
            "retry_fetch": "retry_fetch",
            "entity_sentiment": "entity_sentiment",
            "abort": "abort",
        }
    )
    graph.add_edge("retry_fetch", "fetch")

    # Enrichment phase
    graph.add_edge("entity_sentiment", "angle")

    # Analysis phase
    graph.add_edge("angle", "analysis")
    graph.add_edge("analysis", "compliance")

    # Compliance → reanalyze / profile_ranking / deliver_with_warning
    graph.add_conditional_edges(
        "compliance",
        should_retry_analysis,
        {
            "reanalyze": "reanalyze",
            "profile_ranking": "profile_ranking",
            "deliver_with_warning": "deliver_with_warning",
        }
    )
    graph.add_edge("reanalyze", "analysis")

    # Personalization phase
    graph.add_edge("profile_ranking", "conflict")
    graph.add_edge("conflict", "emotion")

    # Delivery phase
    graph.add_edge("emotion", "video")
    graph.add_edge("deliver_with_warning", "video")
    graph.add_edge("video", "delivery")

    # Terminal edges
    graph.add_edge("delivery", END)
    graph.add_edge("abort", END)

    return graph


# Compile the graph once at module load
pipeline = build_pipeline().compile()


def run_pipeline(
    topic: str,
    persona: str = "General",
    language: str = "en",
    knowledge_session_id: str = "",
    custom_persona: str = "",
) -> dict:
    """
    Execute the full 10-agent pipeline for a given topic.

    Args:
        topic: News topic to analyze
        persona: Persona preset name
        language: Target language code
        knowledge_session_id: Session ID for story arc persistence
        custom_persona: Free-text persona description

    Returns:
        Complete pipeline state as a dict
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
