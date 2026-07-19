#!/usr/bin/env python3
import json
import requests

dosya_path = 'uploads/03_cokbilmis_alingan.pdf'

# Analyze
r = requests.post('http://127.0.0.1:5000/api/degerlendir', 
                  json={'dosya_yolu': dosya_path, 'profil': 'maarif_meb'})

if r.status_code != 200:
    print(f"Error: {r.status_code}")
    exit(1)

data = r.json()
analiz_sonucu = data.get('analiz_sonucu', {})

print("=== KATEGORI BULGULARI YAPISI ===")
for cat_key in list(analiz_sonucu.get('kategori_bulgulari', {}).keys())[:1]:
    cat = analiz_sonucu['kategori_bulgulari'][cat_key]
    print(f"\n{cat_key} keys: {list(cat.keys())}")
    if cat.get('bulundu'):
        print(f"  - bulunan_kelimeler: {type(cat.get('bulunan_kelimeler'))}")
        print(f"  - bulunan_bulgular: {type(cat.get('bulunan_bulgular'))}")
        
        # Check what keys exist for findings
        if 'bulunan_belgiler' in cat:
            print(f"\n  İlk bulgu: {list(cat['bulunan_belgiler'][0].keys())}")
        elif 'bulunan_bulgular' in cat:
            print(f"\n  İlk bulgu: {list(cat['bulunan_bulgular'][0].keys())}")

print("\n\n=== MEB KRITERLER RISKI ===")
meb = analiz_sonucu.get('meb_degerlendirmesi', {})
kriterler = meb.get('meb_kriterler', {})
for k, v in kriterler.items():
    print(f"{k}: risk={v.get('risk')}")
