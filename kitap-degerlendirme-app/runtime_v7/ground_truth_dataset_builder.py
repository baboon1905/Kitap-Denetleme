import copy
from typing import Any, Dict, List


def _normalize_book(book: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'book_id': book.get('book_id'),
        'human_patterns': list(book.get('human_patterns') or []),
        'human_themes': list(book.get('human_themes') or []),
        'human_character_roles': list(book.get('human_character_roles') or []),
        'human_learning_outcomes': list(book.get('human_learning_outcomes') or []),
        'reviewer_id': book.get('reviewer_id'),
        'review_status': book.get('review_status', 'pending'),
    }


def build_ground_truth_dataset(books: List[Dict[str, Any]], dataset_version: str = '1.0') -> Dict[str, Any]:
    books_copy = copy.deepcopy(books) if isinstance(books, list) else []
    normalized_books = [
        _normalize_book(book)
        for book in books_copy
        if isinstance(book, dict)
    ]
    normalized_books.sort(key=lambda item: (str(item.get('book_id') or ''), str(item.get('reviewer_id') or '')))

    return {
        'dataset_version': dataset_version,
        'generated_at': '1970-01-01T00:00:00Z',
        'total_books': len(normalized_books),
        'books': normalized_books,
    }
