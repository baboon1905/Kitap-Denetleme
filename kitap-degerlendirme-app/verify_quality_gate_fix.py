#!/usr/bin/env python
"""Verification test for PHASE 3B quality gate fix.

Tests that PDF/Word/Teacher endpoints work when V7_SUMMARY_IR_SOURCE=true
and pipeline markers are being sanitized.
"""
import sys
sys.path.insert(0, '.')

from app import app
import json
import io

# Create test context
client = app.test_client()

# Simple test payload with canonical_summary_ir structure
test_payload = {
    "kitap_id": "test_fixture",
    "kitap_adi": "Test Fixture Book",
    "yazar": "Test Author",
    "book_type": "Öykü",
    "book_subtype": "Kısa Öykü",
    "ana_tema": "Umut ve İçsel Güç",
    "ana_karakterler": [
        {
            "ad": "Ali",
            "karakter_adi": "Ali",
            "entity_type": "PERSON",
            "rolu": "ana",
            "ana_karakter_mi": True,
            "guven_skoru": 0.95,
            "mention_count": 25,
            "centrality_score": 0.92,
            "merkezi_varlik_mi": True
        }
    ],
    "tema_analizi": [
        {
            "ad": "Umut ve İçsel Güç",
            "guven_skoru": 0.88,
            "kanitlar": [
                {
                    "metin": "Ali dayanıklı bir karakterdir",
                    "alinti": "Ali her zorluğa karşı mücadele eder"
                }
            ]
        }
    ],
    "event_graph": [
        {
            "index": 0,
            "actors": ["Ali"],
            "olay_metni": "Başlangıç: Ali normal hayatını yaşıyor",
            "kaynak_metin": "Ali sabah uyanıyor",
            "summary": "Ali uyanıyor",
            "importance": 0.7,
            "conflict": False
        },
        {
            "index": 1,
            "actors": ["Ali"],
            "olay_metni": "Gelişme: Ali bir sorunla karşılaşıyor",
            "kaynak_metin": "Bir sorun ortaya çıkıyor",
            "summary": "Sorun ortaya çıkıyor",
            "importance": 0.85,
            "conflict": True
        },
        {
            "index": 2,
            "actors": ["Ali"],
            "olay_metni": "Çözüm: Ali sorunu çözerek güçleniyor",
            "kaynak_metin": "Ali sorunu çözer",
            "summary": "Ali çözüm bulur",
            "importance": 0.9,
            "conflict": False
        }
    ],
    "ozet": "Ali zorluklar karşısında güçlü bir karakter olarak çıkıyor. Umudunu hiç kaybetmez ve sonunda başarıya ulaşır.",
    "summary": "Ali zorluklar karşısında güçlü bir karakter olarak çıkıyor. Umudunu hiç kaybetmez ve sonunda başarıya ulaşır.",
    "kitap_ozeti": "Ali zorluklar karşısında güçlü bir karakter olarak çıkıyor. Umudunu hiç kaybetmez ve sonunda başarıya ulaşır.",
    "canonical_summary": "Ali zorluklar karşısında güçlü bir karakter olarak çıkıyor. Umudunu hiç kaybetmez ve sonunda başarıya ulaşır.",
    "summary_ui": "Ali zorluklar karşısında güçlü bir karakter olarak çıkıyor. Umudunu hiç kaybetmez ve sonunda başarıya ulaşır.",
    "summary_pdf": "Ali zorluklar karşısında güçlü bir karakter olarak çıkıyor. Umudunu hiç kaybetmez ve sonunda başarıya ulaşır.",
    "ana_tema_kanitlari": [
        {
            "metin": "Ali dayanıklı bir karakterdir",
            "alinti": "Ali her zorluğa karşı mücadele eder"
        }
    ]
}

print("\n" + "="*70)
print("PHASE 3B Quality Gate Fix - Verification Test")
print("="*70 + "\n")

# Test PDF endpoint
print("[1/3] Testing PDF Report Endpoint...")
response = client.post(
    '/api/tema-kazanim/rapor',
    json=test_payload,
    query_string={'format': 'pdf'}
)
pdf_status = response.status_code
print(f"      Status: {pdf_status}")
if pdf_status != 200:
    try:
        data = json.loads(response.data)
        error_msg = data.get('hata', 'Unknown error')[:150]
        print(f"      Error: {error_msg}")
    except:
        print(f"      Response: {response.data[:200]}")

# Test Word endpoint
print("\n[2/3] Testing Word Report Endpoint...")
response = client.post(
    '/api/tema-kazanim/rapor',
    json=test_payload,
    query_string={'format': 'word'}
)
word_status = response.status_code
print(f"      Status: {word_status}")
if word_status != 200:
    try:
        data = json.loads(response.data)
        error_msg = data.get('hata', 'Unknown error')[:150]
        print(f"      Error: {error_msg}")
    except:
        print(f"      Response: {response.data[:200]}")

# Test Teacher PDF endpoint
print("\n[3/3] Testing Teacher PDF Endpoint...")
response = client.post(
    '/api/theme-report/teacher-pdf',
    json=test_payload
)
teacher_status = response.status_code
print(f"      Status: {teacher_status}")
if teacher_status != 200:
    try:
        data = json.loads(response.data)
        error_msg = data.get('hata', 'Unknown error')[:150]
        print(f"      Error: {error_msg}")
    except:
        print(f"      Response: {response.data[:200]}")

# Summary
print("\n" + "="*70)
print("Test Results Summary")
print("="*70)
print(f"PDF Endpoint:        {pdf_status} {'✓ PASS' if pdf_status == 200 else '✗ FAIL'}")
print(f"Word Endpoint:       {word_status} {'✓ PASS' if word_status == 200 else '✗ FAIL'}")
print(f"Teacher Endpoint:    {teacher_status} {'✓ PASS' if teacher_status == 200 else '✗ FAIL'}")
print("="*70 + "\n")

sys.exit(0 if pdf_status == 200 and word_status == 200 and teacher_status == 200 else 1)
