from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from pipeline_runtime_enforcer import (
    is_generic_event_action,
    classify_event_graph_concreteness,
    count_canonical_events,
    compute_generic_event_ratio,
    should_use_evidence_based_medium_summary,
)


BRIDGE_PATTERNS = [
    "boylece onceki bilgi",
    "böylece önceki bilgi",
    "bu nedenle olaylar",
    "son adim onceki",
    "son adım önceki",
    "onceki gelisme",
    "önceki gelişme",
    "olaylar ayni sorun",
    "olaylar aynı sorun",
    "sonraki gelisme",
    "sonraki gelişme",
    "bu surecte kisiler",
    "bu süreçte kişiler",
]


def fold_text(text: object) -> str:
    folded = unicodedata.normalize("NFKD", str(text or ""))
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    folded = folded.translate(str.maketrans({"ı": "i", "İ": "i", "ş": "s", "Ş": "s"}))
    return folded.lower()


def split_sentences(text: str) -> list[str]:
    return [item.strip() for item in re.split(r"(?<=[.!?])\s+", str(text or "")) if item.strip()]


def bridge_sentence_ratio(summary: str) -> float:
    sentences = split_sentences(summary)
    if not sentences:
        return 0.0
    bridge_count = 0
    for sentence in sentences:
        folded = fold_text(sentence)
        if any(fold_text(pattern) in folded for pattern in BRIDGE_PATTERNS):
            bridge_count += 1
    return round(bridge_count / len(sentences), 3)


def event_graph_quality_metrics(events: list[dict[str, Any]]) -> dict[str, float | int]:
    valid_events = [item for item in events or [] if isinstance(item, dict)]
    if not valid_events:
        return {"repeated_event_ratio": 0.0, "generic_event_ratio": 0.0, "low_confidence_event_count": 0}
    template_counts: dict[str, int] = {}
    generic_count = 0
    low_count = 0
    # Classify event concreteness using the improved fix module
    classified_events = classify_event_graph_concreteness(valid_events)
    for event in classified_events:
        action = fold_text(event.get("action") or "")
        key = str(event.get("event_template_key") or f"{fold_text(event.get('olay_turu') or '')}:{action}:{bool(event.get('object') or event.get('target'))}")
        template_counts[key] = template_counts.get(key, 0) + 1
        if event.get("generic_event") or is_generic_event_action(action):
            generic_count += 1
        if event.get("low_confidence_event"):
            low_count += 1
    repeated = sum(max(0, count - 2) for count in template_counts.values())
    return {
        "repeated_event_ratio": round(repeated / max(1, len(valid_events)), 3),
        "generic_event_ratio": round(generic_count / max(1, len(valid_events)), 3),
        "low_confidence_event_count": low_count,
    }


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


@dataclass(frozen=True)
class SummaryStrategyDecision:
    summary_strategy: str
    summary_confidence: float
    entity_confidence: float
    event_confidence: float
    theme_confidence: float
    canonical_event_count: int
    event_coverage: float
    evidence_coverage: float
    repeated_event_ratio: float
    generic_event_ratio: float
    low_confidence_event_count: int
    bridge_sentence_ratio: float
    quote_ratio: float
    report_blocking_reasons: list[str]


def select_summary_strategy(
    payload: dict[str, Any],
    summary: str | None = None,
    quality_metrics: dict[str, Any] | None = None,
    consistency_audit: dict[str, Any] | None = None,
) -> SummaryStrategyDecision:
    quality_metrics = quality_metrics or {}
    consistency_audit = consistency_audit or {}
    summary_text = summary if summary is not None else str((payload or {}).get("kitap_ozeti") or "")
    characters = [item for item in (payload or {}).get("ana_karakterler", []) if isinstance(item, dict)]
    events = [item for item in (payload or {}).get("event_graph", []) if isinstance(item, dict)]
    themes = [item for item in (payload or {}).get("tema_analizi", []) if isinstance(item, dict)]
    canonical_event_count = len(events)
    event_quality = event_graph_quality_metrics(events)

    entity_confidence = _clamp(sum(float(item.get("guven_skoru") or 0.6) for item in characters) / max(1, len(characters))) if characters else 0.55
    event_coverage = _clamp(float(quality_metrics.get("event_coverage") or quality_metrics.get("event_completeness") or 0.0) or min(0.9, canonical_event_count / 8))
    evidence_coverage = _clamp(float(quality_metrics.get("evidence_coverage") or quality_metrics.get("evidence_density") or 0.0))
    event_confidence = _clamp(float((payload or {}).get("event_confidence") or 0.0) or event_coverage)
    theme_confidence = _clamp(sum(float(item.get("guven_skoru") or 0.0) for item in themes[:3]) / max(1, len(themes[:3]))) if themes else 0.45
    base_summary_confidence = float((payload or {}).get("ozet_guven_skoru") or quality_metrics.get("summary_score") or 0.0)
    if base_summary_confidence > 1:
        base_summary_confidence /= 100
    quote_ratio = _clamp(float(quality_metrics.get("quote_ratio") or 0.0))
    bridge_ratio = bridge_sentence_ratio(summary_text)

    summary_confidence = _clamp(
        0.45 * base_summary_confidence
        + 0.25 * event_confidence
        + 0.15 * entity_confidence
        + 0.15 * theme_confidence
    )
    if bridge_ratio > 0.20:
        summary_confidence = _clamp(summary_confidence - min(0.25, bridge_ratio - 0.20))
    if quote_ratio > 0.35:
        summary_confidence = _clamp(summary_confidence - 0.10)
    if float(event_quality.get("repeated_event_ratio") or 0.0) > 0.35:
        summary_confidence = _clamp(summary_confidence - 0.18)
        event_confidence = _clamp(event_confidence - 0.20)
    if float(event_quality.get("generic_event_ratio") or 0.0) > 0.40:
        summary_confidence = _clamp(summary_confidence - 0.12)
        event_confidence = _clamp(event_confidence - 0.15)

    # Compute true canonical event count from classified events
    true_canonical_count = count_canonical_events(events)
    generic_event_ratio = float(event_quality.get("generic_event_ratio") or 0.0)
    evidence_count = int(quality_metrics.get("evidence_count") or len(themes) * 2 or 0)
    
    # New rule: if theme is strong but events are generic, use evidence_based_medium_summary
    should_use_evidence_based, evidence_based_reason = should_use_evidence_based_medium_summary(
        theme_confidence=theme_confidence,
        event_confidence=event_confidence,
        canonical_event_count=true_canonical_count,
        generic_event_ratio=generic_event_ratio,
        evidence_count=evidence_count,
    )
    
    theme_strong_event_weak = theme_confidence >= 0.70 and (true_canonical_count < 3 or event_confidence < 0.45)
    repeated_or_generic = (
        float(event_quality.get("repeated_event_ratio") or 0.0) > 0.35
        or generic_event_ratio > 0.40
    )
    
    if should_use_evidence_based:
        strategy = "medium_safe_summary"
        # Override summary_confidence to prevent fallback to short_safe_summary
        summary_confidence = _clamp(max(summary_confidence, 0.55))
    elif theme_strong_event_weak:
        strategy = "medium_safe_summary"
        summary_confidence = _clamp(max(summary_confidence, 0.50))
    elif true_canonical_count < 3 and evidence_count <= 0:
        strategy = "short_safe_summary"
    elif repeated_or_generic:
        strategy = "medium_safe_summary"
    elif summary_confidence < 0.50:
        strategy = "short_safe_summary"
    elif bridge_ratio > 0.35:
        strategy = "medium_safe_summary"
    elif summary_confidence >= 0.75 and true_canonical_count >= 5 and bridge_ratio <= 0.20:
        strategy = "natural_summary"
    else:
        strategy = "medium_safe_summary"

    blocking_reasons: list[str] = []
    for key, label in [
        ("unsupported_characters", "uydurma_karakter"),
        ("unsupported_locations", "uydurma_mekan"),
        ("unsupported_events", "uydurma_olay"),
    ]:
        if consistency_audit.get(key):
            blocking_reasons.append(label)
    if consistency_audit.get("state_contamination") or consistency_audit.get("cross_book_state_contamination"):
        blocking_reasons.append("cross_book_state_contamination")
    if consistency_audit.get("system_inconsistency"):
        blocking_reasons.append("sistem_ici_veri_tutarsizligi")

    return SummaryStrategyDecision(
        summary_strategy=strategy,
        summary_confidence=summary_confidence,
        entity_confidence=entity_confidence,
        event_confidence=event_confidence,
        theme_confidence=theme_confidence,
        canonical_event_count=canonical_event_count,
        event_coverage=event_coverage,
        evidence_coverage=evidence_coverage,
        repeated_event_ratio=float(event_quality.get("repeated_event_ratio") or 0.0),
        generic_event_ratio=float(event_quality.get("generic_event_ratio") or 0.0),
        low_confidence_event_count=int(event_quality.get("low_confidence_event_count") or 0),
        bridge_sentence_ratio=bridge_ratio,
        quote_ratio=quote_ratio,
        report_blocking_reasons=list(dict.fromkeys(blocking_reasons)),
    )


def apply_summary_strategy(payload: dict[str, Any], decision: SummaryStrategyDecision) -> dict[str, Any]:
    updated = dict(payload or {})
    updated["summary_strategy"] = decision.summary_strategy
    updated["summary_confidence"] = decision.summary_confidence
    updated["entity_confidence"] = decision.entity_confidence
    updated["event_confidence"] = decision.event_confidence
    updated["theme_confidence"] = decision.theme_confidence
    updated["canonical_event_count"] = decision.canonical_event_count
    updated["event_coverage"] = decision.event_coverage
    updated["evidence_coverage"] = decision.evidence_coverage
    updated["repeated_event_ratio"] = decision.repeated_event_ratio
    updated["generic_event_ratio"] = decision.generic_event_ratio
    updated["low_confidence_event_count"] = decision.low_confidence_event_count
    updated["bridge_sentence_ratio"] = decision.bridge_sentence_ratio
    updated["quote_ratio"] = decision.quote_ratio
    updated["report_blocking_reasons"] = decision.report_blocking_reasons
    if decision.summary_strategy == "natural_summary":
        updated["ozet_turu"] = "natural_summary"
    elif decision.summary_strategy == "medium_safe_summary":
        updated["ozet_turu"] = "medium_safe_summary"
    elif decision.summary_strategy == "short_safe_summary":
        updated["ozet_turu"] = "short_safe_summary"
    else:
        updated["ozet_turu"] = "safe_limited"
    updated["ozet_guven_skoru"] = decision.summary_confidence
    return updated
