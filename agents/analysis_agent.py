"""
NewsGPT Navigator — Analysis Agent

Builds FAISS vectorstore from articles, classifies complexity,
routes to appropriate LLM, performs RAG Q&A, extracts timeline,
and generates predictions.
"""

import json
from core.safe_json import safe_json_parse
from datetime import datetime, timezone
from agents.state import PipelineState


def analysis_agent(state: PipelineState) -> dict:
    """
    Analysis agent node for the LangGraph pipeline.

    - Builds FAISS index from verified articles
    - Classifies task complexity → routes to 8B or 70B
    - Runs RAG Q&A for summary generation
    - Extracts timeline as structured JSON
    - Generates "what next" prediction
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
            audit_entry["outputs"] = {"error": "No verified articles to analyze"}
            return {
                "analysis": {},
                "analysis_success": False,
                "embeddings_built": False,
                "current_agent": "analysis",
                "error": "No verified articles available for analysis",
                "audit_trail": [audit_entry],
            }

        # ── Step 1: Build FAISS index ──
        clear_index()
        texts = []
        for art in verified_articles:
            content = art.get("content", "") or art.get("description", "")
            title = art.get("title", "")
            texts.append(f"{title}. {content}")

        embeddings_built = build_index(texts)

        # ── Step 2: Classify complexity & pick model ──
        complexity = classify_complexity(verified_articles, topic)

        # ── Step 3: RAG — retrieve relevant context ──
        rag_results = search(topic, top_k=5) if embeddings_built else []
        context = "\n\n---\n\n".join([r["text"] for r in rag_results])

        # ── Step 4: Generate summary via LLM ──
        summary_prompt = f"""You are an expert news analyst. Based on the following articles about "{topic}", provide:

1. A comprehensive summary (3-5 paragraphs)
2. Key entities mentioned (people, organizations, places)
3. Overall sentiment (positive/negative/neutral/mixed)

ARTICLES:
{context}

Respond in this exact JSON format:
{{
    "summary": "your comprehensive summary here",
    "key_entities": ["entity1", "entity2", ...],
    "sentiment": "positive|negative|neutral|mixed"
}}"""

        summary_response = call_llm(
            prompt=summary_prompt,
            system_prompt="You are a precise news analyst. Always respond in valid JSON format.",
            complexity=complexity,
        )

        # Parse summary response (resilient)
        summary_fallback = {
            "summary": summary_response,
            "key_entities": [],
            "sentiment": "neutral",
        }
        summary_data = safe_json_parse(summary_response, summary_fallback)
        if not summary_data.get("summary"):
            summary_data["summary"] = summary_response

        # ── Step 5: Extract timeline ──
        timeline_prompt = f"""Based on these news articles about "{topic}", extract a chronological timeline of key events.

ARTICLES:
{context}

Respond in this exact JSON format:
{{
    "timeline": [
        {{"date": "YYYY-MM-DD or approximate", "event": "description of event"}},
        ...
    ]
}}"""

        timeline_response = call_llm(
            prompt=timeline_prompt,
            system_prompt="You are a chronological event extractor. Always respond in valid JSON.",
            complexity="simple",
        )

        timeline_data = safe_json_parse(timeline_response, {"timeline": [{"date": "N/A", "event": timeline_response[:200]}]})
        timeline = timeline_data.get("timeline", [])

        # ── Step 6: Generate prediction ──
        prediction_prompt = f"""Based on the current news trends about "{topic}", provide a brief "What Next" prediction (2-3 sentences) about likely future developments.

KEY CONTEXT:
{summary_data.get('summary', '')[:1000]}

Respond with just the prediction text, no JSON needed."""

        prediction = call_llm(
            prompt=prediction_prompt,
            system_prompt="You are a forward-looking news analyst. Be specific but measured in predictions.",
            complexity=complexity,
        )

        # ── Assemble result ──
        sources_used = [
            {"title": a.get("title", ""), "source": a.get("source", ""), "url": a.get("url", "")}
            for a in verified_articles
        ]

        analysis_result = {
            "summary": summary_data.get("summary", ""),
            "timeline": timeline,
            "prediction": prediction,
            "key_entities": summary_data.get("key_entities", []),
            "sentiment": summary_data.get("sentiment", "neutral"),
            "sources_used": sources_used,
            "model_used": "llama3-70b" if complexity == "complex" else "llama3-8b",
            "complexity_class": complexity,
        }

        audit_entry["outputs"] = {
            "complexity": complexity,
            "model_used": analysis_result["model_used"],
            "summary_length": len(analysis_result["summary"]),
            "timeline_events": len(timeline),
            "entities_found": len(analysis_result["key_entities"]),
        }

        return {
            "analysis": analysis_result,
            "analysis_success": True,
            "embeddings_built": embeddings_built,
            "current_agent": "analysis",
            "error": "",
            "audit_trail": [audit_entry],
        }

    except Exception as e:
        audit_entry["outputs"] = {"error": str(e)}
        return {
            "analysis": {},
            "analysis_success": False,
            "embeddings_built": False,
            "current_agent": "analysis",
            "error": f"Analysis agent error: {e}",
            "audit_trail": [audit_entry],
        }
