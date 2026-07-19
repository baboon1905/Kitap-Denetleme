import json

try:
    with open('snapshot_result.json', 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    print("\nEndpoint Status Summary:")
    print("=" * 80)
    print(f"{'Book Name':<25} {'Flag':<8} {'PDF':<6} {'Word':<6} {'Teacher':<8}")
    print("=" * 80)

    for book in data.get('books', []):
        pdf_status = book.get('endpoints', {}).get('pdf_200', {}).get('status', 'N/A')
        word_status = book.get('endpoints', {}).get('word_200', {}).get('status', 'N/A')
        teacher_status = book.get('endpoints', {}).get('teacher_pdf', {}).get('status', 'N/A')
        print(f"{book.get('name', 'unknown'):<25} {str(book.get('flag_state')):<8} {pdf_status:<6} {word_status:<6} {teacher_status:<8}")

    print("=" * 80)
except Exception as e:
    print(f"Error: {e}")
