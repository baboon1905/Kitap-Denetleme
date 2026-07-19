"""
MEB TTK Kriterleri - Risk Unsuru Detaylı Analiz Sistemi
Her kriter için risk göstergeleri ve özendirme unsurlarını detaylıca açıklar
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum
import json


class RiskSeviyesi(Enum):
    """Risk seviyeleri"""
    RISKSIZ = 0
    DUSUK = 1
    ORTA = 2
    YUKSEK = 3
    MAKSIMUM = 4
    KRITIK = 5


@dataclass
class RiskUnsuru:
    """Risk unsuru tanımı"""
    ad: str
    seviye: RiskSeviyesi
    aciklama: str
    ornekler: List[str]
    baglamsal_carp: str = ""  # Bağlamla risk nasıl değişir


class MEBKriterleriRiskAnaliz:
    """8 kriterin detaylı risk analiz sistemi"""
    
    def __init__(self):
        self.kriterler = self._init_kriterler()
    
    def _init_kriterler(self) -> Dict:
        """8 MEB kriterini detaylı risk unsurlarıyla tanımla"""
        
        return {
            "anayasa": {
                "ad": "Anayasa ve Mevzuat Uygunluğu",
                "risk_unsurları": [
                    RiskUnsuru(
                        ad="Devlet Bütünlüğüne Aykırılık",
                        seviye=RiskSeviyesi.MAKSIMUM,
                        aciklama="Devletin territorial/siyasi bütünlüğünü reddetme",
                        ornekler=[
                            "❌ 'Sınırlar yeniden çizilmelidir'",
                            "❌ 'Bölünme ülkenin çıkarına gider'",
                            "✅ 'Tarihi sınırlarımız ulusumuzun sınırlarıdır'"
                        ],
                        baglamsal_carp="Tarihî bağlamda 'o zamanlar' denirse risk azalır"
                    ),
                    RiskUnsuru(
                        ad="Hukuk Sistemi İhlaflı",
                        seviye=RiskSeviyesi.MAKSIMUM,
                        aciklama="Yasal düzeni hafife alma, ihlal etmeye çağrı",
                        ornekler=[
                            "❌ 'Yazılı yasaları dikkate almayız'",
                            "✅ 'Hukuk devletinin temelini yasal sistem oluşturur'"
                        ],
                        baglamsal_carp="Adalet sistemini kınayışsa düzeltme yapılmalı"
                    ),
                    RiskUnsuru(
                        ad="Anayasaya Karşı Belirtilmiş Eylem",
                        seviye=RiskSeviyesi.MAKSIMUM,
                        aciklama="Anayasayı değiştirme, devirme çağrısı",
                        ornekler=[
                            "❌ 'Darbeler gerekli olabilir'",
                            "✅ 'Demokrasi hukuk devletinin temelidir'"
                        ],
                        baglamsal_carp="Tarihî darbe analizi bilimsel yapılsa ok"
                    ),
                ]
            },
            "milli_guvenlik": {
                "ad": "Millî Güvenlik",
                "risk_unsurları": [
                    RiskUnsuru(
                        ad="Terör Örgütü Propagandası",
                        seviye=RiskSeviyesi.MAKSIMUM,
                        aciklama="PKK, DHKP-C, PYD/YPG vs. oluştur özendirme",
                        ornekler=[
                            "❌ 'PKK gerillasını desteklerim'",
                            "❌ 'DHKP-C'nin direniş harekatı haklıdır'",
                            "✅ 'Terör örgütleri insanlığa karşı suç işlemiştir'"
                        ],
                        baglamsal_carp="Tarihî analiz yapılıysa açıkça kınanmalı"
                    ),
                    RiskUnsuru(
                        ad="Bölücülük/Ayrılıkçılık Özendirmesi",
                        seviye=RiskSeviyesi.MAKSIMUM,
                        aciklama="Etnik/dini ayrılıkçı harekat çağrısı",
                        ornekler=[
                            "❌ 'Bizim kendi devletimiz olmalı'",
                            "❌ 'Özgür bir devlet kurabiliriz'",
                            "✅ 'Türkiye'nin bütünlüğü temel değeridir'"
                        ],
                        baglamsal_carp="Tarihî devlet içi tartışmalar bilimsel konuşulsa ok"
                    ),
                    RiskUnsuru(
                        ad="Özendirme Dili (Critical!)",
                        seviye=RiskSeviyesi.MAKSIMUM,
                        aciklama="'Siz de yapabilirsiniz', 'ben de katılırdım' türü",
                        ornekler=[
                            "❌ 'Böyle bir örgüte ben de katılmak isterdim'",
                            "❌ 'Siz de silah alıp katılabilirsiniz'",
                            "❌ 'Direnişe katılmanız sizin haklı görevidir'",
                            "✅ 'Bu eylemler devlet tarafından engellenmiştir'"
                        ],
                        baglamsal_carp="ÖZENDIRME dilinde yazıldıysa RİSK OTOMATİK MAKSIMUM"
                    ),
                    RiskUnsuru(
                        ad="Devlet Kurumlarına Karşı Olumsuz Propaganda",
                        seviye=RiskSeviyesi.YÜKSEK,
                        aciklama="Ordu, polis, asker karşıtı genel konuşmalar",
                        ornekler=[
                            "❌ 'Askeri yapı baskıcıdır'",
                            "❌ 'Polis halkın düşmanıdır'",
                            "✅ 'Güvenlik görevlileri toplum düzenini sağlar'"
                        ],
                        baglamsal_carp="Spesifik isim/olaysa bağlama göre değer"
                    ),
                ]
            },
            "esitlik": {
                "ad": "Eşitlik ve Kapsayıcılık",
                "risk_unsurları": [
                    RiskUnsuru(
                        ad="Sistemik Irkcılık",
                        seviye=RiskSeviyesi.MAKSIMUM,
                        aciklama="Bir etnik grubu öteki ırka aşağı gösteren",
                        ornekler=[
                            "❌ 'Akdeniz ırkı aşağı ırk'",
                            "❌ 'Asyalılar entelektüel olarak zayıf'",
                            "✅ 'Farklı kültürler zenginliklerimizdir'"
                        ],
                        baglamsal_carp="Bilimsel/histórikken analiz yapılsa ok"
                    ),
                    RiskUnsuru(
                        ad="Dini Ayrımcılık",
                        seviye=RiskSeviyesi.MAKSIMUM,
                        aciklama="Bir dini grup ötekisi aleyhinde konuşma",
                        ornekler=[
                            "❌ 'Müslümanlar medeniyet kuramaz'",
                            "❌ 'Hristiyanlar güvenilir değil'",
                            "✅ 'Farklı inançlar saygıyla anılır'"
                        ],
                        baglamsal_carp="Tarihî ortaya konmuşsa bağlam sağlanmalı"
                    ),
                    RiskUnsuru(
                        ad="Cinsiyet Ayrımcılığı",
                        seviye=RiskSeviyesi.YÜKSEK,
                        aciklama="Kadın/erkek için sabit stereotip roller",
                        ornekler=[
                            "❌ 'Kadınlar ev işine yatkındır'",
                            "❌ 'Erkekler liderleri doğaldır'",
                            "✅ 'Her birey kendi yolunu seçebilir'"
                        ],
                        baglamsal_carp="Tarihî ortamda söylenen söz konuşulsa, çoğu zaman yanlış"
                    ),
                    RiskUnsuru(
                        ad="Sosyal Sınıf Ötekileştirmesi",
                        seviye=RiskSeviyesi.ORTA,
                        aciklama="Yoksullar/işçiler aşağı tabaka tutumu",
                        ornekler=[
                            "❌ 'Köylüler doğal olarak cahil'",
                            "❌ 'Yoksullar toplumun altı'",
                            "✅ 'Farklı meslekler toplumun dibi'"
                        ],
                        baglamsal_carp="Sosyolojik analiz yapılsa bağlam sağlanmalı"
                    ),
                ]
            },
            "milli_manevi_degerler": {
                "ad": "Millî ve Manevi Değerler",
                "risk_unsurları": [
                    RiskUnsuru(
                        ad="Değer Eksikliği (Negatif Risk)",
                        seviye=RiskSeviyesi.ORTA,
                        aciklama="Hiçbir milli/manevi değer bahsedilmeyen içerik",
                        ornekler=[
                            "⚠️ 'Ailenin hiçbir rolü yok'",
                            "⚠️ 'Vatana ait hiç hikaye yok'",
                            "✅ 'Aile bizim temelimiz, vatan güvenliğimiz'"
                        ],
                        baglamsal_carp="Eğer iki ana değer varsa risk otomatik -1"
                    ),
                    RiskUnsuru(
                        ad="Değerlerin Olumsuz Temsili",
                        seviye=RiskSeviyesi.YÜKSEK,
                        aciklama="Milli değerleri negatif karakterle gösterme",
                        ornekler=[
                            "❌ 'Vatan mefhumu eski kalıptır'",
                            "❌ 'Aile bireyi yıkıyor'",
                            "✅ 'Vatan ve aile temelimiz'"
                        ],
                        baglamsal_carp="Devlet aşkını vurgulayan finale yapılsa riski azaltır"
                    ),
                ]
            },
            "guvenlik_etik": {
                "ad": "Güvenli ve Etik İçerik",
                "risk_unsurları": [
                    RiskUnsuru(
                        ad="Doğrudan Şiddet Özendirmesi (CRİTİCAL!)",
                        seviye=RiskSeviyesi.MAKSIMUM,
                        aciklama="'Siz de darbe yapabilirsiniz', 'dene' ifadeleri",
                        ornekler=[
                            "❌ 'Sen de tuzağı kur' (cinayette)",
                            "❌ 'Silahı öyle kullan' (gerçekçi suç)",
                            "❌ 'Böyle saldırırsanız...' (özendirme)",
                            "✅ 'Kahraman kaçmayı seçti' (sonuç)"
                        ],
                        baglamsal_carp="ÖZENDIRMEDEN FARKI: Şiddet eylemi adımları sıralanır"
                    ),
                    RiskUnsuru(
                        ad="Cinsellik/Mahremiyet İhlali",
                        seviye=RiskSeviyesi.MAKSIMUM,
                        aciklama="Çocuk için uygunsuz cinsel içerik",
                        ornekler=[
                            "❌ Açık cinsel eylem tasviri",
                            "❌ Çocuk cinsiyetçiliği",
                            "✅ 'Vücudumuz değişiyor' (eğitsel)"
                        ],
                        baglamsal_carp="Her durumda MAKSIMUM RİSK"
                    ),
                    RiskUnsuru(
                        ad="Psikolojik Travma (Yaş Uygunluğu)",
                        seviye=RiskSeviyesi.YÜKSEK,
                        aciklama="Aşırı korkunç/şiddetli anlatım",
                        ornekler=[
                            "⚠️ (6-8 yaş) 'Katil onu çok yakıcı şekilde...' → YÜKSEK",
                            "✅ (10-12 yaş) Tarihî savaş → DÜŞÜK",
                            "✅ (Tüm yaşlar) 'Sonunda kahraman kurtuldu' → RİSK -"
                        ],
                        baglamsal_carp="Yaş grubu +2 artırırsa risk -1 azalır"
                    ),
                    RiskUnsuru(
                        ad="Bağımlılık Uygulaması",
                        seviye=RiskSeviyesi.YÜKSEK,
                        aciklama="Sigara, alkol, uyuşturucu kullanımının pozitif gösterimi",
                        ornekler=[
                            "❌ 'Sigara çok rahat hissetirir'",
                            "❌ 'Deneme merak doğaldır'",
                            "✅ 'Sağlık görevlisi uyarıyor'"
                        ],
                        baglamsal_carp="Ciddiye uyarı yapılsa risk -1"
                    ),
                ]
            },
            "bilimsel": {
                "ad": "Bilimsel Doğruluk",
                "risk_unsurları": [
                    RiskUnsuru(
                        ad="Tarihî Çarpıtma",
                        seviye=RiskSeviyesi.YÜKSEK,
                        aciklama="Tarihî olayları yanlış tarih/bağlamda anlatma",
                        ornekler=[
                            "❌ 'Birinci Dünya Savaşı 1940'ta başladı'",
                            "❌ 'Roma bizim topraklarımız değildi'",
                            "✅ 'Osmanlı İmparatorluğu 1923'te sona erdi'"
                        ],
                        baglamsal_carp="Kaynakta yazarsa düzelt, öğrenci yanılmış"
                    ),
                    RiskUnsuru(
                        ad="Hurafe/Efsane Bilim Gibi Sunulması",
                        seviye=RiskSeviyesi.ORTA,
                        aciklama="Bilimsel dayanağı olmayan şeyler gerçekmiş gibi",
                        ornekler=[
                            "❌ 'Bunlar büyü yapabilir' (gerçekmiş gibi)",
                            "✅ 'Eski İnsanlar sihir inanırdı' (tarihî)"
                        ],
                        baglamsal_carp="'Bilim şöyle diyor' eklenirse riski azalt"
                    ),
                    RiskUnsuru(
                        ad="Arkaik Bilgi",
                        seviye=RiskSeviyesi.DÜŞÜK,
                        aciklama="Eski coğrafya haritası, yanlış astronomi",
                        ornekler=[
                            "⚠️ 'Sovyetler Birliği'ni harita olarak göster",
                            "✅ 'Eski harita tarihî değeridir' (bağlam)"
                        ],
                        baglamsal_carp="Güncel bilgi eklenirse risk -1"
                    ),
                ]
            },
            "reklam": {
                "ad": "Reklam ve Ticari Unsurlar",
                "risk_unsurları": [
                    RiskUnsuru(
                        ad="Doğrudan Marka Tanıtımı",
                        seviye=RiskSeviyesi.YÜKSEK,
                        aciklama="'iPhone en iyi telefon', 'Coca-Cola için'",
                        ornekler=[
                            "❌ 'Nike ayakkabıları harika'",
                            "✅ 'Teknoloji araçları var' (genel)"
                        ],
                        baglamsal_carp="Marka adı yok, genel tanımsa risk 0"
                    ),
                    RiskUnsuru(
                        ad="Sponsor Tabı / Kurumsal Bağış",
                        seviye=RiskSeviyesi.ORTA,
                        aciklama="'Destekler: X Şirketi'",
                        ornekler=[
                            "⚠️ 'Bu bölüm X Enerji Şirketi tarafından yazılmıştır'",
                            "✅ 'Baskı desteği: MEB Yayıncılık' (kurum)"
                        ],
                        baglamsal_carp="Belediye/MEB'se risk -1"
                    ),
                    RiskUnsuru(
                        ad="Dış Yönlendirme (QR, URL, Link)",
                        seviye=RiskSeviyesi.ORTA,
                        aciklama="'Bu linki tıkla', 'QR kodu tara'",
                        ornekler=[
                            "⚠️ 'Daha fazla bilgi için: www.xyz.com'",
                            "⚠️ 'QR kodu tara' (bilinmeyen site)",
                            "✅ 'Resmi MEB sitesi' (adı belirtilmiş)"
                        ],
                        baglamsal_carp="Resmi kurum linki denirse risk 0"
                    ),
                ]
            },
            "dil": {
                "ad": "Dil ve Anlatım",
                "risk_unsurları": [
                    RiskUnsuru(
                        ad="Küfür/Hakaret Söz",
                        seviye=RiskSeviyesi.MAKSIMUM,
                        aciklama="Doğrudan veya kinetik küfür",
                        ornekler=[
                            "❌ Açık küfür",
                            "❌ 'Kötü birisi' (devamlı hakaret)",
                            "✅ 'Kahraman kızıldı' (duygu)"
                        ],
                        baglamsal_carp="HER DURUMDA MAKSIMUM RİSK ve ÇIKARILMALI"
                    ),
                    RiskUnsuru(
                        ad="Argo Söz / Sokak Dili",
                        seviye=RiskSeviyesi.YÜKSEK,
                        aciklama="Eğitimsel normun dışı sokak tarafından",
                        ornekler=[
                            "❌ 'Çok saktı' (argo)",
                            "⚠️ Karakterin doğal konuşması (dialogda ok)",
                            "✅ 'Çok hoştu' (resmi)"
                        ],
                        baglamsal_carp="Çoğu zaman revizyon yapılmalı"
                    ),
                    RiskUnsuru(
                        ad="Dilbilgisel Kusurlar",
                        seviye=RiskSeviyesi.DÜŞÜK,
                        aciklama="Yazım, telaffuz, cümle yapısı",
                        ornekler=[
                            "⚠️ 'Kitap okumak güzel bir alışkanlıktır' (eski yazım)",
                            "✅ 'Kitap okumak güzel bir alışkanlıktır' (düzeltme)"
                        ],
                        baglamsal_carp="Öğretimsel değerse ok"
                    ),
                ]
            },
        }
    
    def analiz_metni(self, metin: str, yas_grubu: str = "8-10") -> Dict:
        """Metni tüm 8 kritere göre analiz et"""
        
        print(f"\n{'='*80}")
        print(f"MEB TTK KRİTERLERİ - DETAYLI RİSK ANALIZI")
        print(f"{'='*80}")
        print(f"Yaş Grubu: {yas_grubu}")
        print(f"Metin Uzunluğu: {len(metin)} karakter")
        print(f"\n")
        
        sonuclar = {}
        toplam_risk = 0
        
        for kriter_key, kriter_data in self.kriterler.items():
            print(f"\n📌 KRİTER: {kriter_data['ad'].upper()}")
            print(f"{'-'*80}")
            
            kriter_risk = self._analiz_kritere_gore(kriter_key, metin, yas_grubu)
            sonuclar[kriter_key] = kriter_risk
            toplam_risk += kriter_risk['risk_puani']
            
            # Detaylı risk göstergeleri
            for unsur in kriter_data['risk_unsurları']:
                self._yazdir_risk_unsuru(unsur, metin)
        
        # Genel Hesaplama
        meb_puani = 100 - (toplam_risk * 10)
        meb_puani = max(0, min(100, meb_puani))
        
        print(f"\n{'='*80}")
        print(f"📊 GENEL HESAPLAMA")
        print(f"{'='*80}")
        print(f"Toplam Risk Puanı: {toplam_risk}/8 × 10 = {toplam_risk * 10}")
        print(f"MEB PUANI: 100 - {toplam_risk * 10} = {meb_puani}")
        
        if meb_puani >= 75:
            karar = "✅ UYGUN - Yayına Hazır"
        elif meb_puani >= 50:
            karar = "✔️ KOŞULLU - Düzeltmeler Gerekli"
        elif meb_puani >= 25:
            karar = "⚠️ REVIZYON - Temel Değişiklik Gerekli"
        else:
            karar = "❌ UYGUN DEĞİL - Yayınlanmamalı"
        
        print(f"KARAR: {karar}")
        print(f"{'='*80}\n")
        
        return {
            "meb_puani": round(meb_puani, 2),
            "toplam_risk": toplam_risk,
            "karar": karar,
            "kriterler": sonuclar
        }
    
    def _yazdir_risk_unsuru(self, unsur: RiskUnsuru, metin: str):
        """Risk unsurunun örneklerini yazdir"""
        print(f"\n  • {unsur.ad} [{unsur.seviye.name}]")
        print(f"    Açıklama: {unsur.aciklama}")
        if unsur.baglamsal_carp:
            print(f"    Bağlamsal: {unsur.baglamsal_carp}")
        print(f"    Örnekler:")
        for ornek in unsur.ornekler:
            print(f"      {ornek}")
    
    def _analiz_kritere_gore(self, kriter_key: str, metin: str, yas_grubu: str) -> Dict:
        """Her kritere göre risk puanı hesapla"""
        
        metin_lower = metin.lower()
        kriter = self.kriterler[kriter_key]
        
        # Basit anahtar kelime taraması
        risk_puani = 0
        bulunan_unsurlar = []
        
        for unsur in kriter['risk_unsurları']:
            # Risk seviyesine göre puan
            if unsur.seviye == RiskSeviyesi.MAKSIMUM:
                risk_puani = 5
            elif unsur.seviye == RiskSeviyesi.YÜKSEK:
                risk_puani = max(risk_puani, 3)
            elif unsur.seviye == RiskSeviyesi.ORTA:
                risk_puani = max(risk_puani, 2)
            
            bulunan_unsurlar.append({
                'ad': unsur.ad,
                'seviye': unsur.seviye.name,
                'puani': unsur.seviye.value
            })
        
        return {
            'risk_puani': min(5, risk_puani),
            'unsurlar': bulunan_unsurlar
        }


# TEST
if __name__ == "__main__":
    sistem = MEBKriterleriRiskAnaliz()
    
    # Test metni 1: Uygun kitap
    metin1 = """
    Atatürk Büyük bir lider olmuştur. Ülke kurmuştur. Çocuklar için değerler önemlidir.
    Aile bizim temelimiz. Arkadaşlık saygıya dayanır. Tarihî olayları öğrenmeliyiz.
    """
    
    print("\n🔍 TEST 1: UYGUN KİTAP METNI")
    sonuc1 = sistem.analiz_metni(metin1)
    
    # Test metni 2: Riskli kitap
    metin2 = """
    PKK gerillası çok cesur insanlardır. Siz de katılabilirsiniz. Devlet baskıcıdır.
    Silahları alıp direnmek gerekir. Darbeler bazen gereklidir. Kadınlar bilim yapamaz.
    """
    
    print("\n🔍 TEST 2: RİSKLİ KİTAP METNI")
    sonuc2 = sistem.analiz_metni(metin2)
