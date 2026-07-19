"""
Karakter Çıkarımı Debug - Ali, Kız Tavşan Pati, Evin Konukları Bir
Hangi karakterlerin neden nasıl üretildiğini detaylı logla.
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theme_gain_analysis import (
    _extract_character_profiles,
    _page_sentences,
    _normalize_character_identity,
    _is_forbidden_character_name,
    _fold_text,
    _character_context_score,
    _character_action_score,
    _character_direct_speech_score,
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


def debug_character_extraction():
    """Detaylı karakter çıkarımı debug."""
    
    log_file = "character_debug.log"
    with open(log_file, "w", encoding="utf-8") as log:
        log.write(f"{'='*80}\n")
        log.write(f"KARAKTER ÇIKARIMI DEBUG - {datetime.now().isoformat(timespec='seconds')}\n")
        log.write(f"{'='*80}\n\n")
    
    # Stage 1: Sentence extraction
    records = _page_sentences(TEST_TEXT)
    
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"--- STAGE 1: Sentence Extraction ---\n")
        log.write(f"Total records: {len(records)}\n\n")
    
    # Stage 2: Raw character name extraction
    import re
    name_pattern = re.compile(
        r"\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]{2,}(?:\s+(?:Abi|Abla|Bey|Hanım|Öğretmen|Dede|Nine|Amca|Teyze|[A-ZÇĞİÖŞÜ][a-zçğıöşü]{2,})){0,2})\b"
    )
    
    raw_candidates = []
    for record in records:
        text = record.get("metin", "")
        for match in name_pattern.finditer(text):
            raw_name = match.group(1).strip()
            raw_candidates.append({
                "name": raw_name,
                "page": record.get("sayfa"),
                "context": text[:100],
                "folded": _fold_text(raw_name)
            })
    
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"--- STAGE 2: Raw Character Candidates ---\n")
        log.write(f"Total raw candidates: {len(raw_candidates)}\n\n")
        for idx, candidate in enumerate(raw_candidates, 1):
            log.write(f"{idx}. '{candidate['name']}' (folded: '{candidate['folded']}')\n")
            log.write(f"   Page: {candidate['page']}\n")
            log.write(f"   Context: {candidate['context']}\n")
            log.write(f"   In CHARACTER_NOISE_GATE: {candidate['folded'] in CHARACTER_NOISE_GATE}\n")
            log.write(f"   In CHARACTER_LEADING_NOISE: {candidate['folded'] in CHARACTER_LEADING_NOISE}\n")
            log.write(f"   In CANONICAL_CHARACTER_MAP: {candidate['folded'] in CANONICAL_CHARACTER_MAP}\n\n")
    
    # Stage 3: Normalization
    normalized_candidates = []
    for candidate in raw_candidates:
        raw_name = candidate["name"]
        folded = _fold_text(raw_name)
        
        # Check noise gate
        in_noise_gate = folded in CHARACTER_NOISE_GATE
        in_leading_noise = folded in CHARACTER_LEADING_NOISE
        
        # Normalize
        normalized = _normalize_character_identity(raw_name)
        normalized_folded = _fold_text(normalized)
        
        # Check forbidden
        forbidden = _is_forbidden_character_name(normalized)
        
        normalized_candidates.append({
            "original": raw_name,
            "normalized": normalized,
            "folded": folded,
            "normalized_folded": normalized_folded,
            "in_noise_gate": in_noise_gate,
            "in_leading_noise": in_leading_noise,
            "forbidden": forbidden,
            "page": candidate["page"],
            "context": candidate["context"]
        })
    
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n--- STAGE 3: Normalization ---\n\n")
        for idx, candidate in enumerate(normalized_candidates, 1):
            log.write(f"{idx}. Original: '{candidate['original']}'\n")
            log.write(f"   Normalized: '{candidate['normalized']}'\n")
            log.write(f"   Folded: '{candidate['folded']}'\n")
            log.write(f"   Normalized Folded: '{candidate['normalized_folded']}'\n")
            log.write(f"   In Noise Gate: {candidate['in_noise_gate']}\n")
            log.write(f"   In Leading Noise: {candidate['in_leading_noise']}\n")
            log.write(f"   Forbidden: {candidate['forbidden']}\n")
            log.write(f"   Page: {candidate['page']}\n\n")
    
    # Stage 4: Final character profiles
    profiles = _extract_character_profiles(records, limit=10, raw_text=TEST_TEXT, book_title="Tavşan Pati'nin Şaşırtıcı Yolculuğu")
    
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n--- STAGE 4: Final Character Profiles ---\n")
        log.write(f"Total profiles: {len(profiles)}\n\n")
        for idx, profile in enumerate(profiles, 1):
            log.write(f"{idx}. {profile.get('ad', '?')}\n")
            log.write(f"   Role: {profile.get('rolu', '?')}\n")
            log.write(f"   Category: {profile.get('kategori', '?')}\n")
            log.write(f"   Confidence: {profile.get('guven_skoru', 0)}\n")
            log.write(f"   Count: {profile.get('gecis_sayisi', 0)}\n")
            log.write(f"   Pages: {profile.get('sayfa_sayisi', 0)}\n")
            log.write(f"   Ana Karakter: {profile.get('ana_karakter_mi', False)}\n")
            log.write(f"   Context Score: {profile.get('karakter_baglam_skoru', 0)}\n")
            log.write(f"   Action Score: {profile.get('eylem_baglam_skoru', 0)}\n\n")
    
    # Stage 5: Specific analysis for problematic names
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n--- STAGE 5: Problematic Names Analysis ---\n\n")
        
        # Check "Ali"
        ali_folded = "ali"
        log.write(f"'Ali' Analysis:\n")
        log.write(f"  Folded: '{ali_folded}'\n")
        log.write(f"  In CHARACTER_NOISE_GATE: {ali_folded in CHARACTER_NOISE_GATE}\n")
        log.write(f"  In CHARACTER_LEADING_NOISE: {ali_folded in CHARACTER_LEADING_NOISE}\n")
        log.write(f"  In CANONICAL_CHARACTER_MAP: {ali_folded in CANONICAL_CHARACTER_MAP}\n")
        log.write(f"  Is Forbidden: {_is_forbidden_character_name('Ali')}\n\n")
        
        # Check "Kız Tavşan Pati"
        kiz_tavsan = "Kız Tavşan Pati"
        log.write(f"'Kız Tavşan Pati' Analysis:\n")
        log.write(f"  Folded: '{_fold_text(kiz_tavsan)}'\n")
        log.write(f"  In CANONICAL_CHARACTER_MAP: {_fold_text(kiz_tavsan) in CANONICAL_CHARACTER_MAP}\n")
        log.write(f"  Normalized: '{_normalize_character_identity(kiz_tavsan)}'\n\n")
        
        # Check "Evin Konukları Bir"
        evin_konuklari = "Evin Konukları Bir"
        log.write(f"'Evin Konukları Bir' Analysis:\n")
        log.write(f"  Folded: '{_fold_text(evin_konuklari)}'\n")
        log.write(f"  In CANONICAL_CHARACTER_MAP: {_fold_text(evin_konuklari) in CANONICAL_CHARACTER_MAP}\n")
        log.write(f"  Normalized: '{_normalize_character_identity(evin_konuklari)}'\n\n")
    
    print(f"Character debug completed. See {log_file} for details.")
    return profiles


if __name__ == "__main__":
    debug_character_extraction()