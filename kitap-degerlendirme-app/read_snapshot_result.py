import json

# Try to read snapshot_result.json
with open('snapshot_result.json', 'rb') as f:
    # Read as bytes first and try different encodings
    content = f.read()
    
for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
    try:
        text = content.decode(encoding)
        data = json.loads(text)
        print("\n" + "="*80)
        print(f"{'Book Name':<25} {'Flag':<8} {'PDF':<6} {'Word':<6} {'Teacher':<8}")
        print("="*80)
        for name, results in data.items():
            if isinstance(results, dict):
                for flag_state, endpoints in results.items():
                    if isinstance(endpoints, dict):
                        pdf = endpoints.get('pdf_endpoint_status', 'N/A')
                        word = endpoints.get('word_endpoint_status', 'N/A')
                        teacher = endpoints.get('teacher_endpoint_status', 'N/A')
                        print(f"{name:<25} {flag_state[-5:]:<8} {pdf:<6} {word:<6} {teacher:<8}")
        print("="*80)
        break
    except Exception as e:
        print(f"Failed with {encoding}: {str(e)[:80]}")
