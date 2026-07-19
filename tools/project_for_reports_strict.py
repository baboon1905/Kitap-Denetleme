import copy
import json
from typing import Any, Dict, List

# REQUIRED: present in all real payloads; absence breaks report generation
# OPTIONAL: may be absent; preserved if present; builder uses fallback if absent
# DERIVED: not from request input; builder constructs from other fields

PDF_REQUIRED_FIELDS = [
    "kitap_adi","yazar","book_type","book_subtype","analiz_tarihi","ana_tema",
    "tema_analizi","ilk_uc_baskin_tema","guclu_temalar","destekleyici_temalar",
    "temel_mesajlar","kazanim_analizi","ogretmen_notu","kitap_ozeti"
]

PDF_OPTIONAL_FIELDS = [
    "ogretmen_notlari",
    "event_graph",
    "olay_akisi",
    "ana_tema_kanitlari",
    "canonical_summary",
    "summary",
    "book_summary",
    "ozet",
    "rendered_summary_hash",
    "canonical_summary_ir",
    "summary_consistency_audit",
    "canonical_entity_store",
]

WORD_REQUIRED_FIELDS = PDF_REQUIRED_FIELDS.copy()

WORD_OPTIONAL_FIELDS = PDF_OPTIONAL_FIELDS.copy()

PDF_DERIVED_FIELDS = [
    "ana_tema_tema_gucu","ana_tema_guven_skoru","ozet_guven_skoru","kanit_sayisi"
]

WORD_DERIVED_FIELDS = [
    "ana_tema_tema_gucu","ana_tema_guven_skoru","ozet_guven_skoru"
]

TEACHER_DERIVED_FIELDS = [
    "kisa_ogretmen_ozeti","kitaba_ozguluk"
]

TEACHER_REQUIRED_FIELDS = [
    "kitap_adi","yazar","book_type","book_subtype","analiz_tarihi",
    "ana_tema","ogretmen_notu","kazanim_analizi"
]

TEACHER_OPTIONAL_FIELDS = [
    "hedef_yas_sinif","kisa_ogretmen_ozeti","temalar","kazanimlar","degerler",
    "dikkatli_kullanilacak_degerler","kullanilabilecek_dersler","kitaba_ozel_etkinlikler",
    "tartisma_sorulari","ogretmen_notlari","neden_oneriyoruz",
    "kitap_ozeti",
    "canonical_summary_ir",
    "summary_consistency_audit",
    "rendered_summary",
    "summary_before_gate",
    "summary_after_gate",
    "summary_before_gate_hash",
    "summary_after_gate_hash",
    "summary_ui_hash",
    "summary_pdf_hash",
    "rendered_summary_hash",
    "ui_summary_hash",
    "pdf_summary_hash",
    "canonical_summary_hash",
    "canonical_summary_ir_hash",
    "canonical_entity_store"
]


def canonical_bytes(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def _shallow_keep(obj: Dict[str, Any], allowed: List[str]) -> Dict[str, Any]:
    out = {}
    for k in allowed:
        if k in obj:
            out[k] = copy.deepcopy(obj[k])
    return out


def _project_theme_list_preserve_evidence(themes: Any, evidence_limit: int = 3) -> List[Dict[str, Any]]:
    out = []
    for t in (themes or [])[:50]:
        if not isinstance(t, dict):
            continue
        entry = {}
        for k in ["ad","tema_gucu","kanit_sayisi","farkli_sayfa_sayisi","guven_skoru","gerekce","puan"]:
            if k in t:
                entry[k] = copy.deepcopy(t[k])
        evidences = t.get('kanitlar') or []
        preserved = []
        for ev in evidences[:evidence_limit]:
            if not isinstance(ev, dict):
                continue
            # Preserve only evidence metadata already present in the source.
            e = {}
            for field in [
                'sayfa',
                'alinti',
                'anahtarlar',
                'kanit_turu',
                'kanit_agirligi',
                'baglam_gucu',
                'source_sentence_id',
                'source_sentence_ids',
            ]:
                if field in ev:
                    e[field] = copy.deepcopy(ev[field])
            preserved.append(e)
        if preserved:
            entry['kanitlar'] = preserved
        out.append(entry)
    return out


def _project_kazanim_list_preserve_evidence(ks: Any, evidence_limit: int = 3) -> List[Dict[str, Any]]:
    out = []
    for k in (ks or [])[:50]:
        if not isinstance(k, dict):
            continue
        entry = {}
        for key in ["ad","puan","kanit_sayisi","farkli_sayfa_sayisi","gerekce","guven_skoru"]:
            if key in k:
                entry[key] = copy.deepcopy(k[key])
        evidences = k.get('kanitlar') or []
        preserved = []
        for ev in evidences[:evidence_limit]:
            if not isinstance(ev, dict):
                continue
            e = {}
            if 'sayfa' in ev:
                e['sayfa'] = copy.deepcopy(ev['sayfa'])
            if 'alinti' in ev:
                e['alinti'] = copy.deepcopy(ev['alinti'])
            if 'source_sentence_id' in ev:
                e['source_sentence_id'] = copy.deepcopy(ev['source_sentence_id'])
            if 'source_sentence_ids' in ev:
                e['source_sentence_ids'] = copy.deepcopy(ev['source_sentence_ids'])
            preserved.append(e)
        if preserved:
            entry['kanitlar'] = preserved
        out.append(entry)
    return out


def _project_canonical_entity_store(store: Any) -> Dict[str, Any]:
    if not isinstance(store, dict):
        return {}
    out = {}
    for k, v in store.items():
        if not isinstance(v, dict):
            continue
        item = {}
        for f in ["canonical_form","entity_type","surface_forms","aliases","pages"]:
            if f in v:
                item[f] = copy.deepcopy(v[f])
        out[k] = item
    return out


def _count_field_occurrences(obj: Any, field_name: str) -> int:
    if isinstance(obj, dict):
        count = 0
        for k, v in obj.items():
            if k == field_name:
                count += 1
            count += _count_field_occurrences(v, field_name)
        return count
    if isinstance(obj, list):
        return sum(_count_field_occurrences(item, field_name) for item in obj)
    return 0


def _remove_entity_store_graph(obj: Any) -> Any:
    if isinstance(obj, dict):
        obj.pop('entity_store_graph', None)
        for value in obj.values():
            _remove_entity_store_graph(value)
    elif isinstance(obj, list):
        for item in obj:
            _remove_entity_store_graph(item)
    return obj


def project_analysis_preserve_evidence(analiz_sonucu: Dict[str, Any], report_type: str) -> Dict[str, Any]:
    if not isinstance(analiz_sonucu, dict):
        return {}
    allowed = []
    if report_type == 'pdf':
        allowed = PDF_REQUIRED_FIELDS + PDF_OPTIONAL_FIELDS
    elif report_type == 'word':
        allowed = WORD_REQUIRED_FIELDS + WORD_OPTIONAL_FIELDS
    elif report_type == 'teacher':
        allowed = TEACHER_REQUIRED_FIELDS + TEACHER_OPTIONAL_FIELDS
    else:
        allowed = PDF_REQUIRED_FIELDS + PDF_OPTIONAL_FIELDS

    projected = _shallow_keep(analiz_sonucu, allowed)

    # themes
    if 'tema_analizi' in analiz_sonucu:
        projected['tema_analizi'] = _project_theme_list_preserve_evidence(analiz_sonucu.get('tema_analizi'))
    if 'guclu_temalar' in analiz_sonucu:
        projected['guclu_temalar'] = _project_theme_list_preserve_evidence(analiz_sonucu.get('guclu_temalar'))
    if 'destekleyici_temalar' in analiz_sonucu:
        projected['destekleyici_temalar'] = _project_theme_list_preserve_evidence(analiz_sonucu.get('destekleyici_temalar'))
    if 'ilk_uc_baskin_tema' in analiz_sonucu:
        projected['ilk_uc_baskin_tema'] = _project_theme_list_preserve_evidence(analiz_sonucu.get('ilk_uc_baskin_tema'))

    # kazanımlar
    if 'kazanim_analizi' in analiz_sonucu:
        projected['kazanim_analizi'] = _project_kazanim_list_preserve_evidence(analiz_sonucu.get('kazanim_analizi'))

    # canonical_entity_store
    if 'canonical_entity_store' in analiz_sonucu:
        projected['canonical_entity_store'] = _project_canonical_entity_store(analiz_sonucu.get('canonical_entity_store'))

    # ensure no entity_store_graph survives anywhere in the projected result
    _remove_entity_store_graph(projected)
    assert 'entity_store_graph' not in projected
    assert _count_field_occurrences(projected, 'entity_store_graph') == 0

    # canonical_summary_ir and summary_consistency_audit preserved as-is if present
    if 'canonical_summary_ir' in analiz_sonucu and isinstance(analiz_sonucu.get('canonical_summary_ir'), dict):
        projected['canonical_summary_ir'] = copy.deepcopy(analiz_sonucu.get('canonical_summary_ir'))
    if 'summary_consistency_audit' in analiz_sonucu and isinstance(analiz_sonucu.get('summary_consistency_audit'), dict):
        projected['summary_consistency_audit'] = copy.deepcopy(analiz_sonucu.get('summary_consistency_audit'))

    return json.loads(json.dumps(projected, ensure_ascii=False))
