"""
NewsGPT Navigator — Analysis Agent

Builds FAISS vectorstore from articles, classifies complexity,
routes to appropriate LLM, performs RAG Q&A, extracts timeline,
and generates predictions.
"""

from core.safe_json import safe_json_parse
from core.config import settings
from datetime import datetime, timezone
from agents.state import PipelineState


def analysis_agent(state: PipelineState) -> dict:
    """
    Analysis agent node for the LangGraph pipeline.

    - Builds FAISS vectorstore from verified articles
    - Routes to appropriate LLM based on complexity classification
    - Performs RAG-based multi-article synthesis
    - Extracts timeline events with source mapping
    - Generates predictions and audio-ready summaries
    """

    from core.embeddings import build_index, search
    from core.llm_router import classify_complexity, call_llm

    topic = state.get("topic", "")
    language = state.get("language", "en")
    verified_articles = state.get("verified_articles", [])
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = {
        "timestamp": timestamp,
        "agent": "analysis",
        "action": "analyze_articles",
        "inputs": {"topic": topic, "article_count": len(verified_articles), "language": language},
        "outputs": {},
    }

    try:
        if not verified_articles:
            return {
                "analysis": {},
                "analysis_success": False,
                "current_agent": "analysis",
                "error": "No verified articles",
                "audit_trail": [audit_entry],
            }

        # ── Build FAISS Index ──
        # Note: clear_index() removed to allow reuse across parallel persona queries
        texts = [
            f"{a.get('title', '')}. {a.get('content', '') or a.get('description', '')}"
            for a in verified_articles
        ]
        embeddings_built = build_index(texts)

        # ── Complexity Routing ──
        complexity = classify_complexity(verified_articles, topic)

        # ── RAG Retrieval ──
        rag_results = search(topic, top_k=5) if embeddings_built else []
        context = "\n\n---\n\n".join([r["text"] for r in rag_results])

        # Main consolidated synthesis prompt
        synthesis_prompt = f"""
        Analyze the news about "{topic}" and provide high-value intelligence.
        
        TARGET LANGUAGE: {language}
        You MUST respond in {language}. Use the NATIVE script for {language} (e.g. Gurmukhi for Punjabi, Devanagari for Hindi, Arabic script for Urdu, Hanzi for Chinese, etc.).
        DO NOT use Romanized transliteration. All text fields in the JSON must be in the native script of {language}.

        1. Summary: A professional 3-4 sentence overview of the main event.
        2. Market Impact: Strategic outlook for industries and markets.
        3. Risks: Key threats or negative developments.
        4. Opportunities: Growth potential or positive shifts.
        5. Expert Opinion: Contrast different viewpoints or public narratives.
        6. Future Prediction: A 2-3 line realistic forecast based on current data.
        7. Concise Narration: Under 20 words for smooth voice narration.

        ARTICLES:
        {context}

        Respond in STRICT JSON:
        {{
            "summary": "Full overview text...",
            "key_entities": ["Entity A", "Entity B"],
            "sentiment": "positive|negative|neutral|mixed",
            "market_impact": "impact text...",
            "risks": "risk text...",
            "opportunities": "opportunity text...",
            "expert_opinion": "expert text...",
            "prediction": "Future forecast...",
            "concise_summary": "Short narration summary..."
        }}"""

        response = call_llm(
            prompt=synthesis_prompt,
            system_prompt=f"You are a precise news analyst. Respond strictly in {language} JSON using its native script.",
            complexity=complexity,
        )

        data = safe_json_parse(response, {})
        prediction = data.get("prediction", "Future outlook pending further data.")
        concise_summary = data.get("concise_summary", "Briefing for topic.")

        # ── Timeline (Improved Logic) ──
        timeline_prompt = f"""
        Extract a comprehensive chronological timeline of events for "{topic}".
        
        TARGET LANGUAGE: {language}
        You MUST respond in {language} using its native script.

        INSTRUCTIONS:
        1. Extract ALL significant events with specific dates.
        2. If a specific date is missing but can be inferred (e.g. 'yesterday', 'last week'), calculate it based on today: {datetime.now().strftime('%Y-%m-%d')}.
        3. Ensure events are in strict chronological order.
        4. Provide at least 5-8 events if the data allows.
        5. For each event, provide a 'source_hint' (article snippet or title).

        CONTEXT:
        {context}

        Return STRICT JSON:
        {{"timeline":[{{"date":"YYYY-MM-DD","event":"...", "source_hint":"..."}}]}}
        """

        timeline_resp = call_llm(
            prompt=timeline_prompt,
            system_prompt=f"You are a historical data extractor. Return valid JSON in {language} using its native script.",
            complexity="simple",
        )

        timeline_data = safe_json_parse(timeline_resp, {"timeline": []})
        timeline = timeline_data.get("timeline", [])
        
        # Map timeline to Article (Source Title + URL)
        for ev in timeline:
            hint = ev.get("source_hint", "").lower()
            ev["url"] = ""
            ev["source_title"] = ""
            for a in verified_articles:
                if hint and (hint in a.get("title", "").lower() or hint in a.get("source", "").lower()):
                    ev["url"] = a.get("url", "")
                    ev["source_title"] = a.get("title", "")
                    break
            if not ev["url"] and verified_articles:
                ev["url"] = verified_articles[0].get("url", "")
                ev["source_title"] = verified_articles[0].get("title", "")
        
        if not timeline:
            timeline = [{"date": "N/A", "event": "No major timeline events available", "source_title": "N/A", "url": ""}]

        # ── Entities with Article Links ──
        entities_metadata = []
        for ent in data.get("key_entities", []):
            entity_articles = []
            # Find up to 2 articles mentioning this entity
            for a in sorted(verified_articles, key=lambda x: x.get("quality_score", 0), reverse=True):
                content_to_check = (a.get("title", "") + " " + (a.get("content", "") or a.get("description", "") or "")).lower()
                if ent.lower() in content_to_check:
                    entity_articles.append({
                        "title": a.get("title", ""),
                        "url": a.get("url", "")
                    })
                if len(entity_articles) >= 2:
                    break
            
            # Fallback to first article if none found
            if not entity_articles and verified_articles:
                entity_articles.append({
                    "title": verified_articles[0].get("title", ""),
                    "url": verified_articles[0].get("url", "")
                })
            
            entities_metadata.append({
                "entity": ent,
                "entity_articles": entity_articles
            })

        # ── Sources ──
        sources_used = [
            {
                "title": a.get("title", ""),
                "source": a.get("source", ""),
                "url": a.get("url", ""),
            }
            for a in verified_articles
        ]

        analysis_result = {
            "summary": data.get("summary", ""),
            "concise_summary": concise_summary,
            "timeline": timeline,
            "prediction": prediction,
            "key_entities": data.get("key_entities", []),
            "entities_metadata": entities_metadata,
            "sentiment": data.get("sentiment", "neutral"),

            # Structured intelligence fields
            "market_impact": data.get("market_impact", ""),
            "risks": data.get("risks", ""),
            "opportunities": data.get("opportunities", ""),
            "expert_opinion": data.get("expert_opinion", ""),

            "sources_used": sources_used,
            "model_used": settings.POWER_MODEL if complexity == "complex" else settings.FAST_MODEL,
            "complexity_class": complexity,
        }

        audit_entry["outputs"] = {
            "summary_length": len(analysis_result["summary"]),
            "has_angles": True,
            "timeline_events": len(analysis_result["timeline"]),
        }

        return {
            "analysis": analysis_result,
            "analysis_success": True,
            "current_agent": "analysis",
            "error": "",
            "audit_trail": [audit_entry],
        }

    except Exception as e:
        audit_entry["outputs"] = {"error": str(e)}
        return {
            "analysis": {},
            "analysis_success": False,
            "current_agent": "analysis",
            "error": f"Analysis error: {e}",
            "audit_trail": [audit_entry],
        }
