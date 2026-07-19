from __future__ import annotations

from .contracts import EventGraph
from .story_arc_planner import plan_story_arc


def build_story_arc(event_graph: EventGraph) -> dict:
    try:
        plan = plan_story_arc(event_graph)
        return plan
    except Exception:
        return {"type": "unknown", "stages": {}, "source": "runtime_v7_story_arc"}
