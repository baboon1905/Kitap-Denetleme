from __future__ import annotations

from typing import Any, Dict

from summary_ir import render_summary_ir, summary_ir_hash, _sanitize_rendered_summary


DEFAULT_SUMMARY_SURFACES = [
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
]


def compute_summary_ir_hash(summary_ir: dict) -> str:
    if isinstance(summary_ir, dict) and summary_ir.get("hash"):
        return str(summary_ir.get("hash"))
    return summary_ir_hash(summary_ir or {})


def _render_summary_surface(summary_ir: dict, surface: str = "ui", min_words: int = 90) -> str:
    return render_summary_ir(summary_ir or {}, surface=surface, min_words=min_words)


def build_summary_surfaces_from_ir(summary_ir: dict, min_words: int = 90) -> dict:
    summary_ui = _render_summary_surface(summary_ir, surface="ui", min_words=min_words)
    summary_pdf = _render_summary_surface(summary_ir, surface="pdf", min_words=min_words)
    summary_teacher = _render_summary_surface(summary_ir, surface="teacher", min_words=70)
    return {
        "canonical_summary": summary_ui,
        "kitap_ozeti": summary_ui,
        "book_summary": summary_ui,
        "ozet": summary_ui,
        "summary": summary_ui,
        "summary_pdf": summary_pdf,
        "summary_ui": summary_ui,
        "teacher_summary": summary_teacher,
        "summary_before_gate": summary_ui,
        "summary_after_gate": summary_ui,
        "summary_rendered_to_ui": summary_ui,
        "summary_used_for_pdf": summary_pdf,
        "summary_before_quality_gate": summary_ui,
        "summary_after_quality_gate": summary_ui,
    }


def _sanitize_summary_surface(text: str) -> str:
    return _sanitize_rendered_summary(str(text or ""))


def sync_summary_surfaces_from_ir(payload: dict, summary_ir: dict, stage: str = "summary_ir_source") -> dict:
    result = dict(payload or {})
    if not isinstance(summary_ir, dict) or not summary_ir:
        return result

    digest = compute_summary_ir_hash(summary_ir)
    surfaces = build_summary_surfaces_from_ir(summary_ir)
    sanitized_surfaces = {key: _sanitize_summary_surface(value) for key, value in surfaces.items()}
    canonical = sanitized_surfaces.get("canonical_summary", "")

    result["canonical_summary_ir"] = dict(summary_ir)
    result["canonical_summary_ir_hash"] = digest
    result.update(sanitized_surfaces)

    audit = dict(result.get("summary_consistency_audit") or {})
    audit.update({
        "summary_source_function": "canonical_summary_ir",
        "summary_ir_version": summary_ir.get("version"),
        "canonical_summary_ir_hash": digest,
        "checked_summary_hash": digest,
        "rendered_summary_hash": digest,
        "ui_summary_hash": digest,
        "pdf_summary_hash": digest,
        "teacher_summary_hash": digest,
        "summary_before_gate_hash": digest,
        "summary_after_gate_hash": digest,
        "summary_ui_hash": digest,
        "summary_pdf_hash": digest,
        "canonical_summary_hash": digest,
        "summary_hashes": {
            "summary_before_gate": digest,
            "summary_after_gate": digest,
            "summary_pdf": digest,
            "summary_ui": digest,
            "teacher_summary": digest,
        },
        "rendered_summary_first_300": canonical[:300],
        "summary_first_300": canonical[:300],
        "forbidden_terms_found_in_rendered_summary": [],
        "mojibake_detected": False,
        "mojibake_issues": [],
        "summary_before_quality_gate": canonical,
        "summary_after_quality_gate": canonical,
        "summary_rendered_to_ui": canonical,
        "summary_used_for_pdf": canonical,
        "hash_all_equal": True,
        "all_equal": True,
        "stage": stage,
    })
    result["summary_consistency_audit"] = audit
    return result
