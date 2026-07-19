import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.semantic_pattern_monitor import build_canonical_activations_from_pattern_matches


class TestSemanticPatternMonitorStage233(unittest.TestCase):
    def test_empty_match_list_returns_empty_activations(self):
        result = build_canonical_activations_from_pattern_matches([])
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('pattern_activations'), [])

    def test_canonical_activations_are_produced_for_confident_matches(self):
        matches = [
            {
                'pattern_id': 'theme_adventure',
                'pattern_category': 'theme',
                'matched_keywords': ['macera'],
                'source': 'summary_ir.themes',
                'match_snippet': 'Macera dolu bir hikaye.',
                'raw_confidence': 0.55,
                'calibrated_confidence': 0.59,
                'recommendation': 'keep',
            },
            {
                'pattern_id': 'theme_growth',
                'pattern_category': 'theme',
                'matched_keywords': ['büyüme'],
                'source': 'semantic.theme_clusters',
                'match_snippet': 'Kahraman kendini geliştiriyor.',
                'raw_confidence': 0.65,
                'calibrated_confidence': 0.68,
                'recommendation': 'keep',
            },
        ]
        result = build_canonical_activations_from_pattern_matches(matches)
        activations = result.get('pattern_activations', [])
        self.assertGreater(len(activations), 0)
        for entry in activations:
            self.assertGreater(entry.get('evidence_count', 0), 0)
            self.assertEqual(entry.get('raw_confidence'), round(entry.get('raw_confidence'), 2))
            self.assertEqual(entry.get('calibrated_confidence'), round(entry.get('calibrated_confidence'), 2))
            self.assertIn(entry['pattern_id'], {'theme_adventure', 'theme_growth'})

    def test_upstream_confidence_is_preserved(self):
        matches = [
            {
                'pattern_id': 'theme_adventure',
                'pattern_category': 'theme',
                'matched_keywords': ['macera'],
                'source': 'summary_ir.themes',
                'match_snippet': 'Macera dolu bir hikaye.',
                'raw_confidence': 0.55,
                'calibrated_confidence': 0.59,
            }
        ]
        result = build_canonical_activations_from_pattern_matches(matches)
        activations = result.get('pattern_activations', [])
        self.assertEqual(len(activations), 1)
        self.assertEqual(activations[0]['raw_confidence'], 0.55)
        self.assertEqual(activations[0]['calibrated_confidence'], 0.59)

    def test_same_input_produces_same_output(self):
        matches = [
            {
                'pattern_id': 'theme_adventure',
                'pattern_category': 'theme',
                'matched_keywords': ['macera'],
                'source': 'summary_ir.themes',
                'match_snippet': 'Macera dolu bir hikaye.',
                'raw_confidence': 0.55,
                'calibrated_confidence': 0.59,
            }
        ]
        first = build_canonical_activations_from_pattern_matches(matches)
        second = build_canonical_activations_from_pattern_matches(matches)
        self.assertEqual(first, second)

    def test_first_three_canonical_activations_example(self):
        matches = [
            {
                'pattern_id': 'theme_adventure',
                'pattern_category': 'theme',
                'matched_keywords': ['macera'],
                'source': 'summary_ir.themes',
                'match_snippet': 'Macera dolu bir hikaye.',
                'raw_confidence': 0.55,
                'calibrated_confidence': 0.59,
            },
            {
                'pattern_id': 'theme_growth',
                'pattern_category': 'theme',
                'matched_keywords': ['büyüme'],
                'source': 'semantic.theme_clusters',
                'match_snippet': 'Kahraman kendini geliştiriyor.',
                'raw_confidence': 0.65,
                'calibrated_confidence': 0.68,
            },
            {
                'pattern_id': 'character_protagonist',
                'pattern_category': 'character_role',
                'matched_keywords': ['kahraman'],
                'source': 'narrative.summary',
                'match_snippet': 'Kahraman liderliğini kanıtladı.',
                'raw_confidence': 0.72,
                'calibrated_confidence': 0.75,
            },
        ]
        result = build_canonical_activations_from_pattern_matches(matches)
        activations = result.get('pattern_activations', [])
        self.assertEqual(len(activations), 3)
        self.assertEqual(activations[0]['pattern_id'], 'character_protagonist')
        self.assertEqual(activations[1]['pattern_id'], 'theme_adventure')
        self.assertEqual(activations[2]['pattern_id'], 'theme_growth')
        self.assertEqual(activations[0]['raw_confidence'], 0.72)
        self.assertEqual(activations[0]['calibrated_confidence'], 0.75)
        self.assertEqual(activations[1]['raw_confidence'], 0.55)
        self.assertEqual(activations[1]['calibrated_confidence'], 0.59)
        self.assertEqual(activations[2]['raw_confidence'], 0.65)
        self.assertEqual(activations[2]['calibrated_confidence'], 0.68)


if __name__ == '__main__':
    unittest.main()
