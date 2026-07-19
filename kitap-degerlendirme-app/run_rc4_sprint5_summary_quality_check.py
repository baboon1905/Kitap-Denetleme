import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime_v7.summary_quality_engine import evaluate_summary_quality

REGRESSION_SUMMARIES: List[Dict[str, Any]] = [
    {
        "case_id": "tavsan-pati-weak",
        "description": "Tavşan Pati mevcut zayıf özet",
        "summary_text": (
            "The book says the rabbit named Pati loses his way. "
            "For example, he meets a strange fox. "
            "According to the text, he learns something and the end is okay."
        ),
        "summary_ir": {"central_entities": ["Tavşan Pati"], "themes": ["arkadaşlık", "cesaret"]},
    },
    {
        "case_id": "buyulu-yastiklar-weak",
        "description": "Büyülü Yastıklar mevcut zayıf/tutarsız özet",
        "summary_text": (
            "This book is about magic pillows and a family. "
            "It has a strange lesson about dreams. "
            "In the end, something changes but it is not clear why."
        ),
        "summary_ir": {"central_entities": ["Yastık", "Gizem"], "themes": ["hayal gücü", "aile"]},
    },
    {
        "case_id": "good-narrative-summary",
        "description": "İyi narrative summary örneği",
        "summary_text": (
            "This story is about a girl named Elif who lives in a village surrounded by a forest. "
            "She faces a challenge when a storm destroys her home, and she must find a safe place for her family. "
            "At the end, the community works together to rebuild the house, showing the value of courage and friendship."
        ),
        "summary_ir": {"central_entities": ["Elif"], "themes": ["cesaret", "arkadaşlık"]},
    },
]


def _evaluate_summary_case(case: Dict[str, Any]) -> Dict[str, Any]:
    evaluation = evaluate_summary_quality(case["summary_text"], case.get("summary_ir"))
    return {
        "case_id": case["case_id"],
        "description": case["description"],
        "summary_text": case["summary_text"],
        "summary_ir": case.get("summary_ir", {}),
        "evaluation": evaluation,
    }


def build_summary_quality_check_artifact(
    output_path: Optional[Path] = None,
    cases: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    base = Path(__file__).resolve().parent
    artifact_path = Path(output_path) if output_path else base / "rc4_sprint5_summary_quality_results.json"
    case_definitions = cases if cases is not None else REGRESSION_SUMMARIES
    first_run = [_evaluate_summary_case(case) for case in case_definitions]
    second_run = [_evaluate_summary_case(case) for case in case_definitions]
    deterministic = first_run == second_run
    total_cases = len(first_run)
    passed_count = sum(1 for case in first_run if case["evaluation"]["passed"])
    failed_count = total_cases - passed_count
    average_summary_quality_score = (
        sum(case["evaluation"]["summary_quality_score"] for case in first_run) / total_cases
        if total_cases
        else 0.0
    )
    average_coherence = (
        sum(case["evaluation"]["coherence"] for case in first_run) / total_cases if total_cases else 0.0
    )
    average_concreteness = (
        sum(case["evaluation"]["concreteness_score"] for case in first_run) / total_cases
        if total_cases
        else 0.0
    )
    evidence_concatenation_detected_count = sum(
        1 for case in first_run if case["evaluation"]["evidence_concatenation_detected"]
    )
    artifact = {
        "total_cases": total_cases,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "per_case_results": first_run,
        "average_summary_quality_score": round(average_summary_quality_score, 3),
        "average_coherence": round(average_coherence, 3),
        "average_concreteness": round(average_concreteness, 3),
        "evidence_concatenation_detected_count": evidence_concatenation_detected_count,
        "deterministic": deterministic,
        "production_output_changed": False,
        "runtime_pipeline_bound": False,
    }
    artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return artifact


def main() -> None:
    artifact = build_summary_quality_check_artifact()
    print(json.dumps(artifact, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
