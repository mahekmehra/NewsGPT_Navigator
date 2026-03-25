"""
NewsGPT Navigator — FastAPI Backend

Main API server with endpoints for topic analysis, audit trail
retrieval, system health checks, and video serving.
Supports all 11 agents.
"""

import uuid
import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    BriefingResponse,
    AuditResponse,
    HealthResponse,
    UserProfileResponse,
    EmotionalRegisterResponse,
    VideoOutputResponse,
)
from core.config import settings

app = FastAPI(
    title="NewsGPT Navigator",
    description="Autonomous multi-agent news intelligence platform — 11 agents",
    version="2.0.0",
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store (for demo; production would use Redis/DB)
_sessions: dict = {}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint — lists all 11 agents."""
    return HealthResponse(
        status="ok",
        version="2.0.0",
        agents=[
            "orchestrator", "fetch", "entity_sentiment", "angle_decomposition",
            "analysis", "compliance", "profile_ranking", "conflict",
            "emotional_calibration", "delivery", "knowledge_diff", "video"
        ],
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_topic(request: AnalyzeRequest):
    """
    Run the full NewsGPT 11-agent pipeline on a topic.

    Accepts topic, persona, language, and optional knowledge_session_id.
    Returns full briefing with all agent outputs and audit trail.
    """
    from agents.orchestrator import run_pipeline

    session_id = str(uuid.uuid4())

    try:
        # Accept any persona — no hardcoded validation
        persona = request.persona or "General"

        # Validate language
        valid_languages = list(settings.SUPPORTED_LANGUAGES.keys())
        language = request.language if request.language in valid_languages else "en"

        # Use session_id as knowledge session if none provided
        knowledge_session_id = request.knowledge_session_id or session_id

        # Run the pipeline
        result = run_pipeline(
            topic=request.topic,
            persona=persona,
            language=language,
            knowledge_session_id=knowledge_session_id,
            custom_persona=getattr(request, 'custom_persona', ''),
        )

        # Store session for audit retrieval
        _sessions[session_id] = {
            "topic": request.topic,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Build response
        briefing_data = result.get("briefing", {})
        briefing = BriefingResponse(**briefing_data) if briefing_data else None

        # Build user profile response
        user_profile_data = result.get("user_profile", {})
        user_profile = UserProfileResponse(**user_profile_data) if user_profile_data else None

        # Build emotional register response
        emotional_data = result.get("emotional_register", {})
        emotional_register = EmotionalRegisterResponse(**emotional_data) if emotional_data else None

        # Build video output response
        video_data = result.get("video_output", {})
        video_output = VideoOutputResponse(**video_data) if video_data else None

        return AnalyzeResponse(
            success=result.get("pipeline_status") == "completed",
            briefing=briefing,
            entity_sentiments=result.get("entity_sentiments", []),
            angle_clusters=result.get("angle_clusters", []),
            user_profile=user_profile,
            conflicts=result.get("conflicts", []),
            emotional_register=emotional_register,
            knowledge_diff=result.get("knowledge_diff", []),
            video_output=video_output,
            story_arc=result.get("story_arc", []),
            audit_trail=result.get("audit_trail", []),
            error=result.get("error", ""),
            pipeline_status=result.get("pipeline_status", "unknown"),
            articles_fetched=len(result.get("articles", [])),
            articles_verified=len(result.get("verified_articles", [])),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@app.get("/audit/{session_id}", response_model=AuditResponse)
async def get_audit_trail(session_id: str):
    """Retrieve audit trail for a specific session."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = session["result"]
    audit_trail = result.get("audit_trail", [])

    return AuditResponse(
        topic=session["topic"],
        audit_trail=audit_trail,
        total_entries=len(audit_trail),
    )


@app.get("/video/{session_id}")
async def get_video(session_id: str):
    """Serve the generated video file for a session."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = session["result"]
    video_output = result.get("video_output", {})
    video_path = video_output.get("video_path", "")

    if not video_path or not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=os.path.basename(video_path),
    )


@app.get("/sessions")
async def list_sessions():
    """List all available sessions."""
    sessions = []
    for sid, data in _sessions.items():
        sessions.append({
            "session_id": sid,
            "topic": data["topic"],
            "timestamp": data["timestamp"],
        })
    return {"sessions": sessions}


@app.get("/languages")
async def get_supported_languages():
    """Return supported languages."""
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in settings.SUPPORTED_LANGUAGES.items()
        ]
    }


@app.get("/personas")
async def get_personas():
    """Return available personas."""
    return {
        "personas": [
            {"name": name, "description": prompt}
            for name, prompt in settings.PERSONA_PROMPTS.items()
        ],
        "custom_persona_supported": True,
        "custom_examples": ["Startup Founder", "Journalist", "Policy Analyst", "College Student"]
    }


@app.get("/stress-test")
async def stress_test():
    """
    Quick smoke test: validates all agent imports, safe_json_parse,
    and config sanity. Run before a demo to catch failures early.
    """
    results = {}

    # 1. Check all agent imports
    agent_checks = [
        ("fetch", "agents.fetch_agent"),
        ("entity_sentiment", "agents.entity_sentiment_agent"),
        ("angle", "agents.angle_agent"),
        ("analysis", "agents.analysis_agent"),
        ("compliance", "agents.compliance_agent"),
        ("profile_ranking", "agents.profile_ranking_agent"),
        ("conflict", "agents.conflict_agent"),
        ("emotional", "agents.emotional_agent"),
        ("delivery", "agents.delivery_agent"),
        ("knowledge_diff", "agents.knowledge_diff_agent"),
        ("video", "agents.video_agent"),
    ]
    for name, module in agent_checks:
        try:
            __import__(module)
            results[name] = "ok"
        except Exception as e:
            results[name] = f"FAIL: {e}"

    # 2. Check safe_json_parse
    try:
        from core.safe_json import safe_json_parse
        test_result = safe_json_parse('{"test": true}', {})
        results["safe_json_parse"] = "ok" if test_result.get("test") else "FAIL"
    except Exception as e:
        results["safe_json_parse"] = f"FAIL: {e}"

    # 3. Check pipeline compiles
    try:
        from agents.orchestrator import build_pipeline
        pipeline = build_pipeline().compile()
        results["pipeline_compile"] = "ok"
    except Exception as e:
        results["pipeline_compile"] = f"FAIL: {e}"

    # 4. Check config
    results["groq_api_key"] = "ok" if settings.GROQ_API_KEY else "MISSING"
    results["news_api_key"] = "ok" if settings.NEWS_API_KEY else "MISSING"
    results["languages"] = len(settings.SUPPORTED_LANGUAGES)

    all_ok = all(v == "ok" for k, v in results.items() if k not in ["languages"])
    return {"status": "ready" if all_ok else "issues_found", "checks": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
