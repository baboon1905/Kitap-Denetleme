#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
report_generator.py'nin MEB Raporlayıcı Yüklemesini Test Et
"""

import sys

print("=" * 80)
print("REPORT_GENERATOR MEB RAPORLAYICI IMPORT TEST")
print("=" * 80)
print()

print("[1] Importing report_generator...")
try:
    from report_generator import RaporOlusturucu, MEB_RAPORLAYICI_YÜKLÜ
    print(f"    ✅ Başarılı")
    print(f"    MEB_RAPORLAYICI_YÜKLÜ = {MEB_RAPORLAYICI_YÜKLÜ}")
except ImportError as e:
    print(f"    ❌ Hata: {e}")

print()
print("[2] MEBBulgularıRaporlayıcı Doğrudan İmport Test:")
try:
    from meb_basit_raporlayici import MEBBulgularıRaporlayıcı
    print(f"    ✅ Başarılı")
    print(f"    Sınıf: {MEBBulgularıRaporlayıcı}")
except ImportError as e:
    print(f"    ❌ Hata: {e}")

print()
print("=" * 80)
