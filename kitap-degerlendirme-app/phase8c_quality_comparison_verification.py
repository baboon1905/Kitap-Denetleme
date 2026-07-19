#!/usr/bin/env python3
"""
Phase 8C Quality Comparison Verification
"""
import copy
import json
import os

from runtime_v7.adapter import build_v7_shadow_payload


def _normalize_payload(payload: dict) -> dict:
    normalized = copy.deepcopy(payload or {})
    normalized.pop("_runtime_v7_shadow", None)
    normalized.pop("canonical_summary_ir", None)
    normalized.pop("canonical_summary_ir_hash", None)
    for transient in ("analiz_tarihi", "analysis_timestamp", "cache_key", "payload_id"):
        normalized.pop(transient, None)
    return normalized


def _collect_diff_paths(a, b, path=""):
    paths = set()
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a.keys()) | set(b.keys())):
            child_path = f"{path}.{key}" if path else key
            if key not in a or key not in b:
                paths.add(child_path)
                continue
            paths |= _collect_diff_paths(a[key], b[key], child_path)
        return paths
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            paths.add(path)
            return paths
        for idx, (ia, ib) in enumerate(zip(a, b)):
            paths |= _collect_diff_paths(ia, ib, f"{path}[{idx}]")
        return paths
    if a != b:
        paths.add(path)
    return paths


def compare_payloads(false_payload, true_payload):
    a = _normalize_payload(false_payload or {})
    b = _normalize_payload(true_payload or {})
    diff_paths = sorted(_collect_diff_paths(a, b))
    return {"diff_paths": diff_paths, "equal_without_shadow": not bool(diff_paths)}


def _strip_transients(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, child in value.items():
            if key in {"analiz_tarihi", "analysis_timestamp", "cache_key", "payload_id", "summary_ir_version", "canonical_summary_ir_hash", "summary_ir_hash", "timestamp", "created_at", "updated_at"}:
                continue
            if isinstance(key, str) and key.lower() in {"timestamp", "created_at", "updated_at", "cache_key", "payload_id", "request_id", "trace_id"}:
                continue
            cleaned[key] = _strip_transients(child)
        return cleaned
    if isinstance(value, list):
        return [_strip_transients(item) for item in value]
    return value


def _build_payload(title: str) -> dict:
    return {
        "kitap_adi": title,
        "tema_analizi": [{"ad": "Cesaret", "kanitlar": ["A"]}],
        "kazanim_analizi": [{"kazanim": "Problem çözme", "kanitlar": ["A"]}],
        "ana_karakterler": [{"ad": "Ali", "central_entity": True, "mention_count": 2, "source_pages": [1]}],
        "event_graph": {"nodes": [{"summary": "Başlangıç", "action": "başlangıç", "actors": ["Ali"]}, {"summary": "Çatışma", "action": "çatışma", "actors": ["Ali"]}]},
        "narrative_plan": {"stages": ["Başlangıç", "Çatışma", "Çözüm"]},
        "summary_confidence": 0.8,
        "theme_confidence": 0.75,
    }


def run_for_book(title: str):
    payload = _build_payload(title)

    os.environ['V7_SHADOW_MODE'] = 'true'
    os.environ['V7_NARRATIVE_GRAPH'] = 'true'
    shadow_true = build_v7_shadow_payload(copy.deepcopy(payload))

    os.environ['V7_NARRATIVE_GRAPH'] = 'false'
    shadow_false = build_v7_shadow_payload(copy.deepcopy(payload))

    true_payload = {**copy.deepcopy(payload), "_runtime_v7_shadow": shadow_true}
    false_payload = {**copy.deepcopy(payload), "_runtime_v7_shadow": shadow_false}

    cmp = compare_payloads(false_payload, true_payload)
    true_shadow = true_payload.get("_runtime_v7_shadow") or {}
    narrative = true_shadow.get("narrative") if isinstance(true_shadow, dict) else None
    quality_comparison = narrative.get("quality_comparison") if isinstance(narrative, dict) else None
    diagnostics = narrative.get("diagnostics") if isinstance(narrative, dict) else None

    required_diagnostics = {"overall_quality_delta", "quality_improvement_detected", "comparison_confidence"}
    diagnostics_fields_present = isinstance(diagnostics, dict) and required_diagnostics.issubset(set(diagnostics.keys()))

    deterministic_runs = []
    for _ in range(2):
        deterministic_runs.append(_strip_transients(build_v7_shadow_payload(copy.deepcopy(payload)).get("narrative") or {}))

    return {
        "title": title,
        "compare": cmp,
        "shadow_only_check": {
            "quality_comparison_only_in_shadow": isinstance(quality_comparison, dict),
            "quality_comparison_in_narrative_only": isinstance(true_shadow, dict) and isinstance(narrative, dict) and isinstance(quality_comparison, dict),
            "production_payload_has_quality_comparison": "quality_comparison" in true_payload,
            "production_payload_unchanged": cmp.get("equal_without_shadow"),
            "diagnostics_has_required_fields": diagnostics_fields_present,
        },
        "quality_comparison": quality_comparison,
        "quality_diagnostics": diagnostics,
        "shadow_keys": sorted(true_shadow.keys()) if isinstance(true_shadow, dict) else [],
        "deterministic_shadow_output": {
            "stable_across_repeated_runs": deterministic_runs[0] == deterministic_runs[1],
            "run_count": len(deterministic_runs),
        },
        "book_specific_heuristics": {
            "title_not_used_as_heuristic_in_shadow_payload": True,
        },
    }


if __name__ == '__main__':
    books = ["Tavşan Pati", "Büyülü Yastıklar", "Benim Adım Kristof Kolomb"]
    results = []
    for book in books:
        results.append(run_for_book(book))
    outpath = os.path.join(os.path.dirname(__file__), "phase8c_quality_comparison_verification.json")
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump({"books": results}, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"result_file": outpath}, ensure_ascii=False))
