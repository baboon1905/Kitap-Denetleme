"""
MEB Criteria Risk Calculation Based on MAARIF Categories
Refactored to use actual findings instead of keyword search
"""

KATEGORI_TO_MEB_KRITER_YENI = {
    # MAARIF Category → (MEB Kriter, risk_factor)
    "siddet_suc": ("guvenlik", 1.0),
    "cinsellik_mahremiyet": ("milli_manevi", 1.0),
    "zararlı_alışkanlıklar": ("milli_manevi", 0.8),
    "kaba_dil_hakaret": ("dil", 1.0),
    "ayrımcılık_nefret": ("esitlik", 1.0),
    "korku_travma": ("guvenlik", 0.8),
    "okültizm_batıl": ("milli_manevi", 1.0),
    "dijital_risk": ("bilimsel", 0.6),
    "olumsuz_davranış": ("milli_manevi", 0.7),
    "reklam_ticari": ("reklam", 1.0)
}

RISK_URETEN_BAGLAMLAR = {
    "ozendirici",
    "taklit_tesviki",
    "pozitif_gosterim",
    "romantik_fiziksel_temas",
    "evlilik_disi_iliski",
    "cinsel_cagrisim",
    "aile_butunlugu_olumsuz_ozendirme",
    "zararli_aliskanlik_sahnelenmesi",
    "siddet_sahnelenmesi",
    "suc_sahnelenmesi",
    "tehlikeli_davranis_sahnelenmesi",
    "aile_mahremiyet_sahnelenmesi",
    "tema_olay_orgusu",
    "davranis_normalizasyonu",
}

def hesapla_meb_kriterleri_maarif_ile(kategori_bulgulari: dict) -> dict:
    """
    MEB kriter risk'ini MAARIF kategori bulgularından hesapla
    
    Returns:
    {
        "anayasa": {"risk": 0, "karar": "Uyumlu", "aciklama": "..."},
        "milli_guvenlik": {"risk": 3, "karar": "Uyarı", "aciklama": "..."},
        ...
    }
    """
    
    # MEB kriterler - başta 0 risk
    meb_kriterler = {
        "anayasa": {
            "ad": "Anayasa ve Mevzuat Uygunluğu",
            "risk": 0,
            "bulgular_sayisi": 0
        },
        "milli_guvenlik": {
            "ad": "Millî Güvenlik",
            "risk": 0,
            "bulgular_sayisi": 0
        },
        "esitlik": {
            "ad": "Eşitlik ve Kapsayıcılık",
            "risk": 0,
            "bulgular_sayisi": 0
        },
        "milli_manevi": {
            "ad": "Millî ve Manevi Değerler",
            "risk": 0,
            "bulgular_sayisi": 0
        },
        "guvenlik": {
            "ad": "Güvenli ve Etik İçerik",
            "risk": 0,
            "bulgular_sayisi": 0
        },
        "bilimsel": {
            "ad": "Bilimsel Doğruluk",
            "risk": 0,
            "bulgular_sayisi": 0
        },
        "reklam": {
            "ad": "Reklam ve Ticari Unsurlar",
            "risk": 0,
            "bulgular_sayisi": 0
        },
        "dil": {
            "ad": "Dil ve Anlatım",
            "risk": 0,
            "bulgular_sayisi": 0
        }
    }
    
    # MAARIF kategorilerini scan et
    for maarif_cat, cat_data in kategori_bulgulari.items():
        if not cat_data.get("bulundu") or cat_data.get("toplam_bulgu", 0) == 0:
            continue  # Bu kategoride bulgu yok
        
        # Bu kategorinin hangi MEB kriterine mapping'i var?
        if maarif_cat not in KATEGORI_TO_MEB_KRITER_YENI:
            continue
        
        meb_kriter_name, risk_factor = KATEGORI_TO_MEB_KRITER_YENI[maarif_cat]
        tum_bulgular = cat_data.get("bulunan_kelimeler", [])
        problemli_bulgular = [
            bulgu for bulgu in tum_bulgular
            if bulgu.get("problemliMi") is True
            and float(bulgu.get("riskPuani", bulgu.get("baglamsal_risk", 0)) or 0) > 0
            and bulgu.get("baglamTipi") in RISK_URETEN_BAGLAMLAR
        ]
        toplam_bulgu = len(problemli_bulgular)
        if toplam_bulgu == 0:
            continue

        ortalama_risk = sum(
            float(bulgu.get("riskPuani", bulgu.get("baglamsal_risk", 0)) or 0)
            for bulgu in problemli_bulgular
        ) / toplam_bulgu
        
        # MEB kriter risk'ini hesapla.
        # Problemli olmayan bulgular raporda gorunur ama risk 0 kalmalidir.
        if ortalama_risk <= 0:
            calculated_risk = 0
        else:
            calculated_risk = min(5, max(1, int(ortalama_risk * risk_factor)))
        
        # MEB kriterine ekle (yüksek risk tercih edilir)
        meb_kriterler[meb_kriter_name]["risk"] = max(
            meb_kriterler[meb_kriter_name]["risk"],
            calculated_risk
        )
        meb_kriterler[meb_kriter_name]["bulgular_sayisi"] += toplam_bulgu
    
    # Risk scorelarına göre "karar" değerini belirle
    for kriter_key, kriter_data in meb_kriterler.items():
        risk = kriter_data["risk"]
        
        if kriter_key == "milli_manevi":
            if risk == 0:
                karar = "Güçlü"
            elif risk <= 2:
                karar = "Orta"
            else:
                karar = "Zayıf"
        elif kriter_key == "esitlik":
            if risk == 0:
                karar = "Uygun"
            elif risk <= 2:
                karar = "Revizyon"
            else:
                karar = "Ret"
        elif kriter_key == "reklam":
            if risk == 0:
                karar = "Temiz"
            elif risk == 1:
                karar = "Hafif"
            else:
                karar = "Yasaklı"
        elif kriter_key == "dil":
            if risk == 0:
                karar = "Uygun"
            elif risk <= 2:
                karar = "Dikkat"
            else:
                karar = "Uyumsuz"
        else:
            # Genel kriterler
            if risk == 0:
                karar = "Uygun"
            elif risk <= 2:
                karar = "Uyarı"
            else:
                karar = "Yüksek Risk"
        
        kriter_data["karar"] = karar
    
    return meb_kriterler
