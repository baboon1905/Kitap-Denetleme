#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test: Pass actual API data to RaporOlusturucu directly
"""

from report_generator import RaporOlusturucu
import pdfplumber
import requests
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Create test PDF
test_text = """
Cumhuriyet devleti, bunun için, işçi sınıfın iktidar olması gerekir çünkü kapitalizm 
patlayacaktır. Türkiye'de sosyalist sistem kurulmalıdır.
"""

pdf_buffer = io.BytesIO()
c = canvas.Canvas(pdf_buffer, pagesize=letter)
c.drawString(50, 750, "Test")
c.save()
pdf_buffer.seek(0)

with open('debug_test_api_data.pdf', 'wb') as f:
    f.write(pdf_buffer.read())

BASE_URL = "http://127.0.0.1:5000"

# Get actual API data
print("Getting actual API data...")
with open('debug_test_api_data.pdf', 'rb') as f:
    files = {'pdf': f}
    r1 = requests.post(f"{BASE_URL}/api/yukleme", files=files)

dosya_yolu = r1.json()['dosya_yolu']

r2 = requests.post(f"{BASE_URL}/api/degerlendir", json={
    'dosya_yolu': dosya_yolu,
    'profil': 'maarif_meb',
    'yas_grubu': 'ilk_ve_ort'
})

result = r2.json()
analiz_sonucu = result.get('analiz_sonucu', {})

print("\nNow testing RaporOlusturucu directly with this data...")
rapor_gen = RaporOlusturucu()
pdf_buffer = rapor_gen.olustur(
    degerlen_sonuclari=analiz_sonucu,
    metadata={"kitap_adi": "Test"}
)

# Save
with open('test_api_data_direct.pdf', 'wb') as f:
    f.write(pdf_buffer.getvalue())

# Check for 4.1
pdf_buffer.seek(0)
with pdfplumber.open(pdf_buffer) as pdf:
    full_text = ""
    for page in pdf.pages:
        full_text += (page.extract_text() or "") + "\n"
    
    if "4.1" in full_text:
        print("✅ 4.1 BULUNDU!")
    else:
        print("❌ 4.1 BULUNAMADI")

print("Saved to test_api_data_direct.pdf")
