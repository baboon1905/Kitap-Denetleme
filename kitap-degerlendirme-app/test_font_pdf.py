#!/usr/bin/env python
"""
Türkçe karakter desteğini test etmek için PDF oluştur
"""

import requests
import json
from datetime import datetime

print("=" * 70)
print("🔤 TÜRKÇE KARAKTER DESTEĞI TESTİ")
print("=" * 70)

# Dosya yükle
print("\n1️⃣  Dosya yükleniyor...")
with open('uploads/Anahtar_Acmaz.pdf', 'rb') as f:
    files = {'pdf': f}
    resp = requests.post('http://localhost:5000/api/yukleme', files=files)
    upload_data = resp.json()
    dosya_yolu = upload_data['dosya_yolu']
    print(f"   ✓ Dosya yüklendi: {dosya_yolu}")

# Analiz et
print("\n2️⃣  Metin analizi yapılıyor...")
data = {
    'dosya_yolu': dosya_yolu,
    'profil': 'hibrit',
    'yas_grubu': '9-12'
}
resp = requests.post('http://localhost:5000/api/degerlendir', json=data)
analysis_data = resp.json()
print(f"   ✓ Analiz tamamlandı")
print(f"   - Final Skor: {analysis_data['analiz_sonucu'].get('final_skor', 'N/A')}")

# Kategori bilgileri
kategoriler = analysis_data['analiz_sonucu'].get('kategori_bulgulari', {})
print(f"   - Bulunan kategoriler: {sum(1 for k, v in kategoriler.items() if v.get('toplam_bulgu', 0) > 0)}")

# Rapor oluştur
print("\n3️⃣  PDF Rapor oluşturuluyor...")
rapor_data = {
    'kitap_adi': upload_data['kitap_adi'],
    'analiz_sonucu': analysis_data['analiz_sonucu']
}

resp = requests.post('http://localhost:5000/api/rapor', json=rapor_data)
if resp.status_code == 200:
    # PDF'yi kaydet
    pdf_filename = f"test_rapor_turkce_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    with open(pdf_filename, 'wb') as f:
        f.write(resp.content)
    print(f"   ✓ PDF başarıyla oluşturuldu")
    print(f"   - Dosya adı: {pdf_filename}")
    print(f"   - Dosya boyutu: {len(resp.content):,} bytes")
    print(f"\n📋 Raporun içeriği kontrol edilmeli:")
    print(f"   - Başlık: 'SAKİNÇALI İÇERİK TARAMA RAPORU' (Türkçe karakterler)")
    print(f"   - Kategori adları (Şiddet, Cinsellik, Okültizm vs.)")
    print(f"   - Tavsiye bölümü (kategori bazlı öneriler)")
else:
    print(f"   ✗ Hata: {resp.status_code}")
    print(f"   {resp.text[:200]}")

print("\n" + "=" * 70)
print("✅ TEST TAMAMLANDI")
print("=" * 70)
