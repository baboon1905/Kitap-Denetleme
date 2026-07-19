#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug script: Check what data is being passed to MEBBulgularıRaporlayıcı
"""

import sys
sys.path.insert(0, '.')

import requests
import json

# Simulate the API flow
test_text = """
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

# Create test PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

pdf_buffer = io.BytesIO()
c = canvas.Canvas(pdf_buffer, pagesize=letter)
c.drawString(50, 750, "Test Riskli Metin")
for i, line in enumerate(test_text.split('\n')):
    c.drawString(50, 700 - (i * 20), line[:80])
c.save()
pdf_buffer.seek(0)

with open('debug_data_check.pdf', 'wb') as f:
    f.write(pdf_buffer.read())

print("=" * 60)
print("Data Check: What's being passed to MEBBulgularıRaporlayıcı")
print("=" * 60)

BASE_URL = "http://127.0.0.1:5000"

# Step 1: Upload
with open('debug_data_check.pdf', 'rb') as f:
    r1 = requests.post(f"{BASE_URL}/api/yukleme", files={'pdf': f})
dosya_yolu = r1.json()['dosya_yolu']

# Step 2: Analyze
r2 = requests.post(f"{BASE_URL}/api/degerlendir", json={
    'dosya_yolu': dosya_yolu,
    'profil': 'maarif_meb',
    'yas_grubu': 'ilk_ve_ort'
})

result = r2.json()
analiz_sonucu = result.get('analiz_sonucu', {})
meb_eval = analiz_sonucu.get('meb_degerlendirmesi', {})

print("\nMEB Degerlendirmesi data:")
print("=" * 60)
print(f"Type: {type(meb_eval)}")
print(f"Keys: {list(meb_eval.keys())}")
print()

print("meb_bulgulari:")
meb_bulgulari = meb_eval.get('meb_bulgulari', {})
print(f"  Type: {type(meb_bulgulari)}")
print(f"  Bool: {bool(meb_bulgulari)}")
print(f"  Content: {meb_bulgulari}")
print()

print("meb_kriterler:")
meb_kriterler = meb_eval.get('meb_kriterler', {})
print(f"  Type: {type(meb_kriterler)}")
print(f"  Keys: {list(meb_kriterler.keys())}")
print()

print("  Criteria with risk > 0:")
for k, v in meb_kriterler.items():
    risk = v.get('risk', 0)
    if risk > 0:
        print(f"    {k}: risk={risk}, karar={v.get('karar')}, ad={v.get('ad')}")

print()
print("Expected fallback result:")
print("-" * 60)

# Simulate fallback
fallback_bulgulari = {}
if not (meb_bulgulari and any(meb_bulgulari.values())):
    print("Fallback triggered!")
    for kriter_key, kriter_info in meb_kriterler.items():
        risk = kriter_info.get('risk', 0)
        if risk > 0:
            print(f"  Adding {kriter_key} with risk={risk}")
            fallback_bulgulari[kriter_key] = [{
                'bulgu': kriter_info.get('karar', 'Uyari'),
                'sebebi': 'Kriter Risk: %d/5' % risk,
                'alinti': '',
                'sayfa': 0
            }]
    
    print(f"\nFallback result: {bool(fallback_bulgulari and any(fallback_bulgulari.values()))}")
    print(f"Fallback content: {fallback_bulgulari}")
else:
    print("Fallback NOT triggered (meb_bulgulari has content)")
