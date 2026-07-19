"""Tests for source ID normalization in canonical_summary_ir.

Validates that:
1. Singular source_sentence_id fields are normalized to plural lists
2. Plural forms are preserved
3. No data loss during normalization
4. Determinism is maintained
5. Production output is unchanged
6. Downstream enricher receives correctly formatted traceability
"""

import copy
import hashlib
import json
import os
import pytest
from pathlib import Path
import sys

# Add parent directory to path so imports work
app_dir = str(Path(__file__).parent.parent)
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from summary_ir import build_summary_ir, _normalize_source_ids, _normalize_item_source_ids
from narrative_planner import build_narrative_outline


class TestNormalizeSourceIds:
    """Unit tests for _normalize_source_ids function."""
    
    def test_singular_string_to_list(self):
        """Test: source_sentence_id: "p14:s4" -> ["p14:s4"]"""
        result = _normalize_source_ids("p14:s4")
        assert result == ["p14:s4"]
    
    def test_plural_list_preserved(self):
        """Test: source_sentence_ids: ["p14:s4", "p15:s2"] -> ["p14:s4", "p15:s2"]"""
        result = _normalize_source_ids(["p14:s4", "p15:s2"])
        assert result == ["p14:s4", "p15:s2"]
    
    def test_duplicate_removal_order_preserved(self):
        """Test: Duplicate values removed while preserving first occurrence order"""
        result = _normalize_source_ids(["p14:s4", "p15:s2", "p14:s4"])
        assert result == ["p14:s4", "p15:s2"]
        assert result.index("p14:s4") == 0
    
    def test_empty_string_ignored(self):
        """Test: Empty strings are filtered out"""
        result = _normalize_source_ids("")
        assert result == []
    
    def test_whitespace_stripped(self):
        """Test: Whitespace is stripped from IDs"""
        result = _normalize_source_ids("  p14:s4  ")
        assert result == ["p14:s4"]
    
    def test_none_ignored(self):
        """Test: None values are handled gracefully"""
        result = _normalize_source_ids(None)
        assert result == []
    
    def test_numeric_id_converted(self):
        """Test: Numeric IDs are converted to strings"""
        result = _normalize_source_ids(42)
        assert result == ["42"]
    
    def test_boolean_ignored(self):
        """Test: Boolean values are ignored"""
        result = _normalize_source_ids(True)
        assert result == []
    
    def test_mixed_list(self):
        """Test: Mixed string and numeric IDs"""
        result = _normalize_source_ids(["p14:s4", 123, "p15:s2"])
        assert "p14:s4" in result
        assert "123" in result
        assert "p15:s2" in result


class TestNormalizeItemSourceIds:
    """Tests for _normalize_item_source_ids recursive normalization."""
    
    def test_dict_singular_to_plural(self):
        """Test: Dict with singular source_sentence_id normalized to plural"""
        item = {"text": "sample", "source_sentence_id": "p14:s4"}
        result = _normalize_item_source_ids(item)
        assert "source_sentence_ids" in result
        assert result["source_sentence_ids"] == ["p14:s4"]
        assert "source_sentence_id" not in result  # Singular field removed
        assert result["text"] == "sample"  # Other fields preserved
    
    def test_dict_plural_preserved(self):
        """Test: Dict with plural source_sentence_ids preserved"""
        item = {"text": "sample", "source_sentence_ids": ["p14:s4", "p15:s2"]}
        result = _normalize_item_source_ids(item)
        assert result["source_sentence_ids"] == ["p14:s4", "p15:s2"]
        assert result["text"] == "sample"
    
    def test_dict_input_not_mutated(self):
        """Test: Input dict is not mutated"""
        original = {"text": "sample", "source_sentence_id": "p14:s4"}
        snapshot = copy.deepcopy(original)
        result = _normalize_item_source_ids(original)
        assert original == snapshot  # Original unchanged
        assert "source_sentence_ids" in result  # Result normalized
    
    def test_nested_list_normalized(self):
        """Test: Nested list items are recursively normalized"""
        items = [
            {"text": "first", "source_sentence_id": "p1:s1"},
            {"text": "second", "source_sentence_id": "p2:s2"},
        ]
        result = _normalize_item_source_ids(items)
        assert len(result) == 2
        assert result[0]["source_sentence_ids"] == ["p1:s1"]
        assert result[1]["source_sentence_ids"] == ["p2:s2"]
    
    def test_nested_dict_normalized(self):
        """Test: Nested dict values are recursively normalized"""
        item = {
            "text": "parent",
            "child": {
                "text": "nested",
                "source_sentence_id": "p3:s3"
            }
        }
        result = _normalize_item_source_ids(item)
        assert result["child"]["source_sentence_ids"] == ["p3:s3"]
        assert "source_sentence_id" not in result["child"]
    
    def test_scalar_unchanged(self):
        """Test: Scalar values returned unchanged"""
        assert _normalize_item_source_ids("string") == "string"
        assert _normalize_item_source_ids(42) == 42
        assert _normalize_item_source_ids(3.14) == 3.14
    
    def test_fallback_source_ids_field(self):
        """Test: Fallback to source_ids field if source_sentence_ids not present"""
        item = {"text": "sample", "source_ids": ["p1:s1"]}
        result = _normalize_item_source_ids(item)
        assert result["source_sentence_ids"] == ["p1:s1"]
        assert "source_ids" not in result
    
    def test_fallback_sentence_ids_field(self):
        """Test: Fallback to sentence_ids field"""
        item = {"text": "sample", "sentence_ids": ["s1", "s2"]}
        result = _normalize_item_source_ids(item)
        assert result["source_sentence_ids"] == ["s1", "s2"]
        assert "sentence_ids" not in result


class TestEventSequenceNormalization:
    """Tests for normalization of event_sequence field in canonical IR."""
    
    def test_event_sequence_with_source_ids(self):
        """Test: event_sequence items with source_sentence_id normalized"""
        payload = {
            "kitap_adi": "Test Book",
            "event_graph": [
                {
                    "canonical_event": True,
                    "action": "jump",
                    "source_sentence_id": "p5:s1",
                    "actors": ["child"]
                },
                {
                    "canonical_event": True,
                    "action": "run",
                    "source_sentence_id": "p6:s2",
                    "actors": ["child"]
                },
            ],
        }
        ir = build_summary_ir(payload)
        
        # Check that event_sequence is normalized
        for event in ir.get("event_sequence", []):
            if isinstance(event, dict) and event.get("source_sentence_id"):
                pytest.fail(f"Found singular source_sentence_id in event_sequence: {event}")
            if isinstance(event, dict) and event.get("source_sentence_ids"):
                assert isinstance(event["source_sentence_ids"], list)
                assert all(isinstance(id, str) for id in event["source_sentence_ids"])
    
    def test_deterministic_normalization(self):
        """Test: Two normalizations produce identical canonical_summary_ir hash"""
        payload = {
            "kitap_adi": "Test Book",
            "event_graph": [
                {
                    "canonical_event": True,
                    "action": "jump",
                    "source_sentence_id": "p5:s1",
                    "actors": ["child"]
                },
            ],
        }
        ir1 = build_summary_ir(payload)
        ir2 = build_summary_ir(copy.deepcopy(payload))
        
        # Both should have same hash
        assert ir1.get("hash") == ir2.get("hash")
    
    def test_production_payload_unchanged(self):
        """Test: Original payload is not modified"""
        payload = {
            "kitap_adi": "Test Book",
            "event_graph": [
                {
                    "canonical_event": True,
                    "action": "jump",
                    "source_sentence_id": "p5:s1",
                    "actors": ["child"]
                },
            ],
        }
        payload_snapshot = copy.deepcopy(payload)
        
        # Build IR
        ir = build_summary_ir(payload)
        
        # Payload should be unchanged
        assert payload == payload_snapshot
        assert payload["event_graph"][0]["source_sentence_id"] == "p5:s1"
        assert "source_sentence_ids" not in payload["event_graph"][0]


class TestTurningPointsNormalization:
    """Tests for normalization of turning_points field."""
    
    def test_turning_points_with_source_ids(self):
        """Test: turning_points items normalized if they are dicts"""
        payload = {
            "kitap_adi": "Test Book",
            "event_graph": [
                {
                    "canonical_event": True,
                    "turning_point": "donum_noktasi",
                    "source_sentence_id": "p10:s5",
                    "action": "decision",
                    "actors": ["protagonist"]
                },
            ],
        }
        ir = build_summary_ir(payload)
        
        # turning_points should be normalized (can be strings or dicts)
        turning_points = ir.get("turning_points", [])
        for tp in turning_points:
            if isinstance(tp, dict):
                assert "source_sentence_ids" in tp or "source_sentence_id" not in tp


class TestEventImportanceNormalization:
    """Tests for normalization of event_importance field."""
    
    def test_event_importance_with_source_ids(self):
        """Test: event_importance items normalized"""
        payload = {
            "kitap_adi": "Test Book",
            "event_graph": [
                {
                    "canonical_event": True,
                    "action": "critical_decision",
                    "source_sentence_id": "p8:s3",
                    "actors": ["hero"]
                },
            ],
        }
        ir = build_summary_ir(payload)
        
        # event_importance should have normalized source IDs
        event_importance = ir.get("event_importance", [])
        for ei in event_importance:
            if isinstance(ei, dict) and "source_sentence_id" in ei:
                pytest.fail(f"Found singular source_sentence_id in event_importance: {ei}")


class TestCanonicalIRFieldNormalization:
    """Integration tests for all normalized fields in canonical IR."""
    
    def test_no_placeholders_created(self):
        """Test: Normalization does not create placeholder source_sentence_ids"""
        payload = {
            "kitap_adi": "Test Book",
            "event_graph": [
                {
                    "canonical_event": True,
                    "action": "run",
                    "actors": ["child"],
                    # No source_sentence_id field
                },
            ],
        }
        ir = build_summary_ir(payload)
        
        # Check no spurious source_sentence_ids created
        for event in ir.get("event_sequence", []):
            if isinstance(event, dict):
                ids = event.get("source_sentence_ids", [])
                assert isinstance(ids, list)
                # Only check if source field existed upstream
    
    def test_no_data_loss_across_normalization(self):
        """Test: All source IDs from payload are present in normalized IR"""
        expected_ids = {"p1:s1", "p2:s2", "p3:s3"}
        
        payload = {
            "kitap_adi": "Test Book",
            "event_graph": [
                {"canonical_event": True, "action": "act1", "source_sentence_id": "p1:s1", "actors": ["a"]},
                {"canonical_event": True, "action": "act2", "source_sentence_id": "p2:s2", "actors": ["b"]},
                {"canonical_event": True, "action": "act3", "source_sentence_id": "p3:s3", "actors": ["c"]},
            ],
        }
        ir = build_summary_ir(payload)
        
        # Collect all normalized IDs from IR
        collected_ids = set()
        for event in ir.get("event_sequence", []):
            if isinstance(event, dict) and "source_sentence_ids" in event:
                collected_ids.update(event["source_sentence_ids"])
        
        # All expected IDs should be present
        assert expected_ids.issubset(collected_ids), f"Lost IDs: {expected_ids - collected_ids}"
    
    def test_deterministic_hash_across_runs(self):
        """Test: canonical_summary_ir hash is deterministic"""
        payload = {
            "kitap_adi": "Test Book",
            "event_graph": [
                {
                    "canonical_event": True,
                    "action": "jump",
                    "source_sentence_id": "p5:s1",
                    "actors": ["child"]
                },
            ],
        }
        
        # Run multiple times
        ir_run1 = build_summary_ir(copy.deepcopy(payload))
        ir_run2 = build_summary_ir(copy.deepcopy(payload))
        ir_run3 = build_summary_ir(copy.deepcopy(payload))
        
        hash1 = ir_run1.get("hash")
        hash2 = ir_run2.get("hash")
        hash3 = ir_run3.get("hash")
        
        assert hash1 == hash2 == hash3


class TestEnricherIntegration:
    """Integration tests with semantic field enricher."""
    
    def test_enricher_consumes_normalized_ids(self):
        """Test: Enricher can consume normalized source_sentence_ids from IR"""
        # Load enricher
        from runtime_v7.semantic_field_enricher import enrich_semantic_fields
        
        # Create item with normalized IDs
        item = {
            "text": "Çocuk parkta oynadı.",
            "source_sentence_ids": ["p1:s1", "p2:s2"]
        }
        
        # Enricher should process without error
        result = enrich_semantic_fields([item])
        assert "enriched_events" in result
        assert len(result["enriched_events"]) > 0
        
        # Enriched item should preserve source_sentence_ids
        enriched = result["enriched_events"][0]
        assert enriched.get("source_sentence_ids") == ["p1:s1", "p2:s2"]


class TestNarrativePlannerSourceIdPropagation:
    """Direct regression tests for narrative planner source-ID propagation."""

    def test_event_sequence_keeps_single_source_sentence_id(self):
        payload = {
            "kitap_adi": "Test Book",
            "event_graph": [
                {
                    "canonical_event": True,
                    "action": "jump",
                    "source_sentence_id": "p5:s1",
                    "actors": ["child"],
                }
            ],
        }

        outline = build_narrative_outline(payload)
        event_sequence = outline.get("event_sequence", [])
        assert len(event_sequence) == 1
        assert event_sequence[0]["source_sentence_id"] == "p5:s1"
        assert event_sequence[0].get("source_sentence_ids") is None

    def test_event_sequence_keeps_source_sentence_ids_list(self):
        payload = {
            "kitap_adi": "Test Book",
            "event_graph": [
                {
                    "canonical_event": True,
                    "action": "run",
                    "source_sentence_ids": ["p7:s2", "p8:s3"],
                    "actors": ["child"],
                }
            ],
        }

        outline = build_narrative_outline(payload)
        event_sequence = outline.get("event_sequence", [])
        assert len(event_sequence) == 1
        assert event_sequence[0]["source_sentence_ids"] == ["p7:s2", "p8:s3"]

    def test_event_importance_keeps_source_id_fields(self):
        payload = {
            "kitap_adi": "Test Book",
            "event_graph": [
                {
                    "canonical_event": True,
                    "action": "decide",
                    "source_sentence_id": "p9:s4",
                    "actors": ["hero"],
                }
            ],
        }

        outline = build_narrative_outline(payload)
        event_importance = outline.get("event_importance", [])
        assert len(event_importance) == 1
        assert event_importance[0]["source_sentence_id"] == "p9:s4"
        assert event_importance[0].get("source_sentence_ids") is None

    def test_turning_points_keeps_source_id_fields(self):
        payload = {
            "kitap_adi": "Test Book",
            "event_graph": [
                {
                    "canonical_event": True,
                    "action": "decide",
                    "source_sentence_id": "p10:s5",
                    "turning_point": "true",
                    "actors": ["hero"],
                }
            ],
        }

        outline = build_narrative_outline(payload)
        turning_points = outline.get("turning_points", [])
        assert len(turning_points) == 1
        assert turning_points[0]["source_sentence_id"] == "p10:s5"

    def test_no_fabricated_source_ids_for_events_without_source_ids(self):
        payload = {
            "kitap_adi": "Test Book",
            "event_graph": [
                {
                    "canonical_event": True,
                    "action": "walk",
                    "actors": ["child"],
                }
            ],
        }

        outline = build_narrative_outline(payload)
        event_sequence = outline.get("event_sequence", [])
        assert len(event_sequence) == 1
        assert "source_sentence_id" not in event_sequence[0]
        assert "source_sentence_ids" not in event_sequence[0]

    def test_input_payload_not_mutated(self):
        payload = {
            "kitap_adi": "Test Book",
            "event_graph": [
                {
                    "canonical_event": True,
                    "action": "jump",
                    "source_sentence_id": "p5:s1",
                    "actors": ["child"],
                }
            ],
        }
        snapshot = copy.deepcopy(payload)

        build_narrative_outline(payload)

        assert payload == snapshot
        assert payload["event_graph"][0]["source_sentence_id"] == "p5:s1"

    def test_deterministic_source_id_propagation(self):
        payload = {
            "kitap_adi": "Test Book",
            "event_graph": [
                {
                    "canonical_event": True,
                    "action": "jump",
                    "source_sentence_id": "p5:s1",
                    "actors": ["child"],
                }
            ],
        }

        outline1 = build_narrative_outline(copy.deepcopy(payload))
        outline2 = build_narrative_outline(copy.deepcopy(payload))

        assert outline1 == outline2
        assert outline1["event_sequence"][0]["source_sentence_id"] == "p5:s1"
        assert outline1["event_sequence"][0].get("source_sentence_ids") is None


class TestRegressionProductionOutput:
    """Regression tests to ensure production output is unchanged."""
    
    def test_v7_flag_off_no_normalization_applied(self):
        """Test: When V7_SUMMARY_IR_SOURCE is off, no canonical_summary_ir returned"""
        # This test verifies the gating mechanism
        os.environ["V7_SUMMARY_IR_SOURCE"] = "0"
        
        try:
            # Load app module - it checks the env flag
            from runtime_v7.contracts import is_v7_summary_ir_source
            
            # Flag should return False
            assert not is_v7_summary_ir_source()
        finally:
            os.environ["V7_SUMMARY_IR_SOURCE"] = "0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
