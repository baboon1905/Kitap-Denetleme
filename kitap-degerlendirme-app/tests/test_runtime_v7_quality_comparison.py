import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from runtime_v7.quality_comparison import compute_quality_comparison


def test_compute_quality_comparison_returns_shadow_fields():
    production_quality = {
        "theme_validation_coverage": 0.6,
        "character_validation_coverage": 0.5,
        "learning_outcome_validation_coverage": 0.3,
        "overall_validation_coverage": 0.47,
        "calibrated_overall_validation_confidence": 0.5,
    }
    shadow_quality = {
        "theme_validation_coverage": 0.8,
        "character_validation_coverage": 0.7,
        "learning_outcome_validation_coverage": 0.4,
        "overall_validation_coverage": 0.63,
        "calibrated_overall_validation_confidence": 0.72,
    }

    result = compute_quality_comparison(production_quality, shadow_quality)

    assert isinstance(result, dict)
    assert "quality_comparison" in result
    assert result["quality_comparison"]["theme_validation_delta"] == 0.2
    assert result["quality_comparison"]["character_validation_delta"] == 0.2
    assert result["quality_comparison"]["learning_outcome_validation_delta"] == 0.1
    assert result["quality_comparison"]["coverage_delta"] == 0.16
    assert result["quality_comparison"]["confidence_delta"] == 0.22
    assert result["quality_comparison"]["overall_quality_delta"] == 0.18
    assert result["diagnostics"]["overall_quality_delta"] == 0.18
    assert result["diagnostics"]["quality_improvement_detected"] is True
    assert result["diagnostics"]["comparison_confidence"] == 0.68
