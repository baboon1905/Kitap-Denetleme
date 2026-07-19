import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from runtime_v7.validation_coverage import compute_validation_coverage


def test_compute_validation_coverage_returns_shadow_fields():
    payload = {
        "tema_analizi": [{"ad": "cesaret", "kanitlar": [{"alinti": "Kahraman yüzleşti."}], "guven_skoru": 0.82}],
        "ana_karakterler": [{"ad": "Ali", "guven_skoru": 0.9, "ana_karakter_mi": True}],
    }
    theme_validation_result = {
        "theme_validation": [
            {
                "theme": "cesaret",
                "validation": {
                    "supported_by_primary_chain": True,
                    "supported_by_cause_effect": False,
                    "supported_by_conflict": False,
                    "supported_by_resolution": False,
                    "confidence": 0.8,
                },
            }
        ]
    }
    character_validation_result = {
        "character_validation": [
            {
                "character": "Ali",
                "validation": {
                    "supported_by_primary_chain": True,
                    "supported_by_cause_effect": False,
                    "supported_by_conflict": False,
                    "supported_by_resolution": False,
                    "confidence": 0.8,
                },
            }
        ]
    }
    learning_outcome_validation_result = {
        "learning_outcome_validation": []
    }

    result = compute_validation_coverage(
        payload,
        theme_validation_result,
        character_validation_result,
        learning_outcome_validation_result,
    )

    assert isinstance(result, dict)
    assert "validation_coverage" in result
    assert result["validation_coverage"]["theme_coverage"] == 1.0
    assert result["validation_coverage"]["character_coverage"] == 1.0
    assert result["validation_coverage"]["learning_outcome_coverage"] == 0.0
    assert result["validation_coverage"]["overall_coverage"] == 0.67
    assert "missing_learning_outcomes" in result["validation_coverage"]["coverage_reasons"]
    assert result["diagnostics"]["theme_validation_coverage"] == 1.0
    assert result["diagnostics"]["character_validation_coverage"] == 1.0
    assert result["diagnostics"]["learning_outcome_validation_coverage"] == 0.0
    assert result["diagnostics"]["overall_validation_coverage"] == 0.67
    assert result["diagnostics"]["weak_validation_coverage_reason"] == "missing_learning_outcomes"
