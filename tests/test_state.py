"""
Tests for the shared pipeline state schema (10-agent architecture).
"""

from agents.state import PipelineState, create_initial_state


def test_create_initial_state():
    """Initial state should contain all required fields for the 10-agent pipeline."""
    state = create_initial_state("AI regulation")

    # Input fields
    assert state["topic"] == "AI regulation"
    assert state["persona"] == "General"
    assert state["language"] == "en"

    # Fetch agent
    assert state["articles"] == []
    assert state["quality_scores"] == []
    assert state["verified_articles"] == []
    assert state["fetch_success"] == False

    # Entity sentiment agent
    assert state["entity_sentiments"] == []
    assert state["entities_extracted"] == False

    # Angle agent
    assert state["angle_clusters"] == []
    assert state["angle_indexes_built"] == False

    # Analysis agent
    assert state["embeddings_built"] == False
    assert state["analysis"] == {}
    assert state["analysis_success"] == False

    # Compliance agent
    assert state["bias_score"] == 0.0
    assert state["compliance_passed"] == False

    # Profile ranking agent
    assert state["user_profile"] == {}
    assert state["ranked_articles"] == []
    assert state["persona_template"] == ""

    # Conflict agent
    assert state["conflicts"] == []
    assert state["conflicts_detected"] == False

    # Emotional calibration agent
    assert state["emotional_register"] == {}
    assert state["emotion_calibrated"] == False

    # Video agent
    assert state["video_output"] == {}
    assert state["video_generated"] == False
    assert state["videos"] == []

    # Delivery agent
    assert state["briefing"] == {}
    assert state["audio_url"] == ""

    # Story arc / persona
    assert state["custom_persona"] == ""
    assert state["story_arc"] == []
    assert state["persona_context"] == ""

    # Pipeline control
    assert state["retry_count"] == 0
    assert state["max_retries"] == 3
    assert state["pipeline_status"] == "running"
    assert state["audit_trail"] == []
    assert state["error"] == ""


def test_create_state_with_custom_params():
    """State creation should accept custom persona and language."""
    state = create_initial_state(
        topic="climate change",
        persona="Investor",
        language="hi",
    )

    assert state["topic"] == "climate change"
    assert state["persona"] == "Investor"
    assert state["language"] == "hi"


def test_create_state_with_knowledge_session():
    """State creation should accept a knowledge session ID."""
    state = create_initial_state(
        topic="budget analysis",
        knowledge_session_id="test-session-123",
    )
    # knowledge_session_id is a parameter used for story arc loading,
    # it is not stored in the pipeline state itself
    assert state["topic"] == "budget analysis"


def test_state_is_typed_dict():
    """State should behave as a standard Python dict."""
    state = create_initial_state("test")
    assert isinstance(state, dict)

    # Mutable updates on original fields
    state["fetch_success"] = True
    assert state["fetch_success"] == True

    state["articles"] = [{"title": "Test"}]
    assert len(state["articles"]) == 1

    # Mutable updates on agent-specific fields
    state["entity_sentiments"] = [{"entity": "Test Entity", "sentiment": "positive"}]
    assert len(state["entity_sentiments"]) == 1

    state["conflicts"] = [{"conflict_type": "factual", "entity": "Budget"}]
    assert len(state["conflicts"]) == 1

    state["video_generated"] = True
    assert state["video_generated"] == True
