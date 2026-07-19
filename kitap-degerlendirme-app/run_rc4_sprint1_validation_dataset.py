import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime_v7.validation_dataset_builder import build_validation_dataset


CANARY_BOOKS: List[Dict[str, Any]] = [
    {
        'book_id': 'book-1',
        'isbn': '978-9750200001',
        'title': 'Canary Story One',
        'publisher': 'Canary Press',
        'grade': '6',
        'genre': 'Adventure',
        'language': 'tr',
        'page_count': 152,
    },
    {
        'book_id': 'book-2',
        'isbn': '978-9750200002',
        'title': 'Canary Story Two',
        'publisher': 'Canary Press',
        'grade': '7',
        'genre': 'Fantasy',
        'language': 'tr',
        'page_count': 184,
    },
    {
        'book_id': 'book-3',
        'isbn': '978-9750200003',
        'title': 'Canary Story Three',
        'publisher': 'Canary Press',
        'grade': '8',
        'genre': 'Drama',
        'language': 'tr',
        'page_count': 200,
    },
]


def build_validation_dataset_artifact(
    output_path: Optional[Path] = None,
    books: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    base = Path(__file__).resolve().parent
    artifact_path = Path(output_path) if output_path else base / 'rc4_sprint1_validation_dataset.json'
    payload = books if books is not None else CANARY_BOOKS
    artifact = build_validation_dataset(payload, dataset_version='1.0')
    artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return artifact


def main() -> None:
    artifact = build_validation_dataset_artifact()
    print(json.dumps(artifact, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
