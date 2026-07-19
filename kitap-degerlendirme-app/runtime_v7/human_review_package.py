import copy
from typing import Any, Dict, List, Optional


REQUIRED_PACKAGE_KEYS = {
    'pattern_id',
    'acceptance_decision',
    'decision_score',
    'confidence_summary',
    'evidence_summary',
    'explanation_summary',
    'delta_summary',
    'review_recommendation',
    'audit_reference',
}


def _effective_confidence(activation: Optional[Dict[str, Any]]) -> float:
    if not activation:
        return 0.0
    return float(activation.get('calibrated_confidence') or activation.get('raw_confidence') or 0.0)


def _build_confidence_summary(activation: Optional[Dict[str, Any]]) -> str:
    confidence = _effective_confidence(activation)
    if not activation:
        return 'confidence unavailable'
    status = activation.get('status', 'unknown')
    return f"status={status}; confidence={confidence}"


def _build_evidence_summary(activation: Optional[Dict[str, Any]], ranked_item: Optional[Dict[str, Any]]) -> str:
    if not activation and not ranked_item:
        return 'no evidence available'
    evidence_count = activation.get('evidence_count', 0) if activation else 0
    rank_score = ranked_item.get('rank_score', 0.0) if ranked_item else 0.0
    rank = ranked_item.get('rank', '?') if ranked_item else '?'
    return f"evidence_count={evidence_count}; rank={rank}; rank_score={rank_score}"


def _build_explanation_summary(explanation: Optional[Dict[str, Any]]) -> str:
    if not explanation:
        return 'no explanation available'
    reasoning = explanation.get('reasoning', 'no reasoning provided')
    supporting = explanation.get('supporting_signals', [])
    return f"reasoning={reasoning}; supporting_signals={','.join(supporting)}"


def _build_delta_summary(delta_info: Optional[Dict[str, Any]]) -> str:
    if not delta_info:
        return 'no delta available'
    coverage = delta_info.get('coverage_delta', 0.0)
    overlap = delta_info.get('overlap_score', 0.0)
    return f"coverage_delta={coverage}; overlap_score={overlap}"


def _build_review_recommendation(acceptance_decision: Optional[Dict[str, Any]], explanation: Optional[Dict[str, Any]]) -> str:
    decision = (acceptance_decision or {}).get('decision', 'review')
    if decision == 'accepted':
        return 'approve_candidate'
    if decision == 'review':
        return 'review_human'
    if not explanation:
        return 'review_human'
    return 'reject_candidate'


def _build_audit_reference(pattern_id: str, acceptance_decision: Optional[Dict[str, Any]]) -> str:
    decision = (acceptance_decision or {}).get('decision', 'review')
    return f"pattern:{pattern_id};decision:{decision}"


def build_human_review_package(
    pattern_activations: List[Dict[str, Any]],
    ranked_evidence: Optional[List[Dict[str, Any]]] = None,
    semantic_explanations: Optional[List[Dict[str, Any]]] = None,
    acceptance_decisions: Optional[List[Dict[str, Any]]] = None,
    delta_analysis: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    activations = copy.deepcopy(pattern_activations or [])
    ranked = copy.deepcopy(ranked_evidence or [])
    explanations = copy.deepcopy(semantic_explanations or [])
    decisions = copy.deepcopy(acceptance_decisions or [])
    delta = copy.deepcopy(delta_analysis or {})

    ranked_by_pattern = {item.get('pattern_id'): item for item in ranked if item.get('pattern_id')}
    explanation_by_pattern = {item.get('pattern_id'): item for item in explanations if item.get('pattern_id')}
    decision_by_pattern = {item.get('pattern_id'): item for item in decisions if item.get('pattern_id')}

    package: List[Dict[str, Any]] = []
    for activation in activations:
        pattern_id = activation.get('pattern_id') or activation.get('id') or ''
        if not pattern_id:
            continue

        acceptance_decision = decision_by_pattern.get(pattern_id)
        explanation = explanation_by_pattern.get(pattern_id)
        ranked_item = ranked_by_pattern.get(pattern_id)

        entry = {
            'pattern_id': pattern_id,
            'acceptance_decision': (acceptance_decision or {}).get('decision', 'review'),
            'decision_score': (acceptance_decision or {}).get('decision_score', 0.0),
            'confidence_summary': _build_confidence_summary(activation),
            'evidence_summary': _build_evidence_summary(activation, ranked_item),
            'explanation_summary': _build_explanation_summary(explanation),
            'delta_summary': _build_delta_summary(delta),
            'review_recommendation': _build_review_recommendation(acceptance_decision, explanation),
            'audit_reference': _build_audit_reference(pattern_id, acceptance_decision),
        }
        if not REQUIRED_PACKAGE_KEYS.issubset(entry.keys()):
            raise ValueError('human review package entry missing required fields')
        package.append(entry)

    return sorted(package, key=lambda item: item['pattern_id'])
