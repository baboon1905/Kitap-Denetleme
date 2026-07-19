import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.semantic_acceptance_gate import build_semantic_acceptance_decisions


class TestSemanticAcceptanceGate(unittest.TestCase):
    def test_same_input_same_decision(self):
        activations = [{
            'pattern_id': 'theme_adventure',
            'status': 'active',
            'raw_confidence': 0.75,
            'calibrated_confidence': 0.8,
        }]
        ranked = [{'pattern_id': 'theme_adventure', 'rank_score': 6.0}]
        explanations = [{'pattern_id': 'theme_adventure', 'reasoning': 'clear support', 'supporting_signals': ['evidence_count=2']}] 
        delta = {'coverage_delta': 0.2}

        first = build_semantic_acceptance_decisions(activations, ranked, explanations, delta)
        second = build_semantic_acceptance_decisions(activations, ranked, explanations, delta)
        self.assertEqual(first, second)

    def test_empty_input_empty_decision(self):
        self.assertEqual(build_semantic_acceptance_decisions([], [], [], {}), [])

    def test_high_confidence_and_strong_evidence_becomes_accepted(self):
        activations = [{
            'pattern_id': 'theme_resilience',
            'status': 'active',
            'raw_confidence': 0.75,
            'calibrated_confidence': 0.8,
        }]
        ranked = [{'pattern_id': 'theme_resilience', 'rank_score': 6.0}]
        explanations = [{'pattern_id': 'theme_resilience', 'reasoning': 'clear support', 'supporting_signals': ['evidence_count=3']}] 
        delta = {'coverage_delta': 0.2}

        decisions = build_semantic_acceptance_decisions(activations, ranked, explanations, delta)
        self.assertEqual(decisions[0]['decision'], 'accepted')
        self.assertEqual(decisions[0]['decision_score'], 1.0)

    def test_low_confidence_or_missing_explanation_is_review_or_rejected(self):
        activations = [{
            'pattern_id': 'theme_courage',
            'status': 'candidate',
            'raw_confidence': 0.4,
            'calibrated_confidence': 0.45,
        }]
        ranked = [{'pattern_id': 'theme_courage', 'rank_score': 2.0}]
        explanations = []
        delta = {'coverage_delta': 0.0}

        decisions = build_semantic_acceptance_decisions(activations, ranked, explanations, delta)
        self.assertIn(decisions[0]['decision'], {'review', 'rejected'})

    def test_input_not_mutated(self):
        activations = [{'pattern_id': 'theme_adventure', 'status': 'active', 'raw_confidence': 0.6, 'calibrated_confidence': 0.65}]
        ranked = [{'pattern_id': 'theme_adventure', 'rank_score': 4.0}]
        explanations = [{'pattern_id': 'theme_adventure', 'reasoning': 'clear support', 'supporting_signals': ['evidence_count=2']}] 
        delta = {'coverage_delta': 0.1}
        original = copy.deepcopy((activations, ranked, explanations, delta))

        build_semantic_acceptance_decisions(activations, ranked, explanations, delta)
        self.assertEqual((activations, ranked, explanations, delta), original)

    def test_no_book_specific_heuristic(self):
        activations = [{'pattern_id': 'theme_adventure', 'status': 'active', 'raw_confidence': 0.7, 'calibrated_confidence': 0.72}]
        ranked = [{'pattern_id': 'theme_adventure', 'rank_score': 5.0}]
        explanations = [{'pattern_id': 'theme_adventure', 'reasoning': 'clear support', 'supporting_signals': ['evidence_count=2']}] 
        delta = {'coverage_delta': 0.2}

        decisions = build_semantic_acceptance_decisions(activations, ranked, explanations, delta)
        joined = ' '.join(str(item) for item in decisions).lower()
        self.assertNotIn('book', joined)
        self.assertNotIn('kitap', joined)


if __name__ == '__main__':
    unittest.main()
