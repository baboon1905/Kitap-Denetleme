#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test: Türkçe kelimeler'in false positive analizi
eşek, ulan, lan, alay, argo, büyü, cadı, ölüm, rakı
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from evaluator_maarif import MaarifDegerlendiricisi

# Test metinleri - Her keyword'ün gerçek ve false positive context'leri
test_cases = [
    ("eşek", """
        Eşek çiftlikte çalışıyor. Eşek çok güçlü hayvandır.
        Peşek, beşekli, eşekçi gibi kelimeler var.
    """),
    ("ulan", """
        Ulan dedim! Bu nasıl olur? Ulan ne acı bir durumdur.
        Bulanuş, sulanan, kulançık gibi kelimeler vardır.
    """),
    ("lan", """
        Lan nedir? Bu çok kötü bir argo.
        Kaplan, Serkan, Ferlan, Marlan gibi isimler var.
    """),
    ("alay", """
        Alay etmek kötüdür. Alay yapan insan aptal.
        Alaylı, alayan, alalayarak gibi kelimeler vardır.
    """),
    ("argo", """
        Argo kelime kullanmak kötüdür. Argo konuşmak saygısızlıktır.
        Kargo, margo, margot gibi kelimeler var.
    """),
    ("büyü", """
        Büyü yapmak yasaktır. Büyü inanç sistemi vardır.
        Büyümek, büyüt, büyütür gibi kelimeler vardır.
    """),
    ("cadı", """
        Cadı hikâyelerinde kötülük vardır. Cadı inancı eski çağlardan kalma.
        Cadısı, cadının, cadıbir gibi kelimeler var.
    """),
    ("ölüm", """
        Ölüm kaçınılmazdır. Ölüm herkese gelir.
        Ölümü, ölümde, ölümcül gibi kelimeler vardır.
    """),
    ("rakı", """
        Rakı alkolik bir içkidir. Rakı tüketimi yasaklanmalı mıdır?
        Rakısı, rakının, rakılı gibi kelimeler var.
    """),
]

evaluator = MaarifDegerlendiricisi()

print("\n" + "="*70)
print("FALSE POSITIVE ANALIZI - Türkçe Kelimeler")
print("="*70)

for kelime, metin in test_cases:
    print(f"\n🔍 Keyword: '{kelime}'")
    print("-" * 70)
    
    sonuc = evaluator.analiz_yap(metin)
    
    # Bu kelimeyi içeren kategorileri bul
    bulunan = False
    for kategori_adi, kategori_bulgular in sonuc["kategori_bulgulari"].items():
        if kategori_bulgular["bulundu"]:
            for bulgu in kategori_bulgular['bulunan_kelimeler']:
                if bulgu['kelime'] == kelime:
                    bulunan = True
                    print(f"  ✓ Kategori: {kategori_adi}")
                    print(f"    Bulgu sayısı: {kategori_bulgular['toplam_bulgu']}")
                    print(f"    Risk: {bulgu['baglamsal_risk']}/5")
                    print(f"    Kontekst: {bulgu['kontext'][:80]}...")
    
    if not bulunan:
        print(f"  ✗ Bulunmadı")

print("\n" + "="*70)
