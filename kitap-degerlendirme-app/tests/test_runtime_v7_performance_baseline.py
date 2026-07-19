from runtime_v7.performance_baseline import build_performance_baseline


def test_build_performance_baseline_shape():
    baseline = build_performance_baseline(
        total_runtime_ms=12.34,
        shadow_pipeline_ms=4.56,
        module_timings={
            "summary_ir": 0.5,
            "narrative_graph": 0.2,
            "narrative_chain": 0.1,
            "cause_effect": 0.1,
            "conflict_graph": 0.2,
            "theme_validation": 0.3,
            "character_validation": 0.2,
            "learning_outcome_validation": 0.2,
            "recommendations": 0.1,
            "promotion_readiness": 0.1,
            "shadow_audit": 0.1,
        },
    )

    assert "performance_baseline" in baseline
    assert baseline["performance_baseline"]["total_runtime_ms"] >= 0
    assert baseline["performance_baseline"]["shadow_pipeline_ms"] >= 0
    assert baseline["performance_baseline"]["shadow_overhead_ratio"] >= 0
    assert set(baseline["performance_baseline"]["module_timings"].keys()) == {
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
    }
