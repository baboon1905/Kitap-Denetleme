import copy
from typing import Any, Dict, List, Optional


def _source_weight(source: Optional[str]) -> float:
    if not source or not isinstance(source, str):
        return 0.5
    low = source.lower()
    if 'semantic' in low:
        return 1.0
    if 'summary_ir' in low or 'summary' in low:
        return 0.8
    if 'narrative' in low or 'story' in low:
        return 0.7
    return 0.6


def _semantic_density(matched_keywords: Optional[List[Any]], match_snippet: Optional[str]) -> float:
    if not matched_keywords:
        return 0.0
    keyword_count = len(matched_keywords)
    if isinstance(match_snippet, str) and match_snippet.strip():
        word_count = len(match_snippet.split())
        return min(1.0, keyword_count / max(word_count, 1))
    return min(1.0, keyword_count * 0.25)


def _cluster_support(source: Optional[str]) -> int:
    if not source or not isinstance(source, str):
        return 0
    return 1 if 'cluster' in source.lower() else 0


def _compute_rank_score(evidence_count: int, source_weight: float, semantic_density: float, cluster_support: int) -> float:
    return round(
        evidence_count * 1.5
        + source_weight * 2.0
        + semantic_density * 1.2
        + cluster_support * 0.8,
        4,
    )


def rank_semantic_evidence(canonical_activations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    activations = copy.deepcopy(canonical_activations or [])
    ranked: List[Dict[str, Any]] = []

    for activation in activations:
        pattern_id = activation.get('pattern_id') or activation.get('id') or ''
        evidence_count = int(activation.get('evidence_count', 0) or 0)
        source = activation.get('source') if isinstance(activation.get('source'), str) else ''
        matched_keywords = activation.get('matched_keywords') if isinstance(activation.get('matched_keywords'), list) else []
        match_snippet = activation.get('match_snippet') if isinstance(activation.get('match_snippet'), str) else ''

        source_weight = _source_weight(source)
        semantic_density = _semantic_density(matched_keywords, match_snippet)
        cluster_support = _cluster_support(source)
        rank_score = _compute_rank_score(evidence_count, source_weight, semantic_density, cluster_support)

        ranking_signals = {
            'evidence_count': evidence_count,
            'source_weight': source_weight,
            'semantic_density': semantic_density,
            'cluster_support': cluster_support,
        }

        ranked.append({
            'pattern_id': pattern_id,
            'rank_score': rank_score,
            'ranking_signals': ranking_signals,
            'evidence_count': evidence_count,
            'source': source,
            'match_snippet': match_snippet,
        })

    ranked = sorted(
        ranked,
        key=lambda item: (
            -item['rank_score'],
            item['pattern_id'] or '',
            item['source'] or '',
        ),
    )

    for position, item in enumerate(ranked, start=1):
        item['rank'] = position

    return ranked
