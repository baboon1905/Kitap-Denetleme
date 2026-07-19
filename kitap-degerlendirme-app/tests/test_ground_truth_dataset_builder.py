import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.ground_truth_dataset_builder import build_ground_truth_dataset


class TestGroundTruthDatasetBuilder(unittest.TestCase):
    def test_empty_dataset(self):
        result = build_ground_truth_dataset([])
        self.assertEqual(result['total_books'], 0)
        self.assertEqual(result['books'], [])

    def test_single_book(self):
        books = [
            {
                'book_id': 'book-1',
                'human_patterns': ['pattern-a'],
                'human_themes': ['theme-x'],
                'human_character_roles': ['role-w'],
                'human_learning_outcomes': ['outcome-1'],
                'reviewer_id': 'reviewer-1',
            }
        ]
        result = build_ground_truth_dataset(books)

        self.assertEqual(result['total_books'], 1)
        self.assertEqual(result['dataset_version'], '1.0')
        self.assertEqual(result['books'][0]['book_id'], 'book-1')
        self.assertEqual(result['books'][0]['human_patterns'], ['pattern-a'])
        self.assertEqual(result['books'][0]['human_themes'], ['theme-x'])
        self.assertEqual(result['books'][0]['human_character_roles'], ['role-w'])
        self.assertEqual(result['books'][0]['human_learning_outcomes'], ['outcome-1'])
        self.assertEqual(result['books'][0]['reviewer_id'], 'reviewer-1')
        self.assertEqual(result['books'][0]['review_status'], 'pending')

    def test_multiple_books(self):
        books = [
            {
                'book_id': 'book-2',
                'human_patterns': ['pattern-b'],
                'human_themes': ['theme-y'],
                'human_character_roles': ['role-z'],
                'human_learning_outcomes': ['outcome-2'],
                'reviewer_id': 'reviewer-2',
            },
            {
                'book_id': 'book-1',
                'human_patterns': ['pattern-a'],
                'human_themes': ['theme-x'],
                'human_character_roles': ['role-w'],
                'human_learning_outcomes': ['outcome-1'],
                'reviewer_id': 'reviewer-1',
            },
        ]
        result = build_ground_truth_dataset(books)

        self.assertEqual(result['total_books'], 2)
        self.assertEqual(result['books'][0]['book_id'], 'book-1')
        self.assertEqual(result['books'][1]['book_id'], 'book-2')

    def test_deterministic_output(self):
        books = [
            {
                'book_id': 'book-2',
                'human_patterns': ['pattern-b'],
                'human_themes': ['theme-y'],
                'human_character_roles': ['role-z'],
                'human_learning_outcomes': ['outcome-2'],
                'reviewer_id': 'reviewer-2',
            },
            {
                'book_id': 'book-1',
                'human_patterns': ['pattern-a'],
                'human_themes': ['theme-x'],
                'human_character_roles': ['role-w'],
                'human_learning_outcomes': ['outcome-1'],
                'reviewer_id': 'reviewer-1',
            },
        ]
        first = build_ground_truth_dataset(books)
        second = build_ground_truth_dataset(copy.deepcopy(books))
        self.assertEqual(first, second)

    def test_input_mutate_ed(self):
        books = [
            {
                'book_id': 'book-1',
                'human_patterns': ['pattern-a'],
                'human_themes': ['theme-x'],
                'human_character_roles': ['role-w'],
                'human_learning_outcomes': ['outcome-1'],
                'reviewer_id': 'reviewer-1',
            }
        ]
        original = copy.deepcopy(books)
        build_ground_truth_dataset(books)
        self.assertEqual(books, original)

    def test_default_review_status_pending(self):
        books = [
            {
                'book_id': 'book-1',
                'human_patterns': ['pattern-a'],
                'human_themes': ['theme-x'],
                'human_character_roles': ['role-w'],
                'human_learning_outcomes': ['outcome-1'],
                'reviewer_id': 'reviewer-1',
            }
        ]
        result = build_ground_truth_dataset(books)
        self.assertEqual(result['books'][0]['review_status'], 'pending')


if __name__ == '__main__':
    unittest.main()
