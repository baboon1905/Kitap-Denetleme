#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct Test: Zararlı Alışkanlıklar - Kontekst Analiz Kuralları
Test _cumle_konteksti_analiz_et() metodunun doğrudan çıktısını kontrol et
"""

import os
import sys
from evaluator_maarif import MaarifDegerlendiricisi

# Test Kuralları
TEST_CASES = [
    # ✅ HARMLESS - EĞİTSEL KULLANIM
    {
        "cumle": "musa dayı sigaranın sağlığa zararlı olduğunu anlattı",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "varsayilan_risk": 4,
        "beklenen_risk": 0,
        "tip": "Eğitsel (sağlığa zararlı)",
    },
    {
        "cumle": "öğretmen alkol içmenin zararlarını detaylı anlattı",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "alkol",
        "varsayilan_risk": 4,
        "beklenen_risk": 0,
        "tip": "Eğitsel (zararlarını anlatma)",
    },
    {
        "cumle": "doktor sigaranın tehlikesi konusunda uyarı verdi",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "varsayilan_risk": 4,
        "beklenen_risk": 0,
        "tip": "Eğitsel (doktor uyarısı)",
    },
    {
        "cumle": "sağlık eğitiminde nargile kullanımının riskli olduğu belirtildi",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "nargile",
        "varsayilan_risk": 4,
        "beklenen_risk": 0,
        "tip": "Eğitsel (sağlık eğitimi)",
    },
    
    # ✅ HARMLESS - TARİHSEL KULLANIM
    {
        "cumle": "tarih 1950 yılında sigarayı herkes içiyordu",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "varsayilan_risk": 4,
        "beklenen_risk": 0,
        "tip": "Tarihsel (1950 yılında)",
    },
    {
        "cumle": "antik çağda alkol törenler için kullanılırdı",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "alkol",
        "varsayilan_risk": 4,
        "beklenen_risk": 0,
        "tip": "Tarihsel (antik çağ)",
    },
    
    # ✅ HARMLESS - ELEŞTİREL KULLANIM
    {
        "cumle": "sigaralamak çekilmez ve tehlikeli bir alışkanlıktır",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "varsayilan_risk": 4,
        "beklenen_risk": 0,
        "tip": "Eleştirel (çekilmez)",
    },
    {
        "cumle": "alkol içmek olumsuz bir karakter özelliği olarak gösterilir",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "alkol",
        "varsayilan_risk": 4,
        "beklenen_risk": 0,
        "tip": "Eleştirel (olumsuz karakter)",
    },
    
    # ❌ HARMFUL - ÖZENDİRİCİ KULLANIM
    {
        "cumle": "sigaranın tadı çok güzel ve harika",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "varsayilan_risk": 4,
        "beklenen_risk": 4,
        "tip": "Özendirici (güzel tadı)",
    },
    {
        "cumle": "alkol içmek çok rahatlatan ve keyif verici bir deneyim",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "alkol",
        "varsayilan_risk": 4,
        "beklenen_risk": 4,
        "tip": "Özendirici (keyif verici)",
    },
    {
        "cumle": "kumar oynayan kız çok eğlenceliydi ve harika hissettiriyordu",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "kumar",
        "varsayilan_risk": 4,
        "beklenen_risk": 4,
        "tip": "Özendirici (eğlenceliydi)",
    },
    
    # ❌ HARMFUL - TAKLİT TEŞVİKİ
    {
        "cumle": "sigara deneyin çok iyi gelecek",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "varsayilan_risk": 4,
        "beklenen_risk": 4,
        "tip": "Taklit teşviki (deneyin)",
    },
    {
        "cumle": "birkaç arkadaş alkol içmeye başladı ve çok eğlendiler",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "alkol",
        "varsayilan_risk": 4,
        "beklenen_risk": 4,
        "tip": "Taklit teşviki (başlama)",
    },
    
    # ❌ HARMFUL - POZİTİF GÖSTERİM
    {
        "cumle": "başarılı bir karakter olarak sigarayla resmediliyordu",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "varsayilan_risk": 4,
        "beklenen_risk": 4,
        "tip": "Pozitif gösterim (başarılı karakter)",
    },
    {
        "cumle": "kahramanın güçlü karakteri alkol içerken vurgulanırdı",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "alkol",
        "varsayilan_risk": 4,
        "beklenen_risk": 4,
        "tip": "Pozitif gösterim (kahraman)",
    },
]

def test_kontekst_analiz_dogrudan():
    """Kontekst analiz metodunu doğrudan test et"""
    
    print("=" * 80)
    print("🧪 TEST: Zararlı Alışkanlıklar - Kontekst Analiz Kuralları (Doğrudan)")
    print("=" * 80)
    
    evaluator = MaarifDegerlendiricisi()
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(TEST_CASES, 1):
        cumle = test_case["cumle"]
        kategori = test_case["kategori"]
        kelime = test_case["kelime"]
        varsayilan_risk = test_case["varsayilan_risk"]
        beklenen_risk = test_case["beklenen_risk"]
        tip = test_case["tip"]
        
        # Kontekst analiz metodunu doğrudan çağır
        actual_risk = evaluator._cumle_konteksti_analiz_et(
            cumle, 
            kelime,
            kategori,
            varsayilan_risk
        )
        
        # Test sonucu
        is_passed = actual_risk == beklenen_risk
        
        status = "✅ PASS" if is_passed else "❌ FAIL"
        passed += 1 if is_passed else 0
        failed += 0 if is_passed else 1
        
        print(f"\n[Test {i:2d}] {status} | {tip}")
        print(f"  Cümle: {cumle[:70]}...")
        print(f"  Kategori: {kategori}")
        print(f"  Beklenen Risk: {beklenen_risk}/5")
        print(f"  Gerçek Risk:   {actual_risk}/5")
        if not is_passed:
            print(f"  ⚠️  UYUMSUZLUK: Beklenen={beklenen_risk}, Gerçek={actual_risk}")
    
    print("\n" + "=" * 80)
    print(f"📊 SONUÇ: {passed} BAŞARILI, {failed} BAŞARISIZ (Toplam: {len(TEST_CASES)})")
    print(f"✅ Başarı Oranı: {100*passed/len(TEST_CASES):.1f}%")
    print("=" * 80)
    
    return failed == 0

if __name__ == "__main__":
    success = test_kontekst_analiz_dogrudan()
    sys.exit(0 if success else 1)
