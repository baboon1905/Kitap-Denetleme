import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.semantic_evidence_ranker import rank_semantic_evidence


class TestSemanticEvidenceRanker(unittest.TestCase):
    def test_same_input_same_ranking(self):
        input_payload = [
            {
                'pattern_id': 'theme_adventure',
                'evidence_count': 2,
                'source': 'summary_ir.themes',
                'matched_keywords': ['macera'],
                'match_snippet': 'Macera dolu bir hikaye.'
            },
            {
                'pattern_id': 'theme_friendship',
                'evidence_count': 1,
                'source': 'semantic.theme_clusters',
                'matched_keywords': ['dostluk'],
                'match_snippet': 'Dostluğun önemi vurgulanır.'
            }
        ]

        first = rank_semantic_evidence(input_payload)
        second = rank_semantic_evidence(input_payload)
        self.assertEqual(first, second)

    def test_empty_list_returns_empty_list(self):
        self.assertEqual(rank_semantic_evidence([]), [])

    def test_ranking_is_deterministic(self):
        input_payload = [
            {
                'pattern_id': 'theme_friendship',
                'evidence_count': 1,
                'source': 'semantic.theme_clusters',
                'matched_keywords': ['dostluk'],
                'match_snippet': 'Dostluğun önemi vurgulanır.'
            },
            {
                'pattern_id': 'theme_adventure',
                'evidence_count': 2,
                'source': 'summary_ir.themes',
                'matched_keywords': ['macera'],
                'match_snippet': 'Macera dolu bir hikaye.'
            },
        ]

        ranked1 = rank_semantic_evidence(input_payload)
        ranked2 = rank_semantic_evidence(list(reversed(input_payload)))
        self.assertEqual(ranked1, ranked2)
        self.assertEqual(ranked1[0]['pattern_id'], 'theme_adventure')
        self.assertEqual(ranked1[0]['rank'], 1)

    def test_confidence_fields_unchanged(self):
        input_payload = [
            {
                'pattern_id': 'theme_adventure',
                'evidence_count': 2,
                'source': 'summary_ir.themes',
                'matched_keywords': ['macera'],
                'match_snippet': 'Macera dolu bir hikaye.',
                'raw_confidence': 0.5,
                'calibrated_confidence': 0.6,
            }
        ]

        ranked = rank_semantic_evidence(input_payload)
        self.assertIn('raw_confidence', input_payload[0])
        self.assertIn('calibrated_confidence', input_payload[0])
        self.assertEqual(input_payload[0]['raw_confidence'], 0.5)
        self.assertEqual(input_payload[0]['calibrated_confidence'], 0.6)
        self.assertNotIn('raw_confidence', ranked[0])
        self.assertNotIn('calibrated_confidence', ranked[0])

    def test_pattern_activation_not_mutated(self):
        activation = {
            'pattern_id': 'theme_adventure',
            'evidence_count': 2,
            'source': 'summary_ir.themes',
            'matched_keywords': ['macera'],
            'match_snippet': 'Macera dolu bir hikaye.',
            'raw_confidence': 0.5,
            'calibrated_confidence': 0.6,
        }
        input_payload = [activation]
        original = copy.deepcopy(input_payload)

        rank_semantic_evidence(input_payload)
        self.assertEqual(input_payload, original)


if __name__ == '__main__':
    unittest.main()
