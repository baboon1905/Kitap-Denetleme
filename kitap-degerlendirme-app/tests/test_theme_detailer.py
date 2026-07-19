import unittest
from runtime_v7.theme_detailer import ThemeDetailer


class TestThemeDetailer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.detailer = ThemeDetailer()
        self.key_events = [
            "Elif decides to climb the mountain alone",
            "She faces a terrible storm despite her fear",
            "She helps her friend escape from danger",
            "They return home together",
        ]
        self.characters = ["Elif", "Dede", "Friend"]
    
    def test_detail_theme_returns_dict(self):
        """Test that detail_theme returns proper structure."""
        result = self.detailer.detail_theme("courage", self.key_events, self.characters)
        
        self.assertIsInstance(result, dict)
        self.assertIn("theme", result)
        self.assertIn("definition", result)
        self.assertIn("explanation", result)
    
    def test_known_theme_has_definition(self):
        """Test that known themes have proper definitions."""
        for theme in ["courage", "friendship", "growth", "perseverance", "kindness"]:
            result = self.detailer.detail_theme(theme, self.key_events)
            
            self.assertTrue(len(result["definition"]) > 0)
            self.assertNotEqual(result["definition"], "")
    
    def test_explanation_contains_theme_name(self):
        """Test that explanation mentions the theme."""
        result = self.detailer.detail_theme("courage", self.key_events)
        
        self.assertIn("courage", result["explanation"].lower())
    
    def test_supporting_instances_extracted(self):
        """Test that supporting instances are found."""
        result = self.detailer.detail_theme("courage", self.key_events)
        
        self.assertIsInstance(result["supporting_instances"], list)
        # Should find at least one instance
        self.assertGreater(len(result["supporting_instances"]), 0)
    
    def test_courage_theme_finds_events(self):
        """Test that courage theme finds relevant events."""
        events = [
            "She faced her fear bravely",
            "She climbed alone despite danger",
            "She persevered through the storm",
        ]
        result = self.detailer.detail_theme("courage", events)
        
        # Should find multiple supporting instances
        self.assertGreater(len(result["supporting_instances"]), 1)
    
    def test_friendship_theme_finds_cooperative_events(self):
        """Test that friendship theme finds cooperative events."""
        events = [
            "They worked together to escape",
            "She helped her friend without hesitation",
            "They trusted each other completely",
        ]
        result = self.detailer.detail_theme("friendship", events)
        
        self.assertGreater(len(result["supporting_instances"]), 0)
    
    def test_character_roles_identified(self):
        """Test that character roles are identified."""
        result = self.detailer.detail_theme("courage", self.key_events, self.characters)
        
        self.assertIsInstance(result["character_roles"], list)
        self.assertGreater(len(result["character_roles"]), 0)
    
    def test_primary_character_listed(self):
        """Test that primary character is listed in roles."""
        result = self.detailer.detail_theme("courage", self.key_events, ["Hero", "Villain"])
        
        roles_str = str(result["character_roles"]).lower()
        self.assertIn("hero", roles_str)
    
    def test_word_count_accurate(self):
        """Test that word count is accurate."""
        result = self.detailer.detail_theme("courage", self.key_events)
        
        actual_words = len(result["explanation"].split())
        self.assertEqual(result["word_count"], actual_words)
    
    def test_depth_score_between_zero_and_one(self):
        """Test that depth score is between 0.0 and 1.0."""
        result = self.detailer.detail_theme("courage", self.key_events)
        
        self.assertGreaterEqual(result["depth_score"], 0.0)
        self.assertLessEqual(result["depth_score"], 1.0)
    
    def test_more_instances_increase_depth_score(self):
        """Test that more instances lead to higher depth score."""
        # Few events
        result1 = self.detailer.detail_theme("courage", ["Event"])
        
        # Many events
        result2 = self.detailer.detail_theme("courage", [
            "Event 1 demonstrates courage",
            "Event 2 shows bravely",
            "Event 3 defies fear",
            "Event 4 persists despite danger",
        ])
        
        self.assertLessEqual(result1["depth_score"], result2["depth_score"])
    
    def test_detail_multiple_themes(self):
        """Test detailing multiple themes at once."""
        themes = ["courage", "friendship"]
        results = self.detailer.detail_multiple_themes(themes, self.key_events, self.characters)
        
        self.assertEqual(len(results), 2)
        self.assertTrue(all("theme" in r for r in results))
    
    def test_create_theme_summary_single_theme(self):
        """Test creating summary with single theme."""
        detailed = [
            {"explanation": "Courage is shown through the hero's actions."}
        ]
        summary = self.detailer.create_theme_summary(detailed)
        
        self.assertIn("Courage", summary)
    
    def test_create_theme_summary_multiple_themes(self):
        """Test creating summary with multiple themes."""
        detailed = [
            {"explanation": "Courage is shown through bravery."},
            {"explanation": "Friendship is shown through cooperation."},
        ]
        summary = self.detailer.create_theme_summary(detailed)
        
        self.assertIn("Courage", summary)
        self.assertIn("Friendship", summary)
    
    def test_theme_summary_uses_connectors(self):
        """Test that theme summary uses connectors between themes."""
        detailed = [
            {"explanation": "Theme 1 is shown."},
            {"explanation": "Theme 2 is shown."},
        ]
        summary = self.detailer.create_theme_summary(detailed)
        
        # Should contain a connector
        connectors = ["Additionally", "Furthermore", "In parallel", "Moreover"]
        has_connector = any(conn in summary for conn in connectors)
        self.assertTrue(has_connector)
    
    def test_validate_valid_theme_detail(self):
        """Test validation of valid theme detail."""
        valid_detail = {
            "theme": "courage",
            "definition": "Strength to face fear and challenge",
            "explanation": "The hero shows courage when facing the dragon alone and when speaking truth to power.",
            "supporting_instances": ["Faces dragon", "Speaks truth"],
            "character_roles": ["Hero: demonstrates courage"],
            "word_count": 15,
            "depth_score": 0.7,
        }
        result = self.detailer.validate_detail(valid_detail)
        
        # Should be valid as it has all required fields and sufficient content
        self.assertTrue(result["valid"], f"Validation failed: {result['issues']}")
    
    def test_validate_missing_field(self):
        """Test validation catches missing fields."""
        invalid_detail = {
            "theme": "courage",
            # Missing definition and explanation
            "explanation": "Something",
        }
        result = self.detailer.validate_detail(invalid_detail)
        
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["issues"]), 0)
    
    def test_validate_short_explanation(self):
        """Test validation catches short explanations."""
        invalid_detail = {
            "theme": "courage",
            "definition": "Bravery",
            "explanation": "Hero",  # Too short
            "supporting_instances": ["Event 1"],
        }
        result = self.detailer.validate_detail(invalid_detail)
        
        self.assertFalse(result["valid"])
        self.assertTrue(any("short" in issue.lower() for issue in result["issues"]))
    
    def test_unknown_theme_gets_generic_definition(self):
        """Test that unknown themes get generic definitions."""
        result = self.detailer.detail_theme("obscure_theme", self.key_events)
        
        self.assertIn("obscure_theme", result["definition"].lower())
    
    def test_deterministic_output(self):
        """Test that same inputs produce same output."""
        result1 = self.detailer.detail_theme("courage", self.key_events, self.characters)
        result2 = self.detailer.detail_theme("courage", self.key_events, self.characters)
        
        self.assertEqual(result1, result2)


if __name__ == "__main__":
    unittest.main()
