import os
import sys
from pathlib import Path
from pdf_processor import PDFProcessor
from theme_gain_analysis import analyze_theme_gain, prepare_theme_report_payload, _select_report_summary
from summary_ir import render_summary_ir, attach_summary_ir
from runtime_v7.summary_surface import sync_summary_surfaces_from_ir

os.environ['V7_SUMMARY_IR_SOURCE'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'

path = Path('uploads') / 'buyulu_yastiklar.pdf'
print('exists', path.exists())
proc = PDFProcessor(str(path))
text = proc.extract_text()
metadata = proc.extract_metadata()
metadata.update({'dosya_adi': path.name, 'dosya_yolu': str(path), 'kitap_adi': 'Büyülü Yastıklar'})

result = analyze_theme_gain(text, metadata, '9-12', 'standart')
prepared = prepare_theme_report_payload(result)
summary = _select_report_summary(prepared)
print('selected len', len(summary))
print('selected contains forbidden', 'karabasan sorununa karsi cozum arayisi belirginlesir' in summary.lower())
print('summary ui contains', 'karabasan sorununa karsi cozum arayisi belirginlesir' in str(prepared.get('summary_ui') or '').lower())
print('canonical_summary', repr(prepared.get('canonical_summary')[:500]))
print('summary_ui', repr(prepared.get('summary_ui')[:500]))
print('teacher_summary', repr(prepared.get('teacher_summary')[:500]))
print('canonical_summary_ir_hash', prepared.get('canonical_summary_ir_hash'))
print('summary_source_function', prepared.get('ozet_kalite_kontrol', {}).get('summary_source_function'))

from app import app
from theme_gain_analysis import rapor_kalite_kapisi

print('quality gate pass', rapor_kalite_kapisi(prepared).get('gecerli'))
with app.test_client() as client:
    analiz_resp = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': str(path), 'ozet_turu': 'standart', 'yas_grubu': '9-12'})
    print('analiz status', analiz_resp.status_code)
    analiz_json = analiz_resp.get_json(silent=True)
    print('analiz keys', list(analiz_json.keys()) if isinstance(analiz_json, dict) else 'not json')
    if isinstance(analiz_json, dict):
        print('analiz hash', analiz_json.get('analiz_sonucu', {}).get('canonical_summary_ir_hash'))
        print('analiz summary_source_function', analiz_json.get('analiz_sonucu', {}).get('ozet_kalite_kontrol', {}).get('summary_source_function'))
        print('analiz canonical_summary contains forbidden', 'karabasan sorununa karsi cozum arayisi belirginlesir' in str(analiz_json.get('analiz_sonucu', {}).get('canonical_summary', '')).lower())
    teacher_resp = client.post('/api/theme-report/teacher-pdf', json={'analiz_sonucu': analiz_json.get('analiz_sonucu') if isinstance(analiz_json, dict) else {}})
    print('teacher status', teacher_resp.status_code)
    teacher_json = teacher_resp.get_json(silent=True)
    print('teacher json', teacher_json)

# render direct IR surfaces
if isinstance(prepared.get('canonical_summary_ir'), dict):
    ir = prepared['canonical_summary_ir']
    print('render_summary_ui', repr(render_summary_ir(ir, 'ui', min_words=90)[:500]))
    print('render_summary_pdf', repr(render_summary_ir(ir, 'pdf', min_words=90)[:500]))
    print('render_summary_teacher', repr(render_summary_ir(ir, 'teacher', min_words=70)[:500]))
