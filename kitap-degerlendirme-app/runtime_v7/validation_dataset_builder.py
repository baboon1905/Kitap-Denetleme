import copy
from typing import Any, Dict, List


REQUIRED_BOOK_FIELDS = [
    'book_id',
    'isbn',
    'title',
    'publisher',
    'grade',
    'genre',
    'language',
    'page_count',
]


def _normalize_book(book: Dict[str, Any]) -> Dict[str, Any]:
    normalized = {
        'book_id': book.get('book_id'),
        'isbn': book.get('isbn'),
        'title': book.get('title'),
        'publisher': book.get('publisher'),
        'grade': book.get('grade'),
        'genre': book.get('genre'),
        'language': book.get('language'),
        'page_count': book.get('page_count'),
        'validation_status': 'pending',
        'human_review_status': 'pending',
    }
    return normalized


def build_validation_dataset(books: List[Dict[str, Any]], dataset_version: str = '1.0') -> Dict[str, Any]:
    books_copy = copy.deepcopy(books) if isinstance(books, list) else []
    normalized_books = [_normalize_book(book) for book in books_copy if isinstance(book, dict)]
    normalized_books.sort(key=lambda item: (str(item.get('book_id') or ''), str(item.get('title') or '')))

    return {
        'dataset_version': dataset_version,
        'generated_at': '1970-01-01T00:00:00Z',
        'total_books': len(normalized_books),
        'books': normalized_books,
    }
