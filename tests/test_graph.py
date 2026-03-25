"""
Tests for the LangGraph pipeline compilation — 11 agent nodes.
"""

from agents.orchestrator import build_pipeline


def test_pipeline_compiles():
    """Test that the 11-node pipeline compiles without errors."""
    graph = build_pipeline()
    pipeline = graph.compile()
    assert pipeline is not None


def test_pipeline_has_correct_node_count():
    """Test that the graph has the expected agent nodes."""
    graph = build_pipeline()
    # Agent nodes (not counting retry/abort helper nodes)
    expected_agent_nodes = {
        "fetch",
        "entity_sentiment",
        "angle_decomposition",
        "analysis",
        "compliance",
        "profile_ranking",
        "conflict",
        "emotional_calibration",
        "delivery",
        "knowledge_diff",
        "video",
    }
    # All nodes (including control flow nodes)
    expected_all_nodes = expected_agent_nodes | {
        "retry_fetch",
        "reanalyze",
        "abort",
        "deliver_with_warning",
    }

    graph_nodes = set(graph.nodes.keys())

    # All agent nodes must be present
    for node in expected_agent_nodes:
        assert node in graph_nodes, f"Missing agent node: {node}"

    # All control nodes must be present
    for node in expected_all_nodes:
        assert node in graph_nodes, f"Missing node: {node}"

    # Should have exactly 15 nodes (11 agents + 4 control)
    assert len(graph_nodes) == 15, f"Expected 15 nodes, got {len(graph_nodes)}: {graph_nodes}"
