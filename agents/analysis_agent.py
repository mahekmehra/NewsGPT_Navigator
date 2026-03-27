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
    IMPROVED Analysis Agent (Track 8 Ready)

    - Multi-article synthesis
    - Structured intelligence output
    - Audio-ready summary
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

        # ── MAIN SYNTHESIS (HACKATHON OPTIMIZED) ──
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

        # ── Timeline ──
        timeline_prompt = f"""
Extract key timeline events from:
{context}

Return JSON:
{{"timeline":[{{"date":"...","event":"..."}}]}}
"""

        timeline_resp = call_llm(
            prompt=timeline_prompt,
            system_prompt="Return valid JSON.",
            complexity="simple",
        )

        timeline_data = safe_json_parse(timeline_resp, {"timeline": []})

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

        # ── Audio-ready summary (PREMIUM UX) ──
        concise_prompt = f"""
Summarize this news in UNDER 20 words for smooth voice narration:
{data.get("summary","")[:1000]}
"""
        concise_summary = call_llm(
            prompt=concise_prompt,
            system_prompt="Short, one-line, professional narration.",
            complexity="simple",
        )

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
            "timeline": timeline_data.get("timeline", []),
            "prediction": prediction,
            "key_entities": data.get("key_entities", []),
            "sentiment": data.get("sentiment", "neutral"),

            # 🔥 NEW STRUCTURED FIELDS
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
