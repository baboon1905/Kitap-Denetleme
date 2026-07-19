import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from runtime_v7.release_candidate_audit import build_release_candidate_audit


def test_build_release_candidate_audit_structure_and_constraints():
    audit = build_release_candidate_audit(
        books=[
            {"title": "Tavşan Pati", "equal_without_shadow": True},
            {"title": "Büyülü Yastıklar", "equal_without_shadow": True},
            {"title": "Benim Adım Kristof Kolomb", "equal_without_shadow": True},
        ],
        performance_results=[
            {"title": "Tavşan Pati", "checks": {"deterministic_semantic_output": True, "production_payload_unchanged": True, "book_specific_heuristic": False}},
            {"title": "Büyülü Yastıklar", "checks": {"deterministic_semantic_output": True, "production_payload_unchanged": True, "book_specific_heuristic": False}},
            {"title": "Benim Adım Kristof Kolomb", "checks": {"deterministic_semantic_output": True, "production_payload_unchanged": True, "book_specific_heuristic": False}},
        ],
        recommendation_results=[
            {"title": "Tavşan Pati", "recommendation_checks": {"deterministic": True, "production_payload_unchanged": True, "book_specific_heuristic": False}},
            {"title": "Büyülü Yastıklar", "recommendation_checks": {"deterministic": True, "production_payload_unchanged": True, "book_specific_heuristic": False}},
            {"title": "Benim Adım Kristof Kolomb", "recommendation_checks": {"deterministic": True, "production_payload_unchanged": True, "book_specific_heuristic": False}},
        ],
    )

    assert isinstance(audit, dict)
    assert "release_candidate_audit" in audit
    rc = audit["release_candidate_audit"]
    assert rc["overall_status"] in {"ready", "needs_work"}
    assert rc["completed_phases"]
    assert rc["missing_requirements"] == []
    assert rc["quality_summary"]["equal_without_shadow"] is True
    assert rc["performance_summary"]["deterministic_semantic_output"] is True
    assert rc["test_summary"]["books_tested"] == 3
    assert rc["confidence"] >= 0.0

    payload = json.dumps(audit, ensure_ascii=False)
    assert "_runtime_v7_shadow" not in payload
