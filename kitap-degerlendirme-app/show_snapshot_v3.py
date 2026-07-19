import json

with open('snapshot_v3.json', 'r', encoding='utf-8-sig', errors='ignore') as f:
    data = json.load(f)

print("\n" + "="*80)
print(f"{'Book Name':<25} {'Flag':<8} {'PDF':<6} {'Word':<6} {'Teacher':<8}")
print("="*80)

for book in data.get('books', []):
    pdf = book.get('endpoints', {}).get('pdf_200', {}).get('status', 'N/A')
    word = book.get('endpoints', {}).get('word_200', {}).get('status', 'N/A')
    teacher = book.get('endpoints', {}).get('teacher_pdf', {}).get('status', 'N/A')
    print(f"{book.get('name', 'unknown'):<25} {str(book.get('flag_state')):<8} {pdf:<6} {word:<6} {teacher:<8}")

print("="*80)
