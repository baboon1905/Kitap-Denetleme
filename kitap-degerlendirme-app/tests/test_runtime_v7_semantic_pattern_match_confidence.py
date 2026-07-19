import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.semantic_pattern_match_confidence import (
    build_pattern_match_confidence,
    build_pattern_matches_with_confidence_from_payload,
)


class TestSemanticPatternMatchConfidence(unittest.TestCase):
    def test_empty_match_list_returns_empty(self):
        self.assertEqual(build_pattern_match_confidence([]), [])
        self.assertEqual(build_pattern_match_confidence(None), [])

    def test_deterministic_confidence_for_same_matches(self):
        matches = [
            {'pattern_id': 'theme_adventure', 'pattern_category': 'theme', 'matched_keywords': ['macera'], 'source': 'summary_ir.themes', 'match_snippet': 'Macera dolu bir öykü.'},
            {'pattern_id': 'character_protagonist', 'pattern_category': 'character_role', 'matched_keywords': ['kahraman'], 'source': 'semantic.character_roles', 'match_snippet': 'Kahraman cesur bir çocuktu.'},
        ]
        first = build_pattern_match_confidence(matches)
        second = build_pattern_match_confidence(matches)
        self.assertEqual(first, second)

    def test_confidence_fields_are_in_range(self):
        matches = [
            {'pattern_id': 'theme_adventure', 'pattern_category': 'theme', 'matched_keywords': ['macera'], 'source': 'summary_ir.themes', 'match_snippet': 'Macera dolu bir öykü.'},
            {'pattern_id': 'theme_growth', 'pattern_category': 'theme', 'matched_keywords': ['büyüme'], 'source': 'narrative.summary', 'match_snippet': 'Kahraman olgunlaşıyor.'},
        ]
        results = build_pattern_match_confidence(matches)
        self.assertEqual(len(results), 2)
        for item in results:
            self.assertIn('raw_confidence', item)
            self.assertIn('calibrated_confidence', item)
            self.assertGreaterEqual(item['raw_confidence'], 0.0)
            self.assertLessEqual(item['raw_confidence'], 1.0)
            self.assertGreaterEqual(item['calibrated_confidence'], 0.0)
            self.assertLessEqual(item['calibrated_confidence'], 1.0)
            self.assertEqual(item['pattern_id'], item['pattern_id'])

    def test_payload_to_confidence_integration(self):
        payload = {
            'summary_ir': {
                'themes': ['macera'],
                'story_arc': 'Kahraman yolculuğu zorluklarla dolu.',
            },
            'semantic': {
                'character_roles': ['kahraman'],
            },
            'narrative': {
                'summary': 'Kahraman büyür ve değişir.',
            },
        }
        results = build_pattern_matches_with_confidence_from_payload(payload)
        self.assertTrue(isinstance(results, list))
        self.assertGreaterEqual(len(results), 1)
        self.assertTrue(all('raw_confidence' in item and 'calibrated_confidence' in item for item in results))

    def test_three_examples_have_confidence(self):
        matches = [
            {'pattern_id': 'theme_adventure', 'pattern_category': 'theme', 'matched_keywords': ['macera'], 'source': 'summary_ir.themes', 'match_snippet': 'Macera dolu bir hikaye.'},
            {'pattern_id': 'theme_growth', 'pattern_category': 'theme', 'matched_keywords': ['gelişim', 'büyüme'], 'source': 'semantic.theme_clusters', 'match_snippet': 'Çocuk büyüme sürecini yaşıyor.'},
            {'pattern_id': 'character_protagonist', 'pattern_category': 'character_role', 'matched_keywords': ['kahraman'], 'source': 'narrative.summary', 'match_snippet': 'Kahraman kararlı bir liderdi.'},
        ]
        results = build_pattern_match_confidence(matches)
        self.assertEqual(len(results), 3)
        self.assertTrue(all('confidence_level' in item for item in results))
        self.assertTrue(all(item['raw_confidence'] >= 0.0 and item['raw_confidence'] <= 1.0 for item in results))
        self.assertTrue(all(item['calibrated_confidence'] >= 0.0 and item['calibrated_confidence'] <= 1.0 for item in results))


if __name__ == '__main__':
    unittest.main()
