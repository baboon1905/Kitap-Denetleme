#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug script: Test API and check PDF content
"""

import requests
import json
import pdfplumber
import io

# Test riskli metin
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

# Test PDF oluştur
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

pdf_buffer = io.BytesIO()
c = canvas.Canvas(pdf_buffer, pagesize=letter)
c.drawString(50, 750, "Test Riskli Metin")
for i, line in enumerate(test_text.split('\n')):
    c.drawString(50, 700 - (i * 20), line[:80])
c.save()
pdf_buffer.seek(0)

with open('debug_api_flow.pdf', 'wb') as f:
    f.write(pdf_buffer.read())

print("=" * 60)
print("API + PDF Test - 4.1 Bölümü Kontrolü")
print("=" * 60)

BASE_URL = "http://127.0.0.1:5000"

# Step 1: Upload
print("\n1. Upload...")
with open('debug_api_flow.pdf', 'rb') as f:
    files = {'pdf': f}
    r1 = requests.post(f"{BASE_URL}/api/yukleme", files=files)
print(f"   Status: {r1.status_code}")

if r1.status_code != 200:
    print("   ❌ Upload failed")
    exit(1)

dosya_yolu = r1.json()['dosya_yolu']
print(f"   ✅ Dosya: {dosya_yolu}")

# Step 2: Analyze
print("\n2. Analyze...")
r2 = requests.post(f"{BASE_URL}/api/degerlendir", json={
    'dosya_yolu': dosya_yolu,
    'profil': 'maarif_meb',
    'yas_grubu': 'ilk_ve_ort'
})
print(f"   Status: {r2.status_code}")

if r2.status_code != 200:
    print("   ❌ Analysis failed")
    print(f"   Response: {r2.text}")
    exit(1)

result = r2.json()
analiz_sonucu = result.get('analiz_sonucu', {})  # Get the inner result
meb_eval = analiz_sonucu.get('meb_degerlendirmesi', {})
print(f"   MEB Bulgulari: {bool(meb_eval.get('meb_bulgulari'))}")

kriterler = meb_eval.get('meb_kriterler', {})
for kriter, info in kriterler.items():
    if info.get('risk', 0) > 0:
        print(f"   {kriter}: risk={info.get('risk')}/5")

# Step 3: Generate Report
print("\n3. Generate Report...")
r3 = requests.post(f"{BASE_URL}/api/rapor", json={
    'analiz_sonucu': analiz_sonucu,  # Send the inner result, not the full API response!
    'kitap_adi': 'Test Kitap'
}, timeout=30)
print(f"   Status: {r3.status_code}")

if r3.status_code != 200:
    print("   ❌ Report generation failed")
    print(f"   Response: {r3.text[:200]}")
    exit(1)

# Save PDF
pdf_bytes = r3.content
with open('debug_output.pdf', 'wb') as f:
    f.write(pdf_bytes)
print(f"   ✅ PDF saved: {len(pdf_bytes)} bytes")

# Step 4: Extract text
print("\n4. Extracting PDF content...")
try:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        print(f"   Pages: {len(pdf.pages)}")
        
        full_text = ""
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            full_text += f"\n--- Page {i+1} ---\n{text}"
        
        # Search for 4.1
        if "4.1" in full_text and "Detayli" in full_text:
            print("   ✅ 4.1 BULUNDU!")
            # Find and show context
            lines = full_text.split('\n')
            for i, line in enumerate(lines):
                if '4.1' in line and 'Detayli' in line:
                    print(f"\n   Context (lines {i-1} to {i+3}):")
                    for j in range(max(0, i-1), min(len(lines), i+4)):
                        print(f"     {lines[j]}")
                    break
        else:
            print("   ❌ 4.1 BULUNAMADI")
            if "MEB TTK" in full_text:
                print("   (But MEB TTK section found)")
            print(f"\n   Full text length: {len(full_text)} chars")
            print(f"   First 500 chars:\n{full_text[:500]}")

except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
