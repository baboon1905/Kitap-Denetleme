#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Direct test of RaporOlusturucu - bypass Flask entirely
"""

from report_generator import RaporOlusturucu
import pdfplumber
import io

# Test data with MEB criteria having risks
analiz_sonucu = {
    "kitap_adi": "Test Kitap",
    "genel_degerlendirme": {
        "risk_skoru": 72,
        "karar": "Revizyon Gerekli"
    },
    "meb_degerlendirmesi": {
        "meb_kriterler": {
            "anayasa": {"risk": 0, "karar": "OK", "ad": "Anayasa"},
            "milli_guvenlik": {"risk": 1, "karar": "Uyarı", "ad": "Millî Güvenlik"},
            "esitlik": {"risk": 0, "karar": "OK", "ad": "Eşitlik"},
            "milli_manevi": {"risk": 3, "karar": "Revizyon Gerekli", "ad": "Millî Manevi Değerler"},
            "guvenlik": {"risk": 0, "karar": "OK", "ad": "Güvenlik"},
            "bilimsel": {"risk": 0, "karar": "OK", "ad": "Bilimsel"},
            "reklam": {"risk": 1, "karar": "Uyarı", "ad": "Reklam"},
            "dil": {"risk": 1, "karar": "Uyarı", "ad": "Dil"}
        },
        "meb_bulgulari": {}  # Empty, should trigger fallback
    }
}

print("="*60)
print("Direct RaporOlusturucu Test")
print("="*60)

# Create report
print("\n1. Creating RaporOlusturucu...")
rapor_gen = RaporOlusturucu()
print("   ✅ Created")

# Generate PDF
print("\n2. Generating PDF...")
pdf_buffer = rapor_gen.olustur(
    degerlen_sonuclari=analiz_sonucu,
    metadata={"kitap_adi": "Test Kitap"}
)
print(f"   ✅ Generated: {pdf_buffer.getbuffer().nbytes} bytes")

# Save for inspection
with open('test_direct_output.pdf', 'wb') as f:
    pdf_buffer.getvalue() # Reset to beginning
    f.write(pdf_buffer.getvalue())
print("   ✅ Saved to test_direct_output.pdf")

# Extract and check for 4.1
print("\n3. Checking for 4.1 section...")
pdf_buffer.seek(0)
try:
    with pdfplumber.open(pdf_buffer) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text() or ""
            full_text += text + "\n"
        
        if "4.1" in full_text and "Detayli" in full_text:
            print("   ✅ 4.1 BULUNDU!")
            lines = full_text.split('\n')
            for i, line in enumerate(lines):
                if '4.1' in line and 'Detayli' in line:
                    print(f"\n   Context:")
                    for j in range(max(0, i-1), min(len(lines), i+5)):
                        print(f"     {lines[j]}")
                    break
        else:
            print("   ❌ 4.1 BULUNAMADI")
            if "MEB TTK" in full_text:
                print("      But MEB TTK section found")
            print(f"\n   Text length: {len(full_text)} chars")
            
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
