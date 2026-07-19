import unittest
from runtime_v7.character_resolver import CharacterResolver


class TestCharacterResolver(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.summary_ir = {
            "title": "Dağın Ötesi",
            "central_entities": ["Elif", "Dede", "Ağabeyi"],
            "places": ["köy", "dağ", "mağara"],
            "historical_figures": ["Atatürk"],
            "temporal_context": "modern"
        }
        self.resolver = CharacterResolver(self.summary_ir)
    
    def test_exact_character_match(self):
        """Test exact character matching."""
        result = self.resolver.resolve_entity("Elif")
        self.assertEqual(result["type"], "character")
        self.assertEqual(result["confidence"], 1.0)
        self.assertEqual(result["resolved_name"], "Elif")
    
    def test_exact_place_match(self):
        """Test exact place matching."""
        result = self.resolver.resolve_entity("köy")
        self.assertEqual(result["type"], "place")
        self.assertEqual(result["confidence"], 1.0)
        self.assertEqual(result["resolved_name"], "köy")
    
    def test_book_title_not_returned_as_character(self):
        """Test that book title is NOT treated as character."""
        result = self.resolver.resolve_entity("Dağın Ötesi")
        self.assertEqual(result["type"], "book_title")
        self.assertIsNone(result["resolved_name"])
    
    def test_historical_figure_match(self):
        """Test historical figure matching."""
        result = self.resolver.resolve_entity("Atatürk")
        self.assertEqual(result["type"], "historical_figure")
        self.assertEqual(result["confidence"], 1.0)
    
    def test_case_insensitive_matching(self):
        """Test that matching is case-insensitive."""
        result = self.resolver.resolve_entity("elif")
        self.assertEqual(result["type"], "character")
        self.assertEqual(result["resolved_name"], "Elif")
    
    def test_fuzzy_matching_characters(self):
        """Test fuzzy matching for characters with typos."""
        result = self.resolver.resolve_entity("Elif")  # exact, but test fuzzy with typo
        # "Elifin" vs "Elif" should match with high confidence
        result = self.resolver.resolve_entity("Elifin")
        self.assertEqual(result["type"], "character")
        self.assertGreaterEqual(result["confidence"], 0.7)
    
    def test_unknown_entity(self):
        """Test handling of unknown entities."""
        result = self.resolver.resolve_entity("Bilinmeyen Karakter")
        self.assertEqual(result["type"], "unknown")
        self.assertEqual(result["confidence"], 0.0)
    
    def test_resolve_multiple_entities(self):
        """Test resolving a list of entities."""
        entities = ["Elif", "köy", "Dağın Ötesi", "Atatürk"]
        results = self.resolver.resolve_entities(entities)
        
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]["type"], "character")
        self.assertEqual(results[1]["type"], "place")
        self.assertEqual(results[2]["type"], "book_title")
        self.assertEqual(results[3]["type"], "historical_figure")
    
    def test_get_characters_only(self):
        """Test filtering to get only characters."""
        entities = ["Elif", "köy", "Dede", "Dağın Ötesi"]
        characters = self.resolver.get_characters_only(entities)
        
        self.assertIn("Elif", characters)
        self.assertIn("Dede", characters)
        self.assertNotIn("köy", characters)
        self.assertNotIn("Dağın Ötesi", characters)
    
    def test_get_places_only(self):
        """Test filtering to get only places."""
        entities = ["Elif", "köy", "dağ", "Dağın Ötesi"]
        places = self.resolver.get_places_only(entities)
        
        self.assertIn("köy", places)
        self.assertIn("dağ", places)
        self.assertNotIn("Elif", places)
    
    def test_sanitize_removes_book_title(self):
        """Test that book title is removed from narrative text."""
        text = "In 'Dağın Ötesi', the hero meets a friend."
        sanitized = self.resolver.sanitize_for_narrative(text)
        
        self.assertNotIn("Dağın Ötesi", sanitized)
        self.assertIn("this story", sanitized)
    
    def test_resolver_without_ir(self):
        """Test resolver without summary IR context."""
        empty_resolver = CharacterResolver()
        result = empty_resolver.resolve_entity("Elif")
        
        # Should return unknown since no context
        self.assertEqual(result["type"], "unknown")
    
    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        result = self.resolver.resolve_entity("  Elif  ")
        self.assertEqual(result["type"], "character")
        self.assertEqual(result["resolved_name"], "Elif")
    
    def test_empty_entity(self):
        """Test handling of empty entity strings."""
        result = self.resolver.resolve_entity("")
        self.assertEqual(result["type"], "unknown")
        self.assertEqual(result["confidence"], 0.0)
    
    def test_none_entity(self):
        """Test handling of None entity."""
        result = self.resolver.resolve_entity(None)
        self.assertEqual(result["type"], "unknown")
        self.assertEqual(result["confidence"], 0.0)
    
    def test_deterministic_output(self):
        """Test that resolver produces deterministic output."""
        entities = ["Elif", "köy", "Dede"]
        
        result1 = self.resolver.resolve_entities(entities)
        result2 = self.resolver.resolve_entities(entities)
        
        self.assertEqual(result1, result2)
    
    def test_no_duplicate_characters(self):
        """Test that get_characters_only doesn't return duplicates."""
        entities = ["Elif", "Elif", "Dede", "Dede", "Elif"]
        characters = self.resolver.get_characters_only(entities)
        
        # Should not have duplicates
        self.assertEqual(len(characters), len(set(characters)))
        self.assertEqual(len(characters), 2)  # Elif and Dede


if __name__ == "__main__":
    unittest.main()
