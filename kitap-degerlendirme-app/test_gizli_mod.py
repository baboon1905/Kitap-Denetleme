#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test: Gizli modda filter test (FALSE POSITIVE filter tüm kelimeleri filtreliyor mu?)
"""

import json
import requests
from pathlib import Path

API_BASE = "http://127.0.0.1:5000"
PDF_YOLU = r"c:\Users\fatih\Masaüstü\Kitap Değerlendirme\kitap-degerlendirme-app\uploads\10_sihirli_duduk.pdf"

def test_analiz():
    """Analiz test et"""
    
    print("=" * 70)
    print("🧪 TEST: FALSE POSITIVE Filter Kontrolü")
    print("=" * 70)
    
    # 1. PDF upload
    print("\n1️⃣ PDF Yükleniyor...")
    with open(PDF_YOLU, 'rb') as f:
        files = {'dosya': f}
        r = requests.post(f"{API_BASE}/api/yukleme", files=files, timeout=30)
    
    if r.status_code != 200:
        print(f"❌ Upload başarısız: {r.status_code}")
        print(r.text)
        return
    
    upload_data = r.json()
    print(f"✅ Upload OK")
    print(f"   Dosya adı: {upload_data.get('dosya_adi')}")
    print(f"   Sayfa sayı: {upload_data.get('sayfa_sayisi')}")
    
    dosya_yolu = upload_data.get('dosya_yolu')
    
    # 2. Analiz yap
    print("\n2️⃣ Analiz Yapılıyor (Hibrit Profili, 9-12 yaş)...")
    analiz_data = {
        "dosya_yolu": dosya_yolu,
        "profil": "hibrit",
        "yas_grubu": "9-12"
    }
    
    r = requests.post(f"{API_BASE}/api/deverlendir", json=analiz_data, timeout=60)
    
    if r.status_code != 200:
        print(f"❌ Analiz başarısız: {r.status_code}")
        print(r.text)
        return
    
    analiz_sonucu = r.json()
    print(f"✅ Analiz OK")
    
    # 3. Sonuçları kontrol et
    print("\n3️⃣ Sonuçlar Kontrol Ediliyor...")
    
    risk_skoru = analiz_sonucu.get('risk_skoru', 0)
    karar = analiz_sonucu.get('karar', '')
    kategori_bulgulari = analiz_sonucu.get('kategori_bulgulari', {})
    
    print(f"   Risk Skoru: {risk_skoru}/100")
    print(f"   Karar: {karar}")
    
    print("\n   📋 Kategori Bulguları:")
    for kategori, bulgular in kategori_bulgulari.items():
        toplam = bulgular.get('toplam_bulgu', 0)
        risk = bulgular.get('ortalama_risk', 0)
        if toplam > 0:
            print(f"      {kategori}: {toplam} bulgu (Ort. Risk: {risk:.1f}/5)")
            
            # Kelimeleri listele
            bulunan = bulgular.get('bulunan_kelimeler', [])
            for bulgu in bulunan[:5]:  # İlk 5'i göster
                kelime = bulgu.get('kelime', '?')
                print(f"         - '{kelime}'")
            
            if len(bulunan) > 5:
                print(f"         ... ve {len(bulunan) - 5} daha")
    
    # 4. KONTROL: FALSE POSITIVE'ler filtered mi?
    print("\n4️⃣ FALSE POSITIVE Filter Kontrolü:")
    
    # Beklenen: 0 bulgu (tüm kelimeleri filter olmalı)
    toplam_bulgu = sum(b.get('toplam_bulgu', 0) for b in kategori_bulgulari.values())
    
    if risk_skoru == 0 and toplam_bulgu == 0:
        print(f"   ✅ BAŞARILI: Risk 0/100, Bulgu 0 (Filter çalışıyor!)")
    elif risk_skoru < 50 and toplam_bulgu < 20:
        print(f"   ⚠️ KISMI BAŞARILI: Risk {risk_skoru}, Bulgu {toplam_bulgu} (Çoğu filtered)")
    else:
        print(f"   ❌ BAŞARISIZ: Risk {risk_skoru}, Bulgu {toplam_bulgu} (Filter çalışmıyor!)")
        print(f"      → Bu sayılar çok YÜKSEK (FALSE POSITIVE'ler filtered DEĞİL)")
    
    # 5. Rapor oluştur ve download et
    print("\n5️⃣ Rapor Oluşturuluyor...")
    rapor_data = analiz_sonucu
    r = requests.post(f"{API_BASE}/api/rapor", json=rapor_data, timeout=30)
    
    if r.status_code == 200:
        # Raporu kaydet
        rapor_dosya = f"test_rapor_gizli_mod_{int(risk_skoru)}.pdf"
        with open(rapor_dosya, 'wb') as f:
            f.write(r.content)
        print(f"   ✅ Rapor kaydedildi: {rapor_dosya}")
        print(f"      Boyut: {len(r.content) / 1024:.1f} KB")
    else:
        print(f"   ❌ Rapor oluşturma başarısız: {r.status_code}")
    
    print("\n" + "=" * 70)
    print("✅ TEST TAMAMLANDI")
    print("=" * 70)

if __name__ == "__main__":
    test_analiz()
