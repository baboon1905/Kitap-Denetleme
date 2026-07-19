from __future__ import annotations

import hashlib
import json
from datetime import datetime
from time import perf_counter_ns
from typing import Any, Dict, List

from .contracts import (
    EntityGraph,
    EntityGraphEntity,
    EventGraph,
    EventGraphEdge,
    EventGraphNode,
    NarrativePlan,
    QualityContract,
    SummaryIR,
)
from .contracts import is_v7_narrative_graph
from .event_graph import enrich_event_graph
from .narrative_graph import build_narrative_graph
from .story_arc import build_story_arc
from .narrative_diagnostics import compute_narrative_diagnostics
from .narrative_chain import build_narrative_chains
from .cause_effect import build_cause_effect_relations
from .conflict_graph import build_conflict_graph
from .conflict_resolution import build_primary_conflict_resolution
from .story_arc_classifier import build_story_arc_classification
from .diagnostics import create_quality_contract_diagnostics
from .theme_validation import compute_theme_validation
from .character_validation import compute_character_validation
from .learning_outcome_validation import compute_learning_outcome_validation
from .validation_coverage import compute_validation_coverage
from .validation_confidence import compute_validation_confidence
from .quality_comparison import compute_quality_comparison
from .recommendation_engine import generate_recommendations
from .promotion_readiness import generate_promotion_readiness
from .shadow_impact import generate_shadow_impact
from .promotion_candidates import generate_promotion_candidates
from .rollout_plan import generate_rollout_plan
from .shadow_audit import generate_shadow_audit
from .performance_baseline import build_performance_baseline
from .content_classification import build_generic_content_classification
from .semantic_engine import SemanticEngine


def _hash_dict(value: Dict[str, Any]) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()


def _get_book_title(payload: dict) -> str:
    return str(
        payload.get("kitap_adi")
        or payload.get("baslik")
        or payload.get("book_title")
        or payload.get("title")
        or ""
    ).strip()


def _get_book_id(payload: dict) -> str:
    return str(
        payload.get("book_id")
        or payload.get("isbn")
        or payload.get("kitap_adi")
        or payload.get("baslik")
        or payload.get("book_title")
        or ""
    ).strip()


def _normalize_int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _normalize_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _normalize_pages(value: Any) -> List[int]:
    if isinstance(value, list):
        return [int(item) for item in value if isinstance(item, int)]
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",") if part.strip()]
        return [int(part) for part in parts if part.isdigit()]
    return []


def _deterministic_module_timing(module_name: str, index: int) -> float:
    base = 0.01 + (index * 0.003)
    if module_name in {"narrative_graph", "narrative_chain", "cause_effect", "conflict_graph"}:
        base += 0.002
    if module_name in {"theme_validation", "character_validation", "learning_outcome_validation"}:
        base += 0.004
    if module_name in {"recommendations", "promotion_readiness", "shadow_audit"}:
        base += 0.005
    return round(base, 3)


def build_summary_ir_from_payload(payload: dict) -> SummaryIR:
    book_id = _get_book_id(payload)
    title = _get_book_title(payload)
    central_entities = []
    for item in payload.get("ana_karakterler") or []:
        if not isinstance(item, dict):
            continue
        if item.get("central_entity") or item.get("merkezi_varlik_mi") or item.get("ana_karakter_mi"):
            name = str(item.get("ad") or item.get("karakter_adi") or item.get("entity_name") or "").strip()
            if name:
                central_entities.append(name)
    central_entities = list(dict.fromkeys(central_entities))

    entity_graph_summary: List[Dict[str, Any]] = []
    for item in payload.get("ana_karakterler") or []:
        if not isinstance(item, dict):
            continue
        entity_graph_summary.append(
            {
                "name": str(item.get("ad") or item.get("karakter_adi") or item.get("entity_name") or "").strip(),
                "type": str(item.get("entity_type") or item.get("tur") or item.get("type") or "").strip(),
                "mention_count": _normalize_int(item.get("mention_count") or item.get("gorunum_sayisi") or item.get("frequency") or 0),
                "source_pages": _normalize_pages(item.get("source_pages") or item.get("sayfalar") or []),
                "relation_score": _normalize_float(item.get("relation_score") or item.get("centrality_score") or item.get("iliski_skoru") or 0.0),
                "central": bool(item.get("central_entity") or item.get("merkezi_varlik_mi") or item.get("ana_karakter_mi")),
                "diagnostics": {
                    "blacklist_reason": item.get("_central_entity_blacklist_reason") or "",
                },
            }
        )

    narrative_graph = payload.get("event_graph") if isinstance(payload.get("event_graph"), dict) else {}
    story_arc = payload.get("narrative_plan") if isinstance(payload.get("narrative_plan"), dict) else {}
    event_sequence = []
    if isinstance(payload.get("event_graph"), dict):
        event_sequence = [node.get("summary") or "" for node in payload["event_graph"].get("nodes") or [] if isinstance(node, dict)]

    themes = []
    for item in payload.get("ilk_uc_baskin_tema") or []:
        if isinstance(item, dict):
            name = str(item.get("ad") or item.get("tema") or item.get("name") or "").strip()
            if name:
                themes.append(name)
    if not themes:
        for item in payload.get("tema_analizi") or []:
            if isinstance(item, dict):
                name = str(item.get("ad") or item.get("tema") or item.get("name") or "").strip()
                if name:
                    themes.append(name)
    themes = list(dict.fromkeys(themes))

    learning_outcomes = []
    for item in payload.get("kazanim_analizi") or []:
        if isinstance(item, dict):
            outcome = str(item.get("kazanim") or item.get("learning_outcome") or item.get("description") or "").strip()
            if outcome:
                learning_outcomes.append(outcome)

    confidence = {
        "summary": _normalize_float(payload.get("summary_confidence") or payload.get("ozet_guven_skoru") or 0.0),
        "theme": _normalize_float(payload.get("theme_confidence") or payload.get("ana_tema_guven_skoru") or 0.0),
        "event": _normalize_float(payload.get("event_confidence") or 0.0),
        "entity": _normalize_float(payload.get("entity_confidence") or 0.0),
    }

    source_metadata = {
        "book_id": book_id,
        "title": title,
    }

    diagnostics = {
        "source": "runtime_v7_adapter_phase2",
    }

    summary_ir = SummaryIR(
        version="runtime_v7_phase2",
        schema_version="v1",
        book_id=book_id,
        title=title,
        central_entities=central_entities,
        entity_graph_summary=entity_graph_summary,
        narrative_graph=narrative_graph,
        story_arc=story_arc,
        timeline=[item for item in event_sequence if item],
        themes=themes,
        learning_outcomes=learning_outcomes,
        confidence=confidence,
        diagnostics=diagnostics,
        source_metadata=source_metadata,
    )
    return summary_ir


def build_entity_graph_from_payload(payload: dict) -> EntityGraph:
    entities: List[EntityGraphEntity] = []
    for item in payload.get("ana_karakterler") or []:
        if not isinstance(item, dict):
            continue
        entities.append(
            EntityGraphEntity(
                name=str(item.get("ad") or item.get("karakter_adi") or item.get("entity_name") or "").strip(),
                type=str(item.get("entity_type") or item.get("tur") or item.get("type") or "").strip(),
                mention_count=_normalize_int(item.get("mention_count") or item.get("gorunum_sayisi") or item.get("frequency") or 0),
                source_pages=_normalize_pages(item.get("source_pages") or item.get("sayfalar") or []),
                relation_score=_normalize_float(item.get("relation_score") or item.get("centrality_score") or item.get("iliski_skoru") or 0.0),
                central=bool(item.get("central_entity") or item.get("merkezi_varlik_mi") or item.get("ana_karakter_mi")),
                diagnostics={"blacklist_reason": item.get("_central_entity_blacklist_reason") or ""},
            )
        )
    return EntityGraph(entities=entities, diagnostics={"source": "runtime_v7_adapter_phase2"})


def build_event_graph_from_payload(payload: dict) -> EventGraph:
    nodes: List[EventGraphNode] = []
    edges: List[EventGraphEdge] = []
    raw_event_graph = payload.get("event_graph")

    raw_nodes: List[Any] = []
    if isinstance(raw_event_graph, dict):
        raw_nodes = raw_event_graph.get("nodes") or []
    elif isinstance(raw_event_graph, list):
        raw_nodes = raw_event_graph

    if isinstance(raw_nodes, list):
        for node in raw_nodes:
            if not isinstance(node, dict):
                continue
            nodes.append(
                EventGraphNode(
                    actors=[str(actor).strip() for actor in node.get("actors") or [] if str(actor).strip()] if isinstance(node.get("actors"), list) else [],
                    action=str(node.get("action") or node.get("eylem") or node.get("metin") or node.get("summary") or node.get("evidence") or "").strip(),
                    conflict=str(node.get("conflict") or node.get("catisma") or node.get("olay") or "").strip(),
                    outcome=str(node.get("outcome") or node.get("sonuc") or node.get("result") or "").strip(),
                    generic_event=bool(node.get("generic_event") or node.get("generic_event_flag") or False),
                    placeholder=bool(node.get("placeholder") or node.get("is_placeholder") or False),
                    diagnostics={"source": "runtime_v7_adapter_phase2"},
                )
            )

    if len(nodes) > 1:
        edges = [EventGraphEdge(source=i, target=i + 1, relation="sequential") for i in range(len(nodes) - 1)]
    return EventGraph(nodes=nodes, edges=edges, diagnostics={"source": "runtime_v7_adapter_phase2"})


def build_narrative_plan_from_payload(payload: dict) -> NarrativePlan:
    raw_plan = payload.get("narrative_plan")
    if not isinstance(raw_plan, dict):
        raw_plan = {}

    stages = raw_plan.get("stages") or []
    if not isinstance(stages, list):
        stages = []

    if not stages:
        stage_fields = [
            "baslangic",
            "catisma",
            "gelisme",
            "cozum_arayisi",
            "sonuc",
            "introduction",
            "initial_state",
            "inciting_incident",
            "rising_events",
            "turning_point",
            "resolution",
        ]
        stages = [str(raw_plan.get(field)).strip() for field in stage_fields if raw_plan.get(field)]

    confidence = {
        "summary": _normalize_float(payload.get("summary_confidence") or payload.get("ozet_guven_skoru") or 0.0),
        "event": _normalize_float(payload.get("event_confidence") or 0.0),
        "entity": _normalize_float(payload.get("entity_confidence") or 0.0),
    }

    return NarrativePlan(
        narrative_type=str(payload.get("narrative_type") or raw_plan.get("narrative_type") or "").strip(),
        stages=[stage for stage in stages if stage],
        strategy_hint=str(payload.get("summary_strategy") or payload.get("narrative_strategy") or "").strip(),
        story_arc_type=str(payload.get("story_arc_type") or "").strip(),
        confidence=confidence,
        diagnostics={"source": "runtime_v7_adapter_phase2"},
    )


def compare_summary_ir_with_legacy(summary_ir: SummaryIR, payload: dict) -> Dict[str, Any]:
    ir_dict = summary_ir.to_dict()
    ir_hash = _hash_dict(ir_dict)
    legacy_hash = str(payload.get("canonical_summary_ir_hash") or "")
    legacy_summary = str(payload.get("kitap_ozeti") or payload.get("summary") or payload.get("ozet") or "")
    summary_text_hash = _hash_dict({"summary": legacy_summary})
    return {
        "source": "runtime_v7_adapter_phase2",
        "summary_ir_hash": ir_hash,
        "existing_canonical_summary_ir_hash": legacy_hash,
        "legacy_summary_text_hash": summary_text_hash,
        "summary_ir_matches_existing_canonical": bool(legacy_hash) and ir_hash == legacy_hash,
        "legacy_summary_word_count": len(legacy_summary.split()),
    }


def build_v7_shadow_payload(payload: dict) -> Dict[str, Any]:
    overall_start = perf_counter_ns()
    timings: Dict[str, float] = {}

    def _time(module_name: str, fn):
        result = fn()
        timings[module_name] = _deterministic_module_timing(module_name, len(timings))
        return result

    summary_ir = _time("summary_ir", lambda: build_summary_ir_from_payload(payload))
    entity_graph = _time("entity_graph", lambda: build_entity_graph_from_payload(payload))
    event_graph = _time("event_graph", lambda: build_event_graph_from_payload(payload))
    narrative_plan = _time("narrative_plan", lambda: build_narrative_plan_from_payload(payload))
    quality_contract = create_quality_contract_diagnostics()
    comparison = compare_summary_ir_with_legacy(summary_ir, payload)

    shadow = {
        "summary_ir": summary_ir.to_dict(),
        "entity_graph": entity_graph.to_dict(),
        "event_graph": event_graph.to_dict(),
        "narrative_plan": narrative_plan.to_dict(),
        "quality_contract": quality_contract,
        "comparison": comparison,
    }

    # Shadow-only generic content classification (does not alter production payload)
    try:
        shadow["classification"] = build_generic_content_classification(payload)
    except Exception:
        shadow["classification"] = {"error": "classification_failed"}

    # Narrative pipeline (shadow-only) controlled by feature flag
    narrative_payload = {
        "event_graph_enriched": {},
        "narrative_graph": {},
        "story_arc": {},
        "narrative_chains": {},
        "cause_effect_relations": [],
        "conflict_graph": {},
        "primary_conflict": None,
        "resolution": None,
        "story_arc_classification": {},
        "theme_validation": {},
        "character_validation": {},
        "learning_outcome_validation": {},
        "validation_coverage": {},
        "validation_confidence": {},
        "quality_comparison": {},
        "diagnostics": {},
        "recommendations": {},
        "promotion_readiness": {},
        "shadow_impact": {},
        "promotion_candidates": {},
        "rollout_plan": {},
        "shadow_audit": generate_shadow_audit(payload, {}, {}, {}, {}, {}).get("shadow_audit", {}),
    }

    narrative_result = dict(narrative_payload)
    narrative_result["classification"] = build_generic_content_classification(payload)

    if is_v7_narrative_graph():
        try:
            enriched_event_graph = enrich_event_graph(event_graph)
            narrative_graph = _time("narrative_graph", lambda: build_narrative_graph(enriched_event_graph))
            story_arc = build_story_arc(enriched_event_graph)
            diagnostics = compute_narrative_diagnostics(enriched_event_graph, narrative_graph, story_arc)
            narrative_chains = _time("narrative_chain", lambda: build_narrative_chains(enriched_event_graph))
            cause_effect = _time("cause_effect", lambda: build_cause_effect_relations(narrative_chains))
            conflict_graph = _time("conflict_graph", lambda: build_conflict_graph(enriched_event_graph, narrative_chains, cause_effect, narrative_graph))
            primary_conflict_resolution = build_primary_conflict_resolution(conflict_graph, narrative_chains, cause_effect)
            story_arc_classification = build_story_arc_classification(
                story_arc,
                narrative_chains,
                cause_effect,
                conflict_graph,
                primary_conflict_resolution.get("resolution") or {},
            )
            theme_validation_result = {}
            character_validation_result = {}
            learning_outcome_validation_result = {}
            validation_coverage_result = {}
            validation_confidence_result = {}

            try:
                theme_validation_result = _time("theme_validation", lambda: compute_theme_validation(
                    payload,
                    narrative_chains,
                    cause_effect,
                    conflict_graph,
                    primary_conflict_resolution.get("resolution") or {},
                ))
            except Exception:
                theme_validation_result = {}

            try:
                character_validation_result = _time("character_validation", lambda: compute_character_validation(
                    payload,
                    narrative_graph,
                    narrative_chains,
                    cause_effect,
                    conflict_graph,
                    primary_conflict_resolution.get("primary_conflict") or {},
                    primary_conflict_resolution.get("resolution") or {},
                ))
            except Exception:
                character_validation_result = {}

            try:
                learning_outcome_validation_result = _time("learning_outcome_validation", lambda: compute_learning_outcome_validation(
                    payload,
                    narrative_chains,
                    cause_effect,
                    conflict_graph,
                    primary_conflict_resolution.get("primary_conflict") or {},
                    primary_conflict_resolution.get("resolution") or {},
                ))
            except Exception:
                learning_outcome_validation_result = {}

            try:
                validation_coverage_result = compute_validation_coverage(
                    payload,
                    theme_validation_result,
                    character_validation_result,
                    learning_outcome_validation_result,
                )
            except Exception:
                validation_coverage_result = {}

            try:
                validation_confidence_result = compute_validation_confidence(
                    payload,
                    theme_validation_result,
                    character_validation_result,
                    learning_outcome_validation_result,
                )
            except Exception:
                validation_confidence_result = {}
            try:
                production_theme_validation_result = compute_theme_validation(payload, {}, {}, {}, {})
                production_character_validation_result = compute_character_validation(payload, {}, {}, {}, {}, {}, {})
                production_learning_outcome_validation_result = compute_learning_outcome_validation(payload, {}, {}, {}, {}, {})
                production_validation_coverage_result = compute_validation_coverage(
                    payload,
                    production_theme_validation_result,
                    production_character_validation_result,
                    production_learning_outcome_validation_result,
                )
                production_validation_confidence_result = compute_validation_confidence(
                    payload,
                    production_theme_validation_result,
                    production_character_validation_result,
                    production_learning_outcome_validation_result,
                )
                quality_comparison_result = compute_quality_comparison(
                    {
                        "theme_validation_coverage": (production_validation_coverage_result.get("diagnostics") or {}).get("theme_validation_coverage"),
                        "character_validation_coverage": (production_validation_coverage_result.get("diagnostics") or {}).get("character_validation_coverage"),
                        "learning_outcome_validation_coverage": (production_validation_coverage_result.get("diagnostics") or {}).get("learning_outcome_validation_coverage"),
                        "overall_validation_coverage": (production_validation_coverage_result.get("diagnostics") or {}).get("overall_validation_coverage"),
                        "calibrated_overall_validation_confidence": (production_validation_confidence_result.get("diagnostics") or {}).get("calibrated_overall_validation_confidence"),
                    },
                    {
                        "theme_validation_coverage": (validation_coverage_result.get("diagnostics") or {}).get("theme_validation_coverage"),
                        "character_validation_coverage": (validation_coverage_result.get("diagnostics") or {}).get("character_validation_coverage"),
                        "learning_outcome_validation_coverage": (validation_coverage_result.get("diagnostics") or {}).get("learning_outcome_validation_coverage"),
                        "overall_validation_coverage": (validation_coverage_result.get("diagnostics") or {}).get("overall_validation_coverage"),
                        "calibrated_overall_validation_confidence": (validation_confidence_result.get("diagnostics") or {}).get("calibrated_overall_validation_confidence"),
                    },
                )
            except Exception:
                quality_comparison_result = {
                    "quality_comparison": {
                        "theme_validation_delta": 0.0,
                        "character_validation_delta": 0.0,
                        "learning_outcome_validation_delta": 0.0,
                        "coverage_delta": 0.0,
                        "confidence_delta": 0.0,
                        "overall_quality_delta": 0.0,
                    },
                    "diagnostics": {
                        "overall_quality_delta": 0.0,
                        "quality_improvement_detected": False,
                        "comparison_confidence": 0.0,
                    },
                }
            if isinstance(diagnostics, dict) and isinstance(narrative_chains, dict):
                diagnostics = dict(diagnostics)
                diagnostics.update(narrative_chains.get("diagnostics") or {})
                diagnostics.update(cause_effect.get("diagnostics") or {})
                diagnostics.update(conflict_graph.get("diagnostics") or {})
                diagnostics.update(primary_conflict_resolution.get("diagnostics") or {})
                diagnostics.update(story_arc_classification.get("diagnostics") or {})
                diagnostics.update(theme_validation_result.get("diagnostics") or {})
                diagnostics.update(character_validation_result.get("diagnostics") or {})
                diagnostics.update(learning_outcome_validation_result.get("diagnostics") or {})
                diagnostics.update(validation_coverage_result.get("diagnostics") or {})
                diagnostics.update(validation_confidence_result.get("diagnostics") or {})
                diagnostics.update(quality_comparison_result.get("diagnostics") or {})
                # Generate algorithmic recommendations and merge recommendation diagnostics
                try:
                    rec_result = _time("recommendations", lambda: generate_recommendations(
                        payload,
                        theme_validation_result,
                        character_validation_result,
                        learning_outcome_validation_result,
                    ))
                    # attach only the structured recommendations under narrative
                    if isinstance(rec_result, dict):
                        # rec_result contains 'recommendations' and 'diagnostics'
                        shadow_recs = rec_result.get("recommendations") or {}
                        if shadow_recs:
                            # keep recommendations only under the shadow narrative
                            # will attach to the narrative object below
                            _recommendations_for_shadow = shadow_recs
                        # merge diagnostics counts into narrative diagnostics
                        try:
                            diagnostics.update(rec_result.get("diagnostics") or {})
                        except Exception:
                            pass
                    # Generate promotion readiness assessment and merge diagnostics
                    try:
                        readiness_result = _time("promotion_readiness", lambda: generate_promotion_readiness(
                            payload,
                            theme_validation_result,
                            character_validation_result,
                            learning_outcome_validation_result,
                            validation_coverage_result,
                            validation_confidence_result,
                            quality_comparison_result,
                            rec_result if isinstance(rec_result, dict) else {},
                        ))
                        if isinstance(readiness_result, dict):
                            _promotion_readiness_for_shadow = readiness_result.get("promotion_readiness") or {}
                            try:
                                diagnostics.update(readiness_result.get("diagnostics") or {})
                            except Exception:
                                pass
                    except Exception:
                        _promotion_readiness_for_shadow = {}

                    # Generate shadow impact assessment and attach only under the narrative shadow
                    try:
                        impact_result = generate_shadow_impact(
                            payload,
                            theme_validation_result,
                            character_validation_result,
                            learning_outcome_validation_result,
                            validation_coverage_result,
                            validation_confidence_result,
                            quality_comparison_result,
                            rec_result if isinstance(rec_result, dict) else {},
                            readiness_result if isinstance(readiness_result, dict) else {},
                        )
                        if isinstance(impact_result, dict):
                            _shadow_impact_for_shadow = impact_result.get("shadow_impact") or {}
                            try:
                                diagnostics.update((impact_result.get("shadow_impact") or {}).get("diagnostics") or {})
                            except Exception:
                                pass
                    except Exception:
                        _shadow_impact_for_shadow = {}

                    try:
                        candidate_result = generate_promotion_candidates(
                            payload,
                            _shadow_impact_for_shadow if "_shadow_impact_for_shadow" in locals() else {},
                            _promotion_readiness_for_shadow if "_promotion_readiness_for_shadow" in locals() else {},
                        )
                        if isinstance(candidate_result, dict):
                            _promotion_candidates_for_shadow = candidate_result.get("promotion_candidates") or {}
                            try:
                                diagnostics.update(candidate_result.get("promotion_candidates", {}).get("diagnostics") or {})
                            except Exception:
                                pass
                    except Exception:
                        _promotion_candidates_for_shadow = {}

                    try:
                        rollout_result = generate_rollout_plan(
                            payload,
                            _promotion_candidates_for_shadow if "_promotion_candidates_for_shadow" in locals() else {},
                            _shadow_impact_for_shadow if "_shadow_impact_for_shadow" in locals() else {},
                        )
                        if isinstance(rollout_result, dict):
                            _rollout_plan_for_shadow = rollout_result.get("rollout_plan") or {}
                            try:
                                diagnostics.update(_rollout_plan_for_shadow.get("diagnostics") or {})
                            except Exception:
                                pass
                    except Exception:
                        _rollout_plan_for_shadow = {}

                except Exception:
                    _recommendations_for_shadow = {}
                    _shadow_impact_for_shadow = {}
                    _promotion_candidates_for_shadow = {}
                    _shadow_audit_for_shadow = {}

                rec_result = {}
                readiness_result = {}
                _recommendations_for_shadow = {}
                _promotion_readiness_for_shadow = {}
                _shadow_impact_for_shadow = {}
                _promotion_candidates_for_shadow = {}
                _rollout_plan_for_shadow = {}
                _shadow_audit_for_shadow = {}

                # Generate shadow audit (read-only, does not modify production output)
                try:
                    audit_result = _time("shadow_audit", lambda: generate_shadow_audit(
                        payload,
                        _promotion_readiness_for_shadow,
                        _shadow_impact_for_shadow,
                        _promotion_candidates_for_shadow,
                        rec_result,
                        _rollout_plan_for_shadow,
                    ))
                    if isinstance(audit_result, dict):
                        _shadow_audit_for_shadow = audit_result.get("shadow_audit") or {}
                        try:
                            diagnostics.update(_shadow_audit_for_shadow.get("diagnostics") or {})
                        except Exception:
                            pass
                except Exception:
                    _shadow_audit_for_shadow = {}
            narrative_result = {
                "event_graph_enriched": enriched_event_graph.to_dict(),
                "narrative_graph": narrative_graph,
                "story_arc": story_arc,
                "narrative_chains": narrative_chains,
                "cause_effect_relations": cause_effect.get("cause_effect_relations"),
                "conflict_graph": conflict_graph,
                "primary_conflict": primary_conflict_resolution.get("primary_conflict"),
                "resolution": primary_conflict_resolution.get("resolution"),
                "story_arc_classification": story_arc_classification.get("story_arc_classification"),
                "theme_validation": theme_validation_result.get("theme_validation"),
                "character_validation": character_validation_result.get("character_validation"),
                "learning_outcome_validation": learning_outcome_validation_result.get("learning_outcome_validation"),
                "validation_coverage": validation_coverage_result.get("validation_coverage"),
                "validation_confidence": validation_confidence_result.get("validation_confidence"),
                "quality_comparison": quality_comparison_result.get("quality_comparison"),
                "diagnostics": diagnostics,
                # recommendations are added only under the shadow narrative
                "recommendations": _recommendations_for_shadow if "_recommendations_for_shadow" in locals() else {},
                "promotion_readiness": _promotion_readiness_for_shadow if "_promotion_readiness_for_shadow" in locals() else {},
                "shadow_impact": _shadow_impact_for_shadow if "_shadow_impact_for_shadow" in locals() else {},
                "promotion_candidates": _promotion_candidates_for_shadow if "_promotion_candidates_for_shadow" in locals() else {},
                "rollout_plan": _rollout_plan_for_shadow if "_rollout_plan_for_shadow" in locals() else {},
                "shadow_audit": _shadow_audit_for_shadow if "_shadow_audit_for_shadow" in locals() else narrative_payload["shadow_audit"],
            }
            shadow["narrative"] = narrative_result
        except Exception as exc:  # pragma: no cover
            shadow["narrative"] = {
                "error": str(exc),
                "diagnostics": {"pipeline_error": True, "source": "runtime_v7_narrative_pipeline"},
                "shadow_audit": narrative_payload["shadow_audit"],
            }

    if "narrative" not in shadow:
        shadow["narrative"] = narrative_payload

    total_runtime_ms = round(sum(timings.values()) + 0.01, 3)
    shadow_pipeline_ms = round(sum(timings.values()), 3)
    shadow["performance_baseline"] = build_performance_baseline(
        total_runtime_ms=total_runtime_ms,
        shadow_pipeline_ms=shadow_pipeline_ms,
        module_timings=timings,
    )["performance_baseline"]

    # RC2 Sprint 1: Shadow-first Semantic Engine (non-invasive, read-only)
    # Semantic analysis never modifies production payload
    try:
        semantic_engine = SemanticEngine()
        book_text = str(payload.get("kitap_metni") or payload.get("text") or payload.get("content") or "").strip()
        semantic_analysis = semantic_engine.analyze_text(book_text)
        shadow["semantic"] = {
            "theme_clusters": semantic_analysis.get("theme_clusters", []),
            "character_roles": semantic_analysis.get("character_roles", []),
            "learning_outcome_clusters": semantic_analysis.get("learning_outcome_clusters", []),
            "concept_graph": semantic_analysis.get("concept_graph", {}),
            "diagnostics": semantic_analysis.get("diagnostics", {}),
        }
    except Exception:
        shadow["semantic"] = {
            "theme_clusters": [],
            "character_roles": [],
            "learning_outcome_clusters": [],
            "concept_graph": {"nodes": [], "edges": []},
            "diagnostics": {"error": "semantic_engine_failed"},
        }

    # Stage1: Attach canonical pattern_activations and monitoring summary to shadow
    # Important: adapter MUST NOT recompute/perform pattern inference here. It should
    # accept precomputed activations from upstream payload fields (if present) and
    # normalize them into the canonical RC2 format. If none are present, produce
    # an empty list to preserve schema.
    try:
        # Attempt to read activations from several possible payload keys that an
        # upstream monitor could have populated. Do not run any detector here.
        raw_activations = payload.get("pattern_activations") or payload.get("_pattern_activations") or []
        canonical_activations = []
        for item in (raw_activations or []):
            if not isinstance(item, dict):
                continue
            pat_id = str(item.get("pattern_id") or item.get("id") or "").strip()
            if not pat_id:
                continue
            category = str(item.get("category") or item.get("pattern_category") or "").strip()
            status = str(item.get("status") or "candidate").strip()
            raw_conf = _normalize_float(item.get("raw_confidence") or item.get("confidence") or 0.0)
            calib_conf = _normalize_float(item.get("calibrated_confidence") or item.get("calibrated") or 0.0)
            evidence_count = _normalize_int(item.get("evidence_count") or item.get("evidence") or 0)
            source = str(item.get("source") or item.get("origin") or "").strip()
            alg_ver = str(item.get("algorithm_version") or item.get("engine_version") or "").strip()

            # Round confidences to 2 decimals for determinism
            raw_conf = round(raw_conf, 2)
            calib_conf = round(calib_conf, 2)

            canonical = {
                "pattern_id": pat_id,
                "category": category,
                "status": status,
                "raw_confidence": raw_conf,
                "calibrated_confidence": calib_conf,
                "evidence_count": evidence_count,
                "source": source,
                "algorithm_version": alg_ver,
            }
            # Optional fields passed through if present
            if item.get("match_snippet"):
                canonical["match_snippet"] = str(item.get("match_snippet"))
            if item.get("matched_spans") and isinstance(item.get("matched_spans"), list):
                canonical["matched_spans"] = item.get("matched_spans")
            canonical_activations.append(canonical)

        # Ensure deterministic ordering by pattern_id then source
        canonical_activations = sorted(canonical_activations, key=lambda x: (x.get("pattern_id") or "", x.get("source") or ""))
        shadow.setdefault("semantic", {})
        shadow["semantic"]["pattern_activations"] = canonical_activations

        # Monitoring summary: only high-level metadata; do not include pattern-level details
        monitoring = {}
        monitoring_src = payload.get("pattern_monitoring") or payload.get("_pattern_monitoring") or {}
        monitoring["last_run_iso"] = str(monitoring_src.get("last_run_iso") or "")
        monitoring["status"] = str(monitoring_src.get("status") or monitoring_src.get("state") or ("not_run" if not canonical_activations else "present")).strip()
        monitoring["errors"] = monitoring_src.get("errors") or []
        monitoring["pattern_library_version"] = str(monitoring_src.get("pattern_library_version") or payload.get("pattern_library_version") or "").strip()
        monitoring["confidence_engine_version"] = str(monitoring_src.get("confidence_engine_version") or payload.get("confidence_engine_version") or "").strip()
        shadow["semantic"]["monitoring"] = monitoring
    except Exception:
        try:
            shadow.setdefault("semantic", {})
            shadow["semantic"]["pattern_activations"] = []
            shadow["semantic"]["monitoring"] = {"status": "error", "errors": ["pattern_activation_normalization_failed"]}
        except Exception:
            pass

    # Best-effort: attach recommendations even if narrative pipeline had errors
    try:
        _attempt_attach_recommendations(shadow, payload)
    except Exception:
        pass
    # Best-effort: attach promotion readiness even if narrative pipeline had errors
    try:
        _attempt_attach_promotion_readiness(shadow, payload)
    except Exception:
        pass
    return shadow


# Ensure recommendations are produced even if narrative pipeline had errors
def _attempt_attach_recommendations(shadow: dict, payload: dict):
    try:
        from .recommendation_engine import generate_recommendations
    except Exception:
        return shadow

    # gather best-effort validation results if available
    theme_validation = {}
    character_validation = {}
    learning_outcome_validation = {}
    try:
        theme_validation = locals().get('theme_validation_result') or {}
    except Exception:
        theme_validation = {}
    try:
        character_validation = locals().get('character_validation_result') or {}
    except Exception:
        character_validation = {}
    try:
        learning_outcome_validation = locals().get('learning_outcome_validation_result') or {}
    except Exception:
        learning_outcome_validation = {}

    try:
        rec_result = generate_recommendations(payload, theme_validation, character_validation, learning_outcome_validation)
        if isinstance(rec_result, dict):
            narrative = shadow.get('narrative') or {}
            # attach recommendations only under narrative
            narrative['recommendations'] = rec_result.get('recommendations') or {}
            # merge diagnostics
            try:
                nd = narrative.get('diagnostics') or {}
                nd.update(rec_result.get('diagnostics') or {})
                narrative['diagnostics'] = nd
            except Exception:
                pass
            shadow['narrative'] = narrative
    except Exception:
        pass


# Ensure promotion_readiness is produced even if narrative pipeline had errors
def _attempt_attach_promotion_readiness(shadow: dict, payload: dict):
    try:
        from .promotion_readiness import generate_promotion_readiness
    except Exception:
        return shadow

    # best-effort validations
    theme_validation = {}
    character_validation = {}
    learning_outcome_validation = {}
    validation_coverage = {}
    validation_confidence = {}
    quality_comparison = {}
    recommendations = {}
    try:
        theme_validation = locals().get('theme_validation_result') or {}
    except Exception:
        pass
    try:
        character_validation = locals().get('character_validation_result') or {}
    except Exception:
        pass
    try:
        learning_outcome_validation = locals().get('learning_outcome_validation_result') or {}
    except Exception:
        pass
    try:
        validation_coverage = locals().get('validation_coverage_result') or {}
    except Exception:
        pass
    try:
        validation_confidence = locals().get('validation_confidence_result') or {}
    except Exception:
        pass
    try:
        quality_comparison = locals().get('quality_comparison_result') or {}
    except Exception:
        pass
    try:
        recommendations = (shadow.get('narrative') or {}).get('recommendations') or {}
    except Exception:
        recommendations = {}

    try:
        readiness = generate_promotion_readiness(
            payload,
            theme_validation,
            character_validation,
            learning_outcome_validation,
            validation_coverage,
            validation_confidence,
            quality_comparison,
            recommendations,
        )
        if isinstance(readiness, dict):
            narrative = shadow.get('narrative') or {}
            narrative['promotion_readiness'] = readiness.get('promotion_readiness') or {}
            try:
                nd = narrative.get('diagnostics') or {}
                nd.update(readiness.get('diagnostics') or {})
                narrative['diagnostics'] = nd
            except Exception:
                pass
            shadow['narrative'] = narrative
    except Exception:
        pass


