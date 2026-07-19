#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test: Zararlı Alışkanlıklar Kategorisi - Kontekst Analiz Kuralları
Test the new context analysis rules for "zararlı_alışkanlıklar" category
"""

import os
import sys
from evaluator_maarif import MaarifDegerlendiricisi

# Test metinleri
TEST_CASES = [
    # ✅ HARMLESS - EĞİTSEL KULLANIM
    {
        "metin": "Musa Dayı sigaranın sağlığa zararlı olduğunu anlattı.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "beklenen_risk": 0,
        "tip": "Eğitsel (sağlığa zararlı)",
    },
    {
        "metin": "Öğretmen alkol içmenin zararlarını detaylı anlattı.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "alkol",
        "beklenen_risk": 0,
        "tip": "Eğitsel (zararlarını anlatma)",
    },
    {
        "metin": "Doktor, sigaranın tehlikesi konusunda uyarı verdi.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "beklenen_risk": 0,
        "tip": "Eğitsel (doktor uyarısı)",
    },
    {
        "metin": "Sağlık eğitiminde nargile kullanımının riskli olduğu belirtildi.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "nargile",
        "beklenen_risk": 0,
        "tip": "Eğitsel (sağlık eğitimi)",
    },
    
    # ✅ HARMLESS - TARİHSEL KULLANIM
    {
        "metin": "Tarih 1950 yılında sigarayı herkes içiyordu.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "beklenen_risk": 0,
        "tip": "Tarihsel (1950 yılında)",
    },
    {
        "metin": "Antik çağda alkol törenler için kullanılırdı.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "alkol",
        "beklenen_risk": 0,
        "tip": "Tarihsel (antik çağ)",
    },
    {
        "metin": "Müzede sergilenen eski nargile, 200 yıllık bir eserdir.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "nargile",
        "beklenen_risk": 0,
        "tip": "Tarihsel (müze)",
    },
    
    # ✅ HARMLESS - ELEŞTİREL KULLANIM
    {
        "metin": "Sigaralamak çekilmez ve tehlikeli bir alışkanlıktır.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "beklenen_risk": 0,
        "tip": "Eleştirel (çekilmez)",
    },
    {
        "metin": "Alkol içmek, olumsuz bir karakter özelliği olarak gösterilir.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "alkol",
        "beklenen_risk": 0,
        "tip": "Eleştirel (olumsuz karakter)",
    },
    {
        "metin": "Kumar oynamak, bir kötü tercih olarak tanımlanır.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "kumar",
        "beklenen_risk": 0,
        "tip": "Eleştirel (kötü tercih)",
    },
    
    # ❌ HARMFUL - ÖZENDİRİCİ KULLANIM
    {
        "metin": "Sigaranın tadı çok güzel, tadını almak harika.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "beklenen_risk": 4,
        "tip": "Özendirici (güzel tadı)",
    },
    {
        "metin": "Alkol içmek çok rahatlatan ve keyif verici bir deneyim.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "alkol",
        "beklenen_risk": 4,
        "tip": "Özendirici (keyif verici)",
    },
    {
        "metin": "Kumar oynayan kız çok eğlenceliydi ve harika hissettiriyordu.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "kumar",
        "beklenen_risk": 4,
        "tip": "Özendirici (eğlenceliydi)",
    },
    
    # ❌ HARMFUL - TAKLİT TEŞVİKİ
    {
        "metin": "Sigara deneyin, çok iyi gelecek.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "beklenen_risk": 4,
        "tip": "Taklit teşviki (deneyin)",
    },
    {
        "metin": "Birkaç arkadaş alkol içmeye başladı ve çok eğlendiler.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "alkol",
        "beklenen_risk": 4,
        "tip": "Taklit teşviki (başlama)",
    },
    {
        "metin": "İlk sigarası çok zevk verdi ve hemen devam etmek istedi.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "beklenen_risk": 4,
        "tip": "Taklit teşviki (ilk sigara)",
    },
    
    # ❌ HARMFUL - POZİTİF GÖSTERİM
    {
        "metin": "Başarılı ve saygın bir karakter olarak sigarayla resmediliyordu.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "beklenen_risk": 4,
        "tip": "Pozitif gösterim (başarılı karakter)",
    },
    {
        "metin": "Kahramanın güçlü karakteri alkol içerken vurgulanırdı.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "alkol",
        "beklenen_risk": 4,
        "tip": "Pozitif gösterim (kahraman)",
    },
    {
        "metin": "Başarı sonrası sevincle sigara içmeyi kutlarlardı.",
        "kategori": "zararlı_alışkanlıklar",
        "kelime": "sigara",
        "beklenen_risk": 4,
        "tip": "Pozitif gösterim (başarı kutlaması)",
    },
]

def test_zararlı_alışkanlıklar():
    """Test zararlı alışkanlıklar kategorisi kontekst kuralları"""
    
    print("=" * 80)
    print("🧪 TEST: Zararlı Alışkanlıklar Kategorisi - Kontekst Analiz Kuralları")
    print("=" * 80)
    
    evaluator = MaarifDegerlendiricisi()
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(TEST_CASES, 1):
        metin = test_case["metin"]
        kategori = test_case["kategori"]
        beklenen_risk = test_case["beklenen_risk"]
        tip = test_case["tip"]
        
        # Analiz yap
        result = evaluator.analiz_yap(metin, profil="hibrit")
        
        # Bulgular kullanılabilir mi kontrol et
        if "bulgular" not in result:
            print(f"  ❌ Result keys: {result.keys()}")
            actual_risk = -1
        elif kategori in result.get("bulgular", {}):
            bulgular_data = result["bulgular"][kategori]
            actual_risk = bulgular_data.get("ortalama_risk", -1)
        else:
            actual_risk = -1
        
        # Test sonucu
        is_passed = actual_risk == beklenen_risk
        
        status = "✅ PASS" if is_passed else "❌ FAIL"
        passed += 1 if is_passed else 0
        failed += 0 if is_passed else 1
        
        print(f"\n[Test {i:2d}] {status} | {tip}")
        print(f"  Metin: {metin[:60]}...")
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
    success = test_zararlı_alışkanlıklar()
    sys.exit(0 if success else 1)
