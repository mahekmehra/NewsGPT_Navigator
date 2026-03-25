"""
NewsGPT Navigator — Delivery Agent

Reformats analysis output based on persona, translates to
target language, builds final JSON payload, and appends
complete audit trail entry.
"""

from datetime import datetime, timezone
from agents.state import PipelineState
from core.config import settings


def _format_for_persona(analysis: dict, persona: str) -> str:
    """Reformat the analysis briefing based on user persona."""
    summary = analysis.get("summary", "")
    prediction = analysis.get("prediction", "")
    timeline = analysis.get("timeline", [])
    entities = analysis.get("key_entities", [])

    if persona == "Student":
        briefing = f"""📚 **News Briefing for Students**

**What's happening?**
{summary}

**Key Players:**
{', '.join(entities[:5]) if entities else 'Various stakeholders'}

**Timeline of Events:**
"""
        for event in timeline[:5]:
            briefing += f"• {event.get('date', 'N/A')}: {event.get('event', '')}\n"
        briefing += f"\n**What could happen next?**\n{prediction}"

    elif persona == "Investor":
        briefing = f"""📊 **Market Intelligence Brief**

**Executive Summary:**
{summary}

**Key Entities & Stakeholders:**
{', '.join(entities[:8]) if entities else 'Multiple market participants'}

**Sentiment:** {analysis.get('sentiment', 'N/A')}

**Event Timeline:**
"""
        for event in timeline[:7]:
            briefing += f"• [{event.get('date', 'N/A')}] {event.get('event', '')}\n"
        briefing += f"\n**Forward Outlook:**\n{prediction}"

    elif persona == "Beginner":
        briefing = f"""🌟 **Simple News Explanation**

**In Simple Words:**
{summary}

**People & Groups Involved:**
{', '.join(entities[:4]) if entities else 'Various people and organizations'}

**What Happened When:**
"""
        for event in timeline[:4]:
            briefing += f"• {event.get('date', 'N/A')}: {event.get('event', '')}\n"
        briefing += f"\n**What Might Happen Next:**\n{prediction}"

    else:  # General
        briefing = f"""📰 **News Intelligence Briefing**

**Summary:**
{summary}

**Key Entities:**
{', '.join(entities[:6]) if entities else 'Multiple stakeholders'}

**Sentiment:** {analysis.get('sentiment', 'N/A')}

**Timeline:**
"""
        for event in timeline[:6]:
            briefing += f"• {event.get('date', 'N/A')}: {event.get('event', '')}\n"
        briefing += f"\n**Prediction:**\n{prediction}"

    return briefing


def delivery_agent(state: PipelineState) -> dict:
    """
    Delivery agent node for the LangGraph pipeline.

    - Reformats output by persona
    - Translates to target language
    - Builds final JSON payload
    - Appends complete audit entry
    """
    from core.translator import translate_text

    analysis = state.get("analysis", {})
    persona = state.get("persona", settings.DEFAULT_PERSONA)
    language = state.get("language", settings.DEFAULT_LANGUAGE)
    topic = state.get("topic", "")
    bias_score = state.get("bias_score", 0.0)
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = {
        "timestamp": timestamp,
        "agent": "delivery",
        "action": "format_and_deliver",
        "inputs": {"persona": persona, "language": language},
        "outputs": {},
    }

    try:
        # Format for persona
        detailed_briefing = _format_for_persona(analysis, persona)

        # Translate if needed
        translated_summary = ""
        if language != "en":
            translated_summary = translate_text(
                analysis.get("summary", ""), language
            )

        # Build sources list
        sources = [
            {
                "title": s.get("title", ""),
                "source": s.get("source", ""),
                "url": s.get("url", ""),
            }
            for s in analysis.get("sources_used", [])
        ]

        # Build final briefing payload
        briefing = {
            "title": f"Intelligence Briefing: {topic}",
            "summary": analysis.get("summary", ""),
            "detailed_briefing": detailed_briefing,
            "timeline": analysis.get("timeline", []),
            "prediction": analysis.get("prediction", ""),
            "key_entities": analysis.get("key_entities", []),
            "sentiment": analysis.get("sentiment", "neutral"),
            "sources": sources,
            "persona": persona,
            "language": language,
            "translated_summary": translated_summary,
            "bias_score": bias_score,
            "compliance_status": "passed",
            "model_used": analysis.get("model_used", "unknown"),
            "complexity_class": analysis.get("complexity_class", "unknown"),
            "generated_at": timestamp,
        }

        audit_entry["outputs"] = {
            "briefing_length": len(detailed_briefing),
            "translated": language != "en",
            "persona": persona,
            "sources_count": len(sources),
        }

        return {
            "briefing": briefing,
            "current_agent": "delivery",
            "pipeline_status": "completed",
            "error": "",
            "audit_trail": [audit_entry],
        }

    except Exception as e:
        audit_entry["outputs"] = {"error": str(e)}
        return {
            "briefing": {},
            "current_agent": "delivery",
            "pipeline_status": "failed",
            "error": f"Delivery agent error: {e}",
            "audit_trail": [audit_entry],
        }
