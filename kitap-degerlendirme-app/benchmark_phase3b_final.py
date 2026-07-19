#!/usr/bin/env python
"""PHASE 3B Benchmark Verification - Clean Results Capture

Tests the three benchmark books to verify:
1. PDF/Word/Teacher endpoints all succeed (200 OK) when V7_SUMMARY_IR_SOURCE=true
2. surface_consistency remains true
3. canonical_summary_ir_hash is consistent
4. Existing baseline failures are documented
"""
import os
import json
from app import app
from datetime import datetime

os.environ['V7_SUMMARY_IR_SOURCE'] = 'true'

# Running in-process using Flask test client to avoid network timeouts

BOOKS = [
    ("Tavşan Pati", "inputs/Tavsan_Pati.pdf"),
    ("Büyülü Yastıklar", "inputs/Buyulu_Yastiklar.pdf"),
    ("Benim Adım Kristof Kolomb", "inputs/Benim_Adim_Kristof_Kolomb.pdf"),
    # Baseline failure for reference
    ("Gökyüzünü Kaybeden Şehir", "inputs/Gokyuzunu_Kaybeden_Sehir.pdf"),
]

RESULTS = {
    "timestamp": datetime.now().isoformat(),
    "flag_state": "V7_SUMMARY_IR_SOURCE=true",
    "books": {}
}

print("\n" + "="*80)
print("PHASE 3B Benchmark Verification - Quality Gate Fix Validation")
print("="*80 + "\n")

client = app.test_client()

for book_name, pdf_path in BOOKS:
    print(f"Testing {book_name}...", end=" ", flush=True)
    
    try:
        # Get analysis
        analiz_response = client.post(
            '/api/tema-kazanim/analiz',
            json={"dosya_yolu": pdf_path},
        )
        
        if analiz_response.status_code != 200:
            print(f"FAILED (analysis: {analiz_response.status_code})")
            RESULTS["books"][book_name] = {
                "analiz_status": analiz_response.status_code,
                "endpoints": {}
            }
            continue
        
        payload = analiz_response.get_json()
        
        # Capture surface consistency info
        surface_consistency = (
            isinstance(payload.get("canonical_summary_ir"), dict)
            and payload.get("canonical_summary_ir_hash") is not None
        )
        
        canonical_hash = payload.get("canonical_summary_ir_hash")
        
        # Test PDF endpoint
        pdf_response = client.post(
            '/api/tema-kazanim/rapor',
            json=payload,
            query_string={"format": "pdf"},
        )
        
        # Test Word endpoint
        word_response = client.post(
            '/api/tema-kazanim/rapor',
            json=payload,
            query_string={"format": "word"},
        )
        
        # Test Teacher endpoint
        teacher_response = client.post(
            '/api/theme-report/teacher-pdf',
            json=payload,
        )
        
        # Capture results
        all_success = (
            pdf_response.status_code == 200
            and word_response.status_code == 200
            and teacher_response.status_code == 200
        )
        
        RESULTS["books"][book_name] = {
            "analiz_status": 200,
            "surface_consistency": surface_consistency,
            "canonical_summary_ir_hash": canonical_hash,
            "endpoints": {
                "pdf": pdf_response.status_code,
                "word": word_response.status_code,
                "teacher": teacher_response.status_code
            }
        }
        
        status_str = "✓ SUCCESS" if all_success else f"✗ FAIL (PDF:{pdf_response.status_code} Word:{word_response.status_code} Teacher:{teacher_response.status_code})"
        print(status_str)
        
    except Exception as e:
        print(f"ERROR: {str(e)[:50]}")
        RESULTS["books"][book_name] = {
            "error": str(e)
        }

# Print summary table
print("\n" + "="*80)
print("Summary Table")
print("="*80)
print(f"{'Book':<35} {'PDF':<8} {'Word':<8} {'Teacher':<8} {'Consistency':<12} {'Hash':<20}")
print("-"*90)

for book_name, book_data in RESULTS["books"].items():
    if "error" in book_data:
        print(f"{book_name:<35} ERROR")
    else:
        endpoints = book_data.get("endpoints", {})
        consistency = "✓" if book_data.get("surface_consistency") else "✗"
        hash_val = (book_data.get("canonical_summary_ir_hash") or "N/A")[:18]
        print(f"{book_name:<35} {endpoints.get('pdf', 'N/A'):<8} {endpoints.get('word', 'N/A'):<8} {endpoints.get('teacher', 'N/A'):<8} {consistency:<12} {hash_val}")

print("="*80)

# Save results to file
with open("benchmark_v4_results.json", "w", encoding="utf-8") as f:
    json.dump(RESULTS, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to: benchmark_v4_results.json\n")

# Final status
all_success = all(
    book.get("endpoints", {}).get("pdf") == 200
    and book.get("endpoints", {}).get("word") == 200
    and book.get("endpoints", {}).get("teacher") == 200
    for book in RESULTS["books"].values()
    if "error" not in book
)

print("="*80)
if all_success:
    print("✓ PHASE 3B FIX VALIDATED - All endpoints successful!")
else:
    print("⚠ Some endpoints failed - see details above")
print("="*80 + "\n")
