import json
import unittest
from pathlib import Path

from quality_regression_dataset import QUALITY_REGRESSION_CASES
from theme_gain_analysis import (
    _editorial_evidence_valid,
    _fold_text,
    _normalize_character_identity,
    analyze_theme_gain,
    prepare_theme_report_payload,
)


def _main_character_name(result: dict) -> str:
    prepared = prepare_theme_report_payload(result)
    for character in prepared.get("ana_karakterler", []):
        if character.get("ana_karakter_mi"):
            return character.get("ad") or ""
    return ""


def _folded_names(items):
    return [_fold_text(item.get("ad") or item.get("profil") or "") for item in items or []]


class V64FinalQualityImprovementsTest(unittest.TestCase):
    def test_p1_bay_lemoncello_main_character_is_kyle_not_miguel(self):
        case = QUALITY_REGRESSION_CASES[0]
        result = analyze_theme_gain(case.text, {"baslik": case.title, "yazar": case.author}, "9-12", "standart")
        self.assertEqual(_main_character_name(result), "Kyle Keeley", result.get("ana_karakterler"))

    def test_p2_theme_evidence_editorial_gate_rejects_non_supporting_dayanisma(self):
        bad = "Bir cocuk yardim istedi ama mahalle birlikte hareket etmedi; dayanisma davranisi gosterilmedi."
        good = "Kyle ve Akimi birlikte gorev bolustu, Miguel'e destek oldu ve son ipucunu ortak kararla paylasti."

        self.assertFalse(_editorial_evidence_valid("dayanisma", bad, ["yardim"], "tema"))
        self.assertTrue(_editorial_evidence_valid("dayanisma", good, ["birlikte", "destek"], "tema"))

    def test_p3_gain_evidence_directly_supports_value_awareness(self):
        bad = "Durustluk kelimesi sinif panosunda yaziyordu ama karakter davranisi anlatilmadi."
        good = "Kyle haksizligi fark etti, dogru davranisi secti ve hatasini itiraf etti."

        self.assertFalse(_editorial_evidence_valid("degerleri fark etme", bad, ["durust"], "kazanim"))
        self.assertTrue(_editorial_evidence_valid("degerleri fark etme", good, ["dogru"], "kazanim"))

    def test_p4_character_canonicalization_merges_haley_variants(self):
        self.assertEqual(_normalize_character_identity("Haley Daley Turtle"), "Haley Daley")
        characters = prepare_theme_report_payload({
            "kitap_adi": "Canonical Test",
            "ana_karakterler": [
                {"ad": "Haley Daley", "gecis_sayisi": 2, "sayfa_sayisi": 2, "ana_karakter_puani": 60},
                {"ad": "Haley Daley Turtle", "gecis_sayisi": 3, "sayfa_sayisi": 3, "ana_karakter_puani": 62},
            ],
        })["ana_karakterler"]
        names = [item["ad"] for item in characters]
        self.assertEqual(names, ["Haley Daley"], names)
        self.assertGreaterEqual(characters[0].get("gecis_sayisi", 0), 3, characters)

    def test_p5_twenty_book_quality_regression_dataset_generates_accuracy_report(self):
        rows = []
        exact_main_character = 0
        theme_hits = 0
        book_type_hits = 0
        gain_hits = 0

        for case in QUALITY_REGRESSION_CASES:
            result = analyze_theme_gain(case.text, {"baslik": case.title, "yazar": case.author}, "9-12", "standart")
            prepared = prepare_theme_report_payload(result)
            main_character = _main_character_name(prepared)
            themes = _folded_names(prepared.get("tema_analizi"))
            gains = _folded_names(prepared.get("kazanim_analizi"))
            expected_theme = _fold_text(case.expected_main_theme)
            expected_type = _fold_text(case.expected_book_type)
            book_type = _fold_text(prepared.get("book_type") or "")
            expected_gains = [_fold_text(item) for item in case.expected_top_gains]

            main_ok = _fold_text(main_character) == _fold_text(case.expected_main_character)
            theme_ok = expected_theme in themes[:3] or bool(themes and expected_theme in themes[0])
            type_ok = expected_type in book_type
            gain_ok = any(expected in gains[:5] for expected in expected_gains)

            exact_main_character += int(main_ok)
            theme_hits += int(theme_ok)
            book_type_hits += int(type_ok)
            gain_hits += int(gain_ok)
            rows.append({
                "case_id": case.case_id,
                "main_character_ok": main_ok,
                "theme_ok": theme_ok,
                "book_type_ok": type_ok,
                "gain_ok": gain_ok,
                "actual_main_character": main_character,
                "actual_main_theme": prepared.get("ana_tema"),
                "actual_book_type": prepared.get("book_type"),
                "actual_gains": [item.get("ad") for item in prepared.get("kazanim_analizi", [])[:5]],
            })

        total = len(QUALITY_REGRESSION_CASES)
        report = {
            "total_cases": total,
            "main_character_accuracy": round(exact_main_character / total, 2),
            "theme_accuracy": round(theme_hits / total, 2),
            "book_type_accuracy": round(book_type_hits / total, 2),
            "gain_accuracy": round(gain_hits / total, 2),
            "rows": rows,
        }
        Path("quality_regression_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

        lemoncello = rows[0]
        self.assertTrue(lemoncello["main_character_ok"], lemoncello)
        self.assertGreaterEqual(report["main_character_accuracy"], 0.70, report)
        self.assertIn("theme_accuracy", report)
        self.assertIn("book_type_accuracy", report)
        self.assertIn("gain_accuracy", report)
        self.assertEqual(len(report["rows"]), 20)


if __name__ == "__main__":
    unittest.main()
