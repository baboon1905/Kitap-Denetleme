#!/usr/bin/env python3
"""
Tutarlilik testi.

Yeni kural: Kelime tek basina risk olusturmaz. Risk 0 bulgular raporda
gorunebilir, ancak skor, uyari veya revizyon onerisi uretmemelidir.
Davranis metinde fiilen sahneleniyorsa en az dusuk risk uretir.
"""

from evaluator_maarif import MaarifDegerlendiricisi


test_metin_temiz = """Fatih cok merakli bir ogrenciydi. Her gun okulda yeni seyler ogrenmeyi cok severdi.
Ogretmeni ona her zaman dogru yolda yurumesini tavsiye ederdi.
Fatih da kardeslerine yardim etmeyi cok severdi.
Vatan sevgisi onun en guclu duygusu idi."""

test_metin_risk_0 = """Çocuk şiddet filmlerini izlemekten bıkmıştı. Ölüm sahneleri onu çok rahatsız ediyor.
Silahlarla dolu bir dünyadaydı artık. Terör haberleri her gün onun korkusunu artırıyordu."""

test_metin_davranis = """Fosur fosur sigara içerdi. Adam komşusunu dövdü.
Kavga etmek çok eğlenceliydi."""


def bulgu_toplam(sonuc):
    return sum(b["toplam_bulgu"] for b in sonuc["kategori_bulgulari"].values())


def riskli_bulgu_toplam(sonuc):
    toplam = 0
    for kategori in sonuc["kategori_bulgulari"].values():
        for bulgu in kategori.get("bulunan_kelimeler", []):
            risk = bulgu.get("riskPuani", bulgu.get("baglamsal_risk", 0)) or 0
            if float(risk) > 0:
                toplam += 1
    return toplam


print("=" * 70)
print("TUTARLILIK TESTI")
print("=" * 70)

evaluator = MaarifDegerlendiricisi()

print("\nTEST 1: Temiz metin")
print("-" * 70)
sonuc1 = evaluator.analiz_yap(test_metin_temiz, profil="hibrit", yas_grubu="10-15")
toplam1 = bulgu_toplam(sonuc1)
print(f"Final Skor: {sonuc1['final_skor']}/100")
print(f"Toplam Bulgu: {toplam1} (0 olmali)")
assert sonuc1["final_skor"] == 0.0 and toplam1 == 0
print("TUTARLI: Skor=0 ve Bulgu=0")

print("\nTEST 2: Kelime var ama risk 0")
print("-" * 70)
sonuc2 = evaluator.analiz_yap(test_metin_risk_0, profil="hibrit", yas_grubu="10-15")
toplam2 = bulgu_toplam(sonuc2)
riskli2 = riskli_bulgu_toplam(sonuc2)
print(f"Final Skor: {sonuc2['final_skor']}/100")
print(f"Toplam Bulgu: {toplam2} (>0 olabilir)")
print(f"Riskli Bulgu: {riskli2} (0 olmali)")
assert sonuc2["final_skor"] == 0.0 and toplam2 > 0 and riskli2 == 0
print("TUTARLI: Risk 0 bulgu gorunur, skor uretmez")

print("\nTEST 3: Davranis sahnelenmesi")
print("-" * 70)
sonuc3 = evaluator.analiz_yap(test_metin_davranis, profil="hibrit", yas_grubu="10-15")
toplam3 = bulgu_toplam(sonuc3)
riskli3 = riskli_bulgu_toplam(sonuc3)
print(f"Final Skor: {sonuc3['final_skor']}/100")
print(f"Toplam Bulgu: {toplam3} (>0 olmali)")
print(f"Riskli Bulgu: {riskli3} (>0 olmali)")
assert sonuc3["final_skor"] > 0 and toplam3 > 0 and riskli3 > 0
print("TUTARLI: Sahnelenen davranis dusuk/riskli karar uretir")

print("\n" + "=" * 70)
print("TEST TAMAMLANDI")
print("=" * 70)
