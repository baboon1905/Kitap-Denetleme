import copy
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.real_book_shadow_validator import build_real_book_shadow_validation


class TestRealBookShadowValidator(unittest.TestCase):
    def test_empty_dataset(self):
        result = build_real_book_shadow_validation([])
        self.assertEqual(result, [])

    def test_single_book(self):
        books = [
            {
                'book_id': 'book-1',
                'isbn': '978-1234567890',
                'title': 'Example Book',
                'publisher': 'Publisher',
                'grade': '7',
                'genre': 'Adventure',
                'language': 'tr',
                'page_count': 150,
            }
        ]
        result = build_real_book_shadow_validation(books)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['book_id'], 'book-1')
        self.assertEqual(result[0]['validation_status'], 'pending')
        self.assertTrue(result[0]['shadow_validation_ready'])
        self.assertFalse(result[0]['semantic_pipeline_called'])
        self.assertFalse(result[0]['production_output_changed'])
        self.assertFalse(result[0]['runtime_pipeline_bound'])

    def test_multiple_books(self):
        books = [
            {'book_id': 'book-2', 'title': 'Second Book'},
            {'book_id': 'book-1', 'title': 'First Book'},
        ]
        result = build_real_book_shadow_validation(books)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['book_id'], 'book-1')
        self.assertEqual(result[1]['book_id'], 'book-2')

    def test_determinism(self):
        books = [
            {'book_id': 'book-1', 'title': 'First Book'},
            {'book_id': 'book-2', 'title': 'Second Book'},
        ]
        first = build_real_book_shadow_validation(books)
        second = build_real_book_shadow_validation(copy.deepcopy(books))
        self.assertEqual(first, second)

    def test_no_mutation_of_input(self):
        books = [
            {'book_id': 'book-1', 'title': 'First Book'},
        ]
        original = copy.deepcopy(books)
        build_real_book_shadow_validation(books)
        self.assertEqual(books, original)

    def test_stable_ordering(self):
        books = [
            {'book_id': 'book-3'},
            {'book_id': 'book-1'},
            {'book_id': 'book-2'},
        ]
        result = build_real_book_shadow_validation(books)
        self.assertEqual([item['book_id'] for item in result], ['book-1', 'book-2', 'book-3'])


if __name__ == '__main__':
    unittest.main()
