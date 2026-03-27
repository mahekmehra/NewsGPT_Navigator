"""
NewsGPT Navigator — FastAPI Backend

Main API server with endpoints for topic analysis, audit trail
retrieval, system health checks, and video serving.
Supports all 10 agents.
"""

import uuid
import os
import json
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from agents.delivery_agent import AUDIO_OUTPUT_DIR

from api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    BriefingResponse,
    HealthResponse,
    UserProfileResponse,
    EmotionalRegisterResponse,
    VideoOutputResponse,
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

_sessions: dict = {}


@app.get("/health", response_model=HealthResponse)
async def health_check():
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
    from agents.orchestrator import run_pipeline

    session_id = str(uuid.uuid4())

    try:
        persona = request.persona or "General"
        valid_languages = list(settings.SUPPORTED_LANGUAGES.keys())
        language = request.language if request.language in valid_languages else "en"

        result = run_pipeline(
            topic=request.topic,
            persona=persona,
            language=language,
            knowledge_session_id=request.knowledge_session_id or session_id,
            custom_persona=getattr(request, "custom_persona", ""),
        )

        _sessions[session_id] = {
            "topic": request.topic,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # 🔥 NEW CLEAN MAPPING (PREMIUM ALIGNMENT)
        briefing_data = result.get("briefing") or {}
        briefing = BriefingResponse(**briefing_data) if briefing_data else None

        user_profile = UserProfileResponse(**result.get("user_profile", {})) if result.get("user_profile") else None
        emotional_register = EmotionalRegisterResponse(**result.get("emotional_register", {})) if result.get("emotional_register") else None

        return AnalyzeResponse(
            success=result.get("pipeline_status") == "completed",
            briefing=briefing,
            entity_sentiments=result.get("entity_sentiments", []),
            angle_clusters=result.get("angle_clusters", []),
            user_profile=user_profile,
            conflicts=result.get("conflicts", []),
            emotional_register=emotional_register,
            knowledge_diff=result.get("knowledge_diff", []),
            video_output=result.get("video_output"),
            story_arc=result.get("story_arc", []),
            audit_trail=result.get("audit_trail", []),
            error=result.get("error", ""),
            pipeline_status=result.get("pipeline_status", "unknown"),
            articles_fetched=len(result.get("articles", [])),
            articles_verified=len(result.get("verified_articles", [])),
            verified_articles=result.get("verified_articles", []),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


# --- REDUCED API SURFACE ---


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    safe_name = os.path.basename(filename)
    audio_path = os.path.join(AUDIO_OUTPUT_DIR, safe_name)

    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio not found")

    return FileResponse(audio_path, media_type="audio/mpeg", filename=safe_name)


@app.get("/video/{filename}")
async def get_video(filename: str):
    safe_name = os.path.basename(filename)
    video_path = os.path.join(VIDEO_OUTPUT_DIR, safe_name)

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")

    return FileResponse(video_path, media_type="video/mp4", filename=safe_name)


# Internal session mapping (kept for brief lookups if needed)
# @app.get("/sessions") removed


@app.get("/languages")
async def get_supported_languages():
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in settings.SUPPORTED_LANGUAGES.items()
        ]
    }


@app.get("/personas")
async def get_personas():
    return {
        "personas": [
            {"name": name, "description": prompt}
            for name, prompt in settings.PERSONA_PROMPTS.items()
        ],
        "custom_persona_supported": True,
    }


# @app.get("/stress-test") removed


# --- HISTORY REMOVED ---
