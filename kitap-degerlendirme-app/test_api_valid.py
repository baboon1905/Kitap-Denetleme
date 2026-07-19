#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test: API upload with valid PDF"""

import requests
import json

url = 'http://127.0.0.1:5000/api/yukleme'
pdf_file = 'uploads/alisin_ofkesi_5.basim.pdf'

try:
    with open(pdf_file, 'rb') as f:
        files = {'pdf': (pdf_file, f, 'application/pdf')}
        print(f"📤 Uploading: {pdf_file}")
        response = requests.post(url, files=files, timeout=30)
        print(f"Status: {response.status_code}")
        
        data = response.json()
        if 'hata' in data:
            print(f"❌ Error: {data['hata']}")
        else:
            print(f"✅ Success!")
            print(f"File: {data['dosya_yolu']}")
            stats = data.get('istatistikler', {})
            print(f"Words: {stats}")
except Exception as e:
    print(f"❌ Exception: {e}")
