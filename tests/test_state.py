"""
Tests for the shared state schema — 11 agent version.
"""

from agents.state import PipelineState, create_initial_state


def test_create_initial_state():
    """Test that initial state has all required fields for 11 agents."""
    state = create_initial_state("AI regulation")

    # Original fields
    assert state["topic"] == "AI regulation"
    assert state["persona"] == "General"
    assert state["language"] == "en"
    assert state["articles"] == []
    assert state["quality_scores"] == []
    assert state["verified_articles"] == []
    assert state["fetch_success"] == False
    assert state["embeddings_built"] == False
    assert state["analysis"] == {}
    assert state["analysis_success"] == False
    assert state["bias_score"] == 0.0
    assert state["compliance_passed"] == False
    assert state["briefing"] == {}
    assert state["retry_count"] == 0
    assert state["max_retries"] == 3
    assert state["pipeline_status"] == "running"
    assert state["audit_trail"] == []
    assert state["error"] == ""

    # New agent fields
    assert state["entity_sentiments"] == []
    assert state["entities_extracted"] == False
    assert state["angle_clusters"] == []
    assert state["angle_indexes_built"] == False
    assert state["user_profile"] == {}
    assert state["ranked_articles"] == []
    assert state["persona_template"] == ""
    assert state["conflicts"] == []
    assert state["conflicts_detected"] == False
    assert state["emotional_register"] == {}
    assert state["emotion_calibrated"] == False
    assert state["knowledge_diff"] == []
    assert state["knowledge_session_id"] == ""
    assert state["knowledge_updated"] == False
    assert state["video_output"] == {}
    assert state["video_generated"] == False
    assert state["custom_persona"] == ""
    assert state["story_arc"] == []
    assert state["persona_context"] == ""


def test_create_state_with_custom_params():
    """Test state creation with custom persona and language."""
    state = create_initial_state(
        topic="climate change",
        persona="Investor",
        language="hi",
    )

    assert state["topic"] == "climate change"
    assert state["persona"] == "Investor"
    assert state["language"] == "hi"


def test_create_state_with_knowledge_session():
    """Test state creation with knowledge session ID."""
    state = create_initial_state(
        topic="budget analysis",
        knowledge_session_id="test-session-123",
    )
    assert state["knowledge_session_id"] == "test-session-123"


def test_state_is_typed_dict():
    """Verify state behaves as a dict."""
    state = create_initial_state("test")
    assert isinstance(state, dict)

    # Can update original fields
    state["fetch_success"] = True
    assert state["fetch_success"] == True

    state["articles"] = [{"title": "Test"}]
    assert len(state["articles"]) == 1

    # Can update new agent fields
    state["entity_sentiments"] = [{"entity": "Test Entity", "sentiment": "positive"}]
    assert len(state["entity_sentiments"]) == 1

    state["conflicts"] = [{"conflict_type": "factual", "entity": "Budget"}]
    assert len(state["conflicts"]) == 1

    state["video_generated"] = True
    assert state["video_generated"] == True
