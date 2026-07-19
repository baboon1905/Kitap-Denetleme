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

print("=== MEB DEGERLENDIRMESI - FULL ===")
meb = analiz_sonucu.get('meb_degerlendirmesi', {})

print("\n1. MEB KRITERLER:")
for k, v in meb.get('meb_kriterler', {}).items():
    if v.get('risk', 0) > 0:
        print(f"   {k}: risk={v['risk']} ({v.get('bulgular_sayisi', 0)} findings)")

print("\n2. MEB BULGULARI:")
bulgulari = meb.get('meb_bulgulari', {})
print(f"   Keys: {list(bulgulari.keys())}")

for criterion, findings in bulgulari.items():
    if findings:
        print(f"\n   {criterion}: {len(findings)} findings")
        for i, bulgu in enumerate(findings[:2], 1):
            print(f"      {i}. sebebi={bulgu.get('sebebi', '?')[:50]}")
            print(f"         alininti={bulgu.get('alininti', '')[:50] if bulgu.get('alininti') else 'EMPTY'}")
