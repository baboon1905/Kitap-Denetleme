import copy
import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT_DIR.parent / "tools"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(TOOLS_DIR))

import app as app_module
from project_for_reports_strict import project_analysis_preserve_evidence


def count_field_occurrences(obj, field_name):
    if isinstance(obj, dict):
        count = 0
        for k, v in obj.items():
            if k == field_name:
                count += 1
            count += count_field_occurrences(v, field_name)
        return count
    if isinstance(obj, list):
        return sum(count_field_occurrences(item, field_name) for item in obj)
    return 0


class TestReportProjectionHelper(unittest.TestCase):
    def test_pdf_and_word_preserve_prepare_required_evidence_fields(self):
        evidence = {
            "sayfa": 7,
            "alinti": "Karakter arkadaşına yardım etti.",
            "anahtarlar": ["yardımlaşma"],
            "kanit_turu": "olay_sahnesi",
            "kanit_agirligi": 0.8,
            "baglam_gucu": 4,
            "source_sentence_id": "p7:s2",
            "source_sentence_ids": ["p7:s2"],
            "projection_disinda": "taşınmamalı",
        }
        sample = {
            "kitap_adi": "Örnek",
            "tema_analizi": [{"ad": "Yardımlaşma", "kanitlar": [evidence]}],
            "event_graph": [{"kaynak_metin": "Somut olay."}],
            "olay_akisi": [{"metin": "Olay akışı."}],
            "ana_tema_kanitlari": [{"alinti": "Ana tema kanıtı."}],
            "canonical_summary": "Kanonik özet.",
            "summary": "Kanonik özet.",
            "book_summary": "Kanonik özet.",
            "ozet": "Kanonik özet.",
            "rendered_summary_hash": "abc123",
        }

        expected_fields = {
            "sayfa", "alinti", "anahtarlar", "kanit_turu",
            "kanit_agirligi", "baglam_gucu", "source_sentence_id",
            "source_sentence_ids",
        }
        for report_type in ("pdf", "word"):
            projected = app_module.project_analysis_preserve_evidence(sample, report_type)
            self.assertEqual(projected["event_graph"], sample["event_graph"])
            self.assertEqual(projected["olay_akisi"], sample["olay_akisi"])
            self.assertEqual(projected["ana_tema_kanitlari"], sample["ana_tema_kanitlari"])
            for field in (
                "canonical_summary", "summary", "book_summary", "ozet",
                "rendered_summary_hash",
            ):
                self.assertEqual(projected[field], sample[field])
            projected_evidence = projected["tema_analizi"][0]["kanitlar"][0]
            self.assertEqual(set(projected_evidence), expected_fields)
            self.assertNotIn("projection_disinda", projected_evidence)

    def test_app_imports_strict_projection_helper(self):
        self.assertTrue(callable(app_module.project_analysis_preserve_evidence))
        self.assertIs(app_module.project_analysis_preserve_evidence, project_analysis_preserve_evidence)

    def test_entity_store_graph_removed_from_projection(self):
        sample = {
            "kitap_adi": "Test Kitap",
            "yazar": "Test Yazar",
            "book_type": "roman",
            "book_subtype": "cocuk",
            "analiz_tarihi": "2026-01-01",
            "ana_tema": "Dostluk",
            "tema_analizi": [{"ad": "Dostluk", "kanitlar": [{"sayfa": 1, "alinti": "x", "source_sentence_id": 5}]}],
            "ilk_uc_baskin_tema": [],
            "guclu_temalar": [],
            "destekleyici_temalar": [],
            "temel_mesajlar": "Önemli mesaj.",
            "kazanim_analizi": [],
            "ogretmen_notu": "Not.",
            "kitap_ozeti": "Özet.",
            "entity_store_graph": {"foo": "bar"},
            "canonical_entity_store": {
                "E1": {
                    "canonical_form": "Foo",
                    "entity_type": "concept",
                    "surface_forms": ["Foo"],
                    "aliases": ["F"],
                    "pages": [1],
                    "entity_store_graph": {"bad": "data"},
                }
            },
        }

        projected = app_module.project_analysis_preserve_evidence(sample, "pdf")
        self.assertNotIn("entity_store_graph", projected)
        self.assertEqual(0, count_field_occurrences(projected, "entity_store_graph"))
        self.assertIn("canonical_entity_store", projected)
        self.assertEqual({"canonical_form": "Foo", "entity_type": "concept", "surface_forms": ["Foo"], "aliases": ["F"], "pages": [1]}, projected["canonical_entity_store"]["E1"])

    def test_teacher_projection_preserves_summary_fields_and_hashes(self):
        sample = {
            "kitap_adi": "Test Kitap",
            "yazar": "Test Yazar",
            "book_type": "roman",
            "book_subtype": "cocuk",
            "analiz_tarihi": "2026-01-01",
            "ana_tema": "Dostluk",
            "ogretmen_notu": "Not.",
            "kazanim_analizi": [],
            "kitap_ozeti": "Özet öğretmen için.",
            "canonical_summary_ir": {"version": 1, "summary": "Özet öğretmen için."},
            "summary_consistency_audit": {"summary_before_gate_hash": "abc", "summary_after_gate_hash": "def"},
            "rendered_summary": "Render edildi",
            "summary_before_gate": "Önce",
            "summary_after_gate": "Sonra",
            "summary_before_gate_hash": "hash-before",
            "summary_after_gate_hash": "hash-after",
            "summary_ui_hash": "hash-ui",
            "summary_pdf_hash": "hash-pdf",
            "rendered_summary_hash": "hash-rendered",
            "ui_summary_hash": "hash-ui-2",
            "pdf_summary_hash": "hash-pdf-2",
            "canonical_summary_hash": "hash-canonical",
            "canonical_summary_ir_hash": "hash-ir",
            "entity_store_graph": {"foo": "bar"},
        }

        original = copy.deepcopy(sample)
        projected = app_module.project_analysis_preserve_evidence(sample, "teacher")

        self.assertEqual(sample["kitap_ozeti"], projected["kitap_ozeti"])
        self.assertEqual(sample["canonical_summary_ir"], projected["canonical_summary_ir"])
        self.assertEqual(sample["summary_consistency_audit"], projected["summary_consistency_audit"])
        self.assertEqual(sample["rendered_summary"], projected["rendered_summary"])
        self.assertEqual(sample["summary_before_gate"], projected["summary_before_gate"])
        self.assertEqual(sample["summary_after_gate"], projected["summary_after_gate"])
        self.assertEqual(sample["summary_before_gate_hash"], projected["summary_before_gate_hash"])
        self.assertEqual(sample["summary_after_gate_hash"], projected["summary_after_gate_hash"])
        self.assertEqual(sample["summary_ui_hash"], projected["summary_ui_hash"])
        self.assertEqual(sample["summary_pdf_hash"], projected["summary_pdf_hash"])
        self.assertEqual(sample["rendered_summary_hash"], projected["rendered_summary_hash"])
        self.assertEqual(sample["ui_summary_hash"], projected["ui_summary_hash"])
        self.assertEqual(sample["pdf_summary_hash"], projected["pdf_summary_hash"])
        self.assertEqual(sample["canonical_summary_hash"], projected["canonical_summary_hash"])
        self.assertEqual(sample["canonical_summary_ir_hash"], projected["canonical_summary_ir_hash"])
        self.assertEqual(0, count_field_occurrences(projected, "entity_store_graph"))
        self.assertEqual(original, sample)

    def test_teacher_projection_does_not_fabricate_summary_placeholders_when_missing(self):
        sample = {
            "kitap_adi": "Test Kitap",
            "yazar": "Test Yazar",
            "book_type": "roman",
            "book_subtype": "cocuk",
            "analiz_tarihi": "2026-01-01",
            "ana_tema": "Dostluk",
            "ogretmen_notu": "Not.",
            "kazanim_analizi": [],
            "entity_store_graph": {"foo": "bar"},
        }

        projected = app_module.project_analysis_preserve_evidence(sample, "teacher")

        self.assertNotIn("kitap_ozeti", projected)
        self.assertNotIn("canonical_summary_ir", projected)
        self.assertNotIn("summary_consistency_audit", projected)
        self.assertNotIn("rendered_summary", projected)
        self.assertNotIn("summary_before_gate", projected)
        self.assertNotIn("summary_after_gate", projected)
        self.assertNotIn("summary_before_gate_hash", projected)
        self.assertNotIn("summary_after_gate_hash", projected)
        self.assertNotIn("summary_ui_hash", projected)
        self.assertNotIn("summary_pdf_hash", projected)
        self.assertNotIn("rendered_summary_hash", projected)
        self.assertNotIn("ui_summary_hash", projected)
        self.assertNotIn("pdf_summary_hash", projected)
        self.assertNotIn("canonical_summary_hash", projected)
        self.assertNotIn("canonical_summary_ir_hash", projected)
        self.assertEqual(0, count_field_occurrences(projected, "entity_store_graph"))

    def test_teacher_projection_is_deterministic_and_preserves_summary_selection(self):
        sample = {
            "kitap_adi": "Test Kitap",
            "yazar": "Test Yazar",
            "book_type": "roman",
            "book_subtype": "cocuk",
            "analiz_tarihi": "2026-01-01",
            "ana_tema": "Dostluk",
            "ogretmen_notu": "Not.",
            "kazanim_analizi": [],
            "kitap_ozeti": "Özet öğretmen için.",
            "summary_consistency_audit": {"summary_before_gate_hash": "abc", "summary_after_gate_hash": "def"},
            "rendered_summary": "Render edildi",
            "summary_before_gate": "Önce",
            "summary_after_gate": "Sonra",
            "summary_before_gate_hash": "hash-before",
            "summary_after_gate_hash": "hash-after",
            "summary_ui_hash": "hash-ui",
            "summary_pdf_hash": "hash-pdf",
            "rendered_summary_hash": "hash-rendered",
            "ui_summary_hash": "hash-ui-2",
            "pdf_summary_hash": "hash-pdf-2",
            "canonical_summary_hash": "hash-canonical",
            "canonical_summary_ir_hash": "hash-ir",
        }

        first = app_module.project_analysis_preserve_evidence(sample, "teacher")
        second = app_module.project_analysis_preserve_evidence(sample, "teacher")

        self.assertEqual(json.dumps(first, ensure_ascii=False, sort_keys=True), json.dumps(second, ensure_ascii=False, sort_keys=True))
        self.assertEqual(app_module._select_report_summary(sample), app_module._select_report_summary(first))
        self.assertEqual(app_module._summary_hash(app_module._select_report_summary(sample)), app_module._summary_hash(app_module._select_report_summary(first)))
        before_consistency = app_module.kitap_tutarlilik_denetimi(sample)
        after_consistency = app_module.kitap_tutarlilik_denetimi(first)
        self.assertEqual(before_consistency.get("gecerli"), after_consistency.get("gecerli"))
        self.assertEqual(before_consistency.get("hatalar"), after_consistency.get("hatalar"))


if __name__ == "__main__":
    unittest.main()
