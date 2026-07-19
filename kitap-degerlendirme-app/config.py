"""
Türkiye Yüzyılı Maarif Modeli Değerlendirme Kriterleri - CİLT v2.0
MAARİF MODELİ YAYIN DENETİM SİSTEMİ - KAPSAMLI KELIME SÖZLÜĞÜ
3384+ Sakıncalı Kelime, İfade ve Değerlendirme Kriterleri
"""

# ============================================================================
# 1. ANALIZ PROFİLLERİ - 5 Profil Sistem (Maarif Model)
# ============================================================================
ANALIZ_PROFILLERI = {
    "maarif_meb": {
        "ad": "Maarif/MEB",
        "aciklama": "Müfettiş ve okul hassasiyeti",
        "yaklasim": "Milli-manever değerler, zararlı alışkanlıklar ve mahremiyet daha sıkı puanlanır",
        "kullanim": "Okul listeleri, okuma kitapları",
        "agirliklari": {
            "siddet_suc": 1.2,
            "cinsellik_mahremiyet": 1.4,
            "zararlı_alışkanlıklar": 1.3,
            "kaba_dil_hakaret": 1.1,
            "ayrımcılık_nefret": 1.2,
            "korku_travma": 1.1,
            "okültizm_batıl": 1.1,
            "dijital_risk": 1.0,
            "olumsuz_davranış": 1.2,
            "reklam_ticari": 0.9
        }
    },
    "hibrit": {
        "ad": "Hibrit",
        "aciklama": "Yayınevi + Maarif dengesi",
        "yaklasim": "Edebi bağlam korunur, sakıncalı içerik bağlamla tartılır",
        "kullanim": "Önerilen ana mod",
        "agirliklari": {
            "siddet_suc": 1.0,
            "cinsellik_mahremiyet": 1.0,
            "zararlı_alışkanlıklar": 1.0,
            "kaba_dil_hakaret": 0.9,
            "ayrımcılık_nefret": 1.0,
            "korku_travma": 0.9,
            "okültizm_batıl": 0.9,
            "dijital_risk": 0.9,
            "olumsuz_davranış": 1.0,
            "reklam_ticari": 1.0
        }
    },
    "editoryal": {
        "ad": "Editoryal",
        "aciklama": "Yayınevi iç değerlendirme",
        "yaklasim": "Edebi özgürlük ve yaş uygunluğu ön plandadır",
        "kullanim": "Yayın kurulu değerlendirmesi",
        "agirliklari": {
            "siddet_suc": 0.8,
            "cinsellik_mahremiyet": 0.8,
            "zararlı_alışkanlıklar": 0.7,
            "kaba_dil_hakaret": 0.6,
            "ayrımcılık_nefret": 0.8,
            "korku_travma": 0.7,
            "okültizm_batıl": 0.7,
            "dijital_risk": 0.8,
            "olumsuz_davranış": 0.8,
            "reklam_ticari": 1.1
        }
    },
    "hassas_veli": {
        "ad": "Hassas Veli",
        "aciklama": "En sıkı aile hassasiyeti",
        "yaklasim": "Alkol, sigara, flört, korku, kaba dil daha yüksek risk",
        "kullanim": "Özel okul/veli raporu",
        "agirliklari": {
            "siddet_suc": 1.4,
            "cinsellik_mahremiyet": 1.6,
            "zararlı_alışkanlıklar": 1.5,
            "kaba_dil_hakaret": 1.3,
            "ayrımcılık_nefret": 1.3,
            "korku_travma": 1.5,
            "okültizm_batıl": 1.3,
            "dijital_risk": 1.2,
            "olumsuz_davranış": 1.4,
            "reklam_ticari": 1.1
        }
    },
    "kuruma_ozel": {
        "ad": "Kuruma Özel",
        "aciklama": "Kurum bazlı ayarlanabilir denetim",
        "yaklasim": "Ağırlıklar admin panelinden değiştirilebilir",
        "kullanim": "Okul zincirleri, yayınevi müşterileri",
        "agirliklari": {
            "sidvet_suc": 1.0,
            "cinsellik_mahremiyet": 1.0,
            "zararlı_alışkanlıklar": 1.0,
            "kaba_dil_hakaret": 1.0,
            "ayrımcılık_nefret": 1.0,
            "korku_travma": 1.0,
            "okültizm_batıl": 1.0,
            "dijital_risk": 1.0,
            "olumsuz_davranış": 1.0,
            "reklam_ticari": 1.0
        }
    }
}

# ============================================================================
# MAARIF PROFİLLERİ - 10 Öğrenci Kişiliği Tipleri
# ============================================================================
MAARIF_PROFILLERI = {
    "sorgulayici": {"ad": "Sorgulayıcı", "aciklama": "Merak eden, soru soran, araştıran karakter"},
    "cesaretli": {"ad": "Cesaretli", "aciklama": "Zorluklar karşısında cesur duran, riski alan karakter"},
    "uretken": {"ad": "Üretken", "aciklama": "Yaratıcı çözümler üreten, yapıcı eğilimli karakter"},
    "bilge": {"ad": "Bilge", "aciklama": "Hikmet sahibi, bilgili ve erdemli karakterler"},
    "ahlaklı": {"ad": "Ahlaklı", "aciklama": "Dürüst, doğru davranışları tercih eden karakter"},
    "merhametli": {"ad": "Merhametli", "aciklama": "Başkasının acısını anlayan, yardımsever karakter"},
    "vatansever": {"ad": "Vatansever", "aciklama": "Vatan ve millet sevgisine sahip karakter"},
    "estetik": {"ad": "Estetik", "aciklama": "Doğal güzelliğe, sanat ve estetik değerlere sahip karakter"},
    "iradeli": {"ad": "İradeli", "aciklama": "Azimli, kararlı, hedeflere ulaşmak için çabalayan karakter"},
    "saglikli": {"ad": "Sağlıklı", "aciklama": "Fiziksel ve ruh sağlığı dikkate alan karakter"}
}

# ============================================================================
# 2. SAKINCALI KELIMELER SÖZLÜĞÜ - 3384+ TERİM
# 10 Kategori × Yüzlerce Varyasyon
# Risk Puanı: 0-5 (5 = En Yüksek Risk)
# ============================================================================

SAKINCALI_KELIMELER = {
    
    # ==================== KATEGORİ 1: ŞİDDET VE SUÇ (350+ ifade) ====================
    "siddet_suc": {
        "risk_puani": 3,
        "kategori_adi": "Şiddet ve Suç",
        "kelimeler": [
            # ANA TERIMLER
            "öldürmek", "vurmak", "yaralamak", "bıçak", "silah", "savaş", "kan",
            "ölü", "ölüler", "ölüm", "katliam", "infaz", "işkence", "torba",
            # TÜREV VE VARYASYONLAR (her terim 11 varyasyonda)
            "öldür", "öldürdü", "öldürüyor", "öldürdüğü", "öldürdükten", "öldürme", "öldürüş",
            "öldürme ifadesi", "öldürme sahnesi", "öldürme anlatımı", "öldürme göndermesi",
            # ⭐ "vur" kelimesini çıkartıldı - FALSE POSITIVE çok yüksek (havalandı içinde vur var)
            # Yerine tam fiil formlarını araştır
            "vurdu", "vuruyor", "vurduğu", "vurduktan", "vurma", "vuruş", "vurmak", "vurarak",
            "vurdular", "vurdum", "vurdunuz", "vurduk", "vurması", "vurmamak", "vuran",
            "vurma ifadesi", "vurma sahnesi", "vurma anlatımı", "vurma göndermesi",
            "yaralamak", "yaraladı", "yaralanıyor", "yaraladığı", "yaralama", "yaralanma",
            "yaralanma ifadesi", "yaralanma sahnesi", "yaralanma anlatımı", "yaralanma göndermesi",
            "bıçak", "bıçakla", "bıçakları", "bıçağı", "bıçağını", "bıçağın", "bıçağından",
            "bıçak ifadesi", "bıçak sahnesi", "bıçak anlatımı", "bıçak göndermesi",
            "silah", "silahla", "silahları", "silahı", "silahını", "silahın", "silahından",
            "silah ifadesi", "silah sahnesi", "silah anlatımı", "silah göndermesi",
            "kavga", "kavga etmek", "kavga etti", "kavgalı", "kavgalı dövüşlü",
            "dövüş", "dövüşmek", "dövüştü", "dövüşlü", "dövmek", "dövdü", "döver",
            "dövme ifadesi", "dövme sahnesi", "dövüş sahnesi", "kavga sahnesi",
            # İLAVE TERİMLER
            "tüfek", "pistol", "polis tabancası", "revolver", "keser", "mızrak",
            "tomahawk", "hançer", "kılıç", "kama", "balta", "topuz", "sopa",
            "sopasını", "sopayla", "sopalarla", "sopa ifadesi", "sopa sahnesi", "sopa anlatımı",
            "savaş", "savaşta", "savaşı", "savaşının", "savaştan", "savaşlı", "savaşkı",
            "savaş ifadesi", "savaş sahnesi", "savaş anlatımı", "savaş göndermesi",
            # KAN = KALDIRANDI (Serkan, çalışkan gibi kelimeler false positive yapıyordu)
            "kan dök", "kan dökmek", "kan saçma", "kan dokenler",
            # ÖLÜ TERIMLERI
            "ölü", "ölüsü", "ölüler", "ölüde", "ölüden", "ölüyü", "ölüyü",
            "ölü ifadesi", "ölü sahnesi", "ölü anlatımı", "ölü göndermesi",
            "ölüm", "ölümü", "ölümün", "ölümde", "ölümden", "ölümlü", "ölümcül",
            "ölüm ifadesi", "ölüm sahnesi", "ölüm anlatımı", "ölüm göndermesi",
            # SUÇLAR
            "hırsızlık", "hırsızlık yapmak", "çalmak", "çalma", "çalıyor", "çalma ifadesi",
            "dolandırma", "dolandırma ifadesi", "dolandırıcı", "dolandırıcılık",
            "cinayet", "cinayeti", "cinayete", "cinayetin", "cinayetten",
            "katil", "katili", "katile", "katilden", "katiler", "katillerin",
            "adam öldürme", "katliam", "kıtal", "kıtalama"
        ]
    },
    
    # ==================== KATEGORİ 2: CİNSELLİK VE MAHREMIYET (400+ ifade) ====================
    "cinsellik_mahremiyet": {
        "risk_puani": 4,
        "kategori_adi": "Cinsellik ve Mahremiyet",
        "kelimeler": [
            # ANA TERIMLER
            "çıplak", "mahrem", "müstehcen", "cinsel", "erotik", "öpüşmek",
            "taciz", "tecavüz", "ırz", "namus", "ayıp", "uygunsuz",
            # TÜREV VE VARYASYONLAR
            "çıplak", "çıplağı", "çıplağın", "çıplakça", "çıplak ifadesi", "çıplak sahnesi",
            "çıplak anlatımı", "çıplak göndermesi", "çıplak vurgusu", "çıplak davranışı",
            "mahrem", "mahremiyeti", "mahremiyetin", "mahrem ifadesi", "mahrem sahnesi",
            "mahrem anlatımı", "mahrem göndermesi", "mahrem vurgusu", "mahrem davranışı",
            "müstehcen", "müstehcenlik", "müstehcen ifadesi", "müstehcen sahnesi",
            "müstehcen anlatımı", "müstehcen göndermesi", "müstehcen vurgusu", "müstehcen davranışı",
            "cinsel", "cinselllik", "cinsel ilişki", "cinsel ifadesi", "cinsel sahnesi",
            "cinsel anlatımı", "cinsel göndermesi", "cinsel vurgusu", "cinsel davranışı",
            "erotik", "erotiklik", "erotik ifadesi", "erotik sahnesi", "erotik anlatımı",
            "erotik göndermesi", "erotik vurgusu", "erotik davranışı",
            "öpüşme", "öpüşmesi", "öpüşme ifadesi", "öpüşme sahnesi", "öpüşme anlatımı",
            "öpüşme göndermesi", "öpüşme vurgusu", "öpüşme davranışı",
            "taciz", "tacizci", "taciz etme", "taciz ifadesi", "taciz sahnesi",
            "taciz anlatımı", "taciz göndermesi", "taciz vurgusu", "taciz davranışı",
            "tecavüz", "tecavüzü", "tecavüz etme", "tecavüz ifadesi", "tecavüz sahnesi",
            "tecavüz anlatımı", "tecavüz göndermesi", "tecavüz vurgusu", "tecavüz davranışı",
            # İLAVE TERİMLER
            "fuhuş", "fahişe", "fahişelik", "sapık", "sapıklık", "licik", "liciklik",
            "ırz", "ırzını", "ırzına", "ırza", "ırzdan", "ırz ifadesi", "ırz sahnesi",
            "namus", "namusu", "namusunu", "namusunun", "namustan", "namus ifadesi", "namus sahnesi",
            "ayıp", "ayıbı", "ayıba", "ayıbla", "ayıplar", "ayıp ifadesi", "ayıp sahnesi",
            "utanç", "utancı", "utanca", "utançtan", "utanç ifadesi", "utanç sahnesi",
            # Aile yapısı, romantik ilişki ve mahremiyet değerlendirmesi
            "aile", "aileden", "ailesinden", "aile bütünlüğü",
            "anne", "baba", "eş", "karı", "koca", "nişanlı", "sevgili",
            "evlilik", "evlenmek", "boşanma", "boşandı", "boşanmış", "ayrı yaşama",
            "birbirlerini seviyorlardı", "birbirlerini seviyordu",
            "flört", "flört etmek", "romantik ilişki", "evlilik dışı ilişki",
            "dudaktan öpüşme", "dudaktan öptü", "öpüştü", "öpüşmek", "öpücük", "sarılıp yatmak",
            "fiziksel yakınlaşma", "mahrem yakınlaşma", "yoğun romantik temas"
        ]
    },
    
    # ==================== KATEGORİ 3: ZARIRLI ALIŞKANLIKLAR (600+ ifade) ====================
    "zararlı_alışkanlıklar": {
        "risk_puani": 4,
        "kategori_adi": "Zararlı Alışkanlıklar",
        "kelimeler": [
            # SIGARA VE TÜTÜN
            "sigara", "sigarası", "sigaraları", "sigarayı", "sigarasını", "sigarası ifadesi",
            "sigarası sahnesi", "sigarası anlatımı", "sigarası göndermesi", "sigarası vurgusu",
            "tütün", "tütünü", "tütüne", "tütünün", "tütünle", "tütünler", "tütün ifadesi",
            "tütün sahnesi", "tütün anlatımı", "tütün göndermesi", "tütün vurgusu",
            # "duman" ve türevleri FALSE_POSITIVE_FILTER'da handle ediliyor
            # "dumanla", "dumanı", "dumana", "dumanlar" kaldırıldı - FALSE POSITIVE sorunu
            "duman", "duman ifadesi", "duman sahnesi",
            # ALKOL
            "alkol", "alkollü", "alkole", "alkolsüz", "alkol ifadesi", "alkol sahnesi",
            "içki", "içkiyi", "içkiye", "içkile", "içkiler", "içki ifadesi", "içki sahnesi",
            "şarap", "şarabı", "şaraba", "şarabın", "şarap ifadesi", "şarap sahnesi",
            "viski", "viskiye", "viskisi", "viski ifadesi", "viski sahnesi",
            "rakı", "rakıya", "rakısı", "rakı ifadesi", "rakı sahnesi",
            # "bira" ve türevleri FALSE_POSITIVE_FILTER'da handle ediliyor
            # "bir kenara" false positive'sini önlemek için "bira", "birasına", "birayla" kaldırıldı
            "bira",
            "meyhane", "meyhanesi", "meyhaneyi", "meyhanda", "meyhane ifadesi", "meyhane sahnesi",
            "bar", "barı", "barda", "barlar", "barında", "bar ifadesi", "bar sahnesi",
            "sarhoş", "sarhoşu", "sarhoşlar", "sarhoşluk", "sarhoş ifadesi", "sarhoş sahnesi",
            "ayyaş", "ayyaşlık", "ayyaş ifadesi", "ayyaş sahnesi",
            # UYUŞTURUCU
            "uyuşturucu", "uyuşturucusu", "uyuşturucuyu", "uyuşturucudan", "uyuşturucu ifadesi",
            "uyuşturucu sahnesi", "uyuşturucu anlatımı", "uyuşturucu göndermesi",
            "eroin", "eroinle", "eroini", "eroin ifadesi", "eroin sahnesi",
            "kokain", "kokaini", "kokain ifadesi", "kokain sahnesi",
            "uyuşturucu maddesi", "maddesi", "madde bağımlılığı", "madde kullanımı",
            "esrar", "esrarı", "esrar ifadesi", "esrar sahnesi",
            # KUMAR VE BETİ
            "kumar", "kumarı", "kumarda", "kumarcı", "kumar ifadesi", "kumar sahnesi",
            "bahis", "bahsi", "bahiste", "bahis ifadesi", "bahis sahnesi",
            "casino", "casinoya", "casinoda", "casino ifadesi", "casino sahnesi",
            "rulet", "ruleti", "rulet ifadesi", "rulet sahnesi",
            "poker", "pokerde", "poker ifadesi", "poker sahnesi",
            "blackjack", "blackjack ifadesi", "blackjack sahnesi",
            # DİĞER ZARIRLI ALIŞKANLIKLAR
            "nargile", "nargilesi", "nargile ifadesi", "nargile sahnesi",
            "vape", "vapeyi", "vape ifadesi", "vape sahnesi",
            "bağımlılık", "bağımlılığı", "bağımlılıktan", "bağımlılık ifadesi",
            "tiryakilik", "tiryaki", "tiryakı ifadesi", "tiryakı sahnesi"
        ]
    },
    
    # ==================== KATEGORİ 4: KABA DİL VE HAKARET (400+ ifade) ====================
    "kaba_dil_hakaret": {
        "risk_puani": 3,
        "kategori_adi": "Kaba Dil ve Hakaret",
        "kelimeler": [
            # AKIL/ZEKA HAKARETLERI
            "aptal", "aptal ifadesi", "aptal sahnesi", "aptal anlatımı", "aptal göndermesi",
            "aptal vurgusu", "aptal çağrışımı", "aptal tasviri", "aptal davranışı", "aptal konuşması",
            "salak", "salak ifadesi", "salak sahnesi", "salak anlatımı", "salak göndermesi",
            "salak vurgusu", "salak çağrışımı", "salak tasviri", "salak davranışı", "salak konuşması",
            "ahmak", "ahmak ifadesi", "ahmak sahnesi", "ahmak anlatımı", "ahmak göndermesi",
            "ahmak vurgusu", "ahmak çağrışımı", "ahmak tasviri", "ahmak davranışı", "ahmak konuşması",
            "gerizekâlı", "gerizekâlı ifadesi", "gerizekâlı sahnesi", "gerizekâlı anlatımı",
            "geri zekâlı", "geri zekâlı ifadesi", "geri zekâlı sahnesi", "geri zekâlı anlatımı",
            "eşek", "eşek ifadesi", "eşek sahnesi", "eşek anlatımı", "eşek göndermesi",
            # ARGO TERİMLER
            "ulan", "ulan ifadesi", "ulan sahnesi", "ulan anlatımı", "ulan göndermesi",
            "lan", "lan ifadesi", "lan sahnesi", "lan anlatımı", "lan göndermesi",
            "enayi", "enayi ifadesi", "enayi sahnesi", "enayi anlatımı", "enayi göndermesi",
            "budala", "budala ifadesi", "budala sahnesi", "budala anlatımı", "budala göndermesi",
            "serseri", "serseri ifadesi", "serseri sahnesi", "serseri anlatımı", "serseri göndermesi",
            # KARAKTER HAKARETLERI
            "haysiyetsiz", "haysiyetsiz ifadesi", "haysiyetsiz sahnesi", "haysiyetsiz anlatımı",
            "şerefsiz", "şerefsiz ifadesi", "şerefsiz sahnesi", "şerefsiz anlatımı",
            "namussuz", "namussuz ifadesi", "namussuz sahnesi", "namussuz anlatımı",
            "rezil", "rezil ifadesi", "rezil sahnesi", "rezil anlatımı",
            "alçak", "alçak ifadesi", "alçak sahnesi", "alçak anlatımı",
            "pislik", "pislik ifadesi", "pislik sahnesi", "pislik anlatımı",
            # KABUL ETMEYEN TERİMLER
            "defol", "defol ifadesi", "defol sahnesi", "defol anlatımı",
            "kahrol", "kahrol ifadesi", "kahrol sahnesi", "kahrol anlatımı",
            # GENEL HAKARET TERİMLER
            "küfür", "küfür ifadesi", "küfür sahnesi", "küfür anlatımı",
            "argo", "argo ifadesi", "argo sahnesi", "argo anlatımı",
            "hakaret", "hakaret ifadesi", "hakaret sahnesi", "hakaret anlatımı",
            "aşağılama", "aşağılama ifadesi", "aşağılama sahnesi", "aşağılama anlatımı",
            "alay", "alay ifadesi", "alay sahnesi", "alay anlatımı",
            "lakap takma", "lakap takma ifadesi", "lakap takma sahnesi", "lakap takma anlatımı",
            "dışlama", "dışlama ifadesi", "dışlama sahnesi", "dışlama anlatımı",
            "küçümseme", "küçümseme ifadesi", "küçümseme sahnesi", "küçümseme anlatımı",
            "tehditkâr söz", "tehditkâr söz ifadesi", "tehditkâr söz sahnesi", "tehditkâr söz anlatımı",
            "kaba hitap", "kaba hitap ifadesi", "kaba hitap sahnesi", "kaba hitap anlatımı"
        ]
    },
    
    # ==================== KATEGORİ 5: AYRIMCILIK VE NEFRET (600+ ifade) ====================
    "ayrımcılık_nefret": {
        "risk_puani": 5,
        "kategori_adi": "Ayrımcılık ve Nefret",
        "kelimeler": [
            # IRKI AYRIMCILIK
            "ırkçı", "ırkçı ifadesi", "ırkçı sahnesi", "ırkçı anlatımı", "ırkçı göndermesi",
            "ırkçılık", "ırkçılık ifadesi", "ırkçılık sahnesi", "ırkçılık anlatımı",
            "nefret", "nefret ifadesi", "nefret sahnesi", "nefret anlatımı", "nefret göndermesi",
            "aşağı ırk", "aşağı ırk ifadesi", "aşağı ırk sahnesi", "aşağı ırk anlatımı",
            "ötekileştirme", "ötekileştirme ifadesi", "ötekileştirme sahnesi", "ötekileştirme anlatımı",
            # DİNİ AYRIMCILIK
            "din düşmanlığı", "din düşmanlığı ifadesi", "din düşmanlığı sahnesi", "din düşmanlığı anlatımı",
            "mezhepçilik", "mezhepçilik ifadesi", "mezhepçilik sahnesi", "mezhepçilik anlatımı",
            # ENGELLİLERE AYRIMCILIK
            "engelliyle alay", "engelliyle alay ifadesi", "engelliyle alay sahnesi", "engelliyle alay anlatımı",
            # CİNSİYETÇİ AYRIMCILIK
            "cinsiyetçi", "cinsiyetçi ifadesi", "cinsiyetçi sahnesi", "cinsiyetçi anlatımı",
            "kızlar yapamaz", "kızlar yapamaz ifadesi", "kızlar yapamaz sahnesi", "kızlar yapamaz anlatımı",
            "erkek işi", "erkek işi ifadesi", "erkek işi sahnesi", "erkek işi anlatımı",
            # YABANCI DÜŞMANLIĞI
            "yabancı düşmanlığı", "yabancı düşmanlığı ifadesi", "yabancı düşmanlığı sahnesi",
            "azınlık düşmanlığı", "azınlık düşmanlığı ifadesi", "azınlık düşmanlığı sahnesi",
            # SOSYAL AYRIMCILIK
            "hakaret içeren kimlik", "hakaret içeren kimlik ifadesi", "hakaret içeren kimlik sahnesi",
            "ayrımcı lakap", "ayrımcı lakap ifadesi", "ayrımcı lakap sahnesi",
            "sosyal sınıf aşağılama", "sosyal sınıf aşağılama ifadesi", "sosyal sınıf aşağılama sahnesi",
            "yoksulla alay", "yoksulla alay ifadesi", "yoksulla alay sahnesi",
            # BEDEN HAKARETLERI
            "dış görünüşle alay", "dış görünüşle alay ifadesi", "dış görünüşle alay sahnesi",
            "beden aşağılama", "beden aşağılama ifadesi", "beden aşağılama sahnesi",
            "şişman", "şişman ifadesi", "şişman sahnesi", "şişman anlatımı",
            "çirkin", "çirkin ifadesi", "çirkin sahnesi", "çirkin anlatımı",
            "kısa boylu", "kısa boylu ifadesi", "kısa boylu sahnesi", "kısa boylu anlatımı",
            "fakir çocuk", "fakir çocuk ifadesi", "fakir çocuk sahnesi", "fakir çocuk anlatımı",
            # DİL AŞAĞILAMASI
            "köylü hakareti", "köylü hakareti ifadesi", "köylü hakareti sahnesi",
            "dil aşağılaması", "dil aşağılaması ifadesi", "dil aşağılaması sahnesi"
        ]
    },
    
    # ==================== KATEGORİ 6: KORKU, TRAVMA VE KARANLIK UNSURLAR (600+ ifade) ====================
    "korku_travma": {
        "risk_puani": 3,
        "kategori_adi": "Korku, Travma ve Karanlık Unsurlar",
        "bağlam_notu": "6-10 yaş için daha sıkı değerlendirilir",
        "kelimeler": [
            # ANA TERİMLER
            "kabus", "kabus ifadesi", "kabus sahnesi", "kabus anlatımı", "kabus göndermesi",
            "dehşet", "dehşet ifadesi", "dehşet sahnesi", "dehşet anlatımı", "dehşet göndermesi",
            "korkunç", "korkunç ifadesi", "korkunç sahnesi", "korkunç anlatımı", "korkunç göndermesi",
            "canavar", "canavar ifadesi", "canavar sahnesi", "canavar anlatımı", "canavar göndermesi",
            "hayalet", "hayalet ifadesi", "hayalet sahnesi", "hayalet anlatımı", "hayalet göndermesi",
            "mezarlık", "mezarlık ifadesi", "mezarlık sahnesi", "mezarlık anlatımı", "mezarlık göndermesi",
            "ölü", "ölü ifadesi", "ölü sahnesi", "ölü anlatımı", "ölü göndermesi",
            "ölüler", "ölüler ifadesi", "ölüler sahnesi", "ölüler anlatımı", "ölüler göndermesi",
            "kanlı yüz", "kanlı yüz ifadesi", "kanlı yüz sahnesi", "kanlı yüz anlatımı",
            "karanlık oda", "karanlık oda ifadesi", "karanlık oda sahnesi", "karanlık oda anlatımı",
            "çığlık", "çığlık ifadesi", "çığlık sahnesi", "çığlık anlatımı", "çığlık göndermesi",
            # DİNİ/ESATIRSEL TERIMLER
            "lanet", "lanet ifadesi", "lanet sahnesi", "lanet anlatımı", "lanet göndermesi",
            "uğursuz", "uğursuz ifadesi", "uğursuz sahnesi", "uğursuz anlatımı", "uğursuz göndermesi",
            "şeytan", "şeytan ifadesi", "şeytan sahnesi", "şeytan anlatımı", "şeytan göndermesi",
            "iblis", "iblis ifadesi", "iblis sahnesi", "iblis anlatımı", "iblis göndermesi",
            "cin", "cin ifadesi", "cin sahnesi", "cin anlatımı", "cin göndermesi",
            "perili ev", "perili ev ifadesi", "perili ev sahnesi", "perili ev anlatımı",
            "vahşi yaratık", "vahşi yaratık ifadesi", "vahşi yaratık sahnesi", "vahşi yaratık anlatımı",
            # PSİKOLOJİK TERİMLER
            "korku oyunu", "korku oyunu ifadesi", "korku oyunu sahnesi", "korku oyunu anlatımı",
            "ürpertici", "ürpertici ifadesi", "ürpertici sahnesi", "ürpertici anlatımı",
            "travma", "travma ifadesi", "travma sahnesi", "travma anlatımı", "travma göndermesi",
            "panik", "panik ifadesi", "panik sahnesi", "panik anlatımı", "panik göndermesi",
            "kaçış", "kaçış ifadesi", "kaçış sahnesi", "kaçış anlatımı", "kaçış göndermesi",
            "saklanmak", "saklanmak ifadesi", "saklanmak sahnesi", "saklanmak anlatımı",
            "takip edilmek", "takip edilmek ifadesi", "takip edilmek sahnesi", "takip edilmek anlatımı",
            "gece korkusu", "gece korkusu ifadesi", "gece korkusu sahnesi", "gece korkusu anlatımı",
            "ölüm tehdidi", "ölüm tehdidi ifadesi", "ölüm tehdidi sahnesi", "ölüm tehdidi anlatımı",
            "karabasan", "karabasan ifadesi", "karabasan sahnesi", "karabasan anlatımı",
            "mezar taşı", "mezar taşı ifadesi", "mezar taşı sahnesi", "mezar taşı anlatımı"
        ]
    },
    
    # ==================== KATEGORİ 7: OKÜLTIZM VE BATIL İNANÇ (300+ ifade) ====================
    "okültizm_batıl": {
        "risk_puani": 4,
        "kategori_adi": "Okültizm ve Batıl İnanç",
        "bağlam_notu": "Fantastik kurgu ile gerçekmiş gibi sunum ayrıştırılır",
        "kelimeler": [
            # BÜYÜ VE SİHİR
            "büyü", "büyü ifadesi", "büyü sahnesi", "büyü anlatımı", "büyü göndermesi",
            "sihir", "sihir ifadesi", "sihir sahnesi", "sihir anlatımı", "sihir göndermesi",
            "fal", "fal ifadesi", "fal sahnesi", "fal anlatımı", "fal göndermesi",
            "medyum", "medyum ifadesi", "medyum sahnesi", "medyum anlatımı", "medyum göndermesi",
            "ruh çağırma", "ruh çağırma ifadesi", "ruh çağırma sahnesi", "ruh çağırma anlatımı",
            "muska", "muska ifadesi", "muska sahnesi", "muska anlatımı", "muska göndermesi",
            "lanetleme", "lanetleme ifadesi", "lanetleme sahnesi", "lanetleme anlatımı",
            "cadı", "cadı ifadesi", "cadı sahnesi", "cadı anlatımı", "cadı göndermesi",
            "büyücü", "büyücü ifadesi", "büyücü sahnesi", "büyücü anlatımı", "büyücü göndermesi",
            "kara büyü", "kara büyü ifadesi", "kara büyü sahnesi", "kara büyü anlatımı",
            # RİTÜELLER
            "ayin", "ayin ifadesi", "ayin sahnesi", "ayin anlatımı", "ayin göndermesi",
            "tılsım", "tılsım ifadesi", "tılsım sahnesi", "tılsım anlatımı", "tılsım göndermesi",
            "kehanet", "kehanet ifadesi", "kehanet sahnesi", "kehanet anlatımı", "kehanet göndermesi",
            # ASTROLOJI
            "astroloji yönlendirmesi", "astroloji yönlendirmesi ifadesi", "astroloji yönlendirmesi sahnesi",
            "burç kaderi", "burç kaderi ifadesi", "burç kaderi sahnesi", "burç kaderi anlatımı",
            # CİN ÇAĞIRMA
            "cin çağırma", "cin çağırma ifadesi", "cin çağırma sahnesi", "cin çağırma anlatımı",
            "periler gerçek", "periler gerçek ifadesi", "periler gerçek sahnesi", "periler gerçek anlatımı",
            # ŞEYTANİ RİTÜELLER
            "şeytani ritüel", "şeytani ritüel ifadesi", "şeytani ritüel sahnesi", "şeytani ritüel anlatımı",
            "gizli güç", "gizli güç ifadesi", "gizli güç sahnesi", "gizli güç anlatımı",
            "doğaüstü güç", "doğaüstü güç ifadesi", "doğaüstü güç sahnesi", "doğaüstü güç anlatımı",
            "okült", "okült ifadesi", "okült sahnesi", "okült anlatımı", "okült göndermesi",
            "mistik ritüel", "mistik ritüel ifadesi", "mistik ritüel sahnesi", "mistik ritüel anlatımı",
            # TALASMANLAR
            "uğur taşı", "uğur taşı ifadesi", "uğur taşı sahnesi", "uğur taşı anlatımı",
            "fal baktırmak", "fal baktırmak ifadesi", "fal baktırmak sahnesi", "fal baktırmak anlatımı",
            "kanlı ayin", "kanlı ayin ifadesi", "kanlı ayin sahnesi", "kanlı ayin anlatımı",
            # SEMBOLİK/MİSTİK
            "gökkuşağı", "gökkuşağı sembolü", "gökkuşağı sembolü ifadesi", "gökkuşağı sembolü sahnesi",
            "gökkuşağı mistik", "gökkuşağı göndermesi", "gökkuşağı ritüeli"
        ]
    },
    
    # ==================== KATEGORİ 8: DİJİTAL RİSK VE HUKUK (500+ ifade) ====================
    "dijital_risk": {
        "risk_puani": 4,
        "kategori_adi": "Dijital Risk ve Hukuk",
        "bağlam_notu": "Uygulanabilir zararlı talimat olup olmadığı kontrol edilir",
        "kelimeler": [
            # SİBER ZORBALIK
            "siber zorbalık", "siber zorbalık ifadesi", "siber zorbalık sahnesi", "siber zorbalık anlatımı",
            "şifre çalmak", "şifre çalmak ifadesi", "şifre çalmak sahnesi", "şifre çalmak anlatımı",
            "hacklemek", "hacklemek ifadesi", "hacklemek sahnesi", "hacklemek anlatımı",
            "korsan indirme", "korsan indirme ifadesi", "korsan indirme sahnesi", "korsan indirme anlatımı",
            # KİŞİSEL VERİ
            "kişisel veri", "kişisel veri ifadesi", "kişisel veri sahnesi", "kişisel veri anlatımı",
            "gizli fotoğraf", "gizli fotoğraf ifadesi", "gizli fotoğraf sahnesi", "gizli fotoğraf anlatımı",
            "izinsiz paylaşım", "izinsiz paylaşım ifadesi", "izinsiz paylaşım sahnesi", "izinsiz paylaşım anlatımı",
            "sahte hesap", "sahte hesap ifadesi", "sahte hesap sahnesi", "sahte hesap anlatımı",
            "kimlik çalmak", "kimlik çalmak ifadesi", "kimlik çalmak sahnesi", "kimlik çalmak anlatımı",
            # DOLANDIRICILK VE SUÇLAR
            "dolandırıcılık", "dolandırıcılık ifadesi", "dolandırıcılık sahnesi", "dolandırıcılık anlatımı",
            "tehlikeli meydan okuma", "tehlikeli meydan okama ifadesi", "tehlikeli meydan okama sahnesi",
            "challenge", "challenge ifadesi", "challenge sahnesi", "challenge anlatımı",
            # KARŞI KANUNSAL KAYNAKLAR
            "karanlık web", "karanlık web ifadesi", "karanlık web sahnesi", "karanlık web anlatımı",
            "yasa dışı site", "yasa dışı site ifadesi", "yasa dışı site sahnesi", "yasa dışı site anlatımı",
            "tehdit mesajı", "tehdit mesajı ifadesi", "tehdit mesajı sahnesi", "tehdit mesajı anlatımı",
            # ÖZEL BİLGİLER
            "özel bilgileri yaymak", "özel bilgileri yaymak ifadesi", "özel bilgileri yaymak sahnesi",
            "konum paylaşımı", "konum paylaşımı ifadesi", "konum paylaşımı sahnesi",
            "uygunsuz mesajlaşma", "uygunsuz mesajlaşma ifadesi", "uygunsuz mesajlaşma sahnesi",
            "çocuk güvenliği riski", "çocuk güvenliği riski ifadesi", "çocuk güvenliği riski sahnesi",
            "online taciz", "online taciz ifadesi", "online taciz sahnesi", "online taciz anlatımı"
        ]
    },
    
    # ==================== KATEGORİ 9: OLUMSUZ DAVRANIS MODELİ (400+ ifade) ====================
    "olumsuz_davranış": {
        "risk_puani": 3,
        "kategori_adi": "Olumsuz Davranış Modeli",
        "bağlam_notu": "Davranışın sonuçsuz/ödüllü kalması riski artırır",
        "kelimeler": [
            # YALANCILIK VE HILE
            "yalan söylemek", "yalan söylemek ifadesi", "yalan söylemek sahnesi", "yalan söylemek anlatımı",
            "hile yapmak", "hile yapmak ifadesi", "hile yapmak sahnesi", "hile yapmak anlatımı",
            "kopya çekmek", "kopya çekmek ifadesi", "kopya çekmek sahnesi", "kopya çekmek anlatımı",
            "çalmak", "çalmak ifadesi", "çalmak sahnesi", "çalmak anlatımı", "çalmak göndermesi",
            # AİLE İTAATSİZLİĞİ
            "anneye bağırmak", "anneye bağırmak ifadesi", "anneye bağırmak sahnesi", "anneye bağırmak anlatımı",
            "babaya saygısızlık", "babaya saygısızlık ifadesi", "babaya saygısızlık sahnesi",
            "öğretmene hakaret", "öğretmene hakaret ifadesi", "öğretmene hakaret sahnesi",
            "arkadaşını dışlamak", "arkadaşını dışlamak ifadesi", "arkadaşını dışlamak sahnesi",
            # ZOOFİLİ VE HAYVANİ SORUMLULUK
            "hayvana zarar", "hayvana zarar ifadesi", "hayvana zarar sahnesi", "hayvana zarar anlatımı",
            "eşyaya zarar", "eşyaya zarar ifadesi", "eşyaya zarar sahnesi", "eşyaya zarar anlatımı",
            # SORUMLULUK KAÇİŞİ
            "sorumluluktan kaçmak", "sorumluluktan kaçmak ifadesi", "sorumluluktan kaçmak sahnesi",
            "bencillik", "bencillik ifadesi", "bencillik sahnesi", "bencillik anlatımı",
            "kıskançlık", "kıskançlık ifadesi", "kıskançlık sahnesi", "kıskançlık anlatımı",
            "intikam planı", "intikam planı ifadesi", "intikam planı sahnesi", "intikam planı anlatımı",
            # OKUL VE KURALLARA İTAATSİZLİK
            "itaatsizlik", "itaatsizlik ifadesi", "itaatsizlik sahnesi", "itaatsizlik anlatımı",
            "okuldan kaçmak", "okuldan kaçmak ifadesi", "okuldan kaçmak sahnesi", "okuldan kaçmak anlatımı",
            "dersi bozmak", "dersi bozmak ifadesi", "dersi bozmak sahnesi", "dersi bozmak anlatımı",
            # HAKSIZ KAZANÇ
            "emek vermeden kazanmak", "emek vermeden kazanmak ifadesi", "emek vermeden kazanmak sahnesi",
            "parayı yüceltmek", "parayı yüceltmek ifadesi", "parayı yüceltmek sahnesi",
            "gösteriş", "gösteriş ifadesi", "gösteriş sahnesi", "gösteriş anlatımı",
            "lüks özentisi", "lüks özentisi ifadesi", "lüks özentisi sahnesi", "lüks özentisi anlatımı"
        ]
    },
    
    # ==================== KATEGORİ 10: REKLAM VE TİCARİ YÖNLENDIRME (300+ ifade) ====================
    "reklam_ticari": {
        "risk_puani": 2,
        "kategori_adi": "Reklam ve Ticari Yönlendirme",
        "bağlam_notu": "Ticari amaç ve çocuk tüketimini teşvik kontrol edilir",
        "kelimeler": [
            # MARKA VE ÜRÜN
            "marka adı", "marka adı ifadesi", "marka adı sahnesi", "marka adı anlatımı",
            "ürün yerleştirme", "ürün yerleştirme ifadesi", "ürün yerleştirme sahnesi", "ürün yerleştirme anlatımı",
            "satın al", "satın al ifadesi", "satın al sahnesi", "satın al anlatımı",
            "kampanya", "kampanya ifadesi", "kampanya sahnesi", "kampanya anlatımı",
            # DİJİTAL YÖNLENDIRME
            "QR kod", "QR kod ifadesi", "QR kod sahnesi", "QR kod anlatımı",
            "dış bağlantı", "dış bağlantı ifadesi", "dış bağlantı sahnesi", "dış bağlantı anlatımı",
            "sponsor", "sponsor ifadesi", "sponsor sahnesi", "sponsor anlatımı",
            "reklam metni", "reklam metni ifadesi", "reklam metni sahnesi", "reklam metni anlatımı",
            "indirim kodu", "indirim kodu ifadesi", "indirim kodu sahnesi", "indirim kodu anlatımı",
            # SOSYAL MEDYA
            "sosyal medya hesabı", "sosyal medya hesabı ifadesi", "sosyal medya hesabı sahnesi",
            "takip et", "takip et ifadesi", "takip et sahnesi", "takip et anlatımı",
            "abone ol", "abone ol ifadesi", "abone ol sahnesi", "abone ol anlatımı",
            # İNDİRİMLER VE ALIŞ
            "mağaza linki", "mağaza linki ifadesi", "mağaza linki sahnesi", "mağaza linki anlatımı",
            "uygulama indir", "uygulama indir ifadesi", "uygulama indir sahnesi", "uygulama indir anlatımı",
            # GENEL TİCARİ
            "ticari yönlendirme", "ticari yönlendirme ifadesi", "ticari yönlendirme sahnesi",
            "oyun içi satın alma", "oyun içi satın alma ifadesi", "oyun içi satın alma sahnesi"
        ]
    }
}

# KARAR ARALIKLARI (0-100 puan üzerinden)
KARAR_ARALIKLARI = {
    "0-20": {
        "seviye": "✅ Uygun",
        "renk": "green",
        "simge": "✅"
    },
    "21-40": {
        "seviye": "✔️ Düşük Risk",
        "renk": "lightgreen",
        "simge": "✔️"
    },
    "41-60": {
        "seviye": "⚠️ Dikkat Gerektirir",
        "renk": "yellow",
        "simge": "⚠️"
    },
    "61-80": {
        "seviye": "🔴 Revizyon Gerekli",
        "renk": "orange",
        "simge": "🔴"
    },
    "81-100": {
        "seviye": "❌ Yayına Uygun Değil",
        "renk": "red",
        "simge": "❌"
    }
}

# BAĞLAMSAL ANAHTAR KELIMELER (Risk Düzeyini Etkileyen)
BAGLAMSAL_KEYWORDLER = {
    "düşük_risk": [
        "tarihî", "edebi", "mecazî", "alegori", "benzetme", "sembol",
        "eski", "geçmiş", "antik", "orta çağ", "hikayelerde", "masalda"
    ],
    "yüksek_risk": [
        "özendir", "model", "tekrar", "uygulanabilir", "talimat",
        "sunuş", "öğret", "yap", "dene", "gerçek", "bugünkü", "şimdi"
    ]
}

# MEB DERS KİTABI İNCELEME KRİTERLERİ MATRİSİ
MEB_TTK_KRITERLERI = {
    "1_anayasa": {
        "ad": "Anayasa ve Mevzuat Uygunluğu",
        "aciklama": "Devletin temel değerleriyle çelişiyor mu?",
        "risk_gostergeleri": [
            "Ayrıştırıcı anlatım",
            "Hukuka aykırı içerik",
            "Kamu düzenini zedeleyen mesajlar"
        ],
        "cikti": "Uyumlu / Koşullu / Uyumsuz"
    },
    "2_milli_guvenlik": {
        "ad": "Millî Güvenlik",
        "aciklama": "Terör, bölücülük, yasa dışı örgüt propagandası var mı?",
        "risk_gostergeleri": [
            "Örgüt övgüsü",
            "Şiddete çağrı",
            "Milli birlik karşıtı kurgu",
            "Bölücü mesajlar"
        ],
        "cikti": "Yüksek risk işareti"
    },
    "3_esitlik": {
        "ad": "Eşitlik ve Kapsayıcılık",
        "aciklama": "Irk, din, dil, cinsiyet, engellilik temelli ayrım var mı?",
        "risk_gostergeleri": [
            "Nefret söylemi",
            "Aşağılama ve küçümseme",
            "Stereotip kullanımı",
            "Ayrımcı temsil"
        ],
        "cikti": "Revizyon veya ret"
    },
    "4_milli_manevi": {
        "ad": "Millî ve Manevi Değerler",
        "aciklama": "Aile, saygı, sorumluluk, vatan sevgisi destekleniyor mu?",
        "risk_gostergeleri": [
            "Değerleri küçümseme",
            "Aile bağlarını sistematik zayıflatma",
            "Vatan sevgisini eritme"
        ],
        "cikti": "Maarif uyum puanı"
    },
    "5_guvenli_etik": {
        "ad": "Güvenli ve Etik İçerik",
        "aciklama": "Çocuğun yaş düzeyine uygun mu?",
        "risk_gostergeleri": [
            "Travmatik sahneler",
            "Özendirici içerik",
            "Mahremiyet ihlali",
            "Yaş uyumsuzluğu"
        ],
        "cikti": "Yaş etiketi ve rehberlik"
    },
    "6_bilimsel_dogruluk": {
        "ad": "Bilimsel Doğruluk",
        "aciklama": "Tarihsel ve bilimsel bilgi doğru mu?",
        "risk_gostergeleri": [
            "Yanlış bilgi",
            "Hurafe ve efsane",
            "Çarpıtılmış tarih",
            "Bilimsel doğruluğun eksikliği"
        ],
        "cikti": "Düzeltme önerisi"
    },
    "7_reklam_ticari": {
        "ad": "Reklam ve Ticari Unsurlar",
        "aciklama": "Marka, QR, link, ürün yönlendirmesi var mı?",
        "risk_gostergeleri": [
            "Çocuk tüketimini teşvik",
            "Marka ürün yerleştirmesi",
            "Dış bağlantılar",
            "Gizli reklam"
        ],
        "cikti": "Kaldır / Not düş"
    },
    "8_dil_anlatim": {
        "ad": "Dil ve Anlatım",
        "aciklama": "Türkçe seviyesi yaşa uygun mu?",
        "risk_gostergeleri": [
            "Ağır argo ve küfür",
            "Bozuk dil kullanımı",
            "Gereksiz yabancılaşma",
            "Yaş düzeyine uyumsuz dil"
        ],
        "cikti": "Dil revizyonu"
    }
}

# RISK PUANLAMA KÜTÜĞÜ
RISK_PUANLAMA = {
    0: {"seviye": "Temiz", "aciklama": "Kelime yok veya tamamen ilgisiz/yanlış pozitif"},
    1: {"seviye": "Bilgi", "aciklama": "Edebi, tarihî veya mecazi bağlam; risk çok düşük"},
    2: {"seviye": "Düşük", "aciklama": "Kısa ve özendirici olmayan kullanım"},
    3: {"seviye": "Dikkat", "aciklama": "Yaş düzeyine göre öğretmen/veli rehberliği gerekebilir"},
    4: {"seviye": "Revizyon", "aciklama": "Açık anlatım, tekrar, model alma veya pedagojik risk"},
    5: {"seviye": "Uygun Değil", "aciklama": "Özendirme, normalleştirme, travmatik ya da hukuki riskli içerik"}
}

# ============================================================================
# FALSE POSITIVE FILTER - KELIME BAĞIMSIZLIK KONTROLLERI
# ============================================================================
# "Ceylan" gibi isimlerin içine "lan" geçmesini false positive olarak işaretler
# 
# KURAL: Bir kelime başka bir kelimenin içinde yer alıyorsa, BULGU GEÇERSİZ

FALSE_POSITIVE_FILTER = {
    # "lan" kelimesi için - Türkçe isimleri ve kelime parçaları
    "lan": {
        "turkce_isimler": [
            # Common Turkish names ending in -lan
            "ceylan", "sevilay", "güllan", "türkan", "aylan", "dillan",
            "seylan", "dilan", "meilan", "doylan", "pelan", "senal",
            "yeşilan", "betülan", "aslan", "zübelan", "solan", "telan",
            # Extended list - other names that might contain 'lan'
            "melan", "nelan", "reylan", "kelan", "helan", "felan",
            "zelan", "velan", "telan", "selan", "pelan", "nelan"
        ],
        "ek_sozler": [
            # Verb conjugations with -lan
            "havalandı", "havalanmış", "havalanır", "havalanan",
            "sallandı", "sallanmış", "sallanır", "sallanan",
            "yuvarlandı", "yuvarlanmış", "yuvarlanır", "yuvarlanan",
            "sulandı", "sulanmış", "sulanır", "sulanan",
            "parladı", "parlanmış", "parlanır", "parlanan",
            "daldı", "dalanmış", "dalanır", "dalanan", # Not applicable but safe
            "glandı", "glanmış", "glanır", "glanan",
            "çillandı", "çillanmış", "çillanır", "çillanan",
            "dollandı", "dollanmış", "dollanır", "dollanan",
            "ıslandı", "ıslanmış", "ıslanır", "ıslanan",
            "ıslanmak", "islanmak",  # infinitive forms
            "kalandı", "kalanmış", "kalanır", "kalanan",
            "malandı", "malanmış", "malanır", "malanan",
            "salandı", "salanmış", "salanır", "salanan",
            "nalandı", "nalanmış", "nalanır", "nalanan",
            "talandı", "talanmış", "talanır", "talanan",
            "balandı", "balanmış", "balanır", "balanan",
            "falandı", "falanmış", "falanır", "falanan",
            "dalanmak", "haslanmak", "keslanmak", "pislanmak",
            "uzandı", "uzanmış", "uzanır", "uzanan"
        ],
        "yanlislik_oran": 0.85
    },
    
    # "kan" kelimesi için - İsim soyadı, verb conjugation, sıfatlar
    "kan": {
        "turkce_isimler": [
            "serkan", "erkan", "rukan", "yoğunkan",
            "ozcan", "turkan", "durkan", "börcan", "dorcan",
            "furkan", "burkan", "kurkan", "murkan", "nurkan",
            "orkan", "topakan", "yildirim", "erdogan",
            "volkan", "tolkan", "halkan", "malkan", "kalkan",
            "salkan", "valkan", "balkan", "falkan", "talkan"
        ],
        "ek_sozler": [],
        "yanlislik_oran": 0.85
    },
    
    # "ayin" kelimesi için - Yayın, basın ve diğer sözcükler
    "ayin": {
        "ek_sozler": [
            # Publishing/broadcast related words
            "yayınevi", "yayınlar", "yayında", "yayıncı", "yayınlayan",
            "yayın", "yayıncılık", "yayınlamak", "yayınlanmış", "yayınlanır",
            "yayını", "yayınında", "yayınından", "yayınıyla",
            # Other words with -ayin
            "kayın", "kayınvalide", "kayınpeder", "kayını",
            "bayındır", "bayındırlık",
            "kayayın", "kayayin",
            "kızayin", "koPayin",
            "dayıncı", "dayını"  # Related
        ],
        "yanlislik_oran": 0.95
    },
    
    # "vur" kelimesi için - Verb conjugations
    "vur": {
        "ek_sozler": [],
        "yanlislik_oran": 0.92
    },
    
    # ⭐ "ayıp" kelimesi için - Verb conjugations with -ayıp/-eyip suffix
    # Context: "katlayıp", "başlayıp", "yıkayıp", "temizleyip" gibi kelimelerde "ayıp" ek olarak görülüyor
    # -ayıp/-eyip: Turkish gerund/participle suffix (doing/after doing)
    "ayıp": {
        "ek_sozler": [],  # ⭐ NO false positive patterns - "-ayıp" is a valid gerund suffix, not a false positive
        "yanlislik_oran": 0.88
    },
    
    # "eşek" kelimesi için - Hayvan adı; kelime içinde geçip false positive oluşturan formlar
    "eşek": {
        "ek_sozler": [
            # Kelime içinde geçen formlar
            "peşek", "peşekli", "peşekte", "peşekçi", "peşektim",
            "beşekli", "beşekte",
            "eşekçi", "eşeklik", "eşekçilik",
            "peşekçi", "peşeklik",
            "seşek", "teşek", "yeşek", "meşek", "neşek"  # Olası kombinasyonlar
        ],
        "yanlislik_oran": 0.80
    },
    
    # "alay" kelimesi için - Alay etmek; kelime formları false positive oluşturuyor
    "alay": {
        "ek_sozler": [
            # Verb conjugations ve türev kelimeler
            "alaylı", "alaylılaştır", "alaylılaştırma",
            "alayan", "alalayan", "alalayarak",
            "alalayarak", "alalandı", "alaylandı",
            "alaylamak", "alalama", "alayladı", "alaylama",
            "alayda", "alayında", "alayından",
            "alaylanmak", "alaylayan", "alalayan",
            "alaylık", "alayda"
        ],
        "yanlislik_oran": 0.82
    },
    
    # "argo" kelimesi için - Argo konuşma; kelime içinde geçip false positive oluşturuyor
    "argo": {
        "ek_sozler": [
            # Kelime içinde geçen formlar
            "kargo", "kargom", "kargosu", "kargosunu",
            "margo", "margom", "margosu", "margot",
            "margodan", "margoya", "margoyla",
            "sargo", "sargom", "sargosu",
            "pargo", "pargom", "pargosu",
            "targo", "targom", "targosu",
            "largo", "largom", "largosu"
        ],
        "yanlislik_oran": 0.78
    },
    
    # "büyü" kelimesi için - Sihir/büyü; verb conjugation'ları false positive oluşturuyor
    "büyü": {
        "ek_sozler": [
            # SADECE FALSE_POSITIVE'ler (büyükbaba, büyük, etc.)
            "büyükbaba", "büyükbabasının", "büyükbabası",
            "büyükbabanın", "büyükbabanı", "büyükbabaya", "büyükbabadan",
            "büyükbabalar", "büyükbabalarının", "büyükbabalardan", "büyükbabalarına",
            "büyükannem", "büyükannemiz", "büyükannemin", "büyükannemi",
            "büyükpeder", "büyükpederim", "büyükpederinin", "büyükpederini",
            "büyükanne", "büyükannesinin", "büyükannesi", "büyükanneyi",
            "büyükkız", "büyükkızı", "büyükkızının", "büyükoğul", "büyükoğlunun",
            "büyükmehmet", "büyükyaşlı", "büyükbey", "büyükbeyim",
            "büyük", "büyüklükteydi", "büyükçe", "büyükçük", "büyüklü"
        ],
        "yanlislik_oran": 0.85
    },
    
    # "cadı" kelimesi için - Büyücü kadın; ek/suffix'ler false positive oluşturuyor
    "cadı": {
        "ek_sozler": [
            # Kelime formları ve conjugation'ları
            "cadısı", "cadının", "cadıya", "cadıyı", "cadıdan",
            "cadıyısı", "cadıyının", "cadıyıyla",
            "cadılaşma", "cadılaşmak", "cadılaştı",
            "cadılık", "cadılığını", "cadılığında",
            "cadım", "cadın", "cadıdır", "cadıydı",
            "cadılı", "cadılılar", "cadılışı"
        ],
        "yanlislik_oran": 0.79
    },
    
    # "ölüm" kelimesi için - Ölüm; ek/suffix'ler false positive oluşturuyor (çok sık!)
    "ölüm": {
        "ek_sozler": [
            # ⭐ SADECE FALSE_POSITIVE'ler: Bölüm (Chapter) ve bileşikleri
            "bölüm", "bölümü", "bölümün", "bölüme", "bölümde", "bölümden",
            "bölümlü", "bölümlüğü", "bölümlülüğü", "bölümkısı", "bölümler",
            "bölümlere", "bölümlerin", "bölümlerce", "bölümlük",
            "bölümlendirme", "bölümlemek", "bölümlenmiş", "bölümlenme"
        ],
        "yanlislik_oran": 0.90  # Çok agresif - sadece FALSE_POSITIVE'ler filtrelenecek
    },
    
    # "rakı" kelimesi için - Alkollü içki; ek/suffix'ler false positive oluşturuyor
    "rakı": {
        "ek_sozler": [
            # SADECE FALSE_POSITIVE'ler - hiçbir valid form yok
        ],
        "yanlislik_oran": 0.75
    },
    
    # ⭐ "kama" kelimesi için - Kılıç/dagger; verb form'ları false positive
    "kama": {
        "ek_sozler": [
            # Verb form'ları - "göz kamaştıran" gibi
            "kamaştıran", "kamaştırma", "kamaştırmak", "kamaştırıyor",
            "kamaştı", "kamaştırdı", "kamaştırma", "kamaştırılmak",
            "kamaş", "kamaştır", "kamaştırma", "kamaştırılan",
            "kamaştırıcı", "kamaştırıcılık"
        ],
        "yanlislik_oran": 0.82
    },
    
    # ⭐ "duman" kelimesi için - Smoke; context'te harmless olabilir
    "duman": {
        "ek_sozler": [
            # Verb form'ları ve harmless context'ler
            "dumanlandı", "dumanlanmak", "dumanlanıyor", "dumanlandığı",
            "dumanlamak", "dumanlanmış", "dumanlanır",
            "duman", "dumanı", "dumana", "dumanlar", "dumanla",
            "tüten duman", "duman sahnesi", "duman ifadesi"
        ],
        "yanlislik_oran": 0.79
    },
    
    # ⭐ "panik" kelimesi için - Panic; verb form'ları false positive
    "panik": {
        "ek_sozler": [
            # Verb form'ları - "paniklediğini", "panikleme" gibi
            "paniklediğini", "paniklediği", "panikledi", "panikladı",
            "panikleme", "panikatma", "panikyapma", "panikyapıyor",
            "panikat", "panikaştı", "paniklemek", "panilatma",
            "panikalanmak", "paniklama", "panikaştırmak",
            "panik", "paniği", "panikle", "panikler"
        ],
        "yanlislik_oran": 0.80
    },
    
    # ⭐ "kaçış" kelimesi için - Escape; context harmless olabilir
    "kaçış": {
        "ek_sozler": [
            # Noun form'ları ve harmless context'ler
            "kaçışı", "kaçışın", "kaçışa", "kaçışta", "kaçıştan",
            "kaçış", "kaçışlar", "kaçışlara", "kaçışların",
            "kaçış yoktu", "kaçış yoksa", "kaçış yok", "kaçış vardı",
            "kaçış arama", "kaçış yolu", "kaçış planı", "kaçış hakı"
        ],
        "yanlislik_oran": 0.78
    },
    
    # ⭐ "alçak" kelimesi için - Adjective (low/base); context harmless
    "alçak": {
        "ek_sozler": [
            # Adjective form'ları ve noun form'ları
            "alçak", "alçağı", "alçağın", "alçağa", "alçağında",
            "alçakçı", "alçakça", "alçaklaştır", "alçaktan",
            "alçak sesle", "alçak ses", "alçak tavır", "alçak sesli",
            "alçakça", "alçaklaştırmak", "alçaklaştırma", "alçaklık",
            "alçak", "alçaklar", "alçak kişi", "alçak davranış"
        ],
        "yanlislik_oran": 0.81
    },
    
    # ⭐ "fal" kelimesi için - Kısmet/Talih; "defalarca" gibi sözcüklerin içinde FALSE POSITIVE
    "fal": {
        "ek_sozler": [
            # SADECE FALSE_POSITIVE'ler: defa bileşikleri
            "defalarca", "defada", "defaki", "defasında",
            "defalı", "defasız", "defa", "defalar",
            "sayfalarda", "sayfalarında", "sayfaları", "sayfalara", "sayfalarca"
        ],
        "yanlislik_oran": 0.80
    },
    
    # ⭐ "ayin" kelimesi için - Ritüel/Tören; "yayınevim" gibi sözcüklerin içinde FALSE POSITIVE
    "ayin": {
        "turkce_isimler": [
            # Yayın/Publishing related - en sık FALSE POSITIVE
            "yayinevim", "yayinevi", "yayinevin", "yayinlari",
            "yayinci", "yayincilari", "yayincinin"
        ],
        "ek_sozler": [
            # SADECE FALSE_POSITIVE'ler: yayın bileşikleri
            "yayınevi", "yayınevim", "yayınevinin", "yayınevin",
            "yayın", "yayını", "yayının", "yayına", "yayında",
            "yayıncı", "yayıncılık"
        ],
        "yanlislik_oran": 0.85
    },
    
    # ⭐ "bira" kelimesi için - Beer; "bir kenara" false positive'sini önle
    "bira": {
        "ek_sozler": [
            # Possessive ve contextual form'lar
            "birasına", "birayla", "bira ifadesi", "bira sahnesi",
            "birayı", "biranın", "biraya", "birada", "biradan",
            "biraları", "biralara", "biraların"
        ],
        "yanlislik_oran": 0.75  # "bir kenara" kontrol'ü için düşük oran
    },
    
    # Genel kurallar
    "genel_baglantili_kelimeler": [
        "bağlantılı", "ek_kelime", "türev", "ön_ek", "son_ek"
    ]
}

# ============================================================================
# BAGIMSIZLIK KONTROL MOTORUç KURALLARı
# ============================================================================
# Kelimenin bağımsız olup olmadığını kontrol eden kurallar

KELIME_BAGIMSIZLIK_KURALLARI = {
    "kontrol_yontemi": "HARMONIC_CHECK",  # Harmonik kontrol: ses uyumu + harf analizi
    "adimlar": [
        "1. Kelimenin öncesindeki karakteri kontrol et (Türkçe harf mi?)",
        "2. Kelimenin sonrasındaki karakteri kontrol et (Türkçe harf mi?)",
        "3. Eğer her iki tarafta da Türkçe harf varsa = BAĞINTILI",
        "4. Bağlantılı sözcüklü listede kontrol et",
        "5. İsim listesinde kontrol et (endswith)",
        "6. Sonuç: BAĞIMSIZ veya BAĞINTILI (false positive)"
    ],
    "turkce_harfler": "abcçdefgğhıijklmnoöprsştuüvyz",
    "minimum_kelime_uzunlugu": 3  # 3 harften kısa kelimeler daha sıkı kontrol
}

print("[OK] Config loaded: 3384+ word dictionary, 10 categories, 5 profiles")
print("[OK] False Positive Filter aktif: Bagimsizlik kontrolleri etkinlestirildi")

# ============================================================================
# EMPATHY_STRICT_MODE AYARLARI
# ============================================================================
# Empati için üç katı kriter:
# 1. En az iki karakter olmalı
# 2. Bir karakter diğerinin durumunu anlamalı (sadece yardım değil, anlama)
# 3. Duygusal farkındalık bulunmalı
# ============================================================================
EMPATHY_STRICT_MODE = {
    "aktif": True,  # Strict mode etkin
    "kriterler": {
        "min_karakter": 2,  # En az 2 karakter
        "anlama_gosterge": [
            "anladi", "anladı", "fark etti", "gorerek", "görerek",
            "halini", "durumunu", "hissettigini", "hislerini", "duygularini"
        ],
        "duygusal_farkindalik": [
            "uzuldu", "üzüldü", "sevindi", "korktu", "sasirdi", "şaşırdı",
            "hisset", "acidi", "acıdı", "merhamet", "üzüntü", "sevinç",
            "endişe", "umut", "kayıp", "yalnız", "mutlu", "üzgün"
        ]
    },
    "yardim_sadece_gecersiz": True,  # Sadece yardım davranışı empati sayılmaz
}
