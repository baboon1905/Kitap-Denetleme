#!/usr/bin/env python3
import json
import requests

dosya_path = 'uploads/03_cokbilmis_alingan.pdf'

# Analyze
r = requests.post('http://127.0.0.1:5000/api/degerlendir', 
                  json={'dosya_yolu': dosya_path, 'profil': 'maarif_meb'})

if r.status_code != 200:
    print(f"Error: {r.status_code}")
    exit(1)

data = r.json()
analiz_sonucu = data.get('analiz_sonucu', {})

print("=== KATEGORI BULGULARI (siddet_suc) ===")
siddet = analiz_sonucu['kategori_bulgulari']['siddet_suc']
print(f"Keys: {list(siddet.keys())}")
print(f"bulundu: {siddet['bulundu']}")
print(f"toplam_bulgu: {siddet['toplam_bulgu']}")
print(f"risk_puani: {siddet['risk_puani']}")

if siddet.get('bulunan_kelimeler'):
    print(f"\nİlk bulgu keys: {list(siddet['bulunan_kelimeler'][0].keys())}")

print("\n=== KATEGORI→MEB MAP ===")
from maarif_meb_risk_mapper import KATEGORI_TO_MEB_KRITER_YENI
print(f"siddet_suc → {KATEGORI_TO_MEB_KRITER_YENI.get('siddet_suc', 'NOT MAPPED')}")

print("\n=== BAĞLAMA HAZIR MI? ===")
print(f"siddet_suc bulundu: {siddet.get('bulundu')}")
print(f"siddet_suc bulunan_kelimeler: {type(siddet.get('bulunan_kelimeler'))} - length={len(siddet.get('bulunan_kelimeler', []))}")
