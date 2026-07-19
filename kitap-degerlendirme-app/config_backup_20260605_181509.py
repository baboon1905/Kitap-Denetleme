"""
Türkiye Yüzyılı Maarif Modeli Değerlendirme Kriterleri
MAARİF MODELİ YAYIN DENETİM SİSTEMİ v1.0
"""

# ============================================================================
# 1. ANALIZ PROFİLLERİ - Belgeye göre 5 profil (Sayfa 3)
# ============================================================================
ANALIZ_PROFILLERI = {
    "maarif_meb": {
        "ad": "Maarif/MEB",
        "aciklama": "Müfettiş ve okul hassasiyeti",
        "yaklasim": "Milli-manever değerler, zararlı alışkanlıklar ve mahremiyet daha sıkı puanlanır",
        "kullanim": "Okul listeleri, okuma kitapları",
        "agirliklari": {
            "sigara_alkol": 1.3,      # Zararlı alışkanlıklar sıkı
            "cinsellik_mahremiyet": 1.4,  # Mahremiyet sıkı
            "siddet": 1.2,
            "argo_kufur": 1.1,
            "islami_ihlal": 1.2,      # Milli-manevi değerler
            "aile_degerleri": 0.9
        }
    },
    "hibrit": {
        "ad": "Hibrit",
        "aciklama": "Yayınevi + Maarif dengesi",
        "yaklasim": "Edebi bağlam korunur, sakıncalı içerik bağlamla tartılır",
        "kullanim": "Önerilen ana mod",
        "agirliklari": {
            "sigara_alkol": 1.0,
            "cinsellik_mahremiyet": 1.0,
            "siddet": 1.0,
            "argo_kufur": 0.9,
            "islami_ihlal": 0.9,
            "aile_degerleri": 1.0
        }
    },
    "editoryal": {
        "ad": "Editoryal",
        "aciklama": "Yayınevi iç değerlendirme",
        "yaklasim": "Edebi özgürlük ve yaş uygunluğu ön plandadır",
        "kullanim": "Yayın kurulu değerlendirmesi",
        "agirliklari": {
            "sigara_alkol": 0.7,
            "cinsellik_mahremiyet": 0.8,
            "siddet": 0.8,
            "argo_kufur": 0.6,
            "islami_ihlal": 0.6,
            "aile_degerleri": 0.9
        }
    },
    "hassas_veli": {
        "ad": "Hassas Veli",
        "aciklama": "En sıkı aile hassasiyeti",
        "yaklasim": "Alkol, sigara, flört, korku, kaba dil daha yüksek risk",
        "kullanim": "Özel okul/veli raporu",
        "agirliklari": {
            "sigara_alkol": 1.5,      # En yüksek
            "cinsellik_mahremiyet": 1.6,  # En yüksek
            "siddet": 1.4,
            "argo_kufur": 1.3,
            "islami_ihlal": 1.2,
            "aile_degerleri": 1.1,
            "korku_travma": 1.3
        }
    },
    "kuruma_ozel": {
        "ad": "Kuruma Özel",
        "aciklama": "Kurum bazlı ayarlanabilir denetim",
        "yaklasim": "Ağırlıklar admin panelinden değiştirilebilir",
        "kullanim": "Okul zincirleri, yayınevi müşterileri",
        "agirliklari": {  # Varsayılan, admin tarafından değiştirilir
            "sigara_alkol": 1.0,
            "cinsellik_mahremiyet": 1.0,
            "siddet": 1.0,
            "argo_kufur": 1.0,
            "islami_ihlal": 1.0,
            "aile_degerleri": 1.0
        }
    }
}

# ============================================================================
# 2. RISK PUANLAMA KÜTÜĞÜ (Sayfa 3 - 0-5 risk puanı sistemi)
# ============================================================================
RISK_PUANLAMA = {
    0: {
        "seviye": "Temiz",
        "aciklama": "Kelime yok veya tamamen ilgisiz/yanlış pozitif"
    },
    1: {
        "seviye": "Bilgi",
        "aciklama": "Edebi, tarihî veya mecazi bağlam; risk çok düşük"
    },
    2: {
        "seviye": "Düşük",
        "aciklama": "Kısa ve özendirici olmayan kullanım"
    },
    3: {
        "seviye": "Dikkat",
        "aciklama": "Yaş düzeyine göre öğretmen/veli rehberliği gerekebilir"
    },
    4: {
        "seviye": "Revizyon",
        "aciklama": "Açık anlatım, tekrar, model alma veya pedagojik risk"
    },
    5: {
        "seviye": "Uygun Değil",
        "aciklama": "Özendirme, normalleştirme, travmatik ya da hukuki riskli içerik"
    }
}

# KARAR ARALIKLARI (Sayfa 3 - 100 üzerinden)
KARAR_ARALIKLARI = {
    "0-20": {
        "seviye": "Uygun",
        "renk": "green",
        "simge": "✅"
    },
    "21-40": {
        "seviye": "Düşük Risk",
        "renk": "lightgreen",
        "simge": "✔️"
    },
    "41-60": {
        "seviye": "Dikkat Gerektirir",
        "renk": "yellow",
        "simge": "⚠️"
    },
    "61-80": {
        "seviye": "Revizyon Gerekli",
        "renk": "orange",
        "simge": "🔴"
    },
    "81-100": {
        "seviye": "Yayına Uygun Değil",
        "renk": "red",
        "simge": "❌"
    }
}

# Maarif Modeli Öğrenci Profili (10 Profil)
MAARIF_PROFILLERI = {
    "sorgulayici": {
        "ad": "Sorgulayıcı",
        "aciklama": "Merak eden, soru soran, araştıran karakter"
    },
    "cesaretli": {
        "ad": "Cesaretli",
        "aciklama": "Zorluklar karşısında cesur duran, riski alan karakter"
    },
    "uretken": {
        "ad": "Üretken",
        "aciklama": "Yaratıcı çözümler üreten, yapıcı eğilimli karakter"
    },
    "bilge": {
        "ad": "Bilge",
        "aciklama": "Hikmet sahibi, bilgili ve erdemli karakterler"
    },
    "ahlaklı": {
        "ad": "Ahlaklı",
        "aciklama": "Dürüst, doğru davranışları tercih eden karakter"
    },
    "merhametli": {
        "ad": "Merhametli",
        "aciklama": "Başkasının acısını anlayan, yardımsever karakter"
    },
    "vatansever": {
        "ad": "Vatansever",
        "aciklama": "Vatan ve millet sevgisine sahip karakter"
    },
    "estetik": {
        "ad": "Estetik",
        "aciklama": "Doğal güzelliğe, sanat ve estetik değerlere sahip karakter"
    },
    "iradeli": {
        "ad": "İradeli",
        "aciklama": "Azimli, kararlı, hedeflere ulaşmak için çabalayan karakter"
    },
    "saglikli": {
        "ad": "Sağlıklı",
        "aciklama": "Fiziksel ve ruh sağlığı dikkate alan karakter"
    }
}

# MEB TTK (Talim ve Terbiye Kurulu) Kriterleri
MEB_TTK_KRITERLERI = {
    "1_1": {
        "ad": "Anayasa ve Mevzuat Uygunluğu",
        "aciklama": "Türkiye Cumhuriyeti Anayasası ve mevzuatla uyum"
    },
    "1_2": {
        "ad": "Millî Güvenlik",
        "aciklama": "Millî güvenlik değerlerine uygunluk"
    },
    "1_3": {
        "ad": "Eşitlik ve Kapsayıcılık",
        "aciklama": "Farklı kökenden, dinden kişilerin saygılı temsili"
    },
    "1_4": {
        "ad": "Millî ve Manevi Değerler",
        "aciklama": "İslami değerler, Türk kültürü ve medeniyeti"
    },
    "1_5": {
        "ad": "Güvenli ve Etik İçerik",
        "aciklama": "Bağımlılık yapıcı, müstehcen, aşırı şiddet içermeme"
    },
    "1_6": {
        "ad": "Bilimsel Doğruluk",
        "aciklama": "Bilimsel bilgilerin doğru ve güncel olması"
    },
    "1_7": {
        "ad": "Reklam ve Ticari Unsurlar",
        "aciklama": "Ticari marka, reklam ve dış bağlantılardan uzak olması"
    },
    "1_9": {
        "ad": "Çevre ve Sürdürülebilir Yaşam",
        "aciklama": "Çevre bilinci ve sürdürülebilirlik teması"
    }
}

# ============================================================================
# 3. SAKINCALI KELIMELER VE İFADELER (1000+ kelime sözlüğü)
# Her kategori "risk_puani" ile işaretlenmiştir (0-5)
# ============================================================================
SAKINCALI_KELIMELER = {
    # ZARIRLI ALIŞKANLIKLAR - SIGARA
    "sigara": {
        "risk_puani": 4,
        "kelimeler": [
            "sigara", "tütün", "sigarası", "sigaraları", "sigarayı", "sigarasını",
            "tütünü", "tütüne", "tütünün", "tütünle", "tütünler", "tütünde",
            "duman", "dumanı", "dumana", "dumanlar", "dumanla",
            "cigara", "çiçek", "çigara", "şiringo", "paça", "kıvılcım",
            "ardı ardına sigara", "sigara içme", "sigara tiryakisi", "sigara bağımlısı"
        ]
    },
    
    # ZARIRLI ALIŞKANLIKLAR - ALKOL
    "alkol": {
        "risk_puani": 4,
        "kelimeler": [
            "alkol", "içki", "alkollü", "alkoholü", "alkole", "alkolsüz",
            "meykhane", "mey", "şarap", "şaraba", "şarabı", "şarabın",
            "viski", "viskiye", "viskisi", "rakı", "rakıya", "rakısı",
            "bira", "birasına", "birayla", "beer", "beverages",
            "kadehi", "kadeh", "kadehin", "kadehi", "kadehe",
            "bar", "barı", "barda", "barda", "barlar", "barında",
            "meyhane", "meyhaneyi", "meyhanede", "meyhanede",
            "türü", "şişe", "şişesi", "şişeyi", "şişede",
            "içki", "içkiyi", "içkiye", "içkile", "içkiler", "içkide",
            "sarhoş", "sarhoşu", "sarhoşlar", "sarhoşluk", "sarhosluk",
            "ayyaş", "ayyaşlık", "köstebek", "delibaş",
            "çekeç", "içecek", "içecekler", "içeceği", "içecekte"
        ]
    },
    
    # CİNSELLİK VE MAHREMIYET
    "cinsellik_mahremiyet": {
        "risk_puani": 5,
        "kelimeler": [
            "çıplak", "çıplağı", "çıplağın", "çıplakça", "çıplaklar",
            "mahrem", "mahremi", "mahremiyeti", "mahremiyetin", "mahrem olması",
            "taciz", "tacizci", "taciz etme", "tacize", "tacizin",
            "tecavüz", "tecavüzü", "tecavüz etme", "tecavüze", "tecavüzün",
            "ırz", "ırzını", "ırzına", "ırza", "ırzdan",
            "namus", "namusu", "namusunu", "namusunun", "namustan",
            "ayıp", "ayıbı", "ayıba", "ayıbla", "ayıplar",
            "utanç", "utancı", "utanca", "utançtan",
            "çocuk istismarı", "istismar", "istismarı", "istismardan",
            "fuhuş", "fuhuşu", "fuhuşa", "fuhuştan",
            "fahişe", "fahişesi", "fahişelik",
            "sapık", "sapıkları", "sapıklık",
            "uygunsuz", "uygunsuzca", "uygunsuzluk",
            "licik", "liciklik", "licikçe"
        ]
    },
    
    # ŞİDDET VE KAHRAMAN OLMAYAN EYLEMLER
    "siddet": {
        "risk_puani": 4,
        "kelimeler": [
            "silah", "silahı", "silaha", "silahla", "silahtan", "silahlar",
            "bomba", "bombasını", "bombaya", "bombalarla", "bombalar",
            "patlayıcı", "patlayıcı maddeler", "patlayıcılar",
            "öldür", "öldürdü", "öldürme", "öldürüyor", "öldürmek",
            "ölüm", "ölümü", "ölümün", "ölümle", "ölümden", "ölümlü",
            "vur", "vurdu", "vurma", "vuruyor", "vurmak",
            "darp", "darbesi", "darbe", "darbeleme",
            "bıçak", "bıçağı", "bıçakla", "bıçaktan",
            "tüfek", "tüfeği", "tüfekle", "tüfekten",
            "polis", "polise", "poliste", "polis tabancası",
            "asker", "askerim", "askerlik", "askerde", "askerden",
            "savaş", "savaşı", "savaşta", "savaştan",
            "kan", "kanı", "kanlı", "kanda", "kandan",
            "acı", "acısı", "acıyla", "acıdan",
            "ölü", "ölüsü", "ölüler", "ölüde",
            "cehennem", "cehennemde", "cehennemin",
            "kötü", "kötüsü", "kötülük", "kötüye",
            "şeytan", "şeytanı", "şeytanın", "şeytanlar",
            "ceza", "cezası", "cezayı", "cezadan",
            "hapis", "hapisane", "hapisanesi", "hapiste",
            "zulüm", "zulmü", "zulmünü", "zulümden",
            "işkence", "işkencesi", "işkenceyi", "işkenceden"
        ]
    },
    
    # ARGO VE KABA DİL
    "argo_kufur": {
        "risk_puani": 3,
        "kelimeler": [
            "küfür", "küfürlü", "küfürler", "küfüre",
            "hakaret", "hakaretler", "hakaretin", "hakarete",
            "argo", "argolar", "argocular", "argocu",
            "münasebetsiz", "münasebetsizlik", "münasebetsizce",
            "edepsiz", "edepsizlik", "edepsizce",
            "yaramaz", "yaramazzlık", "yaramazca",
            "uygunsuz", "uygunsuzca", "uygunsuzluk",
            "belirsiz ifadeler" # Spesifik kufurları listelemiyoruz çünkü eğitim aracı
        ]
    },
    
    # İSLAMİ DEĞERLERE AYKIRILLIK
    "islami_ihlal": {
        "risk_puani": 4,
        "kelimeler": [
            "sihir", "sihirbazlık", "sihirbaz", "sihri", "sihirle",
            "büyü", "büyüsü", "büyüsü", "büyüye", "büyülü",
            "fal", "falı", "falcı", "falından",
            "müstehcen", "müstehcen içerik", "müstehcenlik",
            "riya", "riyadır", "riyalar", "riyada",
            "günah", "günahı", "günahının", "günaha",
            "haram", "harami", "haramsa", "haramdan",
            "peygamberlik", "peygamber", "peygamberi", "peygamberin",
            "tanrı", "tanrıya", "tanrıdan", "tanrısı",
            "demi-tanrı", "yarı-tanrı", "ilah", "ilahta",
            "putperestlik", "put", "putları", "putuna",
            "ibadet", "ibadeti", "ibadete",
            "dua", "duası", "duasını", "duaya",
            "namaz", "namazı", "namaza", "namazın",
            "imam", "imamı", "imama",
            "müezzin", "müezzini", "müezzine",
            "cami", "camisi", "camide", "camilerde",
            "ezan", "ezanı", "ezanın",
            "ramazan", "ramazanı", "ramazanda",
            "bayram", "bayramı", "bayramda",
            "hac", "hacı", "hacıya", "hacıdan",
            "abdest", "abdesti", "abdeste",
            "mushaf", "mushafa", "mushaflı",
            "kuran", "kuranı", "kurana", "kuranın",
            "hadis", "hadisleri", "hadise", "hadislerinde"
        ]
    },
    
    # AİLE VE EVLILIK DEĞERLERI
    "aile_degerleri": {
        "risk_puani": 3,
        "kelimeler": [
            "boşanma", "boşanması", "boşanmak", "boşanmıştır",
            "ana-baba", "anası", "babası", "annesi", "babasının",
            "evlilik", "evliliği", "evlilikten", "evlenme",
            "evlenme", "evlenmek", "evlenmesi", "evlenmiş",
            "kız isteme", "nişanlılık", "nişanlanma",
            "gelin", "damat", "geline",
            "mihr", "mihri", "mihre",
            "cihaz", "cihazı", "cihazın",
            "gümrük", "gümrüksüz", "gümrüğü",
            "araba", "arabasına", "arabasını", "arabayla",
            "mücahede", "mücahedesi",
            "nikah", "nikahı", "nikaha", "nikahsız",
            "talak", "talak", "talakı",
            "iddete", "iddeti", "iddet", "iddette",
            "vesayet", "vesayet", "vesayeti",
            "velayet", "velayeti", "velayetine"
        ]
    },
    
    # ÇOCUK PSİKOLOJİSİ VE TRAVMA RİSKİ
    "korku_travma": {
        "risk_puani": 3,
        "kelimeler": [
            "korku", "korkusu", "korkuyla", "korkmak",
            "dehşet", "dehşeti", "dehşetinden",
            "paniğe", "paniği", "panikleme",
            "travma", "trauması", "traumayla",
            "ruh sağlığı", "psikolojik", "psikiyatrist",
            "stres", "stresi", "stresin", "stresli",
            "depresyon", "depresyonu", "depresyonda",
            "kaygı", "kaygısı", "kaygıyla",
            "panik", "paniği", "panikleme", "paniklemek",
            "fizik hale", "kötü muamele",
            "hayal", "hayali", "hayaletler",
            "korkunç", "korkunçça", "korkunçluğu",
            "müthiş", "müthişce",
            "açlık", "aç", "açlığında", "açlıktan",
            "yağmur", "dolu", "fırtına", "kasırga",
            "hastalık", "hastalığı", "hastalığından",
            "doktor", "doktora", "doktordaki",
            "ameliyat", "ameliyatı", "ameliyathane",
            "iğne", "iğnesi", "iğneyle"
        ]
    },
    
    # UYGUN OLMAYAN DİN TEMASLAR
    "din_temaları": {
        "risk_puani": 2,
        "kelimeler": [
            "hıristiyan", "hıristiyanlık", "hıristiyan kızı",
            "papaz", "papa", "kardinal",
            "aziz", "azizleri", "azizin",
            "kilise", "kilisede", "kiliseyi",
            "çarmıh", "haç", "haçını",
            "rab", "rabb", "rabbim",
            "melek", "melekler", "meleği",
            "şeytan", "şeytanı", "şeytanlar",
            "demon", "demonlar", "demonun",
            "iblis", "iblisi", "iblisten",
            "cinn", "cinni", "cinleri",
            "ruh", "ruhu", "ruhuyla",
            "ölüm sonrası", "ahiret", "akheret",
            "cennet", "cennette", "cennetine",
            "cehennem", "cehennemde", "cehenneminde",
            "yeniden doğuş", "reenkarnasyon"
        ]
    },
    
    # UYUŞTURUCU VE ZARIRLI MADDELER
    "uysturugu": {
        "risk_puani": 5,
        "kelimeler": [
            "uyuşturucu", "uyuşturu", "uyuşturu", "uyuşturucu maddeler",
            "esrar", "esrarı", "esrarla",
            "kenevir", "keneviri",
            "eroın", "eroinle",
            "kokain", "kokaini",
            "heroın", "heroinle",
            "ilaç bağımlılığı", "ilaçlar",
            "morfin", "morfini",
            "uyku ilacı", "uyku İLACI",
            "afyon", "afyonlu",
            "hashish", "haşış", "haşışı",
            "sentetik", "sentetik uyuşturucu"
        ]
    },
    
    # AYRIMILAŞTIRIMACI DİL
    "ayriminastirici_dil": {
        "risk_puani": 3,
        "kelimeler": [
            "ırk", "ırkçılık", "ırkçı", "ırksal",
            "din", "dine göre ayrımcılık",
            "cinsiyetçi", "cinsiyetçilik",
            "engelli", "engellilere karşı",
            "fakirlik", "fakir", "fakirlere",
            "göçmen", "mülteci", "yasadışı göçmen",
            "getto", "gecekondu", "slum",
            "asalak", "parazit", "solucan",
            "barbar", "vahşi", "uygar olmayan",
            "dış gözcü", "dış düşman", "dış kültür",
            "kültürel olmayan", "kültürsüz",
            "karışık medeniyet", "bozuk ahlak"
        ]
    },
    
    # PARA VE EKONOMİ KONULARI
    "para_ekonomi": {
        "risk_puani": 1,
        "kelimeler": [
            "borç", "borçu", "borçlara",
            "faiz", "faizi", "faize",
            "kira", "kirası", "kirasını",
            "vergi", "vergisi", "vergisini",
            "hırsızlık", "hırsız", "hırsızlar",
            "dolandırıcılık", "dolandırıcı",
            "rüşvet", "rüşveti",
            "yolsuzluk", "yolsuzluğu",
            "kaçakçılık", "kaçakçı",
            "kara para", "kara para aklama"
        ]
    }
}

# Bağlam Analiz Kelimeleri (Anlamı değiştiren kelimeleri belirtmek için)
BAGLAMSAL_KEYWORDLER = {
    "tarihî_bağlam": [
        "tarihin", "tarihte", "geçmişte", "eski", "antikçağda",
        "orta çağda", "osmanlı döneminde", "selçuklu", "bizans"
    ],
    "edebî_bağlam": [
        "metafor", "benzetme", "sembol", "simgesi", "hayal", "kurmaca",
        "kurgusal", "romanında", "hikâyede", "menkıbede"
    ],
    "mecazî_anlam": [
        "sanki", "gibi", "almanya benzeri", "sözleştirilmiş", "sembolik",
        "temsili", "yüksek sesle", "göz kararı"
    ]
}

# Değerlendirme Seviyeleri
DEGERLEN_SEVIYELERI = {
    "uyumlu": "✅ UYUMLU",
    "kismi_uyumlu": "⚠️ KISMİ UYUMLU",
    "dikkat": "⚠️ DİKKAT",
    "uyumsuz": "❌ UYUMSUZ"
}

# Hedef Kitleleri
HEDEF_KITLER = ["Okul Öncesi (3-5)", "İlkokul (6-8)", "Ortaokul (9-11)", "Lise (12+)", "Genel"]
