from __future__ import annotations

import os
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import app  # noqa: E402


payload = {
    "format": "pdf",
    "ozet_turu": "ayrintili",
    "yas_grubu": "",
    "dosya_yolu": r"uploads\arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf",
    "analiz_sonucu": {
        "kitap_adi": "Tavsan Pati",
        "yazar": "Ozlem Aytek",
        "dosya_adi": "arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf",
        "dosya_yolu": r"uploads\arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf",
    },
}


with app.test_client() as client:
    response = client.post("/api/tema-kazanim/rapor", json=payload)
    print("status", response.status_code)
    body = response.get_data()
    print("mimetype", response.mimetype)
    print("bytes", len(body))
    print("pdf_header", body[:5])
    if response.status_code >= 400:
        print(body.decode("utf-8", errors="replace")[:1000])
