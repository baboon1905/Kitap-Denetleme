import json
from runtime_v7.semantic_explainability_layer import build_semantic_explanations

activations = [
    {
        'pattern_id': 'theme_resilience',
        'status': 'active',
        'evidence_count': 3,
        'source': 'semantic.theme_clusters',
        'raw_confidence': 0.72,
        'calibrated_confidence': 0.75,
    },
    {
        'pattern_id': 'theme_adventure',
        'status': 'active',
        'evidence_count': 2,
        'source': 'summary_ir.themes',
        'raw_confidence': 0.55,
        'calibrated_confidence': 0.59,
    },
    {
        'pattern_id': 'character_protagonist',
        'status': 'candidate',
        'evidence_count': 1,
        'source': 'narrative.summary',
        'raw_confidence': 0.45,
        'calibrated_confidence': 0.51,
    },
]

ranked = [
    {
        'pattern_id': 'theme_resilience',
        'rank': 1,
        'rank_score': 7.3,
        'ranking_signals': {'evidence_count': 3, 'source_weight': 1.0, 'semantic_density': 0.0, 'cluster_support': 1},
    },
    {
        'pattern_id': 'theme_adventure',
        'rank': 2,
        'rank_score': 4.6,
        'ranking_signals': {'evidence_count': 2, 'source_weight': 0.8, 'semantic_density': 0.0, 'cluster_support': 0},
    },
    {
        'pattern_id': 'character_protagonist',
        'rank': 3,
        'rank_score': 2.1,
        'ranking_signals': {'evidence_count': 1, 'source_weight': 0.7, 'semantic_density': 0.0, 'cluster_support': 0},
    },
]

delta = {
    'coverage_delta': 0.5767,
    'overlap_score': 0.5167,
}

explanations = build_semantic_explanations(activations, ranked, delta)

print("First 2 explanations:")
for i, expl in enumerate(explanations[:2], 1):
    print(f"\n--- Explanation {i} ---")
    print(json.dumps(expl, ensure_ascii=False, indent=2))
