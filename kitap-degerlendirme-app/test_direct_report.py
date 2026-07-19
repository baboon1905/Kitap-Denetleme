#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Direct Test: Report Truncation Fix with Real Evaluator"""

import sys
import io
from pdf_processor import PDFProcessor
from evaluator_maarif import MaarifDegerlendiricisi
from report_generator import RaporOlusturucu

print("=" * 70)
print("DIRECT TEST: Report Truncation Fix")
print("=" * 70)

# Test PDF kullan
pdf_path = "uploads/alisin_ofkesi_5.basim.pdf"

try:
    processor = PDFProcessor(pdf_path)
    metin = processor.extract_text()
    metadata = processor.extract_metadata()
    print(f"\n✅ PDF processed: {len(metin)} chars, {processor.sayfa_sayisi} pages")
    
    # Analyze
    evaluator = MaarifDegerlendiricisi()
    sonuclar = evaluator.analiz_yap(metin, profil="hibrit", yas_grubu="10-15")
    
    print(f"\n📊 Analiz Results:")
    print(f"   Risk: {sonuclar.get('risk_skoru')}/100")
    
    # Debug: Show actual keys in sonuclar
    print(f"\n   Sonuclar Keys: {list(sonuclar.keys())}")
    
    # Check kategori_bulgulari
    kategori_bulgulari = sonuclar.get('kategori_bulgulari', {})
    print(f"   kategori_bulgulari type: {type(kategori_bulgulari)}")
    if kategori_bulgulari:
        print(f"   kategori_bulgulari keys: {list(kategori_bulgulari.keys())}")
    else:
        print(f"   kategori_bulgulari is EMPTY")
    
    total_findings = 0
    for cat, details in kategori_bulgulari.items():
        if isinstance(details, dict):
            count = details.get('bulgu_sayisi', len(details.get('bulgu_listesi', [])))
            if count > 0:
                print(f"   {cat}: {count} findings")
                total_findings += count
                
                # Show actual findings (to verify truncation fix)
                if 'bulgu_listesi' in details:
                    print(f"      Showing ALL findings (truncation fix):")
                    for i, finding in enumerate(details['bulgu_listesi'], 1):
                        if isinstance(finding, dict):
                            word = finding.get('kelime', finding)
                        else:
                            word = finding
                        print(f"      {i}. {word}")
    
    print(f"\n   TOTAL: {total_findings} findings")
    
    if total_findings > 0:
        print(f"\n✅ Findings present - report generation:")
        
        # Generate report
        raportci = RaporOlusturucu()
        try:
            pdf_bytes = raportci.olustur(sonuclar, metadata)
            
            # Save report
            report_file = "test_direct_report.pdf"
            with open(report_file, 'wb') as f:
                f.write(pdf_bytes)
            
            print(f"✅ Report generated: {report_file} ({len(pdf_bytes)} bytes)")
            print(f"\n🎯 CHECK PDF: All findings should be visible (no \"... ve X daha\")")
        except Exception as e:
            print(f"❌ Report error: {e}")
    else:
        print(f"ℹ️  No findings in this PDF")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
