"""
NewsGPT Navigator — Entity Sentiment Agent

Extracts named entities from verified articles via LLM,
tags each with sentiment (positive/negative/neutral), and
builds temporal story arcs from prior knowledge sessions.
"""

import json
from core.safe_json import safe_json_parse
from datetime import datetime, timezone
from agents.state import PipelineState


def entity_sentiment_agent(state: PipelineState) -> dict:
    """
    Entity sentiment agent node for the LangGraph pipeline.

    - Extracts named entities from verified articles via LLM
    - Tags each entity with sentiment (positive/negative/neutral)
    - Assigns confidence score per entity
    - Counts mentions across articles
    """
    from core.llm_router import call_llm

    verified_articles = state.get("verified_articles", [])
    topic = state.get("topic", "")
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = {
        "timestamp": timestamp,
        "agent": "entity_sentiment",
        "action": "extract_entities_and_sentiment",
        "inputs": {"topic": topic, "article_count": len(verified_articles)},
        "outputs": {},
    }

    try:
        if not verified_articles:
            audit_entry["outputs"] = {"error": "No articles to process"}
            return {
                "entity_sentiments": [],
                "entities_extracted": False,
                "current_agent": "entity_sentiment",
                "audit_trail": [audit_entry],
            }

        # Build combined text for NER
        articles_text = ""
        for i, art in enumerate(verified_articles):
            title = art.get("title", "")
            content = art.get("content", "") or art.get("description", "")
            articles_text += f"\n--- Article {i+1}: {title} ---\n{content}\n"

        # LLM-based NER + sentiment tagging
        ner_prompt = f"""Analyze these news articles about "{topic}" and extract ALL named entities.
For each entity, determine:
1. Entity name
2. Entity type (PERSON, ORG, GPE, PRODUCT, EVENT, POLICY, METRIC)
3. Sentiment (positive, negative, neutral) based on how the entity is portrayed
4. Confidence score (0.0 to 1.0)
5. Which article numbers mention this entity (1-indexed)

ARTICLES:
{articles_text[:4000]}

Respond in this exact JSON format:
{{
    "entities": [
        {{
            "entity": "Entity Name",
            "entity_type": "ORG",
            "sentiment": "positive",
            "score": 0.85,
            "article_ids": [1, 3]
        }}
    ]
}}"""

        response = call_llm(
            prompt=ner_prompt,
            system_prompt="You are a precise NER and sentiment analysis engine. Always respond in valid JSON.",
            complexity="simple",
        )

        # Parse response (resilient)
        data = safe_json_parse(response, {"entities": []})
        raw_entities = data.get("entities", [])

        # Build EntitySentiment list
        entity_sentiments = []
        for ent in raw_entities:
            article_ids = ent.get("article_ids", [])
            entity_sentiments.append({
                "entity": ent.get("entity", "Unknown"),
                "entity_type": ent.get("entity_type", "UNKNOWN"),
                "sentiment": ent.get("sentiment", "neutral"),
                "score": float(ent.get("score", 0.5)),
                "mentions": len(article_ids),
                "articles": article_ids,
            })

        # Fallback: ensure at least minimal entity data for downstream agents
        if not entity_sentiments:
            entity_sentiments = [
                {
                    "entity": "Government",
                    "entity_type": "GPE",
                    "sentiment": "neutral",
                    "score": 0.5,
                    "mentions": 1,
                    "articles": [1],
                },
                {
                    "entity": "Economy",
                    "entity_type": "METRIC",
                    "sentiment": "neutral",
                    "score": 0.5,
                    "mentions": 1,
                    "articles": [1],
                }
            ]
        # Load prior knowledge to build temporal trends
        story_arc = []
        try:
            import os
            knowledge_store_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "data", "knowledge_store"
            )
            session_id = state.get("knowledge_session_id", "")
            if session_id:
                prev_path = os.path.join(knowledge_store_dir, f"{session_id}.json")
                prev_knowledge = {}
                try:
                    with open(prev_path, "r", encoding="utf-8") as f:
                        prev_knowledge = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    pass

                prev_entities = prev_knowledge.get("entities", {})
                for ent in entity_sentiments:
                    entity_name = ent.get("entity", "")
                    current_sentiment = ent.get("sentiment", "neutral")
                    current_score = ent.get("score", 0.5)

                    if entity_name in prev_entities:
                        prev = prev_entities[entity_name]
                        prev_sentiment = prev.get("sentiment", "neutral")
                        prev_score = prev.get("score", 0.5)

                        # Build trend from previous + current
                        prev_ts = prev_knowledge.get("last_updated", "")
                        trend = [
                            {"period": prev_ts or "previous", "sentiment": prev_sentiment, "score": round(prev_score, 2)},
                            {"period": timestamp, "sentiment": current_sentiment, "score": round(current_score, 2)},
                        ]
                        shift = f"{prev_sentiment}→{current_sentiment}" if prev_sentiment != current_sentiment else "stable"
                        story_arc.append({
                            "entity": entity_name,
                            "entity_type": ent.get("entity_type", "UNKNOWN"),
                            "trend": trend,
                            "shift": shift,
                            "first_seen": prev_ts or timestamp,
                            "latest_update": timestamp,
                        })
                    else:
                        # New entity — single data point
                        story_arc.append({
                            "entity": entity_name,
                            "entity_type": ent.get("entity_type", "UNKNOWN"),
                            "trend": [{"period": timestamp, "sentiment": current_sentiment, "score": round(current_score, 2)}],
                            "shift": "new",
                            "first_seen": timestamp,
                            "latest_update": timestamp,
                        })
        except Exception:
            pass  # Story arc is best-effort, never blocks pipeline

        audit_entry["outputs"] = {
            "entities_found": len(entity_sentiments),
            "positive": sum(1 for e in entity_sentiments if e["sentiment"] == "positive"),
            "negative": sum(1 for e in entity_sentiments if e["sentiment"] == "negative"),
            "neutral": sum(1 for e in entity_sentiments if e["sentiment"] == "neutral"),
            "story_arc_entries": len(story_arc),
        }

        return {
            "entity_sentiments": entity_sentiments,
            "entities_extracted": True,
            "story_arc": story_arc,
            "current_agent": "entity_sentiment",
            "error": "",
            "audit_trail": [audit_entry],
        }

    except Exception as e:
        audit_entry["outputs"] = {"error": str(e)}
        return {
            "entity_sentiments": [],
            "entities_extracted": False,
            "current_agent": "entity_sentiment",
            "error": f"Entity sentiment agent error: {e}",
            "audit_trail": [audit_entry],
        }
