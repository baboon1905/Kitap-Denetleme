import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional


FAILURE_CAUSE_RULES = [
    ("missing_resolution", lambda ev: not ev.get("resolution_present", True)),
    ("low_concreteness", lambda ev: ev.get("concreteness_score", 0.0) < 0.06),
    ("weak_event_sequence", lambda ev: ev.get("coherence", 0.0) < 0.4 or not ev.get("conflict_present", True)),
    ("theme_summary_disconnect", lambda ev: not ev.get("main_message_present", True)),
    ("evidence_overfitting", lambda ev: ev.get("evidence_concatenation_detected", False)),
    ("weak_character_motivation", lambda ev: ev.get("character_presence", 0.0) < 0.5),
    ("insufficient_narrative_reconstruction", lambda ev: ev.get("summary_quality_score", 0.0) < 65.0),
    ("character_resolution_issue", lambda ev: not ev.get("resolution_present", True) and ev.get("character_presence", 0.0) < 0.7),
]

RECOMMENDED_FIX_AREA = {
    "missing_resolution": "narrative_resolution",
    "low_concreteness": "concreteness_detail",
    "weak_event_sequence": "event_sequence",
    "theme_summary_disconnect": "theme_alignment",
    "evidence_overfitting": "evidence_handling",
    "weak_character_motivation": "character_motivation",
    "insufficient_narrative_reconstruction": "narrative_reconstruction",
    "character_resolution_issue": "character_resolution",
}


def _load_input_artifact(input_path: Path) -> Dict[str, Any]:
    return json.loads(input_path.read_text(encoding="utf-8"))


def _build_book_failure_analysis(book: Dict[str, Any]) -> Dict[str, Any]:
    evaluation = book.get("evaluation", {})
    failed_quality_dimensions: List[str] = []
    if evaluation.get("coherence", 0.0) < 0.4:
        failed_quality_dimensions.append("coherence")
    if evaluation.get("concreteness_score", 0.0) < 0.06:
        failed_quality_dimensions.append("concreteness")
    if not evaluation.get("conflict_present", True):
        failed_quality_dimensions.append("conflict")
    if not evaluation.get("resolution_present", True):
        failed_quality_dimensions.append("resolution")
    if not evaluation.get("main_message_present", True):
        failed_quality_dimensions.append("main_message")
    if evaluation.get("evidence_concatenation_detected", False):
        failed_quality_dimensions.append("evidence_concatenation")
    if evaluation.get("character_presence", 0.0) < 0.5:
        failed_quality_dimensions.append("character_presence")

    likely_root_causes: List[str] = []
    for cause, rule in FAILURE_CAUSE_RULES:
        if rule(evaluation):
            likely_root_causes.append(cause)

    if not likely_root_causes:
        likely_root_causes.append("insufficient_narrative_reconstruction")

    primary_cause = likely_root_causes[0]
    recommended_fix_area = RECOMMENDED_FIX_AREA.get(primary_cause, "narrative_reconstruction")

    return {
        "book_title": book.get("title", ""),
        "summary_quality_score": evaluation.get("summary_quality_score", 0.0),
        "coherence": evaluation.get("coherence", 0.0),
        "concreteness_score": evaluation.get("concreteness_score", 0.0),
        "failed_quality_dimensions": failed_quality_dimensions,
        "likely_root_causes": likely_root_causes,
        "recommended_fix_area": recommended_fix_area,
    }


def build_rc4_sprint7c_failure_analysis_artifact(
    input_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> Dict[str, Any]:
    base = Path(__file__).resolve().parent
    input_path = Path(input_path) if input_path else base / "rc4_sprint7b_real_report_regression_validation.json"
    output_path = Path(output_path) if output_path else base / "rc4_sprint7c_failure_analysis.json"

    artifact_input = _load_input_artifact(input_path)
    book_analyses = [_build_book_failure_analysis(book) for book in artifact_input.get("books", [])]
    failed_books = sum(
        1
        for original_book, analysis in zip(artifact_input.get("books", []), book_analyses)
        if not original_book.get("evaluation", {}).get("passed", False)
        or analysis["summary_quality_score"] < 65.0
    )
    root_causes = [cause for analysis in book_analyses for cause in analysis["likely_root_causes"]]
    common_dimensions = [cause for cause, _ in Counter(root_causes).most_common()]
    primary_root_cause = common_dimensions[0] if common_dimensions else "insufficient_narrative_reconstruction"

    artifact = {
        "sprint": "RC4 Sprint 7C — Failure Analysis",
        "generated_at": "1970-01-01T00:00:00Z",
        "total_books": len(book_analyses),
        "failed_books": failed_books,
        "most_common_failure_dimensions": common_dimensions,
        "primary_root_cause": primary_root_cause,
        "recommended_next_action": "focus_failure_root_causes_in_summary_generation",
        "deterministic": True,
        "books": book_analyses,
    }

    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return artifact


def main() -> None:
    artifact = build_rc4_sprint7c_failure_analysis_artifact()
    print(json.dumps(artifact, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
