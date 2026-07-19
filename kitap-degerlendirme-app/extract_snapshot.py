import re
import json

# Read the snapshot file and extract JSON
with open('snapshot_v3.json', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find all JSON objects (starting with { and ending with })
# We're looking for the main data structure
matches = list(re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content))
print(f"Found {len(matches)} potential JSON objects")

# Try the last one - it should be the complete result
if matches:
    for match in reversed(matches[-5:]):
        try:
            json_str = match.group()
            data = json.loads(json_str)
            if 'books' in data:
                print("\nFound books structure!")
                print("\n" + "="*80)
                print(f"{'Book Name':<25} {'Flag':<8} {'PDF':<6} {'Word':<6} {'Teacher':<8}")
                print("="*80)
                for book in data.get('books', []):
                    pdf = book.get('endpoints', {}).get('pdf_200', {}).get('status', 'N/A')
                    word = book.get('endpoints', {}).get('word_200', {}).get('status', 'N/A')
                    teacher = book.get('endpoints', {}).get('teacher_pdf', {}).get('status', 'N/A')
                    print(f"{book.get('name', 'unknown'):<25} {str(book.get('flag_state')):<8} {pdf:<6} {word:<6} {teacher:<8}")
                print("="*80)
                break
        except json.JSONDecodeError:
            continue
else:
    print("No JSON objects found")
