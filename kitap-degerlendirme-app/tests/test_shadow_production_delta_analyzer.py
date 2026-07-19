import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.shadow_production_delta_analyzer import analyze_shadow_production_delta


class TestShadowProductionDeltaAnalyzer(unittest.TestCase):
    def test_empty_input_deterministic_result(self):
        production_payload = {}
        shadow_payload = {}

        result = analyze_shadow_production_delta(production_payload, shadow_payload)

        self.assertIsInstance(result, dict)
        self.assertEqual(result['coverage_delta'], 0.0)
        self.assertEqual(result['activation_count_delta'], 0)
        self.assertEqual(result['overlap_score'], 1.0)
        self.assertEqual(result['shadow_only_signals'], [])
        self.assertEqual(result['production_only_signals'], [])
        self.assertIsInstance(result['deterministic_fingerprint'], str)

    def test_same_input_same_fingerprint(self):
        production_payload = {'keywords': ['arkadaş', 'macera']}
        shadow_payload = {'pattern_matches': [{'pattern_id': 'theme_friendship'}]}

        first = analyze_shadow_production_delta(production_payload, shadow_payload)
        second = analyze_shadow_production_delta(production_payload, shadow_payload)

        self.assertEqual(first['deterministic_fingerprint'], second['deterministic_fingerprint'])
        self.assertEqual(first, second)

    def test_shadow_activation_increases_coverage_delta(self):
        production_payload = {'pattern_activations': []}
        shadow_payload = {'pattern_activations': [{'pattern_id': 'theme_adventure'}]}

        result = analyze_shadow_production_delta(production_payload, shadow_payload)

        self.assertGreater(result['coverage_delta'], 0.0)
        self.assertEqual(result['activation_count_delta'], 1)

    def test_production_only_fields_are_separated(self):
        production_payload = {'semantic_labels': ['kahraman', 'macera']}
        shadow_payload = {'semantic_labels': ['kahraman', 'dostluk']}

        result = analyze_shadow_production_delta(production_payload, shadow_payload)

        self.assertIn('semantic_labels.dostluk', result['shadow_only_signals'])
        self.assertIn('semantic_labels.macera', result['production_only_signals'])
        self.assertNotIn('semantic_labels.kahraman', result['shadow_only_signals'])
        self.assertNotIn('semantic_labels.kahraman', result['production_only_signals'])

    def test_production_payload_not_mutated(self):
        production_payload = {'pattern_activations': [{'pattern_id': 'theme_adventure'}]}
        production_copy = copy.deepcopy(production_payload)

        analyze_shadow_production_delta(production_payload, {})

        self.assertEqual(production_payload, production_copy)

    def test_shadow_payload_not_mutated(self):
        shadow_payload = {'pattern_activations': [{'pattern_id': 'theme_adventure'}]}
        shadow_copy = copy.deepcopy(shadow_payload)

        analyze_shadow_production_delta({}, shadow_payload)

        self.assertEqual(shadow_payload, shadow_copy)


if __name__ == '__main__':
    unittest.main()
