#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug: What's actually being passed to /api/rapor?
"""

import requests
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Test PDF
test_text = """
Cumhuriyet devleti, bunun için, işçi sınıfın iktidar olması gerekir çünkü kapitalizm 
patlayacaktır. Türkiye'de sosyalist sistem kurulmalıdır.
"""

pdf_buffer = io.BytesIO()
c = canvas.Canvas(pdf_buffer, pagesize=letter)
c.drawString(50, 750, "Test Riskli Metin")
for i, line in enumerate(test_text.split('\n')):
    c.drawString(50, 700 - (i * 20), line[:80])
c.save()
pdf_buffer.seek(0)

with open('debug_check_data.pdf', 'wb') as f:
    f.write(pdf_buffer.read())

BASE_URL = "http://127.0.0.1:5000"

print("="*60)
print("Debugging API Data")
print("="*60)

# Step 1: Upload
print("\n1. Upload...")
with open('debug_check_data.pdf', 'rb') as f:
    files = {'pdf': f}
    r1 = requests.post(f"{BASE_URL}/api/yukleme", files=files)

dosya_yolu = r1.json()['dosya_yolu']
print(f"   Dosya: {dosya_yolu}")

# Step 2: Analyze
print("\n2. Analyze...")
r2 = requests.post(f"{BASE_URL}/api/degerlendir", json={
    'dosya_yolu': dosya_yolu,
    'profil': 'maarif_meb',
    'yas_grubu': 'ilk_ve_ort'
})

result = r2.json()
analiz_sonucu = result.get('analiz_sonucu', {})

print("\n3. Data structure being sent to /api/rapor:")
meb_eval = analiz_sonucu.get('meb_degerlendirmesi', {})

print(f"\n   meb_bulgulari: {meb_eval.get('meb_bulgulari')}")
print(f"   meb_kriterler keys: {list(meb_eval.get('meb_kriterler', {}).keys())}")

kriterler = meb_eval.get('meb_kriterler', {})
print(f"\n   Criteria with risk > 0:")
for kriter, info in kriterler.items():
    risk = info.get('risk', 0)
    if risk > 0:
        print(f"      {kriter}: risk={risk}")

# Check: Is there any fallback-triggering condition?
has_bulgulari = bool(meb_eval.get('meb_bulgulari'))
has_risky_criteria = any(info.get('risk', 0) > 0 for info in kriterler.values())

print(f"\n   Conditions:")
print(f"      Has bulgulari: {has_bulgulari}")
print(f"      Has risky criteria: {has_risky_criteria}")
print(f"      Should trigger fallback: {not has_bulgulari and has_risky_criteria}")

print("\n" + "="*60)
