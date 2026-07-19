#!/usr/bin/env python
"""
PDF içindeki Büyük Ş harfi problemini ve örnek kelimeleri analiz et
"""

from PyPDF2 import PdfReader

pdf_path = "test_rapor_turkce_20260606_003121.pdf"

print("=" * 80)
print("🔍 PDF BÜYÜK Ş HARFİ VE KELIME ANALİZİ")
print("=" * 80)

reader = PdfReader(pdf_path)

# Tüm sayfaları ve Büyük Ş kullanımını kontrol et
print("\n📌 PDF Sayfaları ve Büyük Ş Harfi Kontrolü:")
print("-" * 80)

all_text = ""
for page_num, page in enumerate(reader.pages, 1):
    text = page.extract_text()
    all_text += text
    
    # Büyük Ş ara
    if "Ş" in text:
        print(f"   Sayfa {page_num}: ✅ Büyük Ş HARFİ BULUNDU")
    else:
        print(f"   Sayfa {page_num}: ℹ️  Büyük Ş harfi yok")
    
    # Karakterleri göster (sample)
    if page_num == 1:
        print(f"      İlk 100 char: {text[:100]}")

print("\n📌 Tüm Metinde Büyük Ş Arama:")
print("-" * 80)
if "Ş" in all_text:
    print("   ✅ Büyük Ş HARFİ MEVCUTTUR")
    # İlk 5 örneğini bulma
    import re
    matches = re.finditer(r".{0,20}Ş.{0,20}", all_text)
    for i, match in enumerate(list(matches)[:3], 1):
        print(f"      Örnek {i}: ...{match.group()}...")
else:
    print("   ❌ Büyük Ş HARFİ BULUNAMADI")

# Örnek sakıncalı kelimeler ve cümleleri göster
print("\n📌 Tespit Edilen Kelimeler (Örnek):")
print("-" * 80)

test_words = ["ölüm", "şiddet", "cinayet", "ölürse"]
for word in test_words:
    if word in all_text.lower():
        # Cümle içindeki örneğini bul
        import re
        pattern = rf".{0,40}{re.escape(word)}.{0,40}"
        matches = re.finditer(pattern, all_text, re.IGNORECASE)
        for match in list(matches)[:1]:
            print(f"   '{word}' örneği: ...{match.group().strip()}...")

print("\n" + "=" * 80)
print("✅ ANALIZ TAMAMLANDI")
print("=" * 80)
