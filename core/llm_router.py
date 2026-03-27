"""
NewsGPT Navigator — Smart LLM Router

Routes tasks to llama-3.1-8b-instant (fast) or llama-3.3-70b-versatile (nuanced)
based on task complexity classification.
"""

from groq import Groq
from core.config import settings


_client = None


def _get_client() -> Groq:
    """Lazy-initialize Groq client."""
    global _client
    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


def classify_complexity(articles: list, topic: str) -> str:
    """
    Classify task complexity based on heuristics.

    Returns: "simple" or "complex"
    """
    # Heuristic 1: Article count
    num_articles = len(articles)

    # Heuristic 2: Topic complexity (multi-word = more complex)
    topic_words = len(topic.split())

    # Heuristic 3: Content diversity (unique sources)
    unique_sources = len(set(a.get("source", "") for a in articles))

    # Simple: few articles, single topic focus, few sources
    if num_articles <= 3 and topic_words <= 3 and unique_sources <= 2:
        return "simple"

    return "complex"


def get_model_for_task(complexity: str) -> str:
    """Get the appropriate model name for the complexity level."""
    if complexity == "simple":
        return settings.FAST_MODEL
    return settings.POWER_MODEL


def call_llm(
    prompt: str,
    system_prompt: str = "You are a precise news analyst.",
    complexity: str = "simple",
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """
    Call LLM via Groq with smart model routing.

    Args:
        prompt: User prompt
        system_prompt: System instruction
        complexity: "simple" or "complex"
        temperature: Sampling temperature
        max_tokens: Max response tokens

    Returns:
        LLM response text
    """
    model = get_model_for_task(complexity)

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[LLMRouter] Error with {model}: {e}")
        # If power model fails, try fast model as fallback
        if model == settings.POWER_MODEL:
            try:
                client = _get_client()
                response = client.chat.completions.create(
                    model=settings.FAST_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content.strip()
            except Exception as e2:
                print(f"[LLMRouter] Fallback also failed: {e2}")

        return f"[LLM Error] Could not generate response: {e}"
