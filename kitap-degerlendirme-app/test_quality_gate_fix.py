#!/usr/bin/env python
"""Test if quality gate fix works - check if PDF/Word endpoints no longer fail with pipeline markers."""
import requests
import json
import os

# Set flag for testing
os.environ['V7_SUMMARY_IR_SOURCE'] = 'true'

BASE_URL = "http://127.0.0.1:5000"

# Minimal test payload with required fields
test_payload = {
    "kitap_id": "test_book",
    "kitap_adi": "Test Kitabı",
    "book_type": "Masallar",
    "book_subtype": "Geleneksel Masal",
    "ana_tema": "Samanlık",
    "ana_karakterler": [
        {
            "ad": "Ali",
            "karakter_adi": "Ali",
            "ana_karakter_mi": True,
            "guven_skoru": 0.9,
            "entity_type": "PERSON",
            "mention_count": 10,
            "role": "Protagonisti",
            "relation_score": 0.95
        }
    ],
    "tema_analizi": [
        {
            "ad": "Samanlık",
            "guven_skoru": 0.85,
            "kanitlar": []
        }
    ],
    "event_graph": [
        {
            "index": 0,
            "actors": ["Ali"],
            "summary": "Başlangıç durumu",
            "olay_metni": "Ali samanlıkta uyuyor",
            "kaynak_metin": "Samanlıkta uyuyan Ali"
        }
    ],
    "ozet": "Ali'nin samanlıkta uyku sahnesi.",
    "summary": "Ali'nin samanlıkta uyku sahnesi.",
    "kitap_ozeti": "Ali'nin samanlıkta uyku sahnesi.",
    "canonical_summary": "Ali'nin samanlıkta uyku sahnesi.",
    "summary_ui": "Ali'nin samanlıkta uyku sahnesi.",
    "summary_pdf": "Ali'nin samanlıkta uyku sahnesi.",
}

print("\n" + "="*70)
print("Testing Quality Gate Fix - Pipeline Markers Sanitization")
print("="*70)

# Test 1: PDF Endpoint
print("\n[1/3] Testing PDF Endpoint...")
try:
    response = requests.post(
        f"{BASE_URL}/api/tema-kazanim/rapor",
        json=test_payload,
        params={"format": "pdf"},
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        try:
            error = response.json()
            print(f"Error: {error.get('hata', 'Unknown error')[:200]}")
        except:
            print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")

# Test 2: Word Endpoint
print("\n[2/3] Testing Word Endpoint...")
try:
    response = requests.post(
        f"{BASE_URL}/api/tema-kazanim/rapor",
        json=test_payload,
        params={"format": "word"},
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        try:
            error = response.json()
            print(f"Error: {error.get('hata', 'Unknown error')[:200]}")
        except:
            print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")

# Test 3: Teacher Endpoint
print("\n[3/3] Testing Teacher PDF Endpoint...")
try:
    response = requests.post(
        f"{BASE_URL}/api/theme-report/teacher-pdf",
        json=test_payload,
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        try:
            error = response.json()
            print(f"Error: {error.get('hata', 'Unknown error')[:200]}")
        except:
            print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "="*70)
print("Test Complete")
print("="*70 + "\n")
