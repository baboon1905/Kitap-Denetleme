#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test: MEB Bulguları Entegrasyon Hatası Düzeltmesi"""

from meb_entegrasyon import ekle_meb_bulgularini

# Test sonucu
test_sonuc = {
    'meb_degerlendirmesi': {
        'meb_kriterler': {'anayasa': {'karar': 'Uyumlu', 'risk': 0}},
        'meb_puani': 50,
        'genel_karar': 'KOSULLU'
    }
}

# Test metni - MEB bulgularını içer
test_metin = '''Kitap pkk direniş bahsediyor. Teror örgütü dhkp-c yazı kufur sözcüğü hakaret'''

# Entegrasyon yap
result = ekle_meb_bulgularini(test_sonuc, test_metin)

# Sonuçları göster
meb_eval = result.get('meb_degerlendirmesi', {})
meb_bulgulari = meb_eval.get('meb_bulgulari', {})

print('=' * 50)
print('MEB BULGULARI ENTEGRASYONU - TEST')
print('=' * 50)
print(f'OK: meb_bulgulari dogru yerde mi? {"meb_bulgulari" in meb_eval}')
print(f'OK: Bulgular bulundu mu? {bool(meb_bulgulari)}')

if meb_bulgulari:
    print(f'✓ Toplam {len([b for bs in meb_bulgulari.values() for b in bs])} bulgu bulundu:')
    for kriter, bulgular in meb_bulgulari.items():
        if bulgular:
            print(f'  - {kriter}: {len(bulgular)} bulgu')
            for i, bulgu in enumerate(bulgular, 1):
                print(f'    {i}. "{bulgu["alininti"][:50]}..." (Risk: {bulgu["risk_puani"]}/5)')
else:
    print('⚠️  Bulgu bulunamadı!')

print('=' * 50)
print('4.1 Detayli Bulgu Analizi bölümü oluşturulacak mı?', 'EVET' if meb_bulgulari and any(meb_bulgulari.values()) else 'HAYIR')
