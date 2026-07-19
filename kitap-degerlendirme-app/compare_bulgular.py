#!/usr/bin/env python3
import json
import requests

# Use existing test file
dosya_path = 'uploads/03_cokbilmis_alingan.pdf'
print(f"Using dosya: {dosya_path}")

# Analyze with maarif_meb (correct profile name)
print(f"Analyzing with 'maarif_meb' profile...")
r = requests.post('http://127.0.0.1:5000/api/degerlendir', 
                  json={'dosya_yolu': dosya_path, 'profil': 'maarif_meb'})
analiz = r.json()

print(f"\nStatus: {r.status_code}")
print(f"\nFull response (first 2000 chars):")
print(json.dumps(analiz, indent=2, ensure_ascii=False)[:2000])
for cat, data in analiz.get('kategoriler', {}).items():
    if data.get('bulundu'):
        print(f"\n{cat}: {data.get('toplam_bulgu')} findings")
        for i, bulgu in enumerate(data.get('bulgular', [])[:3], 1):
            print(f"  {i}. {bulgu.get('kelime')} (Risk: {bulgu.get('risk_skoru')})")

if not analiz.get('kategoriler'):
    print("Kategoriler: ", analiz.get('kategoriler'))
    print("\nRisk Skor: ", analiz.get('risk_skor'))
    print("Karar: ", analiz.get('karar'))

print("\n=== MEB KRITERLER ===")
kriterler = analiz.get('meb_degerlendirmesi', {}).get('meb_kriterler', {})
for k, v in kriterler.items():
    print(f"{k}: risk={v.get('risk')}, karar={v.get('karar')}")

print("\n=== MEB BULGULARI ===")
meb_bulgulari = analiz.get('meb_degerlendirmesi', {}).get('meb_bulgulari', {})
print(f"meb_bulgulari keys: {list(meb_bulgulari.keys())}")
print(f"meb_bulgulari empty: {len(meb_bulgulari) == 0}")

if meb_bulgulari:
    print("\nContent:")
    print(json.dumps(meb_bulgulari, indent=2, ensure_ascii=False)[:800])
