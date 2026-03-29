"""
NewsGPT Navigator — Configuration

Central settings loaded from .env with sensible defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings from environment."""

    # ── API Keys ──
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")

    # ── LLM Models (Groq) ──
    FAST_MODEL: str = "llama-3.1-8b-instant"       # Simple tasks
    POWER_MODEL: str = "llama-3.3-70b-versatile"   # Complex tasks

    # ── Thresholds ──
    QUALITY_THRESHOLD: float = float(os.getenv("QUALITY_THRESHOLD", "0.4"))
    BIAS_THRESHOLD: float = float(os.getenv("BIAS_THRESHOLD", "0.3"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

    # ── Defaults ──
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")
    DEFAULT_PERSONA: str = os.getenv("DEFAULT_PERSONA", "General")

    # ── NewsAPI ──
    NEWS_API_BASE_URL: str = "https://newsapi.org/v2"
    MAX_ARTICLES: int = 20

    # ── Embeddings ──
    EMBEDDING_MODEL: str = "paraphrase-MiniLM-L3-v2"  # Lighter (~45MB) model for Render Free Tier
    TOP_K_RESULTS: int = 5

    # ── Translation ──
    SUPPORTED_LANGUAGES: dict = {
        "en": "english",
        "hi": "hindi",
        "pa": "punjabi",
        "ta": "tamil",
        "bn": "bengali",
        "te": "telugu",
        "kn": "kannada",
        "mr": "marathi",
    }

    # ── Personas ──
    PERSONA_PROMPTS: dict = {
        "Student": "Explain in simple, clear language suitable for a college student. Use analogies and examples. Focus on learning through explanation of concepts.",
        "Investor": "Focus on market impact, financial implications, risks, and opportunities. Provide actionable insights with a data-driven outlook.",
        "CFO": "Focus on macroeconomic impact, financial risk, regulatory compliance, and strategic implications for executive decision-making.",
        "Beginner": "Use very simple language, avoid jargon, explain every concept. Suitable for someone new to the topic.",
        "General": "Provide a balanced, comprehensive briefing suitable for a general professional audience.",
    }


settings = Settings()
