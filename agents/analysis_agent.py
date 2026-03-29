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

    from core.embeddings import build_index, search, clear_index
    from core.llm_router import classify_complexity, call_llm

    topic = state.get("topic", "")
    verified_articles = state.get("verified_articles", [])
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = {
        "timestamp": timestamp,
        "agent": "analysis",
        "action": "analyze_articles",
        "inputs": {"topic": topic, "article_count": len(verified_articles)},
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
        clear_index()
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

        # Main synthesis prompt
        synthesis_prompt = f"""
Analyze the news about "{topic}" and provide high-value intelligence.

1. Summary: A professional 3-4 sentence overview of the main event.
2. Market Impact: Strategic outlook for industries and markets.
3. Risks: Key threats or negative developments.
4. Opportunities: Growth potential or positive shifts.
5. Expert Opinion: Contrast different viewpoints or public narratives.

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
    "expert_opinion": "expert text..."
}}"""

        response = call_llm(
            prompt=synthesis_prompt,
            system_prompt="Return valid JSON only.",
            complexity=complexity,
        )

        data = safe_json_parse(response, {})

        # ── Timeline (with Source Mapping) ──
        timeline_prompt = f"""
        Extract key timeline events from:
        {context}

        For each event, specify which article it comes from (provide a short title or index).
        Return JSON:
        {{"timeline":[{{"date":"...","event":"...", "source_hint":"..."}}]}}
        """

        timeline_resp = call_llm(
            prompt=timeline_prompt,
            system_prompt="Return valid JSON. Be accurate with dates.",
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

        # ── Prediction ──
        prediction_prompt = f"""
Based on this:
{data.get("summary","")[:1000]}

Give 2-3 line future prediction.
"""

        prediction = call_llm(
            prompt=prediction_prompt,
            system_prompt="Be realistic and concise.",
            complexity=complexity,
        )

        # Audio-ready concise summary
        concise_prompt = f"""
Summarize this news in UNDER 20 words for smooth voice narration:
{data.get("summary","")[:1000]}
"""
        concise_summary = call_llm(
            prompt=concise_prompt,
            system_prompt="Short, one-line, professional narration.",
            complexity="simple",
        )

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
