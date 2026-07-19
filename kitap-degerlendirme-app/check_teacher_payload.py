from __future__ import annotations

import json
import os
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

from theme_gain_analysis import build_teacher_report_payload  # noqa: E402


with open(os.path.join(BASE_DIR, "runtime_1_analyze_theme_gain_return.json"), "r", encoding="utf-8") as handle:
    result = json.load(handle)

payload = build_teacher_report_payload(result)
text = json.dumps(payload, ensure_ascii=False)
fantasy_terms = ["fantastik", "kurmaca dünya", "fantastik mekân", "fantastik mekan"]

print("book_type", payload.get("book_type"))
print("ana_tema", payload.get("ana_tema"))
print("theme_count", len(payload.get("temalar") or []))
print("fantasy_mentions", sum(text.lower().count(term) for term in fantasy_terms))
print("activities", len(payload.get("kitaba_ozel_etkinlikler") or []))
print("courses", len(payload.get("kullanilabilecek_dersler") or []))
