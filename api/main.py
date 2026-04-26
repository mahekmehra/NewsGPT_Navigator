"""
NewsGPT Navigator — FastAPI Backend

Main API server with endpoints for topic analysis, audio/video
serving, system health checks, and configuration queries.
Orchestrates the full 10-agent LangGraph pipeline.
"""

import uuid
import os
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from anyio import to_thread
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
    CompareRequest,
    CompareResponse,
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

# In-memory session store for audit trail lookups
_sessions: dict = {}


def _map_pipeline_result(result: dict) -> AnalyzeResponse:
    """Helper to map raw pipeline dict to AnalyzeResponse schema."""
    briefing_data = result.get("briefing") or {}
    briefing = BriefingResponse(**briefing_data) if briefing_data else None

    user_profile = (
        UserProfileResponse(**result.get("user_profile", {}))
        if result.get("user_profile") else None
    )
    emotional_register = (
        EmotionalRegisterResponse(**result.get("emotional_register", {}))
        if result.get("emotional_register") else None
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


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check — returns agent list and version."""
    return HealthResponse(
        status="ok",
        version="2.1.0",
        agents=[
            "fetch", "entity_sentiment", "angle",
            "analysis", "compliance", "profile_ranking",
            "conflict", "emotion", "delivery", "video"
        ],
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_topic(request: AnalyzeRequest):
    """Run the full 10-agent pipeline on a news topic."""
    from agents.orchestrator import run_pipeline

    session_id = str(uuid.uuid4())

    try:
        persona = request.persona or "General"
        valid_languages = list(settings.SUPPORTED_LANGUAGES.keys())
        language = request.language if request.language in valid_languages else "en"

        result = await to_thread.run_sync(
            run_pipeline,
            request.topic,
            persona,
            language,
            request.knowledge_session_id or session_id,
            getattr(request, "custom_persona", "")
        )

        _sessions[session_id] = {
            "topic": request.topic,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return _map_pipeline_result(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@app.post("/compare", response_model=CompareResponse)
async def compare_personas(request: CompareRequest):
    """Run two pipelines in parallel for persona comparison."""
    from agents.orchestrator import run_pipeline

    session_id = request.knowledge_session_id or str(uuid.uuid4())
    valid_languages = list(settings.SUPPORTED_LANGUAGES.keys())
    language = request.language if request.language in valid_languages else "en"

    try:
        # Run both pipelines in parallel using anyio thread pool
        # This allows them to run concurrently without blocking the main event loop
        left_task = to_thread.run_sync(
            run_pipeline, request.topic, request.persona_a, language, session_id
        )
        right_task = to_thread.run_sync(
            run_pipeline, request.topic, request.persona_b, language, session_id
        )

        results = await asyncio.gather(left_task, right_task)
        
        left_res = _map_pipeline_result(results[0])
        right_res = _map_pipeline_result(results[1])

        return CompareResponse(
            success=left_res.success and right_res.success,
            left=left_res,
            right=right_res,
            error=left_res.error or right_res.error
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return CompareResponse(success=False, error=str(e))


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve a generated audio narration MP3."""
    safe_name = os.path.basename(filename)
    audio_path = os.path.join(AUDIO_OUTPUT_DIR, safe_name)

    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio not found")

    return FileResponse(audio_path, media_type="audio/mpeg", filename=safe_name)


@app.get("/video/{filename}")
async def get_video(filename: str):
    """Serve a video file."""
    safe_name = os.path.basename(filename)
    video_path = os.path.join(VIDEO_OUTPUT_DIR, safe_name)

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")

    return FileResponse(video_path, media_type="video/mp4", filename=safe_name)


@app.get("/languages")
async def get_supported_languages():
    """Return all supported translation languages."""
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in settings.SUPPORTED_LANGUAGES.items()
        ]
    }


@app.get("/personas")
async def get_personas():
    """Return available persona presets."""
    return {
        "personas": [
            {"name": name, "description": prompt}
            for name, prompt in settings.PERSONA_PROMPTS.items()
        ],
        "custom_persona_supported": True,
    }


# Serve the React frontend build (if available)
if FRONTEND_DIST.is_dir():
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIST), html=True),
        name="spa",
    )
