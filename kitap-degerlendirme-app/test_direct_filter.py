#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test: Gizli modda filter test - DIRECT ANALIZ (Upload değil)
"""

import json
import requests
from pathlib import Path

API_BASE = "http://127.0.0.1:5000"

def test_direct_analiz():
    """Doğrudan analiz test et - uploads dosyasını kullan"""
    
    print("=" * 70)
    print("🧪 TEST: FALSE POSITIVE Filter - DIRECT ANALIZ")
    print("=" * 70)
    
    # Dosya yolunu test et (browser tarafından upload edilmiş olmalı)
    dosya_yolu = "uploads/10_sihirli_duduk.pdf"
    
    # 1. Analiz yap
    print("\n1️⃣ Analiz Yapılıyor (Hibrit Profili, 9-12 yaş)...")
    analiz_data = {
        "dosya_yolu": dosya_yolu,
        "profil": "hibrit",
        "yas_grubu": "9-12"
    }
    
    try:
        r = requests.post(f"{API_BASE}/api/deverlendir", json=analiz_data, timeout=60)
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return
    
    if r.status_code != 200:
        print(f"❌ Analiz başarısız: {r.status_code}")
        print(r.text)
        return
    
    analiz_sonucu = r.json()
    print(f"✅ Analiz OK")
    
    # 2. Sonuçları kontrol et
    print("\n2️⃣ Sonuçlar Kontrol Ediliyor...")
    
    risk_skoru = analiz_sonucu.get('risk_skoru', 0)
    karar = analiz_sonucu.get('karar', '')
    kategori_bulgulari = analiz_sonucu.get('kategori_bulgulari', {})
    
    print(f"   Risk Skoru: {risk_skoru}/100")
    print(f"   Karar: {karar}")
    
    print("\n   📋 Kategori Bulguları:")
    total_findings = 0
    for kategori, bulgular in kategori_bulgulari.items():
        toplam = bulgular.get('toplam_bulgu', 0)
        risk = bulgular.get('ortalama_risk', 0)
        total_findings += toplam
        if toplam > 0:
            print(f"      {kategori}: {toplam} bulgu (Ort. Risk: {risk:.1f}/5)")
            
            # Kelimeleri listele
            bulunan = bulgular.get('bulunan_kelimeler', [])
            for i, bulgu in enumerate(bulunan):
                kelime = bulgu.get('kelime', '?')
                if i < 3:
                    print(f"         - '{kelime}'")
            
            if len(bulunan) > 3:
                print(f"         ... ve {len(bulunan) - 3} daha")
    
    # 3. KONTROL: FALSE POSITIVE'ler filtered mi?
    print("\n3️⃣ FALSE POSITIVE Filter Kontrolü:")
    
    if risk_skoru == 0 and total_findings == 0:
        print(f"   ✅ BAŞARILI: Risk 0/100, Bulgu 0")
        print(f"      → Filter MÜKEMMEL çalışıyor!")
        return True
    elif risk_skoru < 30 and total_findings < 10:
        print(f"   ⚠️ KISMI: Risk {risk_skoru}, Bulgu {total_findings}")
        print(f"      → Çoğu false positive filtered")
        return True
    else:
        print(f"   ❌ BAŞARISIZ: Risk {risk_skoru}, Bulgu {total_findings}")
        print(f"      → Filter ÇALIŞMIYOR!")
        return False

if __name__ == "__main__":
    result = test_direct_analiz()
    print("\n" + "=" * 70)
    if result:
        print("✅ TEST PASSED")
    else:
        print("❌ TEST FAILED")
    print("=" * 70)
