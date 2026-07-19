#!/usr/bin/env python
"""
Hızlı test - "buraya lan" kontrol et
"""
from evaluator_maarif import MaarifDegerlendiricisi

evaluator = MaarifDegerlendiricisi()

test = "Buraya lan! Oraya lan yazacak mısın? Ne yapıyorsun sen?"
print("=" * 60)
print(f"📝 Test: {test}")
print("=" * 60)

result = evaluator.analiz_yap(test)

print(f"\n📊 Final Skor: {result['final_skor']}/100")
print(f"📌 Toplam Bulgular:")

for kategori, data in result['kategori_bulgulari'].items():
    if data['toplam_bulgu'] > 0:
        print(f"\n   {kategori}:")
        print(f"      Bulgu Sayısı: {data['toplam_bulgu']}")
        print(f"      Ort. Risk: {data['ortalama_risk']:.1f}/5")
        
        for bulgu in data['bulunan_kelimeler']:
            print(f"      - {bulgu['kelime']}: {bulgu['baglamsal_risk']}/5")

print("\n" + "=" * 60)
