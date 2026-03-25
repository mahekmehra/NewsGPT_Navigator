"""
NewsGPT Navigator — Compliance + Bias Agent

Scans LLM outputs for bias signals, political skew,
unverified sensational claims, and source credibility issues.
Assigns bias_score (0-1). Threshold = 0.3 by default.
"""

import re
from datetime import datetime, timezone
from agents.state import PipelineState
from core.config import settings


# ── Bias detection patterns ──
SENSATIONAL_WORDS = [
    "shocking", "breaking", "explosive", "bombshell", "devastating",
    "unprecedented", "catastrophic", "incredible", "unbelievable",
    "massive", "stunning", "outrageous", "alarming", "terrifying",
    "horrifying", "jaw-dropping", "mind-blowing", "earth-shattering",
]

POLITICAL_BIAS_LEFT = [
    "progressive victory", "right-wing extremism", "conservative failure",
    "far-right", "bigotry", "systemic oppression",
]

POLITICAL_BIAS_RIGHT = [
    "liberal agenda", "left-wing extremism", "socialist failure",
    "far-left", "woke ideology", "radical left",
]

UNVERIFIED_PHRASES = [
    "sources say", "reportedly", "allegedly", "rumored",
    "unconfirmed reports", "some believe", "it is said that",
    "anonymous sources", "insider claims",
]


def _count_pattern_matches(text: str, patterns: list[str]) -> int:
    """Count how many patterns appear in the text."""
    text_lower = text.lower()
    return sum(1 for p in patterns if p.lower() in text_lower)


def _calculate_bias_score(text: str) -> dict:
    """
    Calculate a detailed bias score for a text.

    Returns:
        dict with component scores and overall bias_score
    """
    text_lower = text.lower()
    word_count = max(len(text.split()), 1)

    # Sensationalism (0-1)
    sensational_count = _count_pattern_matches(text, SENSATIONAL_WORDS)
    sensationalism = min(sensational_count / 5, 1.0)

    # Political bias (0-1)
    left_count = _count_pattern_matches(text, POLITICAL_BIAS_LEFT)
    right_count = _count_pattern_matches(text, POLITICAL_BIAS_RIGHT)
    political_skew = min((left_count + right_count) / 3, 1.0)

    # One-sided check: if only one side is present, increase score
    if (left_count > 0 and right_count == 0) or (right_count > 0 and left_count == 0):
        political_skew = min(political_skew + 0.2, 1.0)

    # Unverified claims (0-1)
    unverified_count = _count_pattern_matches(text, UNVERIFIED_PHRASES)
    unverified_score = min(unverified_count / 4, 1.0)

    # Source diversity check: look for attribution patterns
    attribution_patterns = [r"according to", r"stated that", r"said\b", r"reported by"]
    attribution_count = sum(
        len(re.findall(p, text_lower)) for p in attribution_patterns
    )
    # More attributions = likely more balanced
    attribution_bonus = min(attribution_count * 0.05, 0.15)

    # Overall bias score (weighted average)
    raw_score = (
        sensationalism * 0.35
        + political_skew * 0.35
        + unverified_score * 0.30
    )

    # Apply attribution bonus (reduces score if well-sourced)
    final_score = max(raw_score - attribution_bonus, 0.0)

    return {
        "bias_score": round(final_score, 3),
        "sensationalism": round(sensationalism, 3),
        "political_skew": round(political_skew, 3),
        "unverified_claims": round(unverified_score, 3),
        "attribution_count": attribution_count,
        "flagged_terms": {
            "sensational": [w for w in SENSATIONAL_WORDS if w.lower() in text_lower],
            "political_left": [w for w in POLITICAL_BIAS_LEFT if w.lower() in text_lower],
            "political_right": [w for w in POLITICAL_BIAS_RIGHT if w.lower() in text_lower],
            "unverified": [w for w in UNVERIFIED_PHRASES if w.lower() in text_lower],
        },
    }


def compliance_agent(state: PipelineState) -> dict:
    """
    Compliance agent node for the LangGraph pipeline.

    - Scans analysis output for bias signals
    - Calculates bias_score (0-1)
    - Sets compliance_passed based on threshold
    - If score > threshold → orchestrator loops back to analysis
    """
    analysis = state.get("analysis", {})
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = {
        "timestamp": timestamp,
        "agent": "compliance",
        "action": "bias_check",
        "inputs": {"threshold": settings.BIAS_THRESHOLD},
        "outputs": {},
    }

    try:
        # Combine all text outputs for scanning
        text_to_scan = " ".join([
            analysis.get("summary", ""),
            analysis.get("prediction", ""),
            " ".join(str(e) for e in analysis.get("key_entities", [])),
        ])

        if not text_to_scan.strip():
            audit_entry["outputs"] = {"error": "No analysis text to scan"}
            return {
                "bias_score": 0.0,
                "bias_details": {},
                "compliance_passed": False,
                "current_agent": "compliance",
                "error": "No analysis output to check",
                "audit_trail": [audit_entry],
            }

        # Calculate bias score
        bias_details = _calculate_bias_score(text_to_scan)
        bias_score = bias_details["bias_score"]
        compliance_passed = bias_score <= settings.BIAS_THRESHOLD

        audit_entry["outputs"] = {
            "bias_score": bias_score,
            "compliance_passed": compliance_passed,
            "sensationalism": bias_details["sensationalism"],
            "political_skew": bias_details["political_skew"],
            "unverified_claims": bias_details["unverified_claims"],
        }

        return {
            "bias_score": bias_score,
            "bias_details": bias_details,
            "compliance_passed": compliance_passed,
            "current_agent": "compliance",
            "error": "",
            "audit_trail": [audit_entry],
        }

    except Exception as e:
        audit_entry["outputs"] = {"error": str(e)}
        return {
            "bias_score": 1.0,
            "bias_details": {},
            "compliance_passed": False,
            "current_agent": "compliance",
            "error": f"Compliance agent error: {e}",
            "audit_trail": [audit_entry],
        }
