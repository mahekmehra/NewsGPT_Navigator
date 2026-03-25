"""
NewsGPT Navigator — Video + Vernacular Agent (UNIQUE)

Multilingual script → jargon clean → TTS → moviepy → MP4 in under 60 seconds.
Supports Hindi, Tamil, Telugu, Bengali.
Uses 8B model for script generation, gTTS for audio, moviepy for video.
"""

import json
import os
import time
import tempfile
from datetime import datetime, timezone
from agents.state import PipelineState

# Pre-create output directory
VIDEO_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "video_output"
)
os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)

# Pre-load jargon map at module level for speed
JARGON_MAP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "jargon_map.json"
)
_jargon_maps = {}
try:
    with open(JARGON_MAP_PATH, "r", encoding="utf-8") as f:
        _jargon_data = json.load(f)
        _jargon_maps["hi"] = _jargon_data.get("mappings", {})
        _jargon_maps["ta"] = _jargon_data.get("tamil", {})
        _jargon_maps["te"] = _jargon_data.get("telugu", {})
        _jargon_maps["bn"] = _jargon_data.get("bengali", {})
except Exception:
    pass

# Language configuration for script generation
LANG_CONFIG = {
    "hi": {"name": "Hindi", "script": "Devanagari", "gtts_code": "hi"},
    "ta": {"name": "Tamil", "script": "Tamil", "gtts_code": "ta"},
    "te": {"name": "Telugu", "script": "Telugu", "gtts_code": "te"},
    "bn": {"name": "Bengali", "script": "Bengali", "gtts_code": "bn"},
}

# Pre-create background image at module level (Pillow)
_bg_image_path = None
try:
    from PIL import Image, ImageDraw, ImageFont
    _bg = Image.new("RGB", (1280, 720), color=(15, 23, 42))  # Dark slate
    draw = ImageDraw.Draw(_bg)
    # Add gradient-like bars
    for y in range(720):
        r = int(15 + (y / 720) * 20)
        g = int(23 + (y / 720) * 15)
        b = int(42 + (y / 720) * 30)
        draw.line([(0, y), (1280, y)], fill=(r, g, b))
    # Add NewsGPT branding area
    draw.rectangle([(40, 600), (400, 680)], fill=(59, 130, 246))
    # Save to temp
    _bg_image_path = os.path.join(tempfile.gettempdir(), "newsgpt_bg.png")
    _bg.save(_bg_image_path)
except Exception:
    pass


def _clean_jargon(text: str, lang: str = "hi") -> str:
    """Replace English financial jargon with language-specific equivalents."""
    jargon_map = _jargon_maps.get(lang, _jargon_maps.get("hi", {}))
    if not jargon_map:
        return text
    result = text
    for eng, translated in jargon_map.items():
        result = result.replace(eng, translated)
    return result


def video_agent(state: PipelineState) -> dict:
    """
    Video agent node for the LangGraph pipeline.

    UNIQUE AGENT — Full video pipeline:
    1. Generate Hindi news script via LLM (8B model for speed)
    2. Clean jargon using data/jargon_map.json
    3. TTS via gTTS → temp audio file
    4. moviepy: background image + audio → MP4 (preset='ultrafast')
    5. Save to data/video_output/

    Target: under 60 seconds wall time.
    """
    from core.llm_router import call_llm

    analysis = state.get("analysis", {})
    emotional_register = state.get("emotional_register", {})
    topic = state.get("topic", "")
    language = state.get("language", "hi")  # Default to Hindi for video
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.time()

    # Determine video language (fallback to Hindi if not supported)
    lang_cfg = LANG_CONFIG.get(language, LANG_CONFIG["hi"])
    video_lang = language if language in LANG_CONFIG else "hi"

    audit_entry = {
        "timestamp": timestamp,
        "agent": "video",
        "action": "generate_video",
        "inputs": {"topic": topic},
        "outputs": {},
    }

    try:
        summary = analysis.get("summary", "")
        prediction = analysis.get("prediction", "")
        tone_guidance = emotional_register.get("tone_guidance", "Deliver in a balanced, informative tone.")
        register = emotional_register.get("register", "neutral")

        if not summary:
            audit_entry["outputs"] = {"error": "No analysis summary for video generation"}
            return {
                "video_output": {},
                "video_generated": False,
                "current_agent": "video",
                "audit_trail": [audit_entry],
            }

        # ── Step 1: Generate script via LLM (8B model) in target language ──
        script_prompt = f"""Write a 60-second {lang_cfg['name']} news script about "{topic}".

CONTENT TO COVER:
Summary: {summary[:1500]}
Prediction: {prediction[:300]}

TONE: {tone_guidance}
REGISTER: {register}

Rules:
- Write in simple {lang_cfg['name']} ({lang_cfg['script']} script)
- Keep under 150 words (approximately 60 seconds when spoken)
- Opening hook, main points, closing prediction
- No English words for common terms (use {lang_cfg['name']} equivalents)
- Format as a continuous script for a news anchor

Write ONLY the {lang_cfg['name']} script, nothing else."""

        hindi_script = call_llm(
            prompt=script_prompt,
            system_prompt=f"You are a {lang_cfg['name']} news script writer. Write natural, conversational {lang_cfg['name']} suitable for TTS.",
            complexity="simple",  # Use 8B model for speed
            max_tokens=512,
        )

        # Also keep English version
        english_script = f"Topic: {topic}\n\nSummary: {summary[:500]}\n\nPrediction: {prediction[:200]}"

        # ── Step 2: Clean jargon ──
        cleaned_script = _clean_jargon(hindi_script, video_lang)
        jargon_cleaned = cleaned_script != hindi_script

        # ── Step 3: TTS via gTTS (multilingual) ──
        audio_path = os.path.join(tempfile.gettempdir(), f"newsgpt_tts_{int(time.time())}.mp3")
        try:
            from gtts import gTTS
            tts = gTTS(text=cleaned_script, lang=lang_cfg["gtts_code"], slow=False)
            tts.save(audio_path)
        except Exception as tts_err:
            # Fallback: generate silent placeholder
            audit_entry["outputs"]["tts_error"] = str(tts_err)
            # Create a minimal placeholder audio
            audio_path = None

        # ── Step 4: moviepy → MP4 ──
        video_filename = f"newsgpt_{topic.replace(' ', '_')[:30]}_{int(time.time())}.mp4"
        video_path = os.path.join(VIDEO_OUTPUT_DIR, video_filename)
        duration_seconds = 0.0

        try:
            from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip

            if audio_path and os.path.exists(audio_path):
                audio_clip = AudioFileClip(audio_path)
                duration_seconds = audio_clip.duration
            else:
                audio_clip = None
                duration_seconds = 30.0  # Default 30s if no audio

            # Use pre-created background image
            bg_path = _bg_image_path or os.path.join(tempfile.gettempdir(), "newsgpt_bg.png")
            if not os.path.exists(bg_path):
                # Fallback: create simple background
                from PIL import Image
                bg = Image.new("RGB", (1280, 720), color=(15, 23, 42))
                bg.save(bg_path)

            img_clip = ImageClip(bg_path).set_duration(duration_seconds)

            if audio_clip:
                video = img_clip.set_audio(audio_clip)
            else:
                video = img_clip

            video.write_videofile(
                video_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                preset="ultrafast",
                logger=None,  # Suppress moviepy output
            )

            # Cleanup
            if audio_clip:
                audio_clip.close()
            video.close()
            img_clip.close()

        except Exception as video_err:
            audit_entry["outputs"]["video_error"] = str(video_err)
            video_path = ""
            duration_seconds = 0.0

        # ── Step 5: Build output ──
        generation_time = time.time() - start_time

        video_output = {
            "script_hindi": cleaned_script,
            "script_english": english_script,
            "script_language": lang_cfg["name"],
            "audio_path": audio_path or "",
            "video_path": video_path,
            "duration_seconds": round(duration_seconds, 2),
            "generation_time": round(generation_time, 2),
            "jargon_cleaned": jargon_cleaned,
        }

        audit_entry["outputs"] = {
            "duration_seconds": round(duration_seconds, 2),
            "generation_time_seconds": round(generation_time, 2),
            "under_60s": generation_time < 60,
            "video_generated": bool(video_path),
            "jargon_cleaned": jargon_cleaned,
        }

        return {
            "video_output": video_output,
            "video_generated": bool(video_path),
            "current_agent": "video",
            "error": "",
            "audit_trail": [audit_entry],
        }

    except Exception as e:
        generation_time = time.time() - start_time
        audit_entry["outputs"] = {"error": str(e), "generation_time": round(generation_time, 2)}
        return {
            "video_output": {},
            "video_generated": False,
            "current_agent": "video",
            "error": f"Video agent error: {e}",
            "audit_trail": [audit_entry],
        }
