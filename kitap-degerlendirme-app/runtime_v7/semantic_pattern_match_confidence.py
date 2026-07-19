from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

from runtime_v7.semantic_confidence_engine import SemanticConfidenceEngine
from runtime_v7.semantic_pattern_registry import get_sprint3_pattern_definitions
from runtime_v7.semantic_pattern_match_producer import build_pattern_matches_from_payload


def _build_pattern_registry_map() -> Dict[str, Dict[str, Any]]:
    return {pattern.get('id'): pattern for pattern in get_sprint3_pattern_definitions()}


def _normalize_numeric(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _build_match_metrics(match: Dict[str, Any], pattern_def: Dict[str, Any], pattern_matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    matched_keywords = [str(k).strip() for k in match.get('matched_keywords') or [] if str(k).strip()]
    raw_match_count = max(1, len(matched_keywords))
    pattern_keywords = [str(k).strip() for k in pattern_def.get('keywords') or [] if str(k).strip()]
    keyword_coverage = min(1.0, raw_match_count / max(1, len(pattern_keywords)))

    sources = [str(item.get('source') or '').strip() for item in pattern_matches if item.get('pattern_id') == match.get('pattern_id')]
    unique_sources = len({s for s in sources if s})
    total_matches = max(1, len([item for item in pattern_matches if item.get('pattern_id') == match.get('pattern_id')]))
    evidence_diversity = min(1.0, unique_sources / total_matches)

    return {
        'raw_match_count': raw_match_count,
        'pattern_category': str(match.get('pattern_category') or pattern_def.get('category') or 'theme').strip(),
        'false_positive_risk': str(match.get('fp_risk') or pattern_def.get('default_fp_risk') or 'medium').strip(),
        'semantic_density': min(1.0, 0.2 + 0.8 * keyword_coverage),
        'evidence_diversity': evidence_diversity,
        'coverage_ratio': keyword_coverage,
    }


def build_pattern_match_confidence(
    matches: List[Dict[str, Any]],
    books_analyzed: int = 1,
) -> List[Dict[str, Any]]:
    """Attach deterministic confidence scores to pattern matches.

    This function does not perform pattern matching; it consumes an existing
    pattern match list and delegates all confidence calculations to
    SemanticConfidenceEngine.
    """
    if not isinstance(matches, list) or not matches:
        return []

    engine = SemanticConfidenceEngine()
    registry = _build_pattern_registry_map()
    results: List[Dict[str, Any]] = []

    for match in sorted(matches, key=lambda x: (str(x.get('pattern_id') or ''), str(x.get('source') or ''), str(x.get('match_snippet') or ''))):
        if not isinstance(match, dict):
            continue
        pattern_id = str(match.get('pattern_id') or '').strip()
        if not pattern_id:
            continue

        pattern_def = registry.get(pattern_id, {})
        metrics = _build_match_metrics(match, pattern_def, matches)
        confidence = engine.calculate_confidence(
            raw_match_count=int(metrics['raw_match_count']),
            pattern_category=metrics['pattern_category'],
            false_positive_risk=metrics['false_positive_risk'],
            semantic_density=metrics['semantic_density'],
            evidence_diversity=metrics['evidence_diversity'],
            coverage_ratio=metrics['coverage_ratio'],
            books_analyzed=books_analyzed,
        )

        enriched_match = dict(match)
        enriched_match['raw_confidence'] = confidence['raw_confidence']
        enriched_match['calibrated_confidence'] = confidence['calibrated_confidence']
        enriched_match['confidence_level'] = confidence['confidence_level']
        enriched_match['recommendation'] = confidence['recommendation']
        enriched_match['confidence_explanation'] = confidence['explanation']
        results.append(enriched_match)

    return results


def build_pattern_matches_with_confidence_from_payload(payload: Dict[str, Any], books_analyzed: int = 1) -> List[Dict[str, Any]]:
    """Produce pattern matches from payload and attach confidence scores."""
    matches = build_pattern_matches_from_payload(payload)
    return build_pattern_match_confidence(matches, books_analyzed=books_analyzed)
