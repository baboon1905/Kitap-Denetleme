import unittest

from quality_build_regression import run_build_regression
from theme_gain_analysis import (
    _attach_quality_explanations,
    _select_representative_evidence,
    narrative_quality_assessment,
    prepare_theme_report_payload,
)


class V63QualityOnlySprintTest(unittest.TestCase):
    def test_representative_evidence_prefers_direct_scene_over_weak_mention(self):
        evidence = [
            {
                "sayfa": 1,
                "alinti": "Dayanisma kelimesi tahtada yaziyordu ama kimse birlikte hareket etmedi.",
                "anahtarlar": ["dayanisma"],
                "baglam_gucu": 5,
                "kanit_sinifi": "degerlendirme",
                "kanit_agirligi": 0.45,
                "kanit_turu": "anlati_icerigi",
            },
            {
                "sayfa": 2,
                "alinti": "Kyle ve Akimi birlikte gorev bolustu, Miguel'e destek oldu ve ipucunu ortak kararla paylasti.",
                "anahtarlar": ["birlikte", "destek"],
                "baglam_gucu": 4,
                "kanit_sinifi": "yardim etme",
                "kanit_agirligi": 1.0,
                "kanit_turu": "olay_sahnesi",
            },
        ]
        selected = _select_representative_evidence(evidence, 1)
        self.assertIn("gorev bolustu", selected[0]["alinti"])
        self.assertGreater(selected[0].get("temsil_gucu", 0), 60)

    def test_quality_explanations_are_attached_without_new_teacher_section(self):
        payload = _attach_quality_explanations({
            "ozet_guven_skoru": 0.62,
            "tema_analizi": [{
                "ad": "dayanisma",
                "kanit_sayisi": 1,
                "farkli_sayfa_sayisi": 1,
                "baglam_gucu": 2,
                "kanitlar": [{"sayfa": 1, "alinti": "Ekip birlikte gorev bolustu.", "kanit_turu": "olay_sahnesi", "baglam_gucu": 2}],
            }],
            "kazanim_analizi": [],
            "deger_analizi": [],
            "maarif_profili_eslesmeleri": [],
            "ana_karakterler": [{"ad": "Elif", "ana_karakter_mi": True, "guven_skoru": 0.8}],
        })
        self.assertIn("rapor_guven_aciklamasi", payload)
        self.assertIn("kanit_kalitesi_aciklamasi", payload["tema_analizi"][0])
        self.assertIn("merkezi_kalite_skorlari", payload)

    def test_narrative_quality_assessment_handles_first_third_and_multi_perspective(self):
        first_person = narrative_quality_assessment({
            "anlatim_turu": "birinci_sahis",
            "birinci_sahis_anlatim_skoru": 0.8,
            "ana_karakterler": [
                {"ad": "Elif", "ana_karakter_mi": True, "anlatici_mi": True, "kategori": "anlatici", "guven_skoru": 0.86},
            ],
        })
        third_person = narrative_quality_assessment({
            "anlatim_turu": "ucuncu_sahis",
            "birinci_sahis_anlatim_skoru": 0.05,
            "ana_karakterler": [
                {"ad": "Kristof Kolomb", "ana_karakter_mi": True, "anlatici_mi": False, "guven_skoru": 0.9},
            ],
        })
        multi = narrative_quality_assessment({
            "anlatim_turu": "ucuncu_sahis",
            "birinci_sahis_anlatim_skoru": 0.45,
            "ana_karakterler": [
                {"ad": "Elif", "ana_karakter_mi": True, "dogrudan_konusma_sayisi": 3, "olay_merkezi_skoru": 60, "guven_skoru": 0.8},
                {"ad": "Mert", "ana_karakter_mi": False, "dogrudan_konusma_sayisi": 3, "olay_merkezi_skoru": 55, "guven_skoru": 0.76},
            ],
        })
        self.assertTrue(first_person["gecerli"])
        self.assertEqual(third_person["anlatim_turu"], "ucuncu_sahis")
        self.assertEqual(multi["anlatim_turu"], "coklu_bakis_acisi")

    def test_prepare_payload_includes_narrative_and_score_explanations(self):
        prepared = prepare_theme_report_payload({
            "kitap_adi": "Test",
            "ozet_guven_skoru": 0.75,
            "tema_analizi": [],
            "kazanim_analizi": [],
            "deger_analizi": [],
            "maarif_profili_eslesmeleri": [],
            "ana_karakterler": [{"ad": "Elif", "ana_karakter_mi": True, "guven_skoru": 0.8}],
        })
        self.assertIn("rapor_guven_aciklamasi", prepared)
        self.assertIn("anlatim_kalite_degerlendirmesi", prepared)

    def test_build_regression_runs_mandatory_books(self):
        report = run_build_regression(write_report=False)
        self.assertTrue(report["passed"], report)
        self.assertEqual(sorted(report["mandatory_case_ids"]), ["bay_lemoncello", "kolomb"])
        self.assertEqual(len(report["rows"]), 2)


if __name__ == "__main__":
    unittest.main()
