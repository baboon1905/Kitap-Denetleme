from runtime_v7.semantic_acceptance_gate import build_semantic_acceptance_decisions

pattern_activations = [
    {'pattern_id': 'theme_resilience', 'status': 'active', 'raw_confidence': 0.75, 'calibrated_confidence': 0.8},
    {'pattern_id': 'theme_adventure', 'status': 'active', 'raw_confidence': 0.6, 'calibrated_confidence': 0.65},
    {'pattern_id': 'theme_courage', 'status': 'candidate', 'raw_confidence': 0.4, 'calibrated_confidence': 0.45},
]
ranked_evidence = [
    {'pattern_id': 'theme_resilience', 'rank_score': 6.0},
    {'pattern_id': 'theme_adventure', 'rank_score': 4.0},
    {'pattern_id': 'theme_courage', 'rank_score': 2.0},
]
semantic_explanations = [
    {'pattern_id': 'theme_resilience', 'reasoning': 'clear support', 'supporting_signals': ['evidence_count=3']},
    {'pattern_id': 'theme_adventure', 'reasoning': 'supporting explanation', 'supporting_signals': ['evidence_count=2']},
]
delta_analysis = {'coverage_delta': 0.2}

for item in build_semantic_acceptance_decisions(pattern_activations, ranked_evidence, semantic_explanations, delta_analysis)[:3]:
    print(item)
