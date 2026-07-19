import pytest

from runtime_v7.learning_outcome_validation import compute_learning_outcome_validation


def test_compute_learning_outcome_validation_returns_shadow_fields():
    payload = {
        "kazanim_analizi": [
            {
                "kazanim": "Öğrenci metinden sonuç çıkarır.",
                "kanitlar": [
                    {"alinti": "Metindeki kahraman sorunun çözümünü anlattı."}
                ],
                "guven_skoru": 0.85,
            }
        ]
    }
    narrative_chains = {"chain_count": 1, "chain_confidence": 0.76}
    cause_effect = {"cause_effect_relations": [{"cause_event_id": "0:Başlangıç", "effect_event_id": "1:Sonuç"}]}
    conflict_graph = {"conflicts": [{"conflict_id": "c1", "confidence": 0.7}]}
    primary_conflict = {"participants": ["Ali", "Veli"]}
    resolution = {"status": "resolved", "confidence": 0.88}

    result = compute_learning_outcome_validation(
        payload,
        narrative_chains,
        cause_effect,
        conflict_graph,
        primary_conflict,
        resolution,
    )

    assert isinstance(result, dict)
    assert "learning_outcome_validation" in result
    assert "diagnostics" in result
    assert result["diagnostics"]["validated_learning_outcome_count"] == 1
    assert result["diagnostics"]["primary_chain_supported_outcome_count"] == 1
    assert result["diagnostics"]["cause_effect_supported_outcome_count"] == 1
    assert result["diagnostics"]["conflict_supported_outcome_count"] == 1
    assert result["diagnostics"]["resolution_supported_outcome_count"] == 1
    assert result["diagnostics"]["average_learning_outcome_validation_confidence"] >= 0.0
    assert result["learning_outcome_validation"][0]["learning_outcome"] == "Öğrenci metinden sonuç çıkarır."
    assert result["learning_outcome_validation"][0]["validation"]["supported_by_primary_chain"] is True
    assert result["learning_outcome_validation"][0]["validation"]["supported_by_resolution"] is True
