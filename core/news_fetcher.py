"""
NewsGPT Navigator — News Fetcher

Calls NewsAPI for articles, with fallback to sample JSON.
"""

import json
import os
import requests
from datetime import datetime, timedelta
from typing import Optional

from core.config import settings


_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_SAMPLE_FILE = os.path.join(_DATA_DIR, "sample_articles.json")


def fetch_from_newsapi(
    topic: str,
    max_articles: int = 20,
    days_back: int = 7,
) -> Optional[list]:
    """
    Fetch articles from NewsAPI /everything endpoint.

    Returns list of article dicts or None on failure.
    """
    if not settings.NEWS_API_KEY or settings.NEWS_API_KEY == "your_newsapi_key_here":
        return None

    from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    try:
        response = requests.get(
            f"{settings.NEWS_API_BASE_URL}/everything",
            params={
                "q": " AND ".join(topic.split()),
                "from": from_date,
                "sortBy": "relevancy",
                "pageSize": max_articles,
                "language": "en",
                "apiKey": settings.NEWS_API_KEY,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            return None

        articles = []
        for art in data.get("articles", []):
            # Skip articles with [Removed] content
            if art.get("content") and "[Removed]" in art["content"]:
                continue

            from core.credibility import extract_domain
            source_url = art.get("url", "")
            domain = extract_domain(source_url)

            articles.append({
                "title": art.get("title", ""),
                "description": art.get("description", ""),
                "content": art.get("content", ""),
                "source": art.get("source", {}).get("name", "Unknown"),
                "source_domain": domain,
                "url": source_url,
                "published_at": art.get("publishedAt", ""),
            })

        return articles if articles else None

    except Exception as e:
        print(f"[NewsFetcher] API error: {e}")
        return None


def load_sample_articles(topic: str = "") -> list:
    """Load fallback sample articles from local JSON."""
    try:
        with open(_SAMPLE_FILE, "r") as f:
            data = json.load(f)
        articles = data.get("articles", [])

        # If topic provided, do basic keyword filtering
        if topic:
            keywords = topic.lower().split()
            filtered = []
            for art in articles:
                text = f"{art.get('title', '')} {art.get('description', '')}".lower()
                if any(kw in text for kw in keywords):
                    filtered.append(art)
            # Return filtered if any match, else return all samples
            return filtered if filtered else articles

        return articles
    except Exception as e:
        print(f"[NewsFetcher] Sample load error: {e}")
        return []


def fetch_articles(topic: str, max_articles: int = 20) -> list:
    """
    Primary fetch function. Tries NewsAPI first, falls back to samples.
    """
    # Try live API first
    articles = fetch_from_newsapi(topic, max_articles)

    if articles:
        print(f"[NewsFetcher] Fetched {len(articles)} articles from NewsAPI")
        return articles

    # Fallback to sample data
    print("[NewsFetcher] Falling back to sample articles")
    samples = load_sample_articles(topic)
    return samples
