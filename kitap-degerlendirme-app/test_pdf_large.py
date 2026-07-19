#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Yükleme ve Analiz Test - Büyük Dosya
"""

from evaluator_maarif import MaarifDegerlendiricisi
from pdf_processor import PDFProcessor
import os

print("=" * 70)
print("PDF YÜKLEME VE ANALIZ TEST - BÜYÜK DOSYA")
print("=" * 70)

# uploads klasöründeki dosyaları kontrol et
uploads_dir = 'uploads'
pdf_files = sorted([f for f in os.listdir(uploads_dir) if f.endswith('.pdf')], 
                    key=lambda x: os.path.getsize(os.path.join(uploads_dir, x)), reverse=True)

print(f"\n📁 Yüklü PDF Dosyaları (Boyuta Göre):")
for i, f in enumerate(pdf_files[:3], 1):
    size_mb = os.path.getsize(os.path.join(uploads_dir, f)) / 1024 / 1024
    print(f"   {i}. {f} ({size_mb:.1f} MB)")

# En büyük dosyayı analiz et
test_file = os.path.join(uploads_dir, pdf_files[0])

print(f"\n📄 Seçilen Dosya: {pdf_files[0]}")
print(f"📏 Dosya Boyutu: {os.path.getsize(test_file) / 1024 / 1024:.1f} MB\n")

try:
    # PDF'den metni çıkar
    print("1️⃣ PDF metni çıkarılıyor...")
    processor = PDFProcessor(test_file)
    metin = processor.extract_text()
    sayfa_sayisi = processor.sayfa_sayisi
    print(f"   ✅ {len(metin)} karakter metni çıkarıldı ({sayfa_sayisi} sayfa)")
    
    if len(metin) > 50:
        print(f"   📖 İlk 200 karakter: {metin[:200].strip()}...\n")
    
    # Analiz yap
    print("2️⃣ Analiz yapılıyor (Hibrit Profili)...")
    evaluator = MaarifDegerlendiricisi()
    
    # İlk 8000 karakteri analiz et
    test_metin = metin[:8000] if len(metin) > 8000 else metin
    
    sonuc = evaluator.analiz_yap(test_metin, profil='hibrit', yas_grubu='12-15')
    
    print(f"   ✅ Analiz başarılı!\n")
    
    # Sonuçları göster
    print("📊 ANALIZ SONUÇLARI:")
    print(f"   Risk Skoru: {sonuc['final_skor']}/100")
    karar = sonuc['karar']
    if isinstance(karar, dict):
        print(f"   Karar: {karar.get('seviye', karar)}")
    else:
        print(f"   Karar: {karar}")
    
    # Kategori bulguları
    kategori_bulgulari = sonuc.get('kategori_bulgulari', {})
    if kategori_bulgulari:
        print(f"\n   📋 Kategori Bulguları:")
        for kat, info in list(kategori_bulgulari.items())[:7]:
            bulgu_sayisi = info.get('toplam_bulgu', 0)
            ort_risk = info.get('ortalama_risk', 0)
            if bulgu_sayisi > 0:
                print(f"      • {kat}: {bulgu_sayisi} bulgu, Ort. Risk: {ort_risk:.1f}/5")
    
    # Maarif profilleri
    maarif = sonuc.get('maarif_profilleri', {})
    if maarif:
        print(f"\n   🎓 Maarif Profilleri (Top 5):")
        sorted_profiller = sorted(maarif.items(), key=lambda x: x[1], reverse=True)[:5]
        for profil, skor in sorted_profiller:
            print(f"      • {profil}: {skor}/5")
    
    print("\n✅ HER ŞEY BAŞARILI!")
    
except Exception as e:
    import traceback
    print(f"\n❌ HATA: {type(e).__name__}")
    print(f"   Mesaj: {str(e)}\n")
    print("📍 Hata Detayları:")
    traceback.print_exc()
