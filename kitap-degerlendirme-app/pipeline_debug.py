"""
V6.6 Pipeline Debug - Theme Extraction Root Cause Analysis
Her tema adayının hangi aşamada elendiğini logla.
"""

import os
import sys
import json
import re
import traceback
from datetime import datetime

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theme_gain_analysis import (
    analyze_theme_gain, _page_sentences, _evidence_items,
    THEME_KEYWORDS, VALUE_KEYWORDS, GAIN_PATTERNS,
    _normalize, _matched_keywords, _fold_text,
    _context_strength, _evidence_source_type, _semantic_evidence_type,
    _evidence_weight, _label_context_valid, _pedagogical_evidence_valid,
    _label_evidence_supports_claim, _editorial_evidence_valid,
    detect_book_type, _score_item, _apply_theme_weighting,
    _apply_strong_behavior_cap, _apply_cognitive_gain_cap,
    _evidence_reliability_score, _select_representative_evidence,
    PLOT_CONTEXT_TERMS, BEHAVIOR_CONTEXT_TERMS, CHARACTER_CONTEXT_TERMS,
    THEME_CONTEXT_RULES, EVIDENCE_TYPE_WEIGHTS
)


def debug_pipeline(text: str, metadata: dict = None):
    """Run full pipeline with detailed logging for each theme candidate."""
    metadata = metadata or {}
    book_name = metadata.get("kitap_adi") or "unknown"
    
    with open("pipeline_debug.log", "a", encoding="utf-8") as log:
        log.write(f"\n{'='*80}\n")
        log.write(f"V6.6 PIPELINE DEBUG - {datetime.now().isoformat(timespec='seconds')}\n")
        log.write(f"Book: {book_name}\n")
        log.write(f"{'='*80}\n")
    
    # Stage 1: Book Type Detection
    book_type = detect_book_type(text, metadata)
    with open("pipeline_debug.log", "a", encoding="utf-8") as log:
        log.write(f"\n--- STAGE 1: Book Type Detection ---\n")
        log.write(f"Detected: {book_type}\n")
        log.write(f"Expected (metadata): {metadata.get('book_type', 'N/A')}\n")
    
    # Stage 2: Sentence Extraction
    sentence_records = _page_sentences(text)
    total_records = len(sentence_records)
    unique_pages = len({r.get("sayfa") for r in sentence_records if r.get("sayfa")})
    
    with open("pipeline_debug.log", "a", encoding="utf-8") as log:
        log.write(f"\n--- STAGE 2: Sentence Extraction ---\n")
        log.write(f"Total records: {total_records}\n")
        log.write(f"Unique pages: {unique_pages}\n")
        log.write(f"Text length: {len(text)} chars\n")
    
    # Stage 3: Candidate Extraction (for each theme)
    with open("pipeline_debug.log", "a", encoding="utf-8") as log:
        log.write(f"\n--- STAGE 3: Theme Candidate Extraction ---\n")
    
    theme_mapping = dict(THEME_KEYWORDS)
    
    for theme_name, keywords in theme_mapping.items():
        matched_records = 0
        filtered_messages = []
        
        for idx, record in enumerate(sentence_records):
            evidence_type = record.get("kanit_turu") or _evidence_source_type(record.get("metin", ""))
            
            # Filter 1: evidence_type check
            if evidence_type not in {"olay_sahnesi", "anlati_icerigi"}:
                continue
            
            normalized = _normalize(record["metin"])
            matched = _matched_keywords(normalized, keywords)
            
            if not matched:
                continue
            
            matched_records += 1
            context_strength = _context_strength(normalized, matched)
            
            # Filter 2: _label_context_valid
            if not _label_context_valid(theme_name, normalized, matched, "tema"):
                filtered_messages.append(f"  Filter LABEL_CONTEXT: page={record.get('sayfa')} '{record['metin'][:60]}...' matched={matched}")
                continue
            
            # Filter 3: _pedagogical_evidence_valid
            if not _pedagogical_evidence_valid(theme_name, record["metin"], matched, "tema"):
                semantic = _semantic_evidence_type(record["metin"])
                filtered_messages.append(f"  Filter PEDAGOGICAL: page={record.get('sayfa')} semantic={semantic} '{record['metin'][:60]}...'")
                continue
            
            # Filter 4: _label_evidence_supports_claim
            if not _label_evidence_supports_claim(theme_name, record["metin"], "tema"):
                semantic = _semantic_evidence_type(record["metin"])
                filtered_messages.append(f"  Filter LABEL_CLAIM: page={record.get('sayfa')} semantic={semantic} '{record['metin'][:60]}...'")
                continue
            
            # Filter 5: _editorial_evidence_valid
            if not _editorial_evidence_valid(theme_name, record["metin"], matched, "tema"):
                semantic = _fold_text(_semantic_evidence_type(record["metin"]))
                filtered_messages.append(f"  Filter EDITORIAL: page={record.get('sayfa')} semantic={semantic} '{record['metin'][:60]}...'")
                continue
            
            # Filter 6: evidence_weight
            evidence_weight = _evidence_weight(record["metin"])
            if evidence_weight < 0.4:
                semantic = _semantic_evidence_type(record["metin"])
                filtered_messages.append(f"  Filter WEIGHT: page={record.get('sayfa')} weight={evidence_weight:.2f} semantic={semantic} '{record['metin'][:60]}...'")
                continue
            
            # Filter 7: context_strength for themes
            if context_strength < 3:
                filtered_messages.append(f"  Filter CONTEXT: page={record.get('sayfa')} context={context_strength} '{record['metin'][:60]}...' matched={matched}")
                continue
        
        # Log theme results
        with open("pipeline_debug.log", "a", encoding="utf-8") as log:
            log.write(f"\n[THEME] {theme_name}\n")
            log.write(f"  Keywords: {keywords}\n")
            log.write(f"  Matched records: {matched_records}\n")
            log.write(f"  Passed all filters: {sum(1 for m in filtered_messages if 'Filter' not in m)}\n")
            for msg in filtered_messages:
                log.write(f"  {msg}\n")
            if not filtered_messages and matched_records == 0:
                log.write(f"  FILTERED AT: No keyword matches in any record\n")
            elif not filtered_messages:
                log.write(f"  STATUS: PASSED ALL FILTERS\n")
    
    # Stage 4: Run actual analysis
    result = analyze_theme_gain(text, metadata)
    
    with open("pipeline_debug.log", "a", encoding="utf-8") as log:
        log.write(f"\n--- STAGE 4: Final Theme Selection ---\n")
        themes = result.get("tema_analizi", [])
        log.write(f"Total themes found: {len(themes)}\n")
        for t in themes:
            log.write(f"  {t.get('ad', '?')}: guc={t.get('tema_gucu', 0)} guven={t.get('guven_skoru', 0):.2f} kanit={t.get('kanit_sayisi', 0)} sayfa={t.get('farkli_sayfa_sayisi', 0)}\n")
        
        log.write(f"\nAna tema: {result.get('ana_tema', 'N/A')}\n")
        log.write(f"Values: {[v.get('ad') for v in result.get('deger_analizi', [])]}\n")
        log.write(f"Gains: {[g.get('ad') for g in result.get('kazanim_analizi', [])]}\n")
        log.write(f"Book type: {result.get('book_type')}\n")
        log.write(f"Book subtype: {result.get('book_subtype')}\n")
    
    return result


# Test with simulated children's story text
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
    "kitap_adi": "Tavşan Pati'nin Şaşırtıcı Yolculuğu",
    "yazar": "Test Yazar",
}

if __name__ == "__main__":
    result = debug_pipeline(TEST_TEXT, TEST_METADATA)
    print("\n=== RESULTS ===")
    print(f"Ana Tema: {result.get('ana_tema', 'N/A')}")
    print(f"Themes: {[t['ad'] for t in result.get('tema_analizi', [])]}")
    print(f"Values: {[v['ad'] for v in result.get('deger_analizi', [])]}")
    print(f"Gains: {[g['ad'] for g in result.get('kazanim_analizi', [])]}")
    print(f"Book Type: {result.get('book_type')}")
    print(f"\nSee pipeline_debug.log for detailed trace")