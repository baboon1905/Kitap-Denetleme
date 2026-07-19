#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test: Anahtar_Acmaz.pdf analizi - Rapor ile karşılaştır
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
from evaluator_maarif import MaarifDegerlendiricisi

# PDF'i oku
pdf_path = "uploads/Anahtar_Acmaz.pdf"
try:
    processor = PDFProcessor(pdf_path)
    metin = processor.extract_text()
    print(f"✅ PDF okundu: {len(metin)} karakter\n")
except Exception as e:
    print(f"❌ PDF okunamadı: {e}")
    sys.exit(1)

# Analiz et
evaluator = MaarifDegerlendiricisi()  # Varsayılan (HIBRIT) profili kullanılır
sonuc = evaluator.analiz_yap(metin)

print("="*70)
print("SISTEM ÇIKTISI vs RAPOR KARŞILAŞTIRMASI")
print("="*70)

# Rapordaki bulgular
rapor_bulgulari = {
    "ayrımcılık_nefret": 0,
    "cinsellik_mahremiyet": 1,
    "dijital_risk": 0,
    "kaba_dil_hakaret": 12,
    "korku_travma": 0,
    "okültizm_batıl": 41,
    "olumsuz_davranış": 4,
    "reklam_ticari": 2,
    "siddet_suc": 47,
    "zararlı_alışkanlıklar": 11
}

print("\nKATEGORİ KARŞILAŞTIRMASI:")
print("-" * 70)
print(f"{'Kategori':<30} {'Sistem':<10} {'Rapor':<10} {'Durumu':<10}")
print("-" * 70)

for kategori, rapor_say in rapor_bulgulari.items():
    # Sistem çıktısından bul
    sistem_say = 0
    for k, v in sonuc["kategori_bulgulari"].items():
        if kategori.lower() in k.lower() or k.lower() in kategori.lower():
            sistem_say = v.get("toplam_bulgu", 0)
            break
    
    # Karşılaştır
    if sistem_say == rapor_say:
        status = "✅ MATCH"
    elif sistem_say > rapor_say:
        status = f"⚠️ +{sistem_say - rapor_say}"
    else:
        status = f"❌ -{rapor_say - sistem_say}"
    
    print(f"{kategori:<30} {sistem_say:<10} {rapor_say:<10} {status:<10}")

print("-" * 70)

# Risk skoru karşılaştır
sistem_skor = sonuc.get("final_skor", 0)
rapor_skor = 45.26
print(f"\nRİSK SKORU:")
print(f"  Sistem: {sistem_skor:.2f}/100")
print(f"  Rapor:  {rapor_skor:.2f}/100")
print(f"  Fark:   {abs(sistem_skor - rapor_skor):.2f} puan")

# Özet
print("\n" + "="*70)
toplam_sistem = sum(v["toplam_bulgu"] for v in sonuc["kategori_bulgulari"].values())
toplam_rapor = sum(rapor_bulgulari.values())
print(f"Toplam bulgu - Sistem: {toplam_sistem}, Rapor: {toplam_rapor}")
if toplam_sistem != toplam_rapor:
    print(f"⚠️ UYARI: {abs(toplam_sistem - toplam_rapor)} bulgu farklı!")
