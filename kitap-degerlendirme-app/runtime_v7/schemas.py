from __future__ import annotations

SUMMARY_IR_SCHEMA = {
    "type": "object",
    "properties": {
        "version": {"type": "string"},
        "schema_version": {"type": "string"},
        "book_id": {"type": "string"},
        "title": {"type": "string"},
        "central_entities": {"type": "array", "items": {"type": "string"}},
        "entity_graph_summary": {"type": "array", "items": {"type": "object"}},
        "narrative_graph": {"type": "object"},
        "story_arc": {"type": "object"},
        "timeline": {"type": "array", "items": {"type": "string"}},
        "themes": {"type": "array", "items": {"type": "string"}},
        "learning_outcomes": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "object"},
        "diagnostics": {"type": "object"},
        "source_metadata": {"type": "object"},
    },
    "required": [
        "version",
        "schema_version",
        "book_id",
        "title",
        "central_entities",
        "entity_graph_summary",
        "narrative_graph",
        "story_arc",
        "timeline",
        "themes",
        "learning_outcomes",
        "confidence",
        "diagnostics",
        "source_metadata",
    ],
    "additionalProperties": True,
}

ENTITY_GRAPH_SCHEMA = {
    "type": "object",
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "mention_count": {"type": "integer"},
                    "source_pages": {"type": "array", "items": {"type": "integer"}},
                    "relation_score": {"type": "number"},
                    "central": {"type": "boolean"},
                    "diagnostics": {"type": "object"},
                },
                "additionalProperties": True,
            },
        },
        "diagnostics": {"type": "object"},
    },
    "required": ["entities", "diagnostics"],
    "additionalProperties": True,
}

EVENT_GRAPH_SCHEMA = {
    "type": "object",
    "properties": {
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "actors": {"type": "array", "items": {"type": "string"}},
                    "action": {"type": "string"},
                    "conflict": {"type": "string"},
                    "outcome": {"type": "string"},
                    "generic_event": {"type": "boolean"},
                    "placeholder": {"type": "boolean"},
                    "diagnostics": {"type": "object"},
                },
                "additionalProperties": True,
            },
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "integer"},
                    "target": {"type": "integer"},
                    "relation": {"type": "string"},
                },
                "additionalProperties": True,
            },
        },
        "diagnostics": {"type": "object"},
    },
    "required": ["nodes", "edges", "diagnostics"],
    "additionalProperties": True,
}

NARRATIVE_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "narrative_type": {"type": "string"},
        "stages": {"type": "array", "items": {"type": "string"}},
        "strategy_hint": {"type": "string"},
        "story_arc_type": {"type": "string"},
        "confidence": {"type": "object"},
        "diagnostics": {"type": "object"},
    },
    "required": ["narrative_type", "stages", "strategy_hint", "story_arc_type", "confidence", "diagnostics"],
    "additionalProperties": True,
}

QUALITY_CONTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["PASS", "WARNING", "FAIL"]},
        "issues": {"type": "array", "items": {"type": "object"}},
        "risk_categories": {"type": "array", "items": {"type": "string"}},
        "diagnostics": {"type": "object"},
        "checked_at": {"type": "string"},
        "schema_version": {"type": "string"},
    },
    "required": ["status", "issues", "risk_categories", "diagnostics", "checked_at", "schema_version"],
    "additionalProperties": True,
}
