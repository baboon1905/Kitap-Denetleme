"""
MEB TTK Kriterleri - DETAYLI BULGU TOPLAMA SİSTEMİ
Her kriter için riskli bölümlerin sayfa numarası, alıntısı ve düzeltme önerisi
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum


@dataclass
class RiskiBulgу:
    """Riskli bulgu tanımı"""
    sayfa: int  # Sayfa numarası (0 = bilinmiyor)
    alinți: str  # Riskli metinin alıntısı
    kategori: str  # Hangi kriter (milli_guvenlik, etc.)
    kriter_adi: str  # Kriterin tam adı
    risk_puani: int  # 1-5 arası risk
    sebebi: str  # Neden riskli (kısa açıklama)
    onerili_revizyon: str  # Nasıl düzeltilmeli
    bağlamsal_not: str = ""  # Başka bağlam varsa


class MEB_TTK_BulgularıToplayıcı:
    """MEB kriterlerine ait bulguları topla ve düzelt"""
    
    def __init__(self):
        self.kriterler = {
            "anayasa": "Anayasa ve Mevzuat Uygunluğu",
            "milli_guvenlik": "Millî Güvenlik",
            "esitlik": "Eşitlik ve Kapsayıcılık",
            "milli_manevi": "Millî ve Manevi Değerler",
            "guvenlik": "Güvenli ve Etik İçerik",
            "bilimsel": "Bilimsel Doğruluk",
            "reklam": "Reklam ve Ticari Unsurlar",
            "dil": "Dil ve Anlatım"
        }
    
    def taramalı_tarama(self, metin: str, sayfa_haritası: List[Tuple[int, int]] = None) -> Dict[str, List[RiskiBulgу]]:
        """
        Metni tüm 8 kritere göre tara ve riskli bölümleri topla
        
        sayfa_haritası: [(başlangıç_pozisyon, bitiş_pozisyon, sayfa_no), ...]
        """
        
        metin_lower = metin.lower()
        tüm_bulgular = {key: [] for key in self.kriterler.keys()}
        
        # 1. ANAYASA VE MEVZUAT
        ayrıştırıcı_ifadeler = [
            ("bölünme", "Devlet bölünüşü çağrısı"),
            ("sınırlar yeniden", "Sınır değiştirme çağrısı"),
            ("hukuka aykırı", "Hukuka aykırı eylem"),
            ("yasa dışı örgüt", "Yasaklı örgüt tanıması"),
        ]
        
        for ifade, sebebi in ayrıştırıcı_ifadeler:
            bulgular = self._bul_alıntılar(metin, ifade, sayfa_haritası)
            for bulgu_metni, sayfa in bulgular:
                tüm_bulgular["anayasa"].append(RiskiBulgу(
                    sayfa=sayfa,
                    alinți=bulgu_metni[:100],  # İlk 100 karakter
                    kategori="anayasa",
                    kriter_adi=self.kriterler["anayasa"],
                    risk_puani=4,
                    sebebi=sebebi,
                    onerili_revizyon=f"'{ifade}' ifadesini kaldırın veya bağlam ekleyin"
                ))
        
        # 2. MİLLÎ GÜVENLIK
        teror_ifadeleri = [
            ("pkk", "Terör örgütü anması"),
            ("dhkp-c", "Terör örgütü anması"),
            ("özendirme", "Eyleme özendirme"),
            ("siz de", "Katılım çağrısı"),
            ("ben de", "Özdeşleştirme/özendirme"),
        ]
        
        for ifade, sebebi in teror_ifadeleri:
            bulgular = self._bul_alıntılar(metin, ifade, sayfa_haritası)
            for bulgu_metni, sayfa in bulgular:
                risk = 5 if "özendirme" in sebebi.lower() else 4
                tüm_bulgular["milli_guvenlik"].append(RiskiBulgу(
                    sayfa=sayfa,
                    alinți=bulgu_metni[:100],
                    kategori="milli_guvenlik",
                    kriter_adi=self.kriterler["milli_guvenlik"],
                    risk_puani=risk,
                    sebebi=sebebi,
                    onerili_revizyon="KALDIRMALI - Bu içerik yayınlanmamalı"
                ))
        
        # 3. EŞİTLİK VE KAPSAYICILIK
        ayrımcılık_ifadeleri = [
            ("nefret söylemi", "Nefret söylemi"),
            ("irkcılık", "Irk ayrımcılığı"),
            ("cinsiyetçi", "Cinsiyet ayrımcılığı"),
            ("ötekileştirme", "Sosyal ötekileştirme"),
            ("aşağı ırk", "Irksal aşağılama"),
        ]
        
        for ifade, sebebi in ayrımcılık_ifadeleri:
            bulgular = self._bul_alıntılar(metin, ifade, sayfa_haritası)
            for bulgu_metni, sayfa in bulgular:
                tüm_bulgular["esitlik"].append(RiskiBulgу(
                    sayfa=sayfa,
                    alinți=bulgu_metni[:100],
                    kategori="esitlik",
                    kriter_adi=self.kriterler["esitlik"],
                    risk_puani=5 if "nefret" in sebebi.lower() else 3,
                    sebebi=sebebi,
                    onerili_revizyon="Dil değiştiriniz. Farklılıklara saygılı anlatım kullanız"
                ))
        
        # 4. MİLLÎ VE MANEVI DEĞERLER
        deger_ifadeleri = [
            ("hiç değer", "Değer eksikliği"),
            ("aile yoktur", "Aile değeri eksikliği"),
            ("vatan yok", "Vatan değeri eksikliği"),
        ]
        
        for ifade, sebebi in deger_ifadeleri:
            bulgular = self._bul_alıntılar(metin, ifade, sayfa_haritası)
            for bulgu_metni, sayfa in bulgular:
                tüm_bulgular["milli_manevi"].append(RiskiBulgу(
                    sayfa=sayfa,
                    alinți=bulgu_metni[:100],
                    kategori="milli_manevi",
                    kriter_adi=self.kriterler["milli_manevi"],
                    risk_puani=2,
                    sebebi=sebebi,
                    onerili_revizyon="Milli-manevi değerleri güçlendirmek için bağlam ekleyin"
                ))
        
        # 5. GÜVENLI VE ETİK İÇERİK
        şiddet_ifadeleri = [
            ("talimat savaş", "Şiddet talimatlandırması"),
            ("dene bak", "Eyleme özendirme"),
            ("böyle yaparsın", "Suç talimatı"),
            ("kanı akıyor", "Grafik şiddet"),
        ]
        
        for ifade, sebebi in şiddet_ifadeleri:
            bulgular = self._bul_alıntılar(metin, ifade, sayfa_haritası)
            for bulgu_metni, sayfa in bulgular:
                tüm_bulgular["guvenlik"].append(RiskiBulgу(
                    sayfa=sayfa,
                    alinći=bulgu_metni[:100],
                    kategori="guvenlik",
                    kriter_adi=self.kriterler["guvenlik"],
                    risk_puani=5 if "talimat" in sebebi.lower() else 3,
                    sebebi=sebebi,
                    onerili_revizyon="Şiddet detaylarını çıkarınız. Sonuç odaklı anlatım kullanız"
                ))
        
        # 6. BİLİMSEL DOĞRULUK
        bilimsel_ifadeleri = [
            ("yanlış", "Bilimsel hata"),
            ("hurafe", "Bilim dışı içerik"),
            ("çarpıtılmış", "Çarpıtılmış bilgi"),
        ]
        
        for ifade, sebebi in bilimsel_ifadeleri:
            bulgular = self._bul_alıntılar(metin, ifade, sayfa_haritası)
            for bulgu_metni, sayfa in bulgular:
                tüm_bulgular["bilimsel"].append(RiskiBulgу(
                    sayfa=sayfa,
                    alinți=bulgu_metni[:100],
                    kategori="bilimsel",
                    kriter_adi=self.kriterler["bilimsel"],
                    risk_puani=3,
                    sebebi=sebebi,
                    onerili_revizyon="Bilimsel kaynakla doğru bilgi ile değiştiriniz"
                ))
        
        # 7. REKLAM VE TİCARİ UNSURLAR
        reklam_ifadeleri = [
            ("marka", "Marka tanıtımı"),
            ("satın al", "Satın alma çağrısı"),
            ("qr kod", "Dış yönlendirme"),
        ]
        
        for ifade, sebebi in reklam_ifadeleri:
            bulgular = self._bul_alıntılar(metin, ifade, sayfa_haritası)
            for bulgu_metni, sayfa in bulgular:
                tüm_bulgular["reklam"].append(RiskiBulgу(
                    sayfa=sayfa,
                    alinți=bulgu_metni[:100],
                    kategori="reklam",
                    kriter_adi=self.kriterler["reklam"],
                    risk_puani=2,
                    sebebi=sebebi,
                    onerili_revizyon="Ticari unsurları çıkarınız veya MEB'e atıf yapınız"
                ))
        
        # 8. DİL VE ANLATIM
        dil_ifadeleri = [
            ("küfür", "Küfür sözcüğü"),
            ("argo", "Argo dil kullanımı"),
            ("hakaret", "Hakaret söylemi"),
        ]
        
        for ifade, sebebi in dil_ifadeleri:
            bulgular = self._bul_alıntılar(metin, ifade, sayfa_haritası)
            for bulgu_metni, sayfa in bulgular:
                tüm_bulgular["dil"].append(RiskiBulgу(
                    sayfa=sayfa,
                    alinți=bulgu_metni[:100],
                    kategori="dil",
                    kriter_adi=self.kriterler["dil"],
                    risk_puani=5 if "küfür" in sebebi.lower() else 2,
                    sebebi=sebebi,
                    onerili_revizyon="Sözcüğü resmi dile çevirin veya bağlam ekleyin"
                ))
        
        return tüm_bulgular
    
    def _bul_alıntılar(self, metin: str, arama_kelimesi: str, sayfa_haritası=None) -> List[Tuple[str, int]]:
        """
        Metinde arama kelimesini bul ve etrafındaki 50 karakteri alıntı olarak dön
        """
        sonuçlar = []
        metin_lower = metin.lower()
        arama_lower = arama_kelimesi.lower()
        
        başlangıç = 0
        while True:
            pos = metin_lower.find(arama_lower, başlangıç)
            if pos == -1:
                break
            
            # Etrafındaki 50 karakter al
            baş = max(0, pos - 40)
            son = min(len(metin), pos + 90)
            alıntı = "..." + metin[baş:son] + "..."
            
            # Sayfa numarasını bul
            sayfa = self._bul_sayfa(pos, sayfa_haritası)
            
            sonuçlar.append((alıntı, sayfa))
            başlangıç = pos + 1
        
        return sonuçlar
    
    def _bul_sayfa(self, pozisyon: int, sayfa_haritası=None) -> int:
        """Pozisyona göre sayfa numarasını bul"""
        if not sayfa_haritası:
            return 0  # Bilinmiyor
        
        for baş, son, sayfa in sayfa_haritası:
            if baş <= pozisyon <= son:
                return sayfa
        
        return 0
    
    def raporla(self, bulgular: Dict[str, List[RiskiBulgу]]):
        """Bulguları raporla"""
        
        print("\n" + "="*80)
        print("MEB TTK KRITERLERI - DETAYLI BULGU RAPORU")
        print("="*80)
        
        for kriter_key, bulgular_listesi in bulgular.items():
            if bulgular_listesi:
                print(f"\n[!] {self.kriterler[kriter_key].upper()}")
                print("-" * 80)
                
                for i, bulgu in enumerate(bulgular_listesi, 1):
                    print(f"\n  {i}. BULGU")
                    print(f"     Sayfa: {bulgu.sayfa if bulgu.sayfa > 0 else 'Bilinmiyor'}")
                    print(f"     Alıntı: {bulgu.alinți}")
                    print(f"     Risk: {bulgu.risk_puani}/5 ({bulgu.sebebi})")
                    print(f"     Önerilen Revizyon: {bulgu.onerili_revizyon}")
                    if bulgu.bağlamsal_not:
                        print(f"     Not: {bulgu.bağlamsal_not}")
        
        print("\n" + "="*80 + "\n")


# TEST
if __name__ == "__main__":
    toplayıcı = MEB_TTK_BulgularıToplayıcı()
    
    test_metni = """
    Kitap PKK'nın direniş mücadelesinden bahsediyor. Siz de katılabilirsiniz.
    Devlet hukuka aykırı. Kadınlar bilim yapamaz. Tarihî olarak yanlış bilgi.
    iPhone en iyi telefondur. Küfür söz kullanılıyor.
    """
    
    bulgular = toplayıcı.taramalı_tarama(test_metni)
    toplayıcı.raporla(bulgular)
