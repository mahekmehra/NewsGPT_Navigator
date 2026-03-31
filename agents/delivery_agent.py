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


def _format_for_persona_llm(analysis: dict, persona: str, conflicts: list, source_quality: str) -> dict:
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
        "headline": "Persona-specific title (e.g. Market ROI Analysis vs Beginners Guide)",
        "summary": "Persona-tailored synthesis. Use persona-appropriate depth and vocabulary.",
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
        system_prompt=f"You are a specialized intelligence curator for a {persona}. Provide strictly structured JSON output.",
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
        return f"/api/audio/{filename}"
    except Exception as e:
        print(f"[DeliveryAgent] Audio Error: {e}")
        return ""


async def delivery_agent(state: PipelineState) -> dict:
    from core.translator import translate_text, translate_text_async
    import asyncio

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
        # 1. Generate Persona-Specific Brief (LLM Powered)
        conflicts = state.get("conflicts", [])
        source_quality = state.get("source_quality_summary", "Standard source validation applied.")
        persona_brief = _format_for_persona_llm(analysis, persona, conflicts, source_quality)
        
        # 2. Structure Angles and Follow-ups
        angles = _generate_angles(analysis)
        followups = _generate_followups(topic)
        prediction = analysis.get("prediction", "")
        summary = analysis.get("summary", "")

        # 3. Comprehensive Multilingual Support (Parallelized)
        translated_summary = summary
        translated_timeline = analysis.get("timeline", [])
        translated_prediction = prediction

        if language != "en":
            # List of translation tasks
            tasks = []
            
            # Summary & Prediction tasks
            tasks.append(translate_text_async(summary, language))
            tasks.append(translate_text_async(prediction, language))
            
            # Persona brief tasks
            tasks.append(translate_text_async(persona_brief.get("headline", ""), language))
            tasks.append(translate_text_async(persona_brief.get("summary", ""), language))
            tasks.append(translate_text_async(persona_brief.get("final_assessment", ""), language))
            
            p_key_points = persona_brief.get("key_points", [])
            for kp in p_key_points:
                tasks.append(translate_text_async(kp, language))
            
            p_risks = persona_brief.get("risks", [])
            for r in p_risks:
                tasks.append(translate_text_async(r, language))
                
            p_next_steps = persona_brief.get("next_steps", [])
            for ns in p_next_steps:
                tasks.append(translate_text_async(ns, language))
            
            p_insights = persona_brief.get("insights", [])
            for ins in p_insights:
                tasks.append(translate_text_async(ins, language))

            # Angles
            angle_keys = ["market_impact", "expert_opinion", "risks", "opportunities"]
            for ak in angle_keys:
                tasks.append(translate_text_async(angles.get(ak, ""), language))
            
            # Timeline tasks - (Translate each event's text)
            raw_timeline = analysis.get("timeline", [])
            for event in raw_timeline:
                tasks.append(translate_text_async(event.get("event", ""), language))

            # Execute all translations in parallel
            results = await asyncio.gather(*tasks)
            
            # Assign results back (Order is preserved in asyncio.gather)
            res_idx = 0
            translated_summary = results[res_idx]; res_idx += 1
            translated_prediction = results[res_idx]; res_idx += 1
            
            persona_brief["headline"] = results[res_idx]; res_idx += 1
            persona_brief["summary"] = results[res_idx]; res_idx += 1
            persona_brief["final_assessment"] = results[res_idx]; res_idx += 1
            
            if p_key_points:
                persona_brief["key_points"] = results[res_idx:res_idx+len(p_key_points)]
                res_idx += len(p_key_points)
            if p_risks:
                persona_brief["risks"] = results[res_idx:res_idx+len(p_risks)]
                res_idx += len(p_risks)
            if p_next_steps:
                persona_brief["next_steps"] = results[res_idx:res_idx+len(p_next_steps)]
                res_idx += len(p_next_steps)
            if p_insights:
                persona_brief["insights"] = results[res_idx:res_idx+len(p_insights)]
                res_idx += len(p_insights)
            
            for ak in angle_keys:
                angles[ak] = results[res_idx]; res_idx += 1
            
            # Reconstruct translated timeline
            translated_timeline = []
            for event in raw_timeline:
                translated_timeline.append({
                    "date": event.get("date", ""),
                    "event": results[res_idx]
                })
                res_idx += 1

        # 4. Final Data Mapping (including Article connectivity)
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
        
        intro = f"Intelligence Briefing regarding {topic}."
        summary_label = "General Summary:"
        entities_label = "Key entities involved include:"
        insight_label = f"Insight for {persona}:"
        takeaway_label = "Strategic Takeaway:"
        prediction_label = "Prediction and Future Outlook:"
        outro = "End of briefing."
        
        if language == "pa":
            intro = f"{topic} ਦੇ ਸਬੰਧ ਵਿੱਚ ਖੁਫੀਆ ਜਾਣਕਾਰੀ।"
            summary_label = "ਆਮ ਸੰਖੇਪ:"
            entities_label = "ਸ਼ਾਮਲ ਮੁੱਖ ਇਕਾਈਆਂ:"
            insight_label = f"{persona} ਲਈ ਜਾਣਕਾਰੀ:"
            takeaway_label = "ਰਣਨੀਤਕ ਸਿੱਟਾ:"
            prediction_label = "ਭਵਿੱਖਬਾਣੀ:"
            outro = "ਬ੍ਰੀਫਿੰਗ ਸਮਾਪਤ।"
        elif language == "hi":
            intro = f"{topic} के संबंध में खुफिया जानकारी।"
            summary_label = "सामान्य सारांश:"
            entities_label = "शामिल प्रमुख इकाइयां:"
            insight_label = f"{persona} के लिए जानकारी:"
            takeaway_label = "रणनीतिक निष्कर्ष:"
            prediction_label = "भविष्यवाणी:"
            outro = "ब्रीफिंग समाप्त।"

        audio_script = f"""
        {intro}
        
        {summary_label} {summary}.
        
        {entities_label} {entities_text}.
        
        {insight_label} {persona_brief.get('summary', '')}.
        
        {takeaway_label} {persona_brief.get('final_assessment', '')}.
        
        {prediction_label} {analysis.get('prediction', '')}.
        
        {outro}
        """
        audio_url = await asyncio.to_thread(_generate_audio, audio_script, topic, lang=language)

        if not translated_summary:
            translated_summary = f"Intelligence synthesis for {topic} is currently matching multiple narrative clusters across verified sources."

        # Enforce all 4 angle keys
        for key in ["market_impact", "expert_opinion", "risks", "opportunities"]:
            if not angles.get(key):
                angles[key] = f"Analyzing specific {key.replace('_', ' ')} for {topic}..."

        briefing = {
            "title": f"Intelligence Briefing: {topic}",
            "summary": translated_summary, # Main summary is now translated
            "persona": persona,
            "language": language,

            "persona_brief": persona_brief,
            "angles": angles,
            "follow_up_questions": followups,
            "timeline": translated_timeline, # Timeline is now translated
            "prediction": translated_prediction, # Prediction is now translated

            "key_entities": analysis.get("key_entities", [])[:10],
            "entities_metadata": analysis.get("entities_metadata", []), 
            "sentiment": analysis.get("sentiment", "neutral"),
            "sources": sources[:5],
            "translated_summary": translated_summary,
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