"""
Runtime JSON kanitlarini karsilastirir.

Bu script hardcoded test metni calistirmaz. Gercek /api/tema-kazanim/rapor
akisi tarafindan uretilen runtime_*.json dosyalarini okur.
"""

from __future__ import annotations

import json
import os


RUNTIME_FILES = [
    "runtime_1_analyze_theme_gain_return.json",
    "runtime_2_build_pdf_report_input.json",
    "runtime_3_pdf_template_final_payload.json",
    "runtime_theme_final_selection_debug.json",
]

CORE_FIELDS = [
    "ana_tema",
    "tema_analizi",
    "deger_analizi",
    "kazanim_analizi",
    "ana_karakterler",
    "book_type",
    "book_subtype",
]


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _summary_value(value):
    if isinstance(value, list):
        return f"{len(value)} item"
    return repr(value)


def main() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    loaded = {}

    print("=" * 80)
    print("RUNTIME JSON DUMP KARSILASTIRMA")
    print("=" * 80)
    for filename in RUNTIME_FILES:
        path = os.path.join(base_dir, filename)
        if not os.path.exists(path):
            print(f"EKSIk: {filename}")
            continue
        loaded[filename] = _load_json(path)
        print(f"OK: {filename}")

    stage1 = loaded.get("runtime_1_analyze_theme_gain_return.json") or {}
    stage2 = loaded.get("runtime_2_build_pdf_report_input.json") or {}
    stage3 = loaded.get("runtime_3_pdf_template_final_payload.json") or {}

    print("\n" + "=" * 80)
    print("CORE FIELD KARSILASTIRMA")
    print("=" * 80)
    for key in CORE_FIELDS:
        v1 = stage1.get(key)
        v2 = stage2.get(key)
        v3 = stage3.get(key)
        print(
            f"{key}: "
            f"analyze={_summary_value(v1)} | "
            f"build_input={_summary_value(v2)} | "
            f"final_payload={_summary_value(v3)} | "
            f"analyze==build_input={v1 == v2}"
        )

    theme_debug = loaded.get("runtime_theme_final_selection_debug.json") or {}
    print("\n" + "=" * 80)
    print("TEMA FINAL KARARI")
    print("=" * 80)
    print(theme_debug.get("ana_tema_karar_gerekcesi", "Tema karar debug dosyasi yok."))


if __name__ == "__main__":
    main()
