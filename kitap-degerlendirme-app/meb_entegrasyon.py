"""
MEB TTK Bulgu Toplama Sistemini Evaluator ile Bağlama
Evaluator sonuçlarına detaylı MEB bulguları ekler
"""

def ekle_meb_bulgularini(meb_degerlendirmesi: dict, pdf_text: str = "", sayfa_haritasi = None) -> dict:
    """
    MEB Degerlendirmesine detaylı MEB bulgularını ekle
    
    Parameters:
    - meb_degerlendirmesi: meb_kriterleri_degerlendirmesi'nden dönen dict
    - pdf_text: Metin (bulguları taramak için)
    - sayfa_haritasi: [(pos_bas, pos_son, sayfa_no), ...]
    
    Returns:
    - Güncellenmiş sonuç (meb_bulgulari eklemiş)
    """
    
    if not pdf_text:
        return meb_degerlendirmesi
    
    metin_lower = pdf_text.lower()
    meb_bulgulari = {}
    
    # ===== 1. ANAYASA VE MEVZUAT =====
    ayristi_belirtiler = [
        ("bolunme", "Devlet bolunme cagrisi", 4),
        ("sinirlar yeniden", "Sinir degistirme cagrisi", 4),
        ("hukuka aykirî", "Hukuka aykirî eylem", 4),
    ]
    
    meb_bulgulari['anayasa'] = _bul_bulgulari(pdf_text, ayristi_belirtiler, sayfa_haritasi)
    
    # ===== 2. MILLI GUVENLIK =====
    teror_belirtiler = [
        ("pkk", "Teror orgutu anması", 5),
        ("dhkp-c", "Teror orgutu anması", 5),
        ("teror orgutu", "Teror orgutu anması", 5),
        ("silah al", "Silah kullanma tanimi", 4),
    ]
    
    meb_bulgulari['milli_guvenlik'] = _bul_bulgulari(pdf_text, teror_belirtiler, sayfa_haritasi)
    
    # ===== 3. ESITLIK VE KAPSAYICILIK =====
    ayrimlilk_belirtiler = [
        ("irkcilik", "Irk ayrimciligî", 5),
        ("nefret söylemi", "Nefret söylemi", 5),
        ("cinsiyetci", "Cinsiyet ayrimciligî", 4),
        ("asagı irk", "Irksai asagilama", 5),
    ]
    
    meb_bulgulari['esitlik'] = _bul_bulgulari(pdf_text, ayrimlilk_belirtiler, sayfa_haritasi)
    
    # ===== 4. MILLI VE MANEVI DEGERLER =====
    deger_belirtiler = [
        ("deger yok", "Deger eksikligi", 2),
        ("aile olmadi", "Aile degeri eksik", 2),
    ]
    
    meb_bulgulari['milli_manevi'] = _bul_bulgulari(pdf_text, deger_belirtiler, sayfa_haritasi)
    
    # ===== 5. GUVENLI VE ETIK ICERIK =====
    siddet_belirtiler = [
        ("kan aktî", "Grafik siddet tasviî", 3),
        ("dene bak", "Eyleme ozendir", 5),
        ("böyle yaparsın", "Suç talimati", 5),
    ]
    
    meb_bulgulari['guvenlik'] = _bul_bulgulari(pdf_text, siddet_belirtiler, sayfa_haritasi)
    
    # ===== 6. BILIMSEL DOGRULUK =====
    bilimsel_belirtiler = [
        ("yanlis", "Bilimsel hata", 2),
        ("hurafe", "Bilim disî icerik", 2),
    ]
    
    meb_bulgulari['bilimsel'] = _bul_bulgulari(pdf_text, bilimsel_belirtiler, sayfa_haritasi)
    
    # ===== 7. REKLAM VE TICARI UNSURLAR =====
    reklam_belirtiler = [
        ("marka", "Marka tanitimi", 2),
        ("satîn al", "Satîn alma cagrisi", 2),
        ("qr kod", "Diş yonlendirme", 1),
    ]
    
    meb_bulgulari['reklam'] = _bul_bulgulari(pdf_text, reklam_belirtiler, sayfa_haritasi)
    
    # ===== 8. DIL VE ANLATIM =====
    dil_belirtiler = [
        ("kufur", "Kufur sözcugu", 5),
        ("argo", "Argo dil", 2),
        ("hakaret", "Hakaret söylemi", 3),
    ]
    
    meb_bulgulari['dil'] = _bul_bulgulari(pdf_text, dil_belirtiler, sayfa_haritasi)
    
    # Temiz kriterlerin detay bulgularini rapora tasima.
    # Ana MEB karari 0/5 ise ham kelime eslesmesi raporda celiski uretmemeli.
    meb_kriterler = meb_degerlendirmesi.get('meb_kriterler', {})
    meb_bulgulari = {
        k: [
            bulgu for bulgu in v
            if bulgu.get('risk_puani', 0) > 0 and meb_kriterler.get(k, {}).get('risk', 0) > 0
        ]
        for k, v in meb_bulgulari.items()
    }
    meb_bulgulari = {k: v for k, v in meb_bulgulari.items() if v}
    
    # Sonuca ekle - meb_bulgulari key'inin altına yazılmalı!
    meb_degerlendirmesi['meb_bulgulari'] = meb_bulgulari
    
    return meb_degerlendirmesi


def _is_word_standalone_meb(metin: str, start_pos: int, end_pos: int) -> bool:
    """
    MEB sistemi için - Kelimenin bağımsız olup olmadığını kontrol et
    Eğer başında/sonunda Türkçe harf varsa False döndür (gömülü kelime)
    """
    # Öncesi kontrol
    if start_pos > 0:
        oncesi = metin[start_pos - 1]
        if oncesi.isalpha():
            return False  # Harf varsa gömülü
    
    # Sonrası kontrol
    if end_pos < len(metin):
        sonrasi = metin[end_pos]
        if sonrasi.isalpha():
            return False  # Harf varsa gömülü
    
    return True  # Bağımsız


def _bul_bulgulari(metin: str, belirtiler: list, sayfa_haritasi=None) -> list:
    """
    Belirtileri ara ve bulguları topla
    
    belirtiler: [(arama_kelimesi, sebebi, risk_puani), ...]
    ⭐ FALSE POSITIVE FİLTRELEME: Gömülü kelimeleri filtrele
    """
    bulgular = []
    metin_lower = metin.lower()
    
    for arama, sebebi, risk in belirtiler:
        arama_lower = arama.lower()
        baslangic = 0
        
        while True:
            pos = metin_lower.find(arama_lower, baslangic)
            if pos == -1:
                break
            
            # ⭐ FALSE POSITIVE KONTROL: Kelime bağımsız mı?
            baslas = pos
            bitisi = pos + len(arama_lower)
            
            # Kelimenin başında/sonunda harf varsa FALSE POSITIVE (gömülü)
            if not _is_word_standalone_meb(metin_lower, baslas, bitisi):
                # FALSE POSITIVE - Geç
                baslangic = pos + 1
                continue
            
            # Etrafindaki 100 karakter al
            bas = max(0, pos - 40)
            son = min(len(metin), pos + 100)
            alinti = "..." + metin[bas:son].strip() + "..."
            
            # Sayfa bul
            sayfa = _bul_sayfa(pos, sayfa_haritasi)
            
            # Duplikat kontrol
            duplikat_var_mi = any(
                b['alininti'] == alinti for b in bulgular
            )
            
            if not duplikat_var_mi:
                bulgular.append({
                    'sayfa': sayfa,
                    'alininti': alinti[:120],  # Max 120 karakter
                    'sebebi': sebebi,
                    'risk_puani': risk,
                    'onerili_revizyon': _onerili_revizyon_bul(sebebi)
                })
            
            baslangic = pos + 1
    
    return bulgular


def _bul_sayfa(pozisyon: int, sayfa_haritasi=None) -> int:
    """Pozisyona göre sayfa numarasini bul"""
    if not sayfa_haritasi:
        return 0
    
    for bas, son, sayfa in sayfa_haritasi:
        if bas <= pozisyon <= son:
            return sayfa
    
    return 0


def _onerili_revizyon_bul(sebebi: str) -> str:
    """Sebebiye göre revizyon öneri hazirla"""
    
    revizyonlar = {
        "teror orgutu": "Bu içerik tamamen silinmelidir",
        "ozendir": "Bu içerik tamamen silinmelidir",
        "bolunme": "Baglam ekleyerek yazini aciklayan notlar ekleyin",
        "irk": "Dili desiştirin, farkliliglara saygi gosteriniz",
        "kufur": "Sözcüğü silin veya resmi dile ceviriniz",
        "grafik": "Şiddet detaylarini cikarin, sonuc odakli yapin",
        "marka": "Marka adini silin, genel referans yapin",
        "bilimsel": "Bilimsel kaynak ekleyiniz",
    }
    
    for anahtar, revizyon in revizyonlar.items():
        if anahtar.lower() in sebebi.lower():
            return revizyon
    
    return "Bu bolumu kontrol edip, gerekirse düzeltin"


# ENTEGRASYON ÖRNEĞİ
if __name__ == "__main__":
    # Evaluator sonucu simule et
    evaluator_sonucu = {
        'meb_puani': 50,
        'meb_karar': 'KOSULLU',
        'meb_kriterler': {
            'anayasa': {'risk': 0},
            'milli_guvenlik': {'risk': 4},
            # ... diğer kriterler
        }
    }
    
    # Test metni
    test_metni = """
    Kitap PKK'nın direniş mücadelesinden bahsediyor. Siz de katılabilirsiniz.
    Kadınlar bilim yapamaz. iPhone en iyi telefondur.
    """
    
    # Entegre et
    sonuc = ekle_meb_bulgularini(evaluator_sonucu, test_metni)
    
    print("MEB Bulguları Eklendi:")
    for kriter, bulgular in sonuc.get('meb_bulgulari', {}).items():
        if bulgular:
            print(f"\n{kriter}: {len(bulgular)} bulgu")
            for bulgu in bulgular:
                print(f"  - {bulgu['sebebi']} (Risk: {bulgu['risk_puani']}/5)")
