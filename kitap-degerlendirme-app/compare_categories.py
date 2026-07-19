#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdf_processor import PDFProcessor
from evaluator_maarif import MaarifDegerlendiricisi

processor = PDFProcessor('uploads/Anahtar_Acmaz.pdf')
metin = processor.extract_text()

evaluator = MaarifDegerlendiricisi()
sonuc = evaluator.analiz_yap(metin)

# Rapor kategorileri
rapor = {
    'ayrımcılık_nefret': 0,
    'cinsellik_mahremiyet': 1,
    'dijital_risk': 0,
    'kaba_dil_hakaret': 12,
    'korku_travma': 0,
    'okültizm_batıl': 41,
    'olumsuz_davranış': 4,
    'reklam_ticari': 2,
    'siddet_suc': 47,
    'zararlı_alışkanlıklar': 11
}

print('KATEGORI KARŞILAŞTIRMASI:')
print('{:<25} {:>5} {:>5} {:>5}'.format('Kategori', 'Rapor', 'Sistem', 'Fark'))
print('-' * 50)

for k in rapor:
    sistem_val = 0
    for k2, v2 in sonuc.get('kategori_bulgulari', {}).items():
        if k.lower() in k2.lower() or k2.lower() in k.lower():
            sistem_val = v2.get('toplam_bulgu', 0)
            break
    fark = rapor[k] - sistem_val
    marker = 'EKSIK' if fark > 0 else 'OK'
    print('{:<25} {:>5} {:>5} {:>5}  {}'.format(k, rapor[k], sistem_val, fark, marker))
