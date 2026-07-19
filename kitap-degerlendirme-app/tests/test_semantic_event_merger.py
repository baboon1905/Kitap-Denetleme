import pytest

from runtime_v7.semantic_event_merger import merge_semantic_events


def test_merges_similar_consecutive_events_and_reduces_count():
    items = [
        {"text": "Ali evden çıktı.", "source_sentence_ids": ["s1"], "section": "events"},
        {"text": "Ali evden ayrıldı.", "source_sentence_ids": ["s2"], "section": "events"},
        {"text": "Bu çok zordu.", "source_sentence_ids": ["s3"], "section": "conflict"},
    ]

    result = merge_semantic_events(items)

    assert result["input_event_count"] == 3
    assert result["output_event_count"] == 2
    assert result["merge_ratio"] < 0.75
    assert result["source_sentence_id_preservation_rate"] == 1.0
    assert result["deterministic"] is True
    assert result["production_output_changed"] is False
    assert result["runtime_pipeline_bound"] is False


def test_preserves_source_sentence_ids_on_merge():
    items = [
        {"text": "Ali okula gitti.", "source_sentence_ids": ["s1"], "section": "events"},
        {"text": "Ali okula yürüdü.", "source_sentence_ids": ["s2"], "section": "events"},
    ]

    result = merge_semantic_events(items)
    merged = result["merged_events"][0]

    assert merged["source_sentence_ids"] == ["s1", "s2"]
    assert merged["evidence_count"] == 2


def test_preserves_conflict_and_resolution_events():
    items = [
        {"text": "Bir problem ortaya çıktı.", "source_sentence_ids": ["c1"], "section": "conflict"},
        {"text": "Sonunda çözüm bulundu.", "source_sentence_ids": ["r1"], "section": "resolution"},
    ]

    result = merge_semantic_events(items)

    sections = {event["section"] for event in result["merged_events"]}
    assert sections == {"conflict", "resolution"}


def test_preserves_chronology_order():
    items = [
        {"text": "Başlangıç oldu.", "source_sentence_ids": ["s1"], "section": "setup"},
        {"text": "Başlangıçtan sonra gelişme yaşandı.", "source_sentence_ids": ["s2"], "section": "events"},
        {"text": "Sonunda sonuç alındı.", "source_sentence_ids": ["s3"], "section": "resolution"},
    ]

    result = merge_semantic_events(items)
    texts = [event["text"] for event in result["merged_events"]]

    assert texts[0].startswith("Başlangıç")
    assert texts[-1].startswith("Sonunda")


def test_preserves_conflict_and_resolution_metadata_on_merge():
    items = [
        {"text": "Bir problem ortaya çıktı.", "source_sentence_ids": ["c1"], "section": "conflict", "conflict": True, "resolution_state": "unresolved"},
        {"text": "Sonunda çözüm bulundu.", "source_sentence_ids": ["r1"], "section": "resolution", "conflict": False, "resolution_state": "resolved"},
    ]

    result = merge_semantic_events(items)
    merged_sections = {event["section"] for event in result["merged_events"]}

    assert merged_sections == {"conflict", "resolution"}
    assert any(event.get("conflict") is True for event in result["merged_events"])
    assert any(event.get("resolution_state") == "resolved" for event in result["merged_events"])


def test_deterministic_for_same_input():
    items = [
        {"text": "Ali bir karar verdi.", "source_sentence_ids": ["s1"], "section": "events"},
        {"text": "Ali kararını uyguladı.", "source_sentence_ids": ["s2"], "section": "events"},
    ]

    result_a = merge_semantic_events(items)
    result_b = merge_semantic_events(items)

    assert result_a["merged_events"] == result_b["merged_events"]


def test_accepts_dict_section_input():
    items = {
        "setup": [{"text": "Bir yolculuk başladı.", "source_sentence_ids": ["s1"], "section": "setup"}],
        "events": [
            {"text": "Yolculuk devam etti.", "source_sentence_ids": ["s2"], "section": "events"},
            {"text": "Yolculuk sürdü.", "source_sentence_ids": ["s3"], "section": "events"},
        ],
    }

    result = merge_semantic_events(items)

    assert result["input_event_count"] == 3
    assert result["output_event_count"] == 2


def test_does_not_merge_dissimilar_events():
    items = [
        {"text": "Ali bir kapıyı açtı.", "source_sentence_ids": ["s1"], "section": "events"},
        {"text": "Yarın hava çok güzel olacak.", "source_sentence_ids": ["s2"], "section": "events"},
    ]

    result = merge_semantic_events(items)

    assert result["output_event_count"] == 2


def test_handles_empty_input():
    result = merge_semantic_events([])

    assert result["input_event_count"] == 0
    assert result["output_event_count"] == 0
    assert result["merge_ratio"] == 0.0
    assert result["source_sentence_id_preservation_rate"] == 1.0


def test_accepts_reconstructed_event_like_dicts():
    items = [
        {"action": "Ali yürüdü.", "source_sentence_ids": ["s1"], "section": "events"},
        {"action": "Ali yavaşça yürüdü.", "source_sentence_ids": ["s2"], "section": "events"},
    ]

    result = merge_semantic_events(items)

    assert result["output_event_count"] == 1
    assert result["merged_events"][0]["source_sentence_ids"] == ["s1", "s2"]


def test_does_not_merge_across_section_boundaries():
    items = [
        {"text": "Ali okula gitti.", "source_sentence_ids": ["s1"], "section": "setup"},
        {"text": "Ali okula gitti.", "source_sentence_ids": ["s2"], "section": "events"},
    ]

    result = merge_semantic_events(items)

    assert result["output_event_count"] == 2


def test_keeps_supporting_evidence_ids_and_merges_count():
    items = [
        {"text": "Ali eve döndü.", "source_sentence_ids": ["s1"], "section": "events"},
        {"text": "Ali eve dönmeye karar verdi.", "source_sentence_ids": ["s2"], "section": "events"},
    ]

    result = merge_semantic_events(items)
    merged = result["merged_events"][0]

    assert merged["evidence_count"] == 2
    assert merged["supporting_evidence_ids"] == ["s1", "s2"]
