#!/usr/bin/env python3
# Test if 4.1 section exists in PDF

from PyPDF2 import PdfReader

reader = PdfReader('debug_output.pdf')
print(f"Total pages: {len(reader.pages)}")
print()

for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if '4.1' in text or 'Detayli' in text or 'Bulgular' in text:
        print(f"✅ Page {i+1}: Found 4.1-related text")
        print(text[:1000])
        print()
    else:
        print(f"❌ Page {i+1}: No 4.1-related text")
        
print("\n=== Searching full text for 4.1 ===")
full_text = "\n".join([page.extract_text() for page in reader.pages])
if '4.1' in full_text:
    print("✅ '4.1' found in PDF")
    idx = full_text.find('4.1')
    print(full_text[max(0, idx-100):idx+200])
else:
    print("❌ '4.1' NOT found in PDF")

if 'Detayli Bulgu' in full_text or 'Detayli' in full_text:
    print("✅ 'Detayli' found in PDF")
else:
    print("❌ 'Detayli' NOT found in PDF")
