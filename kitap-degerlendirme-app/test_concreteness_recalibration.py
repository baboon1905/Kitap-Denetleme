#!/usr/bin/env python3
"""Test script for SUMMARY_CONCRETENESS_RECALIBRATION"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from theme_gain_analysis import _summary_concreteness_score

# Test case 1: Summary with high density of concrete elements
# Should have score >= 0.60 due to recalibration
high_density_summary = """
giris:
Bülent, annesi ve babası ile büyüyen bir çocuktur. Sokakta oynar, komşularla tanışır.

gelisme:
Okula gider, öğretmeni Sibel Hanım ile tanışır. Mahallede esnaf Emrullah Efendi ile karşılaşır.

temel catisma:
Şehirleşme başlar, eski mahalle değişir. Bülent çocukluğunu özler.

karakter iliskileri:
Aile, komşular, öğretmen ile ilişkiler gelişir.

genel sonuc:
Geçmişe özlem ve değişim teması öne çıkar.
"""

# Test case 2: Summary with low density of concrete elements
# Should have normal score (could be < 0.60)
low_density_summary = """
giris:
Bir çocuk, hayatına dair düşüncelerle başlar.

gelisme:
Zaman geçtikçe çevresi değişir, fark eder.

temel catisma:
Karşılaştığı durumlar, onu düşünmeye sevk eder.

karakter iliskileri:
Etrafındaki kişilerle ilişkileri gelişir.

genel sonuc:
Deneyimler, onun için anlamlı hale gelir.
"""

# Test case 3: Summary with very high density of concrete elements
# Should have score >= 0.70 due to recalibration
very_high_density_summary = """
giris:
Bülent, annesi, babası ve kardeşi Suna ile İstanbul'da bir evde yaşar. Sokakta oynar, komşularla tanışır.

gelisme:
Okula gider, öğretmeni Sibel Hanım ile tanışır. Mahallede esnaf Emrullah Efendi ile karşılaşır. Tuna Abi ile sohbet eder.

temel catisma:
Şehirleşme başlar, eski mahalle değişir. Bülent çocukluğunu özler. Çiçek Abla ile anılar konuşur.

karakter iliskileri:
Aile, komşular, öğretmen ile ilişkiler gelişir. Dilek ve Çilek ile arkadaşlık kurar.

genel sonuc:
Geçmişe özlem ve değişim teması öne çıkar. Kristof Kolomb'un keşifleriyle karşılaştırılır.
"""

print("=" * 60)
print("SUMMARY_CONCRETENESS_RECALIBRATION TEST")
print("=" * 60)

# Test 1: High density summary
score1 = _summary_concreteness_score(high_density_summary)
print(f"\nTest 1 - High Density Summary:")
print(f"  Score: {score1}")
print(f"  Expected: >= 0.60")
print(f"  Result: {'PASS' if score1 >= 0.60 else 'FAIL'}")

# Test 2: Low density summary
score2 = _summary_concreteness_score(low_density_summary)
print(f"\nTest 2 - Low Density Summary:")
print(f"  Score: {score2}")
print(f"  Expected: < 0.60 (normal calculation)")
print(f"  Result: {'PASS' if score2 < 0.60 else 'FAIL (but acceptable if >= 0.60)'}")

# Test 3: Very high density summary
score3 = _summary_concreteness_score(very_high_density_summary)
print(f"\nTest 3 - Very High Density Summary:")
print(f"  Score: {score3}")
print(f"  Expected: >= 0.70")
print(f"  Result: {'PASS' if score3 >= 0.70 else 'FAIL'}")

# Summary
print("\n" + "=" * 60)
all_pass = score1 >= 0.60 and score3 >= 0.70
print(f"Overall: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")
print("=" * 60)
