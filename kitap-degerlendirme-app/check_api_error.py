#!/usr/bin/env python3
import requests
import json

dosya_path = 'uploads/03_cokbilmis_alingan.pdf'

# Analyze with MAARIF_MEB and show error
r = requests.post('http://127.0.0.1:5000/api/degerlendir', 
                  json={'dosya_yolu': dosya_path, 'profil': 'MAARIF_MEB'})

print(f"Status: {r.status_code}")
print(f"Response: {r.text[:1000]}")

try:
    print("\nJSON:", json.dumps(r.json(), indent=2, ensure_ascii=False)[:500])
except:
    pass
