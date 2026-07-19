from __future__ import annotations

from typing import Any, Dict, List, Literal, TypedDict

StatusLiteral = Literal["PASS", "WARNING", "FAIL"]

class EntityGraphEntity(TypedDict, total=False):
    name: str
    type: str
    mention_count: int
    source_pages: List[int]
    relation_score: float
    central: bool
    diagnostics: Dict[str, Any]

class EntityGraph(TypedDict, total=False):
    entities: List[EntityGraphEntity]
    diagnostics: Dict[str, Any]

class EventGraphNode(TypedDict, total=False):
    actors: List[str]
    action: str
    conflict: str
    outcome: str
    generic_event: bool
    placeholder: bool
    diagnostics: Dict[str, Any]

class EventGraphEdge(TypedDict, total=False):
    source: int
    target: int
    relation: str

class EventGraph(TypedDict, total=False):
    nodes: List[EventGraphNode]
    edges: List[EventGraphEdge]
    diagnostics: Dict[str, Any]

class NarrativePlan(TypedDict, total=False):
    narrative_type: str
    stages: List[str]
    strategy_hint: str
    story_arc_type: str
    confidence: Dict[str, float]
    diagnostics: Dict[str, Any]

class SummaryIR(TypedDict, total=False):
    version: str
    schema_version: str
    book_id: str
    title: str
    central_entities: List[str]
    entity_graph_summary: List[EntityGraphEntity]
    narrative_graph: Dict[str, Any]
    story_arc: Dict[str, Any]
    timeline: List[str]
    themes: List[str]
    learning_outcomes: List[str]
    confidence: Dict[str, float]
    diagnostics: Dict[str, Any]
    source_metadata: Dict[str, Any]

class QualityContract(TypedDict, total=False):
    status: StatusLiteral
    issues: List[Dict[str, Any]]
    risk_categories: List[str]
    diagnostics: Dict[str, Any]
    checked_at: str
    schema_version: str
