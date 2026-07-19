import copy
from typing import Any, Dict, List, Optional


def _build_ranking_context(rank: int, rank_score: float, ranking_signals: Optional[Dict[str, Any]]) -> str:
    if not ranking_signals:
        return f"No ranking context available"
    signals = ranking_signals
    ev_count = signals.get('evidence_count', 0)
    src_weight = signals.get('source_weight', 0.0)
    sem_density = signals.get('semantic_density', 0.0)
    cluster_support = signals.get('cluster_support', 0)
    return f"Rank #{rank} with score {rank_score} due to evidence_count={ev_count}, source_weight={src_weight}, semantic_density={sem_density}, cluster_support={cluster_support}"


def _build_delta_context(delta_info: Optional[Dict[str, Any]]) -> str:
    if not delta_info:
        return "No delta context available"
    coverage = delta_info.get('coverage_delta', 0.0)
    overlap = delta_info.get('overlap_score', 0.0)
    return f"Delta: coverage_delta={coverage}, overlap_score={overlap}"


def _build_supporting_signals(activation: Dict[str, Any]) -> List[str]:
    signals = []
    if activation.get('evidence_count'):
        signals.append(f"evidence_count={activation['evidence_count']}")
    if activation.get('source'):
        signals.append(f"source={activation['source']}")
    if activation.get('status'):
        signals.append(f"status={activation['status']}")
    if activation.get('raw_confidence') is not None:
        signals.append(f"raw_confidence={activation['raw_confidence']}")
    if activation.get('calibrated_confidence') is not None:
        signals.append(f"calibrated_confidence={activation['calibrated_confidence']}")
    return sorted(signals)


def generate_explanation(
    pattern_id: str,
    activation: Dict[str, Any],
    ranked_item: Optional[Dict[str, Any]] = None,
    delta_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    status = activation.get('status', 'candidate')
    evidence_count = activation.get('evidence_count', 0)
    source = activation.get('source', 'unknown')
    
    decision = f"Pattern '{pattern_id}' activated with status '{status}'"
    if status == 'active':
        reasoning = f"Pattern selected due to evidence from {source} source with {evidence_count} supporting evidence items and sufficient confidence threshold"
    else:
        reasoning = f"Pattern marked as candidate based on {evidence_count} evidence item(s) from {source} source, below active threshold"
    
    supporting_signals = _build_supporting_signals(activation)
    
    effective_conf = activation.get('calibrated_confidence') or activation.get('raw_confidence') or 0.0
    conf_level = 'high' if effective_conf >= 0.7 else 'medium' if effective_conf >= 0.5 else 'low'
    
    rank_context = ''
    if ranked_item:
        rank = ranked_item.get('rank', '?')
        rank_score = ranked_item.get('rank_score', 0.0)
        ranking_signals = ranked_item.get('ranking_signals', {})
        rank_context = _build_ranking_context(rank, rank_score, ranking_signals)
    
    delta_context = _build_delta_context(delta_info) if delta_info else ''
    
    audit_trail = [
        f"Pattern detection: source={source}",
        f"Evidence aggregation: count={evidence_count}",
        f"Status assignment: {status}",
    ]
    if ranked_item:
        audit_trail.append(f"Ranking: rank={ranked_item.get('rank', '?')}, score={ranked_item.get('rank_score', 0.0)}")
    
    return {
        'pattern_id': pattern_id,
        'decision': decision,
        'reasoning': reasoning,
        'supporting_signals': supporting_signals,
        'confidence_level': conf_level,
        'rank_context': rank_context,
        'delta_context': delta_context,
        'audit_trail': audit_trail,
    }


def build_semantic_explanations(
    pattern_activations: List[Dict[str, Any]],
    ranked_evidence: Optional[List[Dict[str, Any]]] = None,
    delta_analysis: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    activations = copy.deepcopy(pattern_activations or [])
    ranked = copy.deepcopy(ranked_evidence or [])
    delta = copy.deepcopy(delta_analysis or {})

    ranked_by_pattern = {}
    for item in ranked:
        pid = item.get('pattern_id')
        if pid:
            ranked_by_pattern[pid] = item

    explanations = []
    for activation in activations:
        pattern_id = activation.get('pattern_id') or activation.get('id') or ''
        if not pattern_id:
            continue
        
        ranked_item = ranked_by_pattern.get(pattern_id)
        explanation = generate_explanation(pattern_id, activation, ranked_item, delta)
        explanations.append(explanation)

    explanations = sorted(explanations, key=lambda e: (e['pattern_id'], e['confidence_level']))

    return explanations
