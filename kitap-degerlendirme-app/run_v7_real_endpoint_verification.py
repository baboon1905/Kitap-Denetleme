from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from pipeline_runtime_enforcer import regression_fail_rules, verify_summary_hash_consistency  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent

ENDPOINT = os.environ.get("V7_ENDPOINT", "http://127.0.0.1:5000/api/tema-kazanim/rapor")
HTTP_TIMEOUT_SECONDS = int(os.environ.get("V7_ENDPOINT_TIMEOUT", "600"))
FORBIDDEN_PHASE1_MARKERS = [
    "Bu okuma",
    "Sonuç olarak",
    "Sonuc olarak",
    "Olay akışı",
    "Olay akisi",
    "somut bir karar uygulamak",
    "çözüme yarayan bilgi bulmak",
    "cozume yarayan bilgi bulmak",
]

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
        path = SCRIPT_DIR / name
        if not path.exists():
            path = Path(name)
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8-sig"))
            except json.JSONDecodeError as exc:
                print(f"WARNING: failed to parse {path}: {exc}")
                continue
    return {}


def _post_json(payload: dict) -> tuple[int, str, bytes]:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT,
        data=raw,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            return response.status, response.headers.get("Content-Type", ""), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers.get("Content-Type", ""), exc.read()


def verify_case(case: dict) -> dict:
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
    status, content_type, body = _post_json(payload)
    runtime_payload = _load_latest_payload()
    summary = str(runtime_payload.get("kitap_ozeti") or runtime_payload.get("summary") or "")
    summary_ir = runtime_payload.get("canonical_summary_ir") or {}
    evidence = [
        str(item or "").strip()
        for item in (summary_ir.get("evidence") or [])
        if isinstance(item, str) and len(str(item).split()) >= 5
    ]
    copied_evidence_count = sum(1 for item in evidence if item and item in summary)
    forbidden_markers = [marker for marker in FORBIDDEN_PHASE1_MARKERS if marker in summary]
    hash_check = verify_summary_hash_consistency(runtime_payload)
    failures = regression_fail_rules(runtime_payload)
    row = {
        "title": case["title"],
        "status": status,
        "content_type": content_type,
        "bytes": len(body),
        "summary_word_count": len(summary.split()),
        "summary_ir_hash": runtime_payload.get("canonical_summary_ir_hash"),
        "checked_summary_hash": runtime_payload.get("checked_summary_hash"),
        "rendered_summary_hash": runtime_payload.get("rendered_summary_hash"),
        "ui_summary_hash": runtime_payload.get("ui_summary_hash"),
        "pdf_summary_hash": runtime_payload.get("pdf_summary_hash"),
        "teacher_summary_hash": runtime_payload.get("teacher_summary_hash"),
        "hash_consistency": hash_check.get("hash_consistency_pass", False),
        "generic_event_ratio": runtime_payload.get("generic_event_ratio"),
        "raw_generic_event_ratio": runtime_payload.get("raw_generic_event_ratio"),
        "canonical_event_count": runtime_payload.get("canonical_event_count"),
        "central_entity_resolver_version": runtime_payload.get("central_entity_resolver_version"),
        "summary_ir_version": summary_ir.get("version"),
        "has_story_arc": bool(summary_ir.get("story_arc")),
        "has_event_sequence": bool(summary_ir.get("event_sequence")),
        "has_event_importance": bool(summary_ir.get("event_importance")),
        "forbidden_phase1_markers": forbidden_markers,
        "copied_evidence_count": copied_evidence_count,
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
    assert status == 200, row
    assert "pdf" in content_type.lower(), row
    assert len(body) > 1000, row
    assert row["summary_word_count"] >= 70, row
    assert row["summary_word_count"] != 17, row
    assert row["hash_consistency"], row
    assert row["has_story_arc"], row
    assert row["has_event_sequence"], row
    assert row["has_event_importance"], row
    assert not row["forbidden_phase1_markers"], row
    assert row["copied_evidence_count"] <= 1, row
    assert not hard_failures, row
    return row


if __name__ == "__main__":
    selected = " ".join(sys.argv[1:]).casefold().strip()
    cases = [
        case for case in CASES
        if not selected or selected in case["title"].casefold()
    ]
    rows = [verify_case(case) for case in cases]
    print(json.dumps({"passed": True, "endpoint": ENDPOINT, "rows": rows}, ensure_ascii=False, indent=2))
