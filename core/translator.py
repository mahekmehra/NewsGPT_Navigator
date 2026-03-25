"""
NewsGPT Navigator — Translator

Multi-language translation using deep-translator (Google Translate wrapper).
Supports 7 Indian languages + English.
"""

from core.config import settings


def translate_text(text: str, target_language: str) -> str:
    """
    Translate text to the target language.

    Args:
        text: Source text in English
        target_language: Language code (e.g., "hi", "ta", "bn")

    Returns:
        Translated text, or original if translation fails or target is English
    """
    if target_language == "en" or not target_language:
        return text

    if target_language not in settings.SUPPORTED_LANGUAGES:
        print(f"[Translator] Unsupported language: {target_language}")
        return text

    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source="en", target=target_language)

        # Handle long texts by splitting into chunks (Google has a 5000 char limit)
        max_chunk = 4500
        if len(text) <= max_chunk:
            return translator.translate(text)

        # Split into sentences and translate in chunks
        sentences = text.split(". ")
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 2 <= max_chunk:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        translated_chunks = [translator.translate(chunk) for chunk in chunks]
        return " ".join(translated_chunks)

    except Exception as e:
        print(f"[Translator] Error: {e}")
        return text


def get_supported_languages() -> dict:
    """Return dict of supported language codes and names."""
    return settings.SUPPORTED_LANGUAGES.copy()
