#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extract ALL text from generated PDF
"""

import pdfplumber

# Open the most recently generated PDF
pdf_path = 'debug_output.pdf'

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"PDF has {len(pdf.pages)} pages\n")
        
        full_text = ""
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            full_text += text + "\n--- PAGE BREAK ---\n"
            print(f"=== PAGE {page_num + 1} ===")
            print(text)
            print("\n")
        
        print("\n" + "=" * 60)
        print("Full text analysis:")
        print("=" * 60)
        
        if "4.1" in full_text:
            print("✅ '4.1' found in text")
        else:
            print("❌ '4.1' NOT found in text")
        
        if "Detayli" in full_text:
            print("✅ 'Detayli' found in text")
        else:
            print("❌ 'Detayli' NOT found in text")
        
        if "Bulgu" in full_text:
            print("✅ 'Bulgu' found in text")
        else:
            print("❌ 'Bulgu' NOT found in text")
        
        # Check for "MEB" section
        if "MEB TTK" in full_text:
            print("✅ 'MEB TTK' found in text")
            # Find the section
            lines = full_text.split('\n')
            for i, line in enumerate(lines):
                if "MEB TTK" in line:
                    print(f"\n   Found at line {i}:")
                    for j in range(max(0, i), min(len(lines), i + 20)):
                        print(f"   {lines[j]}")
                    break
        else:
            print("❌ 'MEB TTK' NOT found in text")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
