from __future__ import annotations

from .contracts import (
    EntityGraph,
    EventGraph,
    NarrativePlan,
    QualityContract,
    SummaryIR,
    StatusLiteral,
    V7_SHADOW_MODE,
    V7_SUMMARY_IR_SOURCE,
    is_v7_shadow_mode,
    is_v7_summary_ir_source,
)
from .summary_surface import (
    build_summary_surfaces_from_ir,
    compute_summary_ir_hash,
    sync_summary_surfaces_from_ir,
)
from .narrative_chain import build_narrative_chains
from .cause_effect import build_cause_effect_relations
from .conflict_graph import build_conflict_graph
from .conflict_resolution import build_primary_conflict_resolution
from .theme_validation import compute_theme_validation
from .character_validation import compute_character_validation
from .learning_outcome_validation import compute_learning_outcome_validation
from .validation_coverage import compute_validation_coverage
from .validation_confidence import compute_validation_confidence
from .quality_comparison import compute_quality_comparison
from .schemas import (
    ENTITY_GRAPH_SCHEMA,
    EVENT_GRAPH_SCHEMA,
    NARRATIVE_PLAN_SCHEMA,
    QUALITY_CONTRACT_SCHEMA,
    SUMMARY_IR_SCHEMA,
)
from .typing import (
    EntityGraphEntity,
    EventGraph,
    EventGraphEdge,
    EventGraphNode,
    NarrativePlan as NarrativePlanTyping,
    QualityContract as QualityContractTyping,
    SummaryIR as SummaryIRTyping,
    StatusLiteral,
)
from .semantic_engine import SemanticEngine

__all__ = [
    "SummaryIR",
    "EntityGraph",
    "EventGraph",
    "NarrativePlan",
    "QualityContract",
    "StatusLiteral",
    "V7_SHADOW_MODE",
    "is_v7_shadow_mode",
    "SUMMARY_IR_SCHEMA",
    "ENTITY_GRAPH_SCHEMA",
    "EVENT_GRAPH_SCHEMA",
    "NARRATIVE_PLAN_SCHEMA",
    "QUALITY_CONTRACT_SCHEMA",
    "EntityGraphEntity",
    "EventGraphEdge",
    "EventGraphNode",
    "SummaryIRTyping",
    "NarrativePlanTyping",
    "QualityContractTyping",
    "V7_SUMMARY_IR_SOURCE",
    "is_v7_summary_ir_source",
    "build_summary_surfaces_from_ir",
    "compute_summary_ir_hash",
    "sync_summary_surfaces_from_ir",
    "build_narrative_chains",
    "build_cause_effect_relations",
    "build_conflict_graph",
    "build_conflict_resolution",
    "build_story_arc_classification",
    "compute_theme_validation",
    "compute_character_validation",
    "compute_learning_outcome_validation",
    "compute_validation_coverage",
    "compute_validation_confidence",
    "compute_quality_comparison",
    "SemanticEngine",
]
