#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALID kalan bulgulara context bakalım.
"ölüm" (31), "büyü" (40) vb. hangi bağlamda kullanılıyor?
"""

from pdf_processor import PDFProcessor
from config import SAKINCALI_KELIMELER, FALSE_POSITIVE_FILTER
import re

pdf_path = "uploads/Anahtar_Acmaz.pdf"
processor = PDFProcessor(pdf_path)
metin = processor.extract_text()
metin_lower = metin.lower()

# Analiz edilecek ana kelimeler ve bağlamları
ana_kelimeler = {
    'ölüm': 31,      # Rapor: 31 bulgu
    'büyü': 40,      # Rapor: 40 bulgu  
    'ulan': 6,       # Rapor: 6 bulgu
    'alay': 5,       # Rapor: 5 bulgu
    'rakı': 11,      # Rapor: 11 bulgu
}

# Harmless context patterns
harmless_patterns = {
    'ölüm': [
        'şarkı', 'marş', 'istiklal', 'milli', 'vatan', 'tarih', 'fetih', 'savaş',
        'roman', 'hikaye', 'öykü', 'masala', 'efsane', 'destan', 'kitap'
    ],
    'büyü': [
        'fantazi', 'masala', 'roman', 'peri', 'dev', 'cin', 'efsane', 'hikaye',
        'masal', 'öykü', 'kitap', 'sanat', 'tasarım', 'ressam', 'sanatçı', 'desen'
    ],
    'rakı': [
        'türk', 'kültür', 'tarih', 'geleneksel', 'milli', 'gelenek', 'medeniyет'
    ],
    'alay': [
        'roman', 'hikaye', 'karakter', 'kişi', 'yüzü', 'tavır', 'davranış', 'tonu'
    ],
}

print("="*80)
print("CONTEXT ANALIZI - HARMLESS vs RİSKLİ")
print("="*80)

for kelime, bulgu_sayisi in ana_kelimeler.items():
    print(f"\n📌 '{kelime}' ({bulgu_sayisi} bulgu)")
    print("-" * 80)
    
    # Metinde örnekler bul (çevrede 100 char)
    kelime_lower = kelime.lower()
    pos = 0
    ornekler = []
    
    while True:
        idx = metin_lower.find(kelime_lower, pos)
        if idx == -1:
            break
        
        # Önceki 50 karakter
        start = max(0, idx - 50)
        # Sonraki 50 karakter
        end = min(len(metin), idx + len(kelime_lower) + 50)
        
        context = metin[start:end].strip()
        # Satır sonlarını kaldır
        context = ' '.join(context.split())
        
        ornekler.append({
            'context': context,
            'pos': idx
        })
        
        pos = idx + 1
    
    # İlk 5 örneği göster
    print(f"   Toplam örnek: {len(ornekler)}")
    print(f"\n   İlk 5 Örnek:")
    
    for i, ornek in enumerate(ornekler[:5], 1):
        context = ornek['context']
        # Kelimeyi highlight et
        highlighted = context.replace(kelime_lower, f'[{kelime_lower.upper()}]')
        print(f"\n   {i}. ...{highlighted}...")
        
        # Context check
        context_lower = context.lower()
        harmless_bulundu = []
        if kelime in harmless_patterns:
            for pattern in harmless_patterns[kelime]:
                if pattern in context_lower:
                    harmless_bulundu.append(pattern)
        
        if harmless_bulundu:
            print(f"      ✅ HARMLESS CONTEXT: {', '.join(harmless_bulundu)}")
        else:
            print(f"      ⚠️  RİSKLİ CONTEXT: Bağlam belirsiz")

print("\n" + "="*80)
print("SONUÇ")
print("="*80)
print("""
🔍 Sonuç:
   • Kalan 118 bulgu CONTEXT'e göre risk taşıyor mu?
   • Harmless pattern'lar genişletilmeli mi?
   • İstiklal Şarkısı, fantazi, tarih bağlamları düşük risk mi?
   
💡 Yapılması Gerekenler:
   1. Context patterns'ları genişlet
   2. Risk skorunu context'e göre ayarla
   3. Kategori başına threshold ayarla
   
📊 Rapor Analizi:
   • 45.26/100 ORTA RİSK
   • Kültürel Uyum: 80/100 (Yüksek - sistem anlıyor!)
   • MEB Uyum: 10/100 (Düşük - eğitim standartları sıkı)
""")
