import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from runtime_v7.validation_confidence import compute_validation_confidence


def test_compute_validation_confidence_returns_shadow_fields():
    theme_validation_result = {
        "diagnostics": {
            "average_theme_validation_confidence": 0.72,
        }
    }
    character_validation_result = {
        "diagnostics": {
            "average_character_validation_confidence": 0.65,
        }
    }
    learning_outcome_validation_result = {
        "diagnostics": {
            "average_learning_outcome_validation_confidence": 0.74,
        }
    }

    result = compute_validation_confidence(
        {},
        theme_validation_result,
        character_validation_result,
        learning_outcome_validation_result,
    )

    assert isinstance(result, dict)
    assert "validation_confidence" in result
    assert result["validation_confidence"]["theme_confidence"] == 0.72
    assert result["validation_confidence"]["character_confidence"] == 0.65
    assert result["validation_confidence"]["learning_outcome_confidence"] == 0.74
    assert result["validation_confidence"]["overall_confidence"] == 0.7
    assert result["validation_confidence"]["confidence_band"] == "medium"
    assert result["diagnostics"]["calibrated_theme_validation_confidence"] == 0.72
    assert result["diagnostics"]["calibrated_character_validation_confidence"] == 0.65
    assert result["diagnostics"]["calibrated_learning_outcome_validation_confidence"] == 0.74
    assert result["diagnostics"]["calibrated_overall_validation_confidence"] == 0.7
    assert result["diagnostics"]["validation_confidence_band"] == "medium"
