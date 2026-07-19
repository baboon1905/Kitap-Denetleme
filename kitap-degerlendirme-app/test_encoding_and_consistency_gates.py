import unittest

from text_quality import collect_text_quality_issues, repair_mojibake, repair_payload_text
from theme_gain_analysis import kitap_tutarlilik_denetimi


class EncodingAndConsistencyGateTests(unittest.TestCase):
    def test_mojibake_examples_are_repaired_before_output(self):
        payload = {
            "summary": "olaylarÄ± geÃ§er Ã¶zet paylaÅŸÄ±r Ã§Ã¶zÃ¼m",
            "nested": ["Sorgulayici", "Dusuk"],
        }
        repaired = repair_payload_text(payload)
        self.assertEqual(repaired["summary"], "olayları geçer özet paylaşır çözüm")
        self.assertEqual(collect_text_quality_issues(repaired), [])
        self.assertEqual(repair_mojibake("paylaÅŸÄ±r"), "paylaşır")

    def test_consistency_audit_exposes_checked_and_rendered_summaries(self):
        payload = {
            "kitap_adi": "Test Kitabi",
            "kitap_ozeti": "Test Kitabi, Ali'nin sorumluluk almasini anlatir.",
            "canonical_summary": "Test Kitabi, Ali'nin sorumluluk almasini anlatir.",
            "ana_tema": "sorumluluk",
            "tema_analizi": [{"ad": "sorumluluk", "kanitlar": [{"alinti": "Ali sorumluluk aldi."}]}],
            "ana_karakterler": [{"ad": "Ali", "ana_karakter_mi": True}],
            "event_graph": [{"evidence": "Ali sorumluluk aldi.", "actors": ["Ali"]}],
        }
        audit = kitap_tutarlilik_denetimi(payload)
        self.assertIn("consistency_checked_summary_first_300", audit)
        self.assertIn("rendered_summary_first_300", audit)
        self.assertIn("checked_summary_hash", audit)
        self.assertIn("rendered_summary_hash", audit)
        self.assertIn("offending_phrase_full_sentence", audit)


if __name__ == "__main__":
    unittest.main()
