#!/usr/bin/env python3
import json
import requests

dosya_path = 'uploads/03_cokbilmis_alingan.pdf'

# Analyze
r = requests.post('http://127.0.0.1:5000/api/degerlendir', 
                  json={'dosya_yolu': dosya_path, 'profil': 'maarif_meb'})

if r.status_code != 200:
    print(f"Error: {r.status_code}")
    print(r.text)
    exit(1)

data = r.json()
analiz_sonucu = data.get('analiz_sonucu', {})

print("=== MAARIF BULGULARI ===")
for cat, info in analiz_sonucu.get('kategori_bulgulari', {}).items():
    if info.get('bulundu'):
        print(f"\n{cat}:")
        for i, bulgu in enumerate(info.get('bulunan_kelimeler', [])[:2], 1):
            print(f"  {i}. {bulgu}")

print("\n=== MEB DEGERLENDIRMESI ===")
meb = analiz_sonucu.get('meb_degerlendirmesi', {})
meb_bulgulari = meb.get('meb_bulgulari', {})
print(f"meb_bulgulari keys: {list(meb_bulgulari.keys())}")
print(f"meb_bulgulari empty: {len(meb_bulgulari) == 0}")

if meb_bulgulari:
    print("\nContent (first 500 chars):")
    print(json.dumps(meb_bulgulari, indent=2, ensure_ascii=False)[:500])
else:
    print("\n❌ meb_bulgulari BOŞ - FALLBACK KULLANILACAK!")

print("\n=== MEB KRITERLER (Risk > 0) ===")
kriterler = meb.get('meb_kriterler', {})
for k, v in kriterler.items():
    if v.get('risk', 0) > 0:
        print(f"  {k}: risk={v['risk']}, karar={v.get('karar')}")
