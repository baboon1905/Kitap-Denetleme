#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Complete end-to-end test: Upload → Analyze → Generate Report"""

import requests
import json
from pdf_processor import PDFProcessor

# Upload
print("=" * 70)
print("1️⃣ UPLOAD")
print("=" * 70)
pdf_file = 'uploads/alisin_ofkesi_5.basim.pdf'

upload_url = 'http://127.0.0.1:5000/api/yukleme'
with open(pdf_file, 'rb') as f:
    files = {'pdf': (pdf_file, f, 'application/pdf')}
    upload_response = requests.post(upload_url, files=files, timeout=30)

if upload_response.status_code != 200:
    print(f"❌ Upload failed: {upload_response.json()}")
    exit(1)

upload_data = upload_response.json()
dosya_yolu = upload_data['dosya_yolu']
print(f"✅ Uploaded: {dosya_yolu}")
print(f"   Chars: {upload_data['istatistikler']['karakter_sayisi']}")

# Analyze
print("\n" + "=" * 70)
print("2️⃣ ANALYZE (Hibrit/Balanced Profile)")
print("=" * 70)

analyze_url = 'http://127.0.0.1:5000/api/degerlendir'
analyze_payload = {
    "dosya_yolu": dosya_yolu,
    "profil": "hibrit",
    "yas_grubu": "10-15"
}

analyze_response = requests.post(analyze_url, json=analyze_payload, timeout=60)
if analyze_response.status_code != 200:
    print(f"❌ Analysis failed: {analyze_response.json()}")
    exit(1)

analyze_data = analyze_response.json()
print(f"✅ Analysis complete")
print(f"   Risk Score: {analyze_data.get('risk_skoru', 'N/A')}/100")
print(f"   Decision: {analyze_data.get('karar', {}).get('seviye', 'N/A')}")

# Check kategori_bulgulari
print(f"\n   Kategori Bulgularında:")
kategori_bulgulari = analyze_data.get('kategori_bulgulari', {})
total_findings = 0
for cat, details in kategori_bulgulari.items():
    count = details.get('bulgu_sayisi', 0) if isinstance(details, dict) else 0
    if count > 0:
        print(f"     - {cat}: {count} findings")
        total_findings += count

print(f"   TOPLAM BULGULAR: {total_findings}")

# Generate Report
print("\n" + "=" * 70)
print("3️⃣ GENERATE REPORT (PDF)")
print("=" * 70)

report_url = 'http://127.0.0.1:5000/api/rapor'
report_payload = {
    "analiz_sonucu": analyze_data,
    "metadata": upload_data.get('metadata', {})
}

report_response = requests.post(report_url, json=report_payload, timeout=60)
if report_response.status_code != 200:
    print(f"❌ Report generation failed: {report_response.status_code}")
    print(f"   {report_response.text[:200]}")
else:
    report_file = "test_report_final.pdf"
    with open(report_file, 'wb') as f:
        f.write(report_response.content)
    print(f"✅ Report saved: {report_file} ({len(report_response.content)} bytes)")

print("\n" + "=" * 70)
print(f"🎉 SUCCESS! Risk Score: {analyze_data.get('risk_skoru')}/100, Findings: {total_findings}")
print("=" * 70)
