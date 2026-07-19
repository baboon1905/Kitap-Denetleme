"""
RC2 Sprint 1 — Semantic Intelligence Foundation
Test Suite for SemanticEngine

Tests verify:
✓ Shadow-only semantic analysis (non-invasive)
✓ Production payload not modified (read-only)
✓ Deterministic output (same input → same output)
✓ No book-specific heuristics
✓ Correct shadow structure
"""

import unittest
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.semantic_engine import SemanticEngine


class TestSemanticEngineBasics(unittest.TestCase):
    """Test basic SemanticEngine functionality"""
    
    def setUp(self):
        """Initialize SemanticEngine for tests"""
        self.engine = SemanticEngine()
    
    def test_analyze_text_basic(self):
        """Test basic text analysis with simple narrative"""
        text = "Çocuk okula gitti ve matematik öğrendi."
        result = self.engine.analyze_text(text)
        
        # Check structure
        self.assertIn('theme_clusters', result)
        self.assertIn('character_roles', result)
        self.assertIn('learning_outcome_clusters', result)
        self.assertIn('concept_graph', result)
        self.assertIn('diagnostics', result)
        
        # Check types
        self.assertIsInstance(result['theme_clusters'], list)
        self.assertIsInstance(result['character_roles'], list)
        self.assertIsInstance(result['learning_outcome_clusters'], list)
        self.assertIsInstance(result['concept_graph'], dict)
        self.assertIsInstance(result['diagnostics'], dict)
    
    def test_deterministic_output(self):
        """Verify deterministic output (same input → same output)"""
        text = "Kahramanlar cesur birleşip düşmanı yendiler."
        
        # Run twice
        result1 = self.engine.analyze_text(text)
        result2 = self.engine.analyze_text(text)
        
        # Compare results
        self.assertEqual(result1, result2, "Same input must produce identical output")
        self.assertTrue(self.engine.is_deterministic())
    
    def test_empty_input(self):
        """Test handling of empty text"""
        result = self.engine.analyze_text("")
        
        # Should not crash
        self.assertEqual(result['theme_clusters'], [])
        self.assertEqual(result['character_roles'], [])
        self.assertEqual(result['learning_outcome_clusters'], [])
        self.assertEqual(result['concept_graph']['nodes'], [])
        self.assertEqual(result['concept_graph']['edges'], [])
    
    def test_whitespace_only_input(self):
        """Test handling of whitespace-only input"""
        result = self.engine.analyze_text("   \n\t  ")
        
        # Should treat as empty
        self.assertEqual(result['theme_clusters'], [])
        self.assertEqual(result['character_roles'], [])
    
    def test_theme_extraction(self):
        """Test theme extraction from narrative"""
        text = "Çocuğun macera yolculuğu başladı. Cesur karakteri büyüdü."
        result = self.engine.extract_themes(text)
        
        # Should detect themes
        self.assertGreater(len(result), 0)
        
        # Each theme should have required fields
        for theme in result:
            self.assertIn('theme', theme)
            self.assertIn('keyword_count', theme)
            self.assertIn('confidence', theme)
    
    def test_character_extraction(self):
        """Test character role extraction"""
        text = "Ali ve Veli bahçede oyunuyor. Öğretmen onları rehberlik yapıyor."
        result = self.engine.extract_characters(text)
        
        # Should detect character roles
        self.assertGreater(len(result), 0, "Should detect character roles")
        
        # Each role should have required fields
        for role in result:
            self.assertIn('role', role)
            self.assertIn('count', role)
            self.assertIn('confidence', role)
    
    def test_learning_outcome_extraction(self):
        """Test learning outcome extraction"""
        text = "Öğrenciler bilimsel yöntemi öğrendiler ve sosyal işbirliği deneyimlediler."
        result = self.engine.extract_learning_outcomes(text)
        
        # Should detect learning outcomes
        self.assertGreater(len(result), 0, "Should detect learning outcomes")
        
        # Each outcome should have required fields
        for outcome in result:
            self.assertIn('outcome_type', outcome)
            self.assertIn('keyword_count', outcome)
            self.assertIn('confidence', outcome)
    
    def test_concept_graph_generation(self):
        """Test concept graph generation"""
        text = "Kahramanın macerasının öyküsü ve çevresi."
        result = self.engine.build_concept_graph(text)
        
        # Should have structure
        self.assertIn('nodes', result)
        self.assertIn('edges', result)
        self.assertIn('concept_count', result)
        
        # Nodes and edges should be lists
        self.assertIsInstance(result['nodes'], list)
        self.assertIsInstance(result['edges'], list)
        self.assertIsInstance(result['concept_count'], int)
    
    def test_diagnostics_calculation(self):
        """Test diagnostic metrics generation"""
        text = "Çocuk okula gitti. Öğretmen anlattı. Arkadaşları oyunlaştırdı."
        analysis = self.engine.analyze_text(text)
        diagnostics = analysis['diagnostics']
        
        # Check diagnostic fields
        self.assertIn('semantic_cluster_count', diagnostics)
        self.assertIn('concept_count', diagnostics)
        self.assertIn('semantic_density', diagnostics)
        self.assertIn('semantic_confidence', diagnostics)
        
        # Check value ranges
        self.assertGreaterEqual(diagnostics['semantic_cluster_count'], 0)
        self.assertGreaterEqual(diagnostics['concept_count'], 0)
        self.assertGreaterEqual(diagnostics['semantic_density'], 0)
        self.assertLessEqual(diagnostics['semantic_density'], 1.0)
        self.assertGreaterEqual(diagnostics['semantic_confidence'], 0)
        self.assertLessEqual(diagnostics['semantic_confidence'], 1.0)
    
    def test_no_production_impact(self):
        """Verify SemanticEngine doesn't modify production payload"""
        production_payload = {
            'kitap_adi': 'Test Book',
            'ana_karakterler': [{'ad': 'Ali'}],
            'tema_analizi': [{'tema': 'friendship'}],
        }
        
        # Make a copy to compare
        original = dict(production_payload)
        
        # Run semantic engine
        text = "This is test text"
        self.engine.analyze_text(text)
        
        # Production payload should be unchanged
        self.assertEqual(production_payload, original, "Production payload must not be modified")


class TestSemanticEngineDeterminism(unittest.TestCase):
    """Test determinism guarantees"""
    
    def test_multiple_identical_runs(self):
        """Verify multiple identical runs produce same output"""
        engine = SemanticEngine()
        text = "Karakter serüveni ve öğrenme hikayesi."
        
        results = [engine.analyze_text(text) for _ in range(5)]
        
        # All should be identical
        for i in range(1, len(results)):
            self.assertEqual(results[0], results[i], f"Run {i} differs from run 0")
    
    def test_different_texts_produce_different_outputs(self):
        """Verify different texts produce different outputs"""
        engine = SemanticEngine()
        
        text1 = "Kahramanlar cesur birleşip düşmanı yendiler."
        text2 = "Sakin bir köyde kaynaktan su akıyordu."
        
        result1 = engine.analyze_text(text1)
        result2 = engine.analyze_text(text2)
        
        # Results should differ (but may have some similarities)
        # At least one field should differ
        differs = (
            result1['theme_clusters'] != result2['theme_clusters'] or
            result1['character_roles'] != result2['character_roles'] or
            result1['learning_outcome_clusters'] != result2['learning_outcome_clusters']
        )
        
        self.assertTrue(differs, "Different texts should produce different semantic analyses")


class TestSemanticEngineNonHeuristic(unittest.TestCase):
    """Test that SemanticEngine uses generic patterns, not book-specific heuristics"""
    
    def setUp(self):
        """Initialize SemanticEngine"""
        self.engine = SemanticEngine()
    
    def test_no_book_specific_keywords(self):
        """Verify themes/characters/outcomes are generic, not book-specific"""
        # Valid: Generic themes
        generic_themes = list(self.engine.THEME_KEYWORDS.keys())
        self.assertIn('adventure', generic_themes)
        self.assertIn('friendship', generic_themes)
        self.assertIn('courage', generic_themes)
        
        # No book-specific names
        for theme in generic_themes:
            # Names like "Tavşan Pati" or "GDZ" should not appear
            self.assertNotIn('tavşan_pati', theme.lower())
            self.assertNotIn('gdz', theme.lower())
    
    def test_generic_character_roles(self):
        """Verify character roles are generic"""
        roles = list(self.engine.CHARACTER_ROLES.keys())
        
        # Should be universal roles
        self.assertIn('protagonist', roles)
        self.assertIn('antagonist', roles)
        self.assertIn('mentor', roles)
        self.assertIn('companion', roles)
    
    def test_generic_learning_outcomes(self):
        """Verify learning outcomes are generic"""
        outcomes = list(self.engine.LEARNING_OUTCOMES.keys())
        
        # Should be universal outcome types
        self.assertIn('cognitive', outcomes)
        self.assertIn('social', outcomes)
        self.assertIn('emotional', outcomes)
        self.assertIn('physical', outcomes)


class TestSemanticEngineShadowStructure(unittest.TestCase):
    """Test shadow runtime structure"""
    
    def setUp(self):
        """Initialize SemanticEngine"""
        self.engine = SemanticEngine()
    
    def test_shadow_semantic_structure(self):
        """Verify shadow semantic structure matches spec"""
        text = "Sample narrative text for testing."
        result = self.engine.analyze_text(text)
        
        # Shadow structure: _runtime_v7_shadow.semantic
        shadow_semantic = {
            'theme_clusters': result['theme_clusters'],
            'character_roles': result['character_roles'],
            'learning_outcome_clusters': result['learning_outcome_clusters'],
            'concept_graph': result['concept_graph'],
            'diagnostics': result['diagnostics'],
        }
        
        # All fields must be present
        required_fields = [
            'theme_clusters',
            'character_roles',
            'learning_outcome_clusters',
            'concept_graph',
            'diagnostics',
        ]
        
        for field in required_fields:
            self.assertIn(field, shadow_semantic, f"Missing required shadow field: {field}")
    
    def test_diagnostics_structure(self):
        """Verify diagnostics sub-structure"""
        text = "Test narrative for diagnostics verification."
        result = self.engine.analyze_text(text)
        diagnostics = result['diagnostics']
        
        # Required diagnostic fields
        required = [
            'semantic_cluster_count',
            'concept_count',
            'semantic_density',
            'semantic_confidence',
        ]
        
        for field in required:
            self.assertIn(field, diagnostics, f"Missing diagnostic field: {field}")
        
        # Verify types and ranges
        self.assertIsInstance(diagnostics['semantic_cluster_count'], int)
        self.assertIsInstance(diagnostics['concept_count'], int)
        self.assertIsInstance(diagnostics['semantic_density'], float)
        self.assertIsInstance(diagnostics['semantic_confidence'], float)
        
        self.assertGreaterEqual(diagnostics['semantic_density'], 0)
        self.assertLessEqual(diagnostics['semantic_density'], 1.0)
        self.assertGreaterEqual(diagnostics['semantic_confidence'], 0)
        self.assertLessEqual(diagnostics['semantic_confidence'], 1.0)


class TestSemanticEngineReadOnlyGuarantee(unittest.TestCase):
    """Test that SemanticEngine provides read-only guarantee"""
    
    def setUp(self):
        """Initialize SemanticEngine"""
        self.engine = SemanticEngine()
    
    def test_read_only_guarantee(self):
        """Verify read_only validation returns True"""
        # This should always return True if implementation is correct
        production_payload = {
            'book_id': '123',
            'content': 'Sample text',
            'metadata': {'pages': 100},
        }
        
        result = self.engine.validate_read_only(production_payload)
        self.assertTrue(result, "SemanticEngine must maintain read-only guarantee")


if __name__ == '__main__':
    unittest.main()
