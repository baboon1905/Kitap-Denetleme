#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Generator Debug - Hangi Kod Çalışıyor?
"""

from report_generator import MEB_RAPORLAYICI_YÜKLÜ, DEFAULT_FONT, DEFAULT_FONT_BOLD
from evaluator_maarif import MaarifDegerlendiricisi

print("=" * 80)
print("REPORT GENERATOR DEBUG")
print("=" * 80)
print()

print("[1] Font Ayarları:")
print(f"    DEFAULT_FONT: {DEFAULT_FONT}")
print(f"    DEFAULT_FONT_BOLD: {DEFAULT_FONT_BOLD}")
print()

print("[2] MEB Raporlayıcı Durumu:")
print(f"    MEB_RAPORLAYICI_YÜKLÜ: {MEB_RAPORLAYICI_YÜKLÜ}")
print()

# Test metni
test_kitap = """
Kitap PKK'nın direniş mücadelesinden bahsediyor. Siz de katılabilirsiniz.
"""

print("[3] Evaluator Çalıştırılıyor...")
evaluator = MaarifDegerlendiricisi()
sonuc = evaluator.analiz_yap(test_kitap, profil="hibrit", yas_grubu="8-10")

meb_bulgulari = sonuc.get('meb_degerlendirmesi', {}).get('meb_bulgulari', {})
print(f"    MEB Bulguları: {meb_bulgulari}")

print()
print("=" * 80)
