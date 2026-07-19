import unittest
import sys
from pathlib import Path

# Add project root to path so runtime_v7 imports resolve
sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.semantic_pattern_match_producer import build_pattern_matches_from_payload


class TestSemanticPatternMatchProducer(unittest.TestCase):
    def test_empty_payload_returns_empty_matches(self):
        self.assertEqual(build_pattern_matches_from_payload({}), [])
        self.assertEqual(build_pattern_matches_from_payload({'summary_ir': None}), [])

    def test_matches_are_deterministic_and_sorted(self):
        payload = {
            'summary_ir': {
                'themes': ['macera', 'büyüme'],
                'story_arc': 'Kahraman yolculuğu başlar ve sonunda değişir.',
                'narrative_graph': {
                    'nodes': [
                        {'summary': 'Kahraman uzaklara gider.', 'action': 'yola çıkma'},
                    ]
                }
            },
            'semantic': {
                'theme_clusters': ['macera'],
                'character_roles': ['kahraman'],
                'learning_outcome_clusters': ['öğrenme']
            },
            'narrative': {
                'summary': 'Kahraman yolculuğu sonunda büyür ve kendini tanır.',
            },
            'title': 'Macera Kitabı',
            'book_title': 'Macera Kitabı',
        }

        first = build_pattern_matches_from_payload(payload)
        second = build_pattern_matches_from_payload(payload)
        self.assertEqual(first, second)
        self.assertEqual(sorted(first, key=lambda x: (x['pattern_id'], x['source'], x['match_snippet'])), first)

    def test_title_fields_do_not_create_matches(self):
        # The title contains a theme keyword, but only title fields should be ignored.
        payload = {
            'title': 'Macera Kitabı',
            'summary_ir': {
                'themes': [],
            },
            'semantic': {},
            'narrative': {},
        }
        matches = build_pattern_matches_from_payload(payload)
        self.assertEqual(matches, [])

    def test_summary_ir_and_semantic_fields_produce_pattern_matches(self):
        payload = {
            'summary_ir': {
                'themes': ['Macera', 'Arkadaşlık'],
                'story_arc': 'Kahramanlar birlikte çalışır ve zorlukları aşar.',
            },
            'semantic': {
                'theme_clusters': [{'label': 'macera'}],
                'character_roles': ['kahraman'],
            },
            'narrative': {
                'summary': 'Kahraman yolculuğu zorlu ama öğreticidir.',
            },
        }
        matches = build_pattern_matches_from_payload(payload)
        self.assertGreaterEqual(len(matches), 1)
        self.assertTrue(any(m['pattern_id'].startswith('theme_') for m in matches))
        self.assertTrue(all('pattern_id' in m for m in matches))
        self.assertTrue(all('source' in m for m in matches))


if __name__ == '__main__':
    unittest.main()
