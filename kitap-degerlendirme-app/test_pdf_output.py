#!/usr/bin/env python3
import requests
import pdfplumber

dosya_path = 'uploads/03_cokbilmis_alingan.pdf'

# Generate PDF
print("PDF Generating...")
data = {'analiz_sonucu': {}, 'kitap_adi': 'Test Kitap'}

# First analyze
print("1. Analyzing...")
r = requests.post('http://127.0.0.1:5000/api/degerlendir',
                  json={'dosya_yolu': dosya_path, 'profil': 'maarif_meb'})
analiz = r.json()['analiz_sonucu']

# Generate report
print("2. Generating PDF...")
r = requests.post('http://127.0.0.1:5000/api/rapor',
                  json={'analiz_sonucu': analiz, 'kitap_adi': 'Test Kitap'})

if r.status_code != 200:
    print(f"Error: {r.status_code}")
    exit(1)

# Save PDF
with open('test_output.pdf', 'wb') as f:
    f.write(r.content)

print("✅ PDF Saved: test_output.pdf")

# Check 4.1 content
print("\n3. Checking 4.1 Detayli Bulgu Analizi...")
with pdfplumber.open('test_output.pdf') as pdf:
    print(f"Pages: {len(pdf.pages)}")
    
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if '4.1' in text or 'guvenlik' in text.lower() or 'kan:' in text.lower():
            print(f"\n✅ Found on page {i+1}:")
            # Get context around 4.1
            lines = text.split('\n')
            for j, line in enumerate(lines):
                if '4.1' in line or 'kan:' in line.lower():
                    start = max(0, j-2)
                    end = min(len(lines), j+5)
                    print('\n'.join(lines[start:end]))
                    print("---")
