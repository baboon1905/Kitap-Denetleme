import os, sys, io, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app as flask_app

BOOKS = {
    'Tavşan Pati': 'uploads/arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf',
    'Büyülü Yastıklar': 'uploads/buyulu_yastiklar.pdf',
    'Benim Adım Kristof Kolomb': 'uploads/benim_adim_kristof_kolomb.pdf',
}

client = flask_app.test_client()
for name, path in BOOKS.items():
    full = os.path.abspath(path)
    print('Calling analysis for', name, full)
    resp = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': full})
    print('Status', resp.status_code)
    try:
        payload = resp.get_json()
    except Exception as e:
        payload = {'error': str(e)}
    out = os.path.join('outputs', f'analysis_{name.replace(" ","_")}.json')
    os.makedirs('outputs', exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print('Wrote', out)
