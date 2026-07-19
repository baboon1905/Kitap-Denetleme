import unittest
from runtime_v7.evidence_synthesizer import EvidenceSynthesizer


class TestEvidenceSynthesizer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.synthesizer = EvidenceSynthesizer()
    
    def test_remove_evidence_markers(self):
        """Test removal of technical evidence markers."""
        text = "For example, she faced a storm."
        result = self.synthesizer.synthesize(text)
        
        self.assertNotIn("For example", result)
        self.assertIn("she faced", result.lower())
    
    def test_remove_according_to_marker(self):
        """Test removal of 'According to' marker."""
        text = "According to the text, it was powerful."
        result = self.synthesizer.synthesize(text)
        
        self.assertNotIn("According to", result)
        self.assertNotIn("the text", result)
    
    def test_amplify_concrete_term_storm(self):
        """Test amplification of 'storm' concrete term."""
        text = "For example, she faced a storm."
        result = self.synthesizer.synthesize(text)
        
        # Should amplify "storm" to "powerful storm that threatened her survival"
        self.assertIn("powerful", result.lower())
        self.assertIn("survival", result.lower())
    
    def test_amplify_concrete_term_mountain(self):
        """Test amplification of 'mountain' concrete term."""
        text = "According to the story, the mountain was tall."
        result = self.synthesizer.synthesize(text)
        
        self.assertIn("towering", result.lower())
    
    def test_normalize_capitalization(self):
        """Test that first letter is capitalized."""
        text = "for example, she was brave."
        result = self.synthesizer.synthesize(text)
        
        self.assertTrue(result[0].isupper())
    
    def test_ensure_end_punctuation(self):
        """Test that sentence ends with punctuation."""
        text = "she faced a challenge"
        result = self.synthesizer.synthesize(text)
        
        self.assertTrue(result.endswith((".", "!", "?")))
    
    def test_positive_sentiment_enhancement(self):
        """Test addition of positive sentiment context."""
        text = "she succeeded"
        result = self.synthesizer.synthesize(text, sentiment="positive")
        
        # Should add positive enhancer
        self.assertTrue(any(phrase in result.lower() for phrase in 
                           ["joy", "happiness", "triumph", "relief", "gratitude"]))
    
    def test_negative_sentiment_enhancement(self):
        """Test addition of negative sentiment context."""
        text = "she failed"
        result = self.synthesizer.synthesize(text, sentiment="negative")
        
        # Should add negative enhancer
        self.assertTrue(any(phrase in result.lower() for phrase in 
                           ["sorrow", "desperation", "heavy", "fears"]))
    
    def test_remove_parenthetical_references(self):
        """Test removal of parenthetical story references."""
        text = "She was brave (as the story shows) and determined."
        result = self.synthesizer.synthesize(text)
        
        self.assertNotIn("(", result)
        self.assertNotIn(")", result)
    
    def test_batch_synthesis(self):
        """Test synthesizing multiple snippets."""
        snippets = [
            {"text": "For example, she faced a storm.", "sentiment": "negative"},
            {"text": "According to the text, they worked together.", "sentiment": "positive"},
        ]
        results = self.synthesizer.synthesize_batch(snippets)
        
        self.assertEqual(len(results), 2)
        self.assertTrue(all(isinstance(r, str) for r in results))
        self.assertTrue(all(len(r) > 0 for r in results))
    
    def test_empty_input(self):
        """Test handling of empty input."""
        result = self.synthesizer.synthesize("")
        self.assertEqual(result, "")
    
    def test_none_input(self):
        """Test handling of None input."""
        result = self.synthesizer.synthesize(None)
        self.assertEqual(result, "")
    
    def test_deterministic_output(self):
        """Test that same input produces same output."""
        text = "For example, she climbed the mountain."
        result1 = self.synthesizer.synthesize(text)
        result2 = self.synthesizer.synthesize(text)
        
        self.assertEqual(result1, result2)
    
    def test_merge_evidence_into_narrative(self):
        """Test merging evidence into narrative."""
        narrative = "She faced many challenges."
        evidence = ["For example, the storm was fierce.", "The mountain was tall."]
        
        result = self.synthesizer.merge_evidence_into_narrative(narrative, evidence)
        
        # Should contain either "narrative" or "challenge"
        self.assertTrue("challenge" in result.lower() or "narrative" in result.lower())
        # Evidence should be synthesized and present
        self.assertIn("powerful", result.lower())
    
    def test_validate_synthesis_success(self):
        """Test validation of successful synthesis."""
        original = "For example, she faced a storm."
        synthesized = "She faced a powerful storm."
        
        validation = self.synthesizer.validate_synthesis(original, synthesized)
        
        self.assertTrue(validation["valid"])
        self.assertEqual(len(validation["issues"]), 0)
    
    def test_validate_synthesis_with_remaining_marker(self):
        """Test validation catches remaining markers."""
        original = "For example, she was brave."
        synthesized = "For example, she was very brave."  # Marker still present
        
        validation = self.synthesizer.validate_synthesis(original, synthesized)
        
        self.assertFalse(validation["valid"])
        self.assertGreater(len(validation["issues"]), 0)
    
    def test_multiple_marker_removal(self):
        """Test removal of multiple markers in sequence."""
        text = ("For example, the hero was strong. According to the text, "
               "he faced a challenge. In the story, he succeeded.")
        result = self.synthesizer.synthesize(text)
        
        # Check multiple markers removed
        self.assertNotIn("For example", result)
        self.assertNotIn("According to", result)
        self.assertNotIn("In the story", result)
    
    def test_whitespace_normalization(self):
        """Test that extra whitespace is normalized."""
        text = "For example,  she    faced   a   storm."
        result = self.synthesizer.synthesize(text)
        
        # Check for excessive spaces
        self.assertNotIn("  ", result)  # No double spaces
    
    def test_no_over_amplification(self):
        """Test that concrete terms aren't amplified multiple times."""
        text = "The storm was fierce. Another storm came. And another storm."
        result = self.synthesizer.synthesize(text)
        
        # Count "powerful storm" occurrences - should be at most 1
        count = result.lower().count("powerful storm")
        self.assertLessEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
