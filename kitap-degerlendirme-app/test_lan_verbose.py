#!/usr/bin/env python
"""
"lan" kelimesinin Risk 4 döndürüşünü debug et
Kontekst ve match'leri detaylı göster
"""

from evaluator_maarif import MaarifDegerlendiricisi

# Test metni
metin = "Başında lan kelimesi bulunuyor. Buraya lan yazıldı."

print("=" * 80)
print("🔍 DETAYLI 'LAN' DEBUG")
print("=" * 80)
print(f"\nMetin: \"{metin}\"")

evaluator = MaarifDegerlendiricisi()

# Tüm sonucu al
sonuc = evaluator.analiz_yap(metin, profil='hibrit', yas_grubu='10-15')

kaba_dil = sonuc['kategori_bulgulari'].get('kaba_dil_hakaret', {})

if kaba_dil['toplam_bulgu'] > 0:
    print(f"\n✅ Toplam {kaba_dil['toplam_bulgu']} bulgu\n")
    
    for i, bulgu in enumerate(kaba_dil['bulunan_kelimeler'], 1):
        print(f"BULGU {i}:")
        print(f"  Kelime: \"{bulgu['kelime']}\"")
        print(f"  Orijinal Risk: {bulgu.get('orijinal_risk')}/5")
        print(f"  Bağlamsal Risk: {bulgu.get('baglamsal_risk')}/5")
        print(f"  Kontekst: \"{bulgu.get('kontext')}\"")
        print()

# Şimdi manual olarak _baglamsal_analiz_yap çağır
print("=" * 80)
print("MANUAL BAGLAMSAL ANALIZ YAPILARI")
print("=" * 80)

# "lan" kelimesi'nin pozisyonlarını bul
import re

pattern = r'\blan\b'
for match in re.finditer(pattern, metin.lower()):
    basla = match.start()
    bitis = match.end()
    
    # Kontekst al
    kontekst_basla = max(0, basla - 150)
    kontekst_bitis = min(len(metin), bitis + 150)
    kontekst = metin[kontekst_basla:kontekst_bitis].lower()
    
    print(f"\n'lan' pozisyon: {basla}-{bitis}")
    print(f"  Kontekst ({len(kontekst)} char): \"{kontekst}\"")
    
    # Zararlı bağlamları kontrol et
    zararlı_lan_baglamları = ["ya lan", "o lan", "ha lan", "ulan", "lan be"]
    
    print(f"  Kontrol ediliyor:")
    for baglamı in zararlı_lan_baglamları:
        present = baglamı in kontekst
        print(f"    - '{baglamı}': {present}")
    
    # Evaluator'ün dönüşünü kontrol et
    risk = evaluator._baglamsal_analiz_yap(metin, basla, bitis, 3)
    print(f"  ➜ Evaluator Risk: {risk}/5")
