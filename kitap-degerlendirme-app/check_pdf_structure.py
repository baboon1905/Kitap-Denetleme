#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Check the actual PDF structure and all text
"""

import pdfplumber

try:
    with pdfplumber.open('debug_output.pdf') as pdf:
        print(f"PDF Pages: {len(pdf.pages)}")
        
        # Get ALL text
        all_text = ""
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            all_text += text
            print(f"\nPAGE {page_num + 1}:")
            print(text[:300])
        
        print("\n" + "=" * 60)
        print("FULL PDF STRUCTURE CHECK:")
        print("=" * 60)
        
        # Look for section numbers
        lines = all_text.split('\n')
        for i, line in enumerate(lines):
            if any(x in line for x in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', 'MEB', 'Detayli', 'Bulgu']):
                print(f"Line {i}: {line}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
