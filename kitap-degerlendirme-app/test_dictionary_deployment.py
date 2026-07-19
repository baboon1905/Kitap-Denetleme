#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yeni Kapsamlı Sözlük Dağıtım Testi
3384+ Kelime, 10 Kategori, 5 Profil Sistem
"""

import sys
import json
import requests
from evaluator_maarif import MaarifDegerlendiricisi

def test_config_loading():
    """Konfigürasyonu yükle ve doğrula"""
    print("\n" + "="*60)
    print("TEST 1: Konfigürasyon Yükleme")
    print("="*60)
    try:
        from config import SAKINCALI_KELIMELER, ANALIZ_PROFILLERI, RISK_PUANLAMA
        
        kategoriler = list(SAKINCALI_KELIMELER.keys())
        toplam_kelime = sum(len(k['kelimeler']) for k in SAKINCALI_KELIMELER.values())
        
        print(f"✅ Config yüklendi")
        print(f"📊 Kategoriler ({len(kategoriler)}): {', '.join(kategoriler)}")
        print(f"📝 Toplam kelime sayısı: {toplam_kelime}")
        print(f"⚙️  Profil sayısı: {len(ANALIZ_PROFILLERI)}")
        print(f"🎯 Risk seviyeleri: {len(RISK_PUANLAMA)}")
        return True
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def test_evaluator_initialization():
    """Değerlendiriciyi başlat"""
    print("\n" + "="*60)
    print("TEST 2: Değerlendirici Başlatma")
    print("="*60)
    try:
        evaluator = MaarifDegerlendiricisi()
        print(f"✅ Değerlendirici başlatıldı")
        print(f"📌 Model: {evaluator.model}")
        print(f"🔧 Demo Modu: {evaluator.demo_mode}")
        return evaluator
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None

def test_clean_text(evaluator):
    """Temiz metni test et"""
    print("\n" + "="*60)
    print("TEST 3: Temiz Metin Analizi")
    print("="*60)
    clean_text = "Küçük bir kız güneşli bir günde parkta oyun oynadı ve arkadaşlarıyla eğlendi."
    
    try:
        result = evaluator.analiz_yap(clean_text, "hibrit", "9-12")
        print(f"📖 Metin: {clean_text}")
        print(f"📊 Final Skor: {result['final_skor']}/100")
        print(f"✅ Karar: {result['karar']['seviye']}")
        
        if result['final_skor'] <= 20:
            print("✅ TEST GEÇTI: Temiz metin doğru şekilde değerlendirildi")
            return True
        else:
            print("❌ TEST BAŞARISIZ: Beklenenden yüksek skor")
            return False
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def test_problematic_content(evaluator):
    """Sakıncalı içeriği test et"""
    print("\n" + "="*60)
    print("TEST 4: Sakıncalı İçerik Analizi")
    print("="*60)
    
    tests = [
        ("Zararlı Alışkanlıklar", "Ahmet sigara içiyor ve alkol tüketiyor."),
        ("Şiddet", "Çocuğu bıçakla yaraladılar ve dehşet içinde kaldı."),
        ("Kaba Dil", "Senin aptal ve salak olduğunu herkes biliyor."),
        ("Ayrımcılık", "Ötekiler bizim gibi değil, onlar aşağı ırk.")
    ]
    
    results = []
    for category, text in tests:
        try:
            result = evaluator.analiz_yap(text, "maarif_meb", "9-12")
            score = result['final_skor']
            decision = result['karar']['seviye']
            
            print(f"\n📌 {category}")
            print(f"   Metin: {text[:50]}...")
            print(f"   Skor: {score}/100 - {decision}")
            
            if score > 40:
                print(f"   ✅ Tespit başarılı (skor yüksek)")
                results.append(True)
            else:
                print(f"   ⚠️  Skor düşük, tespitte problem olabilir")
                results.append(False)
        except Exception as e:
            print(f"   ❌ Hata: {e}")
            results.append(False)
    
    return all(results)

def test_profile_comparison(evaluator):
    """Profil karşılaştırması yap"""
    print("\n" + "="*60)
    print("TEST 5: Profil Karşılaştırması")
    print("="*60)
    
    test_text = "Genç bir kız uygunsuz davranışlara başladı."
    profiles = ["maarif_meb", "hibrit", "editoryal", "hassas_veli", "kuruma_ozel"]
    
    try:
        print(f"📖 Test metni: {test_text}")
        print(f"📊 Profillere göre puanlar:\n")
        
        scores = {}
        for profile in profiles:
            result = evaluator.analiz_yap(test_text, profile, "12-15")
            score = result['final_skor']
            scores[profile] = score
            print(f"   {profile:15} → {score:6.1f}/100")
        
        # Profililer farklı puanlar verirse test başarılı
        if len(set(scores.values())) > 1:
            print(f"\n✅ TEST GEÇTI: Profiller farklı puanlar veriyor")
            return True
        else:
            print(f"\n⚠️  TEST UYARISI: Tüm profiller aynı puanı veriyor")
            return False
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def test_api_endpoint():
    """API endpoint test et"""
    print("\n" + "="*60)
    print("TEST 6: API Endpoint Test")
    print("="*60)
    
    try:
        # Profiller endpoint
        response = requests.get("http://127.0.0.1:5000/api/profiller", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ /api/profiller → 200 OK")
            print(f"   Profil sayısı: {len(data)}")
        else:
            print(f"❌ /api/profiller → {response.status_code}")
            return False
        
        # Health check
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ /health → 200 OK")
        else:
            print(f"❌ /health → {response.status_code}")
            return False
        
        print(f"\n✅ API ulaşılabilir ve yanıt veriyor")
        return True
    except requests.exceptions.ConnectionError:
        print(f"⚠️  API ulaşılamıyor (sunucu başlamış mı?)")
        print(f"   http://127.0.0.1:5000 kontrol edin")
        return False
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║  MAARİF MODELİ YAYIN DENETİM SİSTEMİ - TEST PAKETI      ║")
    print("║  3384+ Kelime, 10 Kategori, 5 Profil Sistemi            ║")
    print("╚" + "="*58 + "╝")
    
    results = {}
    
    # Test 1: Config
    results['config'] = test_config_loading()
    
    # Test 2: Evaluator
    evaluator = test_evaluator_initialization()
    results['evaluator_init'] = evaluator is not None
    
    if evaluator:
        # Test 3: Clean text
        results['clean_text'] = test_clean_text(evaluator)
        
        # Test 4: Problematic content
        results['problematic'] = test_problematic_content(evaluator)
        
        # Test 5: Profile comparison
        results['profiles'] = test_profile_comparison(evaluator)
    
    # Test 6: API
    results['api'] = test_api_endpoint()
    
    # Summary
    print("\n" + "="*60)
    print("TEST ÖZETI")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ GEÇTI" if result else "❌ BAŞARISIZ"
        print(f"{test_name:20} {status}")
    
    print("\n" + "="*60)
    print(f"SONUÇ: {passed}/{total} test geçti")
    print("="*60 + "\n")
    
    if passed == total:
        print("🎉 TÜM TESTLER BAŞARILI - SİSTEM HAZIR!")
        return 0
    else:
        print(f"⚠️  {total - passed} test başarısız")
        return 1

if __name__ == "__main__":
    sys.exit(main())
