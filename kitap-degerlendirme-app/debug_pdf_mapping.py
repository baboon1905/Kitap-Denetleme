"""
PDF Mapping Debug - analyze_theme_gain() çıktısı ile build_pdf_report() girişi arasındaki mapping'i kontrol et.
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theme_gain_analysis import (
    analyze_theme_gain,
    prepare_theme_report_payload,
    build_pdf_report,
    _extract_character_profiles,
    _page_sentences,
    detect_book_type,
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


def debug_pdf_mapping():
    """PDF mapping pipeline'ını logla."""
    
    log_file = "pdf_mapping_debug.log"
    log = open(log_file, "w", encoding="utf-8")
    try:
        log.write(f"{'='*80}\n")
        log.write(f"PDF MAPPING DEBUG - {datetime.now().isoformat(timespec='seconds')}\n")
        log.write(f"{'='*80}\n\n")
        
        text = TEST_TEXT
        metadata = TEST_METADATA
        
        # STAGE 1: analyze_theme_gain() çıktısı
        log.write(f"--- STAGE 1: analyze_theme_gain() OUTPUT ---\n")
        log.flush()
        
        result = analyze_theme_gain(text, metadata, "", "standart")
        
        log.write(f"ana_tema: {result.get('ana_tema')}\n")
        log.write(f"book_type: {result.get('book_type')}\n")
        log.write(f"book_subtype: {result.get('book_subtype')}\n")
        log.write(f"tema_analizi count: {len(result.get('tema_analizi', []))}\n")
        log.write(f"tema_analizi: {[t.get('ad') for t in result.get('tema_analizi', [])]}\n")
        log.write(f"karakter_analizi count: {len(result.get('karakter_analizi', []))}\n")
        log.write(f"karakter_analizi: {[k.get('ad') for k in result.get('karakter_analizi', [])]}\n")
        log.write(f"deger_analizi count: {len(result.get('deger_analizi', []))}\n")
        log.write(f"kazanim_analizi count: {len(result.get('kazanim_analizi', []))}\n\n")
        log.flush()
        
        # STAGE 2: prepare_theme_report_payload() çıktısı
        log.write(f"--- STAGE 2: prepare_theme_report_payload() OUTPUT ---\n")
        log.flush()
        
        prepared = prepare_theme_report_payload(result)
        
        log.write(f"ana_tema: {prepared.get('ana_tema')}\n")
        log.write(f"book_type: {prepared.get('book_type')}\n")
        log.write(f"book_subtype: {prepared.get('book_subtype')}\n")
        log.write(f"tema_analizi count: {len(prepared.get('tema_analizi', []))}\n")
        log.write(f"tema_analizi: {[t.get('ad') for t in prepared.get('tema_analizi', [])]}\n")
        log.write(f"karakter_analizi count: {len(prepared.get('karakter_analizi', []))}\n")
        log.write(f"karakter_analizi: {[k.get('ad') for k in prepared.get('karakter_analizi', [])]}\n")
        log.write(f"ana_karakterler count: {len(prepared.get('ana_karakterler', []))}\n")
        log.write(f"ana_karakterler: {[k.get('ad') for k in prepared.get('ana_karakterler', [])]}\n\n")
        log.flush()
        
        # STAGE 3: build_pdf_report() girişi
        log.write(f"--- STAGE 3: build_pdf_report() INPUT ---\n")
        log.write(f"Input keys: {list(prepared.keys())}\n")
        log.write(f"ana_tema key exists: {'ana_tema' in prepared}\n")
        log.write(f"tema_analizi key exists: {'tema_analizi' in prepared}\n")
        log.write(f"karakter_analizi key exists: {'karakter_analizi' in prepared}\n")
        log.write(f"ana_karakterler key exists: {'ana_karakterler' in prepared}\n")
        log.write(f"book_type key exists: {'book_type' in prepared}\n")
        log.write(f"book_subtype key exists: {'book_subtype' in prepared}\n\n")
        log.flush()
        
        # STAGE 4: PDF oluştur (sadece mapping kontrolü, PDF üretmeden)
        log.write(f"--- STAGE 4: PDF Generation (mapping check) ---\n")
        log.flush()
        
        try:
            # build_pdf_report içindeki ilk kullanımı kontrol et
            # Fonksiyonun başındaki quality_gate kontrolünü geç
            from theme_gain_analysis import rapor_kalite_kapisi
            quality_gate = rapor_kalite_kapisi(prepared)
            log.write(f"Quality gate: {quality_gate.get('durum')}\n")
            log.flush()
            
            # PDF'i oluştur ama içeriğine bakmadan önce mapping'i logla
            log.write(f"Calling build_pdf_report with prepared data...\n")
            log.write(f"prepared['ana_tema'] = {prepared.get('ana_tema')}\n")
            log.write(f"prepared['tema_analizi'] length = {len(prepared.get('tema_analizi', []))}\n")
            log.write(f"prepared['karakter_analizi'] length = {len(prepared.get('karakter_analizi', []))}\n")
            log.write(f"prepared['ana_karakterler'] length = {len(prepared.get('ana_karakterler', []))}\n")
            log.flush()
            
            # PDF üret
            pdf_buffer = build_pdf_report(prepared)
            log.write(f"PDF generated successfully, size: {len(pdf_buffer.getvalue())} bytes\n")
            
        except Exception as e:
            log.write(f"ERROR during PDF generation: {e}\n")
            import traceback
            log.write(traceback.format_exc())
    finally:
        log.close()
    
    print(f"PDF mapping debug completed. See {log_file} for details.")


if __name__ == "__main__":
    debug_pdf_mapping()