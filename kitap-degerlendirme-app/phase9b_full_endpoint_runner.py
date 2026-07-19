#!/usr/bin/env python3
"""
Orchestrator for Phase 9B: run each benchmark via subprocess with 15-minute timeout.
Writes per-book partials and final JSON only if all three succeed.
"""
import json
import os
import subprocess
import time

ROOT = os.path.dirname(__file__)
BOOKS = ["Tavşan Pati", "Büyülü Yastıklar", "Benim Adım Kristof Kolomb"]
TIMEOUT_SECONDS = 15 * 60
PY = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")


def run():
    results = []
    all_ok = True
    for book in BOOKS:
        safe = book.replace(' ', '_')
        cmd = [PY, os.path.join(ROOT, 'phase9b_run_single_book.py'), book]
        try:
            subprocess.run(cmd, timeout=TIMEOUT_SECONDS, check=False)
            partial_path = os.path.join(ROOT, f"phase9b_promotion_readiness_verification_{safe}.json")
            if os.path.exists(partial_path):
                with open(partial_path, 'r', encoding='utf-8') as fh:
                    part = json.load(fh)
            else:
                part = {"title": book, "error": "no_partial_output"}
            # basic validation
            ok = part.get('diagnostics_ok') and part.get('components_ok') and part.get('checks', {}).get('equal_without_shadow')
            if not ok:
                all_ok = False
            results.append(part)
        except subprocess.TimeoutExpired:
            all_ok = False
            partial_path = os.path.join(ROOT, f"phase9b_promotion_readiness_verification_{safe}.json")
            part = None
            if os.path.exists(partial_path):
                with open(partial_path, 'r', encoding='utf-8') as fh:
                    part = json.load(fh)
            results.append({"title": book, "error": "timeout", "partial": part})
        except Exception as exc:
            all_ok = False
            results.append({"title": book, "error": str(exc)})

    final = {"books": results, "all_ok": all_ok}
    outpath = os.path.join(ROOT, 'phase9b_promotion_readiness_verification.json')
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump(final, fh, ensure_ascii=False, indent=2)

    if all_ok:
        try:
            subprocess.run(["git", "add", outpath], check=False)
            subprocess.run(["git", "commit", "-m", "phase9b full endpoint verification"], check=False)
        except Exception:
            pass

    print(json.dumps({"result_file": outpath, "all_ok": all_ok}, ensure_ascii=False))


if __name__ == '__main__':
    run()
