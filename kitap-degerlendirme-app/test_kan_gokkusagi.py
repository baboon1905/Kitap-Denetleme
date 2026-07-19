#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test: çıkan, Serkan, gökkuşağı kelimelerini test et"""

import requests
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os

# Test PDF oluştur (çıkan, Serkan, gökkuşağı içeriyor)
print("=" * 70)
print("1️⃣ TEST PDF OLUŞTUR")
print("=" * 70)

test_text = """
Çocukluk Hikayesi

Serkan adında bir çocuk vardı. Okul çıkışında her gün oyun oynamaya giderdi.
Çıkan arkadaşlarıyla futbol oynarken çok eğlenirdi. 

Bir gün gökkuşağı görüldü. Gökkuşağı sembolü çok güzeldi. Çocuklar çıkan sesleri dinlediler.
Serkan'ın ailesi onu sevirdi. Her gün çıkan güneşi seyrederlerdi.

Hikaye burada bitiyor.
"""

# DejaVuSans font kullan (Turkish characters support)
try:
    font_path = "C:\\Windows\\Fonts\\DejaVuSans.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('DejaVu', font_path))
        font_name = 'DejaVu'
    else:
        font_name = 'Helvetica'
except:
    font_name = 'Helvetica'

# PDF'ye yaz
buffer = io.BytesIO()
c = canvas.Canvas(buffer, pagesize=letter)
c.setFont(font_name, 12)

y = 750
for line in test_text.split('\n'):
    if line.strip():
        try:
            c.drawString(50, y, line)
        except:
            # Fallback - ASCII only
            c.drawString(50, y, line.encode('ascii', 'ignore').decode('ascii'))
        y -= 15

c.save()
buffer.seek(0)

# Test PDF dosyasına kaydet
test_pdf_path = "test_keywords.pdf"
with open(test_pdf_path, 'wb') as f:
    f.write(buffer.getvalue())

print(f"✅ Test PDF oluşturuldu: {test_pdf_path}")
print(f"   İçerik: 'çıkan', 'Serkan', 'gökkuşağı' kelimeleri içeriyor")

# Upload
print("\n" + "=" * 70)
print("2️⃣ UPLOAD")
print("=" * 70)

upload_url = 'http://127.0.0.1:5000/api/yukleme'
with open(test_pdf_path, 'rb') as f:
    files = {'pdf': (test_pdf_path, f, 'application/pdf')}
    upload_response = requests.post(upload_url, files=files, timeout=30)

if upload_response.status_code != 200:
    print(f"❌ Upload failed: {upload_response.json()}")
    exit(1)

upload_data = upload_response.json()
dosya_yolu = upload_data['dosya_yolu']
print(f"✅ Uploaded: {dosya_yolu}")

# Analyze
print("\n" + "=" * 70)
print("3️⃣ ANALYZE (Hibrit/Balanced)")
print("=" * 70)

analyze_url = 'http://127.0.0.1:5000/api/degerlendir'
analyze_payload = {
    "dosya_yolu": dosya_yolu,
    "profil": "hibrit",
    "yas_grubu": "10-15"
}

analyze_response = requests.post(analyze_url, json=analyze_payload, timeout=60)
if analyze_response.status_code != 200:
    print(f"❌ Analysis failed: {analyze_response.status_code}")
    print(f"   {analyze_response.text[:300]}")
    exit(1)

analyze_data = analyze_response.json()

# Sonuçlar
print(f"\n✅ Analiz Sonuçları:")
print(f"   Risk Skoru: {analyze_data.get('risk_skoru', 'N/A')}/100")
print(f"   Karar: {analyze_data.get('karar', {}).get('seviye', 'N/A')}")

# Kategori bulgularında ne var?
print(f"\n📊 Kategori Bulgularında:")
kategori_bulgulari = analyze_data.get('kategori_bulgulari', {})

# "çıkan", "Serkan" bulunan mı? (FALSE POSITIVE - filter etmeli)
print(f"\n❌ FALSE POSITIVE CHECK (filtered olması lazım):")
found_false_positives = False
for cat, details in kategori_bulgulari.items():
    if isinstance(details, dict) and 'bulgu_listesi' in details:
        for finding in details['bulgu_listesi']:
            if finding.lower() in ['çıkan', 'serkan', 'kan']:
                print(f"   ❌ {cat}: '{finding}' - FILTERED OLMALI!")
                found_false_positives = True

if not found_false_positives:
    print(f"   ✅ Tüm FALSE POSITIVE'ler filtered!")

# "gökkuşağı" riskli mi? (true positive - bulunması lazım)
print(f"\n✅ TRUE POSITIVE CHECK (bulunması lazım):")
found_gokkusagi = False
for cat, details in kategori_bulgulari.items():
    if isinstance(details, dict) and 'bulgu_listesi' in details:
        for finding in details['bulgu_listesi']:
            if 'gökkuşağı' in finding.lower():
                print(f"   ✅ {cat}: '{finding}' - BULUNDU!")
                found_gokkusagi = True

if not found_gokkusagi:
    print(f"   ⚠️  'gökkuşağı' bulunamadı (ama olması lazım)")

print("\n" + "=" * 70)
print("🎯 TEST ÖZET")
print("=" * 70)
print(f"- 'çıkan', 'Serkan' filtered: {'✅' if not found_false_positives else '❌'}")
print(f"- 'gökkuşağı' found: {'✅' if found_gokkusagi else '❌'}")
