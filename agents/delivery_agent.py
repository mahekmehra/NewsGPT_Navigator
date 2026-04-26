"""
NewsGPT Navigator — Delivery Agent

Assembles the final briefing payload: generates a persona-specific
brief via LLM, applies multilingual translation, builds an audio
narration script (gTTS), and structures all outputs for the API.
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

def _format_for_persona_llm(analysis: dict, persona: str, conflicts: list, source_quality: str, language: str = "en") -> dict:
    """Use LLM to generate a truly custom persona brief with conflict resolution."""
    from core.llm_router import call_llm
    import json
    
    summary = analysis.get("summary", "")
    prediction = analysis.get("prediction", "")
    entities = analysis.get("key_entities", [])
    
    persona_prompt = settings.PERSONA_PROMPTS.get(persona, settings.PERSONA_PROMPTS["General"])
    
    conflicts_text = "None"
    if conflicts:
        conflicts_text = json.dumps(conflicts[:3], indent=2)
    
    prompt = f"""
    You are an advanced AI news intelligence system producing a reliable, structured, and decision-useful briefing.
    
    TARGET LANGUAGE: {language}
    You MUST respond in {language}. Use the NATIVE script for {language} (e.g. Gurmukhi for Punjabi, Devanagari for Hindi, Arabic script for Urdu, Hanzi for Chinese, etc.). 
    DO NOT use Romanized transliteration. All text fields in the JSON must be in the native script of {language}.

    PERSONA GUIDANCE: {persona_prompt}
    
    RAW DATA:
    Summary: {summary}
    Prediction: {prediction}
    Key Entities: {", ".join(entities[:10])}
    Source Quality context: {source_quality}
    Conflicts detected: {conflicts_text}
    
    INSTRUCTIONS - STRICTLY RULES:
    1. CONFLICT RESOLUTION: If conflicts exist, identify the most credible version and explain why. Output this in "final_assessment". If no conflicts, just provide a definitive synthesis.
    2. REASONING LAYER: For every major insight, clearly convey why this matters, what could happen next logically, and the impact.
    3. PERSONALIZATION: Strongly adapt the tone and depth based on the persona.
    4. CONFIDENCE: Provide a numeric or descriptive confidence_score based on the source quality.
    
    Respond STRICTLY in JSON with these exact keys. Do NOT hallucinate data if absent:
    {{
        "headline": "Persona-specific title",
        "summary": "Persona-tailored synthesis in {language} (native script).",
        "key_points": ["Point 1", "Point 2"],
        "final_assessment": "Most likely truth based on evidence is...",
        "confidence_score": "e.g. 85% or High",
        "risks": ["Risk 1", "Risk 2"],
        "next_steps": ["Action 1", "Action 2"],
        "source_quality_summary": "{source_quality}",
        "insights": ["Insight with impact context"]
    }}
    """
    
    response = call_llm(
        prompt=prompt,
        system_prompt=f"You are a specialized intelligence curator for a {persona}. Respond strictly in {language} JSON using its native script.",
        complexity="power"
    )
    
    from core.safe_json import safe_json_parse
    pb = safe_json_parse(response, {
        "headline": f"Intelligence for {persona}",
        "summary": summary[:200],
        "key_points": entities[:4],
        "final_assessment": prediction,
        "confidence_score": "Unknown",
        "risks": [],
        "next_steps": [],
        "source_quality_summary": source_quality,
        "insights": []
    })
    
    return pb


def _generate_audio(script_text: str, topic: str, lang: str = "en") -> str:
    """Generate audio file and return relative URL."""
    try:
        from gtts import gTTS
        import uuid

        # Ensure text is not empty
        if not script_text:
            return ""

        filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
        file_path = os.path.join(AUDIO_OUTPUT_DIR, filename)

        # Map language codes if necessary (gTTS uses standard ISO)
        tts = gTTS(text=script_text, lang=lang)
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
        "inputs": {"persona": persona, "language": language},
        "outputs": {},
    }

    try:
        # 1. Generate Persona-Specific Brief (LLM Powered with Language Support)
        conflicts = state.get("conflicts", [])
        source_quality = state.get("source_quality_summary", "Standard source validation applied.")
        persona_brief = _format_for_persona_llm(analysis, persona, conflicts, source_quality, language=language)
        
        # 2. Structure Angles and Follow-ups
        angles = _generate_angles(analysis)
        followups = _generate_followups(topic)
        prediction = analysis.get("prediction", "")
        summary = analysis.get("summary", "")

        # 3. Multilingual Support (Fallback for non-LLM fields)
        if language != "en":
            # Translate follow-ups
            followups = [translate_text(f, language) for f in followups]
            
            # Note: summary, prediction, and persona_brief are already generated in the target language by analysis_agent and _format_for_persona_llm

        # 4. Final Data Mapping
        sources = [
            {
                "title": s.get("title", ""),
                "source": s.get("source", ""),
                "url": s.get("url", ""),
            }
            for s in analysis.get("sources_used", [])
        ]

        # Audio narration script
        entities_text = ", ".join(analysis.get('key_entities', [])[:5])
        
        # Determine labels based on language
        labels = {
            "en": {
                "intro": f"Intelligence Briefing regarding {topic}.",
                "summary": "General Summary:",
                "entities": "Key entities involved include:",
                "insight": f"Insight for {persona}:",
                "takeaway": "Strategic Takeaway:",
                "prediction": "Prediction and Future Outlook:",
                "outro": "End of briefing."
            },
            "hi": {
                "intro": f"{topic} के संबंध में खुफिया जानकारी।",
                "summary": "सामान्य सारांश:",
                "entities": "शामिल प्रमुख इकाइयां:",
                "insight": f"{persona} के लिए जानकारी:",
                "takeaway": "रणनीतिक निष्कर्ष:",
                "prediction": "भविष्यवाणी:",
                "outro": "ब्रीफिंग समाप्त।"
            },
            "pa": {
                "intro": f"{topic} ਦੇ ਸਬੰਧ ਵਿੱਚ ਖੁਫੀਆ ਜਾਣਕਾਰੀ।",
                "summary": "ਆਮ ਸੰਖੇਪ:",
                "entities": "ਸ਼ਾਮਲ ਮੁੱਖ ਇਕਾਈਆਂ:",
                "insight": f"{persona} ਲਈ ਜਾਣਕਾਰੀ:",
                "takeaway": "ਰਣਨੀਤਕ ਸਿੱਟਾ:",
                "prediction": "ਭਵਿੱਖਬਾਣੀ:",
                "outro": "ਬ੍ਰੀਫਿੰਗ ਸਮਾਪਤ।"
            }
        }
        
        l = labels.get(language, labels["en"])
        
        audio_script = f"""
        {l['intro']}
        
        {l['summary']} {summary}.
        
        {l['entities']} {entities_text}.
        
        {l['insight']} {persona_brief.get('summary', '')}.
        
        {l['takeaway']} {persona_brief.get('final_assessment', '')}.
        
        {l['prediction']} {prediction}.
        
        {l['outro']}
        """
        audio_url = _generate_audio(audio_script, topic, lang=language)

        briefing = {
            "title": f"Intelligence Briefing: {topic}",
            "summary": summary,
            "persona": persona,
            "language": language,

            "persona_brief": persona_brief,
            "angles": angles,
            "follow_up_questions": followups,
            "timeline": analysis.get("timeline", []),
            "prediction": prediction,

            "key_entities": analysis.get("key_entities", [])[:10],
            "entities_metadata": analysis.get("entities_metadata", []),
            "sentiment": analysis.get("sentiment", "neutral"),
            "sources": sources[:5],
            "bias_score": bias_score,
            "compliance_status": "Passed" if state.get("compliance_passed") else "Caution",

            "model_used": analysis.get("model_used", "Llama-3"),
            "complexity_class": analysis.get("complexity_class", "Standard"),
            "generated_at": timestamp,

            "videos": state.get("videos", []),
            "audio_url": audio_url,
        }

        audit_entry["outputs"] = {
            "audio_generated": bool(audio_url),
            "videos_count": len(state.get("videos", [])),
            "persona_brief": persona_brief,
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
        import traceback
        print(f"[DeliveryAgent] Critical Error: {e}")
        traceback.print_exc()
        return {
            "briefing": {},
            "pipeline_status": "failed",
            "error": str(e),
            "audit_trail": [audit_entry],
        }