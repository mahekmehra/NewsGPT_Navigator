"""
NewsGPT Navigator — Fetch Agent

Calls NewsAPI for articles on the given topic.
Scores each article for quality (relevance + recency + length).
Validates source credibility. Falls back to sample JSON silently.
"""

from datetime import datetime, timezone
from agents.state import PipelineState


def _score_article(article: dict, topic: str) -> float:
    """
    Score an article for quality.
    Score = relevance_match * 0.4 + recency * 0.3 + length_score * 0.3
    """
    # Relevance: keyword overlap
    keywords = topic.lower().split()
    text = f"{article.get('title', '')} {article.get('description', '')}".lower()
    matches = sum(1 for kw in keywords if kw in text)
    relevance = min(matches / max(len(keywords), 1), 1.0)

    # Recency: prefer articles from last 3 days
    recency = 0.5  # default
    pub_date = article.get("published_at", "")
    if pub_date:
        try:
            pub_dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            days_old = (now - pub_dt).days
            if days_old <= 1:
                recency = 1.0
            elif days_old <= 3:
                recency = 0.8
            elif days_old <= 7:
                recency = 0.5
            else:
                recency = 0.2
        except Exception:
            pass

    # Length: prefer articles with substantial content
    content = article.get("content", "") or article.get("description", "")
    content_len = len(content)
    if content_len > 500:
        length_score = 1.0
    elif content_len > 200:
        length_score = 0.7
    elif content_len > 50:
        length_score = 0.4
    else:
        length_score = 0.1

    return relevance * 0.4 + recency * 0.3 + length_score * 0.3


def fetch_agent(state: PipelineState) -> dict:
    """
    Fetch agent node for the LangGraph pipeline.

    - Fetches articles from NewsAPI (or fallback samples)
    - Scores each article for quality
    - Filters by quality threshold
    - Validates source credibility
    - Returns updated state fields
    """
    from core.news_fetcher import fetch_articles
    from core.credibility import check_credibility, is_source_acceptable
    from core.config import settings

    topic = state.get("topic", "")
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = {
        "timestamp": timestamp,
        "agent": "fetch",
        "action": "fetch_articles",
        "inputs": {"topic": topic},
        "outputs": {},
    }

    try:
        # Fetch articles
        raw_articles = fetch_articles(topic)

        if not raw_articles:
            audit_entry["outputs"] = {"error": "No articles found", "count": 0}
            return {
                "articles": [],
                "quality_scores": [],
                "verified_articles": [],
                "fetch_success": False,
                "current_agent": "fetch",
                "error": "No articles found for this topic",
                "audit_trail": [audit_entry],
            }

        # Score and filter articles
        scored_articles = []
        quality_scores = []
        verified_articles = []

        for article in raw_articles:
            score = _score_article(article, topic)
            article["quality_score"] = score
            scored_articles.append(article)
            quality_scores.append(score)

            # Check credibility
            domain = article.get("source_domain", "")
            cred = check_credibility(domain)
            article["credibility_verified"] = cred["credibility"] == "trusted"

            # Filter: quality threshold AND not blocked
            if score >= settings.QUALITY_THRESHOLD and is_source_acceptable(domain):
                verified_articles.append(article)
        
        # Enforce limit (User Request)
        verified_articles = verified_articles[:6]

        audit_entry["outputs"] = {
            "total_fetched": len(raw_articles),
            "verified_count": len(verified_articles),
            "avg_quality": round(sum(quality_scores) / len(quality_scores), 3) if quality_scores else 0,
        }

        return {
            "articles": scored_articles,
            "quality_scores": quality_scores,
            "verified_articles": verified_articles,
            "fetch_success": len(verified_articles) > 0,
            "current_agent": "fetch",
            "error": "",
            "audit_trail": [audit_entry],
        }

    except Exception as e:
        audit_entry["outputs"] = {"error": str(e)}
        return {
            "articles": [],
            "quality_scores": [],
            "verified_articles": [],
            "fetch_success": False,
            "current_agent": "fetch",
            "error": f"Fetch agent error: {e}",
            "audit_trail": [audit_entry],
        }
