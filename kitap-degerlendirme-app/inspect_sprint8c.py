import json

with open('rc4_sprint8c_mapping_integration_results.json') as f:
    data = json.load(f)
    print('Sprint:', data.get('sprint'))
    print('Total books:', data.get('total_books'))
    print('\nBooks in data:')
    books = data.get('books', [])
    for book in books:
        print(f"  - {book.get('book_title')} ({len(book.get('evidence_snippets', []))} evidence)")
    
    print('\n\nAll books details:')
    for i, book in enumerate(books, 1):
        print(f'\n{i}. File: {book["file"]}')
        print(f'   Title: {book["title"]}')
        traces = book.get('synthesized_trace', [])
        print(f'   Traces: {len(traces)}')
        
        # Try to get book name from builder_output
        builder = book.get('builder_output', {})
        if 'book_title' in builder:
            print(f'   book_title: {builder["book_title"]}')
        
        # Check evaluation
        eval_data = book.get('evaluation', {})
        if 'book_title' in eval_data:
            print(f'   eval book_title: {eval_data["book_title"]}')
        
        # Show first trace if available
        if traces:
            print(f'   First trace source_id: {traces[0].get("source_sentence_id", "N/A")}')

