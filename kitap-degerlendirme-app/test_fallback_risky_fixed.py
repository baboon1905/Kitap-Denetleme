#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')

from evaluator_maarif import MaarifDegerlendiricisi
from report_generator import RaporOlusturucu
import io

# Riskli metin - MEB kriterlerine aykırı içerik
riskli_metin = """
Cumhuriyet devleti, bunun için, işçi sınıfın iktidar olması gerekir çünkü kapitalizm 
patlayacaktır. Türkiye'de sosyalist sistem kurulmalıdır. Kemalist fikirleri yanlıştır.
Türk milletinin manevi değerleri yozlaşmıştır, herkes kendi işine bakmalı. Din geri kalmaya 
neden olur. Evlilik kurumu kıskaç gibidir, kadınlar ezilmiştir. Cinsel özgürlük doğaldır.
Bilim dini yok sayar, mantık dini çürütür. Bilim yanlıştır, insan içgüdüleriyle yaşamalı.
Bu ilaç markası en iyisidir, hemen satın alın! Apple ürünü olmadan yaşanamaz!
Küfürler: bok, siktir, allanı sikerim, amına kodum, orospu, piç, pezevenklik, sapıklık
Bu kitap ahlak dışı ve Türk değerlerine aykırıdır! Terörle baş etmek için silah lazım.
Çocukları bu tür kitaplardan uzak tutmalıyız, çünkü vatan sevgisini yok ediyor.
"""

print("=" * 60)
print("Test - Fallback ile Riskli Metin")
print("=" * 60)

# Evaluator ile analiz
print("\n1. Riskli metin analiz ediliyor...")
evaluator = MaarifDegerlendiricisi()
try:
    analiz_data = evaluator.analiz_yap(riskli_metin, profil='genel')
    print(f"   ✅ Analiz tamamlandı")
except Exception as e:
    print(f"   ❌ Hata: {e}")
    sys.exit(1)

# MEB bulgularını kontrol et
print(f"\n2. MEB Değerlendirmesi:")
meb_eval = analiz_data.get('meb_degerlendirmesi', {})
meb_bulgulari = meb_eval.get('meb_bulgulari', {})
meb_kriterler = meb_eval.get('meb_kriterler', {})

print(f"   Kriterler:")
for key, info in meb_kriterler.items():
    print(f"     {key}: risk={info.get('risk', 0)}/5 - {info.get('karar', 'N/A')}")

print(f"\n   meb_bulgulari: {bool(meb_bulgulari)}")
print(f"   meb_bulgulari dict: {meb_bulgulari}")

# PDF oluştur
print(f"\n3. PDF Rapor oluşturuluyor...")
rapor_generator = RaporOlusturucu()
pdf_buffer = rapor_generator.olustur(
    degerlen_sonuclari=analiz_data,
    metadata={'kitap_adi': 'Test-Riskli'}
)

# PDF'i kaydet
pdf_buffer.seek(0)
with open("test_fallback_risky_report.pdf", "wb") as f:
    f.write(pdf_buffer.read())

# PDF'in içinde "4.1" var mı kontrol et
pdf_buffer.seek(0)
pdf_text = pdf_buffer.read().decode('utf-8', errors='ignore')

has_4_1_detayli = "4.1 Detayli" in pdf_text
has_4_1_detaylı = "4.1 Detaylı" in pdf_text
has_bulgu_analizi = "Bulgu Analizi" in pdf_text
has_meb_ttk = "MEB TTK" in pdf_text
has_detayli_text = "Detayli" in pdf_text

print(f"\n   String arama sonuçları:")
print(f"     '4.1 Detayli': {has_4_1_detayli}")
print(f"     '4.1 Detaylı': {has_4_1_detaylı}")
print(f"     'Bulgu Analizi': {has_bulgu_analizi}")
print(f"     'MEB TTK': {has_meb_ttk}")
print(f"     'Detayli': {has_detayli_text}")

if has_4_1_detayli or has_4_1_detaylı:
    print(f"\n   ✅ 4.1 BÖLÜMÜ RAPORDA BULUNDU!")
else:
    print(f"\n   ❌ 4.1 BÖLÜMÜ RAPORDA BULUNAMADI")
    if has_meb_ttk:
        print(f"      NOT: MEB TTK bölümü var ama 4.1 altbölümü yok")

print(f"\n4. Rapor kaydedildi: test_fallback_risky_report.pdf")
print("=" * 60)
