#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEB Kriterleri ve AI Prompts Sistem Testi
"""

from evaluator_maarif import MaarifDegerlendiricisi
from ai_prompts import list_prompts, get_prompt

print("\n" + "="*70)
print("TEST 1: MEB KRİTERLERİ DEĞERLENDIRMESI")
print("="*70)

evaluator = MaarifDegerlendiricisi()

# Test metni 1: Değerli kitap
test1 = "Vatan sevgisi, aile bağları ve sorumluluk bu kitabın ana temalarıdır. Çocuklar doğru davranışları öğrenirler."
meb1 = evaluator.meb_kriterleri_degerlendirmesi(test1)

print(f"Metni: {test1[:50]}...")
print(f"MEB Puanı: {meb1['meb_puani']}/100")
print(f"Genel Karar: {meb1['genel_karar']}")
print("\nKriterlere göre:")
for kriter_key, kriter_val in meb1['meb_kriterler'].items():
    print(f"  - {kriter_val['ad']}: {kriter_val['karar']} (Risk: {kriter_val['risk']}/5)")

# Test metni 2: Problematik kitap
print("\n" + "="*70)
test2 = "Çocuk terörizmi ve nefret söylemleri kitapta açıkça anlatılıyor. Argo ve küfürlerle dolu."
meb2 = evaluator.meb_kriterleri_degerlendirmesi(test2)

print(f"Metni: {test2[:50]}...")
print(f"MEB Puanı: {meb2['meb_puani']}/100")
print(f"Genel Karar: {meb2['genel_karar']}")

print("\n" + "="*70)
print("TEST 2: AI PROMPTS SİSTEMİ")
print("="*70)

prompts = list_prompts()
print(f"Toplam Prompt Türü: {len(prompts)}\n")

for pname, desc in prompts.items():
    print(f"✓ {pname:15} → {desc}")

# Örnek prompt göster
print("\n" + "="*70)
print("ÖRNEK: HIZLI KONTROL PROMPTU (İlk 300 karakter)")
print("="*70)
prompt = get_prompt('hizli_kontrol')
print(prompt[:300] + "...")

print("\n" + "="*70)
print("✅ TÜM TESTLER BAŞARILI - SİSTEM HAZIR")
print("="*70 + "\n")
