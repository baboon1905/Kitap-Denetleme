#!/usr/bin/env python
"""Test the API endpoints with real files"""
import requests
import json

print("=" * 60)
print("Testing API Endpoints with Both PDFs")
print("=" * 60)

# Test PDF 1
print("\n📖 PDF 1 - test_kitap.pdf")
print("-" * 60)
with open('test_kitap.pdf', 'rb') as f:
    files = {'pdf': f}
    data = {'kitap_turu': 'Çocuk Kitabı'}
    resp = requests.post('http://localhost:5000/api/yukleme', files=files, data=data)
    print(f"✓ Upload Status: {resp.status_code}")
    if resp.status_code == 200:
        meta1 = resp.json()
        print(f"✓ File saved to: {meta1.get('dosya_yolu')}")
    else:
        print(f"✗ Upload failed: {resp.text}")

# Evaluate PDF 1
print("\nEvaluating PDF 1...")
eval_resp = requests.post('http://localhost:5000/api/degerlendir', 
                         json={'kitap_turu': 'Çocuk Kitabı', 'dosya_yolu': 'uploads/test_kitap.pdf'})
print(f"✓ Eval Status: {eval_resp.status_code}")
if eval_resp.status_code == 200:
    eval1 = eval_resp.json()
    maarif = eval1.get('maarif_modeli', {})
    print(f"📚 Maarif Uyum: {maarif.get('genel_uyum_yuzde')}%")
    print(f"🔍 Sakıncalı Kelimeler: {eval1.get('sakincali_kelimeler', {}).get('toplam_sayisi', 0)}")
else:
    print(f"✗ Eval failed: {eval_resp.text[:200]}")

# Test PDF 2
print("\n" + "=" * 60)
print("📖 PDF 2 - test_kitap2.pdf")
print("-" * 60)
with open('test_kitap2.pdf', 'rb') as f:
    files = {'pdf': f}
    data = {'kitap_turu': 'Çocuk Kitabı'}
    resp = requests.post('http://localhost:5000/api/yukleme', files=files, data=data)
    print(f"✓ Upload Status: {resp.status_code}")
    if resp.status_code == 200:
        meta2 = resp.json()
        print(f"✓ File saved to: {meta2.get('dosya_yolu')}")

# Evaluate PDF 2
print("\nEvaluating PDF 2...")
eval_resp = requests.post('http://localhost:5000/api/degerlendir', 
                         json={'kitap_turu': 'Çocuk Kitabı', 'dosya_yolu': 'uploads/test_kitap2.pdf'})
print(f"✓ Eval Status: {eval_resp.status_code}")
if eval_resp.status_code == 200:
    eval2 = eval_resp.json()
    maarif = eval2.get('maarif_modeli', {})
    print(f"📚 Maarif Uyum: {maarif.get('genel_uyum_yuzde')}%")
    print(f"🔍 Sakıncalı Kelimeler: {eval2.get('sakincali_kelimeler', {}).get('toplam_sayisi', 0)}")
else:
    print(f"✗ Eval failed: {eval_resp.text[:200]}")

# Comparison
print("\n" + "=" * 60)
print("📊 SONUÇLAR KARŞILAŞTIRMASI")
print("=" * 60)
if eval_resp.status_code == 200:
    score1 = eval1.get('maarif_modeli', {}).get('genel_uyum_yuzde')
    score2 = eval2.get('maarif_modeli', {}).get('genel_uyum_yuzde')
    print(f"PDF 1 Maarif Uyum: {score1}%")
    print(f"PDF 2 Maarif Uyum: {score2}%")
    if score1 != score2:
        print(f"\n✅ BAŞARILI! Sonuçlar FARKLIMI? EVET! 🎉")
        print(f"   Fark: {abs(score1 - score2)}%")
    else:
        print(f"\n❌ SORUN: Her iki PDF de aynı sonuç veriyor ({score1}%)")
