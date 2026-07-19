import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from runtime_v7.character_validation import compute_character_validation


def test_compute_character_validation_returns_shadow_fields():
    payload = {
        "ana_karakterler": [
            {"ad": "Ali", "guven_skoru": 0.9, "ana_karakter_mi": True},
            {"ad": "Veli", "guven_skoru": 0.7},
        ],
        "event_graph": [
            {"actors": ["Ali", "Veli"], "action": "fights", "conflict": "clash"},
            {"actors": ["Ali"], "action": "rescues", "outcome": "safe"},
        ],
    }
    narrative_graph = {
        "nodes": [
            {"idx": 0, "actors": ["Ali", "Veli"]},
            {"idx": 1, "actors": ["Ali"]},
        ]
    }
    narrative_chains = {
        "chains": [
            {"events": ["0:fights", "1:rescues"], "length": 2, "confidence": 0.8}
        ],
        "chain_count": 1,
        "chain_confidence": 0.8,
    }
    cause_effect = {
        "cause_effect_relations": [
            {"cause_event_id": "0:fights", "effect_event_id": "1:rescues", "confidence": 0.75}
        ]
    }
    conflict_graph = {
        "conflicts": [
            {"conflict_id": "conflict-001", "participants": ["Ali", "Veli"], "confidence": 0.75}
        ]
    }
    primary_conflict = {
        "participants": ["Ali", "Veli"],
        "confidence": 0.75,
    }
    resolution = {"status": "resolved", "confidence": 0.8}

    result = compute_character_validation(
        payload,
        narrative_graph,
        narrative_chains,
        cause_effect,
        conflict_graph,
        primary_conflict,
        resolution,
    )

    assert isinstance(result, dict)
    assert "character_validation" in result
    assert "diagnostics" in result
    assert result["diagnostics"]["validated_character_count"] == 2
    assert result["diagnostics"]["primary_chain_character_count"] == 2
    assert result["diagnostics"]["primary_conflict_character_count"] == 2
    assert result["diagnostics"]["resolution_character_count"] == 2
    assert result["diagnostics"]["average_character_validation_confidence"] >= 0.0
    assert result["character_validation"][0]["character"] == "Ali"
    assert result["character_validation"][0]["validation"]["supported_by_primary_chain"] is True
    assert result["character_validation"][0]["validation"]["supported_by_resolution"] is True
