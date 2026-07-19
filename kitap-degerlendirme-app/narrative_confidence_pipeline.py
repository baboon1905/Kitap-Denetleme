"""
Narrative Confidence Pipeline — Event Graph → Summary Confidence → Natural/Conservative Summary → Validator → Teacher Report → PDF

Flow:
  Event Graph
  ↓
  Summary Confidence (ozet_guven_skoru)
  ↓
  if confidence >= 0.75 → Natural Summary (full narrative_realize output)
  else → Conservative Summary (evidence-anchored, limited narrative)
  ↓
  Validator (kitap_tutarlilik_denetimi + rapor_kalite_kapisi)
  ↓
  Teacher Report (build_teacher_report_payload)
  ↓
  PDF (generate_teacher_report_pdf)
"""

from __future__ import annotations

import io
import json
import os
from datetime import datetime
from typing import Iterable, List

from theme_gain_analysis import (
    _build_evidence_based_summary,
    _direct_quote_overlap_ratio,
    _event_graph_completeness_score,
    _event_graph_has_concrete_actions,
    _event_graph_has_real_evidence,
    event_graph_quality_metrics,
    _select_report_summary,
    _summary_confidence_score,
    _summary_concreteness_score,
    _summary_forbidden_content_ratio,
    _summary_has_forbidden_content,
    _summary_heading_count,
    _summary_is_reportable_with_lower_confidence,
    _summary_is_valid_for_report,
    _summary_quality_gate_metrics,
    _synchronize_summary_surfaces,
    build_teacher_report_payload,
    generate_teacher_report_pdf,
    kitap_tutarlilik_denetimi,
    prepare_theme_report_payload,
    rapor_kalite_kapisi,
    sanitize_character_profiles,
)

from narrative_realizer import (
    build_story_graph,
    narrative_realize,
    narrative_realize_olay_akisi,
    reconstruct_story_events,
    NARRATIVE_FORBIDDEN_FOLDED,
)
from theme_gain_analysis import PIPELINE_SUMMARY_FORBIDDEN_FOLDED
from narrative_planner import attach_narrative_plan
from narrative_type_classifier import classify_narrative_type
from summary_strategy_selector import apply_summary_strategy, select_summary_strategy

# ---------------------------------------------------------------------------
# 1. CONFIDENCE CALCULATION from event_graph + quality metrics
# ---------------------------------------------------------------------------

NATURAL_CONFIDENCE_THRESHOLD = 0.75
CONSERVATIVE_CONFIDENCE_FLOOR = 0.40


def _calculate_event_graph_confidence(
    event_graph: list[dict],
    characters: Iterable[dict],
    summary: str = "",
) -> float:
    """
    Calculate confidence score based on event graph quality and summary metrics.
    Returns a float 0.0–0.95.
    """
    if not event_graph or len(event_graph) < 3:
        return 0.0

    event_count = len(event_graph)
    has_real_evidence = _event_graph_has_real_evidence(event_graph)
    has_concrete_actions = _event_graph_has_concrete_actions(event_graph)
    completeness = _event_graph_completeness_score(event_graph)
    event_quality = event_graph_quality_metrics(event_graph)

    # Base score from graph properties
    score = 0.0
    if event_count >= 8:
        score += 0.25
    elif event_count >= 5:
        score += 0.20
    else:
        score += 0.10 + (event_count - 3) * 0.03

    if has_real_evidence:
        score += 0.20
    if has_concrete_actions:
        score += 0.15

    score += completeness * 0.25

    # Character diversity bonus
    char_set = set()
    for node in event_graph:
        actors = node.get("actors") or node.get("ilgili_karakterler") or []
        for actor in actors if isinstance(actors, list) else [actors]:
            if str(actor).strip():
                char_set.add(str(actor).strip().lower())
    character_diversity = min(1.0, len(char_set) / 4) * 0.10
    score += character_diversity

    # Page spread bonus
    pages = {
        node.get("page") or node.get("sayfa")
        for node in event_graph
        if node.get("page") or node.get("sayfa")
    }
    if len(pages) >= 5:
        score += 0.05
    if float(event_quality.get("repeated_event_ratio") or 0.0) > 0.35:
        score -= 0.20
    if float(event_quality.get("generic_event_ratio") or 0.0) > 0.40:
        score -= 0.15

    # If summary is provided, factor in quality metrics
    if summary and len(summary.split()) >= 50:
        quality_metrics = _summary_quality_gate_metrics(
            summary,
            {"event_graph": event_graph, "ana_karakterler": list(characters)},
            [],
        )
        if quality_metrics.get("narrative_quality_score"):
            score = (score + float(quality_metrics["narrative_quality_score"])) / 2
        if quality_metrics.get("evidence_coverage"):
            score += float(quality_metrics["evidence_coverage"]) * 0.10
        if quality_metrics.get("character_consistency"):
            score += float(quality_metrics["character_consistency"]) * 0.05
        quote_ratio = _direct_quote_overlap_ratio(summary, event_graph)
        if quote_ratio > 0.40:
            score -= 0.20
        elif quote_ratio > 0.25:
            score -= 0.10
        if quality_metrics.get("repeated_sentence_ratio"):
            score -= min(0.15, float(quality_metrics["repeated_sentence_ratio"]))

    return round(min(0.95, max(0.0, score)), 2)


# ---------------------------------------------------------------------------
# 2. HELPER — filter pipeline phrases from text
# ---------------------------------------------------------------------------

_ALL_FORBIDDEN_FOLDED = set(
    PIPELINE_SUMMARY_FORBIDDEN_FOLDED
    + NARRATIVE_FORBIDDEN_FOLDED
    + [
        "olay adimi", "olay zincirinde", "baslangic durumu",
        "onceki olayda ortaya cikan durum", "catismanin belirginlesmesi",
        "cozumun gorunmesi", "ipucu ve arastirma", "karar ani",
        "sahnedeki sorun", "sahnedeki belirsizlik",
        "daha once ogrenilenler", "belirleyici bir iz",
        "onemli bir ipucu", "onemli bulusunu paylasir",
        "cozum yolunu baslatir", "olayin anlamini kavrar",
        "bu gelismeden sonra", "onceki gelismenin ardindan",
        "onceki sahnedeki bilgi",
        "bilgi veya nesne baska bir kisiye aktarilir",
        "sahne yeni bir yere veya karara yonelir",
        "cozum icin kullanilabilecek bilgi ortaya cikar",
        "karabasan sorununa karsi cozum arayisi belirginlesir",
        "paylasim karakterler arasindaki yonelisi degistirir",
        "anlati ilerler", "yeni yon kazanir", "bu asamada",
        "olaylar gelisir", "karakter harekete gecer", "olay zinciri",
        "somut bir adim", "cozum icin harekete gecer",
        "durumu daha iyi anlar",
    ]
)


def _text_has_forbidden_phrase(text: str) -> bool:
    """Check if text contains any pipeline/forbidden phrase."""
    folded = text.lower()
    for phrase in _ALL_FORBIDDEN_FOLDED:
        if phrase in folded:
            return True
    return False


# ---------------------------------------------------------------------------
# 3. CONSERVATIVE SUMMARY — evidence-anchored, limited narrative
# ---------------------------------------------------------------------------

CONSERVATIVE_SUMMARY_MIN_WORDS = 40
CONSERVATIVE_SUMMARY_MAX_WORDS = 200


def _generate_conservative_summary(
    title: str,
    event_graph: list[dict],
    characters: Iterable[dict],
) -> str:
    """
    Generate a conservative, evidence-anchored summary when confidence < 0.75.
    - Shorter (60–200 words)
    - Uses direct evidence sentences + event properties
    - No narrative embellishment
    - Focuses on confirmed events only
    - Falls back to raw event_graph nodes if reconstruct_story_events is empty
    """
    char_list = list(sanitize_character_profiles(characters))
    main_actor = char_list[0]["ad"] if char_list else "merkez karakter"

    # Try using both raw event_graph and story events
    source_events = reconstruct_story_events(event_graph)
    if not source_events:
        # Fall back to raw event_graph
        source_events = [
            {
                "page": n.get("sayfa"),
                "sayfa": n.get("sayfa"),
                "actor": (n.get("actors") or n.get("ilgili_karakterler") or [None])[0] if isinstance(n.get("actors") or n.get("ilgili_karakterler"), list) else n.get("actors"),
                "actors": n.get("actors") or n.get("ilgili_karakterler") or [],
                "action": n.get("action", ""),
                "evidence": n.get("evidence") or n.get("kanit_metni") or n.get("kaynak_metin") or "",
                "goal": n.get("goal") or n.get("neden") or n.get("reason") or "",
                "consequence": n.get("consequence") or n.get("sonuc") or "",
                "object": n.get("object") or n.get("nesne") or "",
                "obstacle": n.get("obstacle") or n.get("conflict") or "",
                "kaynak_metin": n.get("kaynak_metin") or "",
                "olay_basligi": n.get("olay_basligi") or "",
            }
            for n in event_graph
        ]

    sentences: list[str] = []
    combined_lower = ""  # for dedup tracking

    # Opening — factual, simple
    opening = f"{title}, {main_actor} çevresinde gelişen olayları kronolojik sırayla izler."
    sentences.append(opening)
    combined_lower = opening.lower()

    # Core events — evidence anchored, verbose
    for event in source_events[:10]:
        actors = event.get("actors") or event.get("ilgili_karakterler") or []
        action = event.get("action") or ""
        evidence = (
            event.get("evidence")
            or event.get("kanit_metni")
            or event.get("kaynak_metin")
            or ""
        )
        goal = event.get("goal") or event.get("neden") or event.get("reason") or ""
        consequence = event.get("consequence") or event.get("sonuc") or ""
        obj = event.get("object") or event.get("nesne") or ""
        obstacle = event.get("obstacle") or event.get("conflict") or ""

        if not action and not evidence and not goal:
            continue

        actor_text = actors[0] if isinstance(actors, list) and actors else main_actor
        actor_list_str = ", ".join(str(a) for a in actors if isinstance(a, str)) if isinstance(actors, list) and len(actors) > 1 else actor_text

        # Build a compound sentence from all available fields
        parts = []

        # Use evidence as the primary source
        if evidence and len(evidence.split()) >= 4:
            clean_ev = evidence.strip().rstrip("., ")
            parts.append(clean_ev)
        elif action:
            if goal and goal not in action:
                parts.append(f"{actor_text} {goal.strip().rstrip('.')} için {action.strip().rstrip('.')}")
            else:
                parts.append(f"{actor_text} {action.strip().rstrip('.')}")
        elif goal:
            parts.append(f"{actor_text} {goal.strip().rstrip('.')} için harekete geçer")

        # Add obstacle/conflict context
        if obstacle and len(obstacle.split()) >= 3 and obstacle not in str(parts):
            parts.append(f"ancak {obstacle.strip().rstrip('.')}")

        # Add object
        if obj and obj not in str(parts):
            parts.append(f"{obj.strip()} ile ilgilenir")

        # Add consequence (skip if contains pipeline phrases)
        if consequence and len(consequence.split()) >= 3:
            if not _text_has_forbidden_phrase(consequence):
                clean_cons = consequence.strip().rstrip("., ")
                if not any(w in clean_cons.lower() for w in ["sonuç", "sonuc"]):
                    parts.append(f"sonucunda {clean_cons}")

        if parts:
            sentence = " ".join(parts) + "."
            sent_lower = sentence.lower()[:80]
            if sent_lower not in combined_lower and len(sentence.split()) >= 4:
                sentences.append(sentence)
                combined_lower += sent_lower

    # Combine
    combined = " ".join(sentences)
    words = combined.split()

    # Aggressive padding with raw evidence from nodes if still too short
    if len(words) < CONSERVATIVE_SUMMARY_MIN_WORDS:
        for node in event_graph:
            for key in ("kaynak_metin", "evidence", "kanit_metni", "evidence_sentence", "olay_metni"):
                ev = str(node.get(key) or "").strip()
                if ev and len(ev.split()) >= 4 and ev.lower()[:60] not in combined_lower:
                    clean_ev = ev.rstrip("., ")
                    sentences.append(clean_ev + ".")
                    combined = " ".join(sentences)
                    combined_lower += clean_ev.lower()[:60]
                    words = combined.split()
                    if len(words) >= CONSERVATIVE_SUMMARY_MIN_WORDS:
                        break
            if len(words) >= CONSERVATIVE_SUMMARY_MIN_WORDS:
                break

    # Second padding pass: use olay_basligi and neden/sonuc fields
    if len(words) < CONSERVATIVE_SUMMARY_MIN_WORDS:
        for node in event_graph:
            baslik = str(node.get("olay_basligi") or "").strip()
            neden = str(node.get("neden") or "").strip()
            sonuc = str(node.get("sonuc") or "").strip()
            for text in [baslik, neden, sonuc]:
                if text and len(text.split()) >= 4 and text.lower()[:60] not in combined_lower:
                    # Skip if contains pipeline phrases
                    if _text_has_forbidden_phrase(text):
                        continue
                    clean_text = text.rstrip("., ")
                    sentences.append(clean_text + ".")
                    combined = " ".join(sentences)
                    combined_lower += clean_text.lower()[:60]
                    words = combined.split()
                    if len(words) >= CONSERVATIVE_SUMMARY_MIN_WORDS:
                        break
            if len(words) >= CONSERVATIVE_SUMMARY_MIN_WORDS:
                break

    # Third pass: re-use evidence with different framing (sayfa bilgisi + evidence)
    if len(words) < CONSERVATIVE_SUMMARY_MIN_WORDS:
        for node in event_graph:
            sayfa = node.get("sayfa") or node.get("page") or ""
            for key in ("kaynak_metin", "evidence", "kanit_metni"):
                ev = str(node.get(key) or "").strip()
                if ev and len(ev.split()) >= 4:
                    # Frame with page info
                    framed = f"Sayfa {sayfa}'de: {ev.rstrip('., ')}" if sayfa else ev.rstrip("., ")
                    if framed.lower()[:60] not in combined_lower:
                        sentences.append(framed + ".")
                        combined = " ".join(sentences)
                        combined_lower += framed.lower()[:60]
                        words = combined.split()
                        if len(words) >= CONSERVATIVE_SUMMARY_MIN_WORDS:
                            break
            if len(words) >= CONSERVATIVE_SUMMARY_MIN_WORDS:
                break

    # Trim if over max
    if len(words) > CONSERVATIVE_SUMMARY_MAX_WORDS:
        combined = " ".join(words[:CONSERVATIVE_SUMMARY_MAX_WORDS])
        last_period = combined.rfind(".")
        if last_period > CONSERVATIVE_SUMMARY_MIN_WORDS:
            combined = combined[: last_period + 1]

    return combined.strip()


# ---------------------------------------------------------------------------
# 3. NATURAL SUMMARY — full narrative_realize output (rich, flowing)
# ---------------------------------------------------------------------------

NATURAL_SUMMARY_MIN_WORDS = 150


def _generate_natural_summary(
    title: str,
    event_graph: list[dict],
    characters: Iterable[dict],
) -> str:
    """Generate a rich, flowing natural summary using narrative_realizer."""
    summary = narrative_realize(
        baslik=title,
        event_graph=event_graph,
        karakterler=characters,
        min_kelime=NATURAL_SUMMARY_MIN_WORDS,
    )
    if not summary or summary == "olay örgüsü güvenilir biçimde çıkarılamadı":
        return ""
    # Quality check on the natural summary
    if _summary_has_forbidden_content(summary):
        return ""
    if _direct_quote_overlap_ratio(summary, event_graph) > 0.40:
        return ""
    return summary


# ---------------------------------------------------------------------------
# 4. MAIN PIPELINE ORCHESTRATOR
# ---------------------------------------------------------------------------

PIPELINE_VERSION = "v7-narrative-confidence-20260629"


def run_narrative_confidence_pipeline(
    event_graph: list[dict],
    characters: Iterable[dict],
    title: str = "",
    metadata: dict | None = None,
    existing_analysis: dict | None = None,
) -> dict:
    """
    Main pipeline orchestrator implementing the flow:

    Event Graph → Summary Confidence → Natural/Conservative Summary
    → Validator → Teacher Report → PDF

    Returns a dict with:
      - "pipeline_version": str
      - "confidence": float
      - "summary_type": str ("natural" | "conservative" | "unavailable")
      - "summary": str
      - "event_graph": list[dict]
      - "quality_gate": dict | None
      - "consistency_gate": dict | None
      - "teacher_report": dict | None
      - "pdf_bytes": io.BytesIO | None
      - "errors": list[str]
    """
    errors: list[str] = []
    result: dict = {
        "pipeline_version": PIPELINE_VERSION,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "confidence": 0.0,
        "summary_type": "unavailable",
        "summary": "",
        "event_graph": event_graph or [],
        "quality_gate": None,
        "consistency_gate": None,
        "teacher_report": None,
        "pdf_bytes": None,
        "errors": errors,
    }

    # Validate input
    if not event_graph or len(event_graph) < 3:
        errors.append("event_graph must have at least 3 nodes")
        return result

    char_list = list(sanitize_character_profiles(characters))
    if not char_list:
        errors.append("no valid characters provided")
        return result

    # Step 1: Calculate confidence
    confidence = _calculate_event_graph_confidence(event_graph, char_list)
    result["confidence"] = confidence
    result["metadata"] = dict(metadata or {})
    narrative_type_result = classify_narrative_type(
        " ".join(str(node.get("evidence") or node.get("kaynak_metin") or "") for node in event_graph if isinstance(node, dict)),
        {"kitap_adi": title or (metadata or {}).get("kitap_adi") or (metadata or {}).get("baslik")},
        str((metadata or {}).get("book_type") or ""),
        str((metadata or {}).get("book_subtype") or ""),
    )
    result["narrative_type"] = narrative_type_result.narrative_type
    result["narrative_type_confidence"] = narrative_type_result.confidence

    # Step 2: Branch to Natural or Conservative summary
    if confidence >= NATURAL_CONFIDENCE_THRESHOLD:
        # Try natural summary first
        summary = _generate_natural_summary(title, event_graph, char_list)
        if summary and len(summary.split()) >= 100:
            result["summary"] = summary
            result["summary_type"] = "natural"
        else:
            # Fallback to conservative if natural fails quality checks
            summary = _generate_conservative_summary(title, event_graph, char_list)
            if summary and len(summary.split()) >= CONSERVATIVE_SUMMARY_MIN_WORDS:
                result["summary"] = summary
                result["summary_type"] = "conservative"
                result["_natural_fallback_reason"] = (
                    "natural_summary_failed_quality_checks"
                )
            else:
                errors.append("both natural and conservative summary generation failed")
                return result
    else:
        # Conservative summary for low confidence
        summary = _generate_conservative_summary(title, event_graph, char_list)
        if summary and len(summary.split()) >= CONSERVATIVE_SUMMARY_MIN_WORDS:
            result["summary"] = summary
            result["summary_type"] = "conservative"
        else:
            errors.append("conservative summary generation failed")
            return result

    # Step 3: Build a minimal payload for validation
    payload = {
        "kitap_adi": title or (metadata or {}).get("kitap_adi") or "",
        "kitap_ozeti": result["summary"],
        "canonical_summary": result["summary"],
        "ozet_guven_skoru": confidence,
        "event_graph": event_graph,
        "ana_karakterler": char_list,
        "ozet_turu": "natural" if result["summary_type"] == "natural" else "conservative",
    }
    if metadata:
        payload.update(metadata)
    payload["narrative_type"] = narrative_type_result.narrative_type
    payload["narrative_type_confidence"] = narrative_type_result.confidence
    payload = attach_narrative_plan(payload)

    # Step 4: Synchronize summary surfaces
    payload = _synchronize_summary_surfaces(
        payload,
        result["summary"],
        f"narrative_confidence_pipeline:{result['summary_type']}",
    )

    # Step 5: Validator — Consistency Gate (kitap_tutarlilik_denetimi)
    consistency_audit = kitap_tutarlilik_denetimi(payload)
    strategy_decision = select_summary_strategy(
        payload,
        result["summary"],
        {"event_completeness": confidence},
        consistency_audit,
    )
    payload = apply_summary_strategy(payload, strategy_decision)
    result["summary_strategy"] = payload.get("summary_strategy")
    result["summary_confidence"] = payload.get("summary_confidence")
    result["entity_confidence"] = payload.get("entity_confidence")
    result["event_confidence"] = payload.get("event_confidence")
    result["theme_confidence"] = payload.get("theme_confidence")
    result["bridge_sentence_ratio"] = payload.get("bridge_sentence_ratio")
    result["quote_ratio"] = payload.get("quote_ratio")
    result["consistency_gate"] = {
        "gecerli": consistency_audit.get("gecerli", False),
        "durum": consistency_audit.get("durum", ""),
        "hatalar": consistency_audit.get("hatalar", []),
        "uyarilar": consistency_audit.get("uyarilar", []),
    }
    if not consistency_audit.get("gecerli", False):
        errors.append(
            f"consistency gate failed: {consistency_audit.get('hatalar', [])}"
        )
        return result

    # Step 6: Prepare theme report payload (includes quality gate)
    try:
        if existing_analysis and isinstance(existing_analysis, dict):
            # Use existing analysis as base, inject our summary
            prepared = prepare_theme_report_payload(existing_analysis)
            prepared["kitap_ozeti"] = result["summary"]
            prepared["canonical_summary"] = result["summary"]
            prepared["ozet_guven_skoru"] = confidence
        else:
            prepared = prepare_theme_report_payload(payload)
    except Exception as exc:
        errors.append(f"prepare_theme_report_payload failed: {exc}")
        return result

    # Step 7: Quality Gate (rapor_kalite_kapisi)
    try:
        quality_gate = rapor_kalite_kapisi(prepared)
        result["quality_gate"] = {
            "gecerli": quality_gate.get("gecerli", False),
            "durum": quality_gate.get("durum", ""),
            "hatalar": quality_gate.get("hatalar", []),
        }
        if not quality_gate.get("gecerli", False):
            errors.append(
                f"quality gate failed: {quality_gate.get('hatalar', [])}"
            )
            return result
    except Exception as exc:
        errors.append(f"rapor_kalite_kapisi failed: {exc}")
        return result

    # Step 8: Build teacher report payload
    try:
        teacher_payload = build_teacher_report_payload(prepared)
        result["teacher_report"] = teacher_payload
    except Exception as exc:
        errors.append(f"build_teacher_report_payload failed: {exc}")
        return result

    # Step 9: Generate PDF
    try:
        pdf_buffer = generate_teacher_report_pdf(
            teacher_payload if teacher_payload else prepared
        )
        result["pdf_bytes"] = pdf_buffer
    except Exception as exc:
        errors.append(f"generate_teacher_report_pdf failed: {exc}")

    return result


# ---------------------------------------------------------------------------
# 5. UTILITY — run from event graph dict
# ---------------------------------------------------------------------------


def pipeline_from_event_graph_dict(
    event_graph: list[dict],
    characters: list[dict],
    title: str = "",
    metadata: dict | None = None,
    existing_analysis: dict | None = None,
) -> dict:
    """
    Convenience wrapper: takes an event_graph dict (list of event nodes),
    character profiles, and optional pre-existing analysis,
    and runs the full narrative confidence pipeline.
    """
    return run_narrative_confidence_pipeline(
        event_graph=event_graph,
        characters=characters,
        title=title,
        metadata=metadata,
        existing_analysis=existing_analysis,
    )


# ---------------------------------------------------------------------------
# 6. SELF-TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("NARRATIVE CONFIDENCE PIPELINE — Self Test")
    print("=" * 60)

    # Test event graph (4 nodes — with richer fields for conservative padding)
    test_graph = [
        {
            "sayfa": 1,
            "olay_turu": "olay",
            "ilgili_karakterler": ["Ali"],
            "kaynak_metin": "Ali okula gitmek icin evden cikti.",
            "action": "evden cikmak",
            "actors": ["Ali"],
            "evidence": "Ali okula gitmek icin evden cikti.",
            "neden": "Başlangıç durumu karakteri harekete geçiren ilk koşulu oluşturur.",
            "sonuc": "Olay zincirinde bir sonraki adıma geçiş hazırlanır.",
        },
        {
            "sayfa": 2,
            "olay_turu": "karar",
            "ilgili_karakterler": ["Ali"],
            "kaynak_metin": "Ali arkadasina yardim etmeye karar verdi.",
            "action": "yardim etmek",
            "actors": ["Ali"],
            "evidence": "Ali arkadasina yardim etmeye karar verdi.",
            "neden": "Önceki olayda ortaya çıkan durum yeni bir karar adımını gerekli kılar.",
            "sonuc": "Karakterin seçimi sonraki olayların yönünü belirler.",
        },
        {
            "sayfa": 3,
            "olay_turu": "çatışma",
            "ilgili_karakterler": ["Ali", "Ayşe"],
            "kaynak_metin": "Ali ve Ayse arasinda bir anlasmazlik cikti.",
            "action": "anlasmazlik yasamak",
            "actors": ["Ali", "Ayşe"],
            "evidence": "Ali ve Ayse arasinda bir anlasmazlik cikti.",
            "neden": "Metindeki gerekçe karakterin durumu anlamaya veya seçim yapmaya yöneldiğini gösterir.",
            "sonuc": "Temel sorun görünür hale gelir ve gerilim artar.",
        },
        {
            "sayfa": 4,
            "olay_turu": "çözüm",
            "ilgili_karakterler": ["Ali", "Ayşe"],
            "kaynak_metin": "Ali ve Ayse konusarak sorunu cozduler.",
            "action": "sorunu cozmek",
            "actors": ["Ali", "Ayşe"],
            "evidence": "Ali ve Ayse konusarak sorunu cozduler.",
            "neden": "Önceki olayda ortaya çıkan durum yeni bir çözüm adımını gerekli kılar.",
            "sonuc": "Olay örgüsünde çözüm veya yeni anlayış yönünde ilerleme sağlanır.",
        },
    ]
    test_chars = [
        {"ad": "Ali", "ana_karakter_mi": True, "guven_skoru": 0.8},
        {"ad": "Ayşe", "ana_karakter_mi": False, "guven_skoru": 0.7},
    ]

    # Test with these characters
    confidence = _calculate_event_graph_confidence(
        test_graph, test_chars, "Ali okula gitti. Ali yardim etti. Ali ve Ayse anlasmazlik yasadi. Ali ve Ayse cozdu."
    )
    print(f"\nConfidence with 4 nodes: {confidence}")
    print(f"Threshold (>= 0.75): {'NATURAL' if confidence >= 0.75 else 'CONSERVATIVE'}")

    # Generate conservative summary
    cons = _generate_conservative_summary(
        "Test Kitap", test_graph, test_chars
    )
    print(f"\nConservative summary ({len(cons.split())} words):")
    print(f"  {cons[:300]}...")

    # Generate natural summary
    nat = _generate_natural_summary("Test Kitap", test_graph, test_chars)
    print(f"\nNatural summary ({len(nat.split()) if nat else 0} words):")
    print(f"  {nat[:300] if nat else 'EMPTY'}...")

    # Run full pipeline
    print("\n" + "=" * 60)
    print("Full Pipeline Run")
    print("=" * 60)
    pipeline_result = run_narrative_confidence_pipeline(
        event_graph=test_graph,
        characters=test_chars,
        title="Test Kitap",
    )
    print(f"  Pipeline version: {pipeline_result.get('pipeline_version')}")
    print(f"  Confidence: {pipeline_result.get('confidence')}")
    print(f"  Summary type: {pipeline_result.get('summary_type')}")
    print(f"  Summary length: {len(pipeline_result.get('summary', '').split())} words")
    print(f"  Errors: {pipeline_result.get('errors', [])}")
    cg = pipeline_result.get('consistency_gate') or {}
    print(f"  Consistency gate passed: {cg.get('gecerli')}")
    qg = pipeline_result.get('quality_gate') or {}
    print(f"  Quality gate passed: {qg.get('gecerli')}")
    print(f"  PDF generated: {pipeline_result.get('pdf_bytes') is not None}")
    print("\nDone.")
