import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime_v7.ground_truth_dataset_builder import build_ground_truth_dataset


CANARY_HUMAN_REVIEW_RECORDS: List[Dict[str, Any]] = [
    {
        'book_id': 'book-1',
        'human_patterns': ['pattern-alpha', 'pattern-beta'],
        'human_themes': ['theme-one'],
        'human_character_roles': ['protagonist', 'mentor'],
        'human_learning_outcomes': ['outcome-a'],
        'reviewer_id': 'reviewer-1',
    },
    {
        'book_id': 'book-2',
        'human_patterns': ['pattern-gamma'],
        'human_themes': ['theme-two'],
        'human_character_roles': ['antagonist'],
        'human_learning_outcomes': ['outcome-b', 'outcome-c'],
        'reviewer_id': 'reviewer-2',
    },
    {
        'book_id': 'book-3',
        'human_patterns': ['pattern-delta'],
        'human_themes': ['theme-three'],
        'human_character_roles': ['sidekick'],
        'human_learning_outcomes': ['outcome-d'],
        'reviewer_id': 'reviewer-3',
    },
]


def build_ground_truth_dataset_artifact(
    output_path: Optional[Path] = None,
    records: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    base = Path(__file__).resolve().parent
    artifact_path = Path(output_path) if output_path else base / 'rc4_sprint4_ground_truth_dataset.json'
    payload = records if records is not None else CANARY_HUMAN_REVIEW_RECORDS
    artifact = build_ground_truth_dataset(payload, dataset_version='1.0')
    artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return artifact


def main() -> None:
    artifact = build_ground_truth_dataset_artifact()
    print(json.dumps(artifact, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
