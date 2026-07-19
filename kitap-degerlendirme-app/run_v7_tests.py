import copy
import os
import io
import json
from unittest.mock import patch

# Import app and helper
import app as flask_app_module
import theme_gain_analysis
from summary_ir import attach_summary_ir

# Test PDF (small fixture)
PDF_PATH = os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "debug_test_api_data.pdf"))
if not os.path.exists(PDF_PATH):
    raise FileNotFoundError(f"Test PDF not found: {PDF_PATH}")

adapter_target = "runtime_v7.adapter.build_v7_shadow_payload"
shadow_target = "theme_gain_analysis.build_v7_shadow_payload"


def run_scenario(v7_shadow_value, v7_summary_ir_source_value=False, simulate_adapter_error=False, use_canonical_ir_payload=None):
    os.environ['V7_SHADOW_MODE'] = "true" if v7_shadow_value else "false"
    os.environ['V7_SUMMARY_IR_SOURCE'] = "true" if v7_summary_ir_source_value else "false"
    client = flask_app_module.app.test_client()
    report = {
        "v7_shadow_mode": bool(v7_shadow_value),
        "v7_summary_ir_source": bool(v7_summary_ir_source_value),
        "analiz": {"status": None, "json": None},
        "rapor": {"status": None, "content_type": None, "json": None},
        "shadow_present_in_payload": False,
        "shadow_keys": None,
        "adapter_error_flag": None,
        "canonical_summary_ir_used": None,
        "summary_ir_source_function": None,
        "summary_ir_source_active": False,
    }

    captured = {}

    def fake_build_pdf_report(payload):
        captured['payload'] = dict(payload or {})
        return io.BytesIO(b"%PDF-1.4\n%fake-pdf\n")

    with patch.object(flask_app_module, "build_theme_pdf_report", side_effect=fake_build_pdf_report):
        if simulate_adapter_error:
            with patch(shadow_target, side_effect=Exception("adapter failure for test")):
                payload_for_rapor = _do_calls(client, report, captured, use_canonical_ir_payload)
        else:
            payload_for_rapor = _do_calls(client, report, captured, use_canonical_ir_payload)

    payload = captured.get('payload') or {}
    report["payload"] = copy.deepcopy(payload)
    report["endpoint_payload_captured"] = bool(payload)
    shadow = payload.get("_runtime_v7_shadow")
    report["shadow_present_in_payload"] = bool(shadow)
    report["shadow_keys"] = sorted(shadow.keys()) if isinstance(shadow, dict) else None
    if isinstance(shadow, dict):
        diag = shadow.get("diagnostics") or {}
        report["adapter_error_flag"] = bool(diag.get("adapter_error") is True or diag.get("adapter_error"))
    else:
        report["adapter_error_flag"] = None

    report["direct_payload"] = _build_direct_report_payload(payload_for_rapor, simulate_adapter_error)
    direct_shadow = report["direct_payload"].get("_runtime_v7_shadow") if isinstance(report["direct_payload"], dict) else None
    report["direct_shadow_present_in_payload"] = bool(direct_shadow)
    report["direct_shadow_keys"] = sorted(direct_shadow.keys()) if isinstance(direct_shadow, dict) else None
    if isinstance(direct_shadow, dict):
        diag = direct_shadow.get("diagnostics") or {}
        report["direct_adapter_error_flag"] = bool(diag.get("adapter_error") is True or diag.get("adapter_error"))
    else:
        report["direct_adapter_error_flag"] = None

    canonical_ir = payload.get("canonical_summary_ir")
    if isinstance(canonical_ir, dict):
        audit = payload.get("summary_consistency_audit") or {}
        report["canonical_summary_ir_used"] = {
            "summary_source_function": audit.get("summary_source_function"),
            "canonical_summary": payload.get("canonical_summary"),
            "canonical_summary_ir_hash": payload.get("canonical_summary_ir_hash"),
            "canonical_summary_flag_ok": audit.get("summary_source_function") == "canonical_summary_ir",
        }
        report["summary_ir_source_function"] = audit.get("summary_source_function")
        report["summary_ir_source_active"] = audit.get("summary_source_function") == "canonical_summary_ir"
        required_summary_surface_keys = {
            "canonical_summary",
            "kitap_ozeti",
            "book_summary",
            "ozet",
            "summary",
            "summary_pdf",
            "summary_ui",
            "teacher_summary",
            "summary_before_gate",
            "summary_after_gate",
            "summary_rendered_to_ui",
            "summary_used_for_pdf",
            "summary_before_quality_gate",
            "summary_after_quality_gate",
        }
        present_keys = set(payload.keys())
        missing_keys = sorted(required_summary_surface_keys - present_keys)
        report["summary_ir_source_surface_keys"] = sorted(required_summary_surface_keys & present_keys)
        report["summary_ir_source_missing_surfaces"] = missing_keys
        report["summary_ir_source_has_all_surface_keys"] = not bool(missing_keys)
    else:
        report["canonical_summary_ir_used"] = False
        report["summary_ir_source_active"] = False
        report["summary_ir_source_surface_keys"] = []
        report["summary_ir_source_missing_surfaces"] = []
        report["summary_ir_source_has_all_surface_keys"] = False

    # attach statuses from calls
    return report


def _do_calls(client, report, captured, use_canonical_ir_payload):
    # 1) /api/tema-kazanim/analiz
    resp_analiz = client.post("/api/tema-kazanim/analiz", json={"dosya_yolu": PDF_PATH})
    report["analiz"]["status"] = resp_analiz.status_code
    try:
        report["analiz"]["json"] = resp_analiz.get_json()
    except Exception:
        report["analiz"]["json"] = None

    # Prepare rapor payload
    if use_canonical_ir_payload is None:
        analiz_sonucu = (report["analiz"]["json"] or {}).get("analiz_sonucu") or {}
        payload_for_rapor = {"analiz_sonucu": analiz_sonucu, "format": "pdf"}
    elif use_canonical_ir_payload is True:
        minimal = {"kitap_adi": "tiny book", "ana_karakterler": [], "ilk_uc_baskin_tema": []}
        augmented = attach_summary_ir(minimal, "test-stage")
        payload_for_rapor = {"analiz_sonucu": augmented, "format": "pdf"}
    else:
        payload_for_rapor = {"analiz_sonucu": use_canonical_ir_payload, "format": "pdf"}

    resp_rapor = client.post("/api/tema-kazanim/rapor", json=payload_for_rapor)
    report["rapor"]["status"] = resp_rapor.status_code
    report["rapor"]["content_type"] = resp_rapor.content_type
    try:
        report["rapor"]["json"] = resp_rapor.get_json()
    except Exception:
        report["rapor"]["json"] = None

    return payload_for_rapor


def _extract_report_input(payload_for_rapor: dict) -> dict:
    if not isinstance(payload_for_rapor, dict):
        return {}
    if "analiz_sonucu" in payload_for_rapor:
        return payload_for_rapor.get("analiz_sonucu") or {}
    return payload_for_rapor


def _build_direct_report_payload(payload_for_rapor: dict, simulate_adapter_error: bool = False) -> dict:
    direct_payload_input = _extract_report_input(payload_for_rapor)
    if simulate_adapter_error:
        with patch(shadow_target, side_effect=Exception("adapter failure for test")):
            return theme_gain_analysis.prepare_theme_report_payload(direct_payload_input)
    return theme_gain_analysis.prepare_theme_report_payload(direct_payload_input)


def _collect_diff_paths(a: object, b: object, path: str = "") -> set[str]:
    paths: set[str] = set()
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a.keys()) | set(b.keys())):
            child_path = f"{path}.{key}" if path else key
            if key not in a or key not in b:
                paths.add(child_path)
                continue
            paths |= _collect_diff_paths(a[key], b[key], child_path)
        return paths

    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            paths.add(path)
            return paths
        for index, (item_a, item_b) in enumerate(zip(a, b)):
            paths |= _collect_diff_paths(item_a, item_b, f"{path}[{index}]")
        return paths

    if a != b:
        paths.add(path)
    return paths


def _normalize_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {}
    normalized = copy.deepcopy(payload)
    normalized.pop("_runtime_v7_shadow", None)
    normalized.pop("canonical_summary_ir", None)
    normalized.pop("canonical_summary_ir_hash", None)

    audit = normalized.get("summary_consistency_audit")
    if isinstance(audit, dict):
        audit = dict(audit)
        audit.pop("summary_ir_version", None)
        audit.pop("canonical_summary_ir_hash", None)
        if audit:
            normalized["summary_consistency_audit"] = audit
        else:
            normalized.pop("summary_consistency_audit", None)

    return normalized


def compare_shadow_payloads(false_payload: dict, true_payload: dict) -> dict:
    false_norm = _normalize_payload(false_payload)
    true_norm = _normalize_payload(true_payload)
    diff_paths = sorted(_collect_diff_paths(false_norm, true_norm))
    return {
        "false_has_shadow": bool(false_payload.get("_runtime_v7_shadow")),
        "true_has_shadow": bool(true_payload.get("_runtime_v7_shadow")),
        "shadow_keys_false": sorted(false_payload.get("_runtime_v7_shadow", {}).keys()) if isinstance(false_payload.get("_runtime_v7_shadow"), dict) else None,
        "shadow_keys_true": sorted(true_payload.get("_runtime_v7_shadow", {}).keys()) if isinstance(true_payload.get("_runtime_v7_shadow"), dict) else None,
        "diff_keys": sorted(set(true_norm.keys()) ^ set(false_norm.keys())),
        "diff_paths": diff_paths,
        "equal_without_shadow": not diff_paths,
    }


if __name__ == "__main__":
    final = {}
    final["cases"] = []
    final["cases"].append(run_scenario(False, v7_summary_ir_source_value=False, simulate_adapter_error=False))
    final["cases"].append(run_scenario(True, v7_summary_ir_source_value=False, simulate_adapter_error=False))
    final["cases"].append(run_scenario(False, v7_summary_ir_source_value=True, simulate_adapter_error=False))
    final["cases"].append(run_scenario(True, v7_summary_ir_source_value=True, simulate_adapter_error=False))
    final["adapter_error_case"] = run_scenario(True, v7_summary_ir_source_value=False, simulate_adapter_error=True)
    final["canonical_summary_ir_case"] = run_scenario(False, v7_summary_ir_source_value=False, simulate_adapter_error=False, use_canonical_ir_payload=True)

    # PHASE 2 diff assertion between shadow off/on payloads when summary IR source is disabled
    false_case_payload = None
    true_case_payload = None
    for case in final["cases"]:
        if case["v7_shadow_mode"] is False and case["v7_summary_ir_source"] is False:
            false_case_payload = case
        elif case["v7_shadow_mode"] is True and case["v7_summary_ir_source"] is False:
            true_case_payload = case

    final["payload_diff_assertion"] = {
        "false_has_shadow": false_case_payload["shadow_present_in_payload"] if false_case_payload else None,
        "true_has_shadow": true_case_payload["shadow_present_in_payload"] if true_case_payload else None,
        "shadow_keys_true": true_case_payload["shadow_keys"] if true_case_payload else None,
        "equal_without_shadow": None,
    }

    if false_case_payload and true_case_payload:
        false_payload = false_case_payload.get("direct_payload") or {}
        true_payload = true_case_payload.get("direct_payload") or {}
        final["payload_diff_assertion"] = compare_shadow_payloads(
            false_payload,
            true_payload,
        )
        final["payload_diff_assertion"]["source"] = "direct_prepare_theme_report_payload"

    final["summary_ir_source_cases"] = [
        case for case in final["cases"] if case["v7_summary_ir_source"] is True
    ]
    final["summary_ir_source_assertion"] = {
        "true_cases_have_source_active": all(
            case.get("summary_ir_source_active") is True for case in final["summary_ir_source_cases"]
        ),
        "true_cases_have_canonical_summary_ir": all(
            bool(case.get("payload", {}).get("canonical_summary_ir")) for case in final["summary_ir_source_cases"]
        ),
        "true_cases_have_complete_surface_keys": all(
            case.get("summary_ir_source_has_all_surface_keys") is True for case in final["summary_ir_source_cases"]
        ),
        "true_cases_endpoint_status_ok": all(
            case.get("rapor", {}).get("status") == 200 for case in final["summary_ir_source_cases"]
        ),
        "false_phase2_output_same": bool(final.get("payload_diff_assertion", {}).get("equal_without_shadow") is True),
    }

    print(json.dumps(final, ensure_ascii=False, indent=2))
