"""
Tests for the compliance (bias detection) agent.
"""

from agents.compliance_agent import _calculate_bias_score, compliance_agent


def test_clean_text_low_bias():
    """Neutral, factual text should have low bias score."""
    text = (
        "The government announced a new infrastructure plan. "
        "According to officials, the plan will cost $500 billion over five years. "
        "Industry leaders stated that the plan would create thousands of jobs."
    )
    result = _calculate_bias_score(text)
    assert result["bias_score"] <= 0.3
    assert result["sensationalism"] == 0.0


def test_sensational_text_high_bias():
    """Sensationalized text should have higher bias score."""
    text = (
        "SHOCKING revelation exposes devastating failure! "
        "This explosive report reveals an unprecedented catastrophic event "
        "that has left experts stunned and terrified."
    )
    result = _calculate_bias_score(text)
    assert result["bias_score"] > 0.3
    assert result["sensationalism"] > 0.0
    assert len(result["flagged_terms"]["sensational"]) > 0


def test_politically_biased_text():
    """Politically one-sided text should trigger bias detection."""
    text = (
        "The far-right extremism continues to rise. "
        "Right-wing extremism poses a major threat to democracy. "
        "Conservative failure has led to systemic problems."
    )
    result = _calculate_bias_score(text)
    assert result["political_skew"] > 0.0


def test_unverified_claims():
    """Text with unverified claims should be flagged."""
    text = (
        "Sources say the company is about to collapse. "
        "Anonymous sources claim the CEO will resign. "
        "Reportedly, the deal fell through. "
        "Rumored changes are coming next week."
    )
    result = _calculate_bias_score(text)
    assert result["unverified_claims"] > 0.0
    assert len(result["flagged_terms"]["unverified"]) > 0


def test_compliance_agent_with_clean_analysis():
    """Compliance agent should pass for clean analysis."""
    state = {
        "analysis": {
            "summary": "The technology sector showed steady growth in Q4. Industry reports indicate a 5% increase in revenue across major companies.",
            "prediction": "Growth is expected to continue into the next quarter based on current trends.",
            "key_entities": ["Apple", "Google", "Microsoft"],
        },
        "retry_count": 0,
        "max_retries": 3,
    }

    result = compliance_agent(state)
    assert result["bias_score"] <= 0.3
    assert result["compliance_passed"] == True


def test_compliance_agent_with_biased_analysis():
    """Compliance agent should fail for biased analysis."""
    state = {
        "analysis": {
            "summary": "SHOCKING explosive report reveals devastating catastrophic failure that is unprecedented and unbelievable!",
            "prediction": "Sources say this terrifying situation will get worse.",
            "key_entities": [],
        },
        "retry_count": 0,
        "max_retries": 3,
    }

    result = compliance_agent(state)
    assert result["bias_score"] > 0.3
    assert result["compliance_passed"] == False
