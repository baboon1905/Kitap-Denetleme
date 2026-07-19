#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FINAL END-TO-END TEST
Evaluator -> MEB Bulgularıyonu -> Report -> PDF
"""

from evaluator_maarif import MaarifDegerlendiricisi
from report_generator import RaporOlusturucu

# Test metni (riskli içerik)
test_kitap = """
Kitap PKK'nın direniş mücadelesinden bahsediyor. Siz de katılabilirsiniz.
Kadınlar bilim yapamaz. iPhone en iyi telefondur.
Devleti bölme çağrıları var. Teror örgütü DHKP-C hakkında yazı var.
Kufur kelimesi kullanılmıştır. Hakaret söylenmiştir.
"""

print("=" * 80)
print("END-TO-END TEST: EVALUATOR -> BULGULAR -> REPORT -> PDF")
print("=" * 80)
print()

# 1. EVALUATOR
print("[1] MEB Değerlendirmesi Yapılıyor...")
evaluator = MaarifDegerlendiricisi()
sonuc = evaluator.analiz_yap(test_kitap, profil="hibrit", yas_grubu="8-10")

meb_eval = sonuc.get('meb_degerlendirmesi', {})
print(f"    ✅ MEB Puanı: {meb_eval.get('meb_puani', '?')}/100")

# 2. BULGULAR
meb_bulgulari = meb_eval.get('meb_bulgulari', {})
if meb_bulgulari:
    print(f"    ✅ MEB Bulguları: {len([b for bulgu_list in meb_bulgulari.values() for b in bulgu_list if bulgu_list])} bulgu")
    for kriter, bulgular in meb_bulgulari.items():
        if bulgular:
            print(f"       - {kriter}: {len(bulgular)}")
else:
    print(f"    ⚠️  MEB Bulguları: Yok")

print()

# 3. REPORT GENERATOR
print("[2] PDF Raporu Oluşturuluyor...")
try:
    raporcu = RaporOlusturucu()
    
    # Metadata
    metadata = {
        'kitap_adi': "Test Kitabı - MEB Bulguları",
        'yazar': "Test Yazarı",
        'yayinevi': "Test Yayınevi",
        'tarama_tarihi': "2025-01-09"
    }
    
    # PDF oluştur
    pdf_buffer = raporcu.olustur(sonuc, metadata)
    
    # BytesIO ise getvalue() kullan
    if hasattr(pdf_buffer, 'getvalue'):
        pdf_bytes = pdf_buffer.getvalue()
    else:
        pdf_bytes = pdf_buffer
        
    print(f"    ✅ PDF Oluşturuldu: {len(pdf_bytes)} bytes")
    
    # Dosyaya kaydet
    with open("FINAL_TEST_MEB_BULGULARI.pdf", "wb") as f:
        f.write(pdf_bytes)
    print(f"    📄 Dosya: FINAL_TEST_MEB_BULGULARI.pdf")
    
except Exception as e:
    print(f"    ❌ Hata: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("✅ TEST TAMAMLANDI!")
print()
print("Beklenen Sonuç:")
print("- PDF dosyası oluşturuldu ✓")
print("- MEB TTK Kriterleri bölümü içeriyor ✓")
print("- Detaylı Bulgu Analizi gösteriyor ✓")
print("  * Milli Guvenlik: PKK, DHKP-C, Siz de katılabilir")
print("  * Dil: Kufur, Hakaret")
print()
print("PDF dosyasını açıp \"4. MEB TTK Kriterleri Analizi\" bölümünü kontrol edin.")
print("\"4.1 Detayli Bulgu Analizi\" altında bulgular listelenmiş olmalıdır.")
print("=" * 80)
