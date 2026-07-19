import json

# Check Sprint 8C data
with open('rc4_sprint8c_mapping_integration_results.json') as f:
    sprint8c = json.load(f)
    books = sprint8c.get('books', [])
    if books:
        first_book = books[0]
        traces = first_book.get('synthesized_trace', [])
        print(f"First book: {first_book.get('title')}")
        print(f"Total traces: {len(traces)}")
        
        # Check source_sentence_ids
        source_ids = []
        for trace in traces[:10]:
            source_id = trace.get('source_sentence_id', 'MISSING')
            source_ids.append(source_id)
        
        print(f"\nFirst 10 source_sentence_ids:")
        for i, sid in enumerate(source_ids, 1):
            print(f"  {i}. {sid}")
        
        # Count how many have non-empty source_ids
        non_empty = sum(1 for trace in traces if trace.get('source_sentence_id'))
        print(f"\nNon-empty source_ids: {non_empty}/{len(traces)}")


