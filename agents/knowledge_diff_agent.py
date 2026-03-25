"""
NewsGPT Navigator — Knowledge Diff Agent (UNIQUE)

Compares new articles against user's knowledge state.
Surfaces only the delta — what's genuinely new.
"""

import json
import os
from datetime import datetime, timezone
from agents.state import PipelineState

# Knowledge store directory
KNOWLEDGE_STORE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "knowledge_store"
)


def _load_knowledge_state(session_id: str) -> dict:
    """Load user's existing knowledge state from disk."""
    if not session_id:
        return {"entities": {}, "facts": {}, "last_updated": ""}

    filepath = os.path.join(KNOWLEDGE_STORE_DIR, f"{session_id}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"entities": {}, "facts": {}, "last_updated": ""}


def _save_knowledge_state(session_id: str, state: dict) -> bool:
    """Save updated knowledge state to disk."""
    if not session_id:
        return False

    os.makedirs(KNOWLEDGE_STORE_DIR, exist_ok=True)
    filepath = os.path.join(KNOWLEDGE_STORE_DIR, f"{session_id}.json")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def knowledge_diff_agent(state: PipelineState) -> dict:
    """
    Knowledge diff agent node for the LangGraph pipeline.

    UNIQUE AGENT — Compares new information against what the user already knows:
    - Loads previous knowledge state from data/knowledge_store/
    - Compares entities, facts, and claims
    - Tags each item as: new / changed / known / removed
    - Saves updated knowledge state back to disk
    """
    from core.llm_router import call_llm

    entity_sentiments = state.get("entity_sentiments", [])
    analysis = state.get("analysis", {})
    session_id = state.get("knowledge_session_id", "")
    topic = state.get("topic", "")
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = {
        "timestamp": timestamp,
        "agent": "knowledge_diff",
        "action": "compute_knowledge_delta",
        "inputs": {"topic": topic, "session_id": session_id},
        "outputs": {},
    }

    try:
        # Load previous knowledge state
        prev_knowledge = _load_knowledge_state(session_id)
        prev_entities = prev_knowledge.get("entities", {})

        # Build current entities from entity_sentiments + analysis
        current_entities = {}
        for ent in entity_sentiments:
            entity_name = ent.get("entity", "")
            if entity_name:
                current_entities[entity_name] = {
                    "sentiment": ent.get("sentiment", "neutral"),
                    "score": ent.get("score", 0.5),
                    "type": ent.get("entity_type", "UNKNOWN"),
                    "mentions": ent.get("mentions", 0),
                }

        # Also add key_entities from analysis
        for entity_name in analysis.get("key_entities", []):
            if entity_name and entity_name not in current_entities:
                current_entities[entity_name] = {
                    "sentiment": "neutral",
                    "score": 0.5,
                    "type": "ENTITY",
                    "mentions": 1,
                }

        # Compute diff
        knowledge_diff = []

        # New entities (in current but not in previous)
        for entity, data in current_entities.items():
            if entity not in prev_entities:
                knowledge_diff.append({
                    "entity": entity,
                    "status": "new",
                    "detail": f"New {data['type']}: {entity} (sentiment: {data['sentiment']})",
                    "previous_value": "",
                    "current_value": f"{data['sentiment']} ({data['score']:.2f})",
                })
            else:
                # Check if sentiment changed
                prev_sentiment = prev_entities[entity].get("sentiment", "neutral")
                curr_sentiment = data.get("sentiment", "neutral")
                if prev_sentiment != curr_sentiment:
                    knowledge_diff.append({
                        "entity": entity,
                        "status": "changed",
                        "detail": f"Sentiment shifted from {prev_sentiment} to {curr_sentiment}",
                        "previous_value": f"{prev_sentiment} ({prev_entities[entity].get('score', 0):.2f})",
                        "current_value": f"{curr_sentiment} ({data['score']:.2f})",
                    })
                else:
                    knowledge_diff.append({
                        "entity": entity,
                        "status": "known",
                        "detail": f"Already tracked: {entity}",
                        "previous_value": prev_sentiment,
                        "current_value": curr_sentiment,
                    })

        # Removed entities (in previous but not in current)
        for entity in prev_entities:
            if entity not in current_entities:
                knowledge_diff.append({
                    "entity": entity,
                    "status": "removed",
                    "detail": f"No longer mentioned in current coverage",
                    "previous_value": prev_entities[entity].get("sentiment", ""),
                    "current_value": "",
                })

        # Save updated knowledge state
        updated_knowledge = {
            "entities": current_entities,
            "facts": {
                "summary_hash": hash(analysis.get("summary", ""))
            },
            "last_updated": timestamp,
            "topic": topic,
        }
        saved = _save_knowledge_state(session_id, updated_knowledge)

        audit_entry["outputs"] = {
            "total_items": len(knowledge_diff),
            "new": sum(1 for d in knowledge_diff if d["status"] == "new"),
            "changed": sum(1 for d in knowledge_diff if d["status"] == "changed"),
            "known": sum(1 for d in knowledge_diff if d["status"] == "known"),
            "removed": sum(1 for d in knowledge_diff if d["status"] == "removed"),
            "state_saved": saved,
        }

        return {
            "knowledge_diff": knowledge_diff,
            "knowledge_updated": True,
            "current_agent": "knowledge_diff",
            "error": "",
            "audit_trail": [audit_entry],
        }

    except Exception as e:
        audit_entry["outputs"] = {"error": str(e)}
        return {
            "knowledge_diff": [],
            "knowledge_updated": False,
            "current_agent": "knowledge_diff",
            "error": f"Knowledge diff agent error: {e}",
            "audit_trail": [audit_entry],
        }
