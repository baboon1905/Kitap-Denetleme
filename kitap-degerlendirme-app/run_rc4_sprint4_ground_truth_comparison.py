import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime_v7.ground_truth_comparator import build_ground_truth_comparison


CANARY_SHADOW_PATTERN_OUTPUTS: List[Dict[str, Any]] = [
    {
        'book_id': 'book-1',
        'shadow_patterns': ['pattern-alpha', 'pattern-beta', 'pattern-zeta'],
    },
    {
        'book_id': 'book-2',
        'shadow_patterns': ['pattern-gamma', 'pattern-theta'],
    },
    {
        'book_id': 'book-3',
        'shadow_patterns': ['pattern-delta', 'pattern-epsilon'],
    },
]


def _load_json(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def _build_book_lookup(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {str(record.get('book_id')): record for record in records if isinstance(record, dict)}


def build_ground_truth_comparison_artifact(
    output_path: Optional[Path] = None,
    ground_truth_path: Optional[Path] = None,
    shadow_outputs: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    base = Path(__file__).resolve().parent
    artifact_path = Path(output_path) if output_path else base / 'rc4_sprint4_ground_truth_comparison_results.json'
    gt_path = Path(ground_truth_path) if ground_truth_path else base / 'rc4_sprint4_ground_truth_dataset.json'
    shadow_data = shadow_outputs if shadow_outputs is not None else CANARY_SHADOW_PATTERN_OUTPUTS

    ground_truth = _load_json(gt_path)
    books = ground_truth.get('books', []) if isinstance(ground_truth, dict) else []
    shadow_lookup = _build_book_lookup(shadow_data)

    comparisons = []
    precision_total = 0.0
    recall_total = 0.0
    f1_total = 0.0

    for book in books:
        book_id = str(book.get('book_id'))
        shadow_record = shadow_lookup.get(book_id, {})
        shadow_patterns = shadow_record.get('shadow_patterns', [])
        human_patterns = book.get('human_patterns', [])

        comparison = build_ground_truth_comparison(shadow_patterns, human_patterns)
        comparison_record = {
            'book_id': book_id,
            'matched_patterns': comparison['matched_patterns'],
            'shadow_only_patterns': comparison['shadow_only_patterns'],
            'human_only_patterns': comparison['human_only_patterns'],
            'precision': comparison['precision'],
            'recall': comparison['recall'],
            'f1_score': comparison['f1_score'],
        }

        precision_total += comparison['precision']
        recall_total += comparison['recall']
        f1_total += comparison['f1_score']
        comparisons.append(comparison_record)

    total_books = len(comparisons)
    average_precision = precision_total / total_books if total_books > 0 else 0.0
    average_recall = recall_total / total_books if total_books > 0 else 0.0
    average_f1_score = f1_total / total_books if total_books > 0 else 0.0

    artifact = {
        'total_books': total_books,
        'per_book_comparisons': comparisons,
        'average_precision': average_precision,
        'average_recall': average_recall,
        'average_f1_score': average_f1_score,
        'deterministic': True,
        'production_output_changed': False,
        'shadow_pipeline_called': False,
        'semantic_orchestrator_called': False,
    }

    artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return artifact


def main() -> None:
    artifact = build_ground_truth_comparison_artifact()
    print(json.dumps(artifact, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
