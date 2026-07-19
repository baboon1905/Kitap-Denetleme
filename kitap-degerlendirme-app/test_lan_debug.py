#!/usr/bin/env python
"""
"lan" kelimesinin nasıl bulunduğunu debug et
Risk 3 nereden geliyor?
"""

from evaluator_maarif import MaarifDegerlendiricisi
import json

print("=" * 80)
print("🔍 'LAN' KELİMESİNİN NASIL BULUNDUĞU - DEBUG")
print("=" * 80)

# Test metinleri oluştur
test_metinler = {
    "Havalandı": "Ağaç havalandı ve yaprakları sallandı.",
    "Zararlı LAN": "Ya lan! Ulan ne biçim davranış!",
    "Standalone LAN": "Başında lan kelimesi bulunuyor. Buraya lan yazıldı.",
    "Metin": "--- SAYFA 15 ---\nBu sayfada 'lan' kelimesi yazıldı burada. Havalandı bahçe.",
}

evaluator = MaarifDegerlendiricisi()

for test_adi, metin in test_metinler.items():
    print(f"\n📝 TEST: {test_adi}")
    print(f"   Metin: \"{metin}\"")
    
    # Analiz yap
    sonuc = evaluator.analiz_yap(metin, profil='hibrit', yas_grubu='10-15')
    
    # Kaba dil kategorisini al
    kaba_dil = sonuc['kategori_bulgulari'].get('kaba_dil_hakaret', {})
    
    if kaba_dil['toplam_bulgu'] > 0:
        print(f"\n   ✅ Toplam {kaba_dil['toplam_bulgu']} bulgu:")
        for i, bulgu in enumerate(kaba_dil['bulunan_kelimeler'][:5], 1):
            kelime = bulgu['kelime']
            bag_risk = bulgu.get('baglamsal_risk', '?')
            orig_risk = bulgu.get('orijinal_risk', '?')
            kontekst = bulgu.get('kontext', '')[:70]
            print(f"      {i}. Kelime: \"{kelime}\", Risk: {bag_risk}/5 (Orijinal: {orig_risk}/5)")
            print(f"         Kontekst: \"{kontekst}...\"")
    else:
        print(f"   ✅ Bulgu: 0")

# Config'i kontrol et
print("\n" + "=" * 80)
print("📋 CONFIG.PY'DE 'LAN' ÇEŞITLERI")
print("=" * 80)

from config import SAKINCALI_KELIMELER

kaba_dil_category = SAKINCALI_KELIMELER.get('kaba_dil_hakaret', {})
kaba_dil_kelimeler = kaba_dil_category.get('kelimeler', [])
lan_keywords = [k for k in kaba_dil_kelimeler if 'lan' in k.lower()]

print(f"\n'lan' içeren kelimeler ({len(lan_keywords)} adet):")
for kelime in lan_keywords[:10]:
    print(f"  - \"{kelime}\"")

if len(lan_keywords) > 10:
    print(f"  ... ve {len(lan_keywords) - 10} daha")

# "ulan" kontrol et
print("\nConfigleri kontrol:")
if "ulan" in kaba_dil_kelimeler:
    print("  ✅ 'ulan' config'de tanımlı")
else:
    print("  ❌ 'ulan' config'de tanımlı DEĞİL")

if "lan" in kaba_dil_kelimeler:
    print("  ✅ 'lan' config'de tanımlı")
else:
    print("  ❌ 'lan' config'de tanımlı DEĞİL")

