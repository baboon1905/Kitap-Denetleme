"""
RC2 Sprint 2 — Shadow Confidence Determinism Verification

Verify that semantic confidence calculations are deterministic across:
- Multiple runs with identical inputs
- Different book combinations
- Varied pattern metrics
"""

import unittest
import sys
from pathlib import Path
import json
import hashlib

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.semantic_confidence_engine import SemanticConfidenceEngine


class TestShadowConfidenceDeterminism(unittest.TestCase):
    """Verify deterministic shadow confidence output"""
    
    def setUp(self):
        self.engine = SemanticConfidenceEngine()
    
    def test_identical_inputs_produce_identical_outputs(self):
        """Same input → same output (core determinism test)"""
        params = {
            'raw_match_count': 5,
            'pattern_category': 'theme',
            'false_positive_risk': 'medium',
            'semantic_density': 0.6,
            'evidence_diversity': 0.75,
            'coverage_ratio': 0.65,
        }
        
        # Run 5 times
        results = [self.engine.calculate_confidence(**params) for _ in range(5)]
        
        # All should be identical
        for i in range(1, 5):
            self.assertEqual(results[0], results[i], f"Run {i} differs from run 0")
    
    def test_determinism_across_all_fp_risk_levels(self):
        """Each FP risk level is deterministic"""
        for fp_risk in ['low', 'medium', 'high']:
            params = {
                'raw_match_count': 4,
                'pattern_category': 'theme',
                'false_positive_risk': fp_risk,
                'semantic_density': 0.5,
                'evidence_diversity': 0.5,
                'coverage_ratio': 0.5,
            }
            
            result1 = self.engine.calculate_confidence(**params)
            result2 = self.engine.calculate_confidence(**params)
            
            self.assertEqual(result1, result2, f"Not deterministic for {fp_risk} risk")
    
    def test_determinism_across_all_categories(self):
        """Each pattern category is deterministic"""
        for category in ['theme', 'character_role', 'learning_outcome']:
            params = {
                'raw_match_count': 4,
                'pattern_category': category,
                'false_positive_risk': 'low',
                'semantic_density': 0.5,
                'evidence_diversity': 0.5,
                'coverage_ratio': 0.5,
            }
            
            result1 = self.engine.calculate_confidence(**params)
            result2 = self.engine.calculate_confidence(**params)
            
            self.assertEqual(result1, result2, f"Not deterministic for {category}")
    
    def test_output_hash_consistency(self):
        """Hash of output is deterministic"""
        params = {
            'raw_match_count': 5,
            'pattern_category': 'theme',
            'false_positive_risk': 'medium',
            'semantic_density': 0.6,
            'evidence_diversity': 0.75,
            'coverage_ratio': 0.65,
        }
        
        # Calculate 3 times and hash output
        hashes = []
        for _ in range(3):
            result = self.engine.calculate_confidence(**params)
            result_json = json.dumps(result, sort_keys=True)
            result_hash = hashlib.sha256(result_json.encode()).hexdigest()
            hashes.append(result_hash)
        
        # All hashes should be identical
        self.assertEqual(hashes[0], hashes[1])
        self.assertEqual(hashes[1], hashes[2])
    
    def test_batch_determinism(self):
        """Batch calculation is deterministic"""
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
                'match_count': 2,
                'category': 'theme',
                'fp_risk': 'high',
                'density': 0.4,
                'diversity': 0.3,
                'coverage': 0.3,
            },
            'protagonist': {
                'match_count': 4,
                'category': 'character_role',
                'fp_risk': 'low',
                'density': 0.6,
                'diversity': 0.7,
                'coverage': 0.5,
            },
        }
        
        results1 = self.engine.batch_calculate(patterns)
        results2 = self.engine.batch_calculate(patterns)
        results3 = self.engine.batch_calculate(patterns)
        
        self.assertEqual(results1, results2)
        self.assertEqual(results2, results3)
    
    def test_no_randomness_in_output(self):
        """Output contains no random elements"""
        params = {
            'raw_match_count': 6,
            'pattern_category': 'theme',
            'false_positive_risk': 'low',
            'semantic_density': 0.7,
            'evidence_diversity': 0.8,
            'coverage_ratio': 0.75,
        }
        
        # Collect 10 outputs
        outputs = []
        for _ in range(10):
            result = self.engine.calculate_confidence(**params)
            outputs.append(
                (
                    result['raw_confidence'],
                    result['calibrated_confidence'],
                    result['recommendation'],
                    result['confidence_level'],
                )
            )
        
        # First output
        first = outputs[0]
        
        # All should match first
        for i, output in enumerate(outputs[1:], 1):
            self.assertEqual(first, output, f"Output {i} differs from first")
    
    def test_edge_case_determinism(self):
        """Edge cases are deterministic"""
        edge_cases = [
            # Zero matches
            {
                'raw_match_count': 0,
                'pattern_category': 'theme',
                'false_positive_risk': 'low',
                'semantic_density': 0.0,
                'evidence_diversity': 0.0,
                'coverage_ratio': 0.0,
            },
            # Maximum values
            {
                'raw_match_count': 100,
                'pattern_category': 'theme',
                'false_positive_risk': 'low',
                'semantic_density': 1.0,
                'evidence_diversity': 1.0,
                'coverage_ratio': 1.0,
            },
            # Mixed values
            {
                'raw_match_count': 3,
                'pattern_category': 'character_role',
                'false_positive_risk': 'medium',
                'semantic_density': 0.333,
                'evidence_diversity': 0.667,
                'coverage_ratio': 0.5,
            },
        ]
        
        for case in edge_cases:
            result1 = self.engine.calculate_confidence(**case)
            result2 = self.engine.calculate_confidence(**case)
            self.assertEqual(result1, result2, f"Edge case not deterministic: {case}")
    
    def test_determinism_verification_method(self):
        """Engine's is_deterministic method works"""
        self.assertTrue(self.engine.is_deterministic())
        
        # Run 5 times to be sure
        for _ in range(5):
            self.assertTrue(self.engine.is_deterministic())


class TestShadowConfidenceConsistency(unittest.TestCase):
    """Verify shadow confidence maintains consistency properties"""
    
    def setUp(self):
        self.engine = SemanticConfidenceEngine()
    
    def test_monotonic_increase_with_match_count(self):
        """More matches → higher confidence (monotonic)"""
        base_params = {
            'pattern_category': 'theme',
            'false_positive_risk': 'low',
            'semantic_density': 0.5,
            'evidence_diversity': 0.5,
            'coverage_ratio': 0.5,
        }
        
        confidences = []
        for match_count in [0, 2, 4, 6, 8]:
            result = self.engine.calculate_confidence(
                raw_match_count=match_count,
                **base_params,
            )
            confidences.append(result['calibrated_confidence'])
        
        # Should be non-decreasing
        for i in range(len(confidences) - 1):
            self.assertLessEqual(confidences[i], confidences[i + 1],
                               f"Not monotonic: {confidences[i]} > {confidences[i+1]}")
    
    def test_calibration_delta_signs(self):
        """Calibration adjustments apply consistently"""
        results_low_risk = self.engine.calculate_confidence(
            raw_match_count=5,
            pattern_category='theme',
            false_positive_risk='low',
            semantic_density=0.5,
            evidence_diversity=0.5,
            coverage_ratio=0.5,
        )
        
        results_high_risk = self.engine.calculate_confidence(
            raw_match_count=5,
            pattern_category='theme',
            false_positive_risk='high',
            semantic_density=0.5,
            evidence_diversity=0.5,
            coverage_ratio=0.5,
        )
        
        # High risk should have lower calibrated confidence
        self.assertLess(
            results_high_risk['calibrated_confidence'],
            results_low_risk['calibrated_confidence'],
        )
        
        # But same raw confidence (before adjustment)
        self.assertEqual(
            results_high_risk['raw_confidence'],
            results_low_risk['raw_confidence'],
        )
    
    def test_bounds_maintained(self):
        """Confidence always in [0, 1]"""
        test_cases = [
            (0, 'low', 0.0, 0.0, 0.0),
            (100, 'high', 1.0, 1.0, 1.0),
            (50, 'medium', 0.5, 0.5, 0.5),
            (1, 'high', 0.1, 0.1, 0.1),
            (200, 'low', 1.0, 1.0, 1.0),
        ]
        
        for match_count, fp_risk, density, diversity, coverage in test_cases:
            result = self.engine.calculate_confidence(
                raw_match_count=match_count,
                pattern_category='theme',
                false_positive_risk=fp_risk,
                semantic_density=density,
                evidence_diversity=diversity,
                coverage_ratio=coverage,
            )
            
            self.assertGreaterEqual(result['calibrated_confidence'], 0.0)
            self.assertLessEqual(result['calibrated_confidence'], 1.0)


if __name__ == '__main__':
    unittest.main()
