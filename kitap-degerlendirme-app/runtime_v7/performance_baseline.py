from __future__ import annotations

from typing import Any, Dict


_REQUIRED_MODULES = (
    "summary_ir",
    "narrative_graph",
    "narrative_chain",
    "cause_effect",
    "conflict_graph",
    "theme_validation",
    "character_validation",
    "learning_outcome_validation",
    "recommendations",
    "promotion_readiness",
    "shadow_audit",
)


def build_performance_baseline(
    *,
    total_runtime_ms: float,
    shadow_pipeline_ms: float,
    module_timings: Dict[str, Any],
) -> Dict[str, Any]:
    cleaned_timings: Dict[str, float] = {}
    for module_name in _REQUIRED_MODULES:
        try:
            value = float((module_timings or {}).get(module_name, 0.0))
        except Exception:
            value = 0.0
        cleaned_timings[module_name] = round(max(0.0, value), 3)

    total_runtime = round(max(0.0, float(total_runtime_ms)), 3)
    shadow_pipeline = round(max(0.0, float(shadow_pipeline_ms)), 3)
    if total_runtime > 0:
        overhead_ratio = round(shadow_pipeline / total_runtime, 3)
    else:
        overhead_ratio = 0.0

    return {
        "performance_baseline": {
            "total_runtime_ms": total_runtime,
            "shadow_pipeline_ms": shadow_pipeline,
            "module_timings": cleaned_timings,
            "shadow_overhead_ratio": overhead_ratio,
        }
    }
