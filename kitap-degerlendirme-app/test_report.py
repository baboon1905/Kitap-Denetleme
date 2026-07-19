#!/usr/bin/env python
import requests
import json

# Dosya yükle
with open('uploads/Anahtar_Acmaz.pdf', 'rb') as f:
    files = {'pdf': f}
    resp = requests.post('http://localhost:5000/api/yukleme', files=files)
    upload_data = resp.json()
    dosya_yolu = upload_data['dosya_yolu']
    print(f'✓ Dosya yüklendi: {dosya_yolu}')

# Analiz et
data = {
    'dosya_yolu': dosya_yolu,
    'profil': 'hibrit',
    'yas_grubu': '9-12'
}
resp = requests.post('http://localhost:5000/api/degerlendir', json=data)
analysis_data = resp.json()
print(f'✓ Analiz tamamlandı')

# Rapor oluştur
rapor_data = {
    'kitap_adi': upload_data['kitap_adi'],
    'analiz_sonucu': analysis_data['analiz_sonucu']
}
print(f'kitap_adi: {rapor_data["kitap_adi"]}')
print(f'analiz_sonucu type: {type(rapor_data["analiz_sonucu"]).__name__}')

# Rapor endpoint'ini test et
resp = requests.post('http://localhost:5000/api/rapor', json=rapor_data)
print(f'\nRapor endpoint status: {resp.status_code}')
if resp.status_code != 200:
    print(f'Error: {resp.text[:500]}')
else:
    print(f'PDF başarıyla oluşturuldu. Size: {len(resp.content)} bytes')
