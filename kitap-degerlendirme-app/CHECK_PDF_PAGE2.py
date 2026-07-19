#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Sayfa 2 Tam İçerik
"""

try:
    import PyPDF2
    
    pdf_file = "FINAL_TEST_MEB_BULGULARI.pdf"
    with open(pdf_file, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        
        # Sayfa 2 (index 1) tam içerik
        print("=" * 80)
        print("SAYFA 2 TAM İÇERİK")
        print("=" * 80)
        page = reader.pages[1]
        text = page.extract_text()
        print(text)
        
except ImportError:
    print("PyPDF2 yüklü değil")
