"""
NewsGPT Navigator — User Profile + Ranking Agent

Builds deep user profile from persona presets.
Ranks content by profile. Selects persona prompt template.
"""

import json
from core.safe_json import safe_json_parse
import os
from datetime import datetime, timezone
from agents.state import PipelineState


def _load_persona_presets() -> dict:
    """Load persona presets from data file."""
    preset_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "persona_presets.json"
    )
    try:
        with open(preset_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"presets": {}}


def profile_ranking_agent(state: PipelineState) -> dict:
    """
    Profile ranking agent node for the LangGraph pipeline.

    - Loads persona preset from data/persona_presets.json
    - Builds deep user profile
    - Ranks articles by relevance to the profile
    - Selects persona prompt template for delivery
    """
    from core.llm_router import call_llm

    persona = state.get("persona", "General")
    verified_articles = state.get("verified_articles", [])
    entity_sentiments = state.get("entity_sentiments", [])
    angle_clusters = state.get("angle_clusters", [])
    topic = state.get("topic", "")
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = {
        "timestamp": timestamp,
        "agent": "profile_ranking",
        "action": "build_profile_and_rank",
        "inputs": {"persona": persona, "article_count": len(verified_articles)},
        "outputs": {},
    }

    try:
        # Load persona presets
        presets_data = _load_persona_presets()
        presets = presets_data.get("presets", {})

        # Match persona to preset
        preset_key = None
        for key, preset in presets.items():
            if persona.lower() in key.lower() or key.lower() in persona.lower():
                preset_key = key
                break

        # Build user profile from preset or defaults
        if preset_key and preset_key in presets:
            preset = presets[preset_key]
            user_profile = {
                "persona_preset": preset_key,
                "interests": preset.get("interests", []),
                "knowledge_level": preset.get("knowledge_level", "intermediate"),
                "risk_appetite": preset.get("risk_appetite", "moderate"),
                "jargon_comfort": preset.get("jargon_comfort", "medium"),
                "preferred_depth": preset.get("preferred_depth", "standard"),
            }
        else:
            # Default profile based on existing persona
            profile_defaults = {
                "Student": {
                    "persona_preset": "student",
                    "interests": ["education", "technology", "careers"],
                    "knowledge_level": "beginner",
                    "risk_appetite": "conservative",
                    "jargon_comfort": "low",
                    "preferred_depth": "brief",
                },
                "Investor": {
                    "persona_preset": "investor",
                    "interests": ["markets", "finance", "economics"],
                    "knowledge_level": "expert",
                    "risk_appetite": "aggressive",
                    "jargon_comfort": "high",
                    "preferred_depth": "detailed",
                },
                "Beginner": {
                    "persona_preset": "beginner",
                    "interests": ["general_news", "explanations"],
                    "knowledge_level": "beginner",
                    "risk_appetite": "conservative",
                    "jargon_comfort": "low",
                    "preferred_depth": "brief",
                },
            }
            user_profile = profile_defaults.get(persona, {
                "persona_preset": "general",
                "interests": ["general_news"],
                "knowledge_level": "intermediate",
                "risk_appetite": "moderate",
                "jargon_comfort": "medium",
                "preferred_depth": "standard",
            })

        # ── Custom persona override: use LLM to build dynamic profile ──
        custom_persona = state.get("custom_persona", "")
        if custom_persona and custom_persona.strip():
            try:
                profile_prompt = f"""Build a user profile for a news consumer who describes themselves as: "{custom_persona}"

Respond in this exact JSON format:
{{
    "persona_preset": "custom",
    "interests": ["topic1", "topic2", "topic3"],
    "knowledge_level": "beginner|intermediate|expert",
    "risk_appetite": "conservative|moderate|aggressive",
    "jargon_comfort": "low|medium|high",
    "preferred_depth": "brief|standard|detailed"
}}"""
                profile_response = call_llm(
                    prompt=profile_prompt,
                    system_prompt="You are a user profiling expert. Always respond in valid JSON.",
                    complexity="simple",
                )
                custom_profile = safe_json_parse(profile_response, None)
                if custom_profile and isinstance(custom_profile, dict) and "interests" in custom_profile:
                    custom_profile["persona_preset"] = f"custom:{custom_persona[:50]}"
                    user_profile = custom_profile
            except Exception:
                pass  # Fall back to default profile

        # Rank articles by profile relevance using LLM
        if verified_articles:
            articles_brief = ""
            for i, art in enumerate(verified_articles):
                articles_brief += f"{i+1}. {art.get('title', 'Untitled')}\n"

            rank_prompt = f"""Given this user profile:
- Interests: {', '.join(user_profile.get('interests', []))}
- Knowledge level: {user_profile.get('knowledge_level', 'intermediate')}
- Risk appetite: {user_profile.get('risk_appetite', 'moderate')}

Rank these articles by relevance (most relevant first). Return ONLY a JSON array of article numbers.

ARTICLES:
{articles_brief[:2000]}

Respond in this exact JSON format:
{{"ranked": [3, 1, 5, 2, 4]}}"""

            rank_response = call_llm(
                prompt=rank_prompt,
                system_prompt="You are a content ranker. Always respond in valid JSON.",
                complexity="simple",
            )

            rank_data = safe_json_parse(rank_response, {"ranked": list(range(1, len(verified_articles) + 1))})
            ranked_indices = rank_data.get("ranked", list(range(1, len(verified_articles) + 1)))
            # Convert to 0-indexed and reorder
            ranked_articles = []
            try:
                for idx in ranked_indices:
                    zero_idx = idx - 1
                    if 0 <= zero_idx < len(verified_articles):
                        ranked_articles.append(verified_articles[zero_idx])
                # Add any missing articles
                for art in verified_articles:
                    if art not in ranked_articles:
                        ranked_articles.append(art)
            except (TypeError, AttributeError):
                ranked_articles = verified_articles[:]
        else:
            ranked_articles = []

        # Select persona prompt template
        persona_templates = {
            "CFO": "Deliver as a CFO-level executive briefing. Focus on financial impact, risk exposure, and actionable insights. Use professional financial terminology.",
            "first_gen_investor": "Explain in simple Hindi/English terms suitable for a first-generation investor. Avoid jargon, use real-world analogies, and focus on practical impact on personal finances.",
            "Student": "Explain in clear, educational language. Use analogies and examples a college student would understand.",
            "Investor": "Focus on market impact, financial implications, and data-driven insights. Be concise and actionable.",
            "Beginner": "Use very simple language, avoid jargon, explain every concept from scratch.",
            "General": "Provide a balanced, comprehensive briefing suitable for a general professional audience.",
        }

        persona_template = persona_templates.get(
            user_profile.get("persona_preset", persona),
            persona_templates.get(persona, persona_templates["General"])
        )

        audit_entry["outputs"] = {
            "profile_preset": user_profile.get("persona_preset", "default"),
            "knowledge_level": user_profile.get("knowledge_level", "unknown"),
            "articles_ranked": len(ranked_articles),
        }

        return {
            "user_profile": user_profile,
            "ranked_articles": ranked_articles,
            "persona_template": persona_template,
            "current_agent": "profile_ranking",
            "error": "",
            "audit_trail": [audit_entry],
        }

    except Exception as e:
        audit_entry["outputs"] = {"error": str(e)}
        return {
            "user_profile": {},
            "ranked_articles": verified_articles[:],
            "persona_template": "",
            "current_agent": "profile_ranking",
            "error": f"Profile ranking agent error: {e}",
            "audit_trail": [audit_entry],
        }
