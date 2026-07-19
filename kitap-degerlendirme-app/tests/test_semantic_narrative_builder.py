import unittest
from runtime_v7.semantic_narrative_builder import SemanticNarrativeBuilder


class TestSemanticNarrativeBuilder(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.summary_ir = {
            "title": "Elif's Journey",
            "central_entities": ["Elif", "Dede", "Ağabeyi"],
            "themes": ["courage", "friendship"],
            "places": ["the village", "the mountain"],
            "temporal_context": "modern",
            "key_events": [
                "Elif decides to climb the mountain",
                "She encounters a storm",
                "She finds shelter in a cave",
                "She meets a lost friend",
                "They return home together"
            ],
            "evidence_snippets": {
                "setup": ["She lived in a small village at the foot of a mountain."],
                "conflict": ["A terrible storm blocked the mountain pass."],
                "resolution": ["Together, they found their way home safely."],
            }
        }
        self.builder = SemanticNarrativeBuilder(self.summary_ir)
    
    def test_build_returns_dict_structure(self):
        """Test that build() returns proper structure."""
        result = self.builder.build()
        
        self.assertIsInstance(result, dict)
        self.assertIn("narrative", result)
        self.assertIn("sections", result)
        self.assertIn("metadata", result)
    
    def test_build_returns_all_sections(self):
        """Test that all 6 sections are present."""
        result = self.builder.build()
        sections = result["sections"]
        
        expected_sections = ["setup", "conflict", "events", "themes", "resolution", "message"]
        for section in expected_sections:
            self.assertIn(section, sections)
    
    def test_setup_section_contains_character(self):
        """Test that setup introduces the character."""
        result = self.builder.build()
        setup = result["sections"]["setup"].lower()
        
        self.assertIn("elif", setup)
    
    def test_setup_section_mentions_themes(self):
        """Test that setup mentions themes."""
        result = self.builder.build()
        setup = result["sections"]["setup"].lower()
        
        # Should mention at least one theme
        self.assertTrue("courage" in setup or "friendship" in setup)
    
    def test_conflict_section_not_empty(self):
        """Test that conflict section has content."""
        result = self.builder.build()
        conflict = result["sections"]["conflict"]
        
        self.assertTrue(len(conflict) > 0)
        self.assertNotEqual(conflict, "")
    
    def test_events_section_uses_transitions(self):
        """Test that events use proper transitions (First, Then, etc)."""
        result = self.builder.build()
        events = result["sections"]["events"].lower()
        
        transitions = ["first", "then", "soon", "meanwhile", "finally"]
        has_transition = any(trans in events for trans in transitions)
        self.assertTrue(has_transition)
    
    def test_themes_section_contains_theme_names(self):
        """Test that themes section mentions theme names."""
        result = self.builder.build()
        themes = result["sections"]["themes"].lower()
        
        self.assertIn("courage", themes)
        self.assertIn("friendship", themes)
    
    def test_resolution_section_contains_character(self):
        """Test that resolution mentions character."""
        result = self.builder.build()
        resolution = result["sections"]["resolution"].lower()
        
        self.assertIn("elif", resolution)
    
    def test_message_section_not_empty(self):
        """Test that message section has content."""
        result = self.builder.build()
        message = result["sections"]["message"]
        
        self.assertTrue(len(message) > 0)
    
    def test_full_narrative_includes_all_sections(self):
        """Test that full narrative includes content from all sections."""
        result = self.builder.build()
        narrative = result["narrative"].lower()
        
        # Should include character and themes
        self.assertIn("elif", narrative)
        self.assertTrue("courage" in narrative or "friendship" in narrative)
    
    def test_metadata_word_count(self):
        """Test that metadata includes accurate word count."""
        result = self.builder.build()
        metadata = result["metadata"]
        actual_words = len(result["narrative"].split())
        
        self.assertEqual(metadata["word_count"], actual_words)
    
    def test_metadata_character_count(self):
        """Test that metadata tracks character count."""
        result = self.builder.build()
        metadata = result["metadata"]
        
        self.assertEqual(metadata["character_count"], 3)  # Elif, Dede, Ağabeyi
    
    def test_metadata_theme_count(self):
        """Test that metadata tracks theme count."""
        result = self.builder.build()
        metadata = result["metadata"]
        
        self.assertEqual(metadata["theme_count"], 2)  # courage, friendship
    
    def test_metadata_deterministic(self):
        """Test that metadata marks output as deterministic."""
        result = self.builder.build()
        metadata = result["metadata"]
        
        self.assertTrue(metadata["deterministic"])
    
    def test_deterministic_output(self):
        """Test that same IR produces same narrative."""
        result1 = self.builder.build()
        result2 = self.builder.build()
        
        self.assertEqual(result1["narrative"], result2["narrative"])
    
    def test_no_book_title_in_narrative(self):
        """Test that book title is sanitized from narrative."""
        result = self.builder.build()
        narrative = result["narrative"]
        
        # "Elif's Journey" should not appear
        self.assertNotIn("Elif's Journey", narrative)
    
    def test_setup_section_uses_evidence_detail(self):
        """Test that setup contains concrete detail from evidence."""
        result = self.builder.build()
        setup = result["sections"]["setup"].lower()

        self.assertIn("small village", setup)
        self.assertIn("foot of a mountain", setup)
    
    def test_conflict_section_uses_evidence_text(self):
        """Test that conflict section preserves the core evidence text."""
        result = self.builder.build()
        conflict = result["sections"]["conflict"].lower()

        self.assertIn("terrible storm blocked the mountain pass", conflict)
        self.assertNotIn("for example", conflict)
    
    def test_events_section_has_at_least_three_steps(self):
        """Test that events section produces at least three event sentences."""
        result = self.builder.build()
        events = result["sections"]["events"]
        event_sentences = [s.strip() for s in events.split('.') if s.strip()]

        self.assertGreaterEqual(len(event_sentences), 3)
    
    def test_message_links_to_primary_theme(self):
        """Test that message section references the primary theme."""
        result = self.builder.build()
        message = result["sections"]["message"].lower()

        self.assertIn("courage", message)

    def test_resolution_section_contains_character(self):
        """Test that resolution mentions character."""
        result = self.builder.build()
        resolution = result["sections"]["resolution"].lower()
        
        self.assertIn("elif", resolution)
    
    def test_message_section_not_empty(self):
        """Test that builder handles empty IR safely."""
        empty_builder = SemanticNarrativeBuilder({})
        result = empty_builder.build()
        
        self.assertIsInstance(result, dict)
        self.assertIn("narrative", result)
        # Should not crash, but narrative may be sparse
    
    def test_no_evidence_safe(self):
        """Test that builder works without evidence snippets."""
        ir_no_evidence = {
            "title": "Test Book",
            "central_entities": ["Hero"],
            "themes": ["growth"],
            "places": ["Kingdom"],
            "key_events": ["Event 1", "Event 2"],
            "evidence_snippets": {}
        }
        builder = SemanticNarrativeBuilder(ir_no_evidence)
        result = builder.build()
        
        self.assertTrue(len(result["narrative"]) > 0)
    
    def test_character_resolver_integration(self):
        """Test that character resolver is used."""
        ir = {
            "title": "Story",
            "central_entities": ["Hero"],
            "places": ["Kingdom"],
            "key_events": [],
            "evidence_snippets": {},
        }
        builder = SemanticNarrativeBuilder(ir)
        result = builder.build()
        
        # Character resolver should identify "Hero" as character, not place/title
        self.assertIn("hero", result["narrative"].lower())
    
    def test_evidence_synthesizer_integration(self):
        """Test that evidence synthesizer removes markers."""
        ir = {
            "title": "Story",
            "central_entities": ["Hero"],
            "themes": ["courage"],
            "places": [],
            "key_events": [],
            "evidence_snippets": {
                "conflict": ["For example, the hero faced danger."]
            }
        }
        builder = SemanticNarrativeBuilder(ir)
        result = builder.build()
        
        # "For example" should be removed
        self.assertNotIn("For example", result["narrative"])
    
    def test_section_order_preserved(self):
        """Test that sections appear in correct order in full narrative."""
        result = self.builder.build()
        narrative = result["narrative"]
        
        # This is harder to test precisely, but we can verify setup comes first
        setup = result["sections"]["setup"]
        conflict = result["sections"]["conflict"]
        
        if setup and conflict:
            setup_idx = narrative.find(setup) if setup in narrative else 0
            conflict_idx = narrative.find(conflict) if conflict in narrative else 0
            # If both present, setup should come before conflict
            if setup_idx >= 0 and conflict_idx >= 0:
                self.assertLess(setup_idx, conflict_idx)


if __name__ == "__main__":
    unittest.main()
