#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test: Flask API /api/yukleme endpoint'ini doğrudan test et"""

import requests
import json

# Upload endpoint'ini test et
url = "http://127.0.0.1:5000/api/yukleme"
pdf_file = "uploads/10_sihirli_duduk.pdf"

try:
    with open(pdf_file, 'rb') as f:
        files = {'pdf': (pdf_file, f, 'application/pdf')}
        print(f"📤 POST {url}")
        print(f"📁 File: {pdf_file}")
        
        response = requests.post(url, files=files, timeout=30)
        
        print(f"\n✅ Status Code: {response.status_code}")
        print(f"Response:")
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {response.text}")
            
except Exception as e:
    print(f"❌ Exception: {e}")
