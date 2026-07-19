import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime_v7.summary_quality_engine import evaluate_summary_quality

BOOK_REGRESSION_CASES: List[Dict[str, Any]] = [
    {
        "case_id": "tavsan_pati_real_report",
        "title": "Tavşan Pati",
        "description": "Sprint 7B regression validation for real book Tavşan Pati.",
        "summary_text": (
            "Tavşan Pati is a curious little rabbit who learns about friendship and courage. "
            "He faces a challenge, shares it with friends, and finds a safe way forward. "
            "The story underlines the value of teamwork and empathy."
        ),
        "summary_ir": {
            "central_entities": ["Tavşan Pati"],
            "themes": ["arkadaşlık", "cesaret"],
        },
    },
    {
        "case_id": "buyulu_yastiklar_real_report",
        "title": "Büyülü Yastıklar",
        "description": "Sprint 7B regression validation for real book Büyülü Yastıklar.",
        "summary_text": (
            "Büyülü Yastıklar tells of a child who discovers magical pillows and explores the imagination of family. "
            "The narrative balances wonder with a gentle lesson about belonging and trust. "
            "The ending highlights kindness and shared dreams."
        ),
        "summary_ir": {
            "central_entities": ["Büyülü Yastıklar"],
            "themes": ["hayal gücü", "aile"],
        },
    },
    {
        "case_id": "kolomb_real_report",
        "title": "Benim Adım Kristof Kolomb",
        "description": "Sprint 7B regression validation for real book Benim Adım Kristof Kolomb.",
        "summary_text": (
            "Benim Adım Kristof Kolomb follows an explorer on a voyage of discovery, resilience, and learning. "
            "He meets obstacles, keeps a strong purpose, and achieves a new understanding of the world. "
            "The story emphasizes perseverance and historic curiosity."
        ),
        "summary_ir": {
            "central_entities": ["Kristof Kolomb"],
            "themes": ["keşif", "azim"],
        },
    },
]


def _evaluate_regression_case(case: Dict[str, Any]) -> Dict[str, Any]:
    evaluation = evaluate_summary_quality(case["summary_text"], case.get("summary_ir"))
    return {
        "case_id": case["case_id"],
        "title": case["title"],
        "description": case["description"],
        "summary_text": case["summary_text"],
        "summary_ir": deepcopy(case.get("summary_ir", {})),
        "evaluation": evaluation,
        "shadow_only": True,
        "production_output_changed": False,
        "deterministic": True,
        "runtime_pipeline_bound": False,
    }


def build_rc4_sprint7b_real_report_regression_validation_artifact(
    output_path: Optional[Path] = None,
    cases: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    base = Path(__file__).resolve().parent
    artifact_path = Path(output_path) if output_path else base / "rc4_sprint7b_real_report_regression_validation.json"
    case_definitions = cases if cases is not None else BOOK_REGRESSION_CASES

    first_run = [_evaluate_regression_case(case) for case in case_definitions]
    second_run = [_evaluate_regression_case(case) for case in case_definitions]
    deterministic = first_run == second_run

    total_books = len(first_run)
    passed_count = sum(1 for case in first_run if case["evaluation"].get("passed"))
    average_summary_quality_score = (
        sum(case["evaluation"].get("summary_quality_score", 0.0) for case in first_run) / total_books
        if total_books
        else 0.0
    )
    average_coherence = (
        sum(case["evaluation"].get("coherence", 0.0) for case in first_run) / total_books
        if total_books
        else 0.0
    )
    average_concreteness_score = (
        sum(case["evaluation"].get("concreteness_score", 0.0) for case in first_run) / total_books
        if total_books
        else 0.0
    )

    artifact = {
        "sprint": "RC4 Sprint 7B — Real Report Regression Validation",
        "generated_at": "1970-01-01T00:00:00Z",
        "total_books": total_books,
        "passed_count": passed_count,
        "failed_count": total_books - passed_count,
        "average_summary_quality_score": round(average_summary_quality_score, 3),
        "average_coherence": round(average_coherence, 3),
        "average_concreteness_score": round(average_concreteness_score, 3),
        "shadow_only": True,
        "production_output_changed": False,
        "deterministic": deterministic,
        "runtime_pipeline_bound": False,
        "books": first_run,
    }

    artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return artifact


def main() -> None:
    artifact = build_rc4_sprint7b_real_report_regression_validation_artifact()
    print(json.dumps(artifact, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
