import unittest

from pipeline_runtime_enforcer import enforce_all, regression_fail_rules
from summary_ir import SUMMARY_IR_VERSION
from app import _report_quality_gate


class V7SummaryIRPipelineTests(unittest.TestCase):
    def _payload(self):
        return {
            "kitap_adi": "Benchmark Snapshot",
            "theme_confidence": 0.82,
            "ana_tema": "sorumluluk",
            "ana_tema_kanitlari": [
                {"metin": "Mina yarali kusu eve goturdu ve ona su verdi."},
                {"metin": "Arkadaslari kafesi temizledi ve yiyecek hazirladi."},
                {"metin": "Mina veterinere giderek kusun bakimini ogrendi."},
            ],
            "ana_karakterler": [
                {"ad": "Ihtiyaclari", "central_entity": True, "mention_count": 1, "source_pages": [1]},
                {"ad": "Mina", "mention_count": 7, "source_pages": [1, 2, 3], "relation_score": 0.7, "tur": "kisi"},
                {"ad": "Kus", "mention_count": 5, "source_pages": [1, 3], "relation_score": 0.5, "tur": "hayvan"},
            ],
            "event_graph": [
                {
                    "actor": "Mina",
                    "action": "Mina yarali kusu eve goturdu",
                    "evidence": "Mina yarali kusu eve goturdu ve ona su verdi.",
                    "conflict": "Kusun bakima ihtiyaci vardir",
                    "outcome": "Kus guvenli bir yere alinir",
                },
                {
                    "actor": "Arkadaslari",
                    "action": "Arkadaslari kafesi temizledi",
                    "evidence": "Arkadaslari kafesi temizledi ve yiyecek hazirladi.",
                    "outcome": "Bakim sorumlulugu paylasilir",
                },
                {
                    "actor": "Mina",
                    "action": "Mina veterinere giderek bakim bilgisini ogrendi",
                    "evidence": "Mina veterinere giderek kusun bakimini ogrendi.",
                    "turning_point": "Mina yardimi uzman bilgisiyle surdurur",
                    "outcome": "Kusun iyilesme sureci baslar",
                },
                {
                    "actor": "Mina",
                    "action": "durumun nedenini sorgular",
                    "evidence": "Mina durumun nedenini sorgular.",
                },
            ],
            "kitap_ozeti": "Kisa ozet gereksiz fallback olarak kalmamali.",
        }

    def test_summary_ir_is_single_hash_source(self):
        result = enforce_all(self._payload(), "unit")
        self.assertEqual(result["canonical_summary_ir"]["version"], SUMMARY_IR_VERSION)
        self.assertIn("story_arc", result["canonical_summary_ir"])
        self.assertIn("event_sequence", result["canonical_summary_ir"])
        self.assertIn("event_importance", result["canonical_summary_ir"])
        hashes = {
            result.get("checked_summary_hash"),
            result.get("rendered_summary_hash"),
            result.get("ui_summary_hash"),
            result.get("pdf_summary_hash"),
            result.get("teacher_summary_hash"),
            result.get("quality_summary_hash"),
            result.get("canonical_summary_ir_hash"),
        }
        self.assertEqual(len(hashes), 1)
        self.assertIn("entity_graph_summary", result["canonical_summary_ir"])
        self.assertIn("narrative_graph", result["canonical_summary_ir"])
        self.assertGreaterEqual(len(result["summary"].split()), 70)
        self.assertNotEqual(len(result["summary"].split()), 17)

    def test_phase1_summary_is_not_evidence_concatenation(self):
        result = enforce_all(self._payload(), "unit")
        summary = result["summary"]
        forbidden = [
            "Bu okuma",
            "Sonuç olarak",
            "Sonuc olarak",
            "Olay akışı",
            "Olay akisi",
            "somut bir karar uygulamak",
            "çözüme yarayan bilgi bulmak",
            "cozume yarayan bilgi bulmak",
        ]
        for marker in forbidden:
            self.assertNotIn(marker, summary)
        evidence_sentences = [
            "Mina yarali kusu eve goturdu ve ona su verdi.",
            "Arkadaslari kafesi temizledi ve yiyecek hazirladi.",
            "Mina veterinere giderek kusun bakimini ogrendi.",
        ]
        copied = sum(1 for sentence in evidence_sentences if sentence in summary)
        self.assertLessEqual(copied, 1, summary)
        self.assertNotIn("Ayrica", summary)

    def test_central_entity_and_generic_events_are_cleaned(self):
        result = enforce_all(self._payload(), "unit")
        central_names = [
            item["ad"]
            for item in result["ana_karakterler"]
            if item.get("central_entity") or item.get("merkezi_varlik_mi")
        ]
        self.assertIn("Mina", central_names)
        self.assertNotIn("Ihtiyaclari", central_names)
        self.assertEqual(result.get("generic_event_ratio"), 0.0)
        self.assertTrue(result.get("discarded_generic_events"))
        self.assertFalse(regression_fail_rules(result), regression_fail_rules(result))

    def test_quality_gate_is_warning_only_for_endpoint(self):
        result = enforce_all(self._payload(), "unit")
        result["karakter_kalite_degerlendirmesi"] = {"hatalar": ["quality-only-test"]}
        self.assertIsNone(_report_quality_gate(result, "unit-test"))


if __name__ == "__main__":
    unittest.main()
