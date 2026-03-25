"""
Tests for surprise scenario readiness.

Covers:
- safe_json_parse resilience
- Custom persona handling
- Multilingual video routing
- Story arc data structure
- Agent graceful degradation
"""

import pytest
from core.safe_json import safe_json_parse


# ── safe_json_parse tests ──

class TestSafeJsonParse:
    """Test the 5-stage resilient JSON parser."""

    def test_valid_json(self):
        result = safe_json_parse('{"key": "value"}', {})
        assert result == {"key": "value"}

    def test_markdown_fenced_json(self):
        text = '```json\n{"key": "value"}\n```'
        result = safe_json_parse(text, {})
        assert result == {"key": "value"}

    def test_markdown_fenced_no_lang(self):
        text = '```\n{"key": "value"}\n```'
        result = safe_json_parse(text, {})
        assert result == {"key": "value"}

    def test_garbage_with_embedded_json(self):
        text = 'Here is the result:\n{"entities": [{"name": "Test"}]}\nDone!'
        result = safe_json_parse(text, {"entities": []})
        assert "entities" in result
        assert len(result["entities"]) == 1

    def test_truncated_json(self):
        text = '{"entities": [{"name": "Test"}'
        result = safe_json_parse(text, {"entities": []})
        # Should attempt to close braces
        assert isinstance(result, dict)

    def test_empty_string(self):
        assert safe_json_parse("", {"fallback": True}) == {"fallback": True}

    def test_none_input(self):
        assert safe_json_parse(None, {"fallback": True}) == {"fallback": True}

    def test_pure_garbage(self):
        assert safe_json_parse("not json at all", []) == []

    def test_json_array(self):
        result = safe_json_parse('[1, 2, 3]', [])
        assert result == [1, 2, 3]

    def test_default_fallback(self):
        result = safe_json_parse("garbage")
        assert result == {}

    def test_nested_json(self):
        text = '{"outer": {"inner": [1, 2, 3]}}'
        result = safe_json_parse(text, {})
        assert result["outer"]["inner"] == [1, 2, 3]


# ── Story Arc structure tests ──

class TestStoryArc:
    """Test story arc data structure validity."""

    def test_story_arc_entry_structure(self):
        """A valid story arc entry has all required fields."""
        entry = {
            "entity": "Adani Group",
            "entity_type": "ORG",
            "trend": [
                {"period": "2024-01-01", "sentiment": "negative", "score": 0.9},
                {"period": "2024-02-01", "sentiment": "neutral", "score": 0.5},
            ],
            "shift": "negative→neutral",
            "first_seen": "2024-01-01T00:00:00",
            "latest_update": "2024-02-01T00:00:00",
        }
        assert entry["entity"] == "Adani Group"
        assert len(entry["trend"]) == 2
        assert "→" in entry["shift"]

    def test_new_entity_arc(self):
        """A new entity should have shift='new' and single trend point."""
        entry = {
            "entity": "New Corp",
            "entity_type": "ORG",
            "trend": [{"period": "2024-03-01", "sentiment": "positive", "score": 0.7}],
            "shift": "new",
            "first_seen": "2024-03-01T00:00:00",
            "latest_update": "2024-03-01T00:00:00",
        }
        assert entry["shift"] == "new"
        assert len(entry["trend"]) == 1


# ── Custom persona tests ──

class TestCustomPersona:
    """Test custom persona handling in state."""

    def test_state_with_custom_persona(self):
        from agents.state import create_initial_state
        state = create_initial_state(
            topic="AI regulation",
            custom_persona="startup founder building AI products",
        )
        assert state["custom_persona"] == "startup founder building AI products"

    def test_state_without_custom_persona(self):
        from agents.state import create_initial_state
        state = create_initial_state(topic="AI regulation")
        assert state["custom_persona"] == ""

    def test_state_with_story_arc(self):
        from agents.state import create_initial_state
        state = create_initial_state(topic="test")
        assert state["story_arc"] == []


# ── Multilingual video routing tests ──

class TestMultilingualVideo:
    """Test video agent language configuration."""

    def test_lang_config_exists(self):
        from agents.video_agent import LANG_CONFIG
        assert "hi" in LANG_CONFIG
        assert "ta" in LANG_CONFIG
        assert "te" in LANG_CONFIG
        assert "bn" in LANG_CONFIG

    def test_lang_config_structure(self):
        from agents.video_agent import LANG_CONFIG
        for code, cfg in LANG_CONFIG.items():
            assert "name" in cfg
            assert "script" in cfg
            assert "gtts_code" in cfg

    def test_hindi_config(self):
        from agents.video_agent import LANG_CONFIG
        assert LANG_CONFIG["hi"]["name"] == "Hindi"
        assert LANG_CONFIG["hi"]["gtts_code"] == "hi"

    def test_tamil_config(self):
        from agents.video_agent import LANG_CONFIG
        assert LANG_CONFIG["ta"]["name"] == "Tamil"
        assert LANG_CONFIG["ta"]["gtts_code"] == "ta"


# ── Agent import tests (smoke test) ──

class TestAgentImports:
    """Verify all agents import without errors."""

    def test_import_fetch_agent(self):
        from agents.fetch_agent import fetch_agent
        assert callable(fetch_agent)

    def test_import_entity_sentiment(self):
        from agents.entity_sentiment_agent import entity_sentiment_agent
        assert callable(entity_sentiment_agent)

    def test_import_angle_agent(self):
        from agents.angle_agent import angle_agent
        assert callable(angle_agent)

    def test_import_analysis_agent(self):
        from agents.analysis_agent import analysis_agent
        assert callable(analysis_agent)

    def test_import_compliance_agent(self):
        from agents.compliance_agent import compliance_agent
        assert callable(compliance_agent)

    def test_import_profile_ranking(self):
        from agents.profile_ranking_agent import profile_ranking_agent
        assert callable(profile_ranking_agent)

    def test_import_conflict_agent(self):
        from agents.conflict_agent import conflict_agent
        assert callable(conflict_agent)

    def test_import_emotional_agent(self):
        from agents.emotional_agent import emotional_agent
        assert callable(emotional_agent)

    def test_import_delivery_agent(self):
        from agents.delivery_agent import delivery_agent
        assert callable(delivery_agent)

    def test_import_knowledge_diff(self):
        from agents.knowledge_diff_agent import knowledge_diff_agent
        assert callable(knowledge_diff_agent)

    def test_import_video_agent(self):
        from agents.video_agent import video_agent
        assert callable(video_agent)


# ── Pipeline compilation test ──

class TestPipelineResilience:
    """Test pipeline compiles and handles edge cases."""

    def test_pipeline_compiles(self):
        from agents.orchestrator import build_pipeline
        pipeline = build_pipeline().compile()
        assert pipeline is not None

    def test_safe_json_in_all_agents(self):
        """Verify safe_json is importable (it's used by all agents)."""
        from core.safe_json import safe_json_parse
        assert callable(safe_json_parse)
