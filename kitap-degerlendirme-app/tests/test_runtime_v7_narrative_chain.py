import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from runtime_v7.adapter import build_event_graph_from_payload
from runtime_v7.contracts import EventGraph, EventGraphEdge, EventGraphNode
from runtime_v7.narrative_chain import build_narrative_chains


def test_build_narrative_chains_is_deterministic_and_reports_metrics():
    event_graph = EventGraph(
        nodes=[
            EventGraphNode(action="A", actors=["x"], conflict="c1"),
            EventGraphNode(action="B", actors=["x"]),
            EventGraphNode(action="C", actors=["y"]),
            EventGraphNode(action="D", actors=["y"], outcome="done"),
        ],
        edges=[
            EventGraphEdge(source=0, target=1, relation="sequential"),
            EventGraphEdge(source=1, target=2, relation="sequential"),
            EventGraphEdge(source=2, target=3, relation="sequential"),
        ],
    )

    result = build_narrative_chains(event_graph)

    assert result["chain_count"] == 1
    assert result["largest_chain_size"] == 4
    assert result["isolated_event_count"] == 0
    assert result["average_chain_length"] == 4.0
    assert result["chain_confidence"] >= 0.0
    assert len(result["chains"]) == 1
    assert result["chains"][0]["events"][0].startswith("0")
    assert result["chains"][0]["events"][-1].startswith("3")


def test_build_event_graph_from_payload_supports_list_shape():
    payload = {
        "event_graph": [
            {"action": "A", "actors": ["x"], "conflict": "c1"},
            {"action": "B", "actors": ["x"]},
            {"action": "C", "actors": ["y"], "outcome": "done"},
        ]
    }

    event_graph = build_event_graph_from_payload(payload)

    assert len(event_graph.nodes) == 3
    assert len(event_graph.edges) == 2

    result = build_narrative_chains(event_graph)
    assert result["chain_count"] == 1
    assert result["largest_chain_size"] == 3
