import os
import json
import traceback
from pprint import pprint

os.environ['V7_SUMMARY_IR_SOURCE'] = 'true'

from app import app
from theme_gain_analysis import (
    prepare_theme_report_payload,
    build_pdf_report,
    build_teacher_report_payload,
    build_word_report,
    rapor_kalite_kapisi,
)

PDF_PATH = os.path.join(app.root_path, "uploads", "arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf")


def safe_call(name, func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        print(f"[{name}] success")
        return True, result
    except Exception as exc:
        print(f"[{name}] exception: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        return False, exc


def print_summary_fields(prefix, payload):
    excerpt = {
        "canonical_summary": payload.get("canonical_summary"),
        "summary_ui": payload.get("summary_ui"),
        "summary_pdf": payload.get("summary_pdf"),
        "teacher_summary": payload.get("teacher_summary"),
        "canonical_summary_ir_hash": payload.get("canonical_summary_ir_hash"),
        "summary_consistency_audit": payload.get("summary_consistency_audit"),
        "ozet_kalite_kontrol": payload.get("ozet_kalite_kontrol"),
    }
    print(f"--- {prefix} payload excerpt ---")
    pprint(excerpt, width=180)
    print("--- end excerpt ---\n")


def print_quality_gate_info(prepared):
    print("--- quality gate info ---")
    gate = rapor_kalite_kapisi(prepared)
    pprint({
        "gecerli": gate.get("gecerli"),
        "durum": gate.get("durum"),
        "kod": gate.get("kod"),
        "hatalar": gate.get("hatalar"),
        "mojibake_detected": gate.get("mojibake_detected"),
        "mojibake_issues": gate.get("mojibake_issues"),
        "karakter_kalitesi": gate.get("karakter_kalitesi"),
        "dil_kalitesi": gate.get("dil_kalitesi"),
    }, width=180)
    print("--- end quality gate info ---\n")
    return gate


def main():
    client = app.test_client()
    print("[debug] requesting /api/tema-kazanim/analiz for Tavşan Pati")
    response = client.post("/api/tema-kazanim/analiz", json={"dosya_yolu": PDF_PATH})
    print("status_code:", response.status_code)
    try:
        payload = response.get_json()
    except Exception:
        payload = None
    print("response keys:", sorted(payload.keys()) if isinstance(payload, dict) else payload)
    print()

    if response.status_code != 200:
        print("ANALIZ FAILED")
        pprint(payload)
        return

    print_summary_fields("analysis output", payload)

    print("[debug] calling prepare_theme_report_payload")
    ok, prepared = safe_call("prepare_theme_report_payload", prepare_theme_report_payload, payload)
    if not ok:
        return

    print_summary_fields("prepared", prepared)

    print("[debug] calling rapor_kalite_kapisi on prepared payload")
    gate = rapor_kalite_kapisi(prepared)
    pprint({
        "gecerli": gate.get("gecerli"),
        "durum": gate.get("durum"),
        "kod": gate.get("kod"),
        "hatalar": gate.get("hatalar"),
    }, width=180)
    print()

    print("[debug] calling build_teacher_report_payload")
    ok_teacher, teacher_payload = safe_call("build_teacher_report_payload", build_teacher_report_payload, prepared)
    if ok_teacher:
        print_summary_fields("teacher_payload", teacher_payload)
        print("teacher_summary_source_function:", (teacher_payload.get("summary_consistency_audit") or {}).get("summary_source_function"))

    print("[debug] calling build_pdf_report")
    ok_pdf, pdf_result = safe_call("build_pdf_report", build_pdf_report, prepared)
    if ok_pdf:
        print("build_pdf_report returned BytesIO len", len(pdf_result.getvalue()))

    print("[debug] calling build_word_report")
    ok_word, word_result = safe_call("build_word_report", build_word_report, prepared)
    if ok_word:
        print("build_word_report returned BytesIO len", len(word_result.getvalue()))

    if not ok_pdf or not ok_word:
        print("--- final payload quality fields ---")
        print("summary_source_function:", (prepared.get("ozet_kalite_kontrol") or {}).get("summary_source_function"))
        print("canonical_summary_ir_hash:", prepared.get("canonical_summary_ir_hash"))
        print("summary_consistency_audit:", prepared.get("summary_consistency_audit"))
        print("ozet_kalite_kontrol:", prepared.get("ozet_kalite_kontrol"))


if __name__ == '__main__':
    main()
