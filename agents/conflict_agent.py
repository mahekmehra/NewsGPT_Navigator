"""
NewsGPT Navigator — Conflict Detection Agent

Detects factual, interpretive, and predictive conflicts
across multiple news articles covering the same topic.
"""

import json
from core.safe_json import safe_json_parse
from datetime import datetime, timezone
from agents.state import PipelineState


def conflict_agent(state: PipelineState) -> dict:
    """
    Narrative conflict agent node for the LangGraph pipeline.

    UNIQUE AGENT — Detects disagreements across articles:
    - Factual conflicts: different numbers, dates, claims
    - Interpretive conflicts: different framings of same event
    - Predictive conflicts: different forecasts about outcomes
    """
    from core.llm_router import call_llm

    verified_articles = state.get("verified_articles", [])
    analysis = state.get("analysis", {})
    topic = state.get("topic", "")
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = {
        "timestamp": timestamp,
        "agent": "conflict",
        "action": "detect_narrative_conflicts",
        "inputs": {"topic": topic, "article_count": len(verified_articles)},
        "outputs": {},
    }

    try:
        if len(verified_articles) < 2:
            audit_entry["outputs"] = {"info": "Need at least 2 articles for conflict detection"}
            return {
                "conflicts": [],
                "conflicts_detected": False,
                "current_agent": "conflict",
                "audit_trail": [audit_entry],
            }

        # Build article pairs text for conflict detection
        articles_text = ""
        for i, art in enumerate(verified_articles[:10]):  # Cap at 10 articles
            title = art.get("title", "")
            content = art.get("content", "") or art.get("description", "")
            source = art.get("source", "Unknown")
            articles_text += f"\n--- Article {i+1} (Source: {source}): {title} ---\n{content[:500]}\n"

        conflict_prompt = f"""Analyze these news articles about "{topic}" and identify where they DISAGREE with each other.

Look for three types of conflicts:
1. FACTUAL: Different numbers, dates, or stated facts
2. INTERPRETIVE: Different framings or explanations of the same event
3. PREDICTIVE: Different forecasts about what will happen next

ARTICLES:
{articles_text[:4000]}

For each conflict found, identify:
- The type (factual/interpretive/predictive)
- The specific claim from Article A and its source
- The contradicting claim from Article B and its source
- The entity or topic at the center of the conflict
- Severity (high/medium/low)
- Brief explanation of the disagreement

Respond in this exact JSON format:
{{
    "conflicts": [
        {{
            "conflict_type": "factual",
            "claim_a": "The investment totals $1.2 billion",
            "source_a": "Reuters (Article 1)",
            "claim_b": "The investment is approximately $800 million",
            "source_b": "Bloomberg (Article 3)",
            "entity": "AI Mission Budget",
            "severity": "high",
            "explanation": "The two sources disagree on the total investment amount by $400 million."
        }}
    ]
}}

If no conflicts are found, return {{"conflicts": []}}"""

        response = call_llm(
            prompt=conflict_prompt,
            system_prompt="You are a precise fact-checker and narrative analyst. Detect genuine disagreements, not just different emphases. Always respond in valid JSON.",
            complexity="complex",
        )

        # Parse response (resilient)
        data = safe_json_parse(response, {"conflicts": []})
        raw_conflicts = data.get("conflicts", [])

        # Build ConflictItem list
        conflicts = []
        for conf in raw_conflicts:
            conflicts.append({
                "conflict_type": conf.get("conflict_type", "interpretive"),
                "claim_a": conf.get("claim_a", ""),
                "source_a": conf.get("source_a", ""),
                "claim_b": conf.get("claim_b", ""),
                "source_b": conf.get("source_b", ""),
                "entity": conf.get("entity", ""),
                "severity": conf.get("severity", "medium"),
                "explanation": conf.get("explanation", ""),
            })

        audit_entry["outputs"] = {
            "conflicts_found": len(conflicts),
            "factual": sum(1 for c in conflicts if c["conflict_type"] == "factual"),
            "interpretive": sum(1 for c in conflicts if c["conflict_type"] == "interpretive"),
            "predictive": sum(1 for c in conflicts if c["conflict_type"] == "predictive"),
        }

        return {
            "conflicts": conflicts,
            "conflicts_detected": len(conflicts) > 0,
            "current_agent": "conflict",
            "error": "",
            "audit_trail": [audit_entry],
        }

    except Exception as e:
        audit_entry["outputs"] = {"error": str(e)}
        return {
            "conflicts": [],
            "conflicts_detected": False,
            "current_agent": "conflict",
            "error": f"Conflict agent error: {e}",
            "audit_trail": [audit_entry],
        }
