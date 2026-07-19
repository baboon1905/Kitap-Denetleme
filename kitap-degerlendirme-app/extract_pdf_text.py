#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pdfplumber

pdf_path = "test_fallback_risky_report.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"PDF has {len(pdf.pages)} pages\n")
    
    for page_num, page in enumerate(pdf.pages, 1):
        text = page.extract_text()
        print(f"===== PAGE {page_num} =====")
        print(text[:2000] if text else "[No text]")
        print("\n")
        
        # Check for 4.1
        if text and "4.1" in text:
            print(f"✅ Found '4.1' on page {page_num}")
            # Show context
            idx = text.find("4.1")
            print(f"Context: ...{text[max(0, idx-50):idx+100]}...")
            print()
