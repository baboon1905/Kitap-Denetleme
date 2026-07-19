from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from .typing import StatusLiteral

DEFAULT_SCHEMA_VERSION = "v1"

def is_v7_shadow_mode() -> bool:
    return str(os.environ.get("V7_SHADOW_MODE") or "").lower() in ("1", "true", "yes")

V7_SHADOW_MODE = is_v7_shadow_mode()


def is_v7_summary_ir_source() -> bool:
    return str(os.environ.get("V7_SUMMARY_IR_SOURCE") or "").lower() in ("1", "true", "yes")

V7_SUMMARY_IR_SOURCE = is_v7_summary_ir_source()


def is_v7_narrative_graph() -> bool:
    return str(os.environ.get("V7_NARRATIVE_GRAPH") or "").lower() in ("1", "true", "yes")


V7_NARRATIVE_GRAPH = is_v7_narrative_graph()

@dataclass(frozen=True)
class EntityGraphEntity:
    name: str = ""
    type: str = ""
    mention_count: int = 0
    source_pages: List[int] = field(default_factory=list)
    relation_score: float = 0.0
    central: bool = False
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class EntityGraph:
    entities: List[EntityGraphEntity] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entities": [entity.to_dict() for entity in self.entities],
            "diagnostics": dict(self.diagnostics),
        }

@dataclass(frozen=True)
class EventGraphEdge:
    source: int = 0
    target: int = 0
    relation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class EventGraphNode:
    actors: List[str] = field(default_factory=list)
    action: str = ""
    conflict: str = ""
    outcome: str = ""
    generic_event: bool = False
    placeholder: bool = False
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class EventGraph:
    nodes: List[EventGraphNode] = field(default_factory=list)
    edges: List[EventGraphEdge] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "diagnostics": dict(self.diagnostics),
        }

@dataclass(frozen=True)
class NarrativePlan:
    narrative_type: str = ""
    stages: List[str] = field(default_factory=list)
    strategy_hint: str = ""
    story_arc_type: str = ""
    confidence: Dict[str, float] = field(default_factory=dict)
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class QualityContract:
    status: StatusLiteral = "PASS"
    issues: List[Dict[str, Any]] = field(default_factory=list)
    risk_categories: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    checked_at: str = ""
    schema_version: str = DEFAULT_SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class SummaryIR:
    version: str = ""
    schema_version: str = DEFAULT_SCHEMA_VERSION
    book_id: str = ""
    title: str = ""
    central_entities: List[str] = field(default_factory=list)
    entity_graph_summary: List[Dict[str, Any]] = field(default_factory=list)
    narrative_graph: Dict[str, Any] = field(default_factory=dict)
    story_arc: Dict[str, Any] = field(default_factory=dict)
    timeline: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    learning_outcomes: List[str] = field(default_factory=list)
    confidence: Dict[str, float] = field(default_factory=dict)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    source_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
