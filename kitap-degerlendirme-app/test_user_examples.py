#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test: Kullanıcı rapor ettiği FALSE POSITIVE'ler
Bulan, heyecanlanmıştı, alçak, göz kamaştıran, bir kenara vb.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from evaluator_maarif import MaarifDegerlendiricisi

# Kullanıcı rapor ettiği örnekler
test_metin = """
Bulan kişiye bir şey ifade etmeyecekmiş.

Arkadaşı o kadar heyecanlanmıştı ki neredeyse çıkıp bahçesini kazmaya başlayacaktı.

Alçak sesle konuşuyordu ama yine de önemli detayları kaçırıyordu.

Herkes konseri dinlemek üzere yerini alınca, göz kamaştıran takıların fotoğraflarını çekmek üzere çıktı.

Böylece çok değerli saniyeler pizzadan tüten dumanla uçup gitti.

Depoyu arama işini şimdilik bir kenara bırakacaktı.

Arkadaşının paniklediğini gören Nilay, durumu toparlamaya çalıştı.

Kaçış yoktu! Herkes sıkışmıştı.
"""

evaluator = MaarifDegerlendiricisi()
sonuc = evaluator.analiz_yap(test_metin)

print("\n" + "="*70)
print("TEST: Kullanıcı Raporlama - FALSE POSITIVE Kontrolü")
print("="*70)

for kategori_adi, kategori_bulgular in sonuc["kategori_bulgulari"].items():
    if kategori_bulgular["bulundu"]:
        print(f"\n✅ KATEGORİ: {kategori_adi}")
        print(f"   Bulgu sayısı: {kategori_bulgular['toplam_bulgu']}")
        for bulgu in kategori_bulgular['bulunan_kelimeler']:
            print(f"   • '{bulgu['kelime']}' (Risk: {bulgu['baglamsal_risk']}/5)")
            print(f"     Kontekst: ...{bulgu['kontext'][:60]}...")

print("\n" + "="*70)
print("Beklenen Sonuç:")
print("  ❌ Bulan, heyecanlanmıştı, alçak = Filtered")
print("  ❌ göz kamaştıran (kama içinde) = Filtered")
print("  ❌ tüten duman, bir kenara, paniklediğini = Filtered")
print("  ❌ Kaçış yoktu = Filtered")
print("="*70)
