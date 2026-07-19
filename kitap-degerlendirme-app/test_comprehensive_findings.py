#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Complete Test: vur FALSE POSITIVE + Report Truncation Fix"""

import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os

# Content with MULTIPLE keywords (to test report truncation fix)
test_text = """
Çocuklar Bahçede

1. Çocuklar bahçede vurdular kazmaları toprağa.
2. Çocuklar bahçede koştular ve düştüler.
3. Bahçıvan onlara hikayeleri anlatıverdi.
4. Çocuklar bahçede oynadılar ve güldüler.
5. Çocuklar bahçede şarkı söylediler ve dansladılar.
6. Çocuklar bahçede yemek yediler ve içtiler.
7. Çocuklar bahçede uyudular.
8. Çocuklar bahçede uçurtma uçurttular.
9. Çocuklar bahçede kumpanya ve oyunları oynadılar.
10. Çocuklar bahçede ağaçlara tırmandılar.
11. Çocuklar bahçede çiçekler topladılar.
12. Çocuklar bahçede güvercin beslediler.

Epilog: Çok güzel bir gün geçirdiler.
"""

print("=" * 70)
print("TEST: Rapor Truncation Fix ve Vur FALSE POSITIVE")
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

# Create PDF with multiple occurrences
buffer = io.BytesIO()
c = canvas.Canvas(buffer, pagesize=letter)
c.setFont(font_name, 11)

y = 750
for line in test_text.split('\n'):
    if line.strip():
        try:
            parts = [line[i:i+85] for i in range(0, len(line), 85)]
            for part in parts:
                if y < 50:
                    c.showPage()
                    c.setFont(font_name, 11)
                    y = 750
                c.drawString(50, y, part)
                y -= 14
        except:
            pass

c.save()
buffer.seek(0)

test_pdf_path = "test_comprehensive.pdf"
with open(test_pdf_path, 'wb') as f:
    f.write(buffer.getvalue())

print(f"\n✅ Test PDF: {test_pdf_path}")

# Upload
upload_url = 'http://127.0.0.1:5000/api/yukleme'
with open(test_pdf_path, 'rb') as f:
    files = {'pdf': (test_pdf_path, f, 'application/pdf')}
    response = requests.post(upload_url, files=files, timeout=30)

dosya_yolu = response.json()['dosya_yolu']
print(f"✅ Uploaded: {dosya_yolu}")

# Analyze
analyze_url = 'http://127.0.0.1:5000/api/degerlendir'
payload = {
    "dosya_yolu": dosya_yolu,
    "profil": "hibrit",
    "yas_grubu": "10-15"
}

response = requests.post(analyze_url, json=payload, timeout=60)
analyze_data = response.json()

print(f"\n📊 Sonuçlar:")
print(f"   Risk Score: {analyze_data.get('risk_skoru', 'N/A')}/100")
print(f"   Decision: {analyze_data.get('karar', {}).get('seviye', 'N/A')}")

# Count findings
kategori_bulgulari = analyze_data.get('kategori_bulgulari', {})
total_findings = 0
for cat, details in kategori_bulgulari.items():
    if isinstance(details, dict) and 'bulgu_listesi' in details:
        count = len(details['bulgu_listesi'])
        if count > 0:
            print(f"   {cat}: {count} findings")
            total_findings += count

print(f"   TOPLAM: {total_findings} findings")

# Generate Report
report_url = 'http://127.0.0.1:5000/api/rapor'
report_payload = {
    "analiz_sonucu": analyze_data,
    "metadata": response.json().get('metadata', {})
}

report_response = requests.post(report_url, json=report_payload, timeout=60)
if report_response.status_code == 200:
    report_file = "test_comprehensive_report.pdf"
    with open(report_file, 'wb') as f:
        f.write(report_response.content)
    print(f"\n✅ Report: {report_file} ({len(report_response.content)} bytes)")
    print(f"   Kontrol: Tüm {total_findings} bulgular görüntülenmiş mi?")
    print(f"   (\"... ve X daha\" YOKSAYILMALI - tüm findings açık açık gösterilmeli)")
else:
    print(f"❌ Report failed: {report_response.status_code}")
