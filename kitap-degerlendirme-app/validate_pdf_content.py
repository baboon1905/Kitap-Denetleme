#!/usr/bin/env python
"""
Oluşturulan PDF'nin içeriğini doğrula: Türkçe karakterler ve tavsiye bölümü
"""

try:
    from PyPDF2 import PdfReader
except ImportError:
    print("PyPDF2 kurulu değil, elle doğrulama yapılması gerekir")
    exit(0)

import os

# Son oluşturulan PDF'yi bulma
pdf_dir = "."
pdf_files = [f for f in os.listdir(pdf_dir) if f.startswith("test_rapor_turkce") and f.endswith(".pdf")]
if not pdf_files:
    print("❌ PDF dosyası bulunamadı!")
    exit(1)

# En son dosyayı seç
latest_pdf = sorted(pdf_files)[-1]
pdf_path = os.path.join(pdf_dir, latest_pdf)

print("=" * 70)
print("📄 PDF İÇERİĞİ DOĞRULAMASI")
print("=" * 70)
print(f"\n📋 Dosya: {latest_pdf}")
print(f"   Boyut: {os.path.getsize(pdf_path):,} bytes")

try:
    # PDF'yi oku
    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)
    print(f"   Sayfa Sayısı: {num_pages}")
    
    # Tüm sayfaların metnini çıkart
    all_text = ""
    for page in reader.pages:
        all_text += page.extract_text()
    
    print("\n✅ PDF BAŞARIYLA OKUNDU")
    
    # Kontrol et
    print("\n📌 Türkçe Karakterler Kontrol:")
    turkce_keywords = [
        ("SAKİNÇALI İÇERİK", "Başlık"),
        ("Şiddet", "Şiddet kategorisi"),
        ("Cinsellik", "Cinsellik kategorisi"),
        ("Okültizm", "Okültizm kategorisi"),
        ("Öneriler", "Öneriler bölümü"),
        ("Tespit Edilen Sorunlarla", "Kategori bazlı tavsiye bölümü"),
        ("Tavsiye", "Tavsiye kelimesi"),
    ]
    
    for keyword, description in turkce_keywords:
        if keyword in all_text:
            print(f"   ✅ '{keyword}' bulundu - {description}")
        else:
            print(f"   ⚠️  '{keyword}' BULUNAMADI - {description}")
    
    # Tavsiye bölümünü kontrol et
    print("\n📌 Kategori Bazlı Tavsiye Bölümü:")
    tavsiye_keywords = [
        "Şiddetçi",
        "Cinsel içerik",
        "Batıl inanış",
        "gözden geçirilmeli",
        "düzeltilmelidir",
    ]
    
    found_recommendations = 0
    for keyword in tavsiye_keywords:
        if keyword in all_text:
            found_recommendations += 1
            print(f"   ✅ '{keyword}' bulundu")
    
    if found_recommendations >= 3:
        print(f"\n   ✅ Kategori bazlı tavsiye bölümü BAŞARILI ({found_recommendations}/5)")
    else:
        print(f"\n   ⚠️  Kategori bazlı tavsiye bölümü eksik olabilir ({found_recommendations}/5)")
    
    print("\n" + "=" * 70)
    print("✅ DOĞRULAMA TAMAMLANDI")
    print("=" * 70)
    
except Exception as e:
    print(f"❌ Hata: {e}")
    print("   PDF dosyası elle açılarak kontrol edilmelidir")
