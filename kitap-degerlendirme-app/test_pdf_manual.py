#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Yükleme ve Analiz Test
"""

from evaluator_maarif import MaarifDegerlendiricisi
from pdf_processor import PDFProcessor
import os

print("=" * 60)
print("PDF YÜKLEME VE ANALIZ TEST")
print("=" * 60)

# uploads klasöründeki dosyaları kontrol et
uploads_dir = 'uploads'
pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]

print(f"\n📁 Toplam PDF dosyası: {len(pdf_files)}")
print(f"En son yüklenen: {pdf_files[-1]}\n")

# En son dosyayı analiz et
test_file = os.path.join(uploads_dir, pdf_files[-1])

print(f"📄 Analiz Edilen Dosya: {pdf_files[-1]}")
print(f"📏 Dosya Boyutu: {os.path.getsize(test_file) / 1024 / 1024:.1f} MB\n")

try:
    # PDF'den metni çıkar
    print("1️⃣ PDF metni çıkarılıyor...")
    processor = PDFProcessor(test_file)
    metin = processor.extract_text()
    print(f"   ✅ {len(metin)} karakter metni çıkarıldı")
    
    if len(metin) < 50:
        print(f"   ⚠️  UYARI: Çok kısa metin ({len(metin)} karakter)")
        print(f"   Metin: {metin[:100]}")
    else:
        print(f"   İlk 150 karakter: {metin[:150]}...")
    
    # Analiz yap
    print("\n2️⃣ Analiz yapılıyor...")
    evaluator = MaarifDegerlendiricisi()
    
    # İlk 5000 karakteri analiz et
    test_metin = metin[:5000] if len(metin) > 5000 else metin
    
    sonuc = evaluator.analiz_yap(test_metin, profil='hibrit', yas_grubu='12-15')
    
    print(f"   ✅ Analiz başarılı!\n")
    
    # Sonuçları göster
    print("📊 SONUÇLAR:")
    print(f"   Risk Skoru: {sonuc['final_skor']}/100")
    print(f"   Karar: {sonuc['karar']}")
    print(f"   Kategori Bulgusu Sayısı: {len(sonuc.get('kategori_bulgulari', {}))}")
    
    # Bulunan kategorileri göster
    if 'kategori_bulgulari' in sonuc and sonuc['kategori_bulgulari']:
        print(f"\n   Bulunan Kategoriler:")
        for kat, info in list(sonuc['kategori_bulgulari'].items())[:5]:
            print(f"      • {kat}: {info.get('toplam_bulgu', 0)} bulgu, Risk: {info.get('ortalama_risk', 0)}")
    
    print("\n✅ HER ŞEY BAŞARILI!")
    
except Exception as e:
    import traceback
    print(f"\n❌ HATA: {type(e).__name__}")
    print(f"   Mesaj: {str(e)}\n")
    print("📍 Hata Detayları:")
    traceback.print_exc()
