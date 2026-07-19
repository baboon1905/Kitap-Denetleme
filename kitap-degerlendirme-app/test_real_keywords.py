#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test: Real risk keywords + Context (to verify truncation fix works)"""

import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os

# Real risk keywords but with NEUTRAL context
test_text = """
Çocuklar ve Oyunları

Bugün çocuklar bahçede birçok şey yaptılar:

1. Vurdular kazmaları toprağa.
2. Yumrukladılar topları.
3. Bıçak, çatal kullandılar yemek yerken.
4. Çokça alaşı yediler.
5. Bayram eğlenceleri oynadılar.
6. Korku filmi seyrettiler (ama çok korkutucu değildi).
7. Silah oyuncağıyla oynadılar.
8. Üniformalar giyerek asker oyunu oynadılar.
9. Cigaraların resimleri gördüler (reklamda).
10. Hayvanat bahçesinde hayvanlara baktılar.
11. Kitapta tarihî savaşlar hakkında okudu.
12. Şiddet sahneleri olmayan bir film seyrettiler.

Çok eğlenmiş ve mutlu olmuşlardı.
"""

print("=" * 70)
print("TEST: Report Truncation Fix + Real Keywords")
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
c.setFont(font_name, 10)

y = 750
for line in test_text.split('\n'):
    if line.strip():
        if y < 50:
            c.showPage()
            c.setFont(font_name, 10)
            y = 750
        try:
            if len(line) > 90:
                # Split long lines
                for i in range(0, len(line), 90):
                    c.drawString(50, y, line[i:i+90])
                    y -= 12
            else:
                c.drawString(50, y, line)
                y -= 12
        except:
            pass

c.save()
buffer.seek(0)

test_pdf_path = "test_real_keywords.pdf"
with open(test_pdf_path, 'wb') as f:
    f.write(buffer.getvalue())

print(f"\n✅ Test PDF created with 12 keywords (neutral context)")

# Upload
print("\n" + "=" * 70)
upload_url = 'http://127.0.0.1:5000/api/yukleme'
with open(test_pdf_path, 'rb') as f:
    files = {'pdf': (test_pdf_path, f, 'application/pdf')}
    response = requests.post(upload_url, files=files, timeout=30)

dosya_yolu = response.json()['dosya_yolu']
print(f"✅ Uploaded")

# Analyze
analyze_url = 'http://127.0.0.1:5000/api/degerlendir'
payload = {
    "dosya_yolu": dosya_yolu,
    "profil": "maarif",  # Stricter profile
    "yas_grubu": "10-15"
}

response = requests.post(analyze_url, json=payload, timeout=60)
analyze_data = response.json()

print(f"\n📊 Analysis Results:")
print(f"   Risk Score: {analyze_data.get('risk_skoru', 'N/A')}/100")

# Count findings
kategori_bulgulari = analyze_data.get('kategori_bulgulari', {})
total_findings = 0
findings_by_category = {}

for cat, details in kategori_bulgulari.items():
    if isinstance(details, dict) and 'bulgu_listesi' in details:
        count = len(details['bulgu_listesi'])
        if count > 0:
            findings_by_category[cat] = count
            total_findings += count
            print(f"   - {cat}: {count} findings")

print(f"\n   TOTAL: {total_findings} findings")

if total_findings > 0:
    print(f"\n✅ Keywords detected (Good for testing truncation fix)")
    
    # Generate Report
    print(f"\nGenerating Report...")
    report_url = 'http://127.0.0.1:5000/api/rapor'
    report_payload = {
        "analiz_sonucu": analyze_data,
        "metadata": response.json().get('metadata', {})
    }
    
    report_response = requests.post(report_url, json=report_payload, timeout=60)
    if report_response.status_code == 200:
        report_file = "test_real_keywords_report.pdf"
        with open(report_file, 'wb') as f:
            f.write(report_response.content)
        print(f"✅ Report: {report_file}")
        print(f"\n🎯 VERIFY IN PDF:")
        for cat, count in findings_by_category.items():
            print(f"   ✓ {cat}: All {count} findings should be visible")
            print(f"     (NO \"... ve X daha\" truncation)")
    else:
        print(f"❌ Report failed: {report_response.status_code}")
else:
    print(f"⚠️  No keywords found in DEMO mode")
    print(f"   (Analyze endpoint running in DEMO - not using Groq API)")
