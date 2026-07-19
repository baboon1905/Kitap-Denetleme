#!/usr/bin/env python3
"""
Orchestrator: Run full endpoint verification per benchmark book in subprocesses with timeout.
Writes per-book partial JSONs and final JSON only if all books completed.
If an existing previous runner is active, attempt to terminate it via PID lock.
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(__file__)
BOOKS = ["Tavşan Pati", "Büyülü Yastıklar", "Benim Adım Kristof Kolomb"]
TIMEOUT_SECONDS = 15 * 60
PY = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
LOCKFILE = os.path.join(ROOT, "phase9a_runner.lock")


def _kill_existing_lock():
    if os.path.exists(LOCKFILE):
        try:
            with open(LOCKFILE, 'r') as fh:
                pid = int(fh.read().strip())
        except Exception:
            pid = None
        if pid:
            try:
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except Exception:
                pass
        try:
            os.remove(LOCKFILE)
        except Exception:
            pass


def _write_lock():
    with open(LOCKFILE, 'w') as fh:
        fh.write(str(os.getpid()))


def run():
    # ensure no previous runner
    _kill_existing_lock()
    _write_lock()
    results = []
    all_ok = True
    try:
        for book in BOOKS:
            safe = book.replace(' ', '_')
            cmd = [PY, os.path.join(ROOT, 'phase9a_run_single_book.py'), book]
            start = time.time()
            try:
                proc = subprocess.run(cmd, timeout=TIMEOUT_SECONDS, capture_output=True, text=True)
                # attempt to read partial JSON written by the subprocess
                partial_path = os.path.join(ROOT, f"phase9a_recommendation_engine_verification_{safe}.json")
                if os.path.exists(partial_path):
                    with open(partial_path, 'r', encoding='utf-8') as fh:
                        part = json.load(fh)
                else:
                    # fallback to stdout parse
                    try:
                        part = json.loads(proc.stdout)
                    except Exception:
                        part = {"title": book, "error": "no_partial_output"}
                results.append(part)
            except subprocess.TimeoutExpired:
                # mark timeout; do not accept partial as final
                all_ok = False
                # try to read partial if exists
                partial_path = os.path.join(ROOT, f"phase9a_recommendation_engine_verification_{safe}.json")
                part = None
                if os.path.exists(partial_path):
                    with open(partial_path, 'r', encoding='utf-8') as fh:
                        part = json.load(fh)
                results.append({"title": book, "error": "timeout", "partial": part})
            except Exception as exc:
                all_ok = False
                results.append({"title": book, "error": str(exc)})
    finally:
        try:
            if os.path.exists(LOCKFILE):
                os.remove(LOCKFILE)
        except Exception:
            pass

    final = {"books": results, "all_ok": all_ok}
    outpath = os.path.join(ROOT, 'phase9a_recommendation_engine_verification.json')
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump(final, fh, ensure_ascii=False, indent=2)

    # commit if all_ok
    if all_ok:
        try:
            subprocess.run(["git", "add", outpath], check=False)
            subprocess.run(["git", "commit", "-m", "phase9a full endpoint verification"], check=False)
        except Exception:
            pass

    print(json.dumps({"result_file": outpath, "all_ok": all_ok}, ensure_ascii=False))


if __name__ == '__main__':
    run()
