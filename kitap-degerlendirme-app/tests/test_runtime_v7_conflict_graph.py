import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from runtime_v7.adapter import build_event_graph_from_payload
from runtime_v7.conflict_graph import build_conflict_graph
from runtime_v7.conflict_resolution import build_conflict_resolution
from runtime_v7.contracts import EventGraph, EventGraphEdge, EventGraphNode


def test_build_conflict_graph_generates_shadow_metrics():
    event_graph = EventGraph(
        nodes=[
            EventGraphNode(action="fight", actors=["hero", "villain"], conflict="clash"),
            EventGraphNode(action="escape", actors=["hero"], outcome="saved"),
        ],
        edges=[
            EventGraphEdge(source=0, target=1, relation="causal"),
        ],
    )
    narrative_chains = {
        "chains": [
            {"events": ["0:fight", "1:escape"], "length": 2, "confidence": 0.85}
        ],
        "chain_count": 1,
        "largest_chain_size": 2,
        "isolated_event_count": 0,
        "average_chain_length": 2.0,
        "chain_confidence": 0.85,
    }
    cause_effect = {
        "cause_effect_relations": [
            {"cause_event_id": "0:fight", "effect_event_id": "1:escape", "confidence": 0.8}
        ],
        "diagnostics": {"cause_effect_count": 1, "average_cause_effect_confidence": 0.8, "weak_causal_reason": "sufficient"},
    }

    result = build_conflict_graph(event_graph, narrative_chains, cause_effect)

    assert len(result["conflicts"]) == 1
    assert result["conflicts"][0]["conflict_type"] in {"direct_confrontation", "interpersonal_tension", "narrative_tension", "obstacle"}
    assert result["diagnostics"]["conflict_count"] == 1
    assert result["diagnostics"]["weak_conflict_reason"] == "sufficient"
    assert result["conflicts"][0]["participants"] == ["hero", "villain"]


def test_build_event_graph_from_payload_supports_conflict_graph_shape():
    payload = {
        "event_graph": [
            {"action": "fight", "actors": ["hero", "villain"], "conflict": "clash"},
            {"action": "escape", "actors": ["hero"], "outcome": "saved"},
        ]
    }

    event_graph = build_event_graph_from_payload(payload)
    result = build_conflict_graph(event_graph, {"chains": []}, {"cause_effect_relations": []})
    assert result["diagnostics"]["conflict_count"] >= 0


def test_build_conflict_resolution_returns_primary_conflict_and_resolution():
    event_graph = EventGraph(
        nodes=[
            EventGraphNode(action="fight", actors=["hero", "villain"], conflict="clash"),
            EventGraphNode(action="escape", actors=["hero"], outcome="saved"),
        ],
        edges=[
            EventGraphEdge(source=0, target=1, relation="causal"),
        ],
    )
    narrative_graph = {
        "conflict_links": [{"node": 0, "conflict": "clash"}],
        "resolution_links": [{"node": 1, "outcome": "saved"}],
    }
    story_arc = {"stages": {"resolution": "saved"}}
    conflict_graph = build_conflict_graph(event_graph, {
        "chains": [{"events": ["0:fight", "1:escape"], "length": 2, "confidence": 0.85}],
        "chain_confidence": 0.85,
        "chain_count": 1,
        "isolated_event_count": 0,
    }, {
        "cause_effect_relations": [{"cause_event_id": "0:fight", "effect_event_id": "1:escape", "confidence": 0.8}],
        "diagnostics": {"cause_effect_count": 1, "average_cause_effect_confidence": 0.8, "weak_causal_reason": "sufficient"},
    })

    resolution = build_conflict_resolution(event_graph, narrative_graph, story_arc, conflict_graph)

    assert resolution["primary_conflict"]["conflict_type"] in {"direct_confrontation", "interpersonal_tension", "narrative_tension", "obstacle", ""}
    assert resolution["primary_conflict"]["confidence"] >= 0.0
    assert resolution["resolution"]["resolution_text"] == "saved"
    assert resolution["diagnostics"]["primary_conflict_detected"] is True
    assert resolution["diagnostics"]["resolution_detected"] is True


def test_build_v7_shadow_payload_is_deterministic_for_same_payload():
    from runtime_v7.adapter import build_v7_shadow_payload

    payload = {
        "event_graph": [
            {"action": "fight", "actors": ["hero", "villain"], "conflict": "clash"},
            {"action": "escape", "actors": ["hero"], "outcome": "saved"},
        ],
        "ana_karakterler": [
            {"ad": "hero", "central_entity": True},
            {"ad": "villain"},
        ],
    }

    shadow1 = build_v7_shadow_payload(payload)
    shadow2 = build_v7_shadow_payload(payload)

    assert shadow1 == shadow2
    assert shadow1["quality_contract"]["checked_at"] == ""
