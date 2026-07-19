from evaluator_maarif import MaarifDegerlendiricisi
from pdf_processor import PDFProcessor

# PDF oku
print("1. Analyzing...")
pdf = PDFProcessor('uploads/03_cokbilmis_alingan.pdf')
metin = pdf.extract_text()
metin_normalized = metin.lower()

# Analiz yap
evaluator = MaarifDegerlendiricisi()
result = evaluator.analiz_yap(metin_normalized, 'maarif_meb', 'ilkokul')

# MEB bulgularını kontrol et
meb_bulgulari = result.get('meb_degerlendirmesi', {}).get('meb_bulgulari', {})

print("\n=== MEB BULGULARI ===")
for kriter, bulgular_list in meb_bulgulari.items():
    if bulgular_list:
        print(f"\n{kriter}: {len(bulgular_list)} findings")
        for i, bulgu in enumerate(bulgular_list[:2], 1):
            print(f"  {i}. sebebi={bulgu.get('sebebi', '')}")
            alininti_val = bulgu.get('alininti', '')
            if alininti_val:
                print(f"     alininti={alininti_val[:50]}")
            else:
                print(f"     alininti=EMPTY")
