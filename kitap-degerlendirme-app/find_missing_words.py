#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rapor ile sistem karşılaştırması - Hangi kelimelerde fark var?
"""

from pdf_processor import PDFProcessor
from evaluator_maarif import MaarifDegerlendiricisi

pdf_path = "uploads/Anahtar_Acmaz.pdf"
processor = PDFProcessor(pdf_path)
metin = processor.extract_text()

evaluator = MaarifDegerlendiricisi()
sonuc = evaluator.analiz_yap(metin)

# Rapor verisi
rapor_data = {
    'siddet_suc': {'ölüm': 31, 'vur': 5, 'topuz': 2, 'hırsızlık': 2, 'diğer': 7},
    'okültizm_batıl': {'büyü': 40, 'cadı': 1},
    'kaba_dil_hakaret': {'ulan': 6, 'alay': 5, 'lan': 1},
    'zararlı_alışkanlıklar': {'rakı': 11},
    'olumsuz_davranış': {'gösteriş': 4},
    'reklam_ticari': 2,
    'cinsellik_mahremiyet': 1
}

# Sistem verisi - kategoriye göre kelimeleri sayı
sistem_data = {}
for bulgu in sonuc.get('bulgular', []):
    kat = bulgu.get('kategori')
    kelime = bulgu.get('kelime', '').lower()
    
    if kat not in sistem_data:
        sistem_data[kat] = {}
    
    sistem_data[kat][kelime] = sistem_data[kat].get(kelime, 0) + 1

print("=" * 80)
print("RAPOR vs SİSTEM KARŞILAŞTIRMASI")
print("=" * 80)

for kat in ['siddet_suc', 'okültizm_batıl', 'kaba_dil_hakaret', 'zararlı_alışkanlıklar']:
    rapor_items = rapor_data.get(kat, {})
    sistem_items = sistem_data.get(kat, {})
    
    print(f"\n📌 {kat}")
    print("-" * 80)
    
    if isinstance(rapor_items, dict):
        for kelime, rapor_count in sorted(rapor_items.items(), key=lambda x: -x[1]):
            if kelime == 'diğer':
                continue
            sistem_count = sistem_items.get(kelime, 0)
            fark = sistem_count - rapor_count
            
            status = "✅" if sistem_count == rapor_count else "⚠️"
            print(f"   {status} {kelime:15} Rapor: {rapor_count:3}  Sistem: {sistem_count:3}  (Fark: {fark:+3})")
    else:
        print(f"   Total: Rapor={rapor_items}, Sistem={len(sistem_items)}")

print("\n" + "=" * 80)
print("SONUÇ")
print("=" * 80)

rapor_toplam = 118
sistem_toplam = sum(len(v) if isinstance(v, dict) else v for v in rapor_data.values())
aktual_sistem = sum(sum(v.values()) for v in sistem_data.values())

print(f"""
📊 Toplam Bulgu:
   • Rapor: {rapor_toplam}
   • Sistem: {aktual_sistem}
   • Fark: {rapor_toplam - aktual_sistem}

🔍 Fark Analizi:
   • "ölüm" (31) ve "büyü" (40) filtrelendi ✅
   • Ama 50 bulgu hâlâ eksik
   
💡 Yapılması Gerekenler:
   1. Sistem bulguları detaylı kontrol et
   2. Hangi kelimelerin eksik olduğunu bul
   3. Başka FALSE POSITIVE'ler mi var?
   4. FALSE_POSITIVE_FILTER'ı daha da genişlet
""")
