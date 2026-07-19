import copy
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.validation_dataset_builder import build_validation_dataset


class TestValidationDatasetBuilder(unittest.TestCase):
    def test_empty_list_safe(self):
        result = build_validation_dataset([])
        self.assertEqual(result['total_books'], 0)
        self.assertEqual(result['books'], [])

    def test_same_input_same_dataset(self):
        books = [
            {
                'book_id': 'book-1',
                'isbn': '978-1234567890',
                'title': 'Example Book',
                'publisher': 'Example Publisher',
                'grade': '7',
                'genre': 'Adventure',
                'language': 'tr',
                'page_count': 180,
            }
        ]
        first = build_validation_dataset(books)
        second = build_validation_dataset(copy.deepcopy(books))
        self.assertEqual(first, second)

    def test_deterministic_sorting(self):
        books = [
            {
                'book_id': 'book-2',
                'isbn': '978-2222222222',
                'title': 'B Book',
                'publisher': 'Second Publisher',
                'grade': '8',
                'genre': 'Fantasy',
                'language': 'tr',
                'page_count': 200,
            },
            {
                'book_id': 'book-1',
                'isbn': '978-1111111111',
                'title': 'A Book',
                'publisher': 'First Publisher',
                'grade': '6',
                'genre': 'Drama',
                'language': 'tr',
                'page_count': 150,
            },
        ]
        result = build_validation_dataset(books)
        self.assertEqual(result['books'][0]['book_id'], 'book-1')
        self.assertEqual(result['books'][1]['book_id'], 'book-2')

    def test_metadata_correct(self):
        books = [
            {
                'book_id': 'book-1',
                'isbn': '978-1234567890',
                'title': 'Example Book',
                'publisher': 'Example Publisher',
                'grade': '7',
                'genre': 'Adventure',
                'language': 'tr',
                'page_count': 180,
            }
        ]
        result = build_validation_dataset(books, dataset_version='2.0')
        self.assertEqual(result['dataset_version'], '2.0')
        self.assertEqual(result['generated_at'], '1970-01-01T00:00:00Z')
        self.assertEqual(result['total_books'], 1)
        self.assertEqual(result['books'][0]['validation_status'], 'pending')
        self.assertEqual(result['books'][0]['human_review_status'], 'pending')

    def test_production_payload_not_modified(self):
        books = [
            {
                'book_id': 'book-1',
                'isbn': '978-1234567890',
                'title': 'Example Book',
                'publisher': 'Example Publisher',
                'grade': '7',
                'genre': 'Adventure',
                'language': 'tr',
                'page_count': 180,
            }
        ]
        original = copy.deepcopy(books)
        build_validation_dataset(books)
        self.assertEqual(books, original)

    def test_builder_immutable(self):
        books = [
            {
                'book_id': 'book-1',
                'isbn': '978-1234567890',
                'title': 'Example Book',
                'publisher': 'Example Publisher',
                'grade': '7',
                'genre': 'Adventure',
                'language': 'tr',
                'page_count': 180,
            }
        ]
        result = build_validation_dataset(books)
        result['books'][0]['title'] = 'Modified Title'
        self.assertEqual(books[0]['title'], 'Example Book')


if __name__ == '__main__':
    unittest.main()
