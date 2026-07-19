import unittest
import json
from run_rc4_sprint7a_narrative_quality_check import build_rc4_sprint7a_narrative_quality_report


class TestRunRc4Sprint7aNarrativeQualityCheck(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_books = [
            {
                "book_id": "book-1",
                "summary_ir": {
                    "title": "Elif's Journey",
                    "central_entities": ["Elif", "Dede"],
                    "themes": ["courage", "friendship"],
                    "places": ["village", "mountain"],
                    "temporal_context": "modern",
                    "key_events": [
                        "Elif decides to climb the mountain",
                        "She faces a terrible storm",
                        "She helps her friend escape",
                    ],
                    "evidence_snippets": {
                        "conflict": ["For example, a storm blocked the path."],
                        "resolution": ["Together, they found their way home."],
                    }
                }
            },
            {
                "book_id": "book-2",
                "summary_ir": {
                    "title": "The Desert Journey",
                    "central_entities": ["Karim", "Layla"],
                    "themes": ["perseverance", "hope"],
                    "places": ["desert", "oasis"],
                    "temporal_context": "historical",
                    "key_events": [
                        "They cross the desert",
                        "They find an oasis",
                    ],
                    "evidence_snippets": {
                        "conflict": ["They faced harsh conditions."],
                    }
                }
            }
        ]
    
    def test_build_returns_dict(self):
        """Test that build function returns proper structure."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        
        self.assertIsInstance(result, dict)
        self.assertIn("sprint", result)
        self.assertIn("books", result)
    
    def test_report_has_all_required_fields(self):
        """Test that report has all required fields."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        
        required_fields = [
            "sprint", "generated_at", "total_books", "books",
            "aggregate_metrics", "shadow_only", "production_output_changed"
        ]
        for field in required_fields:
            self.assertIn(field, result, f"Missing field: {field}")
    
    def test_correct_book_count(self):
        """Test that correct number of books processed."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        
        self.assertEqual(result["total_books"], 2)
        self.assertEqual(len(result["books"]), 2)
    
    def test_each_book_has_all_phases(self):
        """Test that each book has results from all 4 phases."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        
        for book in result["books"]:
            self.assertIn("phase1_character_resolution", book)
            self.assertIn("phase2_evidence_synthesis", book)
            self.assertIn("phase3_narrative_structure", book)
            self.assertIn("phase4_theme_details", book)
    
    def test_phase1_character_resolution_present(self):
        """Test Phase 1 results are present."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        book = result["books"][0]
        
        phase1 = book["phase1_character_resolution"]
        self.assertIn("total_characters", phase1)
        self.assertIn("resolved_characters", phase1)
        self.assertGreater(len(phase1["resolved_characters"]), 0)
    
    def test_phase2_evidence_synthesis_present(self):
        """Test Phase 2 results are present."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        book = result["books"][0]
        
        phase2 = book["phase2_evidence_synthesis"]
        self.assertIn("sections_synthesized", phase2)
        self.assertIn("markers_removed", phase2)
        self.assertTrue(phase2["markers_removed"])  # Should remove markers
    
    def test_phase3_narrative_structure_present(self):
        """Test Phase 3 results are present."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        book = result["books"][0]
        
        phase3 = book["phase3_narrative_structure"]
        # Should have 6 sections
        expected_sections = ["setup", "conflict", "events", "themes", "resolution", "message"]
        for section in expected_sections:
            self.assertIn(section, phase3)
    
    def test_phase4_theme_details_present(self):
        """Test Phase 4 results are present."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        book = result["books"][0]
        
        phase4 = book["phase4_theme_details"]
        self.assertIsInstance(phase4, list)
        self.assertEqual(len(phase4), 2)  # 2 themes in test data
    
    def test_integrated_narrative_present(self):
        """Test that integrated narrative is produced."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        book = result["books"][0]
        
        narrative = book["integrated_narrative"]
        self.assertIsInstance(narrative, str)
        self.assertGreater(len(narrative), 50)
    
    def test_quality_assessment_present(self):
        """Test that quality assessment is present."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        book = result["books"][0]
        
        quality = book["quality_assessment"]
        quality_metrics = [
            "human_readability",
            "semantic_accuracy",
            "narrative_coherence",
            "theme_coverage",
            "overall_quality"
        ]
        for metric in quality_metrics:
            self.assertIn(metric, quality)
    
    def test_quality_scores_valid_range(self):
        """Test that quality scores are between 0 and 1."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        book = result["books"][0]
        
        quality = book["quality_assessment"]
        for metric in ["human_readability", "semantic_accuracy", "narrative_coherence", "theme_coverage"]:
            score = quality[metric]
            self.assertGreaterEqual(score, 0.0, f"{metric} below 0.0")
            self.assertLessEqual(score, 1.0, f"{metric} above 1.0")
    
    def test_metadata_present(self):
        """Test that metadata is recorded."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        book = result["books"][0]
        
        metadata = book["metadata"]
        self.assertIn("word_count", metadata)
        self.assertIn("character_count", metadata)
        self.assertIn("theme_count", metadata)
        self.assertIn("deterministic", metadata)
        self.assertTrue(metadata["deterministic"])
    
    def test_aggregate_metrics_calculated(self):
        """Test that aggregate metrics are calculated."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        
        agg = result["aggregate_metrics"]
        self.assertIn("avg_readability", agg)
        self.assertIn("avg_semantic_accuracy", agg)
        self.assertIn("avg_coherence", agg)
        self.assertIn("avg_theme_coverage", agg)
    
    def test_shadow_only_flag(self):
        """Test that shadow_only flag is set."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        
        self.assertTrue(result["shadow_only"])
    
    def test_production_output_unchanged(self):
        """Test that production_output_changed is False."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        
        self.assertFalse(result["production_output_changed"])
    
    def test_empty_input_safe(self):
        """Test that empty book list is handled safely."""
        result = build_rc4_sprint7a_narrative_quality_report([])
        
        self.assertEqual(result["total_books"], 0)
        self.assertEqual(len(result["books"]), 0)
    
    def test_deterministic_output(self):
        """Test that same input produces same output."""
        result1 = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        result2 = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        
        # Compare as JSON for determinism
        json1 = json.dumps(result1, sort_keys=True)
        json2 = json.dumps(result2, sort_keys=True)
        self.assertEqual(json1, json2)
    
    def test_character_names_in_narrative(self):
        """Test that character names appear in integrated narrative."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        book = result["books"][0]
        
        narrative = book["integrated_narrative"].lower()
        self.assertIn("elif", narrative)
    
    def test_themes_in_narrative(self):
        """Test that themes are covered in narrative."""
        result = build_rc4_sprint7a_narrative_quality_report(self.sample_books)
        book = result["books"][0]
        
        narrative = book["integrated_narrative"].lower()
        # Should mention at least one theme
        has_theme = "courage" in narrative or "friendship" in narrative
        self.assertTrue(has_theme)


if __name__ == "__main__":
    unittest.main()
