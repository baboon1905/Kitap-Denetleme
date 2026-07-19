#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compare direct PDF vs API PDF
"""

import pdfplumber

print("="*60)
print("PDF Comparison")
print("="*60)

# Direct PDF
print("\n1. DIRECT PDF (test_direct_output.pdf):")
with pdfplumber.open('test_direct_output.pdf') as pdf:
    full_text = ""
    for page in pdf.pages:
        full_text += (page.extract_text() or "") + "\n"
    
    print(f"   Pages: {len(pdf.pages)}")
    print(f"   Text length: {len(full_text)}")
    print(f"   Has 4.1: {'✅' if '4.1' in full_text else '❌'}")
    print(f"   Has Detayli: {'✅' if 'Detayli' in full_text else '❌'}")

# API PDF  
print("\n2. API PDF (debug_output.pdf):")
with pdfplumber.open('debug_output.pdf') as pdf:
    full_text = ""
    for page in pdf.pages:
        full_text += (page.extract_text() or "") + "\n"
    
    print(f"   Pages: {len(pdf.pages)}")
    print(f"   Text length: {len(full_text)}")
    print(f"   Has 4.1: {'✅' if '4.1' in full_text else '❌'}")
    print(f"   Has Detayli: {'✅' if 'Detayli' in full_text else '❌'}")

print("\n" + "="*60)
