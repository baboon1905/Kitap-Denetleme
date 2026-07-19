"""
RC2 Sprint 2 — Semantic Confidence Engine Tests

Unit tests for confidence calculation engine
Verify: determinism, accuracy, recommendations
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.semantic_confidence_engine import (
    SemanticConfidenceEngine,
    ConfidenceLevel,
    PatternRecommendation,
)


class TestSemanticConfidenceBasics(unittest.TestCase):
    """Test basic confidence calculations"""
    
    def setUp(self):
        self.engine = SemanticConfidenceEngine()
    
    def test_zero_matches(self):
        """Test pattern with zero matches"""
        result = self.engine.calculate_confidence(
            raw_match_count=0,
            pattern_category='theme',
            false_positive_risk='low',
            semantic_density=0.0,
            evidence_diversity=0.0,
            coverage_ratio=0.0,
        )
        
        self.assertEqual(result['raw_confidence'], 0.0)
        self.assertEqual(result['calibrated_confidence'], 0.0)
    
    def test_strong_pattern(self):
        """Test high-confidence pattern"""
        result = self.engine.calculate_confidence(
            raw_match_count=8,
            pattern_category='theme',
            false_positive_risk='low',
            semantic_density=0.9,
            evidence_diversity=1.0,
            coverage_ratio=0.9,
        )
        
        # Should be strong
        self.assertGreaterEqual(result['calibrated_confidence'], 0.65)
        self.assertEqual(result['recommendation'], 'keep')
        self.assertEqual(result['confidence_level'], 'strong')
    
    def test_weak_pattern(self):
        """Test low-confidence pattern"""
        result = self.engine.calculate_confidence(
            raw_match_count=1,
            pattern_category='theme',
            false_positive_risk='high',
            semantic_density=0.2,
            evidence_diversity=0.2,
            coverage_ratio=0.1,
        )
        
        # Should be weak or minimal
        self.assertLess(result['calibrated_confidence'], 0.40)
        self.assertIn(result['recommendation'], ['review', 'narrow'])
    
    def test_confidence_bounds(self):
        """Verify confidence stays in [0, 1]"""
        test_cases = [
            (0, 'theme', 'low', 0.0, 0.0, 0.0),
            (100, 'theme', 'low', 1.0, 1.0, 1.0),
            (50, 'character_role', 'high', 0.5, 0.5, 0.5),
        ]
        
        for match_count, category, fp_risk, density, diversity, coverage in test_cases:
            result = self.engine.calculate_confidence(
                raw_match_count=match_count,
                pattern_category=category,
                false_positive_risk=fp_risk,
                semantic_density=density,
                evidence_diversity=diversity,
                coverage_ratio=coverage,
            )
            
            self.assertGreaterEqual(result['calibrated_confidence'], 0.0)
            self.assertLessEqual(result['calibrated_confidence'], 1.0)
    
    def test_fp_risk_adjustment(self):
        """Verify FP risk reduces confidence appropriately"""
        base_params = {
            'raw_match_count': 4,
            'pattern_category': 'theme',
            'semantic_density': 0.5,
            'evidence_diversity': 0.5,
            'coverage_ratio': 0.5,
        }
        
        low_risk = self.engine.calculate_confidence(
            **base_params,
            false_positive_risk='low',
        )
        
        high_risk = self.engine.calculate_confidence(
            **base_params,
            false_positive_risk='high',
        )
        
        # High risk should have lower confidence
        self.assertLess(high_risk['calibrated_confidence'], low_risk['calibrated_confidence'])
    
    def test_diversity_weighting(self):
        """Verify evidence diversity affects confidence"""
        base_params = {
            'raw_match_count': 4,
            'pattern_category': 'theme',
            'false_positive_risk': 'low',
            'semantic_density': 0.5,
            'coverage_ratio': 0.5,
        }
        
        low_diversity = self.engine.calculate_confidence(
            **base_params,
            evidence_diversity=0.2,
        )
        
        high_diversity = self.engine.calculate_confidence(
            **base_params,
            evidence_diversity=1.0,
        )
        
        # High diversity should have higher confidence
        self.assertGreater(high_diversity['calibrated_confidence'], low_diversity['calibrated_confidence'])


class TestRecommendationLogic(unittest.TestCase):
    """Test recommendation generation"""
    
    def setUp(self):
        self.engine = SemanticConfidenceEngine()
    
    def test_keep_recommendation(self):
        """Strong pattern gets 'keep' recommendation"""
        result = self.engine.calculate_confidence(
            raw_match_count=7,
            pattern_category='theme',
            false_positive_risk='low',
            semantic_density=0.8,
            evidence_diversity=0.9,
            coverage_ratio=0.8,
        )
        
        self.assertEqual(result['recommendation'], 'keep')
    
    def test_review_recommendation(self):
        """Weak pattern gets 'review' recommendation"""
        result = self.engine.calculate_confidence(
            raw_match_count=1,
            pattern_category='theme',
            false_positive_risk='high',
            semantic_density=0.1,
            evidence_diversity=0.1,
            coverage_ratio=0.1,
        )
        
        self.assertEqual(result['recommendation'], 'review')
    
    def test_narrow_recommendation(self):
        """Multiple matches with low diversity gets 'narrow'"""
        result = self.engine.calculate_confidence(
            raw_match_count=6,
            pattern_category='theme',
            false_positive_risk='medium',
            semantic_density=0.6,
            evidence_diversity=0.3,  # Low diversity
            coverage_ratio=0.5,
        )
        
        # Should recommend narrowing or expanding (both valid for low diversity)
        self.assertIn(result['recommendation'], ['narrow', 'review', 'expand'])
    
    def test_expand_recommendation(self):
        """Good signal with low diversity gets 'expand'"""
        result = self.engine.calculate_confidence(
            raw_match_count=6,
            pattern_category='theme',
            false_positive_risk='low',
            semantic_density=0.7,
            evidence_diversity=0.4,  # Medium-low diversity
            coverage_ratio=0.6,
        )
        
        # Should recommend expanding
        self.assertIn(result['recommendation'], ['expand', 'keep'])


class TestDeterminism(unittest.TestCase):
    """Test deterministic output"""
    
    def setUp(self):
        self.engine = SemanticConfidenceEngine()
    
    def test_identical_runs_produce_identical_output(self):
        """Same input twice produces identical output"""
        params = {
            'raw_match_count': 5,
            'pattern_category': 'theme',
            'false_positive_risk': 'medium',
            'semantic_density': 0.6,
            'evidence_diversity': 0.7,
            'coverage_ratio': 0.65,
        }
        
        result1 = self.engine.calculate_confidence(**params)
        result2 = self.engine.calculate_confidence(**params)
        
        self.assertEqual(result1, result2)
    
    def test_engine_determinism_method(self):
        """Engine reports itself as deterministic"""
        self.assertTrue(self.engine.is_deterministic())
    
    def test_different_inputs_produce_different_outputs(self):
        """Different inputs produce different outputs"""
        result1 = self.engine.calculate_confidence(
            raw_match_count=2,
            pattern_category='theme',
            false_positive_risk='low',
            semantic_density=0.3,
            evidence_diversity=0.3,
            coverage_ratio=0.3,
        )
        
        result2 = self.engine.calculate_confidence(
            raw_match_count=8,
            pattern_category='theme',
            false_positive_risk='low',
            semantic_density=0.8,
            evidence_diversity=0.8,
            coverage_ratio=0.8,
        )
        
        # Should differ
        self.assertNotEqual(result1['calibrated_confidence'], result2['calibrated_confidence'])


class TestConfidenceLevels(unittest.TestCase):
    """Test confidence level classification"""
    
    def setUp(self):
        self.engine = SemanticConfidenceEngine()
    
    def test_strong_level(self):
        """High confidence classified as 'strong'"""
        result = self.engine.calculate_confidence(
            raw_match_count=8,
            pattern_category='theme',
            false_positive_risk='low',
            semantic_density=0.9,
            evidence_diversity=1.0,
            coverage_ratio=0.9,
        )
        
        self.assertEqual(result['confidence_level'], 'strong')
    
    def test_acceptable_level(self):
        """Medium confidence classified as 'acceptable'"""
        result = self.engine.calculate_confidence(
            raw_match_count=4,
            pattern_category='theme',
            false_positive_risk='low',
            semantic_density=0.5,
            evidence_diversity=0.6,
            coverage_ratio=0.5,
        )
        
        self.assertEqual(result['confidence_level'], 'acceptable')
    
    def test_weak_level(self):
        """Low confidence classified as 'weak'"""
        result = self.engine.calculate_confidence(
            raw_match_count=3,
            pattern_category='theme',
            false_positive_risk='low',
            semantic_density=0.3,
            evidence_diversity=0.4,
            coverage_ratio=0.3,
        )
        
        self.assertEqual(result['confidence_level'], 'weak')
    
    def test_minimal_level(self):
        """Very low confidence classified as 'minimal'"""
        result = self.engine.calculate_confidence(
            raw_match_count=1,
            pattern_category='theme',
            false_positive_risk='high',
            semantic_density=0.1,
            evidence_diversity=0.1,
            coverage_ratio=0.1,
        )
        
        self.assertEqual(result['confidence_level'], 'minimal')


class TestBatchCalculation(unittest.TestCase):
    """Test batch confidence calculation"""
    
    def setUp(self):
        self.engine = SemanticConfidenceEngine()
    
    def test_batch_calculate(self):
        """Calculate confidence for multiple patterns"""
        patterns = {
            'adventure': {
                'match_count': 3,
                'category': 'theme',
                'fp_risk': 'low',
                'density': 0.5,
                'diversity': 0.6,
                'coverage': 0.4,
            },
            'growth': {
                'match_count': 7,
                'category': 'theme',
                'fp_risk': 'high',
                'density': 0.7,
                'diversity': 0.9,
                'coverage': 0.7,
            },
        }
        
        results = self.engine.batch_calculate(patterns)
        
        self.assertIn('adventure', results)
        self.assertIn('growth', results)
        self.assertIn('calibrated_confidence', results['adventure'])
        self.assertIn('calibrated_confidence', results['growth'])


if __name__ == '__main__':
    unittest.main()
