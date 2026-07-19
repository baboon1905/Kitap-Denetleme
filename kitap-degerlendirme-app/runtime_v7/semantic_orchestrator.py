import copy
from typing import Any, Dict, List, Optional

from runtime_v7.human_review_package import build_human_review_package
from runtime_v7.semantic_acceptance_gate import build_semantic_acceptance_decisions
from runtime_v7.semantic_evidence_ranker import rank_semantic_evidence
from runtime_v7.semantic_explainability_layer import build_semantic_explanations
from runtime_v7.semantic_pattern_match_confidence import build_pattern_match_confidence
from runtime_v7.semantic_pattern_match_producer import build_pattern_matches_from_payload
from runtime_v7.semantic_pattern_monitor import (
    aggregate_category_metrics,
    aggregate_library_metrics,
    compute_per_pattern_metrics,
    generate_canonical_activations,
)
from runtime_v7.semantic_pattern_registry import get_sprint3_pattern_definitions
from runtime_v7.shadow_production_delta_analyzer import analyze_shadow_production_delta


def _empty_result() -> Dict[str, Any]:
    return {
        'pattern_matches': [],
        'confidence': [],
        'pattern_activations': [],
        'ranked_evidence': [],
        'explanations': [],
        'acceptance_decisions': [],
        'human_review_package': [],
        'delta_analysis': {},
        'monitoring': {
            'pattern_metrics': [],
            'category_metrics': [],
            'library_metrics': {},
        },
        'safety': {
            'shadow_only': True,
            'production_output_changed': False,
            'equal_without_shadow': True,
            'orchestrator_enabled': True,
        },
        'stage_order': [
            'pattern_match_producer',
            'confidence_engine',
            'semantic_monitor',
            'evidence_ranking',
            'explainability',
            'acceptance_gate',
            'human_review_package',
            'shadow_production_delta',
        ],
    }


def run_semantic_orchestrator(
    payload: Optional[Dict[str, Any]] = None,
    production_payload: Optional[Dict[str, Any]] = None,
    feature_flags: Optional[Dict[str, Any]] = None,
    pattern_library: Optional[List[Dict[str, Any]]] = None,
    books_analyzed: int = 1,
) -> Dict[str, Any]:
    payload_copy = copy.deepcopy(payload or {})
    production_copy = copy.deepcopy(production_payload or {})
    feature_flags_copy = copy.deepcopy(feature_flags or {})

    if not isinstance(payload_copy, dict):
        payload_copy = {}
    if not isinstance(production_copy, dict):
        production_copy = {}
    if not isinstance(feature_flags_copy, dict):
        feature_flags_copy = {}

    if feature_flags_copy.get('semantic_orchestrator_enabled') is False:
        result = _empty_result()
        result['safety']['orchestrator_enabled'] = False
        return result

    pattern_matches = build_pattern_matches_from_payload(payload_copy)
    confidence = build_pattern_match_confidence(pattern_matches, books_analyzed=books_analyzed)

    patterns = pattern_library or get_sprint3_pattern_definitions()
    activation_payload = generate_canonical_activations(
        patterns,
        confidence,
        pattern_library_version='rc3-sprint6',
        confidence_engine_version='conf-v1',
    )
    pattern_activations = activation_payload.get('pattern_activations', [])

    pattern_metrics = compute_per_pattern_metrics(patterns, confidence, total_docs=max(1, books_analyzed))
    category_metrics = aggregate_category_metrics(pattern_metrics)
    library_metrics = aggregate_library_metrics(pattern_metrics)

    ranked_evidence = rank_semantic_evidence(pattern_activations)
    delta_analysis = analyze_shadow_production_delta(
        production_payload=production_copy,
        shadow_payload=payload_copy,
    )
    explanations = build_semantic_explanations(pattern_activations, ranked_evidence, delta_analysis=delta_analysis)
    acceptance_decisions = build_semantic_acceptance_decisions(
        pattern_activations,
        ranked_evidence,
        explanations,
        delta_analysis,
    )
    human_review_package = build_human_review_package(
        pattern_activations,
        ranked_evidence,
        explanations,
        acceptance_decisions,
        delta_analysis,
    )

    return {
        'pattern_matches': pattern_matches,
        'confidence': confidence,
        'pattern_activations': pattern_activations,
        'ranked_evidence': ranked_evidence,
        'explanations': explanations,
        'acceptance_decisions': acceptance_decisions,
        'human_review_package': human_review_package,
        'delta_analysis': delta_analysis,
        'monitoring': {
            'pattern_metrics': pattern_metrics,
            'category_metrics': category_metrics,
            'library_metrics': library_metrics,
        },
        'safety': {
            'shadow_only': True,
            'production_output_changed': False,
            'equal_without_shadow': True,
            'orchestrator_enabled': True,
        },
        'stage_order': [
            'pattern_match_producer',
            'confidence_engine',
            'semantic_monitor',
            'evidence_ranking',
            'explainability',
            'acceptance_gate',
            'human_review_package',
            'shadow_production_delta',
        ],
    }
