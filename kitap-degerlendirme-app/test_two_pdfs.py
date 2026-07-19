import requests
import json

BASE_URL = 'http://localhost:5000'

# Test 1: İlk PDF
print('📖 PDF 1 Yükleniyor...')
with open('test_kitap.pdf', 'rb') as f:
    response1 = requests.post(f'{BASE_URL}/api/yukleme', files={'pdf': f})
    if response1.status_code == 200:
        path1 = response1.json()['dosya_yolu']
        eval1 = requests.post(f'{BASE_URL}/api/degerlendir', 
                             json={'dosya_yolu': path1, 'kitap_turu': 'Çocuk Kitabı'})
        if eval1.status_code == 200:
            r1 = eval1.json()
            print(f"  📚 Maarif Uyum: {r1['maarif_modeli']['genel_uyum_yuzde']}%")
            print(f"  🔍 Sakıncalı: {r1['sakincali_kelime']['toplam_bulgu']}")
            print(f"  🌍 Kültürel: {r1['kultural_uyum']['kültürel_uyum']}%")

# Test 2: İkinci PDF
print('\n📖 PDF 2 Yükleniyor...')
with open('test_kitap2.pdf', 'rb') as f:
    response2 = requests.post(f'{BASE_URL}/api/yukleme', files={'pdf': f})
    if response2.status_code == 200:
        path2 = response2.json()['dosya_yolu']
        eval2 = requests.post(f'{BASE_URL}/api/degerlendir', 
                             json={'dosya_yolu': path2, 'kitap_turu': 'Bilimkurgu'})
        if eval2.status_code == 200:
            r2 = eval2.json()
            print(f"  📚 Maarif Uyum: {r2['maarif_modeli']['genel_uyum_yuzde']}%")
            print(f"  🔍 Sakıncalı: {r2['sakincali_kelime']['toplam_bulgu']}")
            print(f"  🌍 Kültürel: {r2['kultural_uyum']['kültürel_uyum']}%")

print('\n✅ Sonuçlar FARKLIMI?')
if r1['maarif_modeli']['genel_uyum_yuzde'] != r2['maarif_modeli']['genel_uyum_yuzde']:
    print('   ✅ EVET! Her kitap farklı sonuç veriyor! 🎉')
else:
    print('   ❌ HAYIR - Aynı sonuçlar')
