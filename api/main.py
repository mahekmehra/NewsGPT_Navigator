"""
NewsGPT Navigator — FastAPI Backend

Main API server with endpoints for topic analysis, audio/video
serving, system health checks, and configuration queries.
Orchestrates the full 10-agent LangGraph pipeline.
"""

import asyncio
import os
import uuid
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from agents.delivery_agent import AUDIO_OUTPUT_DIR

VIDEO_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "video_output"
)
os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "web" / "dist"

from api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    BriefingResponse,
    HealthResponse,
    UserProfileResponse,
    EmotionalRegisterResponse,
)
from core.config import settings

app = FastAPI(
    title="NewsGPT Navigator",
    description="Autonomous multi-agent news intelligence platform",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store for audit trail lookups & small caches
_sessions: Dict[str, Dict[str, Any]] = {}
_ANALYZE_CACHE: "OrderedDict[Tuple[str, str, str], Dict[str, Any]]" = OrderedDict()
_MAX_CACHE_ITEMS = 16
_JOBS: Dict[str, Dict[str, Any]] = {}


def _cache_get(key: Tuple[str, str, str]) -> Dict[str, Any] | None:
    value = _ANALYZE_CACHE.get(key)
    if value is not None:
        _ANALYZE_CACHE.move_to_end(key)
    return value


def _cache_set(key: Tuple[str, str, str], value: Dict[str, Any]) -> None:
    _ANALYZE_CACHE[key] = value
    _ANALYZE_CACHE.move_to_end(key)
    if len(_ANALYZE_CACHE) > _MAX_CACHE_ITEMS:
        _ANALYZE_CACHE.popitem(last=False)


api = APIRouter(prefix="/api")


@api.get("/health", response_model=HealthResponse)
async def health_check():
    """Ultra-fast health endpoint for Render."""
    return HealthResponse(
        status="ok",
        version="2.1.0",
        agents=[
            "fetch",
            "entity_sentiment",
            "angle",
            "analysis",
            "compliance",
            "profile_ranking",
            "conflict",
            "emotion",
            "delivery",
            "video",
        ],
    )


async def _run_pipeline_background(
    job_id: str,
    *,
    topic: str,
    persona: str,
    language: str,
    knowledge_session_id: str,
    custom_persona: str,
):
    """
    Execute the heavy LangGraph pipeline in a worker thread.
    This keeps the main event loop responsive and avoids Render
    health-check timeouts.
    """
    from agents.orchestrator import run_pipeline

    key = (topic, persona, language)

    try:
        cached = _cache_get(key)
        if cached is not None:
            result = cached
        else:
            result = await asyncio.to_thread(
                run_pipeline,
                topic=topic,
                persona=persona,
                language=language,
                knowledge_session_id=knowledge_session_id,
                custom_persona=custom_persona,
            )
            if isinstance(result, dict):
                _cache_set(key, result)

        _sessions[knowledge_session_id] = {
            "topic": topic,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        _JOBS[job_id] = {
            "status": "completed",
            "result": result,
            "error": None,
        }
    except Exception as exc:
        _JOBS[job_id] = {
            "status": "failed",
            "result": None,
            "error": str(exc),
        }


def _map_pipeline_to_response(result: Dict[str, Any]) -> AnalyzeResponse:
    """Convert raw pipeline dict into the public AnalyzeResponse schema."""
    briefing_data = result.get("briefing") or {}
    briefing = BriefingResponse(**briefing_data) if briefing_data else None

    user_profile = (
        UserProfileResponse(**result.get("user_profile", {}))
        if result.get("user_profile")
        else None
    )
    emotional_register = (
        EmotionalRegisterResponse(**result.get("emotional_register", {}))
        if result.get("emotional_register")
        else None
    )

    return AnalyzeResponse(
        success=result.get("pipeline_status") == "completed",
        briefing=briefing,
        entity_sentiments=result.get("entity_sentiments", []),
        angle_clusters=result.get("angle_clusters", []),
        user_profile=user_profile,
        conflicts=result.get("conflicts", []),
        emotional_register=emotional_register,
        story_arc=result.get("story_arc", []),
        audit_trail=result.get("audit_trail", []),
        error=result.get("error", ""),
        pipeline_status=result.get("pipeline_status", "unknown"),
        articles_fetched=len(result.get("articles", [])),
        articles_verified=len(result.get("verified_articles", [])),
        verified_articles=result.get("verified_articles", []),
    )


@api.post("/analyze")
async def analyze_topic(request: AnalyzeRequest):
    """
    Enqueue a non-blocking analysis job.

    Returns quickly with a job_id; the frontend polls /api/analyze/{job_id}
    for the final AnalyzeResponse.
    """
    session_id = request.knowledge_session_id or str(uuid.uuid4())
    persona = request.persona or "General"
    valid_languages = list(settings.SUPPORTED_LANGUAGES.keys())
    language = request.language if request.language in valid_languages else "en"

    job_id = str(uuid.uuid4())
    _JOBS[job_id] = {
        "status": "queued",
        "result": None,
        "error": None,
    }

    asyncio.create_task(
        _run_pipeline_background(
            job_id,
            topic=request.topic,
            persona=persona,
            language=language,
            knowledge_session_id=session_id,
            custom_persona=getattr(request, "custom_persona", "") or "",
        )
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "session_id": session_id,
    }


@api.get("/analyze/{job_id}", response_model=AnalyzeResponse)
async def get_analyze_result(job_id: str):
    job = _JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "completed":
        return AnalyzeResponse(
            success=False,
            briefing=None,
            entity_sentiments=[],
            angle_clusters=[],
            user_profile=None,
            conflicts=[],
            emotional_register=None,
            story_arc=[],
            audit_trail=[],
            error=job.get("error") or "",
            pipeline_status=job["status"],
            articles_fetched=0,
            articles_verified=0,
            verified_articles=[],
        )

    return _map_pipeline_to_response(job["result"] or {})


@api.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve a generated audio narration MP3."""
    safe_name = os.path.basename(filename)
    audio_path = os.path.join(AUDIO_OUTPUT_DIR, safe_name)

    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio not found")

    return FileResponse(audio_path, media_type="audio/mpeg", filename=safe_name)


@api.get("/video/{filename}")
async def get_video(filename: str):
    """Serve a video file."""
    safe_name = os.path.basename(filename)
    video_path = os.path.join(VIDEO_OUTPUT_DIR, safe_name)

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")

    return FileResponse(video_path, media_type="video/mp4", filename=safe_name)


@api.get("/languages")
async def get_supported_languages():
    """Return all supported translation languages."""
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in settings.SUPPORTED_LANGUAGES.items()
        ]
    }


@api.get("/personas")
async def get_personas():
    """Return available persona presets."""
    return {
        "personas": [
            {"name": name, "description": prompt}
            for name, prompt in settings.PERSONA_PROMPTS.items()
        ],
        "custom_persona_supported": True,
    }


app.include_router(api)


# Serve the React frontend build (if available)
if FRONTEND_DIST.is_dir():
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIST), html=True),
        name="spa",
    )
