import copy
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.real_book_shadow_execution import build_real_book_shadow_execution


class TestRealBookShadowExecution(unittest.TestCase):
    def test_empty_dataset(self):
        result = build_real_book_shadow_execution([])
        self.assertEqual(result, [])

    def test_single_book(self):
        books = [
            {
                'book_id': 'book-1',
                'title': 'Example Book',
                'publisher': 'Example Publisher',
                'grade': '7',
                'genre': 'Adventure',
                'language': 'tr',
                'page_count': 180,
            }
        ]
        result = build_real_book_shadow_execution(books)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['book_id'], 'book-1')
        self.assertTrue(result[0]['shadow_execution_completed'])
        self.assertTrue(result[0]['orchestrator_called'])
        self.assertEqual(result[0]['deterministic'], True)
        self.assertFalse(result[0]['production_output_changed'])
        self.assertFalse(result[0]['runtime_pipeline_bound'])
        self.assertTrue(isinstance(result[0]['stage_order'], list))

    def test_multiple_books(self):
        books = [
            {'book_id': 'book-2', 'title': 'Second Book'},
            {'book_id': 'book-1', 'title': 'First Book'},
        ]
        result = build_real_book_shadow_execution(books)
        self.assertEqual([item['book_id'] for item in result], ['book-1', 'book-2'])
        self.assertTrue(all(item['shadow_execution_completed'] for item in result))

    def test_determinism(self):
        books = [
            {'book_id': 'book-1', 'title': 'First Book'},
            {'book_id': 'book-2', 'title': 'Second Book'},
        ]
        first = build_real_book_shadow_execution(books)
        second = build_real_book_shadow_execution(copy.deepcopy(books))
        self.assertEqual(first, second)

    def test_stable_ordering(self):
        books = [
            {'book_id': 'book-3', 'title': 'Third Book'},
            {'book_id': 'book-1', 'title': 'First Book'},
            {'book_id': 'book-2', 'title': 'Second Book'},
        ]
        result = build_real_book_shadow_execution(books)
        self.assertEqual([item['book_id'] for item in result], ['book-1', 'book-2', 'book-3'])

    def test_orchestrator_called(self):
        books = [
            {'book_id': 'book-1', 'title': 'Example Book'},
        ]
        result = build_real_book_shadow_execution(books)
        self.assertTrue(result[0]['orchestrator_called'])
        self.assertEqual(result[0]['stage_order'], [
            'pattern_match_producer',
            'confidence_engine',
            'semantic_monitor',
            'evidence_ranking',
            'explainability',
            'acceptance_gate',
            'human_review_package',
            'shadow_production_delta',
        ])


if __name__ == '__main__':
    unittest.main()
