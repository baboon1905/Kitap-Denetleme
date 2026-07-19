"""
TEST: Gerçek PDF dosyası ile sistem testi
"""
import requests
import json

print('📖 PDF Analiz Başlıyor...\n')

# Dosya upload et
print('📤 Dosya yükleniyor...')
try:
    files = {'pdf': open('uploads/Sihirli_Duduk.pdf', 'rb')}
    data = {
        'baslik': 'SİHİRLİ DÜDÜK - PANKİ\'NİN ARKADAŞI',
        'yazar': 'NUR İÇÖZÜ',
        'yayinevi': 'ALTIN KİTAPLAR YAYINEVİ'
    }

    response = requests.post('http://127.0.0.1:5000/api/yukleme', files=files, data=data)
    print('✅ Dosya yüklendi\n')

    if response.status_code == 200:
        result = response.json()
        dosya_yolu = result.get('dosya_yolu')
        
        # Analiz yap
        print('🔍 Analiz yapılıyor (hibrit profil)...')
        analysis = requests.post('http://127.0.0.1:5000/api/degerlendir', json={
            'dosya_yolu': dosya_yolu,
            'profil': 'hibrit',
            'yas_grubu': '6-12'
        })
        
        if analysis.status_code == 200:
            sonuc = analysis.json()
            print(f'\n✅ Analiz Tamamlandı!')
            print(f'📊 Final Skor: {sonuc["final_skor"]}/100')
            print(f'🎯 Karar: {sonuc["karar"]["seviye"]}')
            print(f'🔍 Bulunan Kategori Sayısı: {sonuc["kategori_sayisi"]}')
            
            # Detaylı bulgular
            for kategori, bulgular in sonuc['kategori_bulgulari'].items():
                if bulgular['bulundu']:
                    print(f'\n📋 {kategori}: {bulgular["toplam_bulgu"]} bulgu')
                    for i, bulgu in enumerate(bulgular['bulunan_kelimeler'][:5], 1):
                        print(f'   {i}. "{bulgu["kelime"]}" → Risk: {bulgu["baglamsal_risk"]}/5')
                        print(f'      📄 Sayfa {bulgu["sayfa"]}, Kontekst: {bulgu["kontext"][:60]}...')
        else:
            print(f'❌ Analiz hatası: {analysis.text}')
    else:
        print(f'❌ Yükleme hatası: {response.text}')
        
except FileNotFoundError:
    print('❌ PDF dosyası bulunamadı. Lütfen dosyayı yükleyin.')
except Exception as e:
    print(f'❌ Hata: {str(e)}')
