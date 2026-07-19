import requests
import json

BASE_URL = 'http://localhost:5000'

# 1. PDF yükle
print('📤 PDF yükleniyor...')
with open('test_kitap.pdf', 'rb') as f:
    files = {'pdf': f}
    response = requests.post(f'{BASE_URL}/api/yukleme', files=files)
    print(f'Yükleme status: {response.status_code}')
    
    if response.status_code == 200:
        yukleme_sonucu = response.json()
        dosya_yolu = yukleme_sonucu['dosya_yolu']
        print(f'✅ Dosya yüklendi: {dosya_yolu}')
        
        # 2. Değerlendir
        print('\n🔍 Değerlendirme yapılıyor...')
        degerlen_data = {
            'dosya_yolu': dosya_yolu,
            'kitap_turu': 'Çocuk Kitabı'
        }
        degerlen_response = requests.post(f'{BASE_URL}/api/degerlendir', json=degerlen_data)
        print(f'Değerlendirme status: {degerlen_response.status_code}')
        
        if degerlen_response.status_code == 200:
            sonuc = degerlen_response.json()
            
            # Sonuçları göster
            print('\n📊 SONUÇLAR:')
            
            if 'maarif_modeli' in sonuc:
                print(f"  ✅ Maarif Modeli Uyum: {sonuc['maarif_modeli'].get('genel_uyum_yuzde', 'N/A')}%")
                print(f"  📈 En Güçlü: {sonuc['maarif_modeli'].get('en_guclu_profil', 'N/A')}")
            
            if 'meb_ttk' in sonuc:
                meb = sonuc['meb_ttk']
                print(f"  ✅ MEB TTK Uyumlu: {meb.get('uyumlu_sayi', 0)}")
                print(f"  ⚠️  Kısmi Uyumlu: {meb.get('kismi_uyumlu_sayi', 0)}")
            
            if 'sakincali_kelime' in sonuc:
                print(f"  🔍 Sakıncalı Bulgu: {sonuc['sakincali_kelime'].get('toplam_bulgu', 0)}")
            
            if 'kultural_uyum' in sonuc:
                print(f"  🌍 Kültürel Uyum: {sonuc['kultural_uyum'].get('kültürel_uyum', 0)}%")
        else:
            print(f'❌ Hata: {degerlen_response.text[:500]}')
    else:
        print(f'❌ Yükleme hatası: {response.text[:200]}')
