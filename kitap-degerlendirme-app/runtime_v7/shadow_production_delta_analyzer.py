import copy
import hashlib
import json
from typing import Any, Dict, List, Set, Tuple


def _json_stable_serialize(value: Any) -> str:
    def normalize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: normalize(obj[k]) for k in sorted(obj)}
        if isinstance(obj, list):
            normalized = [normalize(item) for item in obj]
            try:
                return sorted(normalized, key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True))
            except TypeError:
                return normalized
        return obj

    canonical = normalize(value)
    return json.dumps(canonical, ensure_ascii=False, sort_keys=True)


def _build_deterministic_fingerprint(production_payload: Dict[str, Any], shadow_payload: Dict[str, Any]) -> str:
    serialized = _json_stable_serialize({
        'production_payload': production_payload,
        'shadow_payload': shadow_payload,
    })
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()


def _collect_signals(payload: Dict[str, Any]) -> Tuple[Set[str], int]:
    signals: Set[str] = set()
    activation_count = 0

    def record(value: Any, prefix: str = '') -> None:
        nonlocal activation_count
        if isinstance(value, dict):
            for key in sorted(value):
                record(value[key], prefix=f'{prefix}{key}.')
            return

        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    if 'pattern_id' in item:
                        activation_count += 1
                        signals.add(f"pattern_id:{item['pattern_id']}")
                    for inner_key in sorted(item):
                        record(item[inner_key], prefix=f'{prefix}{inner_key}.')
                elif isinstance(item, str):
                    signals.add(f'{prefix}{item}')
                elif isinstance(item, (int, float, bool)):
                    signals.add(f'{prefix}{str(item)}')
                else:
                    record(item, prefix=prefix)
            return

        if isinstance(value, str):
            signals.add(f'{prefix}{value}')
            return

        if isinstance(value, (int, float, bool)):
            signals.add(f'{prefix}{value}')
            return

    # Known signal keys that represent activations or semantic annotations.
    if isinstance(payload, dict):
        for key in sorted(payload):
            value = payload[key]
            if key == 'pattern_activations' or key == 'pattern_matches':
                if isinstance(value, list):
                    activation_count += len(value)
                    for item in value:
                        if isinstance(item, dict) and 'pattern_id' in item:
                            signals.add(f"pattern_id:{item['pattern_id']}")
                        record(item, prefix=f'{key}.')
                else:
                    record(value, prefix=f'{key}.')
                continue
            if key in {'semantic_labels', 'topics', 'tags', 'keywords', 'teacher_annotations', 'editor_labels'}:
                record(value, prefix=f'{key}.')
                continue
            record(value, prefix=f'{key}.')

    return signals, activation_count


def analyze_shadow_production_delta(production_payload: Dict[str, Any], shadow_payload: Dict[str, Any]) -> Dict[str, Any]:
    production_copy = copy.deepcopy(production_payload)
    shadow_copy = copy.deepcopy(shadow_payload)

    production_signals, production_activation_count = _collect_signals(production_copy)
    shadow_signals, shadow_activation_count = _collect_signals(shadow_copy)

    intersection = production_signals.intersection(shadow_signals)
    union = production_signals.union(shadow_signals)

    production_size = len(production_signals)
    shadow_size = len(shadow_signals)

    overlap_score = len(intersection) / len(union) if union else 1.0
    coverage_delta = (shadow_size - production_size) / production_size if production_size else float(shadow_size)
    activation_count_delta = shadow_activation_count - production_activation_count

    confidence_summary = {
        'production_confidence_fields_present': any(
            key in production_copy and production_copy.get(key) is not None
            for key in ['raw_confidence', 'calibrated_confidence', 'confidence_level']
        ),
        'shadow_confidence_fields_present': any(
            key in shadow_copy and shadow_copy.get(key) is not None
            for key in ['raw_confidence', 'calibrated_confidence', 'confidence_level']
        ),
        'note': 'This analyzer does not compute confidence values; it only reports presence/absence of confidence fields.'
    }

    shadow_only_signals = sorted(shadow_signals.difference(production_signals))
    production_only_signals = sorted(production_signals.difference(shadow_signals))

    deterministic_fingerprint = _build_deterministic_fingerprint(production_copy, shadow_copy)

    return {
        'coverage_delta': coverage_delta,
        'activation_count_delta': activation_count_delta,
        'confidence_summary': confidence_summary,
        'overlap_score': overlap_score,
        'shadow_only_signals': shadow_only_signals,
        'production_only_signals': production_only_signals,
        'deterministic_fingerprint': deterministic_fingerprint,
    }
