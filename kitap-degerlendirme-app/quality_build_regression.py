from __future__ import annotations

import json
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from quality_regression_dataset import GOLDEN_BOOKS
from quality_benchmark import benchmark_snapshot
from text_quality import assert_no_mojibake, repair_payload_text
from theme_gain_analysis import (
    _consistency_overlap,
    _consistency_sentences,
    _fold_text,
    _summary_sentence_kind,
    _summary_forbidden_content_ratio,
    analyze_theme_gain,
    build_teacher_report_payload,
    kitap_tutarlilik_denetimi,
    prepare_theme_report_payload,
    summary_quality_issues,
)
from pipeline_runtime_enforcer import verify_summary_hash_consistency


MANDATORY_CASE_IDS = {case.case_id for case in GOLDEN_BOOKS}
CURRENT_REPORT = Path("quality_build_regression_report.json")
PREVIOUS_REPORT = Path("quality_build_regression_previous.json")


def _main_character(prepared: dict[str, Any]) -> str:
    for character in prepared.get("ana_karakterler", []) or []:
        if isinstance(character, dict) and character.get("ana_karakter_mi"):
            return str(character.get("ad") or character.get("karakter_adi") or "")
    return ""


def _central_entity_names(prepared: dict[str, Any]) -> list[str]:
    benchmark = benchmark_snapshot(prepared)
    return [str(item) for item in benchmark.get("central_entities") or [] if str(item).strip()]


def _names(items: list[dict[str, Any]] | None) -> list[str]:
    return [_fold_text(item.get("ad") or item.get("profil") or "") for item in items or [] if isinstance(item, dict)]


def _repair_mojibake_label(value: Any) -> str:
    text = str(value or "")
    try:
        repaired = text.encode("latin1").decode("utf-8")
        if repaired.count("�") <= text.count("�"):
            text = repaired
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    replacements = {
        "Ã§": "ç", "Ã‡": "Ç", "Ã¶": "ö", "Ã–": "Ö", "Ã¼": "ü", "Ãœ": "Ü",
        "Ä±": "ı", "Ä°": "İ", "ÄŸ": "ğ", "Ä": "Ğ", "ÅŸ": "ş", "Å": "Ş",
        "Ä±": "ı", "ÄŸ": "ğ", "ÅŸ": "ş",
    }
    for broken, fixed in replacements.items():
        text = text.replace(broken, fixed)
    return text


def _label_equal(left: Any, right: Any) -> bool:
    return _fold_text(_repair_mojibake_label(left)) == _fold_text(_repair_mojibake_label(right))


def _fake_character_names(prepared: dict[str, Any]) -> list[str]:
    fake_terms = {
        "bir", "sonra", "herkes", "kimse", "kutuphane", "gemi", "okyanus",
        "ispanya", "portekiz", "hindistan", "anlatici", "karakter",
    }
    names = []
    for character in prepared.get("ana_karakterler", []) or []:
        if not isinstance(character, dict):
            continue
        name = str(character.get("ad") or "")
        folded = _fold_text(name)
        if not folded or folded in fake_terms or str(character.get("entity_type") or "PERSON") != "PERSON":
            names.append(name)
    return names


def _evidence_explanations_ready(prepared: dict[str, Any]) -> bool:
    items = []
    for key in ["tema_analizi", "kazanim_analizi"]:
        items.extend(item for item in prepared.get(key, []) or [] if isinstance(item, dict))
    if not items:
        return False
    for item in items[:6]:
        if not item.get("kanitlar"):
            return False
        if not item.get("kanit_kalitesi_aciklamasi"):
            return False
    return True


def _quality_score(prepared: dict[str, Any]) -> int:
    quality = prepared.get("ozet_kalite_kontrol") if isinstance(prepared.get("ozet_kalite_kontrol"), dict) else {}
    for key in ["narrative_quality_score", "summary_score", "ozet_guven_skoru"]:
        value = quality.get(key) if key != "ozet_guven_skoru" else prepared.get(key)
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if number <= 1.0:
            number *= 100
        return int(round(max(0.0, min(100.0, number))))
    summary = str(prepared.get("kitap_ozeti") or "")
    penalty = len(summary_quality_issues(summary)) * 8
    return max(0, 75 - penalty)


def _manual_review_status(prepared: dict[str, Any]) -> str:
    quality = prepared.get("ozet_kalite_kontrol") if isinstance(prepared.get("ozet_kalite_kontrol"), dict) else {}
    if quality.get("manuel_inceleme") or quality.get("guvenilir_uretilemedi"):
        return "manual_review"
    return "clear"


def _teacher_report_status(prepared: dict[str, Any]) -> str:
    try:
        payload = build_teacher_report_payload(prepared)
    except Exception:
        return "failed"
    if payload.get("kisa_ogretmen_ozeti") and payload.get("kullanilabilecek_dersler") is not None:
        return "produced"
    return "failed"


def _top_theme_names(prepared: dict[str, Any], limit: int = 3) -> list[str]:
    return [str(item.get("ad") or "") for item in (prepared.get("tema_analizi") or [])[:limit] if isinstance(item, dict)]


def _summary_hash(text: str) -> str:
    normalized = re.sub(r"\s+", " ", str(text or "")).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _sentence_metrics(summary: str, evidence_text: str) -> dict[str, float]:
    sentences = _consistency_sentences(summary)
    if not sentences:
        return {
            "bridge_sentence_ratio": 0.0,
            "interpretation_sentence_ratio": 0.0,
            "avg_sentence_length": 0.0,
            "event_sentence_ratio": 0.0,
        }
    kinds = [_summary_sentence_kind(sentence, evidence_text) for sentence in sentences]
    bridge_count = sum(1 for kind in kinds if kind == "BRIDGE")
    interpretation_count = sum(1 for kind in kinds if kind in {"INTERPRETATION", "STATE"})
    event_count = sum(1 for kind in kinds if kind == "EVENT")
    avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences)
    return {
        "bridge_sentence_ratio": round(bridge_count / len(sentences), 3),
        "interpretation_sentence_ratio": round(interpretation_count / len(sentences), 3),
        "avg_sentence_length": round(avg_sentence_length, 2),
        "event_sentence_ratio": round(event_count / len(sentences), 3),
    }


def _evidence_density(prepared: dict[str, Any], summary: str) -> float:
    word_count = max(1, len(str(summary or "").split()))
    evidence_items = 0
    for key in ["tema_analizi", "kazanim_analizi", "deger_analizi"]:
        for item in prepared.get(key, []) or []:
            if isinstance(item, dict):
                evidence_items += len(item.get("kanitlar") or [])
    event_evidence = sum(
        1 for event in prepared.get("event_graph", []) or []
        if isinstance(event, dict) and (event.get("evidence") or event.get("evidence_sentence") or event.get("kanit_metni"))
    )
    return round(min(1.0, (evidence_items + event_evidence) / word_count), 3)


def _hallucination_ratio(prepared: dict[str, Any]) -> float:
    try:
        audit = kitap_tutarlilik_denetimi(prepared)
    except Exception:
        return 1.0
    unsupported = 0
    for key in ["unsupported_events", "unsupported_locations", "unsupported_objects"]:
        unsupported += len(audit.get(key) or [])
    sentences = max(1, len(_consistency_sentences(str(prepared.get("kitap_ozeti") or ""))))
    return round(min(1.0, unsupported / sentences), 3)


def _teacher_report_consistency(prepared: dict[str, Any], summary: str) -> float:
    try:
        teacher_payload = build_teacher_report_payload(prepared)
    except Exception:
        return 0.0
    teacher_summary = str(teacher_payload.get("kisa_ogretmen_ozeti") or "")
    return round(_consistency_overlap(summary, teacher_summary), 3)


def _narrative_metrics(prepared: dict[str, Any]) -> dict[str, Any]:
    summary = str(prepared.get("kitap_ozeti") or "")
    quality = prepared.get("ozet_kalite_kontrol") if isinstance(prepared.get("ozet_kalite_kontrol"), dict) else {}
    event_graph = prepared.get("event_graph") or []
    evidence_text = " ".join(
        str(event.get("evidence") or event.get("evidence_sentence") or event.get("kanit_metni") or "")
        for event in event_graph
        if isinstance(event, dict)
    )
    sentence_metrics = _sentence_metrics(summary, evidence_text)
    return {
        "summary_hash": _summary_hash(summary),
        "summary_similarity": 1.0,
        "event_count": len(event_graph),
        "bridge_sentence_ratio": sentence_metrics["bridge_sentence_ratio"],
        "interpretation_sentence_ratio": sentence_metrics["interpretation_sentence_ratio"],
        "avg_sentence_length": sentence_metrics["avg_sentence_length"],
        "event_density": round(float(quality.get("event_density") or sentence_metrics["event_sentence_ratio"] or 0.0), 3),
        "evidence_density": _evidence_density(prepared, summary),
        "hallucination_ratio": _hallucination_ratio(prepared),
        "narrative_diversity": round(float(quality.get("paraphrase_diversity") or 0.0), 3),
        "character_consistency": round(float(quality.get("character_consistency") or 0.0), 3),
        "teacher_report_consistency": _teacher_report_consistency(prepared, summary),
    }


def _report_blocked_only_by_summary_quality(row: dict[str, Any]) -> bool:
    if str(row.get("report_status") or "") != "blocked":
        return False
    reasons = " ".join(str(item) for item in (row.get("quality_gate_manual_reasons") or []))
    reasons = _fold_text(reasons + " " + str(row.get("rapor_guven_aciklamasi") or ""))
    blocking_terms = {"summary_quality", "ozet", "evidence_coverage", "kanit"}
    hard_terms = {"uydurma", "forbidden", "cross", "mojibake", "hash mismatch", "tutarsizlik"}
    return any(term in reasons for term in blocking_terms) and not any(term in reasons for term in hard_terms)


def _metric_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "summary_hash",
        "summary_similarity",
        "event_count",
        "bridge_sentence_ratio",
        "interpretation_sentence_ratio",
        "avg_sentence_length",
        "event_density",
        "evidence_density",
        "hallucination_ratio",
        "narrative_diversity",
        "character_consistency",
        "teacher_report_consistency",
    ]
    return {key: snapshot.get(key) for key in keys if key in snapshot}


def _narrative_metric_comparison(row: dict[str, Any], warnings: list[str], failures: list[str]) -> dict[str, Any]:
    snapshot = _metric_snapshot(row.get("snapshot") or {})
    current = dict(row.get("narrative_metrics") or {})
    summary = str(row.get("summary_text") or "")
    previous_summary = str((row.get("snapshot") or {}).get("summary_text") or "")
    if previous_summary:
        current["summary_similarity"] = round(_consistency_overlap(previous_summary, summary), 3)
    elif snapshot.get("summary_hash"):
        current["summary_similarity"] = 1.0 if snapshot.get("summary_hash") == current.get("summary_hash") else 0.0
    else:
        current["summary_similarity"] = 1.0
    row["narrative_metrics"] = current

    changes: list[dict[str, Any]] = []

    def add_change(metric: str, previous: Any, new: Any, reason: str, severity: str = "warning") -> None:
        changes.append({"metric": metric, "previous": previous, "new": new, "reason": reason, "severity": severity})
        target = failures if severity == "failure" else warnings
        target.append(f"{row['case_id']}:{metric}:{reason}")

    if snapshot.get("summary_hash") and snapshot.get("summary_hash") != current.get("summary_hash"):
        changes.append({
            "metric": "summary_hash",
            "previous": snapshot.get("summary_hash"),
            "new": current.get("summary_hash"),
            "reason": "summary text changed",
            "severity": "info",
        })
    if current.get("summary_similarity", 1.0) < 0.72:
        add_change("summary_similarity", snapshot.get("summary_similarity"), current.get("summary_similarity"), "summary similarity dustu")

    numeric_thresholds = {
        "event_count": (None, -2, "olay sayisi azaldi"),
        "bridge_sentence_ratio": (0.25, None, "bridge cumle orani artti"),
        "interpretation_sentence_ratio": (0.20, None, "yorumlayici cumle orani artti"),
        "avg_sentence_length": (8.0, None, "ortalama cumle uzunlugu artti"),
        "event_density": (None, -0.15, "event density azaldi"),
        "evidence_density": (None, -0.08, "evidence density azaldi"),
        "hallucination_ratio": (0.0, None, "hallucination ratio artti"),
        "narrative_diversity": (None, -0.08, "narrative diversity azaldi"),
        "character_consistency": (None, -0.10, "character consistency azaldi"),
        "teacher_report_consistency": (None, -0.12, "teacher report consistency azaldi"),
    }
    for metric, (max_increase, max_drop, reason) in numeric_thresholds.items():
        if snapshot.get(metric) is None or current.get(metric) is None:
            continue
        previous = float(snapshot.get(metric) or 0.0)
        new = float(current.get(metric) or 0.0)
        delta = round(new - previous, 3)
        if max_increase is not None and delta > max_increase:
            severity = "failure" if metric == "hallucination_ratio" and new > 0.15 else "warning"
            add_change(metric, previous, new, reason, severity)
        if max_drop is not None and delta < max_drop:
            add_change(metric, previous, new, reason)

    return {
        "case_id": row["case_id"],
        "kitap_adi": row["title"],
        "changes": changes,
        "current": current,
        "snapshot": snapshot,
    }


def _snapshot_comparison(row: dict[str, Any], failures: list[str], warnings: list[str]) -> dict[str, Any]:
    snapshot = row.get("snapshot") or {}
    previous_score = int(snapshot.get("summary_quality") or 0)
    new_score = int(row.get("summary_quality") or 0)
    score_delta = new_score - previous_score
    broken_fields: list[str] = []
    reasons: list[str] = []

    if previous_score and score_delta < -5:
        warnings.append(f"{row['case_id']}:summary_quality_drop:{score_delta}")
        broken_fields.append("summary_quality")
        reasons.append("summary quality 5 puandan fazla dustu")
    if previous_score and score_delta < -10:
        warnings.append(f"{row['case_id']}:summary_quality_regression_warning:{previous_score}->{new_score}")
        reasons.append("summary quality 10 puandan fazla dustu; rapor hard nedenle bloklanmadigi icin warning")
    if snapshot.get("book_type") and not _label_equal(snapshot.get("book_type"), row.get("book_type")):
        failures.append(f"{row['case_id']}:book_type_changed")
        broken_fields.append("book_type")
        reasons.append("book_type snapshot degerinden farkli")
    if snapshot.get("narrative_type") and not _label_equal(snapshot.get("narrative_type"), row.get("narrative_type")):
        failures.append(f"{row['case_id']}:narrative_type_changed")
        broken_fields.append("narrative_type")
        reasons.append("narrative_type snapshot degerinden farkli")
    previous_central_entities = snapshot.get("central_entities") or snapshot.get("main_characters") or []
    current_central_entities = (row.get("benchmark_snapshot") or {}).get("central_entities") or []
    if previous_central_entities:
        previous_names = {_fold_text(_repair_mojibake_label(item)) for item in previous_central_entities}
        current_names = {_fold_text(_repair_mojibake_label(item)) for item in current_central_entities}
        serious_drop = len(current_names) < max(1, len(previous_names) - 1)
        no_overlap = bool(current_names) and not previous_names.intersection(current_names)
        if serious_drop or no_overlap:
            failures.append(f"{row['case_id']}:central_entities_regression")
            broken_fields.append("central_entities")
            reasons.append("central_entities ciddi azaldi veya tamamen degisti")
        if len(previous_names) >= 2 and len(current_names) == 1:
            failures.append(f"{row['case_id']}:central_entity_count_dropped_to_1")
            broken_fields.append("central_entities")
            reasons.append("central_entity_count beklenmedik sekilde 1'e dustu")
    elif len(current_central_entities) == 1 and int(row.get("entity_count") or 0) >= 2:
        warnings.append(f"{row['case_id']}:central_entity_count_is_1_with_multiple_entities")
    if snapshot.get("main_theme") and row.get("actual_top_themes"):
        if _fold_text(_repair_mojibake_label(snapshot.get("main_theme"))) not in [_fold_text(_repair_mojibake_label(item)) for item in row.get("actual_top_themes", [])[:3]]:
            failures.append(f"{row['case_id']}:main_theme_changed")
            broken_fields.append("main_theme")
            reasons.append("ana tema ciddi degisti")
    current_unsupported = int(row.get("unsupported_event_count") or 0)
    previous_unsupported = int(snapshot.get("unsupported_event_count") or 0)
    if current_unsupported > previous_unsupported:
        failures.append(f"{row['case_id']}:unsupported_event_count_increased")
        broken_fields.append("unsupported_event_count")
        reasons.append("unsupported_event_count artti")
    if float(row.get("bridge_sentence_ratio") or 0.0) > 0.35:
        failures.append(f"{row['case_id']}:bridge_sentence_ratio_gt_35")
        broken_fields.append("bridge_sentence_ratio")
        reasons.append("bridge_sentence_ratio yuzde 35 ustunde")
    if float(row.get("repeated_event_ratio") or 0.0) > 0.35:
        failures.append(f"{row['case_id']}:repeated_event_ratio_gt_35")
        broken_fields.append("repeated_event_ratio")
        reasons.append("repeated_event_ratio yuzde 35 ustunde")
    if float(row.get("generic_event_ratio") or 0.0) > 0.40 and str(row.get("summary_strategy") or "") not in {"medium_safe_summary", "short_safe_summary"}:
        failures.append(f"{row['case_id']}:generic_event_ratio_without_safe_fallback")
        broken_fields.append("summary_strategy")
        reasons.append("generic_event_ratio yuksekken medium/short fallback secilmedi")
    if float(row.get("generic_event_ratio") or 0.0) > 0.30:
        failures.append(f"{row['case_id']}:generic_event_ratio_gt_30")
        broken_fields.append("generic_event_ratio")
        reasons.append("generic_event_ratio 0.30 ustunde")
    if int(row.get("blacklisted_central_entity_count") or 0) > 0:
        failures.append(f"{row['case_id']}:blacklisted_central_entity_count_gt_0")
        broken_fields.append("central_entities")
        reasons.append("blacklisted central_entity bulundu")
    if int(row.get("summary_word_count") or 0) == 17 and float(row.get("theme_confidence") or 0.0) >= 0.75:
        failures.append(f"{row['case_id']}:summary_17_word_fallback_with_high_theme")
        broken_fields.append("summary_word_count")
        reasons.append("guclu tema varken 17 kelimelik fallback uretildi")
    if float(row.get("theme_confidence") or 0.0) >= 0.75 and int(row.get("evidence_count") or 0) >= 3 and int(row.get("summary_word_count") or 0) < 70:
        failures.append(f"{row['case_id']}:strong_theme_evidence_summary_under_70")
        broken_fields.append("summary_word_count")
        reasons.append("guclu tema ve kanit varken ozet 70 kelime altinda")
    if row.get("summary_hash_mismatch"):
        failures.append(f"{row['case_id']}:checked_rendered_summary_mismatch")
        broken_fields.append("summary_hash")
        reasons.append("checked/rendered summary hash yuzeyleri esit degil")
    if str(row.get("summary_strategy") or "") == "failed":
        failures.append(f"{row['case_id']}:summary_strategy_failed")
        broken_fields.append("summary_strategy")
        reasons.append("summary_strategy failed oldu")
    if str(row.get("report_status") or "") == "blocked":
        failures.append(f"{row['case_id']}:report_status_blocked")
        broken_fields.append("report_status")
        reasons.append("report_status blocked oldu")
    if row.get("mojibake_detected"):
        failures.append(f"{row['case_id']}:mojibake_detected")
        broken_fields.append("mojibake_detected")
        reasons.append("mojibake_detected true")
    if row.get("error_phrase_missing_in_rendered_summary"):
        failures.append(f"{row['case_id']}:error_phrase_missing_in_rendered_summary")
        broken_fields.append("error_phrase_missing_in_rendered_summary")
        reasons.append("hata ifadesi gorunen ozette yok")
    if _report_blocked_only_by_summary_quality(row):
        failures.append(f"{row['case_id']}:blocked_only_by_summary_quality")
        broken_fields.append("report_status")
        reasons.append("rapor sadece summary_quality/evidence_coverage nedeniyle bloklandi")
    if str(row.get("summary_strategy") or "") == "natural_summary" and (
        int(row.get("summary_quality") or 0) < 65 or int(row.get("canonical_event_count") or 0) < 5
    ):
        failures.append(f"{row['case_id']}:long_strategy_with_low_quality")
        broken_fields.append("summary_strategy")
        reasons.append("quality veya olay kapsami dusukken natural_summary secildi")
    if snapshot.get("teacher_report_status") == "produced" and row.get("teacher_report_status") != "produced":
        failures.append(f"{row['case_id']}:teacher_report_missing")
        broken_fields.append("teacher_report_status")
        reasons.append("teacher report daha once uretiliyordu, simdi uretilemiyor")
    if snapshot.get("manual_review_status") == "clear" and row.get("manual_review_status") != "clear":
        failures.append(f"{row['case_id']}:manual_review_regression")
        broken_fields.append("manual_review_status")
        reasons.append("manual review durumu temizden incelemeye dustu")

    return {
        "case_id": row["case_id"],
        "kitap_adi": row["title"],
        "previous_score": previous_score,
        "new_score": new_score,
        "fark": score_delta,
        "kirilan_alan": sorted(set(broken_fields)),
        "sebep": "; ".join(dict.fromkeys(reasons)) or "degisim yok",
    }


def run_build_regression(write_report: bool = True) -> dict[str, Any]:
    rows = []
    failures = []
    warnings = []
    for case in GOLDEN_BOOKS:
        result = analyze_theme_gain(case.text, {"baslik": case.title, "yazar": case.author}, case.age_group, "standart")
        prepared = prepare_theme_report_payload(result)
        main_character = _main_character(prepared)
        themes = _names(prepared.get("tema_analizi"))
        gains = _names(prepared.get("kazanim_analizi"))
        expected_theme = _fold_text(case.expected_main_theme)
        expected_gains = [_fold_text(item) for item in case.expected_top_gains]
        snapshot = case.golden_snapshot
        quality = prepared.get("ozet_kalite_kontrol") if isinstance(prepared.get("ozet_kalite_kontrol"), dict) else {}
        summary_text = str(prepared.get("kitap_ozeti") or "")
        forbidden_ratio = _summary_forbidden_content_ratio(summary_text)
        structural_summary_issues = summary_quality_issues(summary_text)
        narrative_metrics = _narrative_metrics(prepared)
        benchmark = benchmark_snapshot(
            prepared,
            teacher_report_status=_teacher_report_status(prepared),
            manual_review_status=_manual_review_status(prepared),
        )
        row = {
            "case_id": case.case_id,
            "title": case.title,
            "book_type": prepared.get("book_type"),
            "book_subtype": prepared.get("book_subtype"),
            "narrative_type": prepared.get("narrative_type"),
            "benchmark_snapshot": benchmark,
            "snapshot": snapshot.__dict__ if snapshot else {},
            "summary_text": summary_text,
            "summary_hash": narrative_metrics["summary_hash"],
            "narrative_metrics": narrative_metrics,
            "expected_main_character": case.expected_main_character,
            "actual_main_character": main_character,
            "central_entities": benchmark.get("central_entities"),
            "blacklisted_central_entity_count": benchmark.get("blacklisted_central_entity_count"),
            "main_character_ok": (
                not case.expected_main_character
                or _fold_text(main_character) == _fold_text(case.expected_main_character)
            ),
            "expected_main_theme": case.expected_main_theme,
            "actual_top_themes": _top_theme_names(prepared),
            "theme_ok": expected_theme in themes[:3] or bool(themes and expected_theme in themes[0]),
            "expected_top_gains": case.expected_top_gains,
            "actual_top_gains": [item.get("ad") for item in prepared.get("kazanim_analizi", [])[:5]],
            "gain_ok": any(expected in gains[:5] for expected in expected_gains),
            "fake_characters": _fake_character_names(prepared),
            "fake_character_ok": not _fake_character_names(prepared),
            "evidence_quality_ok": _evidence_explanations_ready(prepared),
            "summary_quality": _quality_score(prepared),
            "report_confidence": prepared.get("rapor_guven_skoru"),
            "teacher_report_status": _teacher_report_status(prepared),
            "manual_review_status": _manual_review_status(prepared),
            "report_status": benchmark.get("report_status"),
            "summary_strategy": benchmark.get("summary_strategy"),
            "summary_confidence": benchmark.get("summary_confidence"),
            "entity_confidence": benchmark.get("entity_confidence"),
            "event_confidence": benchmark.get("event_confidence"),
            "event_coverage": benchmark.get("event_coverage"),
            "evidence_coverage": benchmark.get("evidence_coverage"),
            "repeated_event_ratio": benchmark.get("repeated_event_ratio"),
            "generic_event_ratio": benchmark.get("generic_event_ratio"),
            "low_confidence_event_count": benchmark.get("low_confidence_event_count"),
            "theme_confidence": benchmark.get("theme_confidence"),
            "canonical_event_count": benchmark.get("canonical_event_count"),
            "summary_word_count": benchmark.get("summary_word_count"),
            "evidence_count": sum(
                len(item.get("kanitlar") or [])
                for item in prepared.get("tema_analizi", []) or []
                if isinstance(item, dict)
            ),
            "entity_count": benchmark.get("entity_count"),
            "bridge_sentence_ratio": benchmark.get("bridge_sentence_ratio"),
            "quote_ratio": benchmark.get("quote_ratio"),
            "unsupported_event_count": benchmark.get("unsupported_event_count"),
            "mojibake_detected": benchmark.get("mojibake_detected"),
            "mojibake_issues": benchmark.get("mojibake_issues"),
            "error_phrase_missing_in_rendered_summary": (prepared.get("summary_consistency_audit") or {}).get("error_phrase_missing_in_rendered_summary", False),
            "summary_quality_issues": structural_summary_issues,
            "forbidden_patterns": [] if forbidden_ratio == 0 else ["forbidden_content_ratio_nonzero"],
            "forbidden_ratio": forbidden_ratio,
            "forbidden_pattern_ok": forbidden_ratio == 0,
            "character_count": len(prepared.get("ana_karakterler") or []),
            "quality_gate_manual_reasons": quality.get("manual_review_reasons") or [],
            "rapor_guven_skoru": prepared.get("rapor_guven_skoru"),
            "rapor_guven_aciklamasi": prepared.get("rapor_guven_aciklamasi"),
            "summary_hash_mismatch": not verify_summary_hash_consistency(prepared).get("hash_consistency_pass", True),
        }
        if case.expected_book_type and _fold_text(case.expected_book_type) not in _fold_text(str(row["book_type"] or "")):
            row["expected_book_type_ok"] = False
        else:
            row["expected_book_type_ok"] = True
        for key in ["fake_character_ok", "forbidden_pattern_ok"]:
            if not row[key]:
                failures.append(f"{case.case_id}:{key}")
        rows.append(row)

    previous = None
    if PREVIOUS_REPORT.exists():
        try:
            previous = json.loads(PREVIOUS_REPORT.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previous = None
    previous_rows = {row.get("case_id"): row for row in (previous or {}).get("rows", []) if isinstance(row, dict)}
    comparisons = []
    for row in rows:
        old = previous_rows.get(row["case_id"])
        if not old:
            comparisons.append({"case_id": row["case_id"], "status": "no_previous_baseline"})
            continue
        comparisons.append({
            "case_id": row["case_id"],
            "main_character_changed": old.get("actual_main_character") != row.get("actual_main_character"),
            "theme_changed": old.get("actual_top_themes") != row.get("actual_top_themes"),
            "gain_changed": old.get("actual_top_gains") != row.get("actual_top_gains"),
            "previous_report_confidence": old.get("rapor_guven_skoru"),
            "current_report_confidence": row.get("rapor_guven_skoru"),
        })
    snapshot_comparisons = [_snapshot_comparison(row, failures, warnings) for row in rows]
    narrative_metric_comparisons = [
        _narrative_metric_comparison(row, warnings, failures)
        for row in rows
    ]
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mandatory_case_ids": sorted(MANDATORY_CASE_IDS),
        "passed": not failures,
        "warnings": warnings,
        "failures": failures,
        "rows": rows,
        "snapshot_comparison": snapshot_comparisons,
        "narrative_metric_comparison": narrative_metric_comparisons,
        "comparison_to_previous_build": comparisons,
    }
    report = repair_payload_text(report)
    assert_no_mojibake(report, path="quality_build_regression_report")
    if write_report:
        if CURRENT_REPORT.exists():
            PREVIOUS_REPORT.write_text(CURRENT_REPORT.read_text(encoding="utf-8"), encoding="utf-8")
        CURRENT_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    build_report = run_build_regression(write_report=True)
    print(json.dumps({
        "passed": build_report["passed"],
        "failures": build_report["failures"],
        "warnings": build_report["warnings"],
        "mandatory_case_ids": build_report["mandatory_case_ids"],
    }, ensure_ascii=False))
    raise SystemExit(0 if build_report["passed"] else 1)
