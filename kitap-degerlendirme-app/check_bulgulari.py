#!/usr/bin/env python3
import json
import requests

# Upload
print("Uploading...")
with open('test_kitap.pdf', 'rb') as f:
    r = requests.post('http://127.0.0.1:5000/api/yukleme', files={'file': f})
    print(f"Upload response: {r.json()}")
    dosya = r.json().get('dosya_yolu') or r.json().get('file_path')

print(f"Using dosya: {dosya}")

# Analyze
print("Analyzing...")
r = requests.post('http://127.0.0.1:5000/api/degerlendir', json={'dosya_yolu': dosya, 'profil': 'MAARIF_MEB'})
analiz = r.json()

# Show meb_bulgulari content
meb_bulgulari = analiz.get('meb_degerlendirmesi', {}).get('meb_bulgulari', {})
print(f'\n✅ meb_bulgulari keys: {list(meb_bulgulari.keys())}')
print(f'✅ meb_bulgulari empty: {len(meb_bulgulari) == 0}')

if meb_bulgulari:
    print('\n=== MEB BULGULARI CONTENT (first 1500 chars) ===')
    print(json.dumps(meb_bulgulari, indent=2, ensure_ascii=False)[:1500])
else:
    print('\n❌ meb_bulgulari BOŞ - FALLBACK KULLANILACAK!')
    print('\n=== MEB KRITERLER (Risk > 0 olan) ===')
    kriterler = analiz.get('meb_degerlendirmesi', {}).get('meb_kriterler', {})
    for k, v in kriterler.items():
        if v.get('risk', 0) > 0:
            print(f'  {k}: risk={v["risk"]}, karar={v.get("karar", "?")}')

