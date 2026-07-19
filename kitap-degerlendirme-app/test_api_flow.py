#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
import json

# Test riskli metin dosyası oluştur
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

# Test PDF dosyası oluştur
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

pdf_buffer = io.BytesIO()
c = canvas.Canvas(pdf_buffer, pagesize=letter)
c.drawString(50, 750, "Test Riskli Metin")
for i, line in enumerate(test_text.split('\n')):
    c.drawString(50, 700 - (i * 20), line[:80])  # Truncate long lines
c.save()
pdf_buffer.seek(0)

# Dosyayı kaydet
with open('test_api_flow.pdf', 'wb') as f:
    f.write(pdf_buffer.read())

print("=" * 60)
print("API Flow Test - 4.1 Bölümü Kontrolü")
print("=" * 60)

BASE_URL = "http://127.0.0.1:5000"

# Step 1: Upload file
print("\n1. Dosya yükleniyor...")
with open('test_api_flow.pdf', 'rb') as f:
    files = {'pdf': f}
    response = requests.post(f"{BASE_URL}/api/yukleme", files=files)
    
if response.status_code != 200:
    print(f"❌ Upload hatası: {response.text}")
    sys.exit(1)

dosya_yolu = response.json().get('dosya_yolu')
print(f"✅ Dosya yüklendi: {dosya_yolu}")

# Step 2: Analyze
print("\n2. Analiz yapılıyor...")
analiz_response = requests.post(
    f"{BASE_URL}/api/degerlendir",
    json={
        "dosya_yolu": dosya_yolu,
        "profil": "hibrit",
        "yas_grubu": "6-12"
    }
)

if analiz_response.status_code != 200:
    print(f"❌ Analiz hatası: {analiz_response.text}")
    sys.exit(1)

analiz_data = analiz_response.json().get('analiz_sonucu', {})
print(f"✅ Analiz tamamlandı")

# Check MEB data
meb_eval = analiz_data.get('meb_degerlendirmesi', {})
meb_bulgulari = meb_eval.get('meb_bulgulari', {})
meb_kriterler = meb_eval.get('meb_kriterler', {})

print(f"\n   MEB Değerlendirmesi:")
print(f"     meb_bulgulari type: {type(meb_bulgulari)}")
print(f"     meb_bulgulari content: {bool(meb_bulgulari)}")
print(f"     meb_bulgulari items: {len(meb_bulgulari) if meb_bulgulari else 0}")

if meb_kriterler:
    print(f"\n     Kriterler:")
    for key, info in list(meb_kriterler.items())[:3]:
        print(f"       {key}: risk={info.get('risk', 0)}/5")

# Step 3: Generate PDF Report
print("\n3. PDF Raporu oluşturuluyor...")
rapor_response = requests.post(
    f"{BASE_URL}/api/rapor",
    json={
        "analiz_sonucu": analiz_data,
        "kitap_adi": "Test-API-Flow"
    }
)

if rapor_response.status_code != 200:
    print(f"❌ Rapor hatası: {rapor_response.text}")
    sys.exit(1)

print(f"✅ PDF oluşturuldu, boyutu: {len(rapor_response.content)} bytes")

# Save PDF
with open('test_api_flow_report.pdf', 'wb') as f:
    f.write(rapor_response.content)

# Step 4: Check if 4.1 exists in PDF
print("\n4. PDF'de 4.1 bölümü kontrol ediliyor...")
try:
    import pdfplumber
    with pdfplumber.open('test_api_flow_report.pdf') as pdf:
        found_4_1 = False
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text and "4.1" in text:
                found_4_1 = True
                print(f"✅ 4.1 BULUNDU (Page {page_num})")
                # Show context
                idx = text.find("4.1")
                print(f"   Context: {text[max(0, idx-30):idx+80]}")
                break
        
        if not found_4_1:
            print(f"❌ 4.1 BULUNAMADI")
            print(f"   PDF {len(pdf.pages)} sayfa içeriyor")
            
except ImportError:
    print("⚠️  pdfplumber kurulu değil, manuel kontrol yapılamadı")

print("\n" + "=" * 60)
print("Test tamamlandı")
print("=" * 60)
