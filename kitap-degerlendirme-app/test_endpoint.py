import requests
import json

# Test one endpoint to see if it works now
test_payload = {
    "kitap_id": "buyulu_yastiklar",
    "kitap_adi": "Büyülü Yastıklar",
    "book_type": "Korku/Gizem",
    "ana_karakterler": [{"ad": "Ali", "guven_skoru": 0.8, "ana_karakter_mi": True}],
    "ana_tema": "Test tema",
    "tema_analizi": [],
    "event_graph": []
}

try:
    response = requests.post(
        'http://127.0.0.1:5000/api/tema-kazanim/rapor',
        json=test_payload,
        params={'format': 'pdf'}
    )
    print(f"PDF Endpoint Status: {response.status_code}")
    if response.status_code != 200:
        try:
            print(f"Error: {response.json()}")
        except:
            print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Exception: {e}")
