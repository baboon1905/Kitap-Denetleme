# -*- coding: utf-8 -*-
"""
API Endpoint Test - /api/degerlendir
Gerçek API çağrısını test et
"""

import sys
sys.path.insert(0, '.')

import json
from flask import Flask, request, jsonify
from app import app
from evaluator_maarif import MaarifDegerlendiricisi

# Test metni - FALSE POSITIVE'ler
test_data = {
    "metin": """
    Adım Ceylan. Serkan benim arkadaşım.
    Müzede havalandı salon. Büyükbabası geldi.
    Bölüm 1 başlamış. Yayınevim başarılı.
    Sigaranın tadı güzel. Alkol içmek zararlı.
    Katlayıp puttuğu kağıt.
    """,
    "profil": "maarif_meb"
}

print("=" * 80)
print("🧪 API ENDPOINT TEST - /api/degerlendir")
print("=" * 80)

# App context'i içinde test et
with app.test_client() as client:
    # POST request gönder
    response = client.post(
        '/api/degerlendir',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    print(f"\n✓ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        sonuc = response.get_json()
        
        print("\n✓ RAPOR EDILEN BULGULAR:")
        print("-" * 80)
        
        kategori_bulgulari = sonuc.get('kategori_bulgulari', {})
        
        toplam = 0
        for kategori, veri in kategori_bulgulari.items():
            if veri.get('toplam_bulgu', 0) > 0:
                toplam += veri['toplam_bulgu']
                print(f"\n🔴 {kategori}: {veri['toplam_bulgu']} bulgu")
                for item in veri.get('bulunan_kelimeler', [])[:3]:
                    print(f"   - {item['kelime']}: {item['kontext'][:50]}...")
        
        print(f"\n{'=' * 80}")
        print(f"📊 Toplam: {toplam} bulgu")
        print(f"📈 Skor: {sonuc.get('final_skor', 0):.0f}/100")
        print(f"{'=' * 80}")
        
        # Kontrol
        print("\n⚠️  SORUN VAR MI?")
        has_false_positives = toplam > 5
        if has_false_positives:
            print("❌ FALSE POSITIVE'ler hala rapor ediliyor!")
        else:
            print("✅ Sistem doğru - Sadece TRUE POSITIVE'ler rapor ediliyor")
    else:
        print(f"\n❌ Hata: {response.data}")
