"""
Tests for the fetch agent and news fetcher utility.
"""

from agents.fetch_agent import _score_article, fetch_agent
from core.credibility import check_credibility, is_source_acceptable


def test_score_article_high_quality():
    """Article with good relevance, recency, and length should score high."""
    from datetime import datetime, timezone

    article = {
        "title": "AI Regulation Framework Announced",
        "description": "New AI regulation announced by EU and US officials.",
        "content": "x" * 600,  # Long content
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    score = _score_article(article, "AI regulation")
    assert score >= 0.5


def test_score_article_low_quality():
    """Irrelevant, old, short article should score low."""
    article = {
        "title": "Recipe for Chocolate Cake",
        "description": "Baking tips",
        "content": "Short",
        "published_at": "2020-01-01T00:00:00Z",
    }
    score = _score_article(article, "AI regulation")
    assert score < 0.4


def test_credibility_trusted():
    """Trusted domains should return high scores."""
    result = check_credibility("reuters.com")
    assert result["credibility"] == "trusted"
    assert result["score"] == 1.0


def test_credibility_blocked():
    """Blocked domains should return zero score."""
    result = check_credibility("infowars.com")
    assert result["credibility"] == "blocked"
    assert result["score"] == 0.0


def test_credibility_unknown():
    """Unknown domains should return moderate score."""
    result = check_credibility("randomnews.example.com")
    assert result["credibility"] == "unknown"
    assert result["score"] == 0.5


def test_is_source_acceptable():
    """Blocked sources should not be acceptable."""
    assert is_source_acceptable("reuters.com") == True
    assert is_source_acceptable("infowars.com") == False
    assert is_source_acceptable("random.com") == True


def test_fetch_agent_with_fallback():
    """Fetch agent should work with fallback sample data."""
    state = {
        "topic": "AI regulation",
        "retry_count": 0,
        "max_retries": 3,
    }

    result = fetch_agent(state)
    assert "articles" in result
    assert "audit_trail" in result
    assert len(result["audit_trail"]) == 1
    assert result["audit_trail"][0]["agent"] == "fetch"
