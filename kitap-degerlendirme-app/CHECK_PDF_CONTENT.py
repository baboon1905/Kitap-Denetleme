#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF İçeriğini Kontrol Et
"""

try:
    import PyPDF2
    
    pdf_file = "FINAL_TEST_MEB_BULGULARI.pdf"
    with open(pdf_file, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        print(f"PDF Sayfa Sayısı: {len(reader.pages)}")
        print()
        
        # 4. sayfayı kontrol et (genellikle MEB bölümü burada olur)
        for page_num in range(min(3, len(reader.pages))):
            print(f"--- SAYFA {page_num + 1} ---")
            page = reader.pages[page_num]
            text = page.extract_text()
            
            # Anahtar sözcükler ara
            if "MEB" in text:
                print("✅ MEB bölümü bulundu")
            if "Detayli Bulgu" in text or "4.1" in text:
                print("✅ Detayli Bulgu bölümü bulundu")
            if "PKK" in text:
                print("✅ Bulgular mevcut")
            
            # İlk 500 karakteri göster
            print(text[:500])
            print()
            
except ImportError:
    print("PyPDF2 yüklü değil. pip install PyPDF2 çalıştırın.")
    print()
    print("Alternatif: PDF dosyasını doğrudan açın: FINAL_TEST_MEB_BULGULARI.pdf")
