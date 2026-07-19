"""
Profesyonel Değerlendirici API Test
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_api():
    """API endpoint'lerini test et"""
    
    print("\n" + "="*60)
    print("PROFESYONEL DEĞERLENDİRİCİ API TEST")
    print("="*60)
    
    # Test 1: Profiller endpoint'i
    print("\n[TEST 1] Profilleri Listele")
    print("-" * 60)
    try:
        response = requests.get(f"{BASE_URL}/api/professional/profiller")
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    # Test 2: Tarihsel bağlam - Kelime değerlendirmesi
    print("\n[TEST 2] Tarihsel Bağlam - 'kan' kelimesi")
    print("-" * 60)
    try:
        payload = {
            "word": "kan",
            "context": "Kurtuluş Savaşı'nda çok kan dökülmüştür. Tarih dersinde bu önemli olay anlatılıyor.",
            "profile": "maarif"
        }
        response = requests.post(
            f"{BASE_URL}/api/professional/kelime-degerlendirme",
            json=payload
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Geçerli Bulgu: {result['degerlendirme']['is_valid_finding']}")
        print(f"Risk Skoru: {result['degerlendirme']['risk_score']}")
        print(f"Risk Seviyesi: {result['degerlendirme']['risk_level']}")
        print(f"Neden: {result['degerlendirme']['reason']}")
        print(f"\n4. Adım (Bağlam Tipi): {result['degerlendirme']['steps']['4_context_type']['type']}")
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    # Test 3: Substring - Kelime değerlendirmesi
    print("\n[TEST 3] Substring Test - 'lan' kelimesi")
    print("-" * 60)
    try:
        payload = {
            "word": "lan",
            "context": "Havalandırma sistemini kontrol edin.",
            "profile": "maarif"
        }
        response = requests.post(
            f"{BASE_URL}/api/professional/kelime-degerlendirme",
            json=payload
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Geçerli Bulgu: {result['degerlendirme']['is_valid_finding']}")
        print(f"Risk Skoru: {result['degerlendirme']['risk_score']}")
        print(f"Neden: {result['degerlendirme']['reason']}")
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    # Test 4: Doğrudan Risk - Kelime değerlendirmesi
    print("\n[TEST 4] Doğrudan Risk - 'sigara' kelimesi")
    print("-" * 60)
    try:
        payload = {
            "word": "sigara",
            "context": "Kahramanı sigara içerken görüyoruz.",
            "profile": "maarif"
        }
        response = requests.post(
            f"{BASE_URL}/api/professional/kelime-degerlendirme",
            json=payload
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Geçerli Bulgu: {result['degerlendirme']['is_valid_finding']}")
        print(f"Risk Skoru: {result['degerlendirme']['risk_score']}")
        print(f"Risk Seviyesi: {result['degerlendirme']['risk_level']}")
        print(f"Neden: {result['degerlendirme']['reason']}")
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    # Test 5: Metin Analizi
    print("\n[TEST 5] Tam Metin Analizi")
    print("-" * 60)
    try:
        metin = """
        Çocuk oyun oynamıyor. Oyunun eğitsel değeri hakkında öğreniyordu. 
        Tarih dersinde Osmanlı İmparatorluğu hakkında kan dökülmüştür bahsini okuyordu.
        Çocuk sigara içmek istedi ama annesi buna izin vermedi.
        Kahraman cesur ve dürüst bir çocuktu.
        """
        
        payload = {
            "metin": metin,
            "profile": "hybrid"
        }
        response = requests.post(
            f"{BASE_URL}/api/professional/metin-analiz",
            json=payload
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Toplam Bulgu: {result['ozet']['toplam_bulgu']}")
        print(f"Problem Bulgu: {result['ozet']['problem_bulgu']}")
        print(f"Problem Olmayan: {result['ozet']['problem_olmayan']}")
        print(f"Ortalama Risk: {result['ozet']['ortalama_risk']}")
        print(f"Problem Türleri: {result['ozet']['problem_türleri']}")
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    # Test 6: Health Check
    print("\n[TEST 6] Sistem Durumu")
    print("-" * 60)
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    print("\n" + "="*60)
    print("TEST TAMAMLANDI")
    print("="*60)

if __name__ == "__main__":
    # Sunucunun başlaması için bekle
    time.sleep(2)
    test_api()
