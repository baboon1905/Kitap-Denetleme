import copy
from typing import Any, Dict, List


def build_ground_truth_comparison(
    shadow_patterns: List[str],
    human_patterns: List[str],
) -> Dict[str, Any]:
    shadow_copy = copy.deepcopy(shadow_patterns) if isinstance(shadow_patterns, list) else []
    human_copy = copy.deepcopy(human_patterns) if isinstance(human_patterns, list) else []

    shadow_set = set(shadow_copy)
    human_set = set(human_copy)

    matched = sorted(list(shadow_set & human_set))
    shadow_only = sorted(list(shadow_set - human_set))
    human_only = sorted(list(human_set - shadow_set))

    matching_count = len(matched)
    shadow_count = len(shadow_set)
    human_count = len(human_set)

    precision = matching_count / shadow_count if shadow_count > 0 else 0.0
    recall = matching_count / human_count if human_count > 0 else 0.0
    f1_score = (
        2 * precision * recall / (precision + recall)
        if precision + recall > 0
        else 0.0
    )

    return {
        'matched_patterns': matched,
        'shadow_only_patterns': shadow_only,
        'human_only_patterns': human_only,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
    }
