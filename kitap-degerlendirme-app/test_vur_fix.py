#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test: "vurdular" ve diğer verb conjugations - FALSE POSITIVE filter"""

import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os

# Test content with "vurdular"
test_text = """
Çocuklar ve Kazı

Bahar geldi ve çocuklar bahçede oynaşırlarken, bahçıvan onları çağırdı. 
"Çocuklar, gelip bana yardım edebilir misiniz?" dedi.

Çocuklar sevinçle koşarak bahçıvan'ın yanına gittiler. Bahçıvan onlara,
"Bu alan'a ağaç dikmek istiyorum. Toprağı kazmamız lazım," dedi.

Çocuklar şarkılar söyleyerek vurdular kazmaları toprağa. Bir saat sonra,
tüm çalışma bitmiş ve bahçıvan çok mutlu olmuştu. 

Çocuklar bahçede oynayan hayvanları da gördüler. Tavuklar ve arılar bahçede vardı.
Güzel bir gün geçirdiler.

Hikaye burada bitiyor.
"""

print("=" * 70)
print("1️⃣ TEST PDF OLUŞTUR")
print("=" * 70)

# Font setup
try:
    font_path = "C:\\Windows\\Fonts\\DejaVuSans.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('DejaVu', font_path))
        font_name = 'DejaVu'
    else:
        font_name = 'Helvetica'
except:
    font_name = 'Helvetica'

# Create PDF
buffer = io.BytesIO()
c = canvas.Canvas(buffer, pagesize=letter)
c.setFont(font_name, 11)

y = 750
for line in test_text.split('\n'):
    if line.strip():
        try:
            c.drawString(50, y, line[:100])  # Limit line length
        except:
            pass
        y -= 14

c.save()
buffer.seek(0)

test_pdf_path = "test_vurdular.pdf"
with open(test_pdf_path, 'wb') as f:
    f.write(buffer.getvalue())

print(f"✅ Test PDF oluşturuldu: {test_pdf_path}")
print(f"   İçerik: 'vurdular' kelimesi içeriyor (FALSE POSITIVE olması lazım)")

# Upload
print("\n" + "=" * 70)
print("2️⃣ UPLOAD")
print("=" * 70)

upload_url = 'http://127.0.0.1:5000/api/yukleme'
with open(test_pdf_path, 'rb') as f:
    files = {'pdf': (test_pdf_path, f, 'application/pdf')}
    response = requests.post(upload_url, files=files, timeout=30)

if response.status_code != 200:
    print(f"❌ Upload failed: {response.json()}")
    exit(1)

dosya_yolu = response.json()['dosya_yolu']
print(f"✅ Uploaded: {dosya_yolu}")

# Analyze
print("\n" + "=" * 70)
print("3️⃣ ANALYZE (Hibrit/Balanced)")
print("=" * 70)

analyze_url = 'http://127.0.0.1:5000/api/degerlendir'
payload = {
    "dosya_yolu": dosya_yolu,
    "profil": "hibrit",
    "yas_grubu": "10-15"
}

response = requests.post(analyze_url, json=payload, timeout=60)
if response.status_code != 200:
    print(f"❌ Analysis failed: {response.status_code}")
    exit(1)

analyze_data = response.json()

print(f"✅ Analysis complete")
print(f"   Risk Score: {analyze_data.get('risk_skoru', 'N/A')}/100")
print(f"   Decision: {analyze_data.get('karar', {}).get('seviye', 'N/A')}")

# Check for "vur" findings
print(f"\n📊 Kategori Bulgularında:")
kategori_bulgulari = analyze_data.get('kategori_bulgulari', {})

vur_found = False
for cat, details in kategori_bulgulari.items():
    if isinstance(details, dict) and 'bulgu_listesi' in details:
        for finding in details['bulgu_listesi']:
            if 'vur' in finding.lower():
                print(f"   ❌ {cat}: '{finding}' - FILTERED OLMALI!")
                vur_found = True

if not vur_found:
    print(f"   ✅ 'vur' FALSE POSITIVE'i filtered!")

print("\n" + "=" * 70)
print("4️⃣ GENERATE REPORT (kontrol et: TÜM bulgular gösterilmeli)")
print("=" * 70)

report_url = 'http://127.0.0.1:5000/api/rapor'
report_payload = {
    "analiz_sonucu": analyze_data,
    "metadata": response.json().get('metadata', {})
}

report_response = requests.post(report_url, json=report_payload, timeout=60)
if report_response.status_code == 200:
    report_file = "test_vur_report.pdf"
    with open(report_file, 'wb') as f:
        f.write(report_response.content)
    print(f"✅ Report saved: {report_file} ({len(report_response.content)} bytes)")
    print(f"   Kontrol et: Rapor'da \"... ve X daha\" olmamalı - TÜM bulgular gösterilmeli")
else:
    print(f"❌ Report generation failed: {report_response.status_code}")
