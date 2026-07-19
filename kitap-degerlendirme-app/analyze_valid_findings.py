#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anahtar_Acmaz.pdf için SADECE VALID bulguları göster.
FALSE POSITIVE'ler ve detaylı kontekst analizi.
"""

from pdf_processor import PDFProcessor
from evaluator_maarif import MaarifDegerlendiricisi
from config import SAKINCALI_KELIMELER, FALSE_POSITIVE_FILTER
import json

pdf_path = "uploads/Anahtar_Acmaz.pdf"
print(f"📖 PDF Okunuyor: {pdf_path}")
processor = PDFProcessor(pdf_path)
metin = processor.extract_text()
print(f"✅ PDF okundu: {len(metin)} karakter\n")

# Analiz et
print("🔍 Maarif Modeli Analizi Başlıyor...\n")
evaluator = MaarifDegerlendiricisi()

# Manuel analiz - FALSE POSITIVE'leri sayalım
from collections import defaultdict

category_keywords = defaultdict(lambda: defaultdict(int))
false_positives = defaultdict(int)
valid_findings = defaultdict(lambda: defaultdict(list))

metin_lower = metin.lower()

# Tüm kategorileri tara
for kategori, kelimeler in SAKINCALI_KELIMELER.items():
    for kelime in kelimeler:
        kelime_lower = kelime.lower()
        
        # Metinde geçiş sayısını bul
        count = metin_lower.count(kelime_lower)
        if count == 0:
            continue
            
        # FALSE POSITIVE filter kontrol et
        is_false_positive = False
        if kelime in FALSE_POSITIVE_FILTER:
            filter_data = FALSE_POSITIVE_FILTER[kelime]
            
            # Aggressive filter kontrol
            if kelime in ["lan", "kan", "ayin", "vur", "ayıp", "kama", "duman", "panik", "kaçış", "alçak", "bira"]:
                # Character boundary check
                import re
                pattern = r'[a-zçğıöşüA-ZÇĞÍÖŞÜ]' + re.escape(kelime_lower) + r'[a-zçğıöşüA-ZÇĞÍÖŞÜ]'
                if not re.search(pattern, metin_lower):
                    is_false_positive = True
            
            # ek_sozler kontrol
            if not is_false_positive and 'ek_sozler' in filter_data:
                for sozcu in filter_data['ek_sozler']:
                    sozcu_lower = sozcu.lower()
                    if sozcu_lower in metin_lower and kelime_lower in sozcu_lower:
                        is_false_positive = True
                        false_positives[kelime] += metin_lower.count(sozcu_lower)
        
        if not is_false_positive:
            category_keywords[kategori][kelime] = count
            valid_findings[kategori][kelime] = count

print("\n" + "="*80)
print("VALID BULGULAR (FALSE POSITIVE'LER FİLTRELENDİKTEN SONRA)")
print("="*80)

total_valid = 0
for kategori in sorted(category_keywords.keys()):
    bulgular = category_keywords[kategori]
    if not bulgular:
        continue
    
    print(f"\n📌 {kategori.upper()}")
    for kelime, count in sorted(bulgular.items(), key=lambda x: -x[1]):
        total_valid += count
        print(f"   • {kelime:15} → {count:3} bulgu")

print(f"\n{'='*80}")
print(f"Toplam VALID Bulgu: {total_valid}")
print(f"{'='*80}")

# FALSE POSITIVE'leri göster
print("\n" + "="*80)
print("FALSE POSITIVE'LER (FİLTRELENEN)")
print("="*80)

total_fp = sum(false_positives.values())
for kelime in sorted(false_positives.keys(), key=lambda x: -false_positives[x]):
    print(f"❌ {kelime:15} → {false_positives[kelime]:3} FALSE POSITIVE")

print(f"\n{'='*80}")
print(f"Toplam Filtered FALSE POSITIVE: {total_fp}")
print(f"{'='*80}")

# Detaylı bulgular
print("\n" + "="*80)
print("SONUÇ VE ANALİZ")
print("="*80)
print(f"""
📊 Sistem İstatistikleri:
   • Total VALID Bulgular: {total_valid}
   • Filtered FALSE POSITIVE'ler: {total_fp}
   
🎯 Rapor Verisi:
   • Toplam Bulgu: 118
   • Risk Skoru: 45.26/100
   
🔎 Detay Gerekli Kelimeler:
   • "ölüm" - 31 bulgu (İstiklal Şarkısı bağlamı?)
   • "büyü" - 40 bulgu (Fantazi/Masala bağlamı?)
   • "ulan" - 6 bulgu (Hakaret olarak kullanılıyor mu?)
   • "alay" - 5 bulgu (İstihza olarak mı?)
   • "rakı" - 11 bulgu (Tarihi/kültürel bağlam)
""")

print("\n⚠️  Öneriler:")
print("   1. Kontekst analizi genişletilmeli")
print("   2. Tarihi/milli metinler için harmless pattern'lar eklenebilir")
print("   3. Fantazi/masala için ayrı pattern'lar gerekli")
