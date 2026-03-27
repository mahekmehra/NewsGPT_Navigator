"""
Tests for the LangGraph pipeline compilation — 10 agent nodes.
"""

from agents.orchestrator import build_pipeline


def test_pipeline_compiles():
    """Test that the pipeline compiles without errors."""
    graph = build_pipeline()
    pipeline = graph.compile()
    assert pipeline is not None


def test_pipeline_has_correct_node_count():
    """Test that the graph has the expected agent nodes."""
    graph = build_pipeline()

    # Actual agent node names (matching orchestrator.py)
    expected_agent_nodes = {
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
    }

    # Control flow nodes
    expected_control_nodes = {
        "retry_fetch",
        "reanalyze",
        "abort",
        "deliver_with_warning",
    }

    expected_all_nodes = expected_agent_nodes | expected_control_nodes
    graph_nodes = set(graph.nodes.keys())

    # All agent nodes must be present
    for node in expected_agent_nodes:
        assert node in graph_nodes, f"Missing agent node: {node}"

    # All control nodes must be present
    for node in expected_control_nodes:
        assert node in graph_nodes, f"Missing control node: {node}"

    # Should have exactly 14 nodes (10 agents + 4 control)
    assert len(graph_nodes) == 14, f"Expected 14 nodes, got {len(graph_nodes)}: {graph_nodes}"
