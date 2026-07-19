from __future__ import annotations

from typing import Any

from summary_strategy_selector import bridge_sentence_ratio, event_graph_quality_metrics
from pipeline_runtime_enforcer import is_central_entity_blacklisted
from text_quality import collect_text_quality_issues


def _entity_name(item: dict[str, Any]) -> str:
    return str(item.get("ad") or item.get("karakter_adi") or item.get("entity_name") or "").strip()


def _central_entities(characters: list[dict[str, Any]]) -> list[str]:
    central = [
        _entity_name(item)
        for item in characters
        if item.get("ana_karakter_mi") or item.get("central_entity") or item.get("merkezi_varlik_mi")
    ]
    if not central:
        ranked = sorted(
            characters,
            key=lambda item: float(item.get("guven_skoru") or item.get("centrality_score") or 0.0),
            reverse=True,
        )
        central = [_entity_name(item) for item in ranked[:3]]
    return [name for name in central if name]


def _blacklisted_central_entity_count(prepared: dict[str, Any], characters: list[dict[str, Any]]) -> int:
    title = (prepared or {}).get("kitap_adi") or (prepared or {}).get("baslik") or ""
    count = 0
    for item in characters:
        if not isinstance(item, dict):
            continue
        if not (item.get("ana_karakter_mi") or item.get("central_entity") or item.get("merkezi_varlik_mi")):
            continue
        name = _entity_name(item)
        blacklisted, _reason = is_central_entity_blacklisted(name, title)
        if blacklisted:
            count += 1
    return count


def benchmark_snapshot(prepared: dict[str, Any], teacher_report_status: str = "", manual_review_status: str = "") -> dict[str, Any]:
    summary = str((prepared or {}).get("kitap_ozeti") or "")
    themes = [item for item in (prepared or {}).get("tema_analizi", []) if isinstance(item, dict)]
    characters = [item for item in (prepared or {}).get("ana_karakterler", []) if isinstance(item, dict)]
    events = [item for item in (prepared or {}).get("event_graph", []) if isinstance(item, dict)]
    unsupported_event_count = len((prepared or {}).get("unsupported_events") or [])
    quality = (prepared or {}).get("ozet_kalite_kontrol") if isinstance((prepared or {}).get("ozet_kalite_kontrol"), dict) else {}
    mojibake_issues = collect_text_quality_issues(prepared or {}, path="benchmark", limit=10)
    central_entities = _central_entities(characters)
    event_quality = event_graph_quality_metrics(events)
    return {
        "book_title": (prepared or {}).get("kitap_adi") or (prepared or {}).get("baslik") or "",
        "book_type": (prepared or {}).get("book_type") or "",
        "narrative_type": (prepared or {}).get("narrative_type") or "",
        "main_theme": (prepared or {}).get("ana_tema") or "",
        "top_3_themes": [str(item.get("ad") or "") for item in themes[:3]],
        "central_entities": central_entities,
        "blacklisted_central_entity_count": _blacklisted_central_entity_count(prepared or {}, characters),
        "main_characters": central_entities,
        "entity_count": len(characters),
        "canonical_event_count": (prepared or {}).get("canonical_event_count", len(events)),
        "summary_strategy": (prepared or {}).get("summary_strategy") or (prepared or {}).get("ozet_turu") or "",
        "summary_word_count": len(summary.split()),
        "summary_confidence": (prepared or {}).get("summary_confidence", (prepared or {}).get("ozet_guven_skoru", 0)),
        "entity_confidence": (prepared or {}).get("entity_confidence", 0),
        "event_confidence": (prepared or {}).get("event_confidence", quality.get("event_completeness", 0)),
        "event_coverage": (prepared or {}).get("event_coverage", quality.get("event_coverage", quality.get("event_completeness", 0))),
        "evidence_coverage": (prepared or {}).get("evidence_coverage", quality.get("evidence_coverage", quality.get("evidence_density", 0))),
        "repeated_event_ratio": (prepared or {}).get("repeated_event_ratio", event_quality.get("repeated_event_ratio", 0)),
        "generic_event_ratio": (prepared or {}).get("generic_event_ratio", event_quality.get("generic_event_ratio", 0)),
        "low_confidence_event_count": (prepared or {}).get("low_confidence_event_count", event_quality.get("low_confidence_event_count", 0)),
        "theme_confidence": (prepared or {}).get("theme_confidence", (prepared or {}).get("ana_tema_guven_skoru", 0)),
        "bridge_sentence_ratio": (prepared or {}).get("bridge_sentence_ratio", bridge_sentence_ratio(summary)),
        "quote_ratio": (prepared or {}).get("quote_ratio", quality.get("quote_ratio", 0)),
        "unsupported_event_count": unsupported_event_count,
        "mojibake_detected": bool(mojibake_issues),
        "mojibake_issues": mojibake_issues,
        "teacher_report_status": teacher_report_status or "unknown",
        "manual_review_status": manual_review_status or "unknown",
        "report_status": (prepared or {}).get("report_status") or ("blocked" if (prepared or {}).get("report_blocking_reasons") else "produced"),
    }
