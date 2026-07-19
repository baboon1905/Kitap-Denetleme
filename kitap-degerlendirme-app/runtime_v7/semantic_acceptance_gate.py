import copy
from typing import Any, Dict, List, Optional


def _effective_confidence(activation: Dict[str, Any]) -> float:
    return float(activation.get('calibrated_confidence') or activation.get('raw_confidence') or 0.0)


def _rank_strength(ranked_item: Optional[Dict[str, Any]]) -> float:
    if not ranked_item:
        return 0.0
    return float(ranked_item.get('rank_score', 0.0) or 0.0)


def _has_supporting_explanation(explanation: Optional[Dict[str, Any]]) -> bool:
    if not explanation:
        return False
    return bool(explanation.get('reasoning')) and bool(explanation.get('supporting_signals'))


def evaluate_acceptance_gate(
    pattern_id: str,
    activation: Optional[Dict[str, Any]] = None,
    ranked_item: Optional[Dict[str, Any]] = None,
    explanation: Optional[Dict[str, Any]] = None,
    delta_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    activation = copy.deepcopy(activation or {})
    ranked_item = copy.deepcopy(ranked_item or {})
    explanation = copy.deepcopy(explanation or {})
    delta_info = copy.deepcopy(delta_info or {})

    confidence = _effective_confidence(activation)
    rank_score = _rank_strength(ranked_item)
    has_explanation = _has_supporting_explanation(explanation)
    has_active_status = str(activation.get('status', '')).lower() == 'active'
    delta_support = float(delta_info.get('coverage_delta', 0.0) or 0.0)

    decision = 'review'
    decision_score = 0.0
    blocking_factors: List[str] = []
    supporting_factors: List[str] = []

    if confidence >= 0.7 and rank_score >= 5.0 and has_explanation and has_active_status:
        decision = 'accepted'
        decision_score = 1.0
        supporting_factors = [
            'high_confidence',
            'strong_rank',
            'supporting_explanation',
            'active_status',
        ]
    elif confidence >= 0.5 and rank_score >= 3.0 and has_explanation:
        decision = 'review'
        decision_score = 0.5
        supporting_factors = ['moderate_confidence', 'supporting_explanation']
        blocking_factors = ['insufficient_rank_or_status']
    else:
        decision = 'rejected'
        decision_score = 0.0
        blocking_factors = ['low_confidence', 'limited_support']
        supporting_factors = []

    if delta_support <= 0.0:
        blocking_factors.append('negative_delta_support')
        if decision == 'accepted':
            decision = 'review'
            decision_score = 0.6

    if not has_explanation:
        blocking_factors.append('missing_explanation')

    if not activation:
        decision = 'rejected'
        decision_score = 0.0
        blocking_factors = ['missing_activation']
        supporting_factors = []

    decision_reasons = []
    if decision == 'accepted':
        decision_reasons = ['sufficient_confidence', 'strong_evidence_support', 'clear_explanation']
    elif decision == 'review':
        decision_reasons = ['partial_support', 'requires_manual_review']
    else:
        decision_reasons = ['insufficient_support', 'gate_failed']

    decision_trace = [
        f"confidence={confidence}",
        f"rank_score={rank_score}",
        f"has_explanation={has_explanation}",
        f"status={activation.get('status', 'unknown')}",
        f"delta_support={delta_support}",
    ]

    return {
        'pattern_id': pattern_id,
        'decision': decision,
        'decision_score': round(decision_score, 2),
        'decision_reasons': decision_reasons,
        'blocking_factors': sorted(set(blocking_factors)),
        'supporting_factors': sorted(set(supporting_factors)),
        'decision_trace': decision_trace,
    }


def build_semantic_acceptance_decisions(
    pattern_activations: List[Dict[str, Any]],
    ranked_evidence: Optional[List[Dict[str, Any]]] = None,
    semantic_explanations: Optional[List[Dict[str, Any]]] = None,
    delta_analysis: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    activations = copy.deepcopy(pattern_activations or [])
    ranked = copy.deepcopy(ranked_evidence or [])
    explanations = copy.deepcopy(semantic_explanations or [])
    delta = copy.deepcopy(delta_analysis or {})

    ranked_by_pattern = {item.get('pattern_id'): item for item in ranked if item.get('pattern_id')}
    explanation_by_pattern = {item.get('pattern_id'): item for item in explanations if item.get('pattern_id')}

    decisions = []
    for activation in activations:
        pattern_id = activation.get('pattern_id') or activation.get('id') or ''
        if not pattern_id:
            continue
        decision = evaluate_acceptance_gate(
            pattern_id,
            activation=activation,
            ranked_item=ranked_by_pattern.get(pattern_id),
            explanation=explanation_by_pattern.get(pattern_id),
            delta_info=delta,
        )
        decisions.append(decision)

    return sorted(decisions, key=lambda item: (item['pattern_id'], item['decision']))
