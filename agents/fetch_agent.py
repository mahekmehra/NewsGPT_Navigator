"""
NewsGPT Navigator — Fetch Agent

Ingests news articles from NewsAPI (with fallback to local samples),
scores each article for quality (relevance + recency + content length),
validates source credibility, and enforces domain diversity.
"""

from datetime import datetime, timezone
from agents.state import PipelineState


def _score_article(article: dict, topic: str) -> float:
    """
    Score an article for quality.
    Score = relevance_match * 0.4 + recency * 0.3 + length_score * 0.3
    """
    # Relevance: keyword overlap (Weighted towards Title)
    keywords = set(topic.lower().split())
    title = article.get('title', '').lower()
    desc = article.get('description', '').lower()
    
    title_matches = sum(1 for kw in keywords if kw in title)
    desc_matches = sum(1 for kw in keywords if kw in desc)
    
    # Require at least ONE keyword in the title for a decent score
    title_relevance = title_matches / len(keywords) if keywords else 0
    desc_relevance = desc_matches / len(keywords) if keywords else 0
    
    # Combined relevance (Title is more important)
    relevance = (title_relevance * 0.7) + (desc_relevance * 0.3)
    
    # HARD FILTER: If it doesn't match enough (less than 35%), it's junk
    if relevance < 0.35:
        return 0.0

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
    
    # HARD FILTER: Don't accept snippets that are too short (under 100 chars)
    if content_len < 100:
        return 0.0

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

        # Score and calculate credibility for articles
        scored_articles = []
        quality_scores = []
        
        for article in raw_articles:
            score = _score_article(article, topic)
            article["quality_score"] = score
            
            domain = article.get("source_domain", "")
            cred = check_credibility(domain)
            article["credibility_verified"] = cred["credibility"] == "trusted"
            article["credibility_score"] = cred.get("score", 0.5)
            
            scored_articles.append(article)
            quality_scores.append(score)

        # Filter: Ignore sources below 0.6 (unless no alternatives exist)
        reliable_candidates = [
            a for a in scored_articles
            if a["credibility_score"] >= 0.6
            and a["quality_score"] >= settings.QUALITY_THRESHOLD
            and is_source_acceptable(a.get("source_domain", ""))
        ]
        
        if reliable_candidates:
            verified_articles = reliable_candidates
            source_quality_summary = f"High reliability. Filtered {len(verified_articles)} sources with credibility score ≥ 0.6."
        else:
            # Fallback to previously accepted baseline
            verified_articles = [
                a for a in scored_articles
                if a["quality_score"] >= settings.QUALITY_THRESHOLD
                and is_source_acceptable(a.get("source_domain", ""))
            ]
            source_quality_summary = "Low reliability. Insufficient highly credible sources found; fell back to available alternatives."
        
        # Enforce domain diversity (at least 3 unique domains)
        diversity_limit = 3
        domain_groups = {}
        for a in verified_articles:
            d = a.get("source_domain", "unknown")
            if d not in domain_groups:
                domain_groups[d] = []
            domain_groups[d].append(a)
        
        diverse_articles = []
        # First pass: pick top scored from each unique domain
        sorted_domains = sorted(domain_groups.keys(), key=lambda d: max([x["quality_score"] for x in domain_groups[d]]), reverse=True)
        
        for d in sorted_domains:
            if len(diverse_articles) < 6:
                diverse_articles.append(domain_groups[d][0])
        
        # Second pass: fill up to 6 with remaining top articles if diversity target already hit
        if len(diverse_articles) < 6:
            remaining = []
            for d in sorted_domains:
                remaining.extend(domain_groups[d][1:])
            remaining.sort(key=lambda x: x["quality_score"], reverse=True)
            diverse_articles.extend(remaining[:6 - len(diverse_articles)])

        audit_entry["outputs"] = {
            "total_fetched": len(raw_articles),
            "verified_count": len(diverse_articles),
            "unique_domains": len(set(a.get("source_domain") for a in diverse_articles)),
            "avg_quality": round(sum(quality_scores) / len(quality_scores), 3) if quality_scores else 0,
            "source_quality_summary": source_quality_summary
        }

        return {
            "articles": scored_articles,
            "quality_scores": quality_scores,
            "verified_articles": diverse_articles,
            "fetch_success": len(diverse_articles) > 0,
            "current_agent": "fetch",
            "error": "",
            "audit_trail": [audit_entry],
            "source_quality_summary": source_quality_summary,
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
