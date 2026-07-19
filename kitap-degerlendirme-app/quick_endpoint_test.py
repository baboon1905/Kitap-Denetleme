#!/usr/bin/env python
"""Quick test of endpoint status codes after quality gate fix."""
import requests
import json
from datetime import datetime

# Books to test
BOOKS = [
    {
        "name": "Tavşan Pati",
        "id": "tavsan_pati",
        "endpoint": "http://127.0.0.1:5000/api/tema-kazanim/analiz"
    },
    {
        "name": "Büyülü Yastıklar",
        "id": "buyulu_yastiklar",
        "endpoint": "http://127.0.0.1:5000/api/tema-kazanim/analiz"
    },
]

print(f"\n[{datetime.now().isoformat()}] Testing endpoints with V7_SUMMARY_IR_SOURCE=true/false\n")

for book in BOOKS:
    print(f"Testing {book['name']}...")
    
    # Get the analysis result
    try:
        response = requests.get(
            f"{book['endpoint']}?book_id={book['id']}&cache=false",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Try PDF endpoint
            pdf_response = requests.post(
                "http://127.0.0.1:5000/api/tema-kazanim/rapor",
                json=data,
                params={"format": "pdf"},
                timeout=30
            )
            print(f"  PDF: {pdf_response.status_code}")
            
            # Try Word endpoint  
            word_response = requests.post(
                "http://127.0.0.1:5000/api/tema-kazanim/rapor",
                json=data,
                params={"format": "word"},
                timeout=30
            )
            print(f"  Word: {word_response.status_code}")
            
            # Try Teacher endpoint
            teacher_response = requests.post(
                "http://127.0.0.1:5000/api/theme-report/teacher-pdf",
                json=data,
                timeout=30
            )
            print(f"  Teacher: {teacher_response.status_code}")
        else:
            print(f"  Analiz failed: {response.status_code}")
    except Exception as e:
        print(f"  ERROR: {e}")

print(f"\nDone at {datetime.now().isoformat()}")
