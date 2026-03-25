"""
NewsGPT Navigator — Safe JSON Parser

Resilient JSON parsing wrapper that handles malformed LLM output.
Strips markdown fences, extracts JSON blocks via regex, and
always returns a valid fallback — never raises.
"""

import json
import re


def safe_json_parse(text: str, fallback=None):
    """
    Safely parse JSON from LLM output. Handles:
    - Markdown fenced code blocks (```json ... ```)
    - Leading/trailing whitespace and garbage
    - Truncated JSON (best-effort)

    Args:
        text: Raw LLM response string
        fallback: Value to return on failure (default: {})

    Returns:
        Parsed dict/list, or fallback if all parsing fails
    """
    if fallback is None:
        fallback = {}

    if not text or not isinstance(text, str):
        return fallback

    # ── Attempt 1: Direct parse ──
    try:
        return json.loads(text.strip())
    except (json.JSONDecodeError, ValueError):
        pass

    # ── Attempt 2: Strip markdown fences ──
    cleaned = text.strip()
    # Remove ```json ... ``` or ``` ... ```
    cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'\n?```\s*$', '', cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        pass

    # ── Attempt 3: Extract first JSON object {...} ──
    obj_match = re.search(r'\{[\s\S]*\}', cleaned)
    if obj_match:
        try:
            return json.loads(obj_match.group())
        except (json.JSONDecodeError, ValueError):
            pass

    # ── Attempt 4: Extract first JSON array [...] ──
    arr_match = re.search(r'\[[\s\S]*\]', cleaned)
    if arr_match:
        try:
            return json.loads(arr_match.group())
        except (json.JSONDecodeError, ValueError):
            pass

    # ── Attempt 5: Try to fix truncated JSON by closing braces ──
    open_braces = cleaned.count('{') - cleaned.count('}')
    open_brackets = cleaned.count('[') - cleaned.count(']')
    if open_braces > 0 or open_brackets > 0:
        fixed = cleaned + ('}' * open_braces) + (']' * open_brackets)
        try:
            return json.loads(fixed)
        except (json.JSONDecodeError, ValueError):
            pass

    # ── All attempts failed: return fallback ──
    return fallback
