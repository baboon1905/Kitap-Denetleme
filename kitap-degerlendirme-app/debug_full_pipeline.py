"""
Full Pipeline Debug - PDF'den çıkarılan verinin tüm aşamalarını logla.
Gerçek PDF pipeline'ının her adımını kaydet.
"""

import os
import sys
import json
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theme_gain_analysis import (
    analyze_theme_gain,
    _page_sentences,
    _extract_character_profiles,
    detect_book_type,
    _normalize,
    _matched_keywords,
    _context_strength,
    _evidence_source_type,
    _semantic_evidence_type,
    _evidence_weight,
    _label_context_valid,
    _pedagogical_evidence_valid,
    _label_evidence_supports_claim,
    _editorial_evidence_valid,
    THEME_KEYWORDS,
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


def debug_full_pipeline():
    """Test metinden çıkarılan verinin tüm pipeline'ını logla."""
    
    log_file = "full_pipeline_debug.log"
    with open(log_file, "w", encoding="utf-8") as log:
        log.write(f"{'='*80}\n")
        log.write(f"FULL PIPELINE DEBUG - {datetime.now().isoformat(timespec='seconds')}\n")
        log.write(f"{'='*80}\n\n")
    
    # Stage 0: Test metni kullan
    text = TEST_TEXT
    metadata = TEST_METADATA
    
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"--- STAGE 0: Text Source ---\n")
        log.write(f"Source: TEST_TEXT (hardcoded)\n")
        log.write(f"Text Length: {len(text)} chars\n")
        log.write(f"Pages: {metadata.get('sayfa_sayisi', '?')}\n")
        log.write(f"Title: {metadata.get('baslik', '?')}\n")
        log.write(f"Author: {metadata.get('yazar', '?')}\n\n")
    
    # Stage 1: Book Type Detection
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"--- STAGE 1: Book Type Detection ---\n")
    
    book_type = detect_book_type(text, metadata)
    
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"Function: theme_gain_analysis.detect_book_type()\n")
        log.write(f"Detected Type: {book_type}\n")
        log.write(f"Metadata Title: {metadata.get('baslik', '')}\n\n")
    
    # Stage 2: Sentence Extraction
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"--- STAGE 2: Sentence Extraction ---\n")
    
    sentence_records = _page_sentences(text)
    
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"Function: theme_gain_analysis._page_sentences()\n")
        log.write(f"Total Records: {len(sentence_records)}\n")
        log.write(f"Sample Records (first 3):\n")
        for i, rec in enumerate(sentence_records[:3], 1):
            log.write(f"  {i}. Page {rec.get('sayfa')}: {rec.get('metin', '')[:80]}...\n")
        log.write("\n")
    
    # Stage 3: Character Extraction
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"--- STAGE 3: Character Extraction ---\n")
    
    character_profiles = _extract_character_profiles(
        sentence_records, 
        limit=20, 
        raw_text=text, 
        book_title=metadata.get('baslik', '')
    )
    
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"Function: theme_gain_analysis._extract_character_profiles()\n")
        log.write(f"Total Profiles: {len(character_profiles)}\n\n")
        log.write("All Character Profiles:\n")
        for idx, profile in enumerate(character_profiles, 1):
            log.write(f"{idx}. {profile.get('ad', '?')}\n")
            log.write(f"   Role: {profile.get('rolu', '?')}\n")
            log.write(f"   Category: {profile.get('kategori', '?')}\n")
            log.write(f"   Confidence: {profile.get('guven_skoru', 0)}\n")
            log.write(f"   Count: {profile.get('gecis_sayisi', 0)}\n")
            log.write(f"   Pages: {profile.get('sayfa_sayisi', 0)}\n")
            log.write(f"   Ana Karakter: {profile.get('ana_karakter_mi', False)}\n")
            log.write(f"   Context Score: {profile.get('karakter_baglam_skoru', 0)}\n")
            log.write(f"   Action Score: {profile.get('eylem_baglam_skoru', 0)}\n\n")
    
    # Stage 4: Theme Extraction (Detailed)
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"--- STAGE 4: Theme Extraction (Detailed) ---\n")
    
    theme_mapping = dict(THEME_KEYWORDS)
    theme_results = {}
    
    for theme_name, keywords in theme_mapping.items():
        matched_records = 0
        evidence_list = []
        rejected_reasons = []
        
        for idx, record in enumerate(sentence_records):
            evidence_type = record.get("kanit_turu") or _evidence_source_type(record.get("metin", ""))
            
            if evidence_type not in {"olay_sahnesi", "anlati_icerigi"}:
                continue
            
            normalized = _normalize(record["metin"])
            matched = _matched_keywords(normalized, keywords)
            
            if not matched:
                continue
            
            matched_records += 1
            context_strength = _context_strength(normalized, matched)
            evidence_weight = _evidence_weight(record["metin"])
            
            # Check all filters
            filter_results = {
                "label_context": _label_context_valid(theme_name, normalized, matched, "tema"),
                "pedagogical": _pedagogical_evidence_valid(theme_name, record["metin"], matched, "tema"),
                "label_claim": _label_evidence_supports_claim(theme_name, record["metin"], "tema"),
                "editorial": _editorial_evidence_valid(theme_name, record["metin"], matched, "tema"),
                "weight": evidence_weight >= 0.4,
                "context": context_strength >= 2,
            }
            
            if all(filter_results.values()):
                evidence_list.append({
                    "page": record.get("sayfa"),
                    "text": record["metin"][:100],
                    "matched": matched,
                    "context_strength": context_strength,
                    "weight": evidence_weight,
                })
            else:
                failed_filters = [k for k, v in filter_results.items() if not v]
                rejected_reasons.append({
                    "page": record.get("sayfa"),
                    "text": record["metin"][:100],
                    "matched": matched,
                    "context_strength": context_strength,
                    "failed_filters": failed_filters,
                })
        
        theme_results[theme_name] = {
            "candidate_count": matched_records,
            "evidence_count": len(evidence_list),
            "rejected_count": len(rejected_reasons),
            "evidence_list": evidence_list,
            "rejected_reasons": rejected_reasons,
        }
    
    with open(log_file, "a", encoding="utf-8") as log:
        log.write("Theme Extraction Results:\n\n")
        
        # Focus on specific themes
        focus_themes = ["hayvan sevgisi", "sorumluluk", "dostluk", "empati", "vicdan", "pişmanlık"]
        
        for theme_name in focus_themes:
            if theme_name not in theme_results:
                continue
            
            result = theme_results[theme_name]
            log.write(f"[THEME] {theme_name}\n")
            log.write(f"  Keywords: {theme_mapping[theme_name]}\n")
            log.write(f"  Candidate Count: {result['candidate_count']}\n")
            log.write(f"  Accepted Evidence: {result['evidence_count']}\n")
            log.write(f"  Rejected Evidence: {result['rejected_count']}\n")
            
            if result['evidence_list']:
                log.write(f"  Accepted Evidence Details:\n")
                for ev in result['evidence_list'][:3]:
                    log.write(f"    - Page {ev['page']}: {ev['text']}...\n")
                    log.write(f"      Matched: {ev['matched']}, Context: {ev['context_strength']}, Weight: {ev['weight']:.2f}\n")
            
            if result['rejected_reasons']:
                log.write(f"  Rejected Evidence Details (first 3):\n")
                for rej in result['rejected_reasons'][:3]:
                    log.write(f"    - Page {rej['page']}: {rej['text']}...\n")
                    log.write(f"      Matched: {rej['matched']}, Context: {rej['context_strength']}\n")
                    log.write(f"      Failed Filters: {rej['failed_filters']}\n")
            
            log.write("\n")
    
    # Stage 5: Full Analysis
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"--- STAGE 5: Full Theme Analysis ---\n")
    
    metadata_full = {
        "kitap_adi": metadata.get("baslik", "Test Kitabı"),
        "yazar": metadata.get("yazar", "Test Yazar"),
        "dosya_adi": "test_metin.txt",
        "dosya_yolu": "",
    }
    
    full_result = analyze_theme_gain(text, metadata_full, "", "standart")
    
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"Function: theme_gain_analysis.analyze_theme_gain()\n")
        log.write(f"Book Type: {full_result.get('book_type')}\n")
        log.write(f"Book Subtype: {full_result.get('book_subtype')}\n")
        log.write(f"Ana Tema: {full_result.get('ana_tema', 'N/A')}\n")
        log.write(f"Tema Analizi: {len(full_result.get('tema_analizi', []))} themes\n")
        log.write(f"Deger Analizi: {len(full_result.get('deger_analizi', []))} values\n")
        log.write(f"Kazanim Analizi: {len(full_result.get('kazanim_analizi', []))} gains\n")
        log.write(f"Karakterler: {len(full_result.get('karakter_analizi', []))} characters\n\n")
        
        log.write("Theme Analysis Details:\n")
        for tema in full_result.get('tema_analizi', []):
            log.write(f"  - {tema.get('ad')}: guc={tema.get('tema_gucu', 0)}, guven={tema.get('guven_skoru', 0):.2f}, kanit={tema.get('kanit_sayisi', 0)}\n")
        
        log.write("\nCharacter Analysis Details:\n")
        for kar in full_result.get('karakter_analizi', []):
            log.write(f"  - {kar.get('ad')}: rol={kar.get('rolu')}, kategori={kar.get('kategori')}, ana={kar.get('ana_karakter_mi')}\n")
    
    # Stage 6: Problematic Names Analysis
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n--- STAGE 6: Problematic Names Analysis ---\n\n")
        
        # Check raw text for problematic patterns
        log.write("Searching for problematic patterns in raw text:\n")
        
        # "Kız Tavşan Pati" pattern
        kiz_tavsan_matches = []
        for match in re.finditer(r'(?i)(kız|tavşan|pati)', text):
            kiz_tavsan_matches.append({
                "match": match.group(),
                "start": match.start(),
                "context": text[max(0, match.start()-50):match.end()+50],
                "page": "?"
            })
        
        log.write(f"'Kız Tavşan Pati' related matches: {len(kiz_tavsan_matches)}\n")
        for m in kiz_tavsan_matches[:5]:
            log.write(f"  - '{m['match']}' at position {m['start']}\n")
            log.write(f"    Context: {m['context'][:100]}...\n\n")
        
        # "Evin Konukları Bir" pattern
        evin_konuklari_matches = []
        for match in re.finditer(r'(?i)(evin|konuk|bir)', text):
            evin_konuklari_matches.append({
                "match": match.group(),
                "start": match.start(),
                "context": text[max(0, match.start()-50):match.end()+50],
                "page": "?"
            })
        
        log.write(f"'Evin Konukları Bir' related matches: {len(evin_konuklari_matches)}\n")
        for m in evin_konuklari_matches[:5]:
            log.write(f"  - '{m['match']}' at position {m['start']}\n")
            log.write(f"    Context: {m['context'][:100]}...\n\n")
    
    print(f"Full pipeline debug completed. See {log_file} for details.")
    return full_result


if __name__ == "__main__":
    debug_full_pipeline()