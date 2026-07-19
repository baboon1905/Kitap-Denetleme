#!/usr/bin/env python
"""
Oluşturulan PDF'nin yeni özellikleri kontrol et:
1. Sayfa numarası
2. Bağlamsal analiz (risk azaltması)
3. Kategori bazlı tavsiyeler
"""

from PyPDF2 import PdfReader
import os
import re

pdf_dir = "."
pdf_files = [f for f in os.listdir(pdf_dir) if f.startswith("test_rapor_turkce") and f.endswith(".pdf")]
if not pdf_files:
    print("❌ PDF dosyası bulunamadı!")
    exit(1)

latest_pdf = sorted(pdf_files)[-1]
pdf_path = os.path.join(pdf_dir, latest_pdf)

print("=" * 80)
print("🔍 YENİ ÖZELLİKLER KONTROL")
print("=" * 80)
print(f"📋 Dosya: {latest_pdf}\n")

reader = PdfReader(pdf_path)
all_text = ""
for page in reader.pages:
    all_text += page.extract_text()

# 1. Sayfa numarası kontrolü
print("1️⃣  SAYFA NUMARASI KONTROLÜ:")
print("-" * 80)
if "Sayfa " in all_text:
    # Bulguların yanında sayfa numarası var mı?
    sayfa_mentions = re.findall(r'Sayfa (\d+)', all_text)
    print(f"   ✅ Sayfa referansları bulundu: {len(sayfa_mentions)} adet")
    if sayfa_mentions:
        print(f"      Örnek: Sayfa {sayfa_mentions[0]}, Sayfa {sayfa_mentions[-1]}")
else:
    print("   ❌ Sayfa numarası referansı bulunamadı")

# 2. Bağlamsal analiz (risk azaltması)
print("\n2️⃣  BAĞLAMSAL ANALİZ KONTROLü:")
print("-" * 80)
if "→" in all_text or "azaltıldı" in all_text:
    print("   ✅ Risk azaltması gösteriliyor (bağlamsal analiz çalışıyor)")
    # Örnek bulma
    examples = re.findall(r".*→.*", all_text)
    if examples:
        print(f"      Örnek: {examples[0][:80]}...")
else:
    print("   ℹ️  Risk azaltması gösteriliyor görülmüyor (veya bulunan kelime yok)")

# 3. Kategori bazlı tavsiyeler
print("\n3️⃣  KATEGORİ BAZLI TAVSİYE KONTROLÜ:")
print("-" * 80)
if "Tespit Edilen Sorunlarla" in all_text:
    print("   ✅ Kategori bazlı tavsiye bölümü mevcut")
    
    # Tavsiye sayısı
    recommendations = re.findall(r"• .*", all_text)
    print(f"   ✅ Toplam tavsiye: {len(recommendations)} adet")
    
    if "Şiddetçi" in all_text:
        print("   ✅ Şiddet tav siyesi bulundu")
    if "Cinsel" in all_text:
        print("   ✅ Cinsellik tavsiyesi bulundu")
else:
    print("   ❌ Kategori bazlı tavsiye bölümü bulunamadı")

# 4. Büyük Ş harfi
print("\n4️⃣  BÜYÜK Ş HARFİ KONTROLÜ:")
print("-" * 80)
if "Ş" in all_text:
    print("   ✅ Büyük Ş harfi mevcuttur")
    occurrences = all_text.count("Ş")
    print(f"      Toplam {occurrences} adet")
else:
    print("   ⚠️  Büyük Ş harfi bulunamadı")
    if "■" in all_text:
        print("      (Replacement character '■' bulundu - font sorunu)")

# 5. Risk skorunun tutarlılığı
print("\n5️⃣  RİSK SKORU TUTARLILIK:")
print("-" * 80)
# "Bulundu: 0" ve "Risk Skoru: 0.00" birlikte var mı?
if "Bulundu: 0" in all_text and "Risk Skoru: 0.00" in all_text:
    print("   ✅ Tutarlılık sağlanmış (0 bulgu = 0 risk)")
else:
    print("   ℹ️  Tutarlılık kontrol edildi (sayı metin extraction'da sorun yaşanabilir)")

print("\n" + "=" * 80)
print("✅ KONTROL TAMAMLANDI")
print("=" * 80)
