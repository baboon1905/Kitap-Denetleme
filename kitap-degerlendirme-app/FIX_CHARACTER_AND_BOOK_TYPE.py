"""
Karakter çıkarımı ve kitap türü algılama sorunlarını düzelt.
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theme_gain_analysis import (
    _extract_character_profiles,
    _page_sentences,
    detect_book_type,
    _normalize,
    CHARACTER_NOISE_GATE,
    CHARACTER_LEADING_NOISE,
    CANONICAL_CHARACTER_MAP,
)

TEST_TEXT = """
--- SAYFA 1 ---
Ali adında bir çocuk vardı. Bir gün pazarda küçük bir tavşan gördü. Tavşan çok tatlıydı ve Ali onu çok sevdi.

--- SAYFA 2 ---
Ali tavşanı eve getirdi ve ona Pati adını verdi. "Ona iyi bakmalıyım," dedi Ali. Bir canlı sahiplenmek sorumluluk gerektirir.

--- SAYFA 3 ---
Ali her gün Pati'yi besledi ve suyunu verdi. Pati'nin tüylerini temizledi ve onunla oynadı. Ali artık Pati'yi çok seviyordu.

--- SAYFA 4 ---
Bir gün Ali okuldan geldiğinde Pati'yi hasta gördü. Ali çok üzüldü ve hemen annesine haber verdi. "Pati hasta, ona yardım etmeliyiz!" dedi.

--- SAYFA 5 ---
Annesi veterineri aradı. Veteriner Pati'yi muayene etti ve ilaç yazdı. Ali pişman oldu çünkü Pati'yi iyi koruyamamıştı.

--- SAYFA 6 ---
Ali her gün Pati'nin ilacını verdi ve onunla ilgilendi. "Verdiğim sözü tutmalıyım," dedi Ali. Pati yavaş yavaş iyileşti.

--- SAYFA 7 ---
Arkadaşı Cemal, Ali'yi bahçede oynamaya çağırdı. Ali önce gitmek istedi ama sonra Pati'yi yalnız bırakmamaya karar verdi.

--- SAYFA 8 ---
"Pati benim emanetim," dedi Ali. Cemal de Pati'yi görmek istedi. Birlikte Pati'yle ilgilendiler ve çok eğlendiler.

--- SAYFA 9 ---
Eve gelen babaannesi Ali'ye "Aferin, çok sorumluluk sahibi bir çocuksun," dedi. Ali çok mutlu oldu.

--- SAYFA 10 ---
Artık Pati tamamen iyileşmişti. Ali, Cemal ve Pati birlikte bahçede oynadılar. Gerçek dostluk böyle bir şeydi işte.

--- SAYFA 11 ---
Ali, Pati'yi sahiplendiği günden beri çok şey öğrenmişti. Hayvan sevgisi, sorumluluk ve dostluk en önemli değerlerdi.

--- SAYFA 12 ---
"Bir canlıya bakmak büyük sorumluluktur," diye düşündü Ali. "Ama aynı zamanda çok güzeldir."

--- SAYFA 13 ---
Eren adında bir arkadaşı Ali'ye "Pati'yi bana verir misin?" diye sordu. Ali "Hayır, o benim sorumluluğum," dedi.

--- SAYFA 14 ---
Annesi Ali'ye sarıldı. "Sen gerçekten büyüdün," dedi. "Bir canlının sorumluluğunu almak ve ona sevgiyle bakmak büyük iştir."

--- SAYFA 15 ---
Ali yatağında uyumadan önce Pati'yi düşündü. "Ona iyi bir dost oldum," diye fısıldadı. İçinde büyük bir vicdan huzuru vardı.
"""

TEST_METADATA = {
    "baslik": "Tavşan Pati'nin Şaşırtıcı Yolculuğu",
    "yazar": "Test Yazar",
    "sayfa_sayisi": 15
}


def debug_and_fix():
    """Karakter çıkarımı ve kitap türü sorunlarını düzelt."""
    
    log_file = "fix_debug.log"
    log = open(log_file, "w", encoding="utf-8")
    try:
        log.write(f"{'='*80}\n")
        log.write(f"FIX DEBUG - {datetime.now().isoformat(timespec='seconds')}\n")
        log.write(f"{'='*80}\n\n")
        
        text = TEST_TEXT
        metadata = TEST_METADATA
        
        # KITAP TÜRÜ KONTROL
        log.write("--- KİTAP TÜRÜ KONTROL ---\n")
        book_type = detect_book_type(text, metadata)
        log.write(f"Başlık: {metadata.get('baslik')}\n")
        log.write(f"Tespit edilen tür: {book_type}\n")
        
        # "Yolculuk" kelimesi kontrol
        folded_text = _normalize(text + " " + metadata.get('baslik', ''))
        log.write(f"'yolculuk' kelimesi metinde var mı: {'yolculuk' in folded_text}\n")
        log.write(f"'macera' kategorisi tetikleniyor mu: {'macera' in folded_text}\n\n")
        
        # KARAKTER ÇIKARIMI KONTROL
        log.write("--- KARAKTER ÇIKARIMI KONTROL ---\n")
        records = _page_sentences(text)
        log.write(f"Toplam sentence records: {len(records)}\n\n")
        
        # Ham isim adaylarını bul
        import re
        name_pattern = re.compile(
            r"\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]{2,}(?:\s+(?:Abi|Abla|Bey|Hanım|Öğretmen|Dede|Nine|Amca|Teyze|[A-ZÇĞİÖŞÜ][a-zçğıöşü]{2,})){0,2})\b"
        )
        
        raw_candidates = {}
        for record in records:
            for match in name_pattern.findall(record.get("metin", "")):
                name = match.strip()
                raw_candidates[name] = raw_candidates.get(name, 0) + 1
        
        log.write("Ham isim adayları:\n")
        for name, count in sorted(raw_candidates.items(), key=lambda x: -x[1]):
            folded = _normalize(name)
            in_noise = folded in CHARACTER_NOISE_GATE
            in_leading = folded in CHARACTER_LEADING_NOISE
            in_canonical = folded in CANONICAL_CHARACTER_MAP
            log.write(f"  {name}: {count} kez, noise={in_noise}, leading={in_leading}, canonical={in_canonical}\n")
        
        log.write("\n")
        
        # Profil çıkar
        profiles = _extract_character_profiles(records, limit=10)
        
        log.write("Çıkarılan karakter profilleri:\n")
        for i, profile in enumerate(profiles, 1):
            log.write(f"{i}. {profile.get('ad')} - {profile.get('rol')}\n")
            log.write(f"   Geçiş: {profile.get('gecis_sayisi')}, Sayfa: {profile.get('sayfa_sayisi')}\n\n")
        
        # ALİ KONTROL
        log.write("--- ALİ KARAKTERİ KONTROL ---\n")
        ali_found = False
        for profile in profiles:
            if _normalize(profile.get('ad', '')) == 'ali':
                ali_found = True
                log.write(f"✅ Ali bulundu: {profile}\n")
                break
        
        if not ali_found:
            log.write("❌ Ali bulunamadı! Nedenini araştırıyoruz...\n")
            
            # Ali'nin ham aday olarak geçip geçmediğini kontrol et
            if 'Ali' in raw_candidates:
                log.write(f"  - Ham aday olarak 'Ali' var, {raw_candidates['Ali']} kez geçiyor\n")
            else:
                log.write(f"  - Ham aday olarak 'Ali' YOK\n")
            
            # Ignored set kontrol
            ignored = {"Sayfa", "Kitap", "Yazar", "Bölüm", "Copyright", "ISBN", "Türkçe", "Çocuk", "Okul", "Anne", "Baba", "Allah", "Türkiye"}
            if 'Ali' in ignored:
                log.write(f"  - 'Ali' ignored set'inde VAR\n")
            else:
                log.write(f"  - 'Ali' ignored set'inde YOK\n")
            
            # Noise gate kontrol
            if 'ali' in CHARACTER_NOISE_GATE:
                log.write(f"  - 'ali' CHARACTER_NOISE_GATE'da VAR\n")
            else:
                log.write(f"  - 'ali' CHARACTER_NOISE_GATE'da YOK\n")
            
            # Leading noise kontrol
            if 'ali' in CHARACTER_LEADING_NOISE:
                log.write(f"  - 'ali' CHARACTER_LEADING_NOISE'da VAR\n")
            else:
                log.write(f"  - 'ali' CHARACTER_LEADING_NOISE'da YOK\n")
        
        # DÜZELTME ÖNERİSİ
        log.write("\n--- DÜZELTME ÖNERİSİ ---\n")
        log.write("1. Kitap türü: 'Yolculuk' kelimesi 'macera' tetikliyor, alt tür 'fantastik macera' yanlış\n")
        log.write("   Çözüm: detect_book_type() fonksiyonunda 'macera' için alt tür kontrolü ekle\n")
        log.write("2. Karakter: Ali bulunamıyor, Pati ve Arkadaşı Cemal bulunuyor\n")
        log.write("   Çözüm: _extract_character_profiles() fonksiyonunda limit veya filtre sorunu var\n")
        
    finally:
        log.close()
    
    print(f"Fix debug completed. See {log_file} for details.")


if __name__ == "__main__":
    debug_and_fix()