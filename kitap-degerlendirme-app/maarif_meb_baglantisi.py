"""
MAARIF Kategori → MEB Kriter Haritalama
"""

KATEGORI_TO_MEB_KRITER = {
    "siddet_suc": "guvenlik",
    "cinsellik_mahremiyet": "milli_manevi",
    "zararlı_alışkanlıklar": "milli_manevi",
    "kaba_dil_hakaret": "dil",
    "ayrımcılık_nefret": "esitlik",
    "korku_travma": "guvenlik",
    "okültizm_batıl": "milli_manevi",
    "dijital_risk": "bilimsel",
    "olumsuz_davranış": "milli_manevi",
    "reklam_ticari": "reklam"
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
}

def _problemli_bulgulari_al(maarif_data: dict) -> list:
    bulgular = []
    for bulgu in maarif_data.get('bulunan_kelimeler', []):
        risk = bulgu.get('riskPuani', bulgu.get('baglamsal_risk', 0)) or 0
        try:
            risk = float(risk)
        except (TypeError, ValueError):
            risk = 0
        if (
            bulgu.get('problemliMi') is True
            and risk > 0
            and bulgu.get('baglamTipi') in RISK_URETEN_BAGLAMLAR
        ):
            bulgular.append(bulgu)
    return bulgular

def bağla_maarif_bulgularini_meb_kriterlerine(
    meb_degerlendirmesi: dict,
    kategori_bulgulari: dict,
    pdf_text: str = "",
    sayfa_haritasi = None
) -> dict:
    """
    MAARIF kategori bulgularını MEB kriterlerine bağla
    
    Eğer meb_bulgulari boş ama meb_kriterler risk > 0 ise,
    karşılık gelen MAARIF bulgularından MEB bulgularını oluştur.
    
    Parameters:
    - meb_degerlendirmesi: MEB değerlendirmesi dict
    - kategori_bulgulari: MAARIF kategori bulguları dict
    - pdf_text: Metin (sayfa bulma için)
    - sayfa_haritasi: Sayfa mapping
    
    Returns:
    - Güncellenmiş meb_degerlendirmesi
    """
    
    print(f"[BAĞLAMA] Başladı - meb_kriterler keys: {list(meb_degerlendirmesi.get('meb_kriterler', {}).keys())}")
    
    meb_bulgulari = meb_degerlendirmesi.get('meb_bulgulari', {})
    meb_kriterler = meb_degerlendirmesi.get('meb_kriterler', {})

    baglamsal_meb_bulgulari = {}
    for kriter_key, kriter_info in meb_kriterler.items():
        risk = kriter_info.get('risk', 0)
        try:
            risk = float(risk)
        except (TypeError, ValueError):
            risk = 0
        print(f"[BAĞLAMA] {kriter_key}: risk={risk}")
        if risk <= 0:
            continue

        for maarif_cat, meb_mapped_kriter in KATEGORI_TO_MEB_KRITER.items():
            if meb_mapped_kriter != kriter_key or maarif_cat not in kategori_bulgulari:
                continue

            problemli_bulgular = _problemli_bulgulari_al(kategori_bulgulari[maarif_cat])
            if not problemli_bulgular:
                continue

            baglamsal_meb_bulgulari.setdefault(kriter_key, [])
            for bulgu in problemli_bulgular[:5]:
                alinti = bulgu.get('cumle') or bulgu.get('kontext', '')
                baglamsal_meb_bulgulari[kriter_key].append({
                    'alininti': alinti[:300],
                    'sebebi': (
                        f"{bulgu.get('kelime', '')}: {bulgu.get('baglamTipi', '')} "
                        f"bağlamında risk {bulgu.get('riskPuani', bulgu.get('baglamsal_risk', 0))}"
                    ),
                    'sayfa': bulgu.get('sayfa', 0),
                    'risk_puani': bulgu.get('riskPuani', bulgu.get('baglamsal_risk', kriter_info.get('risk', 0))),
                    'onerili_revizyon': bulgu.get('uyariMetni', '')
                })

    meb_degerlendirmesi['meb_bulgulari'] = baglamsal_meb_bulgulari
    return meb_degerlendirmesi
    
    # Her MEB kriter risk > 0 ise kontrol et
    for kriter_key, kriter_info in meb_kriterler.items():
        risk = kriter_info.get('risk', 0)
        print(f"[BAĞLAMA] {kriter_key}: risk={risk}")
        
        if risk > 0:
            # Bu kriter için zaten bulgular var mı?
            existing = meb_bulgulari.get(kriter_key, [])
            print(f"[BAĞLAMA]   {kriter_key} existing bulgular: {len(existing)}")
            
            if kriter_key not in meb_bulgulari or not meb_bulgulari[kriter_key]:
                # Yok - Karşılık gelen MAARIF kategorialını bulup ekle
                for maarif_cat, meb_mapped_kriter in KATEGORI_TO_MEB_KRITER.items():
                    if meb_mapped_kriter == kriter_key:
                        print(f"[BAĞLAMA]   {kriter_key} ← {maarif_cat} harita bulundu")
                        # Bu MAARIF kategorisinde bulgular var mı?
                        if maarif_cat in kategori_bulgulari:
                            maarif_data = kategori_bulgulari[maarif_cat]
                            print(f"[BAĞLAMA]     {maarif_cat} bulundu: {maarif_data.get('bulundu')}, findings: {maarif_data.get('toplam_bulgu')}")
                            # Key: bulunan_kelimeler (not bulunan_bulgular)
                            problemli_bulgular = _problemli_bulgulari_al(maarif_data)
                            if maarif_data.get('bulundu') and problemli_bulgular:
                                # MAARIF bulgularını MEB formatına çevir
                                meb_bulgulari[kriter_key] = []
                                for bulgu in problemli_bulgular[:5]:  # ilk 5
                                    alinti = bulgu.get('cumle') or bulgu.get('kontext', '')
                                    meb_bulgulari[kriter_key].append({
                                        'alininti': alinti[:300],
                                        'sebebi': bulgu.get('kelime', '') + ': Risk ' + str(bulgu.get('baglamsal_risk', 0)),
                                        'sayfa': bulgu.get('sayfa', 0),
                                        'risk_puani': bulgu.get('baglamsal_risk', kriter_info.get('risk', 0))
                                    })
                                print(f"[BAĞLAMA]     → {kriter_key} için {len(meb_bulgulari[kriter_key])} bulgu eklendi")
                                break
    
    # Her MEB kriter risk > 0 ise kontrol et
    for kriter_key, kriter_info in meb_kriterler.items():
        if kriter_info.get('risk', 0) > 0:
            # Bu kriter için zaten bulgular var mı?
            if kriter_key not in meb_bulgulari or not meb_bulgulari[kriter_key]:
                # Yok - Karşılık gelen MAARIF kategorialını bulup ekle
                for maarif_cat, meb_mapped_kriter in KATEGORI_TO_MEB_KRITER.items():
                    if meb_mapped_kriter == kriter_key:
                        # Bu MAARIF kategorisinde bulgular var mı?
                        if maarif_cat in kategori_bulgulari:
                            maarif_data = kategori_bulgulari[maarif_cat]
                            # Key: bulunan_kelimeler (not bulunan_bulgular)
                            problemli_bulgular = _problemli_bulgulari_al(maarif_data)
                            if maarif_data.get('bulundu') and problemli_bulgular:
                                # MAARIF bulgularını MEB formatına çevir
                                meb_bulgulari[kriter_key] = []
                                for bulgu in problemli_bulgular[:5]:  # ilk 5
                                    alinti = bulgu.get('cumle') or bulgu.get('kontext', '')
                                    meb_bulgulari[kriter_key].append({
                                        'alininti': alinti[:300],
                                        'sebebi': bulgu.get('kelime', '') + ': Risk ' + str(bulgu.get('baglamsal_risk', 0)),
                                        'sayfa': bulgu.get('sayfa', 0),
                                        'risk_puani': bulgu.get('baglamsal_risk', kriter_info.get('risk', 0))
                                    })
                                break
    
    meb_degerlendirmesi['meb_bulgulari'] = meb_bulgulari
    return meb_degerlendirmesi
