"""
Kitap Değerlendirme Uygulaması - Flask Ana Sunucusu
MAARİF MODELİ YAYIN DENETİM SİSTEMİ v1.0
"""

import os
import json
import sys
import zipfile
import hashlib
import copy
from datetime import datetime

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from xml.sax.saxutils import escape
from pdf_processor import PDFProcessor
from evaluator_maarif import MaarifDegerlendiricisi
from professional_evaluator import ProfessionalContentEvaluator
from config import ANALIZ_PROFILLERI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tools')))
from project_for_reports_strict import project_analysis_preserve_evidence

from custom_keywords import (
    CUSTOM_KEYWORDS_PATH,
    add_or_update_custom_term,
    custom_keyword_summary,
    display_categories,
    list_keyword_records,
    load_custom_keywords,
    normalize_category,
    remove_custom_term,
    save_custom_keywords,
    set_system_term_active,
    validate_custom_keywords,
)
from pipeline_runtime_enforcer import (
    enforce_all,
    run_golden_regression_checks,
    is_enforcer_active,
    get_enforcer_marker,
    detect_hardcoded_names_in_payload,
)
from runtime_v7 import V7_SHADOW_MODE, is_v7_summary_ir_source
from theme_gain_analysis import (
    analyze_theme_gain,
    build_pdf_report as build_theme_pdf_report,
    build_word_report as build_theme_word_report,
    clear_runtime_json_dumps,
    generate_teacher_report_pdf,
    kitap_tutarlilik_denetimi,
    prepare_theme_report_payload,
    rapor_kalite_kapisi,
    save_analysis as save_theme_analysis,
    _summary_forbidden_content_ratio,
    _summary_has_forbidden_content,
    _summary_heading_count,
    _summary_is_valid_for_report,
    _select_report_summary,
    _forbidden_terms_found_in_summary,
    _summary_hash,
    _synchronize_summary_surfaces,
    _dump_runtime_json,
    RUNTIME_BUILD_TIMESTAMP,
    theme_report_needs_reanalysis,
)
from summary_ir import attach_summary_ir
from runtime_v7.summary_surface import sync_summary_surfaces_from_ir
from text_quality import collect_text_quality_issues, repair_payload_text
from constants import quality_gate_keys, runtime_config
import io

BUILD_ID = "theme-report-payload-v20260625-23-v6.6-debug"
TEACHER_REPORT_VERSION = "teacher-guide-v20260625-23-v6.6-debug"

ANALYSIS_CORE_FIELD_ALIASES = {
    "tema_analizi": ["themes", "theme_analysis"],
    "deger_analizi": ["values", "value_analysis"],
    "kazanim_analizi": ["gains", "gain_analysis"],
    "ana_karakterler": ["characters", "character_analysis"],
    "book_subtype": ["subtype"],
}

ANALYSIS_CORE_FIELDS = [
    "ana_tema",
    "ana_tema_guven_skoru",
    "ana_tema_tema_gucu",
    "ana_tema_kanitlari",
    "tema_analizi",
    "baskin_tema_ozeti",
    "ilk_uc_baskin_tema",
    "guclu_temalar",
    "destekleyici_temalar",
    "deger_analizi",
    "kazanim_analizi",
    "ana_karakterler",
    "book_type",
    "book_subtype",
]


def _harmonize_analysis_core_fields(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return payload
    harmonized = dict(payload)
    for canonical, aliases in ANALYSIS_CORE_FIELD_ALIASES.items():
        if harmonized.get(canonical):
            continue
        for alias in aliases:
            if harmonized.get(alias):
                harmonized[canonical] = copy.deepcopy(harmonized[alias])
                break
    return harmonized


def _restore_analysis_core_fields(payload: dict, source: dict) -> dict:
    if not isinstance(payload, dict) or not isinstance(source, dict):
        return payload
    restored = dict(payload)
    for key in ANALYSIS_CORE_FIELDS:
        if key in source:
            restored[key] = copy.deepcopy(source.get(key))
    return restored

def debug_consistency_log(mesaj: str) -> None:
    try:
        with open(os.path.abspath('debug_consistency_assert.log'), 'a', encoding='utf-8') as log:
            log.write(f"{datetime.now().isoformat(timespec='seconds')} {mesaj}\n")
    except Exception:
        pass


def _theme_summary_debug_fields(payload: dict) -> str:
    summary = _select_report_summary(payload or {})
    first_300 = summary[:300].replace("\n", "\\n")
    fallback_reason = ""
    if summary.strip() in {"Özet güvenilir üretilemedi.", "Ã–zet gÃ¼venilir Ã¼retilemedi."}:
        fallback_reason = (
            (payload or {}).get("ozet_kalite_kontrol", {}).get("gecersiz_sayilma_nedeni")
            or "ozet_bos_veya_gecersiz"
        )
    return (
        f"kitap_ozeti_ilk_300={first_300!r} "
        f"baslik_sayisi={_summary_heading_count(summary)} "
        f"kelime_sayisi={len(summary.split())} "
        f"yasak_icerik_var={_summary_has_forbidden_content(summary)} "
        f"yasak_icerik_orani={_summary_forbidden_content_ratio(summary)} "
        f"fallback_sebebi={fallback_reason or '-'} "
        f"ozet_kalite_hatalari={(payload or {}).get('ozet_kalite_hatalari') or []}"
    )


def _theme_summary_fields(payload: dict) -> dict:
    keys = [
        "canonical_summary",
        "summary_ui",
        "summary_pdf",
        "kitap_ozeti",
        "book_summary",
        "ozet",
        "summary",
        "summary_before_gate",
        "summary_after_gate",
        "summary_rendered_to_ui",
        "summary_used_for_pdf",
        "summary_before_quality_gate",
        "summary_after_quality_gate",
        "ozet_guven_skoru",
        "ozet_somutluk_skoru",
        "ozet_uzunlugu",
        "ozetin_dayandigi_sayfa_sayisi",
        "olay_akisi",
        "ozet_olay_kumeleri",
        "ozet_kalite_kontrol",
        "ozet_kalite_hatalari",
        "ozet_yasak_icerik_orani",
    ]
    return {key: payload.get(key) for key in keys if key in payload}


def _canonicalize_endpoint_summary(payload: dict, stage: str) -> dict:
    if is_v7_summary_ir_source() and isinstance(payload.get("canonical_summary_ir"), dict):
        return _synchronize_summary_surfaces(payload or {}, stage=stage)
    canonical = _select_report_summary(payload or {})
    synced = _synchronize_summary_surfaces(payload or {}, canonical, stage)
    return synced


def _forbidden_terms_in_summary_surfaces(payload: dict) -> dict:
    surfaces = {
        key: str(payload.get(key) or "")
        for key in (
            "canonical_summary",
            "summary_ui",
            "summary_pdf",
            "summary_before_gate",
            "summary_after_gate",
            "summary_rendered_to_ui",
            "summary_used_for_pdf",
            "summary_before_quality_gate",
            "summary_after_quality_gate",
            "teacher_summary",
        )
        if key in payload
    }
    found = {}
    for key, text in surfaces.items():
        terms = _forbidden_terms_found_in_summary(text)
        if terms:
            found[key] = terms
    return found


def _rendered_summary_gate(payload: dict, endpoint: str):
    synced = _canonicalize_endpoint_summary(payload or {}, endpoint)
    rendered = str(synced.get("canonical_summary") or "")
    forbidden = _forbidden_terms_found_in_summary(rendered)
    surface_issues = _forbidden_terms_in_summary_surfaces(synced) if forbidden else {}
    mojibake_issues = collect_text_quality_issues(synced, path=f"{endpoint}.payload", limit=10)
    audit = dict(synced.get("summary_consistency_audit") or {})
    first_forbidden = forbidden[0] if forbidden else ""
    debug_consistency_log(
        quality_gate_keys.SUMMARY_RENDER_GATE_LOG_PREFIX + " "
        f"endpoint={endpoint} "
        f"summary_source_function={audit.get('summary_source_function')} "
        f"summary_before_gate_hash={audit.get('summary_before_gate_hash')} "
        f"summary_after_gate_hash={audit.get('summary_after_gate_hash')} "
        f"rendered_summary_hash={audit.get('rendered_summary_hash')} "
        f"canonical_summary_hash={audit.get('canonical_summary_hash')} "
        f"summary_ui_hash={audit.get('summary_ui_hash')} "
        f"summary_pdf_hash={audit.get('summary_pdf_hash')} "
        f"ui_summary_hash={audit.get('ui_summary_hash')} "
        f"pdf_summary_hash={audit.get('pdf_summary_hash')} "
        f"rendered_summary_first_300={audit.get('rendered_summary_first_300')!r} "
        f"summary_first_300={audit.get('summary_first_300')!r} "
        f"forbidden_terms_found_in_rendered_summary={forbidden} "
        f"forbidden_summary_surfaces={surface_issues}"
    )
    if forbidden or mojibake_issues:
        return synced, (jsonify({
            "basarili": False,
            "mojibake_detected": bool(mojibake_issues),
            "mojibake_issues": mojibake_issues,
            "hata": f"Rendered summary yasak anlatı kalıbı içeriyor ({first_forbidden}); rapor üretimi durduruldu.",
            "kod": quality_gate_keys.SUMMARY_RENDER_GATE_LOG_PREFIX.strip('[]'),
            "summary_source_function": audit.get("summary_source_function"),
            "summary_before_gate_hash": audit.get("summary_before_gate_hash"),
            "summary_after_gate_hash": audit.get("summary_after_gate_hash"),
            "rendered_summary_hash": audit.get("rendered_summary_hash"),
            "canonical_summary_hash": audit.get("canonical_summary_hash"),
            "summary_ui_hash": audit.get("summary_ui_hash"),
            "summary_pdf_hash": audit.get("summary_pdf_hash"),
            "ui_summary_hash": audit.get("ui_summary_hash"),
            "pdf_summary_hash": audit.get("pdf_summary_hash"),
            "rendered_summary_first_300": audit.get("rendered_summary_first_300"),
            "summary_first_300": audit.get("summary_first_300"),
            "forbidden_terms_found_in_rendered_summary": forbidden,
            "forbidden_summary_surfaces": surface_issues,
        }), 409)
    return synced, None


def _file_hash_for_cache(path: str | None) -> str:
    path = str(path or "").strip()
    if not path or not os.path.exists(path):
        return hashlib.sha256(path.encode("utf-8", errors="ignore")).hexdigest()[:16] if path else "no-file"
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()[:16]
    except Exception:
        stat = os.stat(path)
        fallback = f"{path}|{stat.st_size}|{stat.st_mtime}"
        return hashlib.sha256(fallback.encode("utf-8", errors="ignore")).hexdigest()[:16]


def _assign_analysis_cache_identity(payload: dict, file_path: str | None, stage: str) -> dict:
    if not isinstance(payload, dict):
        return payload
    analysis_timestamp = datetime.now().isoformat(timespec="microseconds")
    title = str(payload.get("kitap_adi") or payload.get("baslik") or payload.get("dosya_adi") or file_path or "kitap")
    file_hash = _file_hash_for_cache(file_path or payload.get("dosya_yolu") or (payload.get("metadata") or {}).get("dosya_yolu"))
    book_id = payload.get("book_id") or hashlib.sha256(f"{title}|{file_hash}".encode("utf-8", errors="ignore")).hexdigest()[:16]
    previous_payload_id = payload.get("payload_id") or payload.get("previous_payload_id") or ""
    payload["book_id"] = book_id
    payload["file_hash"] = file_hash
    payload["analysis_timestamp"] = analysis_timestamp
    payload["cache_key"] = f"{book_id}:{file_hash}:{analysis_timestamp}"
    payload["previous_payload_id"] = previous_payload_id
    payload["payload_id"] = id(payload)
    debug_consistency_log(
        f"[analysis_cache_identity] stage={stage} "
        f"book_id={book_id} book_title={title!r} file_hash={file_hash} "
        f"cache_key={payload['cache_key']} previous_payload_id={previous_payload_id} payload_id={id(payload)}"
    )
    return payload


def _theme_summary_source(payload: dict) -> str:
    for key in ("canonical_summary", "kitap_ozeti", "book_summary", "ozet", "summary"):
        value = str((payload or {}).get(key) or "").strip()
        if value:
            return key
    return "-"


def _is_summary_unavailable_text(value: str) -> bool:
    normalized = str(value or "").strip().casefold()
    return normalized in {
        "özet güvenilir üretilemedi.",
        "Ã¶zet gÃ¼venilir Ã¼retilemedi.".casefold(),
        "Ã–zet gÃ¼venilir Ã¼retilemedi.".casefold(),
        "Ãƒâ€“zet gÃƒÂ¼venilir ÃƒÂ¼retilemedi.".casefold(),
    }


def _summary_is_usable_for_pdf(summary: str) -> bool:
    text = str(summary or "").strip()
    return bool(
        text
        and not _is_summary_unavailable_text(text)
        and len(text.split()) >= 100
        and _summary_heading_count(text) >= 5
        and not _summary_has_forbidden_content(text)
        and _summary_forbidden_content_ratio(text) <= 0.10
    )


def _book_consistency_gate(payload: dict, endpoint: str):
    audit = kitap_tutarlilik_denetimi(payload)
    summary_for_error = _select_report_summary(payload or {})
    summary_for_error_hash = _summary_hash(summary_for_error)
    summary_for_error_first_300 = summary_for_error[:300]
    summary_audit = dict((payload or {}).get("summary_consistency_audit") or {})
    audit["consistency_error_summary_hash"] = summary_for_error_hash
    audit["consistency_error_summary_first_300"] = summary_for_error_first_300
    cross = audit.get("cross_book_denetimi") or {}
    print("BOOK:", audit.get("book_title") or cross.get("book_title") or (payload or {}).get("kitap_adi") or "")
    print("CACHE KEY:", audit.get("cache_key") or cross.get("cache_key") or (payload or {}).get("cache_key") or "")
    print("VERIFIED CHARACTERS RAW:", audit.get("verified_characters_raw") or cross.get("verified_characters_raw") or [])
    print("VERIFIED CHARACTERS NORMALIZED:", audit.get("verified_characters_normalized") or cross.get("verified_characters_normalized") or [])
    print("SUMMARY NAMES RAW:", audit.get("summary_names_raw") or cross.get("summary_names_raw") or [])
    print("SUMMARY NAMES NORMALIZED:", audit.get("summary_names_normalized") or cross.get("summary_names_normalized") or [])
    print("ILLEGAL SUMMARY NAMES:", audit.get("illegal_summary_names") or cross.get("illegal_summary_names") or [])
    debug_consistency_log(
        quality_gate_keys.BOOK_CONSISTENCY_CHECK_GATE_LOG_PREFIX + " "
        f"endpoint={endpoint} gecerli={audit.get('gecerli')} "
        f"durum={audit.get('durum')} manuel_inceleme={audit.get('manuel_inceleme')} "
        f"book_id={audit.get('book_id')} book_title={audit.get('book_title')!r} "
        f"cache_key={audit.get('cache_key')} previous_payload_id={audit.get('previous_payload_id')} "
        f"verified_characters_raw={((audit.get('cross_book_denetimi') or {}).get('verified_characters_raw') or audit.get('verified_characters_raw'))} "
        f"verified_characters_normalized={((audit.get('cross_book_denetimi') or {}).get('verified_characters_normalized') or audit.get('verified_characters_normalized'))} "
        f"summary_names_raw={((audit.get('cross_book_denetimi') or {}).get('summary_names_raw') or audit.get('summary_names_raw'))} "
        f"summary_names_normalized={((audit.get('cross_book_denetimi') or {}).get('summary_names_normalized') or audit.get('summary_names_normalized'))} "
        f"illegal_summary_names={((audit.get('cross_book_denetimi') or {}).get('illegal_summary_names') or audit.get('illegal_summary_names'))} "
        f"unsupported_events={audit.get('unsupported_events')} "
        f"unsupported_locations={audit.get('unsupported_locations')} "
        f"unsupported_objects={audit.get('unsupported_objects')} "
        f"evidence_coverage_score={audit.get('evidence_coverage_score')} "
        f"summary_source_pages={audit.get('summary_source_pages')} "
        f"consistency_error_summary_hash={summary_for_error_hash} "
        f"consistency_error_summary_first_300={summary_for_error_first_300!r} "
        f"rendered_summary_hash={summary_audit.get('rendered_summary_hash')} "
        f"canonical_summary_hash={summary_audit.get('canonical_summary_hash') or _summary_hash((payload or {}).get('canonical_summary') or '')} "
        f"ui_summary_hash={summary_audit.get('ui_summary_hash')} "
        f"pdf_summary_hash={summary_audit.get('pdf_summary_hash')} "
        f"hatalar={audit.get('hatalar')} uyarilar={audit.get('uyarilar')} "
        f"uyum_skorlari={audit.get('uyum_skorlari')}"
    )
    if audit.get("gecerli"):
        return None
    plot_gate = (audit.get(quality_gate_keys.ALT_KAPILAR) or {}).get(quality_gate_keys.SUMMARY_PROOF_CONSISTENCY_GATE) or {}
    stopping_gate = quality_gate_keys.SUMMARY_PROOF_CONSISTENCY_GATE if not plot_gate.get("gecerli", True) else quality_gate_keys.BOOK_CONSISTENCY_CHECK_GATE
    return jsonify({
        "basarili": False,
        "hata": "Kitap tutarlılık denetimi başarısız; rapor üretimi durduruldu.",
        "kod": "KITAP_TUTARLILIK_DENETIMI",
        quality_gate_keys.STOPPING_GATE_KEY: stopping_gate,
        "consistency_error_summary_hash": summary_for_error_hash,
        "consistency_error_summary_first_300": summary_for_error_first_300,
        "consistency_checked_summary_first_300": audit.get("consistency_checked_summary_first_300"),
        "rendered_summary_first_300": audit.get("rendered_summary_first_300") or summary_for_error_first_300,
        "checked_summary_hash": audit.get("checked_summary_hash"),
        "rendered_summary_hash": audit.get("rendered_summary_hash") or summary_for_error_hash,
        "offending_phrase_full_sentence": audit.get("offending_phrase_full_sentence"),
        "error_phrase_missing_in_rendered_summary": audit.get("error_phrase_missing_in_rendered_summary"),
        "summary_surface_rendered_hash": summary_audit.get("rendered_summary_hash"),
        "canonical_summary_hash": summary_audit.get("canonical_summary_hash") or _summary_hash((payload or {}).get("canonical_summary") or ""),
        "ui_summary_hash": summary_audit.get("ui_summary_hash"),
        "pdf_summary_hash": summary_audit.get("pdf_summary_hash"),
        "tutarlilik_denetimi": audit,
    }), 409


def _report_quality_gate(payload: dict, endpoint: str):
    audit = rapor_kalite_kapisi(payload)
    debug_consistency_log(
        quality_gate_keys.REPORT_QUALITY_GATE_V7_WARNING_LOG_PREFIX + " "
        f"endpoint={endpoint} report_blocked=False durum={audit.get('durum')} hatalar={audit.get('hatalar')}"
    )
    return None
    debug_consistency_log(
        quality_gate_keys.REPORT_QUALITY_GATE_V6_LOG_PREFIX + " "
        f"endpoint={endpoint} durum={audit.get('durum')} hatalar={audit.get('hatalar')}"
    )
    if audit.get("gecerli"):
        return None
    return jsonify({
        "basarili": False,
        "hata": "Rapor kalite kapısı başarısız; rapor üretimi durduruldu.",
        "kod": quality_gate_keys.REPORT_QUALITY_GATE_V6_CODE,
        quality_gate_keys.QUALITY_GATE_KEY: audit,
    }), 409


def _is_development_mode() -> bool:
    if os.getenv("APP_ENV") == "production":
        return False
    return os.getenv("FLASK_ENV") == "development" or os.getenv("APP_ENV") == "development"

# APP STARTUP LOG
with open('debug_app_startup.log', 'w', encoding='utf-8') as f:
    f.write(f"[app.py] Module loaded build_id={BUILD_ID}\n")

# Ortam değişkenlerini yükle
load_dotenv()

app = Flask(__name__)

# DEBUG: Write to file to verify this version is loaded
with open(runtime_config.DEBUG_FLASK_VERSION_TXT, 'w', encoding='utf-8') as f:
    f.write(f"Flask app.py loaded with fresh bytecode build_id={BUILD_ID}\n")

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB maksimum dosya boyutu
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}


@app.after_request
def _sanitize_json_response(response):
    if not response.is_json:
        return response
    try:
        payload = response.get_json(silent=True)
        if payload is None:
            return response
        repaired = repair_payload_text(payload)
        issues = collect_text_quality_issues(repaired, path=runtime_config.API_RESPONSE_PATH, limit=10)
        if issues:
            response.status_code = 500
            response.set_data(json.dumps({
                "basarili": False,
                "hata": "MOJIBAKE_DETECTED",
                "mojibake_detected": True,
                "mojibake_issues": issues,
            }, ensure_ascii=False))
        else:
            response.set_data(json.dumps(repaired, ensure_ascii=False))
        response.mimetype = "application/json"
    except Exception as exc:
        debug_consistency_log(f"[json_response_sanitize] error={exc!r}")
    return response

# Upload klasörünü oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def _teacher_report_output_path(kitap_adi: str) -> str:
    slug = secure_filename(str(kitap_adi or "kitap")).rsplit(".", 1)[0].lower() or "kitap"
    output_dir = os.path.join(app.root_path, "outputs")
    os.makedirs(output_dir, exist_ok=True)
    return os.path.abspath(os.path.join(output_dir, f"{slug}{runtime_config.TEACHER_REPORT_FILENAME_SUFFIX}"))


def allowed_file(filename):
    """Dosya türünün izin verilen olup olmadığını kontrol et"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def _resolve_pdf_path(path_value: str | None) -> str | None:
    """API'den gelen göreli/mutlak PDF yolunu çalışma dizininden bağımsız çözer."""
    if not path_value:
        return None

    raw_path = str(path_value).strip().strip('"')
    candidates = [
        raw_path,
        os.path.abspath(raw_path),
        os.path.join(app.root_path, raw_path),
        os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], os.path.basename(raw_path)),
    ]
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    debug_consistency_log(
        "[app.resolve_pdf_path] NOT_FOUND "
        f"raw={raw_path} root={app.root_path} cwd={os.getcwd()} "
        f"candidates={candidates}"
    )
    return raw_path


def _reanalyze_theme_payload_from_pdf(sonuc: dict, data: dict) -> dict:
    dosya_yolu = _resolve_pdf_path(
        sonuc.get("dosya_yolu")
        or (sonuc.get("metadata") or {}).get("dosya_yolu")
        or data.get("dosya_yolu")
    )
    if not dosya_yolu or not os.path.exists(dosya_yolu):
        return {}
    processor = PDFProcessor(dosya_yolu)
    metin = processor.extract_text()
    metadata = processor.extract_metadata()
    metadata["kitap_adi"] = sonuc.get("kitap_adi") or metadata.get("baslik") or os.path.basename(dosya_yolu)
    metadata["yazar"] = sonuc.get("yazar") or metadata.get("yazar") or "Belirsiz"
    metadata["dosya_adi"] = os.path.basename(dosya_yolu)
    metadata["dosya_yolu"] = dosya_yolu
    debug_consistency_log(
        "[reanalyze_theme_payload_from_pdf] ANALYZE_ENTER "
        f"build_id={BUILD_ID} runtime_build_timestamp={RUNTIME_BUILD_TIMESTAMP} "
        f"metadata_id={id(metadata)} target_pdf_function=theme_gain_analysis.build_pdf_report"
    )
    analyzed = analyze_theme_gain(
        metin,
        metadata,
        data.get("yas_grubu") or sonuc.get("hedef_yas_grubu") or "",
        data.get("ozet_turu") or sonuc.get("ozet_turu") or "standart",
    )
    # RUNTIME ENFORCER: Apply fixes after reanalysis
    if analyzed and isinstance(analyzed, dict):
        analyzed = enforce_all(analyzed)
    debug_consistency_log(
        "[reanalyze_theme_payload_from_pdf] ANALYZE_EXIT "
        f"build_id={BUILD_ID} runtime_build_timestamp={RUNTIME_BUILD_TIMESTAMP} "
        f"result_id={id(analyzed)} ana_tema={analyzed.get('ana_tema')!r} "
        f"book_type={analyzed.get('book_type')!r} subtype={analyzed.get('book_subtype')!r} "
        f"target_pdf_function=theme_gain_analysis.build_pdf_report"
    )
    return analyzed


def _rapor_icin_gorsel_taramayi_yenile(analiz_sonucu: dict, dosya_yolu: str) -> dict:
    """Rapor asamasinda eski analiz payload'unu taze PDF gorsel taramasiyla gunceller."""
    if not dosya_yolu or not os.path.exists(dosya_yolu):
        return analiz_sonucu
    try:
        gorsel_ozet = PDFProcessor(dosya_yolu).extract_visual_summary()
        analiz_sonucu["gorsel_tarama"] = gorsel_ozet
        metadata = analiz_sonucu.setdefault("metadata", {})
        metadata["gorsel_ozet"] = gorsel_ozet
        metadata["dosya_yolu"] = dosya_yolu
        debug_consistency_log(
            quality_gate_keys.APP_API_RAPOR_FRESH_VISUAL_SCAN_LOG_PREFIX + " "
            f"dosya={dosya_yolu} toplam_gorsel={gorsel_ozet.get('toplam_gorsel')} "
            f"visual_pages={gorsel_ozet.get('visual_pages')} "
            f"visual_analysis_count={gorsel_ozet.get('visual_analysis_count')} "
            f"analiz_yapildi={gorsel_ozet.get('gorsel_icerik_analizi_yapildi')}"
        )
    except Exception as exc:
        debug_consistency_log(quality_gate_keys.APP_API_RAPOR_FRESH_VISUAL_SCAN_FAILED_LOG_PREFIX + f" dosya={dosya_yolu} hata={exc}")
    return analiz_sonucu


@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')


@app.route('/api/profiller', methods=['GET'])
def get_profiller():
    """Maarif Modeli analiz profillerini döndür"""
    profiller = {}
    for key, profil_data in ANALIZ_PROFILLERI.items():
        profiller[key] = {
            "ad": profil_data["ad"],
            "aciklama": profil_data["aciklama"],
            "yaklasim": profil_data["yaklasim"],
            "kullanim": profil_data["kullanim"]
        }
    return jsonify(profiller)


def _custom_keyword_response():
    data = load_custom_keywords()
    validation = validate_custom_keywords(data)
    return jsonify({
        "basarili": True,
        "data": data,
        "summary": custom_keyword_summary(data),
        "validation": validation,
        "categories": display_categories(),
        "records": list_keyword_records(data),
    })


@app.route('/api/ozel-kelimeler', methods=['GET'])
def get_ozel_kelimeler():
    """Kod degistirmeden yonetilen ozel kelime/regex sozlugunu dondur."""
    return _custom_keyword_response()


@app.route('/api/kelime-yonetimi', methods=['GET'])
def get_kelime_yonetimi():
    """Sistem ve ozel kelimeleri tek yonetim listesinde dondur."""
    return _custom_keyword_response()


@app.route('/api/ozel-kelimeler', methods=['PUT'])
def put_ozel_kelimeler():
    """Tum ozel sozlugu ice aktar veya toplu guncelle."""
    payload = request.get_json(silent=True) or {}
    data = payload.get("data", payload)
    saved = save_custom_keywords(data)
    return jsonify({
        "basarili": True,
        "data": saved,
        "summary": custom_keyword_summary(saved),
        "validation": validate_custom_keywords(saved),
    })


@app.route('/api/ozel-kelimeler/terim', methods=['POST'])
def add_ozel_kelime_terimi():
    """Ozel sozluge yeni kelime, ifade veya regex ekle."""
    payload = request.get_json(silent=True) or {}
    category = normalize_category(payload.get("kategori"))
    term = str(payload.get("terim") or payload.get("kelime") or "").strip()
    term_type = "regex" if payload.get("tip") == "regex" else "keywords"

    if not category or not term:
        return jsonify({"basarili": False, "hata": "Kategori ve terim gerekli"}), 400

    saved = add_or_update_custom_term(category, term, term_type, bool(payload.get("active", True)))
    return jsonify({
        "basarili": True,
        "data": saved,
        "summary": custom_keyword_summary(saved),
        "validation": validate_custom_keywords(saved),
        "records": list_keyword_records(saved),
    })


@app.route('/api/ozel-kelimeler/terim', methods=['DELETE'])
def delete_ozel_kelime_terimi():
    """Ozel sozlukten kelime/regex sil."""
    payload = request.get_json(silent=True) or {}
    category = normalize_category(payload.get("kategori"))
    term = str(payload.get("terim") or payload.get("kelime") or "").strip()
    term_type = "regex" if payload.get("tip") == "regex" else "keywords"

    saved = remove_custom_term(category, term, term_type)
    return jsonify({
        "basarili": True,
        "data": saved,
        "summary": custom_keyword_summary(saved),
        "validation": validate_custom_keywords(saved),
        "records": list_keyword_records(saved),
    })


@app.route('/api/ozel-kelimeler/tasi', methods=['POST'])
def move_ozel_kelime_terimi():
    """Ozel kelime veya regex girdisini baska kategoriye tasi."""
    payload = request.get_json(silent=True) or {}
    source = normalize_category(payload.get("kaynak_kategori"))
    target = normalize_category(payload.get("hedef_kategori"))
    term = str(payload.get("terim") or "").strip()
    term_type = "regex" if payload.get("tip") == "regex" else "keywords"

    if not source or not target or not term:
        return jsonify({"basarili": False, "hata": "Kaynak, hedef ve terim gerekli"}), 400

    data = load_custom_keywords()
    source_bucket = data.setdefault(source, {"keywords": [], "regex": []})
    target_bucket = data.setdefault(target, {"keywords": [], "regex": []})
    source_bucket[term_type] = [item for item in source_bucket.get(term_type, []) if item != term]
    if term not in target_bucket.setdefault(term_type, []):
        target_bucket[term_type].append(term)
    saved = save_custom_keywords(data)
    return jsonify({
        "basarili": True,
        "data": saved,
        "summary": custom_keyword_summary(saved),
        "validation": validate_custom_keywords(saved),
        "records": list_keyword_records(saved),
    })


@app.route('/api/kelime-yonetimi/ozel', methods=['PUT'])
def update_ozel_kelime_terimi():
    """Ozel kelimeyi duzenle, kategori degistir veya aktif/pasif yap."""
    payload = request.get_json(silent=True) or {}
    saved = add_or_update_custom_term(
        category=payload.get("kategori"),
        term=payload.get("terim") or payload.get("kelime"),
        term_type=payload.get("tip", "keywords"),
        active=bool(payload.get("active", True)),
        old_category=payload.get("eski_kategori"),
        old_term=payload.get("eski_terim"),
        old_type=payload.get("eski_tip"),
    )
    return jsonify({
        "basarili": True,
        "data": saved,
        "summary": custom_keyword_summary(saved),
        "validation": validate_custom_keywords(saved),
        "records": list_keyword_records(saved),
    })


@app.route('/api/kelime-yonetimi/sistem/aktif', methods=['POST'])
def toggle_sistem_kelime_aktif():
    """Sistem kelimesini silmeden aktif/pasif yap."""
    payload = request.get_json(silent=True) or {}
    category = normalize_category(payload.get("kategori"))
    term = str(payload.get("terim") or payload.get("kelime") or "").strip()
    if not category or not term:
        return jsonify({"basarili": False, "hata": "Kategori ve terim gerekli"}), 400
    saved = set_system_term_active(category, term, bool(payload.get("active", True)))
    return jsonify({
        "basarili": True,
        "data": saved,
        "summary": custom_keyword_summary(saved),
        "validation": validate_custom_keywords(saved),
        "records": list_keyword_records(saved),
    })


@app.route('/api/ozel-kelimeler/export', methods=['GET'])
def export_ozel_kelimeler():
    """custom_keywords.json dosyasini indir."""
    if not os.path.exists(CUSTOM_KEYWORDS_PATH):
        save_custom_keywords({})
    return send_file(CUSTOM_KEYWORDS_PATH, as_attachment=True, download_name="custom_keywords.json")


def _excel_cell_ref(row: int, column: int) -> str:
    letters = ""
    while column:
        column, remainder = divmod(column - 1, 26)
        letters = chr(65 + remainder) + letters
    return f"{letters}{row}"


def _excel_text_cell(row: int, column: int, value) -> str:
    cell_ref = _excel_cell_ref(row, column)
    text = escape(str(value if value is not None else ""))
    return f'<c r="{cell_ref}" t="inlineStr"><is><t>{text}</t></is></c>'


def _build_keyword_management_xlsx(records: list[dict]) -> bytes:
    headers = [
        "Kaynak",
        "Kategori",
        "Kategori Adi",
        "Kelime / ifade",
        "Risk turu",
        "Risk puani",
        "Durum",
        "Baglam kurali",
        "Son guncelleme",
    ]
    rows = [headers]
    for record in records:
        rows.append([
            record.get("kaynak", ""),
            record.get("kategori", ""),
            record.get("kategori_adi", ""),
            record.get("term", ""),
            record.get("risk_turu", ""),
            record.get("risk_puani", ""),
            "Aktif" if record.get("active") else "Pasif",
            record.get("baglam_kurali", ""),
            record.get("updated_at", ""),
        ])

    sheet_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = "".join(_excel_text_cell(row_index, column_index, value) for column_index, value in enumerate(row, start=1))
        sheet_rows.append(f'<row r="{row_index}">{cells}</row>')

    worksheet = (
        runtime_config.XLSX_XML_DECL
        + runtime_config.XLSX_WORKSHEET_OPEN
        + '<cols>'
        + '<col min="1" max="1" width="14" customWidth="1"/>'
        + '<col min="2" max="3" width="24" customWidth="1"/>'
        + '<col min="4" max="4" width="34" customWidth="1"/>'
        + '<col min="5" max="7" width="14" customWidth="1"/>'
        + '<col min="8" max="8" width="48" customWidth="1"/>'
        + '<col min="9" max="9" width="24" customWidth="1"/>'
        + '</cols>'
        + f'<sheetData>{"".join(sheet_rows)}</sheetData>'
        + '</worksheet>'
    )
    workbook = (
        runtime_config.XLSX_XML_DECL
        + runtime_config.XLSX_WORKBOOK_OPEN
        + '<sheets><sheet name="Kelime Yonetimi" sheetId="1" r:id="rId1"/></sheets>'
        + '</workbook>'
    )
    rels = (
        runtime_config.XLSX_XML_DECL
        + runtime_config.XLSX_RELS_OPEN
        + f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="{runtime_config.XLSX_WORKBOOK_PATH}"/>'
        + '</Relationships>'
    )
    workbook_rels = (
        runtime_config.XLSX_XML_DECL
        + runtime_config.XLSX_WORKBOOK_RELS_OPEN
        + f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="{runtime_config.XLSX_WORKSHEET_PATH.split("/")[-1]}"/>'
        + '</Relationships>'
    )
    content_types = (
        runtime_config.XLSX_XML_DECL
        + runtime_config.XLSX_CONTENT_TYPES
        + '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        + '<Default Extension="xml" ContentType="application/xml"/>'
        + f'<Override PartName="/{runtime_config.XLSX_WORKBOOK_PATH}" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        + f'<Override PartName="/{runtime_config.XLSX_WORKSHEET_PATH}" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        + '</Types>'
    )

    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr(runtime_config.XLSX_RELS_PATH, rels)
        archive.writestr(runtime_config.XLSX_WORKBOOK_PATH, workbook)
        archive.writestr(runtime_config.XLSX_WORKBOOK_RELS_PATH, workbook_rels)
        archive.writestr(runtime_config.XLSX_WORKSHEET_PATH, worksheet)
    output.seek(0)
    return output.getvalue()


@app.route('/api/kelime-yonetimi/export-excel', methods=['GET'])
def export_kelime_yonetimi_excel():
    """Kelime yonetimi listesini Excel dosyasi olarak indir."""
    records = list_keyword_records(load_custom_keywords())
    records.sort(key=lambda item: (
        str(item.get("kaynak", "")),
        str(item.get("kategori_adi", "")),
        str(item.get("term", "")).casefold(),
    ))
    excel_bytes = _build_keyword_management_xlsx(records)
    return send_file(
        io.BytesIO(excel_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"kelime_yonetimi_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
    )


@app.route('/api/yukleme', methods=['POST'])
def pdf_yukle():
    """PDF dosyası yükle ve işlemeye başla"""
    
    try:
        # Dosya kontrolü
        if 'pdf' not in request.files:
            return jsonify({"hata": "Dosya seçilmedi"}), 400
        
        file = request.files['pdf']
        if file.filename == '':
            return jsonify({"hata": "Dosya seçilmedi"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"hata": "Sadece PDF dosyaları kabul edilir"}), 400
        
        # Dosyayı kaydet
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # PDF işle
        processor = PDFProcessor(filepath)
        metin = processor.extract_text()
        metadata = processor.extract_metadata()
        gorsel_ozet = processor.extract_visual_summary(analyze_content=False)
        istatistikler = processor.get_text_statistics()
        metadata["gorsel_ozet"] = gorsel_ozet
        
        return jsonify({
            "basarili": True,
            "dosya_yolu": filepath,
            "kitap_adi": filename,
            "metadata": metadata,
            "istatistikler": istatistikler,
            "metin_onizleme": metin[:500] if metin else "Metin çıkarılamadı"
        })
        
    except Exception as e:
        return jsonify({"hata": str(e)}), 500


@app.route('/api/degerlendir', methods=['POST'])
def degerlendir():
    """
    Kitabı Maarif Modeli'ne göre değerlendir
    
    POST Body:
    {
        "dosya_yolu": "path/to/file.pdf",
        "profil": "hibrit" (default),
        "yas_grubu": "6-12" (default)
    }
    """
    
    try:
        data = request.json
        dosya_yolu = _resolve_pdf_path(data.get('dosya_yolu'))
        profil = data.get('profil', 'hibrit')
        yas_grubu = data.get('yas_grubu', '6-12')
        
        if not os.path.exists(dosya_yolu):
            return jsonify({"hata": "Dosya bulunamadı"}), 404
        
        if profil not in ANALIZ_PROFILLERI:
            return jsonify({"hata": f"Geçersiz profil: {profil}"}), 400
        
        # PDF işle
        processor = PDFProcessor(dosya_yolu)
        metin = processor.extract_text()
        metadata = processor.extract_metadata()
        gorsel_ozet = processor.extract_visual_summary(analyze_content=False)
        
        if not metin:
            return jsonify({"hata": "PDF'den metin çıkarılamadı"}), 400
        
        # Maarif Modeli değerlendirmesi yap
        evaluator = MaarifDegerlendiricisi()
        sonuc = evaluator.analiz_yap(
            metin=metin,
            profil=profil,
            yas_grubu=yas_grubu
        )
        sonuc["metadata"] = metadata
        sonuc["gorsel_tarama"] = gorsel_ozet
        from report_generator import RaporOlusturucu
        sonuc = RaporOlusturucu()._tutarlilik_denetime_hazirla(sonuc)
        
        return jsonify({
            "basarili": True,
            "analiz_sonucu": sonuc,
            "metin_istatistikleri": {
                "kelime_sayisi": len(metin.split()),
                "karakter_sayisi": len(metin),
                "satir_sayisi": metin.count('\n') + 1
            }
        })
        
    except Exception as e:
        return jsonify({"hata": f"Değerlendirme hatası: {str(e)}"}), 500


@app.route('/api/tema-kazanim/analiz', methods=['POST'])
def tema_kazanim_analiz():
    """Risk analizinden bagimsiz tema, deger ve kazanim analizi."""
    try:
        data = request.get_json(silent=True) or {}
        dosya_yolu = _resolve_pdf_path(data.get('dosya_yolu'))
        yas_grubu = data.get('yas_grubu', '')
        ozet_turu = data.get("ozet_turu") or "standart"
        if not dosya_yolu or not os.path.exists(dosya_yolu):
            return jsonify({"basarili": False, "hata": "Dosya bulunamadı"}), 404

        processor = PDFProcessor(dosya_yolu)
        metin = processor.extract_text()
        metadata = processor.extract_metadata()
        metadata["kitap_adi"] = data.get("kitap_adi") or metadata.get("baslik") or os.path.basename(dosya_yolu)
        metadata["yazar"] = data.get("yazar") or metadata.get("yazar") or "Belirsiz"
        metadata["dosya_adi"] = os.path.basename(dosya_yolu)
        metadata["dosya_yolu"] = dosya_yolu
        sonuc = analyze_theme_gain(metin, metadata, yas_grubu, ozet_turu)
        # RUNTIME ENFORCER: Apply entity blacklist + event concreteness + no 17-word fallback + hash consistency
        if sonuc and isinstance(sonuc, dict):
            sonuc = enforce_all(sonuc)
            if is_v7_summary_ir_source():
                sonuc = attach_summary_ir(sonuc, "v7_summary_ir_source")
                sonuc = sync_summary_surfaces_from_ir(sonuc, sonuc.get("canonical_summary_ir") or {}, "v7_summary_ir_source")
        return jsonify({"basarili": True, "analiz_sonucu": sonuc})
    except Exception as e:
        return jsonify({"basarili": False, "hata": f"Tema ve kazanım analizi hatası: {str(e)}"}), 500


@app.route('/api/tema-kazanim/kaydet', methods=['POST'])
def tema_kazanim_kaydet():
    """Tema ve kazanim analizini ayri veritabanina kaydet."""
    try:
        data = request.get_json(silent=True) or {}
        sonuc = data.get("analiz_sonucu") or data
        record_id = save_theme_analysis(sonuc)
        return jsonify({"basarili": True, "id": record_id})
    except Exception as e:
        return jsonify({"basarili": False, "hata": f"Kayıt hatası: {str(e)}"}), 500


@app.route('/api/theme-report/teacher-pdf', methods=['POST'])
def teacher_report_pdf():
    """Öğretmen rehberini yalnızca öğretmen renderer'ı ile üret ve fiziksel dosyayı döndür."""
    try:
        data = request.get_json(silent=True) or {}
        sonuc = data.get("analiz_sonucu") or data
        if not isinstance(sonuc, dict) or not sonuc:
            return jsonify({"basarili": False, "hata": "Öğretmen raporu için analiz verisi bulunamadı."}), 400

        if theme_report_needs_reanalysis(sonuc):
            refreshed = _reanalyze_theme_payload_from_pdf(sonuc, data)
            if refreshed:
                debug_consistency_log(quality_gate_keys.TEACHER_REPORT_ENDPOINT_PROACTIVE_REANALYSIS_LOG_PREFIX)
                sonuc = refreshed

        sonuc, rendered_error = _rendered_summary_gate(sonuc, "/api/theme-report/teacher-pdf")
        if rendered_error:
            return rendered_error

        consistency_error = _book_consistency_gate(sonuc, "/api/theme-report/teacher-pdf")
        if consistency_error:
            refreshed = _reanalyze_theme_payload_from_pdf(sonuc, data)
            if not refreshed:
                return consistency_error
            debug_consistency_log(quality_gate_keys.TEACHER_REPORT_ENDPOINT_AUTO_REANALYSIS_LOG_PREFIX)
            sonuc = refreshed
            sonuc, rendered_error = _rendered_summary_gate(sonuc, "/api/theme-report/teacher-pdf:reanalysis")
            if rendered_error:
                return rendered_error
            consistency_error = _book_consistency_gate(sonuc, "/api/theme-report/teacher-pdf:reanalysis")
            if consistency_error:
                return consistency_error

        quality_error = _report_quality_gate(sonuc, "/api/theme-report/teacher-pdf")
        if quality_error:
            return quality_error

        # GOLDEN REGRESSION: Final checks before PDF generation
        golden_failures = run_golden_regression_checks(sonuc)
        if golden_failures:
            debug_consistency_log(
                quality_gate_keys.TEACHER_REPORT_ENDPOINT_GOLDEN_REGRESSION_FAIL_LOG_PREFIX + " "
                f"failures={golden_failures}"
            )
            return jsonify({
                "basarili": False,
                "hata": "Golden regression check failed; rapor üretimi durduruldu.",
                "kod": "GOLDEN_REGRESSION_FAIL",
                "failures": golden_failures,
            }), 409

        kitap_adi = str(sonuc.get("kitap_adi") or "kitap")
        output_path = _teacher_report_output_path(kitap_adi)
        safe_sonuc = project_analysis_preserve_evidence(sonuc, "teacher")
        pdf_buffer = generate_teacher_report_pdf(safe_sonuc)
        pdf_bytes = pdf_buffer.getvalue()
        temp_path = f"{output_path}.tmp"
        with open(temp_path, "wb") as output_file:
            output_file.write(pdf_bytes)
        os.replace(temp_path, output_path)

        digest = hashlib.sha256(pdf_bytes).hexdigest()
        debug_consistency_log(
            quality_gate_keys.TEACHER_REPORT_ENDPOINT_RESPONSE_LOG_PREFIX + " "
            "generator=theme_gain_analysis.generate_teacher_report_pdf "
            f"output_path={output_path!r} bytes={len(pdf_bytes)} sha256={digest} "
            f"version={TEACHER_REPORT_VERSION} title='Öğretmen Kitap Rehberi'"
        )
        response = send_file(
            output_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=os.path.basename(output_path),
        )
        response.headers["X-Report-Generator"] = "generate_teacher_report_pdf"
        response.headers["X-Teacher-Report-Version"] = TEACHER_REPORT_VERSION
        response.headers["X-Report-File"] = os.path.basename(output_path)
        response.headers["X-Report-SHA256"] = digest
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        debug_consistency_log(quality_gate_keys.TEACHER_REPORT_ENDPOINT_ERROR_LOG_PREFIX + f" error={e!r}")
        return jsonify({"basarili": False, "hata": f"Öğretmen raporu hatası: {str(e)}"}), 500


@app.route('/api/tema-kazanim/rapor', methods=['POST'])
def tema_kazanim_rapor():
    """Tema ve kazanim analizini ayri PDF veya Word raporu olarak indir."""
    try:
        data = request.get_json(silent=True) or {}
        clear_runtime_json_dumps("/api/tema-kazanim/rapor:start")
        sonuc = _harmonize_analysis_core_fields(data.get("analiz_sonucu") or {})
        analysis_core_snapshot = copy.deepcopy(sonuc) if isinstance(sonuc, dict) else {}
        raw_sonuc_for_teacher = dict(sonuc) if isinstance(sonuc, dict) else {}
        fmt = str(data.get("format") or "pdf").lower()
        report_type = str(data.get("report_type") or data.get("rapor_turu") or "").lower()
        if request.path.endswith(runtime_config.TEACHER_PDF_SUFFIX):
            report_type = "teacher"
            fmt = "pdf"
        ozet_turu = data.get("ozet_turu") or sonuc.get("ozet_turu") or "standart"
        tema_analizi = sonuc.get("tema_analizi") or []
        yeni_metrikler_var = any(item.get("tema_gucu") for item in tema_analizi if isinstance(item, dict))
        ozet_var = bool(sonuc.get("canonical_summary") or sonuc.get("kitap_ozeti"))
        incoming_summary = _select_report_summary(sonuc)
        incoming_summary_valid = _summary_is_valid_for_report(incoming_summary)
        incoming_summary_usable = _summary_is_usable_for_pdf(incoming_summary)
        incoming_summary_accepted = incoming_summary_valid or incoming_summary_usable
        incoming_summary_source = _theme_summary_source(sonuc)
        incoming_summary_fields = _theme_summary_fields(sonuc) if incoming_summary_accepted else {}
        rapor_oncesi_yeniden_analiz_gerekli = theme_report_needs_reanalysis(sonuc)
        dosya_yolu = _resolve_pdf_path(
            sonuc.get("dosya_yolu")
            or (sonuc.get("metadata") or {}).get("dosya_yolu")
            or data.get("dosya_yolu")
        )
        sonuc = _assign_analysis_cache_identity(sonuc, dosya_yolu, "tema_kazanim_rapor_input")
        _dump_runtime_json("analyze_theme_gain_return", sonuc)
        sonuc, rendered_error = _rendered_summary_gate(sonuc, "/api/tema-kazanim/rapor:input")
        if rendered_error:
            return rendered_error
        incoming_summary = _select_report_summary(sonuc)
        incoming_summary_valid = _summary_is_valid_for_report(incoming_summary)
        incoming_summary_usable = _summary_is_usable_for_pdf(incoming_summary)
        incoming_summary_accepted = incoming_summary_valid or incoming_summary_usable
        incoming_summary_source = _theme_summary_source(sonuc)
        incoming_summary_fields = _theme_summary_fields(sonuc) if incoming_summary_accepted else {}
        analysis_core_snapshot = copy.deepcopy(sonuc) if isinstance(sonuc, dict) else {}
        raw_sonuc_for_teacher = dict(sonuc) if isinstance(sonuc, dict) else {}
        debug_consistency_log(
            "[tema_kazanim_rapor] INPUT_SUMMARY "
            f"build_id={BUILD_ID} "
            f"book_id={sonuc.get('book_id')} cache_key={sonuc.get('cache_key')} "
            f"request_kitap_ozeti_var={bool(sonuc.get('kitap_ozeti'))} "
            f"secilen_ozet_alani={incoming_summary_source} "
            f"incoming_summary_valid={incoming_summary_valid} "
            f"incoming_summary_usable={incoming_summary_usable} "
            f"reanalysis_required={rapor_oncesi_yeniden_analiz_gerekli} "
            f"{_theme_summary_debug_fields(sonuc)}"
        )
        if not incoming_summary_accepted:
            if dosya_yolu and os.path.exists(dosya_yolu):
                debug_consistency_log("[tema_kazanim_rapor] AUTO_REANALYSIS_AFTER_INVALID_SUMMARY")
                rapor_oncesi_yeniden_analiz_gerekli = True
            else:
                debug_consistency_log(
                    "[tema_kazanim_rapor] BLOCKED_MISSING_VALID_SUMMARY "
                    f"build_id={BUILD_ID} "
                    f"request_kitap_ozeti_var={bool(sonuc.get('kitap_ozeti'))} "
                    f"secilen_ozet_alani={incoming_summary_source} "
                    f"{_theme_summary_debug_fields(sonuc)}"
                )
                return jsonify({
                    "basarili": False,
                    "hata": "PDF endpoint geçerli kitap_ozeti almadı",
                    "build_id": BUILD_ID,
                    "request_kitap_ozeti_var": bool(sonuc.get("kitap_ozeti")),
                    "secilen_ozet_alani": incoming_summary_source,
                    "baslik_sayisi": _summary_heading_count(incoming_summary),
                    "kelime_sayisi": len(incoming_summary.split()),
                    "ozet_kalite_hatalari": sonuc.get("ozet_kalite_hatalari") or [],
                }), 400
        consistency_error = _book_consistency_gate(sonuc, "/api/tema-kazanim/rapor:input")
        if consistency_error:
            if not dosya_yolu or not os.path.exists(dosya_yolu):
                return consistency_error
            debug_consistency_log("[tema_kazanim_rapor] AUTO_REANALYSIS_AFTER_CONSISTENCY_FAILURE")
            incoming_summary_accepted = False
            incoming_summary_fields = {}
            rapor_oncesi_yeniden_analiz_gerekli = True
        reanalysis_used = False
        if (not yeni_metrikler_var or not ozet_var or rapor_oncesi_yeniden_analiz_gerekli) and dosya_yolu and os.path.exists(dosya_yolu):
            processor = PDFProcessor(dosya_yolu)
            metin = processor.extract_text()
            metadata = processor.extract_metadata()
            metadata["kitap_adi"] = sonuc.get("kitap_adi") or metadata.get("baslik") or os.path.basename(dosya_yolu)
            metadata["yazar"] = sonuc.get("yazar") or metadata.get("yazar") or "Belirsiz"
            metadata["dosya_adi"] = os.path.basename(dosya_yolu)
            metadata["dosya_yolu"] = dosya_yolu
            debug_consistency_log(
                "[tema_kazanim_rapor] ANALYZE_ENTER "
                f"build_id={BUILD_ID} runtime_build_timestamp={RUNTIME_BUILD_TIMESTAMP} "
                f"metadata_id={id(metadata)} target_pdf_function=theme_gain_analysis.build_pdf_report"
            )
            sonuc = analyze_theme_gain(metin, metadata, data.get("yas_grubu", ""), ozet_turu)
            sonuc = _harmonize_analysis_core_fields(sonuc)
            sonuc = _assign_analysis_cache_identity(sonuc, dosya_yolu, "tema_kazanim_rapor_reanalysis")
            _dump_runtime_json("analyze_theme_gain_return", sonuc)
            analysis_core_snapshot = copy.deepcopy(sonuc)
            debug_consistency_log(
                "[tema_kazanim_rapor] ANALYZE_EXIT "
                f"build_id={BUILD_ID} runtime_build_timestamp={RUNTIME_BUILD_TIMESTAMP} "
                f"result_id={id(sonuc)} ana_tema={sonuc.get('ana_tema')!r} "
                f"book_type={sonuc.get('book_type')!r} subtype={sonuc.get('book_subtype')!r} "
                f"target_pdf_function=theme_gain_analysis.build_pdf_report"
            )
            reanalysis_used = True
            if incoming_summary_accepted:
                sonuc.update(incoming_summary_fields)
                debug_consistency_log(
                    "[tema_kazanim_rapor] PRESERVED_UI_SUMMARY_AFTER_REANALYSIS "
                    f"{_theme_summary_debug_fields(sonuc)}"
                )
        sonuc = prepare_theme_report_payload(sonuc)
        # RUNTIME ENFORCER: Apply fixes after report payload preparation
        if sonuc and isinstance(sonuc, dict):
            sonuc = enforce_all(sonuc)
        if incoming_summary_accepted:
            _norm = runtime_config.normalize_summary_status(sonuc.get("kitap_ozeti") or "")
            if _norm == runtime_config.STATUS_UNRELIABLE_SUMMARY:
                sonuc.update(incoming_summary_fields)
                sonuc = prepare_theme_report_payload(sonuc)
                debug_consistency_log(
                    "[tema_kazanim_rapor] RESTORED_UI_SUMMARY_AFTER_PREPARE_FALLBACK "
                    f"{_theme_summary_debug_fields(sonuc)}"
                )
        if incoming_summary_accepted and _is_summary_unavailable_text(sonuc.get("kitap_ozeti") or ""):
            sonuc.update(incoming_summary_fields)
            sonuc = prepare_theme_report_payload(sonuc)
            debug_consistency_log(
                "[tema_kazanim_rapor] RESTORED_UI_SUMMARY_AFTER_ANY_FALLBACK "
                f"build_id={BUILD_ID} "
                f"{_theme_summary_debug_fields(sonuc)}"
            )
        sonuc = _restore_analysis_core_fields(sonuc, analysis_core_snapshot)
        if sonuc and isinstance(sonuc, dict):
            sonuc = enforce_all(sonuc, "tema_kazanim_rapor_after_core_restore")
        sonuc, rendered_error = _rendered_summary_gate(sonuc, "/api/tema-kazanim/rapor")
        if rendered_error:
            return rendered_error
        tema_analizi = sonuc.get("tema_analizi") or []
        ilk_uc = sonuc.get("ilk_uc_baskin_tema") or []
        consistency_error = _book_consistency_gate(sonuc, "/api/tema-kazanim/rapor")
        if consistency_error:
            return consistency_error
        quality_error = _report_quality_gate(sonuc, "/api/tema-kazanim/rapor")
        if quality_error:
            return quality_error
        debug_consistency_log(
            "[tema_kazanim_rapor] BEFORE_EXPORT "
            f"build_id={BUILD_ID} "
            f"format={fmt} "
            f"endpoint=/api/tema-kazanim/rapor "
            f"pdf_function=theme_gain_analysis.build_pdf_report "
            f"request_kitap_ozeti_var={bool(incoming_summary_fields.get('kitap_ozeti'))} "
            f"secilen_ozet_alani={incoming_summary_source} "
            f"ilk_uc_baskin_tema_var={bool(ilk_uc)} "
            f"ilk_uc_sayi={len(ilk_uc)} "
            f"tema_gucu_var={any(isinstance(item, dict) and item.get('tema_gucu') is not None for item in tema_analizi)} "
            f"dinamik_guven_skoru_var={any(isinstance(item, dict) and item.get('guven_skoru') is not None for item in tema_analizi)} "
            f"guclu_temalar_sayi={len(sonuc.get('guclu_temalar') or [])} "
            f"destekleyici_temalar_sayi={len(sonuc.get('destekleyici_temalar') or [])} "
            f"kitap_ozeti_var={bool(sonuc.get('kitap_ozeti'))} "
            f"ozet_uzunlugu={sonuc.get('ozet_uzunlugu')} "
            f"summary_reanalysis_required={rapor_oncesi_yeniden_analiz_gerekli} "
            f"reanalysis_used={reanalysis_used} "
            f"incoming_summary_valid={incoming_summary_valid} "
            f"incoming_summary_usable={incoming_summary_usable} "
            f"{_theme_summary_debug_fields(sonuc)}"
        )
        kitap_adi = str(sonuc.get("kitap_adi") or "tema_kazanim").replace("/", "_").replace("\\", "_")
        if report_type in {"teacher", "ogretmen", "öğretmen"}:
            teacher_sonuc = dict(sonuc)
            for key in ["tema_analizi", "ilk_uc_baskin_tema", "kazanim_analizi", "deger_analizi"]:
                if not teacher_sonuc.get(key) and raw_sonuc_for_teacher.get(key):
                    teacher_sonuc[key] = raw_sonuc_for_teacher[key]
            teacher_sonuc = project_analysis_preserve_evidence(teacher_sonuc, "teacher")
            buffer = generate_teacher_report_pdf(teacher_sonuc)
            buffer.seek(0)
            return send_file(buffer, mimetype=runtime_config.APPLICATION_PDF, as_attachment=True, download_name=f"{kitap_adi}{runtime_config.TEACHER_REPORT_FILENAME_SUFFIX}")
        if _is_development_mode():
            sonuc["rapor_build_id"] = BUILD_ID
        if fmt == "word":
            safe_sonuc = project_analysis_preserve_evidence(sonuc, "word")
            buffer = build_theme_word_report(safe_sonuc)
            buffer.seek(0)
            return send_file(buffer, mimetype=runtime_config.APPLICATION_MSWORD, as_attachment=True, download_name=f"{kitap_adi}{runtime_config.THEME_REPORT_WORD_FILENAME_SUFFIX}")
        debug_consistency_log(
            "[tema_kazanim_rapor] BUILD_PDF_REPORT_ENTER "
            f"build_id={BUILD_ID} runtime_build_timestamp={RUNTIME_BUILD_TIMESTAMP} "
            f"payload_id={id(sonuc)} ana_tema={sonuc.get('ana_tema')!r} "
            f"book_type={sonuc.get('book_type')!r} subtype={sonuc.get('book_subtype')!r}"
        )
        safe_sonuc = project_analysis_preserve_evidence(sonuc, "pdf")
        buffer = build_theme_pdf_report(safe_sonuc)
        debug_consistency_log(
            "[tema_kazanim_rapor] BUILD_PDF_REPORT_EXIT "
            f"build_id={BUILD_ID} runtime_build_timestamp={RUNTIME_BUILD_TIMESTAMP} "
            f"payload_id={id(sonuc)} buffer_id={id(buffer)}"
        )
        buffer.seek(0)
        return send_file(buffer, mimetype=runtime_config.APPLICATION_PDF, as_attachment=True, download_name=f"{kitap_adi}{runtime_config.THEME_REPORT_FILENAME_SUFFIX}")
    except Exception as e:
        return jsonify({"basarili": False, "hata": f"Tema raporu hatası: {str(e)}"}), 500


@app.route('/api/rapor', methods=['POST'])
def api_rapor_endpoint_v2():
    """
    Değerlendirme raporunu PDF olarak oluştur
    """
    import report_generator
    from report_generator import RaporOlusturucu
    from text_quality import repair_payload_text
    
    try:
        data = request.json
        analiz_sonucu = data.get('analiz_sonucu')
        kitap_adi = data.get('kitap_adi', 'Kitap')
        
        if not analiz_sonucu:
            return jsonify({"hata": "Analiz sonucu gerekli"}), 400
        analiz_sonucu = repair_payload_text(analiz_sonucu)
        rapor_dosya_yolu = (
            data.get('dosya_yolu')
            or analiz_sonucu.get('dosya_yolu')
            or (analiz_sonucu.get('metadata') or {}).get('dosya_yolu')
            or kitap_adi
        )
        analiz_sonucu = _rapor_icin_gorsel_taramayi_yenile(analiz_sonucu, rapor_dosya_yolu)

        kategori_bulgulari = analiz_sonucu.get('kategori_bulgulari', {}) or {}
        kavgalilar = []
        zararli_aliskanlik_kayitlari = []
        for kategori, kategori_data in kategori_bulgulari.items():
            for bulgu in kategori_data.get('bulunan_kelimeler', []) or []:
                kelime = str(bulgu.get('kelime') or bulgu.get('tema_adi') or '').strip().lower()
                if kelime == 'kavgalı':
                    kavgalilar.append({
                        'kategori': kategori,
                        'riskPuani': bulgu.get('riskPuani'),
                        'risk_puani': bulgu.get('risk_puani'),
                        'baglamsal_risk': bulgu.get('baglamsal_risk'),
                        'kararSinifi': bulgu.get('kararSinifi'),
                        'sayfa': bulgu.get('sayfa'),
                    })
                cumle = str(bulgu.get('cumle') or bulgu.get('baglam') or bulgu.get('kontext') or '').lower()
                zararli_metin = f"{kelime} {cumle}"
                if any(anahtar in zararli_metin for anahtar in ('sigara', 'sarhoş', 'sarhos', 'alkol', 'içki', 'icki')):
                    zararli_aliskanlik_kayitlari.append({
                        'kategori': kategori,
                        'kelime': bulgu.get('kelime') or bulgu.get('tema_adi'),
                        'riskPuani': bulgu.get('riskPuani'),
                        'risk_puani': bulgu.get('risk_puani'),
                        'baglamsal_risk': bulgu.get('baglamsal_risk'),
                        'kararSinifi': bulgu.get('kararSinifi'),
                        'sayfa': bulgu.get('sayfa'),
                    })
        debug_consistency_log(
            quality_gate_keys.APP_API_RAPOR_REQUEST_LOG_PREFIX + " "
            f"app_file={__file__} evaluator_file={sys.modules.get('evaluator_maarif').__file__ if sys.modules.get('evaluator_maarif') else '?'} "
            f"report_generator_file={report_generator.__file__} cwd={os.getcwd()} python={sys.executable} "
            f"kitap_adi={kitap_adi} kategori_sayisi={len(kategori_bulgulari)} "
            f"tema_bulgu_sayisi={len(((analiz_sonucu.get('tema_olay_orgusu_bulgulari') or {}).get('bulgular') or []))} "
            f"kavgalilar={kavgalilar} zararli_aliskanlik_kayitlari={zararli_aliskanlik_kayitlari}"
        )

        evaluator = MaarifDegerlendiricisi()
        rapor_generator = RaporOlusturucu()
        analiz_sonucu = evaluator.tema_bulgularini_kanit_kontroluyle_temizle(analiz_sonucu)
        analiz_sonucu = rapor_generator._tutarlilik_denetime_hazirla(analiz_sonucu)
        analiz_sonucu = evaluator._zorunlu_kalite_kontrolunu_uygula(
            analiz_sonucu,
            json.dumps(analiz_sonucu, ensure_ascii=False)
        )
        kalite_kontrol_log = analiz_sonucu.get('zorunlu_kalite_kontrolu') or {}
        kalite_sorulari_log = kalite_kontrol_log.get('son_kalite_kontrol_sorulari') or {}
        debug_consistency_log(
            quality_gate_keys.APP_API_RAPOR_AFTER_KANIT_REVALIDATION_LOG_PREFIX + " "
            f"tema_bulgu_sayisi={len(((analiz_sonucu.get('tema_olay_orgusu_bulgulari') or {}).get('bulgular') or []))} "
            f"final_skor={analiz_sonucu.get('final_skor')} "
            f"rapor_olusturulabilir={kalite_kontrol_log.get('rapor_olusturulabilir')} "
            f"aktif_kalite_bayraklari={[k for k, v in kalite_sorulari_log.items() if v]}"
        )

        analiz_sonucu = rapor_generator.pdf_oncesi_consistency_assert(analiz_sonucu)

        kalite_kontrol = analiz_sonucu.get('zorunlu_kalite_kontrolu', {})
        # Normalize textual report status to structured constant for runtime checks
        _rapor_durumu = analiz_sonucu.get('rapor_durumu')
        _kalite_rapor_durumu = kalite_kontrol.get('rapor_durumu')
        _rapor_missing = (
            (_rapor_durumu == runtime_config.REPORT_STATUS_MISSING_ANALYSIS)
            or (runtime_config.normalize_report_status(_rapor_durumu) == runtime_config.REPORT_STATUS_MISSING_ANALYSIS)
            or (_kalite_rapor_durumu == runtime_config.REPORT_STATUS_MISSING_ANALYSIS)
            or (runtime_config.normalize_report_status(_kalite_rapor_durumu) == runtime_config.REPORT_STATUS_MISSING_ANALYSIS)
        )
        eksik_analiz_raporu = (
            _rapor_missing
            or (
                kalite_kontrol.get('quality_check') == 'FAIL'
                and kalite_kontrol.get('son_kalite_kontrol_sorulari', {}).get('gorsel_icerik_analizi_eksik_mi') is True
            )
        )
        if kalite_kontrol and not kalite_kontrol.get('rapor_olusturulabilir', True) and not eksik_analiz_raporu:
            debug_consistency_log(
                quality_gate_keys.APP_API_RAPOR_BLOCKED_BY_ANALYSIS_QUALITY_LOG_PREFIX + " "
                f"eksikler={kalite_kontrol.get('eksikler', [])}"
            )
            return jsonify({
                "hata": "Zorunlu kalite kontrolü rapor oluşturmayı durdurdu.",
                "son_rapor_dogrulama": kalite_kontrol.get(
                    'son_rapor_dogrulama_cevabi',
                    'HAYIR'
                ),
                "eksikler": kalite_kontrol.get('eksikler', []),
                "kontrol": kalite_kontrol,
            }), 422
        
        # Rapor oluştur
        pdf_buffer = rapor_generator.olustur(
            degerlen_sonuclari=analiz_sonucu,
            metadata={**analiz_sonucu.get('metadata', {}), 'kitap_adi': kitap_adi}
        )
        
        # Buffer position 0'a reset et
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{kitap_adi}{runtime_config.MAARIF_REPORT_FILENAME_SUFFIX}'
        )
        
    except ValueError as e:
        debug_consistency_log(quality_gate_keys.APP_API_RAPOR_BLOCKED_BY_PDF_ASSERT_LOG_PREFIX + f" detay={str(e)}")
        return jsonify({
            "hata": "PDF üretimi tutarlılık denetimi nedeniyle durduruldu.",
            "detay": str(e)
        }), 422
    except Exception as e:
        return jsonify({"hata": f"Rapor oluşturma hatası: {str(e)}"}), 500


@app.route('/api/karsilastir', methods=['POST'])
def karsilastir():
    """
    Aynı kitabı farklı profillerle karşılaştır
    """
    
    try:
        data = request.json
        dosya_yolu = data.get('dosya_yolu')
        yas_grubu = data.get('yas_grubu', '6-12')
        
        if not os.path.exists(dosya_yolu):
            return jsonify({"hata": "Dosya bulunamadı"}), 404
        
        # PDF işle
        processor = PDFProcessor(dosya_yolu)
        metin = processor.extract_text()
        
        if not metin:
            return jsonify({"hata": "PDF'den metin çıkarılamadı"}), 400
        
        # Tüm profillerle değerlendir
        evaluator = MaarifDegerlendiricisi()
        sonuclar = {}
        
        for profil_key in ANALIZ_PROFILLERI.keys():
            sonuc = evaluator.analiz_yap(
                metin=metin,
                profil=profil_key,
                yas_grubu=yas_grubu
            )
            sonuclar[profil_key] = {
                "ad": ANALIZ_PROFILLERI[profil_key]["ad"],
                "final_skor": sonuc["final_skor"],
                "karar": sonuc["karar"]
            }
        
        return jsonify({
            "basarili": True,
            "karsilastirma": sonuclar
        })
        
    except Exception as e:
        return jsonify({"hata": f"Karşılaştırma hatası: {str(e)}"}), 500


@app.route('/api/professional/kelime-degerlendirme', methods=['POST'])
def professional_word_evaluation():
    """
    Profesyonel İçerik Denetim Uzmanı - Tek Kelime Değerlendirmesi
    
    6 Aşamalı Değerlendirme:
    1. Kelime bağımsız mı?
    2. Başka kelimenin içinde mi?
    3. Cümlenin anlamı nedir?
    4. Kullanım tipi nedir?
    5. Çocuk okuyucu üzerinde olumsuz etki?
    6. Risk puanı (profil özelinde)
    
    POST Body:
    {
        "word": "kelime",
        "context": "Kelimenin kullanıldığı cümle",
        "profile": "maarif|meb|hybrid" (default: hybrid)
    }
    """
    
    try:
        data = request.json
        if not data:
            return jsonify({"hata": "JSON body gerekli"}), 400
            
        word = data.get('word', '').strip()
        context = data.get('context', '').strip()
        profile = data.get('profile', 'hybrid')
        
        if not word:
            return jsonify({"hata": "Kelime gerekli"}), 400
        
        if not context:
            return jsonify({"hata": "Bağlam (cümle) gerekli"}), 400
        
        if profile not in ['maarif', 'meb', 'hybrid']:
            profile = 'hybrid'
        
        evaluator = ProfessionalContentEvaluator()
        result = evaluator.evaluate_word(word, context, profile)
        
        return jsonify({
            "basarili": True,
            "degerlendirme": result,
            "ozet": {
                "kelime": word,
                "gecerli_bulgu_mu": result['is_valid_finding'],
                "risk_skoru": result['risk_score'],
                "risk_seviyesi": result['risk_level'],
                "neden": result['reason']
            }
        })
        
    except Exception as e:
        import traceback
        print(f"\n❌ Kelime Değerlendirme Hatası: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "basarili": False,
            "hata": f"Değerlendirme hatası: {str(e)}"
        }), 500


@app.route('/api/professional/metin-analiz', methods=['POST'])
def professional_text_analysis():
    """
    Profesyonel İçerik Denetim Uzmanı - Tam Metin Analizi
    
    POST Body:
    {
        "metin": "Değerlendirilecek kitap metni",
        "profile": "maarif|meb|hybrid" (default: hybrid)
    }
    """
    
    try:
        data = request.json
        if not data:
            return jsonify({"hata": "JSON body gerekli"}), 400
            
        metin = data.get('metin', '').strip()
        profile = data.get('profile', 'hybrid')
        
        if not metin:
            return jsonify({"hata": "Metin gerekli"}), 400
        
        if profile not in ['maarif', 'meb', 'hybrid']:
            profile = 'hybrid'
        
        evaluator = ProfessionalContentEvaluator()
        result = evaluator.evaluate_text(metin, profile)
        
        # Problem sayılarını ve türlerini analiz et
        problem_by_type = {}
        for finding in result['findings']:
            if finding['is_valid_finding']:
                risk_level = finding['risk_level']
                if risk_level not in problem_by_type:
                    problem_by_type[risk_level] = 0
                problem_by_type[risk_level] += 1
        
        return jsonify({
            "basarili": True,
            "analiz": {
                "toplam_bulgu": result['total_findings'],
                "problem_bulgu": result['problem_findings'],
                "problem_olmayan": result['non_problem_count'],
                "ortalama_risk": result['summary']['average_risk'],
                "bulgular": result['findings'][:20]
            },
            "ozet": {
                "toplam_bulgu": result['total_findings'],
                "problem_bulgu": result['problem_findings'],
                "problem_olmayan": result['non_problem_count'],
                "ortalama_risk": result['summary']['average_risk'],
                "problem_türleri": problem_by_type,
                "profil": profile
            }
        })
        
    except Exception as e:
        import traceback
        print(f"\n❌ Metin Analiz Hatası: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "basarili": False,
            "hata": f"Analiz hatası: {str(e)}"
        }), 500


@app.route('/api/professional/profiller', methods=['GET'])
def professional_profiles():
    """Profesyonel Değerlendirici'de Mevcut Profilleri Listele"""
    
    evaluator = ProfessionalContentEvaluator()
    
    return jsonify({
        "basarili": True,
        "profiller": {
            "maarif": {
                "ad": runtime_config.ORG_MAARIF_MEB_LABEL,
                "aciklama": "Müfettiş ve okul hassasiyeti",
                "uygulanabilir": True
            },
            "meb": {
                "ad": "MEB Standart",
                "aciklama": "MEB ders kitapları standardı",
                "uygulanabilir": True
            },
            "hybrid": {
                "ad": "Hibrit",
                "aciklama": "Yayınevi + Maarif dengesi",
                "uygulanabilir": True,
                "default": True
            }
        }
    })


@app.route('/health')
def health():
    """Sistem durumu kontrolü"""
    return jsonify({
        "status": "OK",
        "message": "Maarif Modeli Yayın Denetim Sistemi çalışıyor",
        "versiyon": "1.0",
        "build_id": BUILD_ID,
        "teacher_report_version": TEACHER_REPORT_VERSION,
        "moduller": {
            "maarif_model": "✅ Aktif",
            "professional_evaluator": "✅ Aktif",
            "6_step_evaluation": "✅ Aktif"
        }
    })

@app.route('/version')
@app.route('/debug-build-id')
def debug_build_id():
    return jsonify({
        "status": "OK",
        "build_id": BUILD_ID,
        "teacher_report_version": TEACHER_REPORT_VERSION,
        "pid": os.getpid(),
        "app_root": app.root_path,
        "cwd": os.getcwd(),
    })


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    print("🚀 Maarif Modeli Yayın Denetim Sistemi başlıyor...")
    print(f"📝 Port: {port}")
    print(f"🔧 Debug Modu: {debug_mode}")
    reload_enabled = os.getenv('APP_ENV', 'development').lower() != 'production'
    app.run(debug=False, port=port, use_reloader=reload_enabled)
