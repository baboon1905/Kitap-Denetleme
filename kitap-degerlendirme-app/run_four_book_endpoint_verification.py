from __future__ import annotations

import json
import os
import sys
import contextlib
import io
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import app  # noqa: E402
from pipeline_runtime_enforcer import regression_fail_rules, verify_summary_hash_consistency  # noqa: E402


CASES = [
    {
        "title": "Tavsan Pati",
        "author": "Ozlem Aytek",
        "path": r"uploads\arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf",
    },
    {
        "title": "Buyulu Yastiklar",
        "author": "Test",
        "path": r"uploads\buyulu_yastiklar.pdf",
    },
    {
        "title": "Benim Adim Kristof Kolomb",
        "author": "Test",
        "path": r"uploads\benim_adim_kristof_kolomb.pdf",
    },
    {
        "title": "Gokyuzunu Kaybeden Sehir",
        "author": "Test",
        "path": r"uploads\gokyuzunu_kaybeden_sehir.pdf",
    },
]


def _load_latest_payload() -> dict:
    for name in [
        "runtime_3_pdf_template_final_payload.json",
        "runtime_2_build_pdf_report_input.json",
        "runtime_1_analyze_theme_gain_return.json",
    ]:
        path = Path(name)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _blacklisted_count(payload: dict) -> int:
    failures = regression_fail_rules(payload)
    return sum(1 for item in failures if item.startswith("BLACKLISTED_CENTRAL_ENTITY_COUNT"))


def verify_case(client, case: dict) -> dict:
    payload = {
        "format": "pdf",
        "ozet_turu": "ayrintili",
        "yas_grubu": "9-12",
        "dosya_yolu": case["path"],
        "analiz_sonucu": {
            "kitap_adi": case["title"],
            "yazar": case["author"],
            "dosya_adi": os.path.basename(case["path"]),
            "dosya_yolu": case["path"],
        },
    }
    with contextlib.redirect_stdout(io.StringIO()):
        response = client.post("/api/tema-kazanim/rapor", json=payload)
    runtime_payload = _load_latest_payload()
    summary = str(runtime_payload.get("kitap_ozeti") or runtime_payload.get("summary") or "")
    hash_ok = verify_summary_hash_consistency(runtime_payload).get("hash_consistency_pass", False)
    failures = regression_fail_rules(runtime_payload)
    row = {
        "title": case["title"],
        "status": response.status_code,
        "mimetype": response.mimetype,
        "bytes": len(response.get_data()),
        "summary_word_count": len(summary.split()),
        "generic_event_ratio": runtime_payload.get("generic_event_ratio"),
        "raw_generic_event_ratio": runtime_payload.get("raw_generic_event_ratio"),
        "canonical_event_count": runtime_payload.get("canonical_event_count"),
        "blacklisted_central_entity_count": _blacklisted_count(runtime_payload),
        "hash_consistency": hash_ok,
        "failures": failures,
    }
    hard_failures = [
        item for item in failures
        if item.startswith((
            "SUMMARY_17_WORD_FALLBACK_WITH_HIGH_THEME",
            "GENERIC_EVENT_RATIO_GT_30",
            "BLACKLISTED_CENTRAL_ENTITY_COUNT",
            "CHECKED_RENDERED_SUMMARY_HASH_MISMATCH",
            "TEACHER_SUMMARY_FALLBACK_WITH_STRONG_THEME",
        ))
    ]
    assert response.status_code == 200, row
    assert response.mimetype == "application/pdf", row
    assert row["bytes"] > 1000, row
    assert not hard_failures, row
    assert hash_ok, row
    return row


if __name__ == "__main__":
    rows = []
    with app.test_client() as client:
        for case in CASES:
            rows.append(verify_case(client, case))
    print(json.dumps({"passed": True, "rows": rows}, ensure_ascii=False, indent=2))
