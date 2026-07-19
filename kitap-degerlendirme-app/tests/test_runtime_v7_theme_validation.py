import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from runtime_v7.theme_validation import compute_theme_validation


def test_compute_theme_validation_returns_shadow_fields():
    payload = {
        "tema_analizi": [
            {
                "ad": "cesaret",
                "kanitlar": [
                    {"alinti": "Kahraman tehlikeyle yüzleşti."}
                ],
                "guven_skoru": 0.82,
            }
        ]
    }
    narrative_chains = {"chain_count": 1, "chain_confidence": 0.7}
    cause_effect = {"cause_effect_relations": [{"cause_event_id": "0:Kahraman", "effect_event_id": "1:Zafer", "confidence": 0.75}]}
    conflict_graph = {"conflicts": [{"conflict_id": "conflict-001", "confidence": 0.7}]}
    resolution = {"status": "resolved", "confidence": 0.8}

    result = compute_theme_validation(payload, narrative_chains, cause_effect, conflict_graph, resolution)

    assert isinstance(result, dict)
    assert "theme_validation" in result
    assert "diagnostics" in result
    assert result["diagnostics"]["validated_theme_count"] == 1
    assert result["diagnostics"]["primary_chain_supported_theme_count"] == 1
    assert result["diagnostics"]["conflict_supported_theme_count"] == 1
    assert result["diagnostics"]["resolution_supported_theme_count"] == 1
    assert result["theme_validation"][0]["theme"] == "cesaret"
    assert result["theme_validation"][0]["validation"]["supported_by_primary_chain"] is True
    assert result["theme_validation"][0]["validation"]["confidence"] >= 0.8
