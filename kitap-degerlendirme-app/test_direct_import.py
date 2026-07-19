#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Direct test: Evaluator'ı directly test et
"""

from pathlib import Path
from evaluator_maarif import MaarifDegerlendiricisi
from pdf_processor import PDFProcessor

pdf_path = r"uploads\10_sihirli_duduk.pdf"

print("=" * 70)
print("🧪 DIRECT TEST: Evaluator FALSE POSITIVE Filter")
print("=" * 70)

# 1. PDF işle
print("\n1️⃣ PDF İşleniyor...")
processor = PDFProcessor(pdf_path)
metin = processor.extract_text()
metadata = processor.extract_metadata()
print(f"✅ {len(metin)} karakter metin çıkarıldı")

# 2. Evaluator'ı çalıştır
print("\n2️⃣ Maarif Modeli Analiz Yapılıyor...")
evaluator = MaarifDegerlendiricisi()
sonuc = evaluator.analiz_yap(metin, profil="hibrit", yas_grubu="9-12")

# 3. Sonuçları göster
print("\n3️⃣ Sonuçlar:")
risk_skoru = sonuc.get('risk_skoru', 0)
karar = sonuc.get('karar', '')
kategori_bulgulari = sonuc.get('kategori_bulgulari', {})

print(f"   Risk Skoru: {risk_skoru}/100")
print(f"   Karar: {karar}")

print("\n   📋 Kategori Bulguları:")
total_findings = 0
for kategori, bulgular in kategori_bulgulari.items():
    toplam = bulgular.get('toplam_bulgu', 0)
    risk = bulgular.get('ortalama_risk', 0)
    total_findings += toplam
    if toplam > 0:
        print(f"      {kategori}: {toplam} bulgu (Ort. Risk: {risk:.1f}/5)")
        
        # Kelimeleri listele
        bulunan = bulgular.get('bulunan_kelimeler', [])
        for i, bulgu in enumerate(bulunan):
            kelime = bulgu.get('kelime', '?')
            if i < 10:  # İlk 10'u göster
                print(f"         - '{kelime}'")
        
        if len(bulunan) > 10:
            print(f"         ... ve {len(bulunan) - 10} daha")
    print(f"      Çoğu filtered ama bazıları geçti")
else:
    print(f"   ❌ BAŞARISIZ: Filter çalışmıyor!")
    print(f"      Risk {risk_skoru}, Bulgu {total_findings}")

print("\n" + "=" * 70)
