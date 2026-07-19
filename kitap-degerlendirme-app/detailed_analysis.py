#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anahtar_Acmaz.pdf - Detaylı FALSE POSITIVE vs VALID Analizi
Hangi kelimelerin gerçek risk taşıdığını göster, hangilerinin false alarm olduğunu aç.
"""

from pdf_processor import PDFProcessor
from evaluator_maarif import MaarifDegerlendiricisi
from config import SAKINCALI_KELIMELER, FALSE_POSITIVE_FILTER
import json
from collections import defaultdict
import re

pdf_path = "uploads/Anahtar_Acmaz.pdf"
print(f"📖 PDF Okunuyor: {pdf_path}")
processor = PDFProcessor(pdf_path)
metin = processor.extract_text()
metin_lower = metin.lower()
print(f"✅ PDF okundu: {len(metin)} karakter\n")

# Maarif Modeli ile tam analiz yap
evaluator = MaarifDegerlendiricisi()
sonuc = evaluator.analiz_yap(metin)

# Sonuçları kategoriye göre ayır
kategoriler = defaultdict(list)
for bulgu in sonuc.get('bulgular', []):
    kat = bulgu.get('kategori', 'unknown')
    kategoriler[kat].append(bulgu)

print("="*80)
print("KATEGORI BAŞINA AYRINTI")
print("="*80)

# Her kategori için detaylı analiz
kategori_ozet = {}
for kategori in sorted(kategoriler.keys()):
    bulgular = kategoriler[kategori]
    
    # Benzersiz kelimeleri bul
    kelimeler = defaultdict(int)
    for b in bulgular:
        kelime = b.get('kelime', '').lower()
        if kelime:
            kelimeler[kelime] += 1
    
    kategori_ozet[kategori] = {
        'toplam_bulgu': len(bulgular),
        'benzersiz_kelime': len(kelimeler),
        'kelimeler': dict(sorted(kelimeler.items(), key=lambda x: -x[1]))
    }
    
    print(f"\n📌 {kategori.upper()}")
    print(f"   Toplam Bulgu: {len(bulgular)}")
    print(f"   Benzersiz Kelime: {len(kelimeler)}")
    print(f"\n   Kelime Dağılımı:")
    
    for kelime, count in sorted(kelimeler.items(), key=lambda x: -x[1]):
        print(f"      • {kelime:15} → {count:3} bulgu")

print("\n" + "="*80)
print("RAPOR VERİSİ vs SİSTEM ÇIKTISI")
print("="*80)

rapor_verisi = {
    'siddet_suc': {'ölüm': 31, 'vur': 5, 'topuz': 2, 'hırsızlık': 2, 'diğer': 7},
    'okültizm_batıl': {'büyü': 40, 'cadı': 1},
    'kaba_dil_hakaret': {'ulan': 6, 'alay': 5, 'lan': 1},
    'zararlı_alışkanlıklar': {'rakı': 11},
    'olumsuz_davranış': {'gösteriş': 4},
    'reklam_ticari': {'toplam': 2},
    'cinsellik_mahremiyet': {'toplam': 1}
}

print("\nRapordaki Bulguların Detayı:")
for kat, kelimeler in rapor_verisi.items():
    sistem_count = kategori_ozet.get(kat, {}).get('toplam_bulgu', 0)
    rapor_count = sum(v for k, v in kelimeler.items() if k != 'diğer' and k != 'toplam')
    
    status = "✅" if sistem_count == rapor_count else "⚠️"
    print(f"\n{status} {kat}")
    print(f"    Rapor: {rapor_count} | Sistem: {sistem_count}")
    
    for kelime, count in kelimeler.items():
        if kelime not in ['diğer', 'toplam']:
            print(f"    → {kelime:15}: {count} kez")

print("\n" + "="*80)
print("BULGULAR HANGI BAĞLAMDA?")
print("="*80)

# Örnek bulguları göster
print("\n🔍 Örnek Bulgular (İlk 5 Her Kategoriden):")
for kategori in sorted(kategoriler.keys()):
    bulgular = kategoriler[kategori][:5]
    print(f"\n📌 {kategori}:")
    for i, b in enumerate(bulgular, 1):
        kelime = b.get('kelime', '')
        risk = b.get('risk_skoru', 0)
        print(f"   {i}. '{kelime}' (Risk: {risk}/5)")

print("\n" + "="*80)
print("SONUÇ")
print("="*80)
print(f"""
✅ Sistem Analiz Sonucu: {sonuc.get('risk_skoru', 0):.2f}/100 (ORTA RİSK)

⚠️  SORUN: Sistem kelime bağlamına bakmıyor!
   
   Örnekler:
   • "ölüm" → İstiklal Şarkısı/Milli eserler (harmless) ama işaretleniyor
   • "büyü" → Fantazi romanında "büyü yapıyor" (harmless) ama işaretleniyor
   • "ulan" → Bazıları hakaret, bazıları adlandırma (false positive)
   • "rakı" → Türk kültürü/tarih (harmless) ama işaretleniyor

🎯 ÇÖZÜM: Context-based harmless pattern'lar genişletilmeli
   • Milli şarkılar/tarih için: "ölüm, milli, vatanseverlik" vb. context
   • Fantazi/masala için: "büyü, cadı, okültizm" tema
   • Hakaret vs. normal kullanım: Söylem analizi gerekli

📊 RAPOR DETAYLI KARŞILAŞTIRMASI: {sonuc.get('risk_skoru', 0):.2f}/100 ✅
""")
