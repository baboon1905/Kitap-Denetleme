#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test: VUR FALSE POSITIVE filter (fixed) + GÖKKUŞAĞΙ keyword detection"""

import sys
sys.path.insert(0, '.')

from pdf_processor import PDFProcessor
from evaluator_maarif import MaarifDegerlendiricisi

print("=" * 70)
print("TEST: Vur FALSE POSITIVE Filter + Gökkuşağı Detection")
print("=" * 70)

# Test with the actual book
pdf_path = "uploads/alisin_ofkesi_5.basim.pdf"

try:
    processor = PDFProcessor(pdf_path)
    metin = processor.extract_text()
    
    # Check: Vur ve Gökkuşağı metin'de var mı?
    print(f"\n📄 Metin (ilk 500 char): {metin[:500]}")
    
    vur_count = metin.lower().count("vur")
    gokkusagi_count = metin.lower().count("gökkuşağ")
    
    print(f"\n✅ 'vur' occurrences in PDF: {vur_count}")
    print(f"✅ 'gökkuşağ' occurrences in PDF: {gokkusagi_count}")
    
    if gokkusagi_count > 0:
        # Find line
        idx = metin.lower().find("gökkuşağ")
        context = metin[max(0, idx-50):idx+100]
        print(f"   Context: ...{context}...")
    
    # Analyze
    print("\n" + "=" * 70)
    print("ANALYZING WITH FIXED evaluator_maarif.py...")
    print("=" * 70)
    
    evaluator = MaarifDegerlendiricisi()
    sonuclar = evaluator.analiz_yap(metin, profil="hibrit", yas_grubu="10-15")
    
    print(f"\n📊 Analiz Sonuçları:")
    print(f"   Risk Score: {sonuclar.get('risk_skoru')}/100")
    
    # Check kategoriler
    kategori_bulgulari = sonuclar.get('kategori_bulgulari', {})
    print(f"   kategori_bulgulari keys: {list(kategori_bulgulari.keys())}")
    
    vur_bulundu = False
    gokkusagi_bulundu = False
    
    for cat, details in kategori_bulgulari.items():
        if isinstance(details, dict):
            print(f"\n   {cat}:")
            print(f"      bulundu: {details.get('bulundu', '?')}")
            print(f"      toplam_bulgu: {details.get('toplam_bulgu', '?')}")
            
            # Try different possible keys for findings list
            bulgu_listesi = None
            if 'bulgu_listesi' in details:
                bulgu_listesi = details['bulgu_listesi']
            elif 'bulunan_kelimeler' in details:
                bulgu_listesi = details['bulunan_kelimeler']
            elif 'findings' in details:
                bulgu_listesi = details['findings']
            
            if bulgu_listesi:
                print(f"      findings found: {len(bulgu_listesi)}")
                for i, bulgu in enumerate(bulgu_listesi, 1):
                    if isinstance(bulgu, dict):
                        kelime = bulgu.get('kelime', '?')
                    else:
                        kelime = bulgu
                    
                    if kelime == "vur":
                        vur_bulundu = True
                        print(f"         {i}. ❌ '{kelime}' - SHOULD BE FILTERED!")
                    elif "gökkuşağ" in str(kelime).lower():
                        gokkusagi_bulundu = True
                        print(f"         {i}. ✅ '{kelime}' - FOUND!")
                    else:
                        risk = "?" 
                        if isinstance(bulgu, dict):
                            risk = bulgu.get('baglamsal_risk', '?')
                        print(f"         {i}. '{kelime}' (Risk: {risk}/5)")
    
    print("\n" + "=" * 70)
    print("VERIFICATION:")
    print("=" * 70)
    
    if vur_count > 0:
        if not vur_bulundu:
            print("✅ 'vur' FALSE POSITIVE FILTER WORKS - Not flagged as risk")
        else:
            print("❌ 'vur' FILTER FAILED - Still flagged as risk")
    else:
        print("ℹ️  'vur' not in PDF")
    
    if gokkusagi_count > 0:
        if gokkusagi_bulundu:
            print("✅ 'gökkuşağı' DETECTED - Found as risk")
        else:
            print("❌ 'gökkuşağı' NOT DETECTED - Should be found")
    else:
        print("ℹ️  'gökkuşağı' not in PDF")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
