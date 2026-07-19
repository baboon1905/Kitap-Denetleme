import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from theme_gain_analysis import (
    SUMMARY_PLACE_TERMS,
    _consistency_evidence_text,
    _unsupported_summary_terms,
)


class TestConsistencyEvidenceSurface(unittest.TestCase):
    def test_late_theme_place_evidence_is_available_for_term_validation(self):
        payload = {
            "event_graph": [
                {"kaynak_metin": f"Ön kanıt metni {index} yeterli ayrıntı içerir."}
                for index in range(9)
            ],
            "tema_analizi": [
                {
                    "ad": "İlk tema",
                    "kanitlar": [{"alinti": "İlk tema başka bir olayı açıklar."}],
                },
                {
                    "ad": "İkinci tema",
                    "kanitlar": [{"alinti": "Yolculuğun hedefi Hindistan olarak anlatılır."}],
                },
            ],
        }

        evidence_text = _consistency_evidence_text(payload)

        self.assertIn("Hindistan", evidence_text)
        self.assertEqual(
            [],
            _unsupported_summary_terms(
                "Yolculuğun hedefi Hindistan'dır.",
                evidence_text,
                SUMMARY_PLACE_TERMS,
            ),
        )

    def test_place_missing_from_all_evidence_remains_unsupported(self):
        payload = {
            "tema_analizi": [
                {
                    "ad": "Yolculuk",
                    "kanitlar": [{"alinti": "Gemi açık denizde ilerler."}],
                }
            ]
        }

        evidence_text = _consistency_evidence_text(payload)

        self.assertEqual(
            ["ispanya"],
            _unsupported_summary_terms(
                "Gemi İspanya kıyılarına yönelir.",
                evidence_text,
                SUMMARY_PLACE_TERMS,
            ),
        )


if __name__ == "__main__":
    unittest.main()
