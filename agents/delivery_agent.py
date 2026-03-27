"""
NewsGPT Navigator — Delivery Agent

Reformats analysis output based on persona, translates to
target language, builds final JSON payload, and appends
complete audit trail entry.
"""
from datetime import datetime, timezone
from agents.state import PipelineState
from core.config import settings
import os
import time

# Audio output directory
AUDIO_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "audio_output"
)
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)


def _generate_angles(analysis: dict) -> dict:
    return {
        "market_impact": analysis.get("market_impact", ""),
        "expert_opinion": analysis.get("expert_opinion", ""),
        "risks": analysis.get("risks", ""),
        "opportunities": analysis.get("opportunities", ""),
    }


def _generate_followups(topic: str) -> list:
    return [
        f"What does this mean for different sectors in {topic}?",
        f"Who are the biggest winners and losers in {topic}?",
        f"What should investors watch next regarding {topic}?",
        f"How will this impact the economy in the long term?",
    ]


def _format_for_persona(analysis: dict, persona: str) -> dict:
    summary = analysis.get("concise_summary") or analysis.get("summary", "")[:200]
    prediction = analysis.get("prediction", "")
    entities = analysis.get("key_entities", [])
    sentiment = analysis.get("sentiment", "neutral")

    if persona == "Student":
        return {
            "headline": "📚 Student-Friendly Brief",
            "summary": summary,
            "key_points": entities[:5],
            "explanation": "This topic helps you understand real-world systems.",
            "what_next": prediction,
        }

    elif persona == "Investor":
        return {
            "headline": "📊 Investor Intelligence",
            "summary": summary,
            "key_entities": entities[:8],
            "sentiment": sentiment,
            "actionable_insight": prediction,
        }

    elif persona == "CFO":
        return {
            "headline": "📈 Executive Briefing (CFO)",
            "summary": summary,
            "key_entities": entities[:10],
            "strategic_implication": prediction,
            "sentiment": sentiment,
        }

    elif persona == "Beginner":
        return {
            "headline": "🌟 Simple Explanation",
            "summary": summary,
            "key_entities": entities[:4],
            "explanation": "Explained in simple terms.",
            "what_next": prediction,
        }

    else:
        return {
            "headline": "📰 General Brief",
            "summary": summary,
            "key_entities": entities[:6],
            "sentiment": sentiment,
            "what_next": prediction,
        }


def _generate_audio(summary_text: str, topic: str) -> str:
    """Generate audio file and return relative URL."""
    try:
        from gtts import gTTS
        import uuid

        # Ensure text is not empty
        if not summary_text:
            return ""

        filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
        file_path = os.path.join(AUDIO_OUTPUT_DIR, filename)

        tts = gTTS(text=summary_text, lang="en")
        tts.save(file_path)

        # Return the URL path that the backend serves
        return f"/audio/{filename}"
    except Exception as e:
        print(f"[DeliveryAgent] Audio Error: {e}")
        return ""


def delivery_agent(state: PipelineState) -> dict:
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
        "action": "interactive_briefing_generation",
        "inputs": {"persona": persona},
        "outputs": {},
    }

    try:
        persona_brief = _format_for_persona(analysis, persona)
        angles = _generate_angles(analysis)
        followups = _generate_followups(topic)

        # Translation
        translated_summary = ""
        if language != "en":
            translated_summary = translate_text(
                analysis.get("summary", ""), language
            )

        # Sources
        sources = [
            {
                "title": s.get("title", ""),
                "source": s.get("source", ""),
                "url": s.get("url", ""),
            }
            for s in analysis.get("sources_used", [])
        ]

        # 🔊 AUDIO GENERATION (Using Concise Summary for better UX)
        audio_text = analysis.get("concise_summary") or analysis.get("summary", "")
        audio_url = _generate_audio(audio_text, topic)

        # Final briefing (Fully Aligned with BriefingResponse)
        briefing = {
            "title": f"Intelligence Briefing: {topic}",
            "summary": analysis.get("summary", ""),
            "persona": persona,
            "language": language,

            "persona_brief": persona_brief,
            "angles": angles,
            "follow_up_questions": followups,
            "timeline": analysis.get("timeline", []),
            "prediction": analysis.get("prediction", ""),

            "key_entities": analysis.get("key_entities", [])[:10],
            "sentiment": analysis.get("sentiment", "neutral"),
            "sources": sources[:5],  # Limit to top 5
            "translated_summary": translated_summary,
            "bias_score": bias_score,
            "compliance_status": "Passed" if state.get("compliance_passed") else "Caution",

            "model_used": analysis.get("model_used", "Llama-3"),
            "complexity_class": analysis.get("complexity_class", "Standard"),
            "generated_at": timestamp,

            "videos": state.get("videos", []), # Now available because video agent runs before
            "audio_url": audio_url,
        }

        audit_entry["outputs"] = {
            "audio_generated": bool(audio_url),
            "videos_count": len(state.get("videos", [])),
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
            "pipeline_status": "failed",
            "error": str(e),
            "audit_trail": [audit_entry],
        }