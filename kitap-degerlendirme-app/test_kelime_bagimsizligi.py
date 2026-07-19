#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test: Kelime Bağımsızlık Kontrol Mekanizması
Test word independence and false positive filtering
"""

import os
import sys
from evaluator_maarif import MaarifDegerlendiricisi

# Test Kuralları
TEST_CASES = [
    # ✅ BAĞIMSIZ (standalone word) - Bulgu GEÇERLİ
    {
        "metin": "Sigaranın sakıncaları var.",
        "kelime": "sigara",
        "beklenen_bagil": True,  # Bağımsız
        "tip": "Bağımsız kelime",
        "aciklama": "Başında ve sonunda harf yok"
    },
    {
        "metin": "Alkol içmek zararlı.",
        "kelime": "alkol",
        "beklenen_bagil": True,
        "tip": "Bağımsız kelime",
        "aciklama": "Başında ve sonunda harf yok"
    },
    
    # ❌ BAĞIMLI (embedded word) - Bulgu GEÇERSİZ
    {
        "metin": "Ceylan çok güzel.",
        "kelime": "lan",
        "beklenen_bagil": False,  # Bağımlı
        "tip": "İsim içinde gömülü",
        "aciklama": "Ceylan isiminin içine 'lan' gömülü → FALSE POSITIVE"
    },
    {
        "metin": "Havalandı çok serinletici.",
        "kelime": "lan",
        "beklenen_bagil": False,
        "tip": "Fiil conjugation'ında gömülü",
        "aciklama": "havalandı fiilinin içine 'lan' gömülü → FALSE POSITIVE"
    },
    {
        "metin": "Serkan çok zeki.",
        "kelime": "kan",
        "beklenen_bagil": False,
        "tip": "İsim içinde gömülü",
        "aciklama": "Serkan isiminin içine 'kan' gömülü → FALSE POSITIVE"
    },
    {
        "metin": "Yayınevim gayet başarılı.",
        "kelime": "ayin",
        "beklenen_bagil": False,
        "tip": "Kelime içinde gömülü",
        "aciklama": "yayınevi kelimesinin içine 'ayin' gömülü → FALSE POSITIVE"
    },
    {
        "metin": "Katlayıp gittin.",
        "kelime": "ayıp",
        "beklenen_bagil": False,
        "tip": "Fiil suffix'inde gömülü",
        "aciklama": "katlayıp fiilinin içine 'ayıp' gömülü → FALSE POSITIVE (-ayıp suffix)"
    },
    {
        "metin": "Ölüm çok ürkütücü.",
        "kelime": "ölüm",
        "beklenen_bagil": True,
        "tip": "Bağımsız kelime",
        "aciklama": "Bölüm'e karşı bağımsız kullanım"
    },
    {
        "metin": "Bölüm çok uzun.",
        "kelime": "ölüm",
        "beklenen_bagil": False,
        "tip": "Kelime içinde gömülü",
        "aciklama": "Bölüm kelimesinin içine 'ölüm' gömülü → FALSE POSITIVE"
    },
    
    # ✅ BAĞIMLI WORD BOUNDARY - Bulgu GEÇERSİZ
    {
        "metin": "Kargo getir.",
        "kelime": "argo",
        "beklenen_bagil": False,
        "tip": "Kelime sonu eşleşmesi",
        "aciklama": "kargo → argo gömülü"
    },
    {
        "metin": "Büyükbaba çok iyi.",
        "kelime": "büyü",
        "beklenen_bagil": False,
        "tip": "Kelime başında gömülü",
        "aciklama": "büyükbaba → 'büyü' gömülü"
    },
    {
        "metin": "Büyükanne sevgili.",
        "kelime": "büyü",
        "beklenen_bagil": False,
        "tip": "Kelime başında gömülü",
        "aciklama": "büyükanne → 'büyü' gömülü"
    },
    
    # ✅ GENUINE USAGE - Bulgu GEÇERLİ
    {
        "metin": "Büyüsü bozuldu.",
        "kelime": "büyü",
        "beklenen_bagil": True,
        "tip": "Bağımsız kullanım",
        "aciklama": "Sihir anlamında gerçek kullanım"
    },
    {
        "metin": "Eşek bir hayvandır.",
        "kelime": "eşek",
        "beklenen_bagil": True,
        "tip": "Bağımsız kelime",
        "aciklama": "Hayvan ismi olarak bağımsız"
    },
    {
        "metin": "Peşekli kır atı seviyor.",
        "kelime": "eşek",
        "beklenen_bagil": False,
        "tip": "Kelime içinde gömülü",
        "aciklama": "peşekli → 'eşek' gömülü"
    },
    
    # ✅ CONTEXT WORD BOUNDARIES
    {
        "metin": "Vurdu topunun başında.",
        "kelime": "vur",
        "beklenen_bagil": False,
        "tip": "Fiil conjugation'ında",
        "aciklama": "vurdu → 'vur' gömülü"
    },
    {
        "metin": "Vur bu topu!",
        "kelime": "vur",
        "beklenen_bagil": True,
        "tip": "Bağımsız fiil",
        "aciklama": "Emir kipi, bağımsız"
    },
]

def test_kelime_bagimsizligi():
    """Test kelime bağımsızlığı kontrol mekanizmasını"""
    
    print("=" * 90)
    print("🧪 TEST: Kelime Bağımsızlık Kontrol Mekanizması")
    print("=" * 90)
    print("\nKüçük kelimeler: 'lan', 'kan', 'ayin', 'ayıp', 'vur'")
    print("Kural: Eğer başka kelimenin içinde geçiyorsa → Bulgu GEÇERSİZ\n")
    
    evaluator = MaarifDegerlendiricisi()
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(TEST_CASES, 1):
        metin = test_case["metin"]
        kelime = test_case["kelime"]
        beklenen_bagil = test_case["beklenen_bagil"]
        tip = test_case["tip"]
        aciklama = test_case["aciklama"]
        
        # Analiz yap
        result = evaluator.analiz_yap(metin, profil="hibrit")
        
        # Bulguları kontrol et
        found = False
        actual_bagil = None
        
        for kategori, bulgular in result.get("bulgular", {}).items():
            if bulgular.get("bulundu"):
                for bulgu in bulgular.get("bulgular", []):
                    if bulgu["kelime"].lower() == kelime.lower():
                        found = True
                        # Eğer bulgu varsa, bulgu GEÇERLİ demektir
                        actual_bagil = True
                        break
        
        # Eğer hiç bulgu yoksa
        if not found:
            actual_bagil = False
        
        # Test sonucu
        is_passed = actual_bagil == beklenen_bagil
        
        status = "✅ PASS" if is_passed else "❌ FAIL"
        passed += 1 if is_passed else 0
        failed += 0 if is_passed else 1
        
        print(f"[Test {i:2d}] {status} | {tip}")
        print(f"  Metin: {metin}")
        print(f"  Kelime: '{kelime}'")
        print(f"  {aciklama}")
        print(f"  Beklenen Bağımsız: {beklenen_bagil} (Bulgu {'VAR' if beklenen_bagil else 'YOK'})")
        print(f"  Gerçek Bağımsız:   {actual_bagil} (Bulgu {'VAR' if actual_bagil else 'YOK'})")
        
        if not is_passed:
            print(f"  ⚠️  UYUMSUZLUK")
        print()
    
    print("=" * 90)
    print(f"📊 SONUÇ: {passed} BAŞARILI, {failed} BAŞARISIZ (Toplam: {len(TEST_CASES)})")
    print(f"✅ Başarı Oranı: {100*passed/len(TEST_CASES):.1f}%")
    print("=" * 90)
    
    return failed == 0

if __name__ == "__main__":
    success = test_kelime_bagimsizligi()
    sys.exit(0 if success else 1)
