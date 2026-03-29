"""
NewsGPT Navigator — Angle Decomposition Agent

Clusters verified articles by narrative angle via LLM,
labels each cluster, and builds per-angle FAISS indexes
for downstream RAG retrieval.
"""

import json
from core.safe_json import safe_json_parse
from datetime import datetime, timezone
from agents.state import PipelineState


def angle_agent(state: PipelineState) -> dict:
    """
    Angle decomposition agent node for the LangGraph pipeline.

    - Clusters articles by narrative angle via LLM
    - Labels each cluster (fiscal impact, market reaction, etc.)
    - Generates per-angle summaries
    - Builds per-angle FAISS indexes
    """
    from core.llm_router import call_llm
    from core.embeddings import build_index

    verified_articles = state.get("verified_articles", [])
    topic = state.get("topic", "")
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = {
        "timestamp": timestamp,
        "agent": "angle",
        "action": "cluster_by_angle",
        "inputs": {"topic": topic, "article_count": len(verified_articles)},
        "outputs": {},
    }

    try:
        if not verified_articles:
            audit_entry["outputs"] = {"error": "No articles to cluster"}
            return {
                "angle_clusters": [],
                "angle_indexes_built": False,
                "current_agent": "angle",
                "audit_trail": [audit_entry],
            }

        # Build articles summary for clustering
        articles_summary = ""
        for i, art in enumerate(verified_articles):
            title = art.get("title", "")
            desc = art.get("description", "") or art.get("content", "")[:200]
            articles_summary += f"Article {i+1}: {title} — {desc}\n"

        # LLM clustering
        cluster_prompt = f"""Analyze these news articles about "{topic}" and group them by narrative angle.
Each angle is a distinct perspective or framing of the story.

ARTICLES:
{articles_summary[:3500]}

Identify up to 5 distinct narrative angles. For each angle, provide:
1. A short label (2-4 words)
2. Which article numbers belong to this angle (1-indexed)
3. A brief summary of this angle's narrative (2-3 sentences)

Respond in this exact JSON format:
{{
    "angles": [
        {{
            "label": "Fiscal Impact",
            "article_ids": [1, 4],
            "summary": "Articles focusing on the budget implications and fiscal policy changes."
        }}
    ]
}}"""

        response = call_llm(
            prompt=cluster_prompt,
            system_prompt="You are a narrative analyst. Identify distinct angles and framings. Always respond in valid JSON.",
            complexity="simple",
        )

        # Parse response (resilient)
        fallback_angles = {"angles": [{"label": "General Coverage", "article_ids": list(range(1, len(verified_articles) + 1)), "summary": "All articles grouped together."}]}
        data = safe_json_parse(response, fallback_angles)
        raw_angles = data.get("angles", fallback_angles["angles"])

        # Build AngleCluster list
        angle_clusters = []
        indexes_built = True
        for idx, angle in enumerate(raw_angles):
            article_ids = angle.get("article_ids", [])
            # Convert 1-indexed to 0-indexed
            zero_indexed = [aid - 1 for aid in article_ids if 1 <= aid <= len(verified_articles)]

            # Build per-angle FAISS index from the cluster's articles
            angle_texts = []
            for aid in zero_indexed:
                art = verified_articles[aid]
                content = art.get("content", "") or art.get("description", "")
                angle_texts.append(f"{art.get('title', '')}. {content}")

            if angle_texts:
                try:
                    build_index(angle_texts)
                except Exception:
                    indexes_built = False

            angle_clusters.append({
                "angle_id": idx,
                "label": angle.get("label", f"Angle {idx + 1}"),
                "article_ids": zero_indexed,
                "summary": angle.get("summary", ""),
                "article_count": len(zero_indexed),
            })

        audit_entry["outputs"] = {
            "angles_found": len(angle_clusters),
            "indexes_built": indexes_built,
        }

        return {
            "angle_clusters": angle_clusters,
            "angle_indexes_built": indexes_built,
            "current_agent": "angle",
            "error": "",
            "audit_trail": [audit_entry],
        }

    except Exception as e:
        audit_entry["outputs"] = {"error": str(e)}
        return {
            "angle_clusters": [],
            "angle_indexes_built": False,
            "current_agent": "angle",
            "error": f"Angle decomposition agent error: {e}",
            "audit_trail": [audit_entry],
        }
