from evaluator_maarif import MaarifDegerlendiricisi
from pdf_processor import PDFProcessor

# PDF oku
pdf = PDFProcessor('uploads/03_cokbilmis_alingan.pdf')
metin = pdf.extract_text()
metin_normalized = metin.lower()

# Analiz yap
evaluator = MaarifDegerlendiricisi()
result = evaluator.analiz_yap(metin_normalized, 'maarif_meb', 'ilkokul')
bulgular = result.get('kategori_bulgulari', {})

# 'kan' bulgusu kontrol et
if 'siddet_suc' in bulgular:
    data = bulgular['siddet_suc']
    print(f"siddet_suc bulundu: {data.get('bulundu')}")
    if data.get('bulunan_kelimeler'):
        for bulgu in data['bulunan_kelimeler'][:2]:
            print(f"Bulgu: {bulgu.get('kelime')}")
            print(f"  Kontext: {repr(bulgu.get('kontext', '')[:50])}")
            print(f"  Sayfa: {bulgu.get('sayfa')}")
            print()
