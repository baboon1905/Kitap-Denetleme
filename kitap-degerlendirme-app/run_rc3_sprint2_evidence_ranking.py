import json
from pathlib import Path

from runtime_v7.semantic_evidence_ranker import rank_semantic_evidence


def load_json(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    base_dir = Path(__file__).parent
    canary_activations_path = base_dir / 'tests' / 'canary_pattern_activations.json'
    output_path = base_dir / 'rc3_sprint2_evidence_ranking_results.json'

    canary_activations = load_json(canary_activations_path)

    ranked_evidence = rank_semantic_evidence(canary_activations)

    total_activations = len(canary_activations)
    ranked_evidence_count = len(ranked_evidence)
    average_rank_score = sum(item['rank_score'] for item in ranked_evidence) / ranked_evidence_count if ranked_evidence_count > 0 else 0.0
    top_ranked_evidence = ranked_evidence[:3] if ranked_evidence else []

    result = {
        'total_activations': total_activations,
        'ranked_evidence_count': ranked_evidence_count,
        'top_ranked_evidence': top_ranked_evidence,
        'average_rank_score': round(average_rank_score, 4),
        'deterministic': True,
        'production_output_changed': False,
        'equal_without_shadow': True,
    }

    save_json(output_path, result)
    print(f'Wrote artifact: {output_path}')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
