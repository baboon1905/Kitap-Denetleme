import os
import io
import json
from unittest.mock import patch
import app as flask_app_module

PDFS = {
    "Tavşan Pati": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf")),
    "Büyülü Yastıklar": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "buyulu_yastiklar.pdf")),
    "Benim Adım Kristof Kolomb": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "benim_adim_kristof_kolomb.pdf")),
}


def run(title):
    client = flask_app_module.app.test_client()
    pdf_path = PDFS[title]
    resp = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': pdf_path})
    if resp.status_code != 200:
        raise RuntimeError(f'Analysis failed {title} status {resp.status_code}')
    analiz_sonucu = resp.get_json().get('analiz_sonucu') or {}

    def fake_pdf(payload):
        fake_pdf.captured = dict(payload or {})
        return io.BytesIO(b'%PDF-1.4\n%fake-pdf\n')

    os.environ['V7_SHADOW_MODE'] = 'true'
    os.environ['V7_NARRATIVE_GRAPH'] = 'true'
    outputs = []
    for i in range(2):
        fake_pdf.captured = None
        with patch.object(flask_app_module, 'build_theme_pdf_report', side_effect=fake_pdf):
            client.post('/api/tema-kazanim/rapor', json={'analiz_sonucu': analiz_sonucu, 'format': 'pdf'})
        outputs.append(fake_pdf.captured.get('_runtime_v7_shadow') if fake_pdf.captured else None)
    if outputs[0] == outputs[1]:
        print(title, 'same')
        return
    print(title, 'diff')
    s1 = json.dumps(outputs[0], sort_keys=True, ensure_ascii=False, indent=2).splitlines()
    s2 = json.dumps(outputs[1], sort_keys=True, ensure_ascii=False, indent=2).splitlines()
    import difflib
    for line in difflib.unified_diff(s1, s2, fromfile='first', tofile='second'):
        print(line)


if __name__ == '__main__':
    for title in PDFS:
        run(title)
