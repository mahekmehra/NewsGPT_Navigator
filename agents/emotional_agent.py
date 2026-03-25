"""
NewsGPT Navigator — Emotional Calibration Agent (UNIQUE)

Detects crisis/opportunity/uncertainty register.
Calibrates tone for video + vernacular delivery.
"""

import json
from core.safe_json import safe_json_parse
from datetime import datetime, timezone
from agents.state import PipelineState


def emotional_agent(state: PipelineState) -> dict:
    """
    Emotional calibration agent node for the LangGraph pipeline.

    UNIQUE AGENT — Detects the emotional register of the news:
    - Crisis: urgent, alarming, negative impact
    - Opportunity: positive developments, growth potential
    - Uncertainty: ambiguous outcomes, conflicting signals
    - Neutral: routine updates, no strong emotional charge

    Measures intensity and generates tone guidance for downstream agents.
    """
    from core.llm_router import call_llm

    analysis = state.get("analysis", {})
    entity_sentiments = state.get("entity_sentiments", [])
    conflicts = state.get("conflicts", [])
    topic = state.get("topic", "")
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = {
        "timestamp": timestamp,
        "agent": "emotional_calibration",
        "action": "calibrate_emotional_register",
        "inputs": {"topic": topic},
        "outputs": {},
    }

    try:
        summary = analysis.get("summary", "")
        prediction = analysis.get("prediction", "")
        sentiment = analysis.get("sentiment", "neutral")

        # Build context for emotional analysis
        conflict_summary = ""
        if conflicts:
            conflict_texts = [f"- {c.get('explanation', '')}" for c in conflicts[:5]]
            conflict_summary = f"\nCONFLICTS DETECTED:\n" + "\n".join(conflict_texts)

        sentiment_summary = ""
        if entity_sentiments:
            pos = sum(1 for e in entity_sentiments if e.get("sentiment") == "positive")
            neg = sum(1 for e in entity_sentiments if e.get("sentiment") == "negative")
            sentiment_summary = f"\nENTITY SENTIMENT: {pos} positive, {neg} negative entities"

        calibration_prompt = f"""Analyze the emotional register of this news coverage about "{topic}".

SUMMARY:
{summary[:2000]}

PREDICTION:
{prediction[:500]}

OVERALL SENTIMENT: {sentiment}
{conflict_summary}
{sentiment_summary}

Determine:
1. The dominant emotional register: crisis / opportunity / uncertainty / neutral
2. Intensity (0.0 to 1.0) — how strongly this register is felt
3. Specific signals that indicate this register
4. Tone guidance for how a presenter should deliver this news

Respond in this exact JSON format:
{{
    "register": "opportunity",
    "intensity": 0.7,
    "tone_guidance": "Emphasize the positive developments while noting cautionary elements. Use an optimistic but measured tone.",
    "crisis_signals": [],
    "opportunity_signals": ["major investment announced", "positive market response"],
    "uncertainty_signals": ["implementation timeline unclear"]
}}"""

        response = call_llm(
            prompt=calibration_prompt,
            system_prompt="You are an emotional intelligence analyst for news media. Detect the emotional register accurately. Always respond in valid JSON.",
            complexity="simple",
        )

        # Parse response (resilient)
        emotional_fallback = {
            "register": "neutral",
            "intensity": 0.3,
            "tone_guidance": "Deliver in a balanced, informative tone.",
            "crisis_signals": [],
            "opportunity_signals": [],
            "uncertainty_signals": [],
        }
        emotional_data = safe_json_parse(response, emotional_fallback)

        emotional_register = {
            "register": emotional_data.get("register", "neutral"),
            "intensity": float(emotional_data.get("intensity", 0.3)),
            "tone_guidance": emotional_data.get("tone_guidance", ""),
            "crisis_signals": emotional_data.get("crisis_signals", []),
            "opportunity_signals": emotional_data.get("opportunity_signals", []),
            "uncertainty_signals": emotional_data.get("uncertainty_signals", []),
        }

        audit_entry["outputs"] = {
            "register": emotional_register["register"],
            "intensity": emotional_register["intensity"],
        }

        return {
            "emotional_register": emotional_register,
            "emotion_calibrated": True,
            "current_agent": "emotional_calibration",
            "error": "",
            "audit_trail": [audit_entry],
        }

    except Exception as e:
        audit_entry["outputs"] = {"error": str(e)}
        return {
            "emotional_register": {},
            "emotion_calibrated": False,
            "current_agent": "emotional_calibration",
            "error": f"Emotional calibration agent error: {e}",
            "audit_trail": [audit_entry],
        }
