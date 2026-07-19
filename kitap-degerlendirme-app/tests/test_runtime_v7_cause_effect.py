import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from runtime_v7.cause_effect import build_cause_effect_relations


def test_build_cause_effect_relations_generates_shadow_metrics():
    narrative_chains = {
        "chains": [
            {"events": ["0:begin", "1:middle", "2:end"], "length": 3, "confidence": 0.9}
        ],
        "chain_count": 1,
        "largest_chain_size": 3,
        "isolated_event_count": 0,
        "average_chain_length": 3.0,
        "chain_confidence": 0.9,
    }

    result = build_cause_effect_relations(narrative_chains)

    assert result["diagnostics"]["cause_effect_count"] == 2
    assert result["diagnostics"]["average_cause_effect_confidence"] >= 0.55
    assert result["diagnostics"]["weak_causal_reason"] == "sufficient"
    assert result["cause_effect_relations"][0]["relation_type"] == "sequential_inference"
