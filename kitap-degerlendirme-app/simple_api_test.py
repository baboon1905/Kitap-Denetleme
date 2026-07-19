#!/usr/bin/env python3
# Simple API endpoint test

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# Prepare data
test_data = {
    "analiz_sonucu": {
        "meb_degerlendirmesi": {
            "meb_kriterler": {
                "dil": {"risk": 1, "karar": "Uyarı"},
                "milli_guvenlik": {"risk": 1, "karar": "Uyarı"},
                "milli_manevi": {"risk": 3, "karar": "Orta"},
                "reklam": {"risk": 1, "karar": "Uyarı"},
            },
            "meb_bulgulari": {},
            "meb_puani": 50,
            "genel_karar": "Revizyon Gerekli"
        }
    },
    "kitap_adi": "Test Kitap"
}

print("Sending /api/rapor request...")
try:
    response = requests.post(f"{BASE_URL}/api/rapor", json=test_data, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response size: {len(response.content)} bytes")
    
    if response.status_code == 200:
        with open('simple_test_output.pdf', 'wb') as f:
            f.write(response.content)
        print(f"✅ PDF saved to simple_test_output.pdf")
        
        # Check for 4.1
        from pdfplumber import PDF
        try:
            import pdfplumber
            with pdfplumber.open('simple_test_output.pdf') as pdf:
                text = "\n".join([page.extract_text() for page in pdf.pages])
                if "4.1" in text:
                    print("✅ 4.1 found in PDF!")
                else:
                    print("❌ 4.1 NOT found in PDF")
        except:
            print("(pdfplumber check skipped)")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")
