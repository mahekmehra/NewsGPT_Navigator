"""
NewsGPT Navigator — Source Credibility Checker

Validates news sources against trusted/caution/blocked domain lists.
"""

import json
import os
from urllib.parse import urlparse


_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_SOURCES_FILE = os.path.join(_DATA_DIR, "credible_sources.json")

_credibility_data = None


def _load_sources() -> dict:
    """Load credibility data lazily."""
    global _credibility_data
    if _credibility_data is None:
        with open(_SOURCES_FILE, "r") as f:
            _credibility_data = json.load(f)
    return _credibility_data


def extract_domain(url: str) -> str:
    """Extract base domain from a URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove 'www.' prefix
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def check_credibility(source_domain: str) -> dict:
    """
    Check source credibility against domain lists.

    Returns:
        dict with keys:
        - credibility: "trusted" | "caution" | "blocked" | "unknown"
        - score: float (1.0=trusted, 0.5=unknown, 0.3=caution, 0.0=blocked)
        - domain: the checked domain
    """
    data = _load_sources()
    domain = source_domain.lower().strip()

    if domain in data.get("trusted_domains", []):
        return {"credibility": "trusted", "score": 1.0, "domain": domain}
    elif domain in data.get("caution_domains", []):
        return {"credibility": "caution", "score": 0.3, "domain": domain}
    elif domain in data.get("blocked_domains", []):
        return {"credibility": "blocked", "score": 0.0, "domain": domain}
    else:
        return {"credibility": "unknown", "score": 0.5, "domain": domain}


def is_source_acceptable(source_domain: str) -> bool:
    """Check if a source is acceptable (not blocked)."""
    result = check_credibility(source_domain)
    return result["credibility"] != "blocked"
