import copy
import json

from runtime_v7.adapter import build_v7_shadow_payload


PAYLOAD = {
    "kitap_adi": "Tavşan Pati",
    "summary_confidence": 0.8,
    "theme_confidence": 0.7,
    "event_confidence": 0.6,
    "entity_confidence": 0.5,
    "ana_karakterler": [
        {
            "ad": "Ali",
            "entity_type": "character",
            "mention_count": 3,
            "source_pages": [1, 2],
            "relation_score": 0.9,
            "central_entity": True,
        }
    ],
    "event_graph": {
        "nodes": [
            {"summary": "Ali bir yolculuğa çıkar."},
            {"summary": "Bir engel ile karşılaşır."},
            {"summary": "Sorun çözülür."},
        ]
    },
    "narrative_plan": {
        "stages": ["başlangıç", "gelişme", "sonuç"],
        "narrative_type": "quest",
    },
    "ilk_uc_baskin_tema": [{"ad": "kader"}, {"ad": "arkadaşlık"}, {"ad": "cesaret"}],
    "kazanim_analizi": [{"kazanim": "Öğrenci empati kurar."}],
}


def test_performance_baseline_is_always_present_and_consistent():
    shadow = build_v7_shadow_payload(copy.deepcopy(PAYLOAD))

    baseline = shadow.get("performance_baseline") or {}
    assert baseline, "performance_baseline alanı üretilmeli"
    assert "module_timings" in baseline, "module_timings alanı mevcut olmalı"
    assert "shadow_overhead_ratio" in baseline, "shadow_overhead_ratio mevcut olmalı"

    module_timings = baseline.get("module_timings") or {}
    assert isinstance(module_timings, dict)
    for name, timing in module_timings.items():
        assert timing >= 0, f"Negatif timing {name}: {timing}"

    total_runtime = float(baseline.get("total_runtime_ms", 0.0) or 0.0)
    shadow_runtime = float(baseline.get("shadow_pipeline_ms", 0.0) or 0.0)
    assert total_runtime >= shadow_runtime, "Toplam runtime shadow runtime'dan küçük olamaz"

    assert "performance_baseline" not in PAYLOAD, "Performance ölçümleri production payload'a sızmamalı"


def test_semantic_shadow_output_remains_deterministic_without_performance_field():
    first = build_v7_shadow_payload(copy.deepcopy(PAYLOAD))
    second = build_v7_shadow_payload(copy.deepcopy(PAYLOAD))

    def _strip_performance(value):
        if isinstance(value, dict):
            cleaned = {}
            for k, v in value.items():
                if k == "performance_baseline":
                    continue
                cleaned[k] = _strip_performance(v)
            return cleaned
        if isinstance(value, list):
            return [_strip_performance(item) for item in value]
        return value

    assert _strip_performance(first) == _strip_performance(second)
