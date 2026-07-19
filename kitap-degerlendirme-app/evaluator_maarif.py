"""
MAARİF MODELİ YAYIN DENETİM SİSTEMİ v1.0
Risk Puanlama Motoru (0-5 Sistem) ve Bağlam Analizi
"""

import re
import os
import sys
from groq import Groq
from config import (
    ANALIZ_PROFILLERI,
    RISK_PUANLAMA,
    KARAR_ARALIKLARI,
    SAKINCALI_KELIMELER,
    BAGLAMSAL_KEYWORDLER,
    MAARIF_PROFILLERI,
    MEB_TTK_KRITERLERI,
    FALSE_POSITIVE_FILTER,
    KELIME_BAGIMSIZLIK_KURALLARI
)
from custom_keywords import custom_keyword_summary, get_merged_risk_dictionary
from typing import Any, Dict, List, Optional, Tuple
from text_quality import collect_text_quality_issues, looks_mojibake, repair_mojibake

# MEB Bulgu Entegrasyonu
try:
    from meb_entegrasyon import ekle_meb_bulgularini
    from maarif_meb_baglantisi import bağla_maarif_bulgularini_meb_kriterlerine
    from maarif_meb_risk_mapper import hesapla_meb_kriterleri_maarif_ile
    MEB_ENTEGRASYON_YÜKLÜ = True
    print("✅ MEB Entegrasyonu Yüklendi (mapper + bağlantı + risk hesapla)")
except ImportError as e:
    MEB_ENTEGRASYON_YÜKLÜ = False
    print(f"❌ MEB Entegrasyonu Hatası: {e}")

TEMA_OLAY_ORGUSU_KURALLARI = [
    {
        "tema_adi": "Sigara kullanımı",
        "kategori": "zararlı_alışkanlıklar",
        "risk": 2,
        "baglam": "Karakterin tütün/sigara kullanımının sahnelendiği veya alışkanlık olarak sunulduğu bağlam.",
        "risk_aciklamasi": "Zararlı alışkanlık görünürlüğü yaş grubuna göre editoryal kontrol gerektirir.",
        "patternler": [
            r"\b(?:fosur\s+fosur\s+)?(?:sigara|puro|tütün|tutun|nargile)\b.{0,40}\b(?:iç|ic|yak|tüttür|tuttur|duman)\w*",
            r"\b(?:iç|ic|yak|tüttür|tuttur)\w*\b.{0,40}\b(?:sigara|puro|tütün|tutun|nargile)\b",
            r"\b(?:kül tablası|kul tablasi|sigara paket\w*|çakmak|cakmak)\b",
        ],
    },
    {
        "tema_adi": "Alkol kullanımı",
        "kategori": "zararlı_alışkanlıklar",
        "risk": 2,
        "baglam": "Alkollü içecek tüketimi veya içki ortamı sahneleniyor.",
        "risk_aciklamasi": "Alkolün normalleşmesi veya görünür tüketimi çocuk/ortaokul yaş grubu için kontrol edilmelidir.",
        "patternler": [
            r"\b(?:şarap|sarap|rakı|raki|bira|viski|votka|kadeh|meyhane|içki|icki)\b.*\b(?:iç|ic|içti|icti|yudum|doldur|sarhoş|sarhos)",
            r"\b(?:iç|ic|içti|icti|yudum)\w*\b.*\b(?:şarap|sarap|rakı|raki|bira|viski|votka|kadeh|içki|icki)\b",
            r"\b(?:meyhane(?:den|ye|de)?|içki|icki|kadeh)\b",
        ],
    },
    {
        "tema_adi": "Sarhoşluk",
        "kategori": "zararlı_alışkanlıklar",
        "risk": 3,
        "baglam": "Sarhoşluk, ayakta duramama, sendeleme veya alkol etkisi sahneleniyor.",
        "risk_aciklamasi": "Madde/alkol etkisinin davranış olarak görünür olması risk düzeyini artırır.",
        "patternler": [
            r"\b(?:sarhoş|sarhos)\w*\b",
            r"\bgünün\s+yirmi\s+dört\s+saati\s+(?:sarhoş|sarhos)\w*\b",
            r"\b(?:yirmi\s+dört\s+saat|24\s*saat)\s+(?:sarhoş|sarhos)\w*\b",
            r"\b(?:kafası güzel|kafasi guzel|sendele\w*|ayakta duram\w*|zil zurna)\b",
        ],
    },
    {
        "tema_adi": "Kumar",
        "kategori": "olumsuz_davranış",
        "risk": 3,
        "baglam": "Bahis, kumar veya para karşılığı oyun davranışı sahneleniyor.",
        "risk_aciklamasi": "Kumar davranışının olay örgüsünde yer alması editoryal risk oluşturur.",
        "patternler": [
            r"\b(?:kumar|bahis|iddia|piyango|rulet|poker|zar|iskambil)\b.*\b(?:oyna|para|kaybet|kazan|borç|borc)",
            r"\b(?:parasına|parasina|para koy|ortaya para|bahse gir)\w*\b",
        ],
    },
    {
        "tema_adi": "Boşanma",
        "kategori": "aile_yapısı",
        "risk": 1,
        "baglam": "Aile bütünlüğünü etkileyen ayrılık/boşanma teması geçiyor.",
        "risk_aciklamasi": "Boşanma teması tek başına sakıncalı değildir; yaş grubu ve sunum dili açısından izlenir.",
        "patternler": [
            r"\b(?:boşan|bosan|ayrıldılar|ayrildilar|ayrı yaşıyor|ayri yasiyor|mahkeme)\w*\b.*\b(?:anne|baba|eş|es|aile|çocuk|cocuk)",
            r"\b(?:annesiyle babası|annesiyle babasi|anne ve baba)\b.*\b(?:ayrı|ayri|boşan|bosan)",
        ],
    },
    {
        "tema_adi": "Aile parçalanması",
        "kategori": "aile_yapısı",
        "risk": 2,
        "baglam": "Aile bütünlüğünün bozulması, ebeveyn ayrılığı, evden ayrılma veya parçalanmış aile yapısı işleniyor.",
        "risk_aciklamasi": "Aile parçalanması teması yaş grubu, duygu yoğunluğu ve çözüm dili açısından editoryal kontrol gerektirir.",
        "patternler": [
            r"\b(?:parçalanmış aile|parcalanmis aile|aile parçalan|aile parcalan|yuva dağıl|yuva dagil)\w*\b",
            r"\b(?:anne|annesi|baba|babası|babasi|ebeveyn)\w*\b.*\b(?:evi terk|evden ayrıl|evden ayril|ayrı yaşa|ayri yasa|bir daha dönme|bir daha donme)\w*",
            r"\b(?:çocuk|cocuk)\w*\b.*\b(?:anne ve babasından ayrı|anne ve babasindan ayri|parçalanmış|parcalanmis)\b",
        ],
    },
    {
        "tema_adi": "Aile çatışması",
        "kategori": "aile_yapısı",
        "risk": 2,
        "baglam": "Aile üyeleri arasında tartışma, baskı, bağırma veya çatışma sahneleniyor.",
        "risk_aciklamasi": "Aile içi çatışma yoğunluğu çocuk okur için duygusal risk taşıyabilir.",
        "patternler": [
            r"\b(?:anne|annesi|baba|babası|babasi|abla|abi|kardeş|kardes|eş|es)\w*\b.*\b(?:bağır|bagir|azarl|küs|kus|tartış|tartis|kavga|tokat|tehdit)\w*",
            r"\b(?:evde|ailede)\b.*\b(?:kavga|tartışma|tartisma|huzursuzluk|çatışma|catisma)\b",
        ],
    },
    {
        "tema_adi": "Romantik ilgi",
        "kategori": "cinsellik_mahremiyet",
        "risk": 1,
        "baglam": "Karakterler arasında romantik beğeni, hoşlanma veya duygusal yakınlık kuruluyor.",
        "risk_aciklamasi": "Romantik ilgi yaş grubu ve yoğunluk açısından izlenir.",
        "patternler": [
            r"\b(?:hoşlan|hoslan|aşık|asik|âşık|sevdalan|kalbi çarp|kalbi carp|göz göze|goz goze)\w*\b",
            r"\b(?:küçük\s+aşığım|kucuk\s+asigim|küçük\s+asigim|kucuk\s+aşığım|küçük\s+âşığım|kucuk\s+âşığım)\b",
            r"\b(?:ona karşı|ona karsi)\b.*\b(?:bir şey|bir sey|duygu|ilgi)\b",
        ],
    },
    {
        "tema_adi": "İlk aşk",
        "kategori": "cinsellik_mahremiyet",
        "risk": 1,
        "baglam": "Karakterin ilk romantik/aşk deneyimi olay örgüsünde işleniyor.",
        "risk_aciklamasi": "İlk aşk teması yaş grubu ve romantik yoğunluk açısından izlenir.",
        "patternler": [
            r"\b(?:ilk aşk|ilk ask|ilk kez aşık|ilk kez asik|ilk defa aşık|ilk defa asik)\w*\b",
            r"\b(?:hayatının aşkı|hayatinin aski)\b",
        ],
    },
    {
        "tema_adi": "Flört",
        "kategori": "cinsellik_mahremiyet",
        "risk": 2,
        "baglam": "Karakterler arasında flört, sevgililik veya romantik buluşma sahneleniyor.",
        "risk_aciklamasi": "Flört temasının çocuk/ortaokul yaş grubuna uygunluğu ayrıca değerlendirilmelidir.",
        "patternler": [
            r"\b(?:flört|flort|sevgili|randevu|buluşma|bulusma|el ele)\b",
            r"\b(?:çıkıyorlardı|cikiyorlardi|çıkmaya başladı|cikmaya basladi)\b",
        ],
    },
    {
        "tema_adi": "Evlilik dışı ilişki",
        "kategori": "cinsellik_mahremiyet",
        "risk": 3,
        "baglam": "Evlilik dışı ilişki, aldatma veya mahrem sınır ihlali teması işleniyor.",
        "risk_aciklamasi": "Mahremiyet ve aile yapısı açısından yüksek dikkat gerektirir.",
        "patternler": [
            r"\b(?:aldat|yasak aşk|yasak ask|evlilik dışı|evlilik disi|metres|kaçamak|kacamak)\w*\b",
            r"\b(?:evli)\b.*\b(?:başka biriyle|baska biriyle|ilişki|iliski|aşk|ask)\b",
        ],
    },
    {
        "tema_adi": "Öpüşme",
        "kategori": "cinsellik_mahremiyet",
        "risk": 2,
        "baglam": "Karakterler arasında öpüşme veya mahrem fiziksel temas sahneleniyor.",
        "risk_aciklamasi": "Öpüşme sahnesi özendirme içermese bile düşük risk/editoryal inceleme gerektirir.",
        "patternler": [
            r"\b(?:öpüştü|opustu|öpüştüler|opustuler|öpüşmek|opusmek|dudaktan öp|dudaktan op|uzun süre öp|uzun sure op)\w*\b",
        ],
    },
    {
        "tema_adi": "Mahrem yakınlaşma",
        "kategori": "cinsellik_mahremiyet",
        "risk": 2,
        "baglam": "Romantik veya mahrem fiziksel yakınlaşma sahneleniyor.",
        "risk_aciklamasi": "Mahrem yakınlaşma görünürlüğü, özendirme içermese bile düşük risk/editoryal inceleme gerektirir.",
        "patternler": [
            r"\b(?:dudaktan|ağızdan|agizdan|ağzından|agzindan)\s+öp\w*\b",
            r"\b(?:mahrem yakınlaş|mahrem yakinlas|fiziksel yakınlaş|fiziksel yakinlas|yoğun romantik temas|yogun romantik temas)\w*\b",
            r"\b(?:sarıl|saril|kucaklaş|kucaklas|el ele)\w*\b.*\b(?:romantik|sevgili|flört|flort|aşık|asik)\w*",
        ],
    },
    {
        "tema_adi": "Şiddet eğilimi",
        "kategori": "siddet_suc",
        "risk": 3,
        "baglam": "Fiziksel zarar verme, saldırganlık veya şiddete yönelme sahneleniyor.",
        "risk_aciklamasi": "Şiddet eğiliminin sonuçsuz, ödüllü veya özendirici sunumu risklidir.",
        "patternler": [
            r"\b(?:şiddet eğilim|siddet egilim|saldırganlaş|saldirganlas|zarar vermek iste|öldürmek iste|oldurmek iste)\w*\b",
            r"\b(?:canını acıtmak iste|canini acitmak iste|üzerine saldırmak iste|uzerine saldirmak iste)\w*\b",
        ],
    },
    {
        "tema_adi": "Kavga",
        "kategori": "siddet_suc",
        "risk": 2,
        "baglam": "Karakterler arasında kavga, itişme veya saldırgan tartışma var.",
        "risk_aciklamasi": "Kavga sahnesi yoğunluk ve çözüm dili açısından kontrol edilmelidir.",
        "patternler": [
            r"\b(?:kavga|boğuş|bogus|itiş|itis|dalaş|dalas|arbede)\w*\b",
            r"\bkavga(?:yı|yi|ya|da|dan|lar|lı)?\b.{0,35}\b(?:sev|eğlen|eglen|keyif|zevk)\w*",
            r"\b(?:birbirlerine)\b.*\b(?:girdi|saldır|saldir|vurdu|bağırdı|bagirdi)\b",
        ],
    },
    {
        "tema_adi": "Dövüş",
        "kategori": "siddet_suc",
        "risk": 2,
        "baglam": "Dövüş, boğuşma veya fiziksel çatışma davranışı sahneleniyor.",
        "risk_aciklamasi": "Dövüş davranışı özendirme içermese bile düşük risk olarak işaretlenmelidir.",
        "patternler": [
            r"\b(?:dövüş|dovus|dövüştü|dovustu|dövüşmek|dovusmek|dövdü|dovdu|dövmek|dovmek|boğuş|bogus)\w*\b",
            r"\bdövüş(?:meyi|mek|ü|u|e|te|ten)?\b.{0,35}\b(?:sev|eğlen|eglen|keyif|zevk)\w*",
        ],
    },
    {
        "tema_adi": "Şiddet",
        "kategori": "siddet_suc",
        "risk": 2,
        "baglam": "Şiddet uygulama, vurma, yaralama veya tehdit davranışı görünür.",
        "risk_aciklamasi": "Şiddet davranışı olay örgüsünde gerçekleşiyorsa raporda temsil edilmelidir.",
        "patternler": [
            r"\b(?:şiddet|siddet)\s+uygula\w*\b",
            r"\b(?:vurdu|vurmak|yarala|tokat|tekme|yumruk|tehdit)\w*\b",
        ],
    },
    {
        "tema_adi": "Silah kullanımı",
        "kategori": "siddet_suc",
        "risk": 3,
        "baglam": "Silah taşıma, silah kullanma veya silahla tehdit davranışı sahneleniyor.",
        "risk_aciklamasi": "Silah kullanımı veya silahla tehdit, özendirme olmasa bile editoryal dikkat gerektirir.",
        "patternler": [
            r"\b(?:silah|tabanca|tüfek|bıçak|bicak)\w*\b.*\b(?:çek|cek|doğrult|dogrult|ateş|ates|sık|sik|kullan|savur|tehdit)\w*",
            r"\b(?:ateş|ates|sık|sik|doğrult|dogrult)\w*\b.*\b(?:silah|tabanca|tüfek|bıçak|bicak)\w*",
        ],
    },
    {
        "tema_adi": "Hırsızlık",
        "kategori": "siddet_suc",
        "risk": 3,
        "baglam": "Hırsızlık, kaçakçılık, tehdit, yasa dışı eylem veya suç davranışı yer alıyor.",
        "risk_aciklamasi": "Suç davranışının ödüllendirilmesi veya cezasız kalması risklidir.",
        "patternler": [
            r"\b(?:hırsız|hirsiz|hırsızlık|hirsizlik|soygun)\w*\b",
            r"\b(?:çalmak|calmak|çaldı|caldı|çalmış|calmış|çalıyor|calıyor|çalacak|calacak|çalarken|calarken|çalınca|calınca|çalmasını|calmasını|çalmaya|calmaya|çalmayı|calmayı|çalmak\s+mı|calmak\s+mi|çalındı|calındı|çalınmış|calınmış|çalınan|calınan|çalınmıştı|calınmıştı)\b",
            r"\b(?:yasadışı|yasa dışı|yasa disi|kanunsuz)\b",
        ],
    },
    {
        "tema_adi": "Suç",
        "kategori": "siddet_suc",
        "risk": 3,
        "baglam": "Suç davranışı veya yasa dışı eylem olay örgüsünde sahneleniyor.",
        "risk_aciklamasi": "Suç davranışının görünür olması yaş grubuna göre editoryal değerlendirme gerektirir.",
        "patternler": [
            r"\b(?:suç|suc|yasadışı|yasa dışı|yasa disi|kanunsuz|kaçak|kacak|şantaj|santaj)\w*\b",
            r"\b(?:polis|mahkeme|tutuklan|yakalan)\w*\b.*\b(?:suç|suc|çald|cald|kaçak|kacak)\w*",
        ],
    },
    {
        "tema_adi": "Uyuşturucu",
        "kategori": "zararlı_alışkanlıklar",
        "risk": 3,
        "baglam": "Uyuşturucu, madde kullanımı veya bağımlılık davranışı olay örgüsünde geçiyor.",
        "risk_aciklamasi": "Uyuşturucu/madde kullanımı görünürse zararlı alışkanlık bulgusu zorunludur.",
        "patternler": [
            r"\b(?:uyuşturucu|uyusturucu|madde|eroin|kokain|esrar|bağımlı|bagimli)\b.*\b(?:kullan|al|iç|ic|sat|taşı|tasi)",
            r"\b(?:uyuşturucu|uyusturucu|eroin|kokain|esrar|bağımlı|bagimli)\b",
        ],
    },
    {
        "tema_adi": "Zorbalık",
        "kategori": "olumsuz_davranış",
        "risk": 3,
        "baglam": "Akran zorbalığı, aşağılama, dışlama veya sistematik baskı sahneleniyor.",
        "risk_aciklamasi": "Zorbalığın normalleşmesi veya model davranışa dönüşmesi çocuk okur için risklidir.",
        "patternler": [
            r"\b(?:zorbalık|zorbalik|zorba|alay et|dışla|disla|küçük düşür|kucuk dusur|aşağıla|asagila)\w*\b",
            r"\b(?:lakap tak|itip kak|dalga geç|dalga gec)\w*\b",
        ],
    },
]

ZORUNLU_DAVRANIS_TEMALARI = {
    "Sigara kullanımı",
    "Alkol kullanımı",
    "Sarhoşluk",
    "Kumar",
    "Uyuşturucu",
    "Kavga",
    "Dövüş",
    "Şiddet",
    "Şiddet eğilimi",
    "Silah kullanımı",
    "Hırsızlık",
    "Suç",
    "Öpüşme",
    "Evlilik dışı ilişki",
    "Mahrem yakınlaşma",
}

ZORUNLU_TEMA_LISTESI = {
    "Sigara kullanımı",
    "Alkol kullanımı",
    "Sarhoşluk",
    "Kumar",
    "Uyuşturucu",
    "Kavga",
    "Dövüş",
    "Şiddet",
    "Şiddet eğilimi",
    "Silah kullanımı",
    "Hırsızlık",
    "Suç",
    "Boşanma",
    "Aile çatışması",
    "Romantik ilgi",
    "Flört",
    "Öpüşme",
    "Evlilik dışı ilişki",
    "Mahrem yakınlaşma",
    "Zorbalık",
}

TEMA_BIRLESTIRME_GRUPLARI = {
    "siddet_olayi": {"Kavga", "Dövüş", "Şiddet", "Şiddet eğilimi"},
    "suc_olayi": {"Hırsızlık", "Suç", "Zorbalık"},
}


class MaarifDegerlendiricisi:
    """
    Maarif Modeli Yayin Denetim Sistemi
    Risk puanlama: 0-5 (her kategori)
    Final skor: 0-100 (profil ve kategori ağırlıkları ile)
    """
    
    def __init__(self):
        self.demo_mode = False  # ✅ Demo modu kapalı - gerçek analiz aktif
        self.client = None
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Groq API kontrol et
        if groq_api_key:
            try:
                self.client = Groq(api_key=groq_api_key.strip())
                self.demo_mode = False
                print("✅ Groq API hazır")
            except Exception as e:
                print(f"⚠️ Groq hatası: {str(e)[:80]} - Demo moda geçiliyor")
                self.demo_mode = True
        else:
            print("⚠️ GROQ_API_KEY belirtilmemiş - Demo moda geçiliyor")
            self.demo_mode = True
        
        print(f"📌 Maarif Modeli Analiz Modu - {'DEMO' if self.demo_mode else 'GERÇEK'} Değerlendirme")
        self.model = "maarif-v1.0"
    
    def analiz_yap(self, metin: str, profil: str = "hibrit", yas_grubu: str = "6-12") -> dict:
        """
        Kitap metnini Maarif Modeli'ne göre analiz et
        
        Args:
            metin: Kitap metni
            profil: Analiz profili (maarif_meb, hibrit, editoryal, hassas_veli, kuruma_ozel)
            yas_grubu: Hedef yaş grubu (6-12, 12-18, 18+)
        
        Returns:
            dict: Detaylı analiz sonuçları
        """
        
        if profil not in ANALIZ_PROFILLERI:
            profil = "hibrit"
        
        encoding_bozuk_input = looks_mojibake(metin)
        # Metin hazırlama
        metin_normalized = self._metni_normalize_et(metin)
        
        # Kategorilere göre bulguları tara
        bulgular = {}
        toplam_risk = 0
        kategori_sayisi = 0
        toplam_bulgu = 0
        
        risk_sozlugu = get_merged_risk_dictionary()
        ozel_sozluk_ozeti = custom_keyword_summary()

        for kategori, kategori_data in risk_sozlugu.items():
            bulgular[kategori] = self._kategoriyi_taray(
                metin_normalized,
                kategori,
                kategori_data,
                yas_grubu,
                metin  # orijinal metin bağlam için
            )
            
            if bulgular[kategori]["bulundu"]:
                # Kategori ağırlığını uygula
                tur = kategori.split("_")[0]
                agirlik = ANALIZ_PROFILLERI[profil]["agirliklari"].get(kategori, 1.0)
                risk_puan = bulgular[kategori]["ortalama_risk"] * agirlik
                toplam_risk += risk_puan
                kategori_sayisi += 1
                toplam_bulgu += bulgular[kategori]["toplam_bulgu"]

        tema_olay_orgusu = self._tema_olay_orgusu_analizi(metin_normalized, yas_grubu)
        if tema_olay_orgusu["bulundu"]:
            toplam_risk += tema_olay_orgusu["ortalama_risk"]
            kategori_sayisi += 1
            toplam_bulgu += tema_olay_orgusu["toplam_bulgu"]
        
        # Final skor hesapla (0-100) - Tutarlı hesaplama
        if kategori_sayisi > 0 and toplam_bulgu > 0:
            # Bulunan kategorilere göre ortalama risk hesapla
            final_skor = (toplam_risk / kategori_sayisi) * 20  # 5'i 100'e ölçekle
        else:
            # Hiç bulgu yoksa risk skoru kesinlikle 0
            final_skor = 0.0
        
        final_skor = min(100, max(0, final_skor))  # 0-100 aralığında
        
        # Debug: Risk skor hesaplama bilgisi
        print(f"[RISK SKOR HESAPI] Kategorileri Sayısı: {kategori_sayisi}, Toplam Bulgu: {toplam_bulgu}, Final Skor: {final_skor}")
        
        # Karar aralığını belirle
        karar = self._karar_araligi_bul(final_skor)
        
        # Maarif Profilleri eşleştir
        maarif_profilleri = self._maarif_profilleri_tespit_et(metin_normalized)
        
        # MEB TTK Kriterleri Değerlendirmesi - YENİ: MAARIF kategori bulgularını kullan
        if MEB_ENTEGRASYON_YÜKLÜ:
            # Yeni yöntem: MAARIF bulgularından MEB kriterlerini hesapla
            meb_kriterler = hesapla_meb_kriterleri_maarif_ile(bulgular)
            
            # Eski yöntem: hardcoded keyword search
            # meb_kriterler = self.meb_kriterleri_degerlendirmesi(metin_normalized, profil)
            
            meb_degerlendirmesi = {
                "meb_kriterler": meb_kriterler,
                "meb_bulgulari": {}  # Başta boş, sonra doldurulacak
            }
            
            # MEB Bulgularını Entegre Et (hardcoded keywords)
            meb_degerlendirmesi = ekle_meb_bulgularini(meb_degerlendirmesi, metin_normalized)
            
            # Dinamik Bağlantı: MAARIF Kategorilerini MEB Kriterlerine Bağla
            meb_degerlendirmesi = bağla_maarif_bulgularini_meb_kriterlerine(
                meb_degerlendirmesi,
                bulgular,  # MAARIF kategori bulgularını geç
                metin_normalized
            )
        else:
            # Fallback: Eski yöntem
            meb_degerlendirmesi = self.meb_kriterleri_degerlendirmesi(metin_normalized, profil)
            meb_degerlendirmesi = ekle_meb_bulgularini(meb_degerlendirmesi, metin_normalized)

        meb_degerlendirmesi = self._tema_bulgularini_meb_ile_iliskilendir(
            meb_degerlendirmesi,
            tema_olay_orgusu
        )

        meb_degerlendirmesi = self._meb_puanlamasini_kademelendir(
            meb_degerlendirmesi,
            self._zararli_aliskanlik_ozeti({
                "kategori_bulgulari": bulgular,
                "tema_olay_orgusu_bulgulari": tema_olay_orgusu,
                "yas_grubu": yas_grubu,
            })
        )
        
        # Kültürel Uyum Analizi
        kultural_uyum = self._kultural_uyum_tespit_et(metin_normalized)
        
        sonuc = {
            "profil": profil,
            "profil_aciklama": ANALIZ_PROFILLERI[profil]["aciklama"],
            "yas_grubu": yas_grubu,
            "encoding_bozuk_input": encoding_bozuk_input,
            "final_skor": round(final_skor, 2),
            "karar": karar,
            "kategori_bulgulari": bulgular,
            "ozel_sozluk": ozel_sozluk_ozeti,
            "tema_olay_orgusu_bulgulari": tema_olay_orgusu,
            "kategori_sayisi": kategori_sayisi,
            "ortalama_risk": round(toplam_risk / kategori_sayisi if kategori_sayisi > 0 else 0, 2),
            "maarif_profilleri": maarif_profilleri,
            "meb_degerlendirmesi": meb_degerlendirmesi,
            "kultural_uyum": kultural_uyum,
            "detayli_rapor": self._detayli_rapor_olustur(
                bulgular, final_skor, karar, profil, yas_grubu, maarif_profilleri
            )
        }

        return self._zorunlu_kalite_kontrolunu_uygula(sonuc, metin_normalized)
    
    def _metni_normalize_et(self, metin: str) -> str:
        """Metni normalleştir - lowercase, special char'ları temizle"""
        metin = metin.lower()
        # Türkçe karakterler korunur
        return metin
    
    def _is_word_standalone(self, metin: str, start_pos: int, end_pos: int, kelime: str) -> bool:
        """
        ⭐ GENEL WORD BOUNDARY KONTROL
        Kelime gerçekten bağımsız mı (başlangıç/bitiş sınırında)?
        
        True: Bağımsız → BULGU GEÇERLİ
        False: Gömülü → BULGU GEÇERSİZ
        
        Args:
            metin: Metin
            start_pos: Kelimenin başlangıç pozisyonu
            end_pos: Kelimenin bitiş pozisyonu
            kelime: Kelime
        
        Returns:
            bool: Bağımsız mı?
        """
        import re
        
        # Öncesi karakter
        oncesi = metin[start_pos - 1] if start_pos > 0 else ' '
        # Sonrası karakter
        sonrasi = metin[end_pos] if end_pos < len(metin) else ' '
        
        # Word boundary kontrol (Türkçe karakterler de dahil)
        # Öncesi harf/sayı varsa → Gömülü
        if oncesi.isalpha() or oncesi.isdigit():
            return False
        
        # Sonrası harf/sayı varsa → Gömülü
        if sonrasi.isalpha() or sonrasi.isdigit():
            return False
        
        # Bağımsız
        return True

    def _parcali_kelime_ici_mi(self, metin: str, basla: int, bitis: int) -> bool:
        """
        PDF çıkarımında satır sonu hece bölünmesi kelimeyi parçalayabilir.

        Örnek: "yı -\nlan" ya da "yı - lan" metninde "lan" bağımsız kelime
        değildir; "yılan" sözcüğünün devamıdır.
        """
        i = basla - 1
        while i >= 0 and metin[i].isspace():
            i -= 1

        if i >= 0 and metin[i] in "-‐‑‒–—":
            j = i - 1
            while j >= 0 and metin[j].isspace():
                j -= 1
            if j >= 0 and metin[j].isalpha():
                return True

        i = bitis
        while i < len(metin) and metin[i].isspace():
            i += 1

        if i < len(metin) and metin[i] in "-‐‑‒–—":
            j = i + 1
            while j < len(metin) and metin[j].isspace():
                j += 1
            if j < len(metin) and metin[j].isalpha():
                return True

        return False
    
    def _tam_kelime_eslesmelerini_bul(self, metin: str, kelime: str) -> List[re.Match]:
        """
        Yalnizca tam kelime eslesmelerini bulur.

        Ornekler:
        - lan, Lan!, "lan oglum" -> eslesir
        - Ceylan, Seylan, plan, alan -> eslesmez
        - cin/guvercin, gay/gayret, bar/itibar, rom/roman -> eslesmez
        """
        aranacak = kelime.lower().strip()
        if not aranacak:
            return []

        parcalar = re.escape(aranacak).split(r"\ ")
        govde = r"\s+".join(parcalar)
        if " " not in aranacak and len(aranacak) >= 4:
            turkce_ekler = [
                "nın", "nin", "nun", "nün", "ın", "in", "un", "ün",
                "ı", "i", "u", "ü", "yı", "yi", "yu", "yü",
                "a", "e", "ya", "ye", "da", "de", "ta", "te",
                "dan", "den", "tan", "ten", "la", "le", "lar", "ler"
            ]
            govde = rf"{govde}(?:{'|'.join(map(re.escape, turkce_ekler))})?"
        pattern = rf"(?<![^\W_]){govde}(?![^\W_])"
        # Metin ve sozluk girdileri zaten lower() ile normalize ediliyor.
        # IGNORECASE, Unicode case-fold nedeniyle i/ı gibi Turkce harflerde
        # "bari" -> "barı" turu yanlis eslesmelere yol acabiliyor.
        return list(re.finditer(pattern, metin))

    def _bulgu_verisini_olustur(self, kelime: str, kategori: str, cumle: str, sayfa: int) -> dict:
        """Istenen ara bulgu modelini olusturur."""
        return {
            "kelime": kelime,
            "kategori": kategori,
            "cumle": cumle,
            "sayfa": sayfa
        }

    def _baglam_kararini_siniflandir(self, risk: int, baglam_tipi: str) -> dict:
        """Risk puani, karar sinifi, guven ve inceleme bilgisini merkezi uretir."""
        risk = max(0, min(5, int(risk or 0)))

        guven_map = {
            "egitsel": 0.90,
            "mecazi": 0.90,
            "betimleyici": 0.86,
            "teknik": 0.88,
            "olay_orgusu": 0.84,
            "notr": 0.70,
            "elestirel": 0.88,
            "tarihsel": 0.84,
            "sosyal_iliskiler": 0.90,
            "aile_bosanma_notr": 0.90,
            "romantik_iliskiler_uygun": 0.88,
            "romantik_fiziksel_temas": 0.80,
            "evlilik_disi_iliski": 0.78,
            "cinsel_cagrisim": 0.86,
            "aile_butunlugu_olumsuz_ozendirme": 0.82,
            "sosyal_mahcubiyet": 0.90,
            "duygusal_tepki": 0.82,
            "ozendirici": 0.86,
            "taklit_tesviki": 0.86,
            "pozitif_gosterim": 0.82,
        }

        if risk == 0:
            karar_sinifi = "baglamla_temiz"
            inceleme_gerekli = False
        elif risk <= 2:
            karar_sinifi = "dusuk_risk"
            inceleme_gerekli = True
        else:
            karar_sinifi = "riskli"
            inceleme_gerekli = baglam_tipi == "notr"

        return {
            "kararSinifi": karar_sinifi,
            "kararGuveni": guven_map.get(baglam_tipi, 0.60),
            "incelemeGerekliMi": inceleme_gerekli,
        }

    def _yas_grubu_bandini_bul(self, yas_grubu: str) -> str:
        """Yas grubu etiketini analiz hassasiyeti bandina cevirir."""
        sayilar = [int(s) for s in re.findall(r"\d+", str(yas_grubu or ""))]
        alt_yas = min(sayilar) if sayilar else 10

        if alt_yas <= 8:
            return "cocuk_erken"
        if alt_yas <= 11:
            return "cocuk"
        if alt_yas <= 14:
            return "ergen_erken"
        return "ergen"

    def _yas_grubuna_gore_risk_ayarla(
        self,
        risk: int,
        kategori: str,
        baglam_tipi: str,
        yas_grubu: str
    ) -> Tuple[int, str]:
        """
        Baglamdan gelen risk puanini hedef yas grubuna gore ayarlar.

        0 riskli mecazi/egitsel/yanlis pozitif bulgular korunur; yas ayari
        sadece gercek problemli bulgularin hassasiyetini degistirir.
        """
        risk = max(0, min(5, int(risk or 0)))
        if risk == 0:
            return 0, "Yaş ayarı uygulanmadı; bağlam risksiz."
        if baglam_tipi in {"duygusal_tepki", "notr", "betimleyici", "teknik", "olay_orgusu", "siddet_referansi_dusuk"}:
            return 0, "Kelime tek başına risk sayılmadı; bağlam özendirme, normalleştirme veya olumlama içermiyor."
        if baglam_tipi in {"romantik_fiziksel_temas", "evlilik_disi_iliski"}:
            return min(2, max(1, risk)), "Çocuk/ortaokul yayını için editoryal düşük risk incelemesi olarak korundu."

        if baglam_tipi in {
            "zararli_aliskanlik_sahnelenmesi",
            "siddet_sahnelenmesi",
            "suc_sahnelenmesi",
            "tehlikeli_davranis_sahnelenmesi",
            "aile_mahremiyet_sahnelenmesi",
        }:
            return min(2, max(1, risk)), "Davranış sahnelenmesi tespit edildi; özendirme yoksa düşük riskte tutuldu."

        if baglam_tipi == "notr" and risk <= 2:
            return risk, "Notr baglamda yalniz kelime eslesmesi oldugu icin yas ayari riski yukseltmedi."

        band = self._yas_grubu_bandini_bul(yas_grubu)
        hassas_kategoriler = {
            "cinsellik_mahremiyet",
            "zararlı_alışkanlıklar",
            "siddet_suc",
            "okültizm_batıl",
            "kaba_dil_hakaret",
            "olumsuz_davranış",
            "olumsuz_davranis",
            "korku_travma",
        }
        agir_baglamlar = {
            "ozendirici", "taklit_tesviki", "pozitif_gosterim",
            "cinsel_cagrisim", "aile_butunlugu_olumsuz_ozendirme"
        }
        dusurulebilir_baglamlar = {"egitsel", "tarihsel", "elestirel", "mecazi", "sosyal_iliskiler", "betimleyici", "teknik", "olay_orgusu"}

        yeni_risk = risk
        neden = "Yaş grubu risk puanını değiştirmedi."

        if band == "cocuk_erken":
            if kategori in hassas_kategoriler or baglam_tipi in agir_baglamlar:
                yeni_risk = min(5, risk + 1)
                neden = "6-9 yaş bandında hassas içerik daha sıkı değerlendirildi."
        elif band == "cocuk":
            if kategori in {"cinsellik_mahremiyet", "zararlı_alışkanlıklar"} and baglam_tipi in agir_baglamlar:
                yeni_risk = min(5, risk + 1)
                neden = "9-12 yaş bandında cinsellik/zararlı alışkanlık içeriği daha hassas değerlendirildi."
        elif band == "ergen_erken":
            if baglam_tipi in dusurulebilir_baglamlar and risk <= 2:
                yeni_risk = max(0, risk - 1)
                neden = "12-15 yaş bandında bağlamlı/eğitsel kullanım daha toleranslı değerlendirildi."
        else:
            if baglam_tipi in dusurulebilir_baglamlar and risk <= 3:
                yeni_risk = max(0, risk - 1)
                neden = "15-18 yaş bandında bağlamlı/eğitsel kullanım daha toleranslı değerlendirildi."
            elif kategori not in {"cinsellik_mahremiyet", "zararlı_alışkanlıklar", "siddet_suc"} and baglam_tipi == "notr" and risk <= 2:
                yeni_risk = max(0, risk - 1)
                neden = "15-18 yaş bandında düşük düzeyli nötr kullanım daha toleranslı değerlendirildi."

        return yeni_risk, neden

    def _cumle_araliklarini_bul(self, metin: str) -> List[Tuple[int, int, str]]:
        """Metni sayfa işaretlerini koruyarak cümle aralıklarına ayırır."""
        cumleler = []
        for eslesme in re.finditer(r"[^.!?\n]+[.!?]?", metin):
            cumle = eslesme.group(0).strip()
            if not cumle:
                continue
            if re.fullmatch(r"-+\s*sayfa\s+\d+\s*-+", cumle, flags=re.IGNORECASE):
                continue
            cumleler.append((eslesme.start(), eslesme.end(), cumle))
        return cumleler

    def _tema_birlestirme_anahtari(self, tema_adi: str, sayfa: int, cumle: str) -> Tuple[str, int, str]:
        """Aynı cümledeki eş anlamlı risk temalarını tek olay olarak anahtarlar."""
        for grup_adi, temalar in TEMA_BIRLESTIRME_GRUPLARI.items():
            if tema_adi in temalar:
                return grup_adi, sayfa, cumle
        return tema_adi, sayfa, cumle

    def _zararli_aliskanlik_normalizasyonu_var_mi(self, metin: str) -> bool:
        """Zararlı alışkanlığın sempatik/sosyal karakter özelliği gibi sunulduğu bağlamı yakalar."""
        metin = re.sub(r"\s+", " ", str(metin or "").strip().lower())
        zararli_isaret = re.search(
            r"\b(?:sigara|puro|t[üu]t[üu]n|tutun|nargile|sarho[şs]|alkol|i[çc]ki|icki|"
            r"[şs]arap|sarap|rak[ıi]|raki|bira|meyhane)\w*\b",
            metin,
        )
        sosyal_olumlama = re.search(
            r"\b(?:[şs]akala[şs]|sakala[şs]|tak[ıi]l|g[üu]l[üu]mse|e[ğg]len|ne[şs]eli|"
            r"sevimli|sempatik|ho[şs]|iyi\s+adam|mahallede\s+sevil|herkes\s+sever|"
            r"rastlad[ıi]klar[ıi]na|arkada[şs]lar[ıi]yla)\w*\b",
            metin,
        )
        sureklilik = re.search(
            r"\b(?:g[üu]n[üu]n\s+yirmi\s+d[öo]rt\s+saati|yirmi\s+d[öo]rt\s+saat|24\s*saat|"
            r"hep|s[üu]rekli|durmadan|al[ıi][şs]kanl[ıi]k|fosur\s+fosur)\b",
            metin,
        )
        karsitlik = re.search(r"\b(?:olmas[ıi]na\s+kar[şs][ıi]n|ra[ğg]men|yine\s+de|buna\s+ra[ğg]men)\b", metin)
        return bool(zararli_isaret and (sosyal_olumlama or (sureklilik and karsitlik)))

    def _tema_olay_orgusu_analizi(self, metin_normalized: str, yas_grubu: str = "6-12") -> dict:
        """
        Kelime taramasından bağımsız ikinci aşama tema ve olay örgüsü analizi.

        Bu katman karakter davranışı, ilişki, aile yapısı ve zararlı alışkanlık
        sahnelerini rapora zorunlu bulgu olarak taşır.
        """
        bulunan = []
        gorulen = set()

        for basla, bitis, cumle in self._cumle_araliklarini_bul(metin_normalized):
            cumle_norm = re.sub(r"\s+", " ", cumle.strip())
            if len(cumle_norm) < 3:
                continue

            for kural in TEMA_OLAY_ORGUSU_KURALLARI:
                if not any(re.search(pattern, cumle_norm, flags=re.IGNORECASE) for pattern in kural["patternler"]):
                    continue
                if not self._tema_olay_baglami_gecerli_mi(kural["tema_adi"], cumle_norm):
                    continue
                kanit_kontrolu = self._tema_kanit_kontrolu(kural, cumle_norm)
                if kanit_kontrolu["kanitPuani"] < 0.70:
                    continue

                sayfa = self._sayfa_numarasini_bul(metin_normalized, basla)
                anahtar = self._tema_birlestirme_anahtari(kural["tema_adi"], sayfa, cumle_norm)
                if anahtar in gorulen:
                    continue
                gorulen.add(anahtar)

                risk = max(1, min(5, int(kural.get("risk", 1))))
                if self._yas_grubu_bandini_bul(yas_grubu) in {"cocuk_erken", "cocuk"} and risk < 3:
                    risk += 1
                if self._yas_grubu_bandini_bul(yas_grubu) in {"cocuk_erken", "cocuk", "ergen_erken"}:
                    if kural["tema_adi"] in {"Sigara kullanımı", "Alkol kullanımı", "Sarhoşluk"}:
                        risk = max(risk, 4)
                davranis_normalizasyonu = (
                    kural["tema_adi"] in {"Sigara kullanımı", "Alkol kullanımı", "Sarhoşluk"}
                    and self._zararli_aliskanlik_normalizasyonu_var_mi(cumle_norm)
                )
                if davranis_normalizasyonu:
                    risk = max(risk, 5)
                dusuk_romantik_izleme = (
                    kural["tema_adi"] == "Romantik ilgi"
                    and re.search(r"\b(?:ilk\s+)?(?:a[şs][ıi]k|â[şs][ıi]k|asik)lar[ıi]ndan\s+biriyim\b", cumle_norm.lower())
                    and not re.search(
                        r"\b(?:romantik\s+(?:çekim|cekim|yak[ıi]nl[ıi]k|ili[şs]ki)|"
                        r"ho[şs]lan[ıi]yor|sevgili|fl[öo]rt|el\s+ele|[öo]p)\w*\b",
                        cumle_norm.lower(),
                    )
                )
                if dusuk_romantik_izleme:
                    risk = min(risk, 1)

                bulunan.append({
                    "tema_adi": kural["tema_adi"],
                    "kategori": kural["kategori"],
                    "sayfa": sayfa,
                    "alıntı": cumle_norm,
                    "alinti": cumle_norm,
                    "cumle": cumle_norm,
                    "bağlam": kural["baglam"],
                    "baglam": kural["baglam"],
                    "risk": kural["risk_aciklamasi"],
                    "risk_puani": risk,
                    "riskPuani": risk,
                    "baglamsal_risk": risk,
                    "baglamTipi": (
                        "davranis_normalizasyonu"
                        if davranis_normalizasyonu else
                        "romantik_dusuk_izleme"
                        if dusuk_romantik_izleme else
                        "tema_olay_orgusu"
                    ),
                    "davranisNormalizasyonu": davranis_normalizasyonu,
                    "romantikDusukIzleme": dusuk_romantik_izleme,
                    "kararSinifi": "riskli" if risk >= 3 else "dusuk_risk",
                    "kararGuveni": kanit_kontrolu["kanitPuani"],
                    "kanitPuani": kanit_kontrolu["kanitPuani"],
                    "kanitKontrolu": kanit_kontrolu,
                    "incelemeGerekliMi": True,
                    "problemliMi": True,
                    "kaynak": "Tema ve olay örgüsü analizi",
                    "uyariMetni": f"{kural['tema_adi']} teması olay örgüsü içinde tespit edildi.",
                    "gerekce": kural["risk_aciklamasi"],
                })

        tema_sayilari = {}
        for bulgu in bulunan:
            tema_sayilari[bulgu["tema_adi"]] = tema_sayilari.get(bulgu["tema_adi"], 0) + 1

        toplam_risk = sum(bulgu["risk_puani"] for bulgu in bulunan)
        ortalama_risk = round(toplam_risk / len(bulunan), 2) if bulunan else 0

        return {
            "bulundu": bool(bulunan),
            "toplam_bulgu": len(bulunan),
            "ortalama_risk": ortalama_risk,
            "riskli_bulgu_sayisi": sum(1 for bulgu in bulunan if bulgu["risk_puani"] >= 3),
            "dusuk_risk_sayisi": sum(1 for bulgu in bulunan if bulgu["risk_puani"] < 3),
            "temalar": tema_sayilari,
            "bulgular": bulunan,
        }

    def _zorunlu_kalite_kontrolunu_uygula(self, sonuc: dict, metin_normalized: str) -> dict:
        """
        Rapor oncesi zorunlu kalite kapisi.

        Tema/olay orgusu bulgulari kategori raporuna tasinir; sahnelenen
        davranislar ozendirme olmasa bile Risk 0'a dusmez.
        """
        sonuc.setdefault("kategori_bulgulari", {})
        self.tema_bulgularini_kanit_kontroluyle_temizle(sonuc)
        tema_analizi = sonuc.setdefault("tema_olay_orgusu_bulgulari", {})
        tema_bulgulari = tema_analizi.get("bulgular", []) or []

        eklenenler = self._zorunlu_tema_bulgularini_kategorilere_tasi(sonuc, tema_bulgulari)
        temizlenen_risk0 = self._risk_0_kurallarini_uygula(sonuc)
        self._final_skoru_kalite_kontrolune_gore_duzelt(sonuc)
        tutarsizliklar = self._zorunlu_tutarlilik_sorunlarini_bul(sonuc)
        metin_kalite_sorunlari = collect_text_quality_issues(sonuc, path="analiz_sonucu")
        gorsel_ozet = (sonuc.get("gorsel_tarama") or (sonuc.get("metadata") or {}).get("gorsel_ozet") or {})
        visual_pages = int(gorsel_ozet.get("visual_pages", len(gorsel_ozet.get("gorselli_sayfalar", []) or [])) or 0)
        visual_analysis_count = int(
            gorsel_ozet.get(
                "visual_analysis_count",
                gorsel_ozet.get("analiz_edilen_gorsel_sayisi", len(gorsel_ozet.get("gorsel_analizleri", []) or []))
            ) or 0
        )
        gorsel_analiz_eksik = visual_pages > 0 and visual_analysis_count == 0
        gorunen_temalar = {bulgu.get("tema_adi") for bulgu in tema_bulgulari if bulgu.get("tema_adi")}
        zorunlu_temalar = gorunen_temalar & ZORUNLU_TEMA_LISTESI

        kategori_bulgulari = sonuc.get("kategori_bulgulari", {})
        eksik_tema_bulgulari = [
            bulgu for bulgu in tema_bulgulari
            if not self._tema_bulgusu_kategoride_var_mi(bulgu, kategori_bulgulari)
        ]
        tum_bulgular = [
            bulgu
            for kategori_data in kategori_bulgulari.values()
            for bulgu in kategori_data.get("bulunan_kelimeler", [])
        ]
        risk0_bulgular = [bulgu for bulgu in tum_bulgular if self._risk_puani_al(bulgu) <= 0]
        pozitif_riskli_bulgular = [bulgu for bulgu in tum_bulgular if self._risk_puani_al(bulgu) > 0]
        zararli_sahneler = [
            bulgu for bulgu in tema_bulgulari
            if bulgu.get("kategori") == "zararlı_alışkanlıklar" and self._risk_puani_al(bulgu) > 0
        ]
        romantik_sahneler = [
            bulgu for bulgu in tema_bulgulari
            if bulgu.get("kategori") == "cinsellik_mahremiyet"
            and bulgu.get("tema_adi") in {"Romantik ilgi", "Flört", "Öpüşme", "Evlilik dışı ilişki"}
        ]

        zararli_kayit_var = any(
            self._risk_puani_al(bulgu) > 0
            for bulgu in kategori_bulgulari.get("zararlı_alışkanlıklar", {}).get("bulunan_kelimeler", [])
        )
        romantik_kayit_var = any(
            self._risk_puani_al(bulgu) > 0
            for bulgu in kategori_bulgulari.get("cinsellik_mahremiyet", {}).get("bulunan_kelimeler", [])
        )

        eksikler = []
        for bulgu in eksik_tema_bulgulari[:10]:
            eksikler.append(
                "Tema analizi bulgusu kategori raporuna taşınmadı: %s / sayfa %s"
                % (bulgu.get("tema_adi", "Tema"), bulgu.get("sayfa", "?"))
            )
        if zararli_sahneler and not zararli_kayit_var:
            eksikler.append("Zararlı alışkanlık sahnesi var ancak kategori bulgusu yok.")
        if romantik_sahneler and not romantik_kayit_var:
            eksikler.append("Romantik içerik teması var ancak rapor kategorisinde görünmüyor.")
        if gorsel_analiz_eksik:
            eksikler.append("Görsel içerik analizi eksik yapıldı")

        ozel_sozluk_validasyon = (sonuc.get("ozel_sozluk") or {}).get("validation") or {}
        if ozel_sozluk_validasyon.get("duplicates"):
            eksikler.append("Özel sözlükte aynı kelime birden fazla kategoride tanımlanmış.")
        if ozel_sozluk_validasyon.get("invalid_regex"):
            eksikler.append("Özel sözlükte geçersiz regex tanımı var.")

        tum_onemli_olaylar_temsil_edildi = bool(zorunlu_temalar or tema_bulgulari or any(
            data.get("toplam_bulgu", 0) > 0 for data in kategori_bulgulari.values()
        ))
        rapor_olusturulabilir = not eksikler and not tutarsizliklar
        utf8_bozuk_mu = bool(sonuc.get("encoding_bozuk_input") or looks_mojibake(metin_normalized) or metin_kalite_sorunlari)
        risk0_sonuca_tasindi_mi = bool(risk0_bulgular) and not pozitif_riskli_bulgular and float(sonuc.get("final_skor", 0) or 0) > 0
        sonuc_bulgularla_tutarsiz_mi = (
            (not pozitif_riskli_bulgular and float(sonuc.get("final_skor", 0) or 0) > 0)
            or (pozitif_riskli_bulgular and float(sonuc.get("final_skor", 0) or 0) <= 0)
        )
        son_kalite_sorunlari = {
            "ayni_bulgu_iki_farkli_karar_aldi_mi": bool(tutarsizliklar),
            "risk_0_bulgular_sonuca_tasindi_mi": risk0_sonuca_tasindi_mi,
            "sigara_kullanimi_eksik_mi": any(b.get("tema_adi") == "Sigara kullanımı" for b in tema_bulgulari) and not zararli_kayit_var,
            "alkol_veya_sarhosluk_eksik_mi": any(b.get("tema_adi") in {"Alkol kullanımı", "Sarhoşluk"} for b in tema_bulgulari) and not zararli_kayit_var,
            "kavga_veya_siddet_sahneleri_eksik_mi": any(b.get("tema_adi") in {"Kavga", "Dövüş", "Şiddet", "Şiddet eğilimi"} for b in tema_bulgulari) and not any(self._risk_puani_al(b) > 0 for b in kategori_bulgulari.get("siddet_suc", {}).get("bulunan_kelimeler", [])),
            "romantik_icerikler_eksik_mi": bool(romantik_sahneler) and not romantik_kayit_var,
            "tema_analizi_olusturulmadi_mi": tema_analizi.get("bulundu") is not True and bool(zorunlu_temalar),
            "fiil_nesne_analizi_eksik_mi": False,
            "tekrarlayan_kayitlar_var_mi": False,
            "utf8_karakter_bozulmasi_var_mi": utf8_bozuk_mu,
            "riskli_alinti_eksik_mi": self._riskli_alinti_eksik_mi(sonuc),
            "tekrar_eden_tema_yanlis_siniflanmis_mi": bool(tutarsizliklar),
            "romantik_ilgi_yanlis_pozitif_mi": self._romantik_yanlis_pozitif_var_mi(sonuc),
            "risk_aciklamasi_puanla_uyumsuz_mu": self._risk_aciklamasi_puanla_uyumsuz_mu(sonuc),
            "puanlama_formulu_sonuc_tutarsiz_mi": self._puanlama_formulu_tutarsiz_mi(sonuc),
            "meb_tablosu_formulle_tutarsiz_mi": self._meb_tablosu_formulle_tutarsiz_mi(sonuc),
            "risk_puani_karar_esigiyle_uyumsuz_mu": self._karar_esigiyle_uyumsuz_mu(sonuc),
            "ayni_tema_gereksiz_iki_kez_cezalandirilmis_mi": self._tekrar_tema_cifte_ceza_var_mi(sonuc),
            "riskli_kriterler_ana_tabloda_eksik_mi": self._riskli_meb_kriteri_tabloda_eksik_mi(sonuc),
            "kategori_tema_eslesmesi_hatali_mi": bool(eksik_tema_bulgulari),
            "gorsel_icerik_analizi_eksik_mi": gorsel_analiz_eksik,
            "ozel_sozluk_cakismasi_var_mi": bool(ozel_sozluk_validasyon.get("duplicates")),
            "ozel_sozluk_regex_hatasi_var_mi": bool(ozel_sozluk_validasyon.get("invalid_regex")),
            "sonuc_bulgularla_tutarsiz_mi": sonuc_bulgularla_tutarsiz_mi,
            "sonuc_metni_risk_seviyesiyle_celisiyor_mu": self._sonuc_metni_riskle_celisiyor_mu(sonuc),
        }
        raporu_durduran_sorunlar = {
            anahtar: deger
            for anahtar, deger in son_kalite_sorunlari.items()
        }
        yeniden_olusturma_gerekli = any(raporu_durduran_sorunlar.values()) or bool(eksikler)

        sonuc["zorunlu_kalite_kontrolu"] = {
            "uygulandi": True,
            "rapor_olusturulabilir": rapor_olusturulabilir and not yeniden_olusturma_gerekli,
            "tema_kontrolu": {
                "aranan_temalar": sorted(ZORUNLU_TEMA_LISTESI),
                "tespit_edilen_zorunlu_temalar": sorted(zorunlu_temalar),
                "tema_raporda_gorunuyor_mu": not eksik_tema_bulgulari,
                "kategoriye_tasinmayan_tema_sayisi": len(eksik_tema_bulgulari),
            },
            "davranis_sahnelenmesi_denetimi": {
                "risk_0_olamaz": sorted(ZORUNLU_DAVRANIS_TEMALARI),
                "kategoriye_tasinan_bulgu_sayisi": eklenenler,
            },
            "risk_0_kurali": {
                "uygulandi": True,
                "uyari_revizyon_temizlenen_bulgu_sayisi": temizlenen_risk0,
                "sonuca_tasindi_mi": risk0_sonuca_tasindi_mi,
            },
            "tutarlilik_denetimi": {
                "celiski_var_mi": bool(tutarsizliklar),
                "celiskiler": tutarsizliklar,
            },
            "zararli_aliskanlik_denetimi": {
                "sahne_var_mi": bool(zararli_sahneler),
                "kategori_kaydi_var_mi": zararli_kayit_var,
            },
            "romantik_icerik_denetimi": {
                "tema_var_mi": bool(romantik_sahneler),
                "kategori_kaydi_var_mi": romantik_kayit_var,
            },
            "gorsel_icerik_analizi": {
                "gorsel_var_mi": visual_pages > 0,
                "analiz_edilen_gorsel_sayisi": visual_analysis_count,
                "analiz_motoru_calisti_mi": not gorsel_analiz_eksik,
                "uyari": "Görsel içerik analizi eksik yapıldı" if gorsel_analiz_eksik else "",
            },
            "son_rapor_dogrulama_sorusu": "Kitapta geçen tüm önemli olaylar raporda temsil edildi mi?",
            "son_rapor_dogrulama_cevabi": "EVET" if rapor_olusturulabilir and not yeniden_olusturma_gerekli and tum_onemli_olaylar_temsil_edildi and not gorsel_analiz_eksik else "HAYIR",
            "son_kalite_kontrol_sorulari": son_kalite_sorunlari,
            "yeniden_olusturma_gerekli_mi": yeniden_olusturma_gerekli,
            "eksikler": eksikler,
            "rapor_durumu": "Eksik Analiz" if gorsel_analiz_eksik else sonuc.get("rapor_durumu"),
            "quality_check": "FAIL" if gorsel_analiz_eksik else "PASS",
            "all_events_represented": False if gorsel_analiz_eksik else tum_onemli_olaylar_temsil_edildi,
        }
        tutarlilik = self.consistency_assert(sonuc, raise_on_error=False)
        sonuc["zorunlu_kalite_kontrolu"]["consistency_assert"] = tutarlilik
        if not tutarlilik["gecti"]:
            sonuc["zorunlu_kalite_kontrolu"]["rapor_olusturulabilir"] = False
            sonuc["zorunlu_kalite_kontrolu"]["son_rapor_dogrulama_cevabi"] = "HAYIR"
            sonuc["zorunlu_kalite_kontrolu"]["yeniden_olusturma_gerekli_mi"] = True
            sonuc["zorunlu_kalite_kontrolu"].setdefault("eksikler", []).extend(tutarlilik["hatalar"])
        return sonuc

    def _riskli_alinti_eksik_mi(self, sonuc: dict) -> bool:
        for kategori_data in (sonuc.get("kategori_bulgulari", {}) or {}).values():
            for bulgu in kategori_data.get("bulunan_kelimeler", []) or []:
                if self._risk_puani_al(bulgu) <= 0:
                    continue
                alinti = repair_mojibake(
                    bulgu.get("alinti")
                    or bulgu.get("alıntı")
                    or bulgu.get("quote")
                    or bulgu.get("cumle")
                    or bulgu.get("kontext")
                    or ""
                ).strip()
                if not alinti:
                    return True
        meb_eval = sonuc.get("meb_degerlendirmesi", {}) or {}
        for bulgular in (meb_eval.get("meb_bulgulari", {}) or {}).values():
            if isinstance(bulgular, dict):
                bulgular = [bulgular]
            for bulgu in bulgular or []:
                if not isinstance(bulgu, dict) or self._risk_puani_al(bulgu) <= 0:
                    continue
                alinti = repair_mojibake(
                    bulgu.get("alinti")
                    or bulgu.get("alıntı")
                    or bulgu.get("alininti")
                    or bulgu.get("quote")
                    or bulgu.get("cumle")
                    or ""
                ).strip()
                if not alinti:
                    return True
        return False

    def _puanlama_formulu_tutarsiz_mi(self, sonuc: dict) -> bool:
        puanlama = ((sonuc.get("meb_degerlendirmesi") or {}).get("puanlama_detayi") or {})
        if puanlama:
            cezalar = puanlama.get("kriter_cezalari") or {}
            beklenen_ceza = sum(
                float((detay or {}).get("puan_cezasi", 0) or 0)
                for detay in cezalar.values()
                if isinstance(detay, dict)
            )
            toplam_ceza = float(puanlama.get("toplam_ceza", beklenen_ceza) or 0)
            baslangic = float(puanlama.get("baslangic_puani", 100) or 100)
            meb_puani = float(((sonuc.get("meb_degerlendirmesi") or {}).get("meb_puani", baslangic - toplam_ceza)) or 0)
            if abs(beklenen_ceza - toplam_ceza) > 0.01:
                return True
            if abs(max(0.0, baslangic - toplam_ceza) - meb_puani) > 0.01:
                return True
        risk_formulu = sonuc.get("risk_hesaplama_formulu") or {}
        if risk_formulu:
            toplam = float(risk_formulu.get("toplam", sonuc.get("final_skor", 0)) or 0)
            final = float(sonuc.get("final_skor", toplam) or 0)
            if abs(toplam - final) > 0.01:
                return True
        return False

    def _meb_tablosu_formulle_tutarsiz_mi(self, sonuc: dict) -> bool:
        meb_eval = sonuc.get("meb_degerlendirmesi") or {}
        puanlama = meb_eval.get("puanlama_detayi") or {}
        if not puanlama:
            return False
        kriterler = meb_eval.get("meb_kriterler") or {}
        cezalar = puanlama.get("kriter_cezalari") or {}
        formul_toplam = round(float(puanlama.get("toplam_ceza", 0) or 0), 2)
        detay_toplam = round(sum(
            float((detay or {}).get("puan_cezasi", 0) or 0)
            for detay in cezalar.values()
            if isinstance(detay, dict)
        ), 2)
        tablo_toplam = round(sum(
            float((kriter or {}).get("puan_cezasi", 0) or 0)
            for kriter in kriterler.values()
            if isinstance(kriter, dict)
        ), 2)
        if abs(detay_toplam - formul_toplam) > 0.01 or abs(tablo_toplam - formul_toplam) > 0.01:
            return True
        for kriter_key, detay in cezalar.items():
            if not isinstance(detay, dict):
                continue
            detay_ceza = float(detay.get("puan_cezasi", 0) or 0)
            detay_risk = float(detay.get("risk", 0) or 0)
            satir = kriterler.get(kriter_key) or {}
            if detay_ceza > 0 and (
                float(satir.get("puan_cezasi", 0) or 0) <= 0
                or float(satir.get("risk", 0) or 0) <= 0
            ):
                return True
            if abs(float(satir.get("puan_cezasi", 0) or 0) - detay_ceza) > 0.01:
                return True
            if detay_risk > 0 and float(satir.get("risk", 0) or 0) <= 0:
                return True
        return False

    def _karar_esigiyle_uyumsuz_mu(self, sonuc: dict) -> bool:
        final_skor = float(sonuc.get("final_skor", 0) or 0)
        if final_skor < 50:
            beklenen = "uygun"
        elif final_skor < 70:
            beklenen = "inceleme"
        else:
            beklenen = "uygun değil"
        karar = sonuc.get("karar") or {}
        metin = repair_mojibake(" ".join(str(karar.get(alan, "") or "").lower() for alan in ("seviye", "aciklama")))
        metin = metin.replace("i̇", "i")
        if not metin:
            return False
        if beklenen == "uygun" and "uygun" in metin and "uygun de" not in metin:
            return False
        if beklenen == "inceleme" and ("inceleme" in metin or "editoryal" in metin):
            return False
        if beklenen == "uygun değil" and ("uygun değil" in metin or "uygun degil" in metin):
            return False
        return True

    def _tekrar_tema_cifte_ceza_var_mi(self, sonuc: dict) -> bool:
        kural = sonuc.get("zararli_aliskanlik_skor_kurali") or {}
        return bool(kural.get("tema_tekrar_yogunlugu_var") and kural.get("tekrar_katsayisi_uygulandi"))

    def _riskli_meb_kriteri_tabloda_eksik_mi(self, sonuc: dict) -> bool:
        meb_eval = sonuc.get("meb_degerlendirmesi") or {}
        kriterler = meb_eval.get("meb_kriterler") or {}
        cezalar = ((meb_eval.get("puanlama_detayi") or {}).get("kriter_cezalari") or {})
        for kriter_key, detay in cezalar.items():
            if not isinstance(detay, dict) or float(detay.get("puan_cezasi", 0) or 0) <= 0:
                continue
            satir = kriterler.get(kriter_key) or {}
            if float(satir.get("puan_cezasi", 0) or 0) <= 0 or float(satir.get("risk", 0) or 0) <= 0:
                return True
        return False

    def _romantik_yanlis_pozitif_var_mi(self, sonuc: dict) -> bool:
        bulgular = (
            (sonuc.get("kategori_bulgulari", {}) or {})
            .get("cinsellik_mahremiyet", {})
            .get("bulunan_kelimeler", [])
            or []
        )
        for bulgu in bulgular:
            if self._risk_puani_al(bulgu) <= 0:
                continue
            tema = str(bulgu.get("tema_adi") or bulgu.get("kelime") or "").strip().lower()
            if tema != "romantik ilgi":
                continue
            metin = " ".join(
                str(bulgu.get(alan, "") or "")
                for alan in ("cumle", "alinti", "alıntı", "kontext", "baglam", "gerekce")
            )
            if not self._romantik_ilgi_kaniti_var_mi(metin):
                return True
        return False

    def _risk_aciklamasi_puanla_uyumsuz_mu(self, sonuc: dict) -> bool:
        for kategori_data in (sonuc.get("kategori_bulgulari", {}) or {}).values():
            for bulgu in kategori_data.get("bulunan_kelimeler", []) or []:
                risk = self._risk_puani_al(bulgu)
                karar = str(bulgu.get("nihaiKarar") or bulgu.get("kararSinifi") or "").lower()
                if risk >= 3 and re.search(r"\b(?:temiz|uygun|d[üu]ş[üu]k\s+risk|dusuk\s+risk|risk\s*0)\b", karar):
                    return True
                if risk <= 0 and re.search(r"\b(?:riskli|y[üu]ksek\s+risk|uygun\s+de[ğg]il)\b", karar):
                    return True
        return False

    def _sonuc_metni_riskle_celisiyor_mu(self, sonuc: dict) -> bool:
        final_skor = float(sonuc.get("final_skor", 0) or 0)
        karar = sonuc.get("karar") or {}
        metin = " ".join(str(karar.get(alan, "") or "").lower() for alan in ("seviye", "renk", "aciklama"))
        if final_skor >= 70 and re.search(r"\buygun(?:dur)?\b", metin) and "uygun de" not in metin:
            return True
        if final_skor < 50 and re.search(r"\b(?:riskli|uygun\s+de[ğg]il|revizyon)\b", metin):
            return True
        return False

    def tema_bulgularini_kanit_kontroluyle_temizle(self, sonuc: dict) -> dict:
        """
        Eski/cache analiz sonucundaki tema bulgularini PDF oncesi yeniden kanitlar.

        KANIT_KONTROLU 0.70 altinda kalan temalar hem tema tablosundan hem de
        kategoriye tasinmis tema kopyalarindan temizlenir.
        """
        tema_analizi = sonuc.setdefault("tema_olay_orgusu_bulgulari", {})
        tema_bulgulari = tema_analizi.get("bulgular", []) or []
        if not tema_bulgulari:
            return sonuc

        kalanlar = []
        reddedilen_anahtarlar = set()
        for tema_bulgu in tema_bulgulari:
            tema_adi = str(tema_bulgu.get("tema_adi", "") or "").strip()
            cumle = str(
                tema_bulgu.get("cumle")
                or tema_bulgu.get("alinti")
                or tema_bulgu.get("alıntı")
                or ""
            )
            kural = self._tema_kuralini_bul(tema_adi)
            kanit = self._tema_kanit_kontrolu(kural or tema_bulgu, cumle)
            anahtar = self._tema_bulgu_temizleme_anahtari(tema_bulgu)
            if kanit["kanitPuani"] < 0.70:
                reddedilen_anahtarlar.add(anahtar)
                continue
            tema_bulgu["kanitPuani"] = kanit["kanitPuani"]
            tema_bulgu["kararGuveni"] = kanit["kanitPuani"]
            tema_bulgu["kanitKontrolu"] = kanit
            kalanlar.append(tema_bulgu)

        if len(kalanlar) == len(tema_bulgulari):
            return sonuc

        tema_analizi["bulgular"] = kalanlar
        tema_analizi["bulundu"] = bool(kalanlar)
        tema_analizi["toplam_bulgu"] = len(kalanlar)
        tema_analizi["riskli_bulgu_sayisi"] = sum(1 for bulgu in kalanlar if self._risk_puani_al(bulgu) >= 3)
        tema_analizi["dusuk_risk_sayisi"] = sum(1 for bulgu in kalanlar if 0 < self._risk_puani_al(bulgu) < 3)
        toplam_risk = sum(self._risk_puani_al(bulgu) for bulgu in kalanlar)
        tema_analizi["ortalama_risk"] = round(toplam_risk / len(kalanlar), 2) if kalanlar else 0
        tema_sayilari = {}
        for bulgu in kalanlar:
            tema = bulgu.get("tema_adi")
            if tema:
                tema_sayilari[tema] = tema_sayilari.get(tema, 0) + 1
        tema_analizi["temalar"] = tema_sayilari

        for kategori_data in (sonuc.get("kategori_bulgulari", {}) or {}).values():
            yeni_bulgular = []
            for bulgu in kategori_data.get("bulunan_kelimeler", []) or []:
                kaynak = str(bulgu.get("kaynak", "") or "").lower()
                tema_kopyasi = (
                    "tema" in kaynak
                    or bulgu.get("tema_adi")
                    or str(bulgu.get("baglamTipi", "") or "") == "tema_olay_orgusu"
                )
                if tema_kopyasi and self._tema_bulgu_temizleme_anahtari(bulgu) in reddedilen_anahtarlar:
                    continue
                yeni_bulgular.append(bulgu)
            kategori_data["bulunan_kelimeler"] = yeni_bulgular
            self._kategori_ozetini_yenile(kategori_data)

        self._skoru_bulgulardan_yeniden_hesapla(sonuc)
        return sonuc

    def _tema_bulgu_temizleme_anahtari(self, bulgu: dict) -> tuple:
        tema = str(bulgu.get("tema_adi", "") or bulgu.get("kelime", "") or "").strip().lower()
        sayfa = str(bulgu.get("sayfa", "") or "")
        cumle = str(
            bulgu.get("cumle")
            or bulgu.get("alinti")
            or bulgu.get("alıntı")
            or bulgu.get("kontext")
            or ""
        ).strip().lower()
        return tema, sayfa, re.sub(r"\s+", " ", cumle)[:220]

    def _skoru_bulgulardan_yeniden_hesapla(self, sonuc: dict) -> None:
        pozitif_riskler = [
            self._risk_puani_al(bulgu)
            for kategori_data in (sonuc.get("kategori_bulgulari", {}) or {}).values()
            for bulgu in kategori_data.get("bulunan_kelimeler", []) or []
            if self._risk_puani_al(bulgu) > 0
        ]
        if not pozitif_riskler:
            sonuc["final_skor"] = 0.0
            sonuc["ortalama_risk"] = 0
            if isinstance(sonuc.get("karar"), dict):
                sonuc["karar"]["seviye"] = "Uygun"
                sonuc["karar"]["renk"] = "green"
            return

        sonuc["ortalama_risk"] = round(sum(pozitif_riskler) / len(pozitif_riskler), 2)
        sonuc["final_skor"] = round(min(100, max(0, sonuc["ortalama_risk"] * 20)), 2)
        self._zararli_aliskanlik_skor_kuralini_uygula(sonuc)

    def _zararli_aliskanlik_ozeti(self, sonuc: dict) -> dict:
        tema_bulgulari = (sonuc.get("tema_olay_orgusu_bulgulari", {}) or {}).get("bulgular", []) or []
        kategori_bulgulari = sonuc.get("kategori_bulgulari", {}) or {}
        tum_kayitlar = list(tema_bulgulari)
        for kategori_data in kategori_bulgulari.values():
            tum_kayitlar.extend(kategori_data.get("bulunan_kelimeler", []) or [])
        sayim_kayitlari = tema_bulgulari if tema_bulgulari else tum_kayitlar

        def metin(bulgu: dict) -> str:
            return " ".join(
                str(bulgu.get(alan, "") or "").lower()
                for alan in ("tema_adi", "kelime", "cumle", "alinti", "alıntı", "kontext", "baglamTipi")
            )

        def benzersiz_say(kosul) -> int:
            anahtarlar = set()
            for bulgu in sayim_kayitlari:
                if self._risk_puani_al(bulgu) <= 0 or not kosul(bulgu):
                    continue
                anahtarlar.add((
                    str(bulgu.get("tema_adi") or bulgu.get("kelime") or "").lower(),
                    str(bulgu.get("sayfa", "") or ""),
                    re.sub(r"\s+", " ", metin(bulgu))[:220],
                ))
            return len(anahtarlar)

        sigara = any(
            self._risk_puani_al(bulgu) > 0
            and ("sigara kullanımı" in metin(bulgu) or re.search(r"\bsigara|puro|tütün|tutun|nargile\b", metin(bulgu)))
            for bulgu in tum_kayitlar
        )
        sarhosluk = any(
            self._risk_puani_al(bulgu) > 0
            and ("sarhoşluk" in metin(bulgu) or re.search(r"\bsarhoş|sarhos|alkol etkisi|sendele", metin(bulgu)))
            for bulgu in tum_kayitlar
        )
        alkol = any(
            self._risk_puani_al(bulgu) > 0
            and ("alkol kullanımı" in metin(bulgu) or re.search(r"\balkol|içki|icki|şarap|sarap|rakı|raki|bira|viski|votka|kadeh|meyhane\b", metin(bulgu)))
            for bulgu in tum_kayitlar
        )
        sigara_sayisi = benzersiz_say(lambda bulgu: "sigara kullanımı" in metin(bulgu) or re.search(r"\bsigara|puro|tütün|tutun|nargile\b", metin(bulgu)))
        sarhosluk_sayisi = benzersiz_say(lambda bulgu: "sarhoşluk" in metin(bulgu) or re.search(r"\bsarhoş|sarhos|alkol etkisi|sendele", metin(bulgu)))
        alkol_sayisi = benzersiz_say(lambda bulgu: "alkol kullanımı" in metin(bulgu) or re.search(r"\balkol|içki|icki|şarap|sarap|rakı|raki|bira|viski|votka|kadeh|meyhane\b", metin(bulgu)))
        tema_sahne_sayilari = {
            "sigara": sigara_sayisi,
            "sarhosluk": sarhosluk_sayisi,
            "alkol": alkol_sayisi,
        }
        tekrar_eden_temalar = {
            tema: sayi
            for tema, sayi in tema_sahne_sayilari.items()
            if sayi > 1
        }
        toplam_zararli_sahne = max(sigara_sayisi + sarhosluk_sayisi + alkol_sayisi, 1 if (sigara or sarhosluk or alkol) else 0)
        benzersiz_tema_sayisi = sum(1 for var_mi in (sigara, sarhosluk, alkol) if var_mi)
        tema_yogunlugu = benzersiz_tema_sayisi >= 2
        tekrar_esigi_asildi = toplam_zararli_sahne >= 4 and benzersiz_tema_sayisi >= 2
        tekrar_katsayisi = False
        davranis_normalizasyonu = any(
            self._risk_puani_al(bulgu) > 0
            and (
                bulgu.get("davranisNormalizasyonu") is True
                or str(bulgu.get("baglamTipi", "") or "") == "davranis_normalizasyonu"
                or self._zararli_aliskanlik_normalizasyonu_var_mi(metin(bulgu))
            )
            for bulgu in tum_kayitlar
        )
        yas_band = self._yas_grubu_bandini_bul(sonuc.get("yas_grubu", "6-12"))
        return {
            "sigara_var": sigara,
            "sarhosluk_var": sarhosluk,
            "alkol_var": alkol,
            "zararli_aliskanlik_sahnesi_var": sigara or sarhosluk or alkol,
            "sigara_ve_sarhosluk_var": sigara and sarhosluk,
            "sigara_sahne_sayisi": sigara_sayisi,
            "sarhosluk_sahne_sayisi": sarhosluk_sayisi,
            "alkol_sahne_sayisi": alkol_sayisi,
            "toplam_zararli_sahne_sayisi": toplam_zararli_sahne,
            "benzersiz_zararli_tema_sayisi": benzersiz_tema_sayisi,
            "tema_sahne_sayilari": tema_sahne_sayilari,
            "tekrar_eden_temalar": tekrar_eden_temalar,
            "tema_tekrar_yogunlugu_var": bool(tekrar_eden_temalar),
            "tema_yogunlugu_katsayisi_uygulandi": tema_yogunlugu,
            "tekrar_katsayisi_uygulandi": tekrar_katsayisi,
            "tekrar_esigi_asildi": tekrar_esigi_asildi,
            "tekrar_katsayisi_notu": (
                "Tekrar eden referanslar yoğunluk açıklamasında izlenir; ayrı puan çarpanı üretmez."
                if (tekrar_eden_temalar or tekrar_esigi_asildi) else
                ""
            ),
            "mukerrer_olay_ayrimi": "Aynı tema/karakter devamı olan tekrarlar ayrı katsayı üretmez; farklı zararlı temalar yoğunluk katsayısı üretir.",
            "davranis_normalizasyonu_var": davranis_normalizasyonu,
            "yas_band": yas_band,
            "yas_katsayisi_uygulandi": yas_band in {"cocuk_erken", "cocuk", "ergen_erken"},
        }

    def _zararli_aliskanlik_skor_kuralini_uygula(self, sonuc: dict) -> None:
        ozet = self._zararli_aliskanlik_ozeti(sonuc)
        if not ozet["zararli_aliskanlik_sahnesi_var"]:
            return

        mevcut = float(sonuc.get("final_skor", 0) or 0)
        uygulanan_carpan = 1.0
        if ozet["sigara_ve_sarhosluk_var"]:
            mevcut *= 1.35
            uygulanan_carpan = 1.35
        if ozet.get("tema_yogunlugu_katsayisi_uygulandi"):
            mevcut *= 1.10
            uygulanan_carpan = round(uygulanan_carpan * 1.10, 2)
        if ozet.get("tema_tekrar_yogunlugu_var") or ozet.get("tekrar_katsayisi_uygulandi"):
            ozet["tekrar_katsayisi_notu"] = "Tekrar eden referanslar yoğunluk açıklamasında izlenir; ayrı puan çarpanı üretmez."
        if ozet.get("davranis_normalizasyonu_var"):
            mevcut *= 1.10
            uygulanan_carpan = round(uygulanan_carpan * 1.10, 2)
        if ozet.get("yas_katsayisi_uygulandi"):
            mevcut *= 1.10
            uygulanan_carpan = round(uygulanan_carpan * 1.10, 2)

        minimum = 40.0 if ozet["sigara_ve_sarhosluk_var"] else 30.0
        if ozet["sigara_ve_sarhosluk_var"] and ozet.get("tema_yogunlugu_katsayisi_uygulandi"):
            minimum += 5.0
        if ozet.get("tema_tekrar_yogunlugu_var"):
            minimum += 5.0
        if ozet.get("davranis_normalizasyonu_var"):
            minimum += 10.0
        if ozet.get("yas_katsayisi_uygulandi"):
            minimum += 5.0
        minimum = min(69.0, minimum)
        tavan = 69.0 if (
            ozet["sigara_ve_sarhosluk_var"]
            and ozet.get("tema_yogunlugu_katsayisi_uygulandi")
            and ozet.get("davranis_normalizasyonu_var")
            and ozet.get("yas_katsayisi_uygulandi")
        ) else 100.0
        sonuc["final_skor"] = round(min(tavan, max(mevcut, minimum)), 2)
        sonuc["ortalama_risk"] = round(sonuc["final_skor"] / 20, 2)
        if isinstance(sonuc.get("risk_hesaplama_formulu"), dict):
            sonuc["risk_hesaplama_formulu"]["toplam"] = sonuc["final_skor"]
            sonuc["risk_hesaplama_formulu"]["ortalama_risk"] = sonuc["ortalama_risk"]
        sonuc["zararli_aliskanlik_skor_kurali"] = {
            **ozet,
            "minimum_genel_risk": minimum,
            "zararli_aliskanlik_carpani": uygulanan_carpan,
            "uygulandi": True,
        }

        if isinstance(sonuc.get("karar"), dict):
            sonuc["karar"]["seviye"] = "EDİTORYAL İNCELEME GEREKLİ"
            sonuc["karar"]["renk"] = "orange"

    def consistency_assert(self, sonuc: dict, raise_on_error: bool = True) -> dict:
        self._debug_log(
            "[evaluator_maarif.consistency_assert] START "
            f"file={__file__} cwd={os.getcwd()} python={sys.executable}"
        )
        hatalar = []
        kategori_bulgulari = sonuc.get("kategori_bulgulari", {}) or {}
        tema_bulgulari = (sonuc.get("tema_olay_orgusu_bulgulari", {}) or {}).get("bulgular", []) or []

        tum_bulgular = []
        pozitif_kelime_anahtarlari = set()
        risk0_kelime_anahtarlari = set()
        pozitif_sade_kelimeler = set()
        risk0_sade_kelimeler = set()

        for kategori, kategori_data in kategori_bulgulari.items():
            bulgular = kategori_data.get("bulunan_kelimeler", []) or []
            riskli = dusuk = risk0 = insan = 0
            for bulgu in bulgular:
                tum_bulgular.append((kategori, bulgu))
                risk = self._risk_puani_al(bulgu)
                if risk > 0:
                    pozitif_kelime_anahtarlari.add(self._bulgu_kelime_anahtari(bulgu, kategori))
                    pozitif_sade_kelimeler.add(self._bulgu_sade_kelime_anahtari(bulgu))
                    if risk >= 3:
                        riskli += 1
                    else:
                        dusuk += 1
                else:
                    risk0 += 1
                    risk0_kelime_anahtarlari.add(self._bulgu_kelime_anahtari(bulgu, kategori))
                    risk0_sade_kelimeler.add(self._bulgu_sade_kelime_anahtari(bulgu))
                if str(bulgu.get("kararSinifi", "")).lower() == "insan_incelemesi":
                    insan += 1

            toplam = int(kategori_data.get("toplam_bulgu", 0) or 0)
            if toplam != len(bulgular):
                hatalar.append(
                    f"Kategori toplamı liste uzunluğu ile tutarsız: {kategori} toplam={toplam}, liste={len(bulgular)}"
                )
            if int(kategori_data.get("riskli_bulgu_sayisi", 0) or 0) != riskli:
                hatalar.append(f"Riskli kayıt sayısı tutarsız: {kategori}")
            if int(kategori_data.get("dusuk_risk_sayisi", 0) or 0) != dusuk:
                hatalar.append(f"Düşük risk kayıt sayısı tutarsız: {kategori}")
            if int(kategori_data.get("temizlenen_bulgu_sayisi", 0) or 0) != risk0:
                hatalar.append(f"Risk 0 kayıt sayısı tutarsız: {kategori}")
            if toplam != riskli + dusuk + risk0:
                hatalar.append(
                    f"Kategori alt toplamları tutarsız: {kategori} toplam={toplam}, riskli+düşük+risk0={riskli + dusuk + risk0}"
                )

        cakisani = pozitif_kelime_anahtarlari & risk0_kelime_anahtarlari
        for kategori, kelime in sorted(cakisani):
            hatalar.append(f"Risk alan kayıt Risk 0 savunma listesinde de var: {kategori}/{kelime}")
        for kelime in sorted((pozitif_sade_kelimeler & risk0_sade_kelimeler) - {""}):
            hatalar.append(f"Risk alan kelime Risk 0 savunma listesinde de var: {kelime}")

        for tema_bulgu in tema_bulgulari:
            kategori = tema_bulgu.get("kategori")
            tema_adi = str(tema_bulgu.get("tema_adi", "") or "").strip().lower()
            tema_cumle = str(tema_bulgu.get("cumle", "") or tema_bulgu.get("alinti", "") or "")
            tema_kural = self._tema_kuralini_bul(tema_bulgu.get("tema_adi", ""))
            kanit_kontrolu = self._tema_kanit_kontrolu(tema_kural or tema_bulgu, tema_cumle)
            if kanit_kontrolu["kanitPuani"] < 0.70:
                hatalar.append(
                    "Tema kanıt kontrolünden geçemedi: %s / sayfa %s / kanıt=%.2f / %s"
                    % (
                        tema_bulgu.get("tema_adi", "Tema"),
                        tema_bulgu.get("sayfa", "?"),
                        kanit_kontrolu["kanitPuani"],
                        "; ".join(kanit_kontrolu.get("eksikler", [])),
                    )
                )
            if not self._tema_olay_baglami_gecerli_mi(tema_bulgu.get("tema_adi", ""), tema_cumle):
                hatalar.append(
                    "Tema yalnızca kelime eşleşmesiyle üretilmiş olabilir: %s / sayfa %s"
                    % (tema_bulgu.get("tema_adi", "Tema"), tema_bulgu.get("sayfa", "?"))
                )
            if tema_adi == "hırsızlık" and self._hirsizlik_yanlis_pozitif_mi(tema_bulgu):
                hatalar.append(
                    "Hırsızlık teması çalış*/çalım*/çalı* kaynaklı yanlış pozitif olabilir: sayfa %s"
                    % (tema_bulgu.get("sayfa", "?"))
                )
            temsil_var = self._tema_bulgusu_kategoride_var_mi(tema_bulgu, kategori_bulgulari)
            risk0_var = any(
                self._risk_puani_al(bulgu) <= 0
                and str(bulgu.get("tema_adi", "") or bulgu.get("kelime", "")).strip().lower() == tema_adi
                for bulgu in (kategori_bulgulari.get(kategori, {}) or {}).get("bulunan_kelimeler", [])
            )
            if not temsil_var and not risk0_var:
                hatalar.append(
                    "Tema bulgusu kategori veya Risk 0 raporunda temsil edilmiyor: %s / sayfa %s"
                    % (tema_bulgu.get("tema_adi", "Tema"), tema_bulgu.get("sayfa", "?"))
                )

        zararli_temalar = {"Sigara kullanımı", "Alkol kullanımı", "Sarhoşluk", "Uyuşturucu"}
        zararli_tespit = [
            bulgu for bulgu in tema_bulgulari
            if bulgu.get("tema_adi") in zararli_temalar and self._risk_puani_al(bulgu) > 0
        ]
        zararli_kategori_var = any(
            self._risk_puani_al(bulgu) > 0
            for bulgu in kategori_bulgulari.get("zararlı_alışkanlıklar", {}).get("bulunan_kelimeler", [])
        )
        if zararli_tespit and not zararli_kategori_var:
            hatalar.append("Zararlı alışkanlık davranışı tespit edildi ama Zararlı Alışkanlıklar kategorisinde görünmüyor.")

        sonuc_dict = {
            "gecti": not hatalar,
            "hatalar": hatalar,
            "sayaclar": {
                "riskli": sum(1 for _, bulgu in tum_bulgular if self._risk_puani_al(bulgu) >= 3),
                "dusuk_risk": sum(1 for _, bulgu in tum_bulgular if 0 < self._risk_puani_al(bulgu) < 3),
                "risk0": sum(1 for _, bulgu in tum_bulgular if self._risk_puani_al(bulgu) <= 0),
                "toplam": len(tum_bulgular),
            }
        }
        self._debug_log(
            "[evaluator_maarif.consistency_assert] END "
            f"gecti={sonuc_dict['gecti']} toplam={len(tum_bulgular)} "
            f"tema_bulgu={len(tema_bulgulari)} hata_sayisi={len(hatalar)} "
            f"hatalar={hatalar[:12]}"
        )
        if raise_on_error and hatalar:
            raise ValueError("Tutarlılık denetimi başarısız: " + " | ".join(hatalar))
        return sonuc_dict

    def _debug_log(self, mesaj: str) -> None:
        try:
            from datetime import datetime
            with open(os.path.abspath("debug_consistency_assert.log"), "a", encoding="utf-8") as log:
                log.write(f"{datetime.now().isoformat(timespec='seconds')} {mesaj}\n")
        except Exception:
            pass

    def _hirsizlik_yanlis_pozitif_mi(self, bulgu: dict) -> bool:
        metin = " ".join(
            str(bulgu.get(alan, "") or "").lower()
            for alan in ("kelime", "tema_adi", "cumle", "baglam", "gerekce")
        )
        izinli_calmak = re.search(
            r"\b(?:çalmak|calmak|çaldı|caldı|çalmış|calmış|çalıyor|calıyor|çalacak|calacak|"
            r"çalarken|calarken|çalınca|calınca|çalmasını|calmasını|çalmaya|calmaya|"
            r"çalmayı|calmayı|çalmak\s+mı|calmak\s+mi|çalındı|calındı|çalınmış|calınmış|"
            r"çalınan|calınan|çalınmıştı|calınmıştı)\b",
            metin,
            flags=re.IGNORECASE,
        )
        kara_liste = re.search(
            r"\b(?:çalış\w*|calış\w*|calis\w*|çalıml\w*|calıml\w*|caliml\w*|"
            r"çalım\w*|calım\w*|calim\w*|çalı(?:\b|lık\w*|kuşu\w*)|cali(?:\b|lik\w*|kusu\w*))",
            metin,
            flags=re.IGNORECASE,
        )
        return bool(kara_liste and not izinli_calmak)

    def _tema_olay_baglami_gecerli_mi(self, tema_adi: str, cumle: str) -> bool:
        tema = str(tema_adi or "").strip().lower()
        metin = re.sub(r"\s+", " ", str(cumle or "").strip().lower())
        if not metin:
            return False
        if not self._tema_formulu_saglanir_mi(tema, metin):
            return False

        if tema == "romantik ilgi":
            return self._romantik_ilgi_kaniti_var_mi(metin)

        if tema == "zorbalık":
            return self._zorbalik_kaniti_var_mi(metin)

        if tema == "flört":
            if re.search(r"\bsevgili\s+(?:eşi|esi|kocası|kocasi|karısı|karisi|hanımı|hanimi|bey(?:i)?)\b", metin):
                return False
            return bool(re.search(
                r"\b(?:flört|flort|randevu|buluş(?:tu|uyor|acak|maya|ma)|bulus(?:tu|uyor|acak|maya|ma)|"
                r"el\s+ele|sevgili(?:si|ler|ydiler|ydi)?\s+(?:ol|oldu|olmuş|olmus|oluyor|buluş|bulus|gez|görüş|gorus))\w*",
                metin,
            ) or re.search(
                r"\bsevgili(?:si|sinden|sine|siyle|ler)?\w*\b.{0,45}\b(?:ho[şs]lan|el\s+ele)\w*|"
                r"\bel\s+ele\b.{0,45}\bsevgili(?:si|sinden|sine|siyle|ler)?\w*",
                metin,
            ))

        if tema == "evlilik dışı ilişki":
            if re.search(r"\bmetresini\s+değil\b|\bmetresini\s+degil\b|\bmilimetresini\b|\bmilimetre\w*\b", metin):
                return False
            return bool(re.search(
                r"\b(?:aldat(?:tı|ti|mış|mis|ıyor|iyor|mak|ma)|yasak\s+aşk|yasak\s+ask|"
                r"evlilik\s+dışı|evlilik\s+disi|kaçamak|kacamak|metres(?:i|le|ine|ini)?\s+(?:var|vardı|vardi|görüş|gorus|buluş|bulus))\w*",
                metin,
            ))

        if tema in {"hırsızlık", "suç"}:
            if self._hirsizlik_yanlis_pozitif_mi({"cumle": metin}):
                return False
            if re.search(r"\b(?:sivil\s+polis\w*|polis\w*\s+geldi|polis\w*\s+gördükçe|polis\w*\s+gordukce|polisler\s+.*götürdükten|polisler\s+.*goturdukten)\b", metin):
                return False
            return bool(re.search(
                r"\b(?:hırsızlık|hirsizlik)\s+yap\w*|"
                r"\b(?:hırsız|hirsiz|soygun)\w*\b|"
                r"\b(?:çalmak|calmak|çaldı|caldı|çalmış|calmış|çalıyor|calıyor|çalacak|calacak|"
                r"çalarken|calarken|çalınca|calınca|çalmasını|calmasını|çalmaya|calmaya|çalmayı|calmayı|"
                r"çalmak\s+mı|calmak\s+mi|çalındı|calındı|çalınmış|calınmış|çalınan|calınan|çalınmıştı|calınmıştı)\b|"
                r"\b(?:suç|suc|kaçak|kacak|tutuklan|yakalan)\w*\b.*\b(?:çald|cald|hırsız|hirsiz|soygun|yasa\s*dışı|yasa\s*disi)\w*",
                metin,
            ))

        if tema in {"şiddet eğilimi", "şiddet", "kavga", "dövüş"}:
            if re.search(r"\b(?:yüreğimden|yuregimden|yüreğinden|yureginden|kalbimden|gönlümden|gonlumden)\b", metin):
                return False
            if re.search(
                r"\b(?:kavgal[ıi]|d[öo]v[üu][şs]l[üu]|[şs]iddetli)\b.{0,35}\bfilm(?:i|ler|leri|lerdeki)?\b"
                r"|"
                r"\bfilm(?:i|ler|leri|lerdeki)?\b.{0,35}\b(?:kavgal[ıi]|d[öo]v[üu][şs]l[üu]|[şs]iddetli)\b",
                metin,
            ):
                return False
            if re.search(
                r"\b(?:kavga|d[öo]v[üu][şs]|[şs]iddet)\w*\b.{0,35}\b(?:sev|e[ğg]len|keyif|zevk)\w*\b",
                metin,
            ):
                return True
            return bool(re.search(
                r"\b(?:yumruk|tokat|tekme)\s+(?:attı|atti|atıyor|atiyor|atmak|attılar|attilar)\b|"
                r"\b(?:vurdu|vuruyor|vuracak|vurmak|dövdü|dovdu|dövüyor|dovuyor|yaraladı|yaraladi|öldürdü|oldurdu)\b|"
                r"\b(?:kavga|dövüş|dovus)\s+(?:etti|ettiler|çıktı|cikti|başladı|basladi)\b|"
                r"\b(?:bıçak|bicak|silah|tüfek|tufek)\s+(?:çekti|cekti|salladı|salladi|kullandı|kullandi)\b",
                metin,
            ))

        if tema == "mahrem yakınlaşma":
            return bool(re.search(
                r"\b(?:dudaktan|ağzından|agzindan)\s+öp\w*|\böp(?:tü|tu|üş|us|mek|üyor|uyor)\w*\b.*\b(?:dudak|mahrem|romantik)\w*",
                metin,
            ))

        if tema in {"sigara kullanımı", "alkol kullanımı", "sarhoşluk", "uyuşturucu", "kumar"}:
            return True

        return True

    def _romantik_ilgi_kaniti_var_mi(self, metin: str) -> bool:
        metin = re.sub(r"\s+", " ", str(metin or "").strip().lower())
        tek_basina_yetersiz = re.search(
            r"\b(?:ho[şs]lan[ıi]rd[ıi]|severd[ıi]|sayard[ıi]|de[ğg]er\s+verird[ıi]|"
            r"day[ıi]|amca|abi|teyze|hala|ilk\s+a[şs][ıi]k|ilk\s+asik)\b",
            metin,
        )
        romantik_kanit = re.search(
            r"\b(?:kar[şs][ıi]l[ıi]kl[ıi]\s+(?:duygusal\s+)?yak[ıi]nl[ıi]k|"
            r"romantik\s+(?:bir\s+)?(?:[çc]ekim|duygu|yak[ıi]nl[ıi]k|ili[şs]ki)|"
            r"fl[öo]rt|sevgili|randevu|bulu[şs]ma|el\s+ele|(?:dudaktan|romantik)\s+öp)\w*\b|"
            r"\b(?:birbirlerinden|birbirlerine)\s+ho[şs]lan\w*\b|"
            r"\b(?:birbirlerini|birbirlerine)\s+sev\w*\b",
            metin,
        )
        hayranlik_ornek_alma = re.search(
            r"\b(?:hayran|hayrand[ıi]m|hayran[ıi]yd[ıi]m|onu\s+izlerdim|onu\s+izliyordum|"
            r"[öo]rnek\s+al[ıi]r|takdir\s+eder|be[ğg]enirdim|nostalji|nostaljik|"
            r"mecaz(?:i)?|sanki|gibi|film(?:ler)?deki|kitaptaki|romandaki|hikayedeki|"
            r"sahnedeki|oyundaki|karakter(?:i|le)?|rol(?:u|ünü|unu)?|platonik|hayali|"
            r"çaresiz|caresiz)\w*\b",
            metin,
        )
        hitap_memnuniyeti = re.search(
            r"\b(?:day[ıi]|amca|abi|teyze|hala)\s+deme\w*.*ho[şs]lan\w*\b|"
            r"\bho[şs]lan\w*.*(?:day[ıi]|amca|abi|teyze|hala)\s+deme\w*\b",
            metin,
        )
        if hitap_memnuniyeti:
            return False
        if re.search(
            r"\b(?:film(?:ler)?deki|kitaptaki|romandaki|hikayedeki|sahnedeki|oyundaki|"
            r"karakter(?:i|le)?|rol(?:u|ünü|unu)?|mecaz(?:i)?|sanki|gibi)\b.{0,40}"
            r"\b(?:a[Åşs][Äıi]k|â[Åşs][Äıi]k|asik)\w*\b|"
            r"\b(?:çaresiz|caresiz|platonik|hayali)\s+(?:a[Åşs][Äıi]k|â[Åşs][Äıi]k|asik)\w*\b",
            metin,
        ) and not re.search(
            r"\b(?:ondan|ona|benden|bana|senden|sana|birbirlerinden|birbirlerine)\s+ho[Åşs]lan\w*\b|"
            r"romantik\s+(?:[Ãçc]ekim|ilgi|duygu|yak[Äıi]nl[Äıi]k)|"
            r"\b(?:fl[Ãöo]rt|sevgili|randevu|el\s+ele)\w*\b",
            metin,
        ):
            return False
        if hayranlik_ornek_alma and not romantik_kanit:
            return False
        if tek_basina_yetersiz and not romantik_kanit:
            return False
        return bool(romantik_kanit)

    def _zorbalik_kaniti_var_mi(self, metin: str) -> bool:
        if re.search(r"\bkendi(?:yle|siyle)?\s+bile\s+dalga\s+ge[çc]\w*\b", metin):
            return False

        hedef = r"(?:onu|ona|onunla|arkada[şs][ıi](?:n[ıi]|yla|yle)?|[çc]ocu[ğg]u|[öo][ğg]renciyi|s[ıi]n[ıi]f arkada[şs][ıi](?:n[ıi]|yla|yle)?|karde[şs]ini)"
        asagilayici = r"(?:alay\s+et|dalga\s+ge[çc]|a[şs]a[ğg][ıi]la|k[üu][çc][üu]k\s+d[üu][şs][üu]r|lakap\s+tak|itip\s+kak)"
        hedefli_davranis = re.search(rf"\b{hedef}\b.{{0,45}}\b{asagilayici}\w*\b|\b{asagilayici}\w*\b.{{0,45}}\b{hedef}\b", metin)
        sistematik_baski = re.search(r"\b(?:s[üu]rekli|hep|her\s+g[üu]n|durmadan|tekrar\s+tekrar)\b.{0,50}\b(?:alay\s+et|dalga\s+ge[çc]|d[ıi][şs]la|a[şs]a[ğg][ıi]la|bask[ıi])\w*\b", metin)
        dislama = re.search(r"\b(?:d[ıi][şs]la|aram[ıi]za\s+alma|oyuna\s+alma|yaln[ıi]z\s+b[ıi]rak)\w*\b", metin)
        kucuk_dusurme = re.search(r"\b(?:k[üu][çc][üu]k\s+d[üu][şs][üu]r|a[şs]a[ğg][ıi]la|rezil\s+et|utand[ıi]r)\w*\b", metin)
        dogrudan_zorbalik = re.search(r"\b(?:zorbal[ıi]k|zorba)\w*\b", metin)

        return bool(hedefli_davranis or sistematik_baski or dislama or kucuk_dusurme or dogrudan_zorbalik)

    def _tema_formulu_saglanir_mi(self, tema: str, metin: str) -> bool:
        """
        Tema = anahtar kelime + ozne + fiil + gercek olay baglami.

        Turkcede ozne sikca gizli oldugu icin cekimli fiil, ozne+fiil
        birlikteligini tasiyan asgari olay isareti olarak kabul edilir.
        """
        if not metin:
            return False

        olay_fiili = self._tema_olay_fiili_var_mi(tema, metin)
        ozne_var = bool(re.search(
            r"\b(?:ben|sen|o|biz|siz|onlar|adam|kad[ıi]n|[çc]ocuk|[çc]ocuklar|"
            r"k[ıi]z|o[ğg]lan|anne|baba|abi|abla|karde[şs]|arkada[şs]|"
            r"[öo][ğg]renci|[öo][ğg]retmen|karakter|kahraman|ki[şs]i|"
            r"h[ıi]rs[ıi]z|polis|kom[şs]u|sevgili|e[şs]i|ailesi)\w*\b",
            metin,
        ))
        cekimli_fiil_var = bool(re.search(
            r"\b\w+(?:d[ıiuü]|t[ıiuü]|yor|[ıiuü]yor|acak|ecek|m[ıiuü][şs]|"
            r"m[ıiuü][şs]t[ıiuü]|[ıiuü]r|ar|er|maz|mez|mal[ıi]|meli|"
            r"ken|di|ti|du|tu|d[üu]|t[üu])\b",
            metin,
        ))

        meta_kullanim = re.search(
            r"\b(?:kelime|s[öo]zc[üu]k|terim|ifade|liste|s[öo]zl[üu]k|"
            r"anahtar\s+kelime|rapor|analiz|kategori|ba[ğg]lam|tema)\w*\b",
            metin,
        )
        if meta_kullanim and not ozne_var:
            return False

        olay_dislayici = re.search(
            r"\b(?:film|filmi|filmleri|roman|kitap|hikaye|hik[âa]ye|masal|"
            r"sahne|sahnesi|haber|haberi|oyun|oyunu)\w*\b",
            metin,
        )
        if olay_dislayici and not (ozne_var and olay_fiili):
            return False

        tema_anahtari = repair_mojibake(tema).replace("ş", "s").replace("ı", "i").replace("ö", "o").replace("ü", "u").replace("ğ", "g")
        if (
            any(anahtar in tema_anahtari for anahtar in ("kavga", "dovus", "siddet"))
            and re.search(
                r"\b(?:kavga|d[öo]v[üu][şs]|[şs]iddet)\w*\b.{0,35}\b(?:sev|e[ğg]len|keyif|zevk)\w*\b",
                metin,
            )
        ):
            return True

        return olay_fiili and (ozne_var or cekimli_fiil_var)

    def _tema_olay_fiili_var_mi(self, tema: str, metin: str) -> bool:
        tema_fiilleri = {
            "sigara kullanımı": r"\b(?:i[çc]|ic|yak|t[üu]tt[üu]r|tuttur|duman)\w*\b",
            "alkol kullanımı": r"\b(?:i[çc]|ic|yudum|doldur|sarho[şs])\w*\b",
            "sarhoşluk": r"\b(?:sarho[şs]\w*|sendele\w*|duram\w*)\b",
            "kumar": r"\b(?:oyna|kaybet|kazan|bahse\s+gir|para\s+koy)\w*\b",
            "uyuşturucu": r"\b(?:kullan|al|i[çc]|ic|sat|ta[şs][ıi]|tasi)\w*\b",
            "hırsızlık": r"\b(?:[çc]al|h[ıi]rs[ıi]zl[ıi]k\s+yap|soygun\s+yap)\w*\b",
            "suç": r"\b(?:[çc]al|ka[çc]ak|tutuklan|yakalan|su[çc]\s+i[şs]le|yasa\s*d[ıi][şs][ıi])\w*\b",
            "şiddet eğilimi": r"\b(?:sald[ıi]r|zarar\s+ver|[öo]ld[üu]r|ac[ıi]t|iste)\w*\b",
            "şiddet": r"\b(?:vur|d[öo]v|yarala|[öo]ld[üu]r|tokat|tekme|yumruk|tehdit|uygula)\w*\b",
            "kavga": r"\b(?:kavga\s+et|kavga\s+[çc][ıi]k|kavga\s+ba[şs]la|kavga\w*.{0,30}(?:sev|e[ğg]len|keyif|zevk)|sald[ıi]r|vur|ba[ğg][ıi]r)\w*\b",
            "dövüş": r"\b(?:d[öo]v|d[öo]v[üu][şs]|d[öo]v[üu][şs]\w*.{0,30}(?:sev|e[ğg]len|keyif|zevk)|bo[ğg]u[şs])\w*\b",
            "silah kullanımı": r"\b(?:[çc]ek|do[ğg]rult|ate[şs]|s[ıi]k|kullan|savur|tehdit)\w*\b",
            "aile çatışması": r"\b(?:ba[ğg][ıi]r|azarl|k[üu]s|tart[ıi][şs]|kavga|tokat|tehdit)\w*\b",
            "aile parçalanması": r"\b(?:terk|ayr[ıi]l|ya[şs]a|d[öo]nme|par[çc]alan|da[ğg][ıi]l)\w*\b",
            "boşanma": r"\b(?:bo[şs]an|ayr[ıi]l|ya[şs][ıi]yor|mahkeme)\w*\b",
            "romantik ilgi": r"\b(?:ho[şs]lan|a[şs][ıi]k|â[şs][ıi]k|asik|sevdalan|[çc]arp|duygu|ilgi)\w*\b",
            "ilk aşk": r"\b(?:a[şs][ıi]k|asik|sev|ya[şs]a)\w*\b",
            "flört": r"\b(?:fl[öo]rt|randevu|bulu[şs]|bulus|gez|g[öo]r[üu][şs]|gorus|ol|sevgili|ho[şs]lan|el\s+ele)\w*\b",
            "öpüşme": r"\b(?:[öo]p|opus|[öo]p[üu][şs])\w*\b",
            "mahrem yakınlaşma": r"\b(?:[öo]p|opus|sar[ıi]l|kucakla[şs]|yak[ıi]nla[şs])\w*\b",
            "evlilik dışı ilişki": r"\b(?:aldat|g[öo]r[üu][şs]|gorus|bulu[şs]|bulus|ka[çc]amak|ili[şs]ki)\w*\b",
            "zorbalık": r"\b(?:zorbal[ıi]k|alay\s+et|d[ıi][şs]la|a[şs]a[ğg][ıi]la|tak|itip\s+kak|dalga\s+ge[çc])\w*\b",
        }
        pattern = tema_fiilleri.get(tema)
        if pattern and re.search(pattern, metin):
            return True
        return bool(re.search(
            r"\b(?:yap|et|ol|i[çc]|ic|vur|d[öo]v|[çc]al|[öo]p|"
            r"kullan|sald[ıi]r|tehdit|tart[ıi][şs]|bo[şs]an|bulu[şs]|bulus)\w*\b",
            metin,
        ))

    def _tema_kuralini_bul(self, tema_adi: str) -> Optional[dict]:
        tema = str(tema_adi or "").strip().lower()
        for kural in TEMA_OLAY_ORGUSU_KURALLARI:
            if str(kural.get("tema_adi", "")).strip().lower() == tema:
                return kural
        return None

    def _tema_kanit_kontrolu(self, kural: dict, cumle: str) -> dict:
        """KANIT_KONTROLU(alinti, tema): 0.70 alti tema rapora alinmaz."""
        metin = re.sub(r"\s+", " ", str(cumle or "").strip().lower())
        if not metin:
            return {
                "kanitPuani": 0.0,
                "kosullar": {
                    "acik_ifade_var_mi": False,
                    "baglam_cikarilabilir_mi": False,
                    "kavram_karsiligi_var_mi": False,
                },
                "eksikler": ["Alıntı boş."],
            }

        tema = str(kural.get("tema_adi", "") or "").strip().lower()
        kategori = str(kural.get("kategori", "") or "").strip().lower()
        aciklama = " ".join(
            str(kural.get(alan, "") or "").lower()
            for alan in ("tema_adi", "kategori", "baglam", "risk_aciklamasi")
        )

        kanit_haritasi = {
            "tutun": r"\b(?:sigara|puro|t[üu]t[üu]n|tutun|nargile|[çc]akmak|k[üu]l\s+tablas[ıi])\w*\b",
            "alkol": r"\b(?:alkol|i[çc]ki|icki|[şs]arap|sarap|rak[ıi]|raki|bira|viski|votka|kadeh|meyhane|sarho[şs])\w*\b",
            "madde": r"\b(?:uyu[şs]turucu|uyusturucu|eroin|kokain|esrar|madde|ba[ğg][ıi]ml[ıi])\w*\b",
            "kumar": r"\b(?:kumar|bahis|iddia|piyango|rulet|poker|zar|iskambil)\w*\b",
            "aile": r"\b(?:aile|anne|baba|ebeveyn|e[şs]|yuva|[çc]ocuk|bo[şs]an|ayr[ıi]|terk)\w*\b",
            "romantik": r"\b(?:romantik|ho[şs]lan|a[şs][ıi]k|â[şs][ıi]k|asik|fl[öo]rt|sevgili|randevu|bulu[şs]|bulus|el\s+ele|[öo]p)\w*\b",
            "mahrem": r"\b(?:mahrem|dudak|[öo]p|sar[ıi]l|kucakla[şs]|yak[ıi]nla[şs]|aldat|evlilik\s+d[ıi][şs][ıi])\w*\b",
            "siddet": r"\b(?:[şs]iddet|siddet|kavga|d[öo]v|vur|tokat|tekme|yumruk|yarala|[öo]ld[üu]r|tehdit|sald[ıi]r|b[ıi][çc]ak|silah|t[üu]fek)\w*\b",
            "suc": r"\b(?:su[çc]|h[ıi]rs[ıi]z|h[ıi]rs[ıi]zl[ıi]k|soygun|[çc]al|ka[çc]ak|kanunsuz|yasa\s*d[ıi][şs][ıi]|tutuklan|yakalan)\w*\b",
            "zorbalik": r"\b(?:zorbal[ıi]k|zorba|alay\s+et|d[ıi][şs]la|a[şs]a[ğg][ıi]la|lakap|dalga\s+ge[çc]|itip\s+kak)\w*\b",
        }

        beklenenler = set()
        if any(anahtar in aciklama for anahtar in ("sigara", "tütün", "tutun", "nargile")):
            beklenenler.add("tutun")
        if any(anahtar in aciklama for anahtar in ("alkol", "içki", "icki", "sarhoş", "sarhos", "meyhane")):
            beklenenler.add("alkol")
        if any(anahtar in aciklama for anahtar in ("uyuşturucu", "uyusturucu", "madde", "bağımlı", "bagimli")):
            beklenenler.add("madde")
        if "kumar" in aciklama or "bahis" in aciklama:
            beklenenler.add("kumar")
        if any(anahtar in aciklama for anahtar in ("aile", "boşan", "bosan", "ebeveyn", "anne", "baba")):
            beklenenler.add("aile")
        if any(anahtar in aciklama for anahtar in ("romantik", "flört", "flort", "sevgili", "aşk", "ask")):
            beklenenler.add("romantik")
        if any(anahtar in aciklama for anahtar in ("mahrem", "öp", "op", "aldat", "evlilik dışı", "evlilik disi")):
            beklenenler.add("mahrem")
        if any(anahtar in aciklama for anahtar in ("şiddet", "siddet", "kavga", "dövüş", "dovus", "silah", "tehdit")):
            beklenenler.add("siddet")
        if any(anahtar in aciklama for anahtar in ("suç", "suc", "hırsız", "hirsiz", "yasa dışı", "yasa disi")):
            beklenenler.add("suc")
        if "zorbal" in aciklama or "akran" in aciklama:
            beklenenler.add("zorbalik")

        kategori_beklenenleri = {
            "zararlı_alışkanlıklar": {"tutun", "alkol", "madde", "kumar"},
            "zararli_aliskanliklar": {"tutun", "alkol", "madde", "kumar"},
            "siddet_suc": {"siddet", "suc", "zorbalik"},
            "cinsellik_mahremiyet": {"romantik", "mahrem"},
            "aile_yapısı": {"aile"},
            "aile_yapisi": {"aile"},
            "olumsuz_davranış": {"kumar", "zorbalik"},
            "olumsuz_davranis": {"kumar", "zorbalik"},
        }
        beklenenler |= kategori_beklenenleri.get(kategori, set())

        kanit_eslesmeleri = {
            kanit
            for kanit in beklenenler
            if kanit in kanit_haritasi and re.search(kanit_haritasi[kanit], metin)
        }
        acik_ifade_var = bool(kanit_eslesmeleri)
        if not beklenenler:
            acik_ifade_var = self._tema_olay_fiili_var_mi(tema, metin)

        olay_fiili_var = self._tema_olay_fiili_var_mi(tema, metin)
        baglam_cikarilabilir = acik_ifade_var and olay_fiili_var
        kavram_karsiligi_var = bool(kanit_eslesmeleri) if beklenenler else acik_ifade_var

        ozel_ret_nedenleri = self._tema_ozel_ret_nedenleri(tema, metin)
        if ozel_ret_nedenleri:
            acik_ifade_var = False
            baglam_cikarilabilir = False

        kosullar = {
            "acik_ifade_var_mi": acik_ifade_var,
            "baglam_cikarilabilir_mi": baglam_cikarilabilir,
            "kavram_karsiligi_var_mi": kavram_karsiligi_var,
        }
        agirliklar = {
            "acik_ifade_var_mi": 0.35,
            "baglam_cikarilabilir_mi": 0.35,
            "kavram_karsiligi_var_mi": 0.30,
        }
        puan = sum(agirliklar[ad] for ad, gecti in kosullar.items() if gecti)
        eksikler = [
            etiket
            for anahtar, etiket in {
                "acik_ifade_var_mi": "Alıntı içinde temayı doğrudan destekleyen açık ifade yok.",
                "baglam_cikarilabilir_mi": "Bağlam açıklaması alıntıdan mantıksal olarak çıkarılamıyor.",
                "kavram_karsiligi_var_mi": "Tema açıklamasındaki kavramlar alıntıda/yakın bağlamda karşılık bulmuyor.",
            }.items()
            if not kosullar[anahtar]
        ]
        eksikler.extend(ozel_ret_nedenleri)

        return {
            "kanitPuani": round(puan, 2),
            "esik": 0.70,
            "kosullar": kosullar,
            "beklenenKanitlar": sorted(beklenenler),
            "bulunanKanitlar": sorted(kanit_eslesmeleri),
            "eksikler": eksikler,
        }

    def _tema_alinti_aciklama_bagi_var_mi(self, kural: dict, cumle: str) -> bool:
        return self._tema_kanit_kontrolu(kural, cumle)["kanitPuani"] >= 0.70

    def _tema_ozel_ret_nedenleri(self, tema: str, metin: str) -> List[str]:
        nedenler = []
        if tema == "romantik ilgi":
            if re.search(r"\b(?:kimseyle|hi[çc]\s+kimseyle)\s+g[öo]z\s+g[öo]ze\s+gelme\w*\b", metin):
                nedenler.append("Olumsuz göz teması romantik ilgi kanıtı değildir.")
            if re.search(r"\bg[öo]z\s+g[öo]ze\s+geldi\w*\b", metin) and not re.search(r"\b(?:ho[şs]lan|a[şs][ıi]k|asik|sev|romantik|kalbi\s+[çc]arp)\w*\b", metin):
                nedenler.append("Sadece göz göze gelme romantik ilgi için yeterli değildir.")
            if re.search(r"\by[üu]z[üu]\s+as[ıi]k\w*\b", metin):
                nedenler.append("Yüz ifadesi romantik ilgi kanıtı değildir.")
            if re.search(r"\bday[ıi]\s+deme\w*.*ho[şs]lan\w*\b|\bho[şs]lan\w*.*day[ıi]\s+deme\w*\b", metin):
                nedenler.append("Akrabalık hitabından hoşlanma romantik ilgi kanıtı değildir.")
            if re.search(r"\b(?:ho[şs]lan[ıi]rd[ıi]|severd[ıi]|sayard[ıi]|de[ğg]er\s+verird[ıi]|day[ıi]|amca|abi|teyze|hala)\b", metin) and not self._romantik_ilgi_kaniti_var_mi(metin):
                nedenler.append("Hitap, sevgi/saygı veya memnuniyet kelimesi tek başına romantik ilgi kanıtı değildir.")
            if re.search(r"\b(?:hayran|hayrand[ıi]m|hayran[ıi]yd[ıi]m|onu\s+izlerdim|onu\s+izliyordum|[öo]rnek\s+al|takdir\s+et|be[ğg]en)\w*\b", metin) and not self._romantik_ilgi_kaniti_var_mi(metin):
                nedenler.append("Hayranlık, beğeni, izleme veya örnek alma tek başına romantik ilgi kanıtı değildir.")

        if tema == "zorbalık":
            if re.search(r"\bkendi(?:yle|siyle)?\s+bile\s+dalga\s+ge[çc]\w*\b", metin):
                nedenler.append("Kendiyle dalga geçme akran zorbalığı kanıtı değildir.")
            if re.search(r"\bdalga\s+ge[çc]\w*\b", metin) and not self._zorbalik_kaniti_var_mi(metin):
                nedenler.append("Dalga geçmek ifadesi tek başına hedefli zorbalık kanıtı değildir.")

        if tema == "aile çatışması":
            if re.search(r"\ba[çc]l[ıi]ktan\b.*\bba[ğg][ıi]r\w*|\bba[ğg][ıi]r\w*.*\ba[çc]l[ıi]ktan\b", metin):
                nedenler.append("Açlık/bedensel ihtiyaç kaynaklı bağırma aile çatışması kanıtı değildir.")

        if tema == "hırsızlık":
            if re.search(r"\bgidi\s+\w*\s*h[ıi]rs[ıi]zlar[ıi]?\b", metin):
                nedenler.append("Lakapsı/ünlemli hırsız ifadesi gerçek suç davranışı, fail ve eylem içermez.")
            if not re.search(r"\b(?:[çc]al(?:d[ıi]|m[ıi][şs]|[ıi]yor|acak|arken|maya|may[ıi]|[ıi]nd[ıi]|[ıi]nm[ıi][şs])|h[ıi]rs[ıi]zl[ıi]k\s+yap|soygun\s+yap)\w*\b", metin):
                nedenler.append("Hırsızlık için gerçek suç eylemi bulunmadı.")

        return nedenler

    def _tema_bulgusu_kategoride_var_mi(self, tema_bulgu: dict, kategori_bulgulari: dict) -> bool:
        kategori = tema_bulgu.get("kategori")
        tema_adi = str(tema_bulgu.get("tema_adi", "") or "").strip().lower()
        cumle = re.sub(
            r"\s+",
            " ",
            str(tema_bulgu.get("alinti") or tema_bulgu.get("alıntı") or tema_bulgu.get("cumle") or "").strip().lower()
        )
        sayfa = str(tema_bulgu.get("sayfa", "") or "")
        if not kategori:
            return False

        for bulgu in kategori_bulgulari.get(kategori, {}).get("bulunan_kelimeler", []):
            bulgu_tema = str(bulgu.get("tema_adi", "") or bulgu.get("kelime", "") or "").strip().lower()
            bulgu_cumle = re.sub(
                r"\s+",
                " ",
                str(bulgu.get("cumle") or bulgu.get("alinti") or bulgu.get("alıntı") or "").strip().lower()
            )
            bulgu_sayfa = str(bulgu.get("sayfa", "") or "")
            if bulgu_tema == tema_adi and bulgu_sayfa == sayfa and (not cumle or bulgu_cumle == cumle):
                return True
        return False

    def _risk_0_kurallarini_uygula(self, sonuc: dict) -> int:
        temizlenen = 0
        kategori_bulgulari = sonuc.get("kategori_bulgulari", {})
        pozitif_anahtarlar = set()
        pozitif_kelime_anahtarlari = set()
        pozitif_sade_kelimeler = set()
        for kategori, kategori_data in kategori_bulgulari.items():
            for bulgu in kategori_data.get("bulunan_kelimeler", []):
                if self._risk_puani_al(bulgu) > 0:
                    pozitif_anahtarlar.add(self._bulgu_tutarlilik_anahtari(bulgu, kategori))
                    pozitif_kelime_anahtarlari.add(self._bulgu_kelime_anahtari(bulgu, kategori))
                    pozitif_sade_kelimeler.add(self._bulgu_sade_kelime_anahtari(bulgu))

        for kategori, kategori_data in kategori_bulgulari.items():
            yeni_bulgular = []
            for bulgu in kategori_data.get("bulunan_kelimeler", []):
                if (
                    self._risk_puani_al(bulgu) <= 0
                    and (
                        self._bulgu_tutarlilik_anahtari(bulgu, kategori) in pozitif_anahtarlar
                        or self._bulgu_kelime_anahtari(bulgu, kategori) in pozitif_kelime_anahtarlari
                        or self._bulgu_sade_kelime_anahtari(bulgu) in pozitif_sade_kelimeler
                    )
                ):
                    temizlenen += 1
                    continue
                yeni_bulgular.append(bulgu)
            kategori_data["bulunan_kelimeler"] = yeni_bulgular

        for kategori_data in sonuc.get("kategori_bulgulari", {}).values():
            for bulgu in kategori_data.get("bulunan_kelimeler", []):
                if self._risk_puani_al(bulgu) > 0:
                    continue
                bulgu["riskPuani"] = 0
                bulgu["baglamsal_risk"] = 0
                bulgu["risk_puani"] = 0
                bulgu["kararSinifi"] = "baglamla_temiz"
                bulgu["problemliMi"] = False
                bulgu["incelemeGerekliMi"] = False
                bulgu["nihaiKarar"] = "Risk 0 / Temiz"
                if bulgu.get("uyariMetni"):
                    temizlenen += 1
                if bulgu.get("onerili_revizyon"):
                    temizlenen += 1
                bulgu["uyariMetni"] = ""
                bulgu["onerili_revizyon"] = ""
            self._kategori_ozetini_yenile(kategori_data)
        return temizlenen

    def _bulgu_kelime_anahtari(self, bulgu: dict, kategori: str = "") -> tuple:
        kelime = str(bulgu.get("kelime", "") or bulgu.get("tema_adi", "")).strip().lower()
        return (kategori or str(bulgu.get("kategori", ""))).strip().lower(), kelime

    def _bulgu_sade_kelime_anahtari(self, bulgu: dict) -> str:
        return str(bulgu.get("kelime", "") or bulgu.get("tema_adi", "")).strip().lower()

    def _bulgu_tutarlilik_anahtari(self, bulgu: dict, kategori: str = "") -> tuple:
        kelime = str(bulgu.get("kelime", "") or bulgu.get("tema_adi", "")).strip().lower()
        cumle = str(
            bulgu.get("cumle")
            or bulgu.get("kontext")
            or bulgu.get("alinti")
            or bulgu.get("alıntı")
            or ""
        ).strip().lower()
        cumle = re.sub(r"\s+", " ", cumle)[:220]
        sayfa = str(bulgu.get("sayfa", "") or "")
        return (kategori or str(bulgu.get("kategori", ""))).strip().lower(), kelime, sayfa, cumle

    def _final_skoru_kalite_kontrolune_gore_duzelt(self, sonuc: dict) -> None:
        kategori_bulgulari = sonuc.get("kategori_bulgulari", {})
        pozitif_riskler = [
            self._risk_puani_al(bulgu)
            for kategori_data in kategori_bulgulari.values()
            for bulgu in kategori_data.get("bulunan_kelimeler", [])
            if self._risk_puani_al(bulgu) > 0
        ]
        if not pozitif_riskler:
            sonuc["final_skor"] = 0.0
            if isinstance(sonuc.get("karar"), dict):
                sonuc["karar"]["seviye"] = "Uygun"
                sonuc["karar"]["renk"] = "green"
            return

        if float(sonuc.get("final_skor", 0) or 0) <= 0:
            sonuc["final_skor"] = round(min(30.0, max(pozitif_riskler) * 10), 2)
            if isinstance(sonuc.get("karar"), dict):
                sonuc["karar"]["seviye"] = "Düşük Risk"
                sonuc["karar"]["renk"] = "yellow"

        self._zararli_aliskanlik_skor_kuralini_uygula(sonuc)

    def _zorunlu_tema_bulgularini_kategorilere_tasi(self, sonuc: dict, tema_bulgulari: list) -> int:
        kategori_bulgulari = sonuc.setdefault("kategori_bulgulari", {})
        eklenen = 0
        for tema_bulgu in tema_bulgulari:
            kategori = tema_bulgu.get("kategori")
            tema_adi = tema_bulgu.get("tema_adi")
            if not kategori or tema_adi not in ZORUNLU_TEMA_LISTESI:
                continue

            risk = self._risk_puani_al(tema_bulgu)
            if tema_adi in {"Sigara kullanımı", "Alkol kullanımı", "Sarhoşluk"}:
                risk = max(4, risk or 4)
            elif str(tema_bulgu.get("baglamTipi", "")) == "romantik_dusuk_izleme":
                risk = 0
            elif tema_adi in ZORUNLU_DAVRANIS_TEMALARI:
                risk = max(1, min(2, risk or 1))

            kategori_data = kategori_bulgulari.setdefault(kategori, {
                "bulundu": False,
                "toplam_bulgu": 0,
                "riskli_bulgu_sayisi": 0,
                "dusuk_risk_sayisi": 0,
                "temizlenen_bulgu_sayisi": 0,
                "bulunan_kelimeler": [],
            })
            kategori_data.setdefault("bulunan_kelimeler", [])

            cumle = tema_bulgu.get("alinti") or tema_bulgu.get("alıntı") or ""
            kelime = tema_adi or "Tema"
            anahtar = (kelime, tema_bulgu.get("sayfa", 1), cumle)
            mevcut = {
                (bulgu.get("kelime"), bulgu.get("sayfa"), bulgu.get("cumle"))
                for bulgu in kategori_data.get("bulunan_kelimeler", [])
            }
            if anahtar in mevcut:
                continue

            kategori_data["bulunan_kelimeler"].append({
                "kelime": kelime,
                "kategori": kategori,
                "cumle": cumle,
                "sayfa": tema_bulgu.get("sayfa", 1),
                "orijinal_risk": risk,
                "yas_ayarsiz_risk": risk,
                "riskPuani": risk,
                "baglamsal_risk": risk,
                "baglamTipi": tema_bulgu.get("baglamTipi") or "zorunlu_tema_sahnelenmesi",
                "kararSinifi": "dusuk_risk" if risk <= 2 else "riskli",
                "problemliMi": risk > 0,
                "incelemeGerekliMi": True,
                "kararGuveni": 0.95,
                "nihaiKarar": "Risk 0 - İzleme Notu" if risk <= 0 else "Düşük Risk" if risk <= 2 else "Riskli",
                "tema_adi": tema_adi,
                "kaynak": "Zorunlu kalite kontrolü",
                "uyariMetni": tema_bulgu.get("uyariMetni", ""),
                "gerekce": tema_bulgu.get("gerekce", ""),
            })
            eklenen += 1

        for kategori_data in kategori_bulgulari.values():
            self._kategori_ozetini_yenile(kategori_data)
        return eklenen

    def _kategori_ozetini_yenile(self, kategori_data: dict) -> None:
        bulgular = kategori_data.get("bulunan_kelimeler", [])
        kategori_data["bulundu"] = bool(bulgular)
        kategori_data["toplam_bulgu"] = len(bulgular)
        kategori_data["riskli_bulgu_sayisi"] = sum(1 for bulgu in bulgular if self._risk_puani_al(bulgu) >= 3)
        kategori_data["dusuk_risk_sayisi"] = sum(1 for bulgu in bulgular if 0 < self._risk_puani_al(bulgu) < 3)
        kategori_data["temizlenen_bulgu_sayisi"] = sum(1 for bulgu in bulgular if self._risk_puani_al(bulgu) <= 0)
        toplam_risk = sum(self._risk_puani_al(bulgu) for bulgu in bulgular)
        kategori_data["ortalama_risk"] = round(toplam_risk / len(bulgular), 2) if bulgular else 0

    def _risk_puani_al(self, bulgu: dict) -> float:
        riskler = []
        for alan in ("riskPuani", "risk_puani", "baglamsal_risk", "risk", "puan"):
            if alan in bulgu and bulgu.get(alan) is not None:
                try:
                    riskler.append(float(bulgu.get(alan) or 0))
                except (TypeError, ValueError):
                    pass
        return max(riskler) if riskler else 0.0

    def _zorunlu_tutarlilik_sorunlarini_bul(self, sonuc: dict) -> list:
        durumlar = {}
        for kategori, kategori_data in sonuc.get("kategori_bulgulari", {}).items():
            for bulgu in kategori_data.get("bulunan_kelimeler", []):
                kelime = str(bulgu.get("kelime", "")).strip().lower()
                cumle = str(bulgu.get("cumle", "")).strip().lower()[:180]
                sayfa = str(bulgu.get("sayfa", "") or "")
                if not kelime:
                    continue
                anahtar = (kelime, sayfa, cumle)
                durum = "riskli" if self._risk_puani_al(bulgu) > 0 else "risksiz"
                durumlar.setdefault(anahtar, set()).add(durum)

        sorunlar = []
        for (kelime, sayfa, _cumle), kayit_durumlari in durumlar.items():
            if len(kayit_durumlari) > 1:
                sorunlar.append(f"'{kelime}' sayfa {sayfa or '?'} içinde hem riskli hem risksiz raporlandı.")
        return sorunlar

    def _meb_kademeli_ceza_hesapla(self, kriter_anahtari: str, kriter: dict, zararli_ozet: dict) -> float:
        """MEB puan cezasını tek kriter için sabit -50 yerine kademeli hesaplar."""
        risk = max(0.0, min(5.0, float(kriter.get("risk", 0) or 0)))
        if risk <= 0:
            return 0.0

        bulgu_sayisi = int(kriter.get("bulgular_sayisi", 0) or 0)
        if kriter_anahtari == "guvenlik" and zararli_ozet.get("zararli_aliskanlik_sahnesi_var"):
            bulgu_sayisi = max(bulgu_sayisi, int(zararli_ozet.get("toplam_zararli_sahne_sayisi", 0) or 0))
        ceza = risk * 4.0
        if bulgu_sayisi >= 3:
            ceza += 3.0
        if bulgu_sayisi >= 5:
            ceza += 4.0

        if kriter_anahtari == "guvenlik" and zararli_ozet.get("zararli_aliskanlik_sahnesi_var"):
            if zararli_ozet.get("tema_yogunlugu_katsayisi_uygulandi"):
                ceza += 5.0
            if zararli_ozet.get("tema_tekrar_yogunlugu_var"):
                ceza += 4.0
            if zararli_ozet.get("davranis_normalizasyonu_var"):
                ceza += 5.0
            if zararli_ozet.get("yas_katsayisi_uygulandi"):
                ceza += 4.0
            tavan = 45.0 if zararli_ozet.get("davranis_normalizasyonu_var") else 35.0
            return round(min(tavan, ceza), 2)

        return round(min(35.0, ceza), 2)

    def _meb_puanlamasini_kademelendir(self, meb_degerlendirmesi: dict, zararli_ozet: dict) -> dict:
        meb_puanlama_detayi = {}
        toplam_ceza = 0.0
        for kriter_anahtari, kriter in meb_degerlendirmesi.get("meb_kriterler", {}).items():
            risk = max(0.0, min(5.0, float(kriter.get("risk", 0) or 0)))
            ceza = self._meb_kademeli_ceza_hesapla(kriter_anahtari, kriter, zararli_ozet)
            toplam_ceza += ceza
            kriter["puan_cezasi"] = ceza
            kriter["puan_etkisi"] = f"-{ceza:g}"
            meb_puanlama_detayi[kriter_anahtari] = {
                "risk": risk,
                "bulgu_sayisi": (
                    max(
                        int(kriter.get("bulgular_sayisi", 0) or 0),
                        int(zararli_ozet.get("toplam_zararli_sahne_sayisi", 0) or 0)
                    )
                    if kriter_anahtari == "guvenlik" and zararli_ozet.get("zararli_aliskanlik_sahnesi_var")
                    else int(kriter.get("bulgular_sayisi", 0) or 0)
                ),
                "puan_cezasi": ceza,
                "formul": "kademeli: risk şiddeti + bulgu yoğunluğu + yaş/normalizasyon katsayıları",
                "karar": kriter.get("karar", "Bilinmiyor"),
            }

        meb_puani = max(0.0, min(100.0, 100.0 - toplam_ceza))
        meb_degerlendirmesi["meb_puani"] = round(meb_puani, 2)
        meb_degerlendirmesi["puanlama_detayi"] = {
            "baslangic_puani": 100,
            "kriter_cezalari": meb_puanlama_detayi,
            "toplam_ceza": round(toplam_ceza, 2),
            "formul": f"100 - kademeli_toplam_ceza({round(toplam_ceza, 2):g}) = {round(meb_puani, 2):g}",
            "kalibrasyon_notu": "Tek kriter otomatik -50 üretmez; ceza bulgu şiddeti, tekrar/tema yoğunluğu, yaş grubu ve normalizasyon bağlamıyla kademeli hesaplanır.",
            "zararli_aliskanlik_ozeti": zararli_ozet,
        }
        meb_degerlendirmesi["genel_karar"] = (
            "Uygun" if meb_puani >= 75 else
            "Koşullu" if meb_puani >= 50 else
            "Revizyon" if meb_puani >= 25 else
            "Uygun Değil"
        )
        return meb_degerlendirmesi

    def _tema_bulgularini_meb_ile_iliskilendir(self, meb_degerlendirmesi: dict, tema_analizi: dict) -> dict:
        """Tema/olay örgüsü bulgularını MEB güvenli içerik kriterine taşır."""
        if not tema_analizi or not tema_analizi.get("bulgular"):
            return meb_degerlendirmesi

        meb_degerlendirmesi.setdefault("meb_kriterler", {})
        meb_degerlendirmesi.setdefault("meb_bulgulari", {})
        meb_degerlendirmesi["meb_kriterler"].setdefault("guvenlik", {
            "ad": "Güvenli ve Etik İçerik",
            "risk": 0,
            "karar": "Uygun"
        })

        guvenlik_bulgulari = meb_degerlendirmesi["meb_bulgulari"].setdefault("guvenlik", [])
        mevcut_anahtarlar = {
            (bulgu.get("sayfa"), bulgu.get("quote") or bulgu.get("alıntı") or bulgu.get("alinti"))
            for bulgu in guvenlik_bulgulari
        }
        max_risk = int(meb_degerlendirmesi["meb_kriterler"]["guvenlik"].get("risk", 0) or 0)

        for bulgu in tema_analizi.get("bulgular", []):
            risk = int(bulgu.get("risk_puani", bulgu.get("riskPuani", 0)) or 0)
            if bulgu.get("tema_adi") in {"Sigara kullanımı", "Alkol kullanımı", "Sarhoşluk"}:
                risk = max(risk, 4)
            max_risk = max(max_risk, risk)
            anahtar = (bulgu.get("sayfa"), bulgu.get("alinti"))
            if anahtar in mevcut_anahtarlar:
                continue
            mevcut_anahtarlar.add(anahtar)
            guvenlik_bulgulari.append({
                "quote": bulgu.get("alinti", ""),
                "sebebi": "%s: %s" % (bulgu.get("tema_adi", "Tema"), bulgu.get("gerekce", "")),
                "sayfa": bulgu.get("sayfa", 0),
                "risk_puani": risk,
                "tema_adi": bulgu.get("tema_adi", ""),
                "baglam": bulgu.get("baglam", ""),
                "onerili_revizyon": "Tema olay örgüsünde korunacaksa yaş grubuna uygun eleştirel/sonuç gösteren bağlam güçlendirilmelidir."
            })

        meb_degerlendirmesi["meb_kriterler"]["guvenlik"]["risk"] = min(5, max_risk)
        if max_risk >= 4:
            meb_degerlendirmesi["meb_kriterler"]["guvenlik"]["karar"] = "Yüksek Risk"
        elif max_risk >= 3:
            meb_degerlendirmesi["meb_kriterler"]["guvenlik"]["karar"] = "Uyarı"
        elif max_risk > 0:
            meb_degerlendirmesi["meb_kriterler"]["guvenlik"]["karar"] = "Kontrol"

        return meb_degerlendirmesi

    def _kategoriyi_taray(self, metin_normalized: str, kategori: str, kategori_data: dict,
                          yas_grubu: str = "6-12", orijinal_metin: str = "") -> dict:
        """
        Bir kategoriyi tam kelime eslesmesi ve cumle baglami ile tara.
        """
        kelimeler = kategori_data.get("kelimeler", [])
        regexler = kategori_data.get("regexler", [])
        risk_puani = kategori_data["risk_puani"]

        bulunan = []
        gorulen_olaylar = set()
        toplam_risk = 0

        for kelime in kelimeler:
            for eslesme in self._tam_kelime_eslesmelerini_bul(metin_normalized, kelime):
                basla = eslesme.start()
                bitis = eslesme.end()

                bagimsizlik_kontrol = self._kelime_bagimsiz_mi(
                    metin_normalized,
                    basla,
                    bitis,
                    kelime
                )

                if not bagimsizlik_kontrol["bagimsiz"]:
                    print(f"FALSE POSITIVE: '{kelime}' <- '{bagimsizlik_kontrol['yapan_kelime']}' (gecersiz)")
                    continue

                cumle = self._cumleyi_cikart(metin_normalized, basla, bitis)
                sayfa_numarasi = self._sayfa_numarasini_bul(metin_normalized, basla)
                ham_bulgu = self._bulgu_verisini_olustur(kelime, kategori, cumle, sayfa_numarasi)

                # Once cumle bazli baglam analizi, ardindan AI/fallback risk modeli calisir.
                baglamsal_risk = self._baglamsal_analiz_yap(
                    metin_normalized,
                    basla,
                    bitis,
                    risk_puani,
                    kategori
                )
                ai_sonuc = self._ai_baglam_analizi(ham_bulgu, risk_puani, baglamsal_risk)
                yas_ayarsiz_risk = ai_sonuc["riskPuani"]
                baglamsal_risk, yas_ayari_aciklama = self._yas_grubuna_gore_risk_ayarla(
                    yas_ayarsiz_risk,
                    kategori,
                    ai_sonuc["baglamTipi"],
                    yas_grubu
                )
                ai_sonuc["yasAyarsizRiskPuani"] = yas_ayarsiz_risk
                ai_sonuc["riskPuani"] = baglamsal_risk
                ai_sonuc["problemliMi"] = baglamsal_risk > 0
                ai_sonuc["yasGrubu"] = yas_grubu
                ai_sonuc["yasAyariAciklama"] = yas_ayari_aciklama
                ai_sonuc.update(self._baglam_kararini_siniflandir(baglamsal_risk, ai_sonuc["baglamTipi"]))
                if baglamsal_risk != yas_ayarsiz_risk:
                    ai_sonuc["gerekce"] = f"{ai_sonuc['gerekce']} Yaş grubu ayarı: {yas_ayari_aciklama}"
                    ai_sonuc["uyariMetni"] = "" if baglamsal_risk == 0 else self._uyari_metni_olustur(
                        ham_bulgu,
                        ai_sonuc["baglamTipi"],
                        baglamsal_risk
                    )

                satir_numarasi = metin_normalized[:basla].count('\n') + 1
                olay_anahtari = (
                    kategori,
                    sayfa_numarasi,
                    re.sub(r"\s+", " ", cumle.strip().lower()),
                    ai_sonuc["baglamTipi"],
                    ai_sonuc["kararSinifi"],
                )
                if olay_anahtari in gorulen_olaylar:
                    continue
                gorulen_olaylar.add(olay_anahtari)

                bulunan.append({
                    "kelime": kelime,
                    "kategori": kategori,
                    "cumle": cumle,
                    "orijinal_risk": risk_puani,
                    "yas_ayarsiz_risk": yas_ayarsiz_risk,
                    "baglamsal_risk": baglamsal_risk,
                    "satir": satir_numarasi,
                    "sayfa": sayfa_numarasi,
                    "kontext": self._konteksti_al(metin_normalized, basla, bitis),
                    "ai_baglam_analizi": ai_sonuc,
                    "bulguVar": ai_sonuc["bulguVar"],
                    "problemliMi": ai_sonuc["problemliMi"],
                    "riskPuani": ai_sonuc["riskPuani"],
                    "baglamTipi": ai_sonuc["baglamTipi"],
                    "gerekce": ai_sonuc["gerekce"],
                    "yasGrubu": yas_grubu,
                    "yasAyariAciklama": yas_ayari_aciklama,
                    "kararSinifi": ai_sonuc["kararSinifi"],
                    "kararGuveni": ai_sonuc["kararGuveni"],
                    "incelemeGerekliMi": ai_sonuc["incelemeGerekliMi"],
                    "uyariMetni": ai_sonuc["uyariMetni"]
                })

                toplam_risk += baglamsal_risk

        for regex in regexler:
            try:
                regex_eslesmeleri = list(re.finditer(regex, metin_normalized, flags=re.IGNORECASE))
            except re.error:
                continue
            for eslesme in regex_eslesmeleri:
                basla = eslesme.start()
                bitis = eslesme.end()
                kelime = eslesme.group(0)
                cumle = self._cumleyi_cikart(metin_normalized, basla, bitis)
                sayfa_numarasi = self._sayfa_numarasini_bul(metin_normalized, basla)
                ham_bulgu = self._bulgu_verisini_olustur(kelime, kategori, cumle, sayfa_numarasi)
                baglamsal_risk = self._baglamsal_analiz_yap(
                    metin_normalized,
                    basla,
                    bitis,
                    risk_puani,
                    kategori
                )
                ai_sonuc = self._ai_baglam_analizi(ham_bulgu, risk_puani, baglamsal_risk)
                yas_ayarsiz_risk = ai_sonuc["riskPuani"]
                baglamsal_risk, yas_ayari_aciklama = self._yas_grubuna_gore_risk_ayarla(
                    yas_ayarsiz_risk,
                    kategori,
                    ai_sonuc["baglamTipi"],
                    yas_grubu
                )
                ai_sonuc["yasAyarsizRiskPuani"] = yas_ayarsiz_risk
                ai_sonuc["riskPuani"] = baglamsal_risk
                ai_sonuc["problemliMi"] = baglamsal_risk > 0
                ai_sonuc["yasGrubu"] = yas_grubu
                ai_sonuc["yasAyariAciklama"] = yas_ayari_aciklama
                ai_sonuc.update(self._baglam_kararini_siniflandir(baglamsal_risk, ai_sonuc["baglamTipi"]))

                satir_numarasi = metin_normalized[:basla].count('\n') + 1
                olay_anahtari = (
                    kategori,
                    sayfa_numarasi,
                    re.sub(r"\s+", " ", cumle.strip().lower()),
                    ai_sonuc["baglamTipi"],
                    ai_sonuc["kararSinifi"],
                )
                if olay_anahtari in gorulen_olaylar:
                    continue
                gorulen_olaylar.add(olay_anahtari)

                bulunan.append({
                    "kelime": kelime,
                    "kategori": kategori,
                    "cumle": cumle,
                    "orijinal_risk": risk_puani,
                    "yas_ayarsiz_risk": yas_ayarsiz_risk,
                    "baglamsal_risk": baglamsal_risk,
                    "satir": satir_numarasi,
                    "sayfa": sayfa_numarasi,
                    "kontext": self._konteksti_al(metin_normalized, basla, bitis),
                    "ai_baglam_analizi": ai_sonuc,
                    "bulguVar": ai_sonuc["bulguVar"],
                    "problemliMi": ai_sonuc["problemliMi"],
                    "riskPuani": ai_sonuc["riskPuani"],
                    "baglamTipi": ai_sonuc["baglamTipi"],
                    "gerekce": ai_sonuc["gerekce"],
                    "yasGrubu": yas_grubu,
                    "yasAyariAciklama": yas_ayari_aciklama,
                    "kararSinifi": ai_sonuc["kararSinifi"],
                    "kararGuveni": ai_sonuc["kararGuveni"],
                    "incelemeGerekliMi": ai_sonuc["incelemeGerekliMi"],
                    "uyariMetni": ai_sonuc["uyariMetni"],
                    "kaynak": "ozel_regex"
                })

                toplam_risk += baglamsal_risk

        riskli_bulgu_sayisi = sum(1 for bulgu in bulunan if bulgu.get("kararSinifi") == "riskli")
        dusuk_risk_sayisi = sum(1 for bulgu in bulunan if bulgu.get("kararSinifi") == "dusuk_risk")
        temizlenen_bulgu_sayisi = sum(1 for bulgu in bulunan if bulgu.get("kararSinifi") == "baglamla_temiz")
        ortalama_risk = (toplam_risk / len(bulunan)) if bulunan else 0

        return {
            "bulundu": len(bulunan) > 0,
            "toplam_bulgu": len(bulunan),
            "riskli_bulgu_sayisi": riskli_bulgu_sayisi,
            "dusuk_risk_sayisi": dusuk_risk_sayisi,
            "temizlenen_bulgu_sayisi": temizlenen_bulgu_sayisi,
            "bulunan_kelimeler": bulunan,
            "ortalama_risk": ortalama_risk,
            "risk_puani": risk_puani
        }

    def _kelime_bagimsiz_mi(self, metin_normalized: str, basla: int, bitis: int, 
                            kelime: str) -> dict:
        """
        ⭐ YENİ KONTROL: Kelimenin bağımsız olup olmadığını kontrol et
        
        Kural: Eğer kelime başka bir kelimenin içindeyse → FALSE POSITIVE
        Örnek: "Ceylan" → "lan" geçiyor ama bağımsız değil → geçersiz
                "havalandı" → "lan" geçiyor ama "lan" ek değil → geçersiz
        
        Returns:
            {
                "bagimsiz": bool,
                "yapan_kelime": str (if dependent),
                "neden": str
            }
        """
        
        # Öncesi ve sonrası karakterleri kontrol et
        onceki_konum = basla - 1
        kelimenin_oncesi = metin_normalized[onceki_konum] if onceki_konum >= 0 else ' '
        
        sonraki_konum = bitis
        kelimenin_sonrasi = metin_normalized[sonraki_konum] if sonraki_konum < len(metin_normalized) else ' '
        
        # Türkçe harf kontrolü
        turk_harf_oncesi = kelimenin_oncesi.isalpha() and kelimenin_oncesi not in ' \n\t'
        turk_harf_sonrasi = kelimenin_sonrasi.isalpha() and kelimenin_sonrasi not in ' \n\t'

        if self._parcali_kelime_ici_mi(metin_normalized, basla, bitis):
            return {
                "bagimsiz": False,
                "yapan_kelime": metin_normalized[max(0, basla-20):min(len(metin_normalized), bitis+20)].strip(),
                "neden": "PDF satır sonu hece bölünmesi; kelime parçası"
            }

        # Yeni mimari: tam kelime siniri ana filtredir.
        if turk_harf_oncesi or turk_harf_sonrasi or kelimenin_oncesi.isdigit() or kelimenin_sonrasi.isdigit():
            return {
                "bagimsiz": False,
                "yapan_kelime": metin_normalized[max(0, basla-20):min(len(metin_normalized), bitis+20)].strip(),
                "neden": "Kelime baska bir kelimenin icinde"
            }

        return {
            "bagimsiz": True,
            "yapan_kelime": None,
            "neden": "Tam kelime"
        }
        
        # ⭐ ADIM 1: Çok kısa sakıncalı kelimeler - embedding'de FALSE POSITIVE olur
        # "lan" (Ceylan, havalandı), "vur" (vurdular), "ayin" (yayınevim), 
        # "fal" REMOVED - aggressive filter was too strict
        # "ayıp" (katlayıp)
        if kelime in ["lan", "vur", "ayin", "ayıp"]:
            # Kontrol 1: Öncesi harf var mı?
            if basla > 0:
                oncesi = metin_normalized[basla - 1]
                # Eğer öncesi Türkçe harf ise → KESINLIKLE FALSE POSITIVE (embedded)
                if oncesi.isalpha() and oncesi not in ' \n\t':
                    return {
                        "bagimsiz": False,
                        "yapan_kelime": metin_normalized[max(0, basla-10):min(len(metin_normalized), bitis+10)].strip(),
                        "neden": f"Kısa kelime '{kelime}' öncesi komşu harf → embedded word"
                    }
            
            # Kontrol 2: Sonrası harf var mı?
            if bitis < len(metin_normalized):
                sonrasi = metin_normalized[bitis]
                # Eğer sonrası Türkçe harf ise → KESINLIKLE FALSE POSITIVE (embedded)
                if sonrasi.isalpha() and sonrasi not in ' \n\t':
                    return {
                        "bagimsiz": False,
                        "yapan_kelime": metin_normalized[max(0, basla-10):min(len(metin_normalized), bitis+10)].strip(),
                        "neden": f"Kısa kelime '{kelime}' sonrası komşu harf → embedded word"
                    }
            
            # Kontrol 3: PDF extraction'ında parçalı yazılan isimler (ör: "ser kan" → "Serkan")
            # Context window'unda isim parçaları kontrol et
            if kelime in FALSE_POSITIVE_FILTER:
                fp_list = FALSE_POSITIVE_FILTER[kelime]
                
                # PDF spacing: "ser kan", "cey lan" vb. parçalı writes
                if "turkce_isimler" in fp_list:
                    for isim in fp_list["turkce_isimler"]:
                        # Tam isim metin'de var mı?
                        if isim.lower() in metin_normalized.lower():
                            return {
                                "bagimsiz": False,
                                "yapan_kelime": metin_normalized[max(0, basla-20):min(len(metin_normalized), bitis+20)].strip(),
                                "neden": f"'{isim}' ismi metinde var → '{kelime}' false positive"
                            }
                        
                        # Parçalı yazılmış hali kontrol et (ör: "ser kan" → "Serkan")
                        # İsmi çıkart: ilk n-len(kelime) karakterleri + space + kelime
                        if len(isim) > len(kelime):
                            prefix = isim[:-len(kelime)]  # "serkan" → "ser"
                            partial = prefix + " " + kelime  # "ser kan"
                            if partial.lower() in metin_normalized.lower():
                                return {
                                    "bagimsiz": False,
                                    "yapan_kelime": metin_normalized[max(0, basla-20):min(len(metin_normalized), bitis+20)].strip(),
                                    "neden": f"'{partial}' (parçalı {isim}) metinde var → '{kelime}' false positive"
                                }
        if kelime in FALSE_POSITIVE_FILTER:
            kelime_filter = FALSE_POSITIVE_FILTER[kelime]
            
            # Türkçe isimler kontrolü (endswith)
            if "turkce_isimler" in kelime_filter:
                # YAKIN kontekst al (20 char - çok STRICT, yanlış match'i önle)
                yakin_kontekst_basla = max(0, basla - 20)
                yakin_kontekst_bitis = min(len(metin_normalized), bitis + 20)
                yakin_kontekst = metin_normalized[yakin_kontekst_basla:yakin_kontekst_bitis].lower()
                
                for isim in kelime_filter["turkce_isimler"]:
                    if isim.lower().endswith(kelime.lower()):
                        # STRICT: Kelime BAŞINDA başka Türkçe harf varsa (ör: "ceylansevecen") → SKIP
                        # Kelimenin ÖNCESİNDEKİ karakter kontrol et
                        onceki_char = metin_normalized[basla - 1] if basla > 0 else ' '
                        
                        # Eğer öncesi Türkçe harf ise, bu kelimenin parçası = FALSE POSITIVE
                        if onceki_char.isalpha() and onceki_char not in ' \n\t':
                            return {
                                "bagimsiz": False,
                                "yapan_kelime": isim,
                                "neden": f"'{isim}' isiminin son hecesi (ama başında harf var)"
                            }
                        
                        # Ismi kontrol et (strict match)
                        if isim.lower() in yakin_kontekst:
                            return {
                                "bagimsiz": False,
                                "yapan_kelime": isim,
                                "neden": f"'{isim}' isiminin son hecesi"
                            }
            
            # ek_sozler kontrolü - SADECE FALSE_POSITIVE'ler (bölüm, büyükbaba, defalarca, yayınevi, etc.)
            if "ek_sozler" in kelime_filter and kelime_filter["ek_sozler"]:
                for sozcu in kelime_filter["ek_sozler"]:
                    sozcu_lower = sozcu.lower()
                    kelime_lower = kelime.lower()
                    metin_lower = metin_normalized.lower()
                    
                    # Sözcük kelime içinde geçiyor mu?
                    if (len(sozcu) > len(kelime) and 
                        kelime_lower in sozcu_lower and
                        sozcu_lower in metin_lower):
                        # Sözcüğün pozisyonunu kontrol et
                        search_pos = 0
                        while True:
                            sozcu_pos = metin_lower.find(sozcu_lower, search_pos)
                            if sozcu_pos == -1:
                                break
                            
                            # Kelimenin bu sözcük içinde mi?
                            if sozcu_pos <= basla and basla < sozcu_pos + len(sozcu):
                                return {
                                    "bagimsiz": False,
                                    "yapan_kelime": sozcu,
                                    "neden": f"'{sozcu}' sözcüğünün parçası"
                                }
                            
                            search_pos = sozcu_pos + 1

# ⭐ ADIM 3: Harmonic (ses uyumu) kontrol
        # Eğer öncesi sesli harfle bitiyorsa ve sonrası sesli harfle başlıyorsa = bağlantı olabilir
        sesli_harfler = "aeıioöuü"
        if (kelimenin_oncesi.lower() in sesli_harfler and 
            kelimenin_sonrasi.lower() in sesli_harfler and
            len(kelime) < 5):
            # Ek olabilir - kontrol et
            return {
                "bagimsiz": False,
                "yapan_kelime": metin_normalized[max(0, basla-10):min(len(metin_normalized), bitis+10)].strip(),
                "neden": "Sesli harf uyumu (muhtemelen ek)"
            }
        
        # Tüm kontroller geçildi → Bağımsız kelime
        return {
            "bagimsiz": True,
            "yapan_kelime": None,
            "neden": "Bağımsız kelime (valid)"
        }
    
    def _baglamsal_analiz_yap(self, metin: str, basla: int, bitis: int, 
                              varsayilan_risk: int, kategori: str = "") -> int:
        """
        Kelimeyi çevreleyen bağlamı analiz et
        Risk puanını ayarla (0-5 aralığında)
        Zararlı vs zararsız bağlamları ayırt et
        
        ⭐ YENİ STRATEJİ: Cümle içindeki gerçek anlamına bakarak risk belirle
        CÜMLE-SEVİYESİ KONTEKST ANALİZİ: Her kelime için cümleyi analiz et
        """
        import re
        
        # Kelimenin bulunduğu cümleyi çıkart
        cumle = self._cumleyi_cikart(metin, basla, bitis)
        cumle_lower = cumle.lower()
        
        # Etrafındaki konteksti al (geri uyumluluk için)
        kontekst_basla = max(0, basla - 150)
        kontekst_bitis = min(len(metin), bitis + 150)
        kontekst = metin[kontekst_basla:kontekst_bitis].lower()
        
        # Öncesi/sonrası ayrı ayrı al (semantik analiz için)
        onceki_basla = max(0, basla - 50)
        onceki = metin[onceki_basla:basla].lower()
        sonraki_bitis = min(len(metin), bitis + 50)
        sonraki = metin[bitis:sonraki_bitis].lower()
        
        kelime_metin = metin[basla:bitis].lower()
        
        # ⭐ ÖZEL DURUM: "lan" - AKILLI KONTEKST ANALİZİ
        if kelime_metin == "lan":
            # Durum 1: "buraya lan", "oraya lan" - konumdan sonra = kaba söz (RİSK YÜKSEK)
            # Durum 2: "ya lan", "o lan", "ulan" = direkt argo (RİSK YÜKSEK)
            # Durum 3: "havalandı", "yuvarlandı" = embedded word (RİSK DÜŞÜK)
            
            # ✓ Kontrol 1: Konumsal adverblerden sonra "lan" = risky
            # "buraya lan", "oraya lan", "şuraya lan", vb.
            konum_lan_paternleri = [
                r'buraya\s+lan\b',   # "buraya lan"
                r'oraya\s+lan\b',    # "oraya lan"
                r'şuraya\s+lan\b',   # "şuraya lan"
                r'buradan\s+lan\b',  # "buradan lan"
                r'oradan\s+lan\b',   # "oradan lan"
                r'şuradan\s+lan\b',  # "şuradan lan"
                r'burada\s+lan\b',   # "burada lan"
                r'orada\s+lan\b',    # "orada lan"
                r'şurada\s+lan\b',   # "şurada lan"
            ]
            
            for patern in konum_lan_paternleri:
                if re.search(patern, kontekst):
                    return 4  # "buraya lan" = kaba söz (RİSK YÜKSEK)
            
            # ✓ Kontrol 2: Zararlı direkt patterns
            zararlı_lan_paternleri = [
                r'\bya\s+lan\b',    # "ya lan"
                r'\bo\s+lan\b',     # "o lan"
                r'\bha\s+lan\b',    # "ha lan"
                r'\bulan\b',        # "ulan"
                r'lan\s+be\b'       # "lan be"
            ]
            
            for patern in zararlı_lan_paternleri:
                if re.search(patern, kontekst):
                    return 4  # Argo hakaret
            
            # ✓ Kontrol 3: Embedded word (havalandı, sallandı) = harmless
            # Eğer öncesi harf ile bitiyorsa = bağlantılı = zararsız
            if onceki and onceki[-1].isalpha() and onceki[-1] not in 'aeiıouö':
                # Türkçe sessiz harf = bağlantılı kelime
                return 0  # Harmless embedded
            
            return 0  # Varsayılan: harmless
        
        # ⭐ ÖZEL DURUM: "kan" - AKILLI KONTEKST ANALİZİ
        if kelime_metin == "kan":
            # Durum 1: "kan dökmek", "kan akıyor" = şiddet (RİSK YÜKSEK)
            # Durum 2: "Serkan", "çalışkan" = isim/sıfat (RİSK DÜŞÜK)
            
            # ✓ Kontrol 1: Şiddet bağlamları
            zararlı_kan_paternleri = [
                r'kan\s+dök',       # "kan dökmek"
                r'kan\s+ak',        # "kan akmak"
                r'kan\s+saç',       # "kan saçmak"
                r'kanı\s+ak',       # "kanını akmak"
                r'kan\s+göl',       # "kan gölü"
                r'\bkanlı\b',       # "kanlı"
                r'kan\s+içinde',    # "kan içinde"
                r'kan\s+bulaş'      # "kan bulaşması"
            ]
            
            for patern in zararlı_kan_paternleri:
                if re.search(patern, kontekst):
                    return 4  # Şiddet bağlamı
            
            # ✓ Kontrol 2: Harmless patterns (isim, sıfat)
            harmless_kan_paternleri = [
                r'serkan',          # İsim
                r'çalışkan',        # Sıfat
                r'erkan',           # İsim
                r'turkmen|rukan'    # Diğer isimler
            ]
            
            for patern in harmless_kan_paternleri:
                if re.search(patern, metin[max(0, basla-20):bitis+20].lower()):
                    return 0  # Harmless
            
            return 0  # Varsayılan: harmless
        
        # ⭐ ÖZEL DURUM: "ayin" - AKILLI KONTEKST ANALİZİ
        if kelime_metin == "ayin":
            # Durum 1: "şeytani ayin", "kanlı ayin" = okültizm (RİSK YÜKSEK)
            # Durum 2: "yayınevi", "yayın" = yayın/basın (RİSK DÜŞÜK)
            
            # ✓ Kontrol 1: Okültizm bağlamları
            zararlı_ayin_paternleri = [
                r'ayin\s+yapma',    # "ayin yapma"
                r'ayin\s+sunumu',   # "ayin sunumu"
                r'ayin\s+sahne',    # "ayin sahne"
                r'kanlı\s+ayin',    # "kanlı ayin"
                r'şeytani\s+ayin',  # "şeytani ayin"
                r'ritüel\s+ayin',   # "ritüel ayin"
                r'gizli\s+ayin',    # "gizli ayin"
                r'okült\s+ayin',    # "okült ayin"
                r'ayin\s+ibadeti',  # "ayin ibadeti"
                r'ayinde\s+gece'    # "ayinde gece"
            ]
            
            for patern in zararlı_ayin_paternleri:
                if re.search(patern, kontekst):
                    return 4  # Okültizm
            
            # ✓ Kontrol 2: Harmless patterns (yayın, basın)
            if "yay" in onceki or "yay" in sonraki:
                return 0  # yayınevi, yayın = harmless
            
            return 0  # Varsayılan: harmless
        
        # ⭐ GENEL ZARARSIZ BAGLAMLAR (risk azalır)
        zararsiz_baglamlar = [
            "tarihî", "tarihen", "geçmişte", "orta çağda", 
            "metafor", "benzetme", "sembol", "kurmaca", "romanında",
            "hikâyede", "menkıbede", "sanki", "gibi", "hayal", "efsane",
            "antik", "antika", "müze", "araştırma", "bilimsel",
            "belgesel", "tarih kitabı", "dokümanter", "arkeoloji"
        ]
        
        for anahtar in zararsiz_baglamlar:
            if anahtar in kontekst:
                # Risk puanını 1-2 derece düşür
                return max(0, varsayilan_risk - 2)
        
        # ⭐ ZARARLI BAGLAMLAR (risk artar)
        zararlı_baglamlar = {
            "ölüm": ["ölüm sahnesi", "ölüm görüntüsü", "ölüm korkusu", "ölüm tehdit",
                     "ölüme götür", "öldür", "ölüm oyunu", "ölüm pıkırması"],
            "silah": ["silahla vurdu", "silah taşıyor", "silah kullanıyor", "tüfek",
                      "polis kurşunu", "silah çekti", "silah başında"],
            "şiddet": ["şiddet sahnesi", "dövüş sahne", "dövüldü", "baskı", "tecavüz",
                       "işkence", "şiddetli", "şiddetçe"],
            "cinayet": ["cinayeti işledi", "cinayet sahnesi", "öldürüldü", "katledildi"],
            "haram": ["haram eylem", "haram davranış", "günahkâr", "haram kılındı"]
        }
        
        kelime_arama = kelime_metin.replace("kan", "").replace("lan", "").replace("ayin", "")
        if kelime_arama:  # Diğer kelimeler için
            for anahtar_kelime, baglamlar in zararlı_baglamlar.items():
                if anahtar_kelime in kelime_metin:
                    for zararlı_baglamı in baglamlar:
                        if zararlı_baglamı in kontekst:
                            return min(5, varsayilan_risk + 2)
        
        # ⭐ CÜMLE-SEVİYESİ KONTEKST ANALİZİ (Yeni!)
        # Kelimenin bulunduğu cümleyi analiz et
        risk = self._cumle_konteksti_analiz_et(cumle_lower, kelime_metin, kategori, varsayilan_risk)
        if risk != varsayilan_risk:  # Eğer custom rule uygulandıysa
            return risk
        
        # Tarafsız bağlam - orijinal riski kullan
        return varsayilan_risk
    
    def _konteksti_al(self, metin: str, basla: int, bitis: int, 
                     etraf_uzunluk: int = 60) -> str:
        """Kelimeyi çevreleyen konteksti al"""
        
        kontekst_basla = max(0, basla - etraf_uzunluk)
        kontekst_bitis = min(len(metin), bitis + etraf_uzunluk)
        
        kontekst = metin[kontekst_basla:kontekst_bitis]
        
        # Kelimeyi vurgula
        goreli_basla = basla - kontekst_basla
        goreli_bitis = bitis - kontekst_basla
        
        kontekst = (
            kontekst[:goreli_basla] + 
            "[" + kontekst[goreli_basla:goreli_bitis] + "]" + 
            kontekst[goreli_bitis:]
        )
        
        return kontekst.strip()
    
    def _sayfa_numarasini_bul(self, metin: str, konum: int) -> int:
        """
        Verilen konumdaki sayfanın numarasını bul
        "--- SAYFA X ---" marker'ından hareketle
        """
        
        metin_oncesi = metin[:konum]
        
        # Son "SAYFA" marker'ını bul
        sayfa_markers = re.finditer(r'--- SAYFA (\d+) ---', metin_oncesi, flags=re.IGNORECASE)
        
        sayfa_num = 1
        for match in sayfa_markers:
            sayfa_num = int(match.group(1))
        
        return sayfa_num
    
    def _cumleyi_cikart(self, metin: str, basla: int, bitis: int) -> str:
        """
        Kelimenin bulunduğu cümleyi çıkart
        Cümle sınırlarını . ! ? ile belirle
        """
        # Geriye doğru cümle başını bul
        cumle_basla = basla
        for i in range(basla - 1, -1, -1):
            if metin[i] in '.!?':
                cumle_basla = i + 1
                break
            if i == 0:
                cumle_basla = 0
        
        # İleri doğru cümle sonunu bul
        cumle_sonu = bitis
        for i in range(bitis, len(metin)):
            if metin[i] in '.!?':
                cumle_sonu = i + 1
                break
            if i == len(metin) - 1:
                cumle_sonu = len(metin)
        
        cumle = metin[cumle_basla:cumle_sonu].strip()
        return cumle

    def _baglam_metin_temizle(self, metin: str) -> str:
        """PDF sayfa kirilmasi etiketlerini baglam analizinden temizler."""
        temiz = re.sub(r"-+\s*sayfa\s+\d+\s*-+", " ", metin, flags=re.IGNORECASE)
        temiz = re.sub(r"(?<=\s)\d{1,4}(?=[a-zçğıöşü])", " ", temiz)
        temiz = re.sub(r"\s+", " ", temiz)
        return temiz.strip()
    
    def _cumle_konteksti_analiz_et(self, cumle_lower: str, kelime: str, 
                                   kategori: str, varsayilan_risk: int) -> int:
        """
        Cümle bağlamına göre risk puanını belirle
        Kategori-spesifik kontekst kurallarını uygula
        
        CÜMLE İÇİNDEKİ ANLAMA BAKARAK RİSK KARAR VER
        """
        import re
        cumle_lower = self._baglam_metin_temizle(cumle_lower)
        
        # ⭐ KATEGORİ-SPESIFIK KONTEKST KURALLAR
        
        # 1️⃣ KABA DİL / HAKARET (kaba_dil_hakaret)
        if kategori == "kaba_dil_hakaret":
            # Harmless context (eğitim/açıklama amaçlı)
            harmless_patterns = [
                r'\butan[çc]\s+duygusu\b',
                r'\butan[çc]\b.{0,50}(?:mahcup|pi[şs]man|k[ıi]zar|ba[şs][ıi]m[ıi]\s+[öo]ne|a[ğg]lamak)',
                r'(?:mahcup|pi[şs]man|k[ıi]zar|ba[şs][ıi]m[ıi]\s+[öo]ne).{0,50}\butan[çc]\b',
                r'fazla\s+laubali',
                r'ba[şs][ıi]m[ıi]\s+[öo]ne\s+e[ğg]dim',
                r'pi[şs]manl[ıi]klar\s+denizinde',
                r'kelime.*dedi',
                r'kelime.*derken',
                r'kelime.*söyledi',
                r"'.*'.*kelime",  # Alıntı içinde
                r'kaba.*söz',
                r'argo.*kelime',
                r'kötü.*kelime',
                r'sözü.*anlam',
                r'ifade.*açıklanmaktadır',
                r'kullanılırken',
                r'örnek.*ver',
            ]
            
            for pattern in harmless_patterns:
                if re.search(pattern, cumle_lower):
                    return 0  # Eğitim/açıklama amaçlı → harmless
            
            # Harmful context (direkt hakaret)
            harmful_patterns = [
                r'!+\s*$',  # Cümle sonunda ünlem
                r'\bulan!',
                r'\blan!',
                r'buraya\s+lan',
                r'oraya\s+lan',
                r'şuraya\s+lan',
                r'ne\s+yapıyorsun',
            ]
            
            for pattern in harmful_patterns:
                if re.search(pattern, cumle_lower):
                    return 4  # Direkt hakaret → high risk
        
        # 2️⃣ ŞİDDET / SUÇLAR (siddet_suc)
        elif kategori == "siddet_suc":
            # Harmless context (tarihî, efsane, bilimsel)
            harmless_patterns = [
                r'tarih.*yılında',
                r'hikâyede',
                r'romanında',
                r'efsanede',
                r'mitoloji',
                r'antik.*çağda',
                r'sahnede.*gösterilir',
                r'filminde',
                r'resimde',
                r'kitapta',
                r'kütüphanede',
                r'müzede',
                r'bilimsel.*bağlamda',
                r'tarihî.*olaya',
                r'söylendiği',
                r'anlatıldığı',
                r'yazıldığı',
                r'gösterildiği',
            ]
            
            for pattern in harmless_patterns:
                if re.search(pattern, cumle_lower):
                    return max(0, varsayilan_risk - 2)  # Risk azalt
            
            # Harmful context (gerçekçi/ciddi) 
            harmful_patterns = [
                r'kan\s+(?:akmış|akıyor|akıp)',
                r'kan\s+dökülmüş',
                r'dövüldü',
                r'saldırılara',
                r'yaralandı',
                r'silahla',
                r'kurşunla',
                r'öldürdü',
                r'katledildi',
                r'tecavüz',
                r'işkence',
                r'şiddetli',
                r'savaşta',
                r'çarpışma',
                r'baskın',
            ]
            
            for pattern in harmful_patterns:
                if re.search(pattern, cumle_lower):
                    return 4  # Ciddi şiddet → high risk
        
        # 3️⃣ CİNSELLİK / MAHREMIYET (cinsellik_mahremiyet)
        elif kategori == "cinsellik_mahremiyet":
            # Harmless context (eğitim, sağlık)
            harmless_patterns = [
                r'cinsel.*eğitim',
                r'cinsel.*sağlık',
                r'üreme.*sistemi',
                r'biyoloji.*ders',
                r'bilimsel.*açıdan',
                r'tıbbi.*bilgi',
                r'doktor.*söyle',
                r'öğretmen.*anlat',
                r'psikolojist',
                r'uzman.*tarafından',
                # Çok anlamlı "ilişki": arkadaşlık, güven, tanışma ve sosyal bağlam
                r'\bilişki(?:miz|si|leri|m|n)?\b.{0,40}(?:arkadaş|dost|güven|tanış|bağ|iletişim|komşu|aile)',
                r'(?:arkadaş|dost|güven|tanış|bağ|iletişim|komşu|aile).{0,40}\bilişki(?:miz|si|leri|m|n)?\b',
                r'\bilişki(?:miz|si|leri|m|n)?\s+(?:daha\s+)?yeni\s+başlad[ıi]\b',
                r'karakterler\s+aras[ıi]\s+ilişki',
                r'sosyal\s+ilişki',
                # ⭐ AYIP - Harmless Patterns (verb conjugations with -ayıp/-eyip)
                r'katlayıp|katlamadan|katlayan',  # Folding (neutral action)
                r'başlayıp|başlamadan|başlayan',  # Starting (neutral action)
                r'yıkayıp|yıkamadan|yıkayan',  # Washing (neutral action)
                r'temizleyip|temizlemeden|temizleyen',  # Cleaning (neutral action)
                r'öğreneyip|öğrenmeden|öğrenen',  # Learning (neutral action)
                r'öğretyip|öğretmeden|öğreten',  # Teaching (neutral action)
                r'kurayıp|kurmadan|kuran',  # Building/setting up (neutral action)
                r'döşeyip|döşemeden|döşeyen',  # Paving (neutral action)
                r'oynayıp|oynamadan|oynayan',  # Playing (neutral action)
                r'atayıp|atmadan|atan',  # Throwing (neutral action)
                r'alayıp|almadan|alan',  # Taking (neutral action)
                r'koyayıp|koymadan|koyan',  # Putting (neutral action)
                r'tutayıp|tutmadan|tutuyan',  # Holding (neutral action)
                r'giyip|giymeden|giyen',  # Wearing (neutral action)
                r'çıkayıp|çıkmadan|çıkan',  # Exiting (neutral action)
                r'salayıp|salmadan|salan',  # Releasing (neutral action)
                r'dalayıp|dalmadan|dalan',  # Diving (neutral action)
                r'kalayıp|kalmadan|kalan',  # Remaining (neutral action)
                r'bulayıp|bulmadan|bulan',  # Finding (neutral action)
                r'korkayıp|korkmadan|korkan',  # Fear/afraid (emotion, not harmful)
                r'yaşlayıp|yaşlamadan|yaşlayan',  # Aging (natural process)
                r'saklayıp|saklamadan|saklayan',  # Hiding (neutral action)
            ]
            
            for pattern in harmless_patterns:
                if re.search(pattern, cumle_lower):
                    return 0  # Eğitim/verb conjugation → harmless
            
            # Harmful context (cinsel saldırı, istismar)
            harmful_patterns = [
                r'cinsel.*saldırı',
                r'cinsel.*istismar',
                r'cinsel\s+ilişki',
                r'ilişki(?:ye|ye\s+girmek|ye\s+zorlamak)',
                r'bedensel\s+yak[ıi]nl[ıi]k',
                r'tecavüz',
                r'ayartma',
                r'arzu.*ettirme',
                r'fuhuş',
            ]
            
            for pattern in harmful_patterns:
                if re.search(pattern, cumle_lower):
                    return 5  # Çok yüksek risk
        
        # 4️⃣ OKÜLTIZM / BATIL (okültizm_batıl)
        elif kategori == "okültizm_batıl":
            # Harmless context (tarihî, müze, araştırma, doğa)
            harmless_patterns = [
                r'antik\s+(?:ayin|ritüel)',
                r'müzede.*sergilenen',
                r'tarihî.*ayin',
                r'araştırma.*kapsamında',
                r'akademik.*çalışma',
                r'mitoloji.*bağlamında',
                r'arkeoloji',
                r'antropoloji',
                r'kültür.*mirası',
                # ⭐ GÖKKUŞAĞI - Harmless Patterns
                r'gökkuşağı.*(?:rengi|renginde|görmek|var)',  # Doğal renk tanımı
                r'gökkuşağı.*(?:kuş|çiçek|ağaç)',  # Doğada görülür
                r'gökkuşağı.*(?:hikâye|masala|çocuk)',  # Çocuk hikâyeleri
                r'gökkuşağı.*(?:ressam|sanatçı|resim)',  # Sanat bağlamı
                r'gökkuşağı.*(?:bulut|yağmur|güneş)',  # Meteoroloji
                r'gökkuşağı.*(?:kitap|roman|öykü)',  # Edebiyat bağlamı
                r'gökkuşağı.*(?:tasarım|desen|motif)',  # Tasarım elemanı
                r'gökkuşağı\s+(?:çiçeği|kuşu|yolu)',  # Adı taşıyan şeyler
                r'(?:at|bul|gör|ara).*gökkuşağı',  # Bir şey "at/bul/gör" fiili ile
                r'\bbüyü\s+bozul(?:ur|mas[ıi]n|du|acak)\b',  # Mecazi: mutlu/özel anın etkisi bozulmasın
                r'\bbüyüsü\s+bozul(?:ur|mas[ıi]n|du|acak)\b',  # Mecazi: cazibe/atmosfer etkisi
                r'\bbüyüleyici\b',  # Estetik/duygusal beğeni
            ]
            
            for pattern in harmless_patterns:
                if re.search(pattern, cumle_lower):
                    return 0  # Bilimsel/doğal → harmless
            
            # Harmful context (gerçekçi okültizm)
            harmful_patterns = [
                r'şeytani\s+ayin',
                r'kara\s+sihir',
                r'kanlı\s+ayin',
                r'gizli\s+ritüel',
                r'okült\s+(?:ayin|ritüel)',
                r'ayin.*yapma',
                r'adama.*ibadet',
                r'cinlere\s+tazim',
                # ⭐ GÖKKUŞAĞI - Harmful Patterns  
                r'gökkuşağı\s+(?:sembolü|göndermesi|ritüeli|mistik)',  # Sembolik/batıl bağlam
            ]
            
            for pattern in harmful_patterns:
                if re.search(pattern, cumle_lower):
                    return 4  # Yüksek risk → okültizm
        
        # 5️⃣ UYUŞTURUCU (uyusturucu)
        elif kategori == "uyusturucu":
            # Harmless context (eğitim, uyarı)
            harmless_patterns = [
                r'uyuşturucu.*tehlikesi',
                r'uyuşturucu.*kötülükleri',
                r'uyuşturucu.*yasaklanmıştır',
                r'tıbbi.*amaçla',
                r'doktor.*reçete',
                r'ilaç.*tedavi',
                r'sağlık.*hizmet',
                r'hastane.*kullanılan',
                r'bilimsel.*çalışma',
                r'eğitim.*amaçlı',
            ]
            
            for pattern in harmless_patterns:
                if re.search(pattern, cumle_lower):
                    return 0  # Eğitim → harmless
            
            # Harmful context (kullanım, bağımlılık)
            harmful_patterns = [
                r'uyuşturucu.*kullanıyor',
                r'uyuşturucu.*aldı',
                r'bağımlı',
                r'eroin.*hazırla',
                r'kokain.*al',
                r'esrar.*iç',
                r'alkol.*içti',
            ]
            
            for pattern in harmful_patterns:
                if re.search(pattern, cumle_lower):
                    return 4  # Yüksek risk
        
        # 6️⃣ ZARIRLI ALIŞKANLIKLARI (sigara, alkol, nargile, vb.)
        elif kategori == "zararlı_alışkanlıklar":
            # Harmless context: Eğitsel, tarihsel, eleştirel kullanım
            harmless_patterns = [
                # ✅ EĞİTSEL KULLANIM (Uyarı, öğretim, sağlık bilgisi)
                r'sağlığa\s+(?:zararlı|kötü|zarar)',  # "sağlığa zararlı"
                r'(?:zararlarını|sakıncalarını|olumsuz.*etkilerini)',  # Zararları anlatma
                r'tehlikesi',  # "sigara tehlikesi"
                r'riskli',  # "riskli alışkanlık"
                r'hastalık.*sebep',  # Hastalık sebebi
                r'doktor.*(?:söyledi|tavsiye|belirtti)',  # Doktor tavsiyesi
                r'profesyonel.*(?:açıdan|tarafından)',  # Uzman görüşü
                r'bilimsel.*(?:araştırma|bulgu)',  # Bilimsel bağlam
                r'tıbbi.*perspektif',  # Tıbbi bağlam
                r'sağlık.*eğitim',  # Sağlık eğitimi
                r'uyarı.*vermek',  # Uyarı verme
                r'bilinç.*(?:artırma|yükseltme)',  # Bilinç yükseltme
                r'eğitim.*amaçlı',  # Eğitim amaçlı kullanım
                r'öğretmen.*anlat',  # Öğretmen anlatımı
                r'kitapta.*açıklanır',  # Kitapta açıklanma
                
                # ✅ TARİHSEL KULLANIM (Geçmiş, tarih, eski zamanlar)
                r'tarih.*yılında',  # "tarih 1950 yılında"
                r'eski\s+zamanlarda',  # Eski zamanlar
                r'geçmişte',  # Geçmiş zamanda
                r'antik\s+(?:çağda|dönemde)',  # Antik çağ
                r'ortaçağ',  # Ortaçağ
                r'19\..*yüzyıl',  # 19. yüzyıl
                r'tarih.*kütüphanede',  # Tarihî bağlam müze/kütüphane
                r'müze.*sergilenen',  # Müzede sergilenen
                r'arkeoloji',  # Arkeoloji
                
                # ✅ ELEŞTİREL KULLANIM (Olumsuz eleştiri, sorunlar)
                r'sorunludur',  # "sorunludur"
                r'çekilmez',  # "çekilmez alışkanlık"
                r'olumsuz.*davranış',  # Olumsuz davranış
                r'yanlış.*seçim',  # Yanlış seçim
                r'kötü.*tercih',  # Kötü tercih
                r'kaçınılması',  # Kaçınılması gereken
                r'saklanması',  # Saklanması gereken
                r'tutulmaması',  # Tutulmaması gereken
                r'olumsuz.*karakter',  # Olumsuz karakter özelliği
                r'hata.*gerçekleştir',  # Hata yapan karakter
            ]
            
            for pattern in harmless_patterns:
                if re.search(pattern, cumle_lower):
                    return 0  # Eğitsel/tarihsel/eleştirel → harmless
            
            # Harmful context: Özendirici, taklit teşviki, pozitif gösterim
            harmful_patterns = [
                # ❌ ÖZENDİRİCİ KULLANIM (Pozitif nitelemeler)
                r'güzel.*(?:tadı|aroması|his)',  # "güzel tadı"
                r'tadı.*güzel',  # "tadı güzel"
                r'lezzetli',  # "lezzetli"
                r'hoş.*his',  # "hoş his"
                r'rahatlatan',  # "rahatlatan"
                r'rahat\s+(?:hissettir|eder)',  # "rahat ettirme"
                r'keyif.*(?:al|ver)',  # "keyif alma/verme"
                r'zevk\s+(?:al|ver)',  # "zevk alma/verme"
                r'eğlence.*sunmak',  # "eğlence sunmak"
                r'eğlenceliydi',  # "eğlenceliydi"
                r'harika.*his',  # "harika his"
                r'iyi.*(?:geldi|hissetti)',  # "iyi geldi"
                r'doyurucu',  # "doyurucu"
                r'tatmin\s+(?:edici|ettirici)',  # "tatmin edici"
                r'sevdiği.*alışkanlık',  # "sevdiği alışkanlık"
                r'sevindirici',  # "sevindirici"
                
                # ❌ TAKLİT TEŞVİKİ (Deneme, başlama, taklit)
                r'deneme.*gerek',  # "deneme gerek"
                r'deneyin',  # "deneyin"
                r'başla(?:r|yın|ması)',  # "başla", "başlayın", "başlaması"
                r'al(?:ıp|ın)',  # "al", "alıp", "alın"
                r'tut(?:abilir|uş)',  # "tutabilir", "tutuş"
                r'içmeyi.*başlad',  # "içmeyi başladı"
                r'kullanmaya.*başlad',  # "kullanmaya başladı"
                r'ilk.*(?:sigara|alkol|içki)',  # "ilk sigara"
                r'merak.*tat',  # "merak tat"
                r'prob\w+',  # Probando, prob... gibi
                r'arkadaş.*(?:çalışkan|hep)',  # "arkadaş... çalışkan/hep"
                
                # ❌ POZİTİF GÖSTERİM (Karakterin pozitif eylemi olarak)
                r'sevinçle.*(?:sigara|alkol)',  # "sevinçle sigara"
                r'mutlu.*(?:sigara|alkol)',  # "mutlu sigara"
                r'başarı.*(?:sonra|ardından).*(?:sigara|alkol)',  # Başarı → sigara
                r'gurur.*(?:sigara|alkol)',  # "gurur sigara"
                r'başarılı.*(?:sigara|alkol)',  # Başarılı karakter sigara içiyor
                r'rol.*model.*(?:sigara|alkol)',  # Rol model sigara içiyor
                r'beğenilen.*(?:sigara|alkol)',  # Beğenilen karakter
                r'harika.*karakter.*(?:sigara|alkol)',  # Harika karakter
                r'sempati.*(?:sigara|alkol)',  # Sempati çeken karakter
                r'saygı\s+gördü.*(?:sigara|alkol)',  # Saygı görüyorken
                r'kahraman.*(?:sigara|alkol)',  # Kahraman karakter
                r'(?:erkek|kız)\s+(?:çok|baya).*(?:sigara|alkol)',  # "Çok sigara içen kız"
            ]
            
            for pattern in harmful_patterns:
                if re.search(pattern, cumle_lower):
                    return 4  # Özendirici/taklit teşviki/pozitif → high risk
        
        # Varsayılan: özel rule uygulanmadı → original risk
        return varsayilan_risk
    

    def _ai_baglam_analizi(self, bulgu: dict, varsayilan_risk: int, kural_riski: int) -> dict:
        """
        AI baglam analizi icin tek cikis modeli.

        Groq istemcisi hazir degilse ayni ilkeleri deterministik fallback uygular.
        Bu katman kelime eslesmesini tek basina risk saymaz; risk kararini cumle
        baglamindan uretir.
        """
        cumle = bulgu.get("cumle", "")
        cumle_lower = cumle.lower()
        kelime = bulgu.get("kelime", "").lower()

        baglam_tipi, gerekce = self._baglam_tipini_belirle(cumle_lower, kelime)

        risksiz_tipler = {
            "egitsel", "mecazi", "elestirel", "sosyal_iliskiler",
            "aile_bosanma_notr", "romantik_iliskiler_uygun",
            "sosyal_mahcubiyet", "duygusal_tepki", "betimleyici",
            "teknik", "olay_orgusu", "tarihsel", "notr"
        }
        if baglam_tipi in risksiz_tipler:
            risk = 0
        elif baglam_tipi in {
            "zararli_aliskanlik_sahnelenmesi",
            "siddet_sahnelenmesi",
            "suc_sahnelenmesi",
            "tehlikeli_davranis_sahnelenmesi",
            "aile_mahremiyet_sahnelenmesi",
        }:
            risk = max(1, min(2, kural_riski or varsayilan_risk or 1))
        elif baglam_tipi == "romantik_fiziksel_temas":
            risk = 2
        elif baglam_tipi == "evlilik_disi_iliski":
            risk = 2
        elif baglam_tipi == "aile_butunlugu_olumsuz_ozendirme":
            risk = 3
        elif baglam_tipi == "cinsel_cagrisim":
            risk = max(3, min(5, kural_riski or varsayilan_risk))
        elif baglam_tipi in {"ozendirici", "taklit_tesviki", "pozitif_gosterim"}:
            risk = max(1, min(5, kural_riski or varsayilan_risk))
        else:
            risk = max(0, min(5, kural_riski))

        karar = self._baglam_kararini_siniflandir(risk, baglam_tipi)

        return {
            "bulguVar": True,
            "problemliMi": risk > 0,
            "riskPuani": risk,
            "baglamTipi": baglam_tipi,
            "gerekce": gerekce,
            "uyariMetni": "" if risk == 0 else self._uyari_metni_olustur(bulgu, baglam_tipi, risk),
            **karar
        }

    def _baglam_tipini_belirle(self, cumle_lower: str, kelime: str) -> Tuple[str, str]:
        """Cumlenin kullanim tipini belirler."""
        cumle_lower = self._baglam_metin_temizle(cumle_lower)
        egitsel = [
            r"sa\u011fl\u0131\u011fa\s+(?:zarar|zararl\u0131)",
            r"zararlar[\u0131i]", r"sak\u0131ncalar[\u0131i]",
            r"tehlike(?:si)?", r"risk(?:li|leri)?", r"uyar[\u0131i]",
            r"anlat(?:t[\u0131i]|[\u0131i]ld[\u0131i]|[\u0131i]l[\u0131i]r|mak)",
            r"a\u00e7\u0131kla", r"e\u011fitim", r"\u00f6\u011fretmen", r"doktor", r"bilimsel", r"ders"
        ]
        tarihsel = [
            r"tarih", r"ge\u00e7mi\u015fte", r"eski\s+zaman", r"antik",
            r"orta\s*\u00e7a\u011f", r"y\u00fczy\u0131l", r"osmanl[\u0131i]",
            r"m\u00fcze", r"arkeoloji", r"i\u015fgal", r"m\u00fctareke",
            r"kuvay[\u0131i]\s+milliye", r"mill[\u00eei]\s+m\u00fccadele",
            r"pera", r"beyo\u011flu", r"galata", r"meddah", r"d\u00f6nem",
            r"d\u00f6nemin", r"frans[\u0131i]z\s+(?:asker|subay|parti)",
            r"rum\s+karakter", r"az[\u0131i]nl[\u0131i]k", r"\b191[89]\b", r"\b192[0-3]\b"
        ]
        mecazi = [
            r"mecaz", r"metafor", r"benzetme", r"sembol", r"sanki", r"\bgibi\b", r"adeta",
            r"\u00e7[\u0131i]plak\s+ayak", r"zafer\s+sarho\u015f", r"manzara\s+sarho\u015f",
            r"efsunlu.*sarho\u015f", r"falta\u015f[\u0131i]", r"karma\s+tak[\u0131i]m",
            r"g\u00fcvercin", r"\bbiraz\b", r"\bb\u0131rak", r"\u00e7al\u0131\u015fkan",
            r"kanun", r"kan[\u0131i]t", r"itibar", r"roman", r"soluk", r"solgun",
            r"\bb\u00fcy\u00fc\s+bozul(?:ur|mas[\u0131i]n|du|acak)\b",
            r"\bb\u00fcy\u00fcs\u00fc\s+bozul(?:ur|mas[\u0131i]n|du|acak)\b",
            r"\bb\u00fcy\u00fcleyici\b"
        ]
        elestirel = [
            r"ele\u015ftir", r"yanl[\u0131i]\u015f", r"k\u00f6t\u00fc", r"olumsuz",
            r"ka\u00e7[\u0131i]n[\u0131i]lmas[\u0131i]", r"sak[\u0131i]n", r"yasak",
            r"zararl[\u0131i]\s+al[\u0131i]\u015fkanl[\u0131i]k", r"b[\u0131i]rakmas[\u0131i]", r"pi\u015fman",
            r"meyhane.*(?:ele\u015ftir|dolu)", r"i\u015fgalci", r"sefahat",
            r"hak\s+ihlali", r"tecav\u00fcz\s+ve\s+ihanet", r"asker[\u00eei]\s+ba\u011flam",
            r"cinsel\s+i\u00e7erik\s+de\u011fil", r"yoksullu\u011funu\s+simgeler",
            r"\bay[\u0131i]p\s+(?:olur|etme|de\u011fil)\b"
        ]
        sosyal_iliskiler = [
            r"\bili\u015fki(?:miz|si|leri|m|n)?\b.{0,40}(?:arkada\u015f|dost|g\u00fcven|tan[\u0131i]\u015f|ba\u011f|ileti\u015fim|kom\u015fu|aile)",
            r"(?:arkada\u015f|dost|g\u00fcven|tan[\u0131i]\u015f|ba\u011f|ileti\u015fim|kom\u015fu|aile).{0,40}\bili\u015fki(?:miz|si|leri|m|n)?\b",
            r"\bili\u015fki(?:miz|si|leri|m|n)?\s+(?:daha\s+)?yeni\s+ba\u015flad[\u0131i]\b",
            r"karakterler\s+aras[\u0131i]\s+ili\u015fki",
            r"sosyal\s+ili\u015fki"
        ]
        aile_bosanma_notr = [
            r"(?:anne|baba|ebeveyn).{0,40}bo\u015fan(?:m\u0131\u015f|d\u0131|ma)",
            r"bo\u015fan(?:m\u0131\u015f|d\u0131|ma).{0,40}(?:anne|baba|ebeveyn|aile)",
            r"ayr[\u0131i]\s+ya\u015f(?:ar|ama|[ıi]yor)",
            r"aile\s+i\u00e7i\s+sorun",
            r"anne\s+ve\s+babas[\u0131i].{0,40}bo\u015fanm[\u0131i]\u015ft[\u0131i]",
            r"\be\u015f(?:i|ler)?\b", r"\bkar[\u0131i]\b", r"\bkoca(?:s[\u0131i])?\b",
            r"evlilik(?:leri|leri|leri)?\s+(?:s\u00fcr|devam|vard[\u0131i])"
        ]
        romantik_iliskiler_uygun = [
            r"birbirlerini\s+sev(?:iyor|iyorlard[\u0131i]|di|mi\u015f)",
            r"ya\u015f\s+grubuna\s+uygun.{0,40}(?:romantik|sevgili|fl\u00f6rt)",
            r"(?:sevgili|ni\u015fanl[\u0131i]|fl\u00f6rt).{0,40}(?:masum|uygun|sayg[\u0131i]l[\u0131i])",
            r"(?:birbirlerine|ona|birbirini).{0,30}sevgi(?:yle|li|sini)",
            r"romantik\s+duygu"
        ]
        romantik_fiziksel_temas = [
            r"dudaktan\s+\u00f6p",
            r"uzun\s+s\u00fcre(?:li)?\s+\u00f6p",
            r"yo\u011fun\s+romantik\s+temas",
            r"sar[\u0131i]larak\s+yat",
            r"mahrem\s+(?:fiziksel\s+)?yak[\u0131i]nla\u015f",
            r"fiziksel\s+yak[\u0131i]nla\u015f",
            r"\u00f6p\u00fc\u015f(?:t\u00fc|me|mek|mesi)"
        ]
        evlilik_disi_iliski = [
            r"evlilik\s+d[\u0131i]\u015f[\u0131i]\s+ili\u015fki",
            r"evli\s+oldu\u011fu\s+halde.{0,50}(?:ili\u015fki|sevgili|fl\u00f6rt)",
            r"ba\u015fkas[\u0131i]yla\s+ili\u015fki",
            r"yasak\s+a\u015fk"
        ]
        aile_butunlugu_olumsuz_ozendirme = [
            r"ailesinden\s+kurtuldu\u011fu\s+i\u00e7in\s+\u00e7ok\s+mutluydu",
            r"(?:bo\u015fanma|ayr[\u0131i]\s+ya\u015fama).{0,50}(?:en\s+iyi|ideal|harika|mutlu|kurtulu\u015f)",
            r"aile(?:den|sinden).{0,40}kurtul(?:mak|du|du\u011fu).{0,40}(?:mutlu|rahat|harika)",
            r"evlilik\s+d[\u0131i]\u015f[\u0131i]\s+ili\u015fki.{0,50}(?:g\u00fczel|ideal|harika|mutlu|do\u011fru)"
        ]
        cinsel_cagrisim = [
            r"cinsel\s+(?:i\u00e7erik|konu\u015fma|ima|ça\u011fr[\u0131i]\u015f[\u0131i]m)",
            r"cinsel\s+ili\u015fki",
            r"ili\u015fki(?:ye|ye\s+girmek|ye\s+zorlamak)",
            r"erotik", r"arzu\s+ve\s+tensellik", r"tensel",
            r"mahrem\s+b\u00f6lge", r"beden(?:i|sel).{0,30}(?:arzu|tensel|erotik)",
            r"\u00e7[\u0131i]plakl[\u0131i]k", r"uygunsuz\s+beden"
        ]
        sosyal_mahcubiyet = [
            r"\butan[çc]\s+duygusu\b",
            r"\butan[çc]\b.{0,80}(?:mahcup|pi[şs]man|k[ıi]zar|ba[şs][ıi]m[ıi]\s+[öo]ne|a[ğg]lamak)",
            r"(?:mahcup|pi[şs]man|k[ıi]zar|ba[şs][ıi]m[ıi]\s+[öo]ne).{0,80}\butan[çc]\b",
            r"fazla\s+laubali",
            r"pi[şs]manl[ıi]klar\s+denizinde",
            r"yorgan[ıi]\s+[üu]st[üu]me\s+[çc]ekip",
        ]
        duygusal_tepki = [
            r"deh\u015fet(?:ten|le)?\s+kocaman\s+olmu\u015f\s+g\u00f6z",
            r"deh\u015fet(?:ten|le)?.{0,40}g\u00f6zlerimizle\s+birbirimize\s+bakt[\u0131i]k",
            r"g\u00f6zleri(?:miz)?\s+deh\u015fet(?:ten|le)?.{0,30}kocaman",
            r"bir\s+anda\s+deh\u015fet(?:le|ten)?\s+bakt",
        ]
        betimleyici = [
            r"\bgibi\b", r"\bsanki\b", r"\badeta\b", r"benzet", r"tasvir",
            r"g\u00f6r\u00fcn(?:d\u00fc|mez|en|iyor)", r"ses(?:i)?", r"rengi", r"koku(?:su)?",
            r"so\u011fuk", r"sinsi", r"korkun\u00e7\s+g\u00f6r\u00fcn", r"betimle"
        ]
        teknik = [
            r"teknik", r"terim", r"s\u00f6zl\u00fck", r"ansiklopedi", r"bilimsel",
            r"t\u0131bbi", r"hukuki", r"akademik", r"kavram", r"tan\u0131m"
        ]
        guvenli_betimleyici = [
            r"\b(?:\u0131\u015f[\u0131i]\u011f[\u0131i]n|g\u00fcne\u015fin|ay[\u0131i]n)\s+vur(?:du\u011fu|du|an).{0,30}(?:duvar|tavan|cam|y\u00fczey)",
            r"vur(?:du\u011fu|du|an).{0,30}(?:duvar|tavan|cam|y\u00fczey)",
            r"sa\u00e7lar[\u0131i]n[\u0131i]\s+topuz\s+yap",
            r"\btopuz\s+(?:sa\u00e7|yap)",
        ]
        olay_orgusu = [
            r"karakter", r"kahraman", r"anlat\u0131", r"olay", r"sahne",
            r"hikaye", r"\u00f6yk\u00fc", r"roman", r"masal", r"dedi", r"diye",
            r"yapt\u0131", r"oldu", r"g\u00f6rd\u00fc", r"korktu", r"ka\u00e7t\u0131",
            r"hata", r"su\u00e7", r"ceza", r"pi\u015fman", r"sonu\u00e7"
        ]
        ozendirici = [
            r"\u00e7ok\s+sev(?:er|iyordu|di)", r"sevdi\u011fi", r"keyif", r"zevk",
            r"rahatlat", r"g\u00fczel", r"harika", r"e\u011flenceli", r"lezzetli", r"iyi\s+geldi",
            r"haval[\u0131i]\s+g\u00f6ster"
        ]
        taklit = [
            r"deneyin", r"dene(?:yin|mek)?",
            r"(?:sigara|alkol|i\u00e7ki|uyu\u015fturucu|madde).{0,24}ba\u015fla(?:d[\u0131i]|mak|y[\u0131i]n)",
            r"ba\u015fla(?:d[\u0131i]|mak|y[\u0131i]n).{0,24}(?:sigara|alkol|i\u00e7ki|uyu\u015fturucu|madde)",
            r"taklit", r"sen\s+de", r"yapmay[\u0131i]\s+\u00f6\u011fren", r"nas[\u0131i]l\s+yap"
        ]
        pozitif = [
            r"kahraman.*" + re.escape(kelime), r"ba\u015far[\u0131i]l[\u0131i].*" + re.escape(kelime),
            r"sayg[\u0131i]\s+g\u00f6r.*" + re.escape(kelime), r"rol\s+model.*" + re.escape(kelime),
            r"g\u00fc\u00e7l\u00fc.*" + re.escape(kelime)
        ] if kelime else []
        zararli_aliskanlik_sahnelenmesi = [
            r"(?:fosur\s+fosur\s+)?sigara.{0,30}i\u00e7(?:erdi|er|ti|iyor|mek|meyi|mi\u015f)",
            r"i\u00e7(?:erdi|er|ti|iyor|mek|meyi|mi\u015f).{0,30}(?:sigara|alkol|i\u00e7ki|\u015farap|bira|rak[\u0131i])",
            r"(?:alkol|i\u00e7ki|\u015farap|bira|rak[\u0131i]).{0,30}(?:i\u00e7|kullan|al)",
            r"sarho\u015f(?:tu|tu|tu\u011fu|oldu|olmak|dur|ken)",
            r"g\u00fcn\u00fcn\s+yirmi\s+d\u00f6rt\s+saati\s+sarho\u015f",
            r"kumar.{0,30}(?:oyna|oynad[\u0131i]|oynuyor|oynamak)",
            r"uyu\u015fturucu.{0,30}(?:kullan|kulland[\u0131i]|ald[\u0131i]|almak)",
        ]
        siddet_sahnelenmesi = [
            r"\bkavga\s+et(?:ti|mek|tiler|iyor)",
            r"\bd\u00f6v\u00fc\u015f(?:t\u00fc|mek|tiler|l\u00fc)",
            r"\bd\u00f6v(?:d\u00fc|mek|er|m\u00fc\u015f)\b",
            r"adam[\u0131i]\s+d\u00f6vd\u00fc",
            r"\u015fiddet\s+uygula",
            r"\byarala(?:d[\u0131i]|mak)",
            r"\bb[\u0131i]\u00e7akla(?:d[\u0131i]|mak)",
        ]
        siddet_referansi_dusuk = [
            r"(?:kavgal[\u0131i]|d\u00f6v\u00fc\u015fl\u00fc|\u015fiddetli).{0,35}film(?:i|ler|leri|lerdeki)?"
            r".{0,35}(?:sever(?:dik|di|im)?|izler(?:dik|di|im)?|ho\u015flan(?:\u0131r|irdik|d\u0131k)|an[\u0131i])",
            r"film(?:i|ler|leri|lerdeki)?.{0,35}(?:kavgal[\u0131i]|d\u00f6v\u00fc\u015fl\u00fc|\u015fiddetli)"
            r".{0,35}(?:sever(?:dik|di|im)?|izler(?:dik|di|im)?|ho\u015flan(?:\u0131r|irdik|d\u0131k)|an[\u0131i])",
        ]
        suc_sahnelenmesi = [
            r"h[\u0131i]rs[\u0131i]zl[\u0131i]k\s+yap",
            r"\b\u00e7al(?:d[\u0131i]|mak|m[\u0131i]\u015f)\b",
            r"\bsu\u00e7\s+i\u015fle",
        ]
        tehlikeli_davranis_sahnelenmesi = [
            r"silah\s+kullan",
            r"(?:tabanca|t\u00fcfek|b[\u0131i]\u00e7ak|patlay[\u0131i]c[\u0131i]).{0,30}(?:kullan|ate\u015fle|salla|savur)",
            r"tehlikeli\s+davran[\u0131i]\u015f\s+sergile",
        ]

        fiil_nesne_karari = self._siddet_fiil_nesne_baglamini_belirle(cumle_lower)
        if fiil_nesne_karari:
            return fiil_nesne_karari

        kontrol_listesi = [
            ("sosyal_mahcubiyet", sosyal_mahcubiyet, "Sosyal mahcubiyet ve içsel pişmanlık bağlamı; mahrem/cinsel anlam taşımıyor."),
            ("duygusal_tepki", duygusal_tepki, "Kısa süreli korku/şaşkınlık tepkisi; travmatik ayrıntı veya özendirme yok."),
            ("egitsel", egitsel, "Eğitsel/uyarıcı kullanım risk oluşturmaz."),
            ("tarihsel", tarihsel, "Tarihsel veya kültürel aktarım bağlamı."),
            ("teknik", teknik, "Teknik/terimsel kullanım; davranışı olumlamaz veya özendirmez."),
            ("sosyal_iliskiler", sosyal_iliskiler, "Sosyal/arkadaşlık ilişkisi bağlamı; cinsel anlam taşımıyor."),
            ("aile_bosanma_notr", aile_bosanma_notr, "Aile, evlilik veya boşanma yalnızca olay bilgisi olarak geçiyor; özendirme yok."),
            ("romantik_iliskiler_uygun", romantik_iliskiler_uygun, "Yaş grubuna uygun romantik/duygusal ilişki; mahrem görünürlük veya özendirme yok."),
            ("mecazi", mecazi, "Mecazi/sembolik kullanım."),
            ("siddet_referansi_dusuk", siddet_referansi_dusuk, "Şiddet/kavga ifadesi geçmiş izleme tercihi veya film referansı olarak geçiyor; davranış sahnelenmiyor."),
            ("betimleyici", guvenli_betimleyici, "Betimleyici/teknik kullanım; fiili risk davranışı sahnelenmiyor."),
            ("betimleyici", betimleyici, "Betimleyici kullanım; sakıncalı davranışı olumlamaz."),
            ("elestirel", elestirel, "Eleştirel veya olumsuzlayıcı kullanım."),
            ("cinsel_cagrisim", cinsel_cagrisim, "Cinsel çağrışım, tensellik veya mahrem beden odağı içeriyor."),
            ("aile_butunlugu_olumsuz_ozendirme", aile_butunlugu_olumsuz_ozendirme, "Aile bütünlüğünü zedeleyen davranış ideal/olumlu çözüm gibi sunuluyor."),
            ("taklit_tesviki", taklit, "Taklit etmeye veya denemeye yönelten kullanım."),
            ("pozitif_gosterim", pozitif, "Sakıncalı unsur olumlu karakter/başarı ile ilişkilendirilmiş."),
            ("ozendirici", ozendirici, "Özendirici veya olumlayıcı kullanım."),
            ("romantik_fiziksel_temas", romantik_fiziksel_temas, "Çocuk/ortaokul okuru açısından romantik veya mahrem fiziksel temas görünürlüğü var."),
            ("evlilik_disi_iliski", evlilik_disi_iliski, "Evlilik dışı ilişki olay örgüsünde geçiyor; editoryal düşük risk incelemesi gerekir."),
            ("zararli_aliskanlik_sahnelenmesi", zararli_aliskanlik_sahnelenmesi, "Zararlı alışkanlık yalnızca ad olarak geçmiyor; davranış metinde sahneleniyor. Özendirme olmasa da düşük risk incelemesi gerekir."),
            ("siddet_sahnelenmesi", siddet_sahnelenmesi, "Şiddet/kavga/dövüş davranışı metinde sahneleniyor. Özendirme olmasa da düşük risk incelemesi gerekir."),
            ("suc_sahnelenmesi", suc_sahnelenmesi, "Suç davranışı olay içinde fiilen gerçekleşiyor. Özendirme olmasa da düşük risk incelemesi gerekir."),
            ("tehlikeli_davranis_sahnelenmesi", tehlikeli_davranis_sahnelenmesi, "Silah veya tehlikeli davranış metinde sahneleniyor. Özendirme olmasa da düşük risk incelemesi gerekir."),
            ("olay_orgusu", olay_orgusu, "Olay örgüsü içinde geçen referans; anlatıcının olumlama mesajı yok.")
        ]

        for baglam_tipi, patternler, gerekce in kontrol_listesi:
            if any(re.search(pattern, cumle_lower) for pattern in patternler):
                return baglam_tipi, gerekce

        return "notr", "Tam kelime bulundu; özendirme, normalleştirme veya olumlama bağlamı saptanmadığı için risk oluşturmaz."

    def _siddet_fiil_nesne_baglamini_belirle(self, cumle_lower: str) -> Optional[Tuple[str, str]]:
        """
        Dovmek/vurmak gibi fiilleri nesnesiyle birlikte degerlendirir.
        Canliya yonelmeyen kullanimlar siddet sayilmaz.
        """
        siddet_fiili = re.search(
            r"\b(?:d[oö]v(?:d[uü]|mek|er|m[uü][sş])|vur(?:du|mak|uyor|an|arak))\b",
            cumle_lower
        )
        if not siddet_fiili:
            return None

        cansiz_nesneler = [
            "ayran", "ayranı", "ayrani", "hamur", "hamuru", "bakır", "bakiri", "bakırı", "kumaş", "kumasi", "kumaşı",
            "metal", "demir", "kapı", "kapi", "duvar", "tavan", "cam", "yüzey", "yuzey",
            "davul", "halı", "hali", "kilim", "toprak"
        ]
        canli_nesneler = [
            "adam", "adamı", "adami", "kadın", "kadini", "kadını", "erkek", "çocuk", "cocuk",
            "çocuğu", "cocugu", "insan", "kişi", "kisi", "öğrenci", "ogrenci", "arkadaş",
            "arkadas", "komşu", "komsu", "komşusunu", "komsusunu", "köpek", "kopek", "köpeği",
            "kopegi", "kedi", "kediyi", "hayvan", "hayvanı", "hayvani", "onu", "beni",
            "seni", "bizi", "sizi", "onları", "onlari"
        ]

        yakin_baglam = cumle_lower[:siddet_fiili.start()][-45:]
        if any(re.search(rf"\b{re.escape(nesne)}\b", yakin_baglam) for nesne in cansiz_nesneler):
            return "betimleyici", "Fiil cansız/teknik nesneye yöneliyor; şiddet davranışı sahnelenmiyor."

        if any(re.search(rf"\b{re.escape(nesne)}\b", yakin_baglam) for nesne in canli_nesneler):
            return "siddet_sahnelenmesi", "Fiil canlı bir varlığa yöneldiği için şiddet davranışı sahnelenmesi kabul edildi."

        return None

    def _uyari_metni_olustur(self, bulgu: dict, baglam_tipi: str, risk: int) -> str:
        return (
            f"'{bulgu.get('kelime', '')}' kelimesi {baglam_tipi} bağlamında "
            f"{risk}/5 riskle işaretlendi."
        )

    def _maarif_profilleri_tespit_et(self, metin: str) -> dict:
        """
        Metinde bulunan Maarif Modeli profil özelliklerini tespit et
        """
        metin_lower = metin.lower()
        
        profil_anahtarlar = {
            "sorgulayici": ["neden", "nasıl", "merak", "araştırma", "soru", "bilim"],
            "cesaretli": ["cesur", "cesaret", "korkmadan", "zorluk", "güçlük", "karşı dur"],
            "uretken": ["yaratıcı", "üretim", "yenilik", "icat", "tasarım", "buluş"],
            "bilge": ["bilgelik", "hikmet", "öğretici", "deneyim", "akıl", "adalet"],
            "ahlaklı": ["doğru", "dürüst", "ahlak", "erdem", "vicdan", "sorumluluk"],
            "merhametli": ["merhamet", "şefkat", "yardım", "acıma", "sevgi", "iyilik"],
            "vatansever": ["vatan", "millet", "türkiye", "bayrak", "güvenlik", "istiklal"],
            "estetik": ["güzel", "estetik", "sanat", "ressam", "müzik", "doğa"],
            "iradeli": ["irade", "kararlı", "azimli", "hedef", "başarı", "çaba"],
            "adil": ["adalet", "adil", "eşit", "hakça", "taraf", "haksız"]
        }
        
        profiller = {}
        for profil_adi, kelimeler in profil_anahtarlar.items():
            toplam_bulgu = sum(metin_lower.count(kelime) for kelime in kelimeler)
            puan = min(5, toplam_bulgu // 2) if toplam_bulgu > 0 else 0
            
            profiller[profil_adi] = {
                "profil_adi": profil_adi.capitalize(),
                "puan": puan,
                "bulgu_sayisi": toplam_bulgu
            }
        
        return profiller
    
    def _kultural_uyum_tespit_et(self, metin: str) -> dict:
        """
        Metinde bulunan Maarif Modeli profil özelliklerini tespit et
        """
        
        profil_bulgusu = {}
        
        # Her profil için anahtar kelimeler
        profil_anahtarlar = {
            "sorgulayici": ["neden", "nasıl", "merak", "araştırma", "soru", "bilim"],
            "cesaretli": ["cesur", "cesaret", "korkmadan", "zorluk", "güçlük", "karşı dur"],
            "uretken": ["yaratıcı", "üretim", "yenilik", "icat", "tasarım", "buluş"],
            "bilge": ["bilgelik", "hikmet", "öğretici", "deneyim", "akıl", "adalet"],
            "ahlaklı": ["doğru", "dürüst", "ahlak", "erdem", "vicdan", "sorumluluk"],
            "merhametli": ["merhamet", "şefkat", "yardım", "acıma", "sevgi", "iyilik"],
            "vatansever": ["vatan", "millet", "türkiye", "bayrak", "güvenlik", "İstiklal"],
            "estetik": ["güzel", "estetik", "sanat", "ressam", "müzik", "doğa"],
            "iradeli": ["irade", "kararlı", "azimli", "hedef", "başarı", "çaba"],
            "saglikli": ["sağlık", "spor", "beslenme", "refahm", "temizlik", "hijyen"]
        }
        
        metin_lower = metin.lower()
        
        for profil, anahtarlar in profil_anahtarlar.items():
            bulgu_sayisi = sum(
                metin_lower.count(anahtar) 
                for anahtar in anahtarlar
            )
            
            if bulgu_sayisi > 0:
                profil_bulgusu[profil] = {
                    "profil_adi": MAARIF_PROFILLERI[profil]["ad"],
                    "bulgu_sayisi": bulgu_sayisi,
                    "puan": min(5, bulgu_sayisi)  # Max 5
                }
        
        return profil_bulgusu
    
    def _karar_araligi_bul(self, skor: float) -> dict:
        """Final skokundan karar aralığını bul"""
        
        if skor < 50:
            anahtar = "21-40" if skor > 20 else "0-20"
        elif skor < 70:
            anahtar = "41-60"
        else:
            anahtar = "61-80" if skor <= 80 else "81-100"
        
        return KARAR_ARALIKLARI[anahtar]
    
    def _detayli_rapor_olustur(self, bulgular: dict, final_skor: float, karar: dict,
                               profil: str, yas_grubu: str, maarif_profilleri: dict) -> str:
        """Detaylı metin raporu oluştur"""
        
        rapor = f"""
╔════════════════════════════════════════════════════════════════════════╗
║         MAARİF MODELİ YAYIN DENETİM SİSTEMİ v1.0 - RAPOR             ║
╚════════════════════════════════════════════════════════════════════════╝

📊 ÖZET BULGULAR
{'='*70}
Analiz Profili    : {ANALIZ_PROFILLERI[profil]["ad"]}
Hedef Yaş Grubu   : {yas_grubu}
Final Skor        : {final_skor}/100
Karar             : {karar['simge']} {karar['seviye']}

📋 KATEGORILERE GÖRE BULGULAR
{'='*70}
"""
        
        # Kategorilere göre detaylar
        for kategori, bulgu_data in bulgular.items():
            if bulgu_data["bulundu"]:
                rapor += f"\n📌 {kategori.upper().replace('_', ' ')}\n"
                rapor += f"   Toplam Bulgu      : {bulgu_data['toplam_bulgu']}\n"
                rapor += f"   Risk Puanı        : {bulgu_data['risk_puani']}/5\n"
                rapor += f"   Ortalama Risk     : {round(bulgu_data['ortalama_risk'], 2)}/5\n"
                
                # İlk 3 bulguyu göster
                for i, bulgu in enumerate(bulgu_data['bulunan_kelimeler'][:3], 1):
                    rapor += f"\n   {i}. \"{bulgu['kelime']}\"\n"
                    rapor += f"      Satır {bulgu['satir']} : {bulgu['kontext']}\n"
                    rapor += f"      Risk : {bulgu['baglamsal_risk']}/5\n"
                
                if len(bulgu_data['bulunan_kelimeler']) > 3:
                    rapor += f"\n   ... ve {len(bulgu_data['bulunan_kelimeler']) - 3} daha\n"
        
        # Maarif Profilleri
        if maarif_profilleri:
            rapor += f"\n\n🎓 MAARİF MODELİ ÖĞRENCİ PROFİLLERİ\n{'='*70}\n"
            for profil_adi, profil_info in maarif_profilleri.items():
                rapor += f"✓ {profil_info['profil_adi']}: {profil_info['puan']}/5 "
                rapor += f"({profil_info['bulgu_sayisi']} bulgu)\n"
        
        # Öneriler
        rapor += f"\n\n💡 ÖNERILER\n{'='*70}\n"
        
        if final_skor <= 20:
            rapor += "✅ Bu kitap seçilen profil için uygun görülmektedir.\n"
            rapor += "   Herhangi bir düzeltme gerekmemektedir.\n"
        elif final_skor <= 40:
            rapor += "✔️ Bu kitap seçilen profil için düşük risk taşımaktadır.\n"
            rapor += "   Belirtilen bulgular göz önünde bulundurulmalıdır.\n"
        elif final_skor < 70:
            rapor += "⚠️ Bu kitap dikkat edilmesi gereken içerik barındırmaktadır.\n"
            rapor += "   Editoryal inceleme önerilir; uygun yaş grubu ve bağlam birlikte değerlendirilmelidir.\n"
        elif final_skor <= 80:
            rapor += "🔴 Bu kitapta revizyon gereken bölümler bulunmaktadır.\n"
            rapor += "   Lütfen belirtilen bölümleri inceleyin.\n"
        else:
            rapor += "❌ Bu kitap seçilen profil için uygun değildir.\n"
            rapor += "   Önemli revizyonlar gereklidir.\n"
        
        rapor += f"\n{'='*70}\n"
        rapor += "Rapor Tarihi: {}\n".format(__import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        return rapor
    
    def meb_kriterleri_degerlendirmesi(self, metin: str, profil: str = "hibrit") -> dict:
        """
        MEB Ders Kitabı İnceleme Kriterleri Matrisine göre değerlendirme
        8 Kriter × Risk Göstergeleri
        """
        
        metin_lower = metin.lower()
        
        meb_sonuclari = {}
        
        # 1. ANAYASA VE MEVZUAT UYGUNLUĞU
        ayrıştırıcı_kelimeler = [
            "ayrıştırıcı", "hukuka aykırı", "kamu düzenini zedeleme",
            "dokunulmazlık ihlali", "yasa dışı", "teşebbüs"
        ]
        ayrıştırıcı_risk = sum(1 for kelime in ayrıştırıcı_kelimeler if kelime in metin_lower)
        meb_sonuclari["anayasa"] = {
            "ad": "Anayasa ve Mevzuat Uygunluğu",
            "risk": min(5, ayrıştırıcı_risk),
            "karar": "Uyumlu" if ayrıştırıcı_risk == 0 else "Koşullu" if ayrıştırıcı_risk < 2 else "Uyumsuz"
        }
        
        # 2. MİLLÎ GÜVENLIK
        terror_kelimeler = [
            "terör", "terörist", "bölücü", "ayrılıkçı", "yasa dışı örgüt",
            "pkk", "pyd", "ypg", "dhkp-c", "propagandası", "özendirme"
        ]
        terror_risk = sum(1 for kelime in terror_kelimeler if kelime in metin_lower)
        meb_sonuclari["milli_guvenlik"] = {
            "ad": "Millî Güvenlik",
            "risk": min(5, terror_risk),
            "karar": "Temiz" if terror_risk == 0 else "Uyarı" if terror_risk < 2 else "Yüksek Risk"
        }
        
        # 3. EŞİTLİK VE KAPSAYICILIK
        ayrimcilik_kelimeler = [
            "nefret söylemi", "ırkcılık", "cinsiyetçi", "ötekileştirme",
            "aşağı ırk", "cahil", "kötü din", "ayrımcı"
        ]
        ayrimcilik_risk = sum(1 for kelime in ayrimcilik_kelimeler if kelime in metin_lower)
        meb_sonuclari["esitlik"] = {
            "ad": "Eşitlik ve Kapsayıcılık",
            "risk": min(5, ayrimcilik_risk),
            "karar": "Uygun" if ayrimcilik_risk == 0 else "Revizyon" if ayrimcilik_risk < 2 else "Ret"
        }
        
        # 4. MİLLÎ VE MANEVI DEĞERLER
        degerler_kelimeler = [
            "aile", "saygı", "sorumluluk", "vatan", "bayrak", "İstiklal",
            "erdem", "ahlak", "dürüstlük", "fedakârlık"
        ]
        degerler_sayisi = sum(1 for kelime in degerler_kelimeler if kelime in metin_lower)
        degerler_risk = max(0, 5 - degerler_sayisi)  # Değerler varsa risk düşer
        meb_sonuclari["milli_manevi"] = {
            "ad": "Millî ve Manevi Değerler",
            "risk": min(5, degerler_risk),
            "karar": "Güçlü" if degerler_sayisi > 3 else "Orta" if degerler_sayisi > 0 else "Zayıf"
        }
        
        # 5. GÜVENLİ VE ETİK İÇERİK
        # Bunu kategori bulgularından al
        tehlikeli_kategoriler = ["siddet_suc", "cinsellik_mahremiyet", "korku_travma"]
        guvenlik_riski = 0
        # Ek kontroller
        ozendir_kelimeler = ["deneme", "dene bak", "denemek istersen", "özendirme"]
        guvenlik_riski += sum(1 for kelime in ozendir_kelimeler if kelime in metin_lower)
        meb_sonuclari["guvenlik"] = {
            "ad": "Güvenli ve Etik İçerik",
            "risk": min(5, guvenlik_riski),
            "karar": "Uygun" if guvenlik_riski == 0 else "Uyarı" if guvenlik_riski < 2 else "Risk"
        }
        
        # 6. BİLİMSEL DOĞRULUK
        yanlıs_kelimeler = ["yanlış", "hurafe", "efsane", "çarpıtılmış", "yanıltıcı"]
        bilimsel_risk = sum(1 for kelime in yanlıs_kelimeler if kelime in metin_lower)
        meb_sonuclari["bilimsel"] = {
            "ad": "Bilimsel Doğruluk",
            "risk": min(5, bilimsel_risk),
            "karar": "Doğru" if bilimsel_risk == 0 else "Kontrol" if bilimsel_risk < 2 else "Yanlış"
        }
        
        # 7. REKLAM VE TİCARİ UNSURLAR
        reklam_kelimeler = [
            "marka", "qr kod", "URL", "http", "link", "bağlantı",
            "satın al", "indir", "abone ol", "takip et", "sponsor"
        ]
        reklam_risk = sum(1 for kelime in reklam_kelimeler if kelime in metin_lower)
        meb_sonuclari["reklam"] = {
            "ad": "Reklam ve Ticari Unsurlar",
            "risk": min(5, reklam_risk),
            "karar": "Temiz" if reklam_risk == 0 else "Hafif" if reklam_risk < 2 else "Yasaklı"
        }
        
        # 8. DİL VE ANLATIM
        argo_kelimeler = ["argo", "küfür", "ağır söz", "edepsiz", "hakaret"]
        dil_risk = sum(1 for kelime in argo_kelimeler if kelime in metin_lower)
        meb_sonuclari["dil"] = {
            "ad": "Dil ve Anlatım",
            "risk": min(5, dil_risk),
            "karar": "Temiz" if dil_risk == 0 else "Dikkat" if dil_risk < 2 else "Revizyon"
        }
        
        return self._meb_puanlamasini_kademelendir(
            {
                "meb_kriterler": meb_sonuclari,
                "meb_bulgulari": {},
            },
            {},
        )
    
    def _kultural_uyum_tespit_et(self, metin: str) -> dict:
        """
        Kültürel uyum ve Türk-İslam değerlerini analiz et
        """
        
        metin_lower = metin.lower()
        
        # Türk isimleri ve Batı isimleri
        turk_isimler = ['ali', 'ayşe', 'mehmet', 'fatih', 'emine', 'hasan', 'zeynep', 'mustafa',
                        'türk', 'türkçe', 'anadolu', 'istanbul', 'ankara']
        batili_isimler = ['john', 'mary', 'david', 'sarah', 'james', 'emma', 'robert', 'susan']
        
        turk_count = sum(metin_lower.count(isim) for isim in turk_isimler)
        batili_count = sum(metin_lower.count(isim) for isim in batili_isimler)
        
        # Coğrafi referanslar
        cografi = ['istanbul', 'ankara', 'anadolu', 'çanakkale', 'sakarya', 'kayseri', 'gaziantep']
        cografi_count = sum(metin_lower.count(yer) for yer in cografi)
        
        # İslami referanslar
        islami = ['cami', 'ezan', 'namaz', 'dua', 'kuran', 'ramazan', 'bayram', 'abdest']
        islami_count = sum(metin_lower.count(kelime) for kelime in islami)
        
        # Aile ve vatanseverlik değerleri
        degerler = ['aile', 'vatan', 'millet', 'bayrak', 'saygı', 'sorumluluk', 'erdem', 'ahlak']
        degerler_count = sum(metin_lower.count(kelime) for kelime in degerler)
        
        # Genel Türk-İslam uyum puanı
        kultural_puan = 0
        if turk_count > batili_count:
            kultural_puan += 20
        if cografi_count > 0:
            kultural_puan += 20
        if islami_count > 0:
            kultural_puan += 20
        if degerler_count > 0:
            kultural_puan += 20
        if batili_count == 0:
            kultural_puan += 20
        
        return {
            "turk_karakter": turk_count,
            "batili_karakter": batili_count,
            "cografi_referans": cografi_count,
            "islami_referans": islami_count,
            "degerler": degerler_count,
            "kultural_puan": min(100, kultural_puan),
            "genel_degerlendirme": "✅ Yüksek uyum" if kultural_puan >= 80 else "✔️ Orta uyum" if kultural_puan >= 50 else "⚠️ Düşük uyum"
        }


# Test
if __name__ == "__main__":
    evaluator = MaarifDegerlendiricisi()
    
    test_metin = """
    Fatih, çok meraklı bir çocuk idi. Her gün okulda öğretmenine binlerce soru sorardı.
    Öğretmeni Bayan Ayşe onun bu özelliğini çok severdi.
    Fatih'in amacı her zaman doğruyu bulmak ve adil davranmaktı.
    """
    
    sonuc = evaluator.analiz_yap(test_metin, profil="hibrit", yas_grubu="6-12")
    print("\n✅ Analiz tamamlandı!")
    print(f"Final Skor: {sonuc['final_skor']}/100")
    print(f"Karar: {sonuc['karar']['seviye']}")
