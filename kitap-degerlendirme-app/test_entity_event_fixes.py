from __future__ import annotations

import unittest

from pipeline_runtime_enforcer import (
    enforce_all,
    is_central_entity_blacklisted,
    is_generic_event_action,
    regression_fail_rules,
    verify_summary_hash_consistency,
)


class EntityEventRuntimeEnforcerTests(unittest.TestCase):
    def test_blacklisted_central_entities_are_demoted(self) -> None:
        payload = {
            "kitap_adi": "Buyulu Yastiklar",
            "ana_karakterler": [
                {"ad": "Buyulu Yastiklar", "central_entity": True},
                {"ad": "Ihtiyaclari", "central_entity": True},
                {"ad": "Katolik", "central_entity": True},
                {"ad": "Yasemin", "central_entity": True, "mention_count": 3},
            ],
            "kitap_ozeti": "Yasemin bir sorunu fark eder ve cozum arar.",
        }

        result = enforce_all(payload)
        central = [item for item in result["ana_karakterler"] if item.get("central_entity")]

        self.assertEqual(["Yasemin"], [item["ad"] for item in central])
        self.assertTrue(is_central_entity_blacklisted("Hepinize")[0])
        self.assertTrue(is_central_entity_blacklisted("Ingilizce")[0])

    def test_generic_events_are_not_kept_as_canonical_events(self) -> None:
        payload = {
            "event_graph": [
                {"actors": ["Ali"], "action": "durumun nedenini sorgular", "evidence": "Ali durumun nedenini sorgular."},
                {"actors": ["Ali"], "action": "Patiyi Erene teslim eder", "evidence": "Ali Patiyi Erene teslim eder."},
            ],
            "kitap_ozeti": "Ali Patiyi Erene teslim eder.",
        }

        result = enforce_all(payload)

        self.assertTrue(is_generic_event_action("ipucunu okur"))
        self.assertEqual(1, result["canonical_event_count"])
        self.assertEqual(0.0, result["generic_event_ratio"])
        self.assertEqual(1, len(result["discarded_generic_events"]))

    def test_high_theme_evidence_prevents_short_fallback_and_syncs_hashes(self) -> None:
        payload = {
            "kitap_adi": "Ornek Kitap",
            "ana_tema": "sorumluluk",
            "theme_confidence": 0.82,
            "kitap_ozeti": "Bu kisa ozet on yedi kelimeye yakindir ve guclu kanita ragmen yetersiz kalir.",
            "tema_analizi": [
                {
                    "ad": "sorumluluk",
                    "guven_skoru": 0.82,
                    "kanitlar": [
                        {"metin": "Ali sabah tavsani beslemek icin erken kalkti."},
                        {"metin": "Ali kafesi temizledi ve yem kabini doldurdu."},
                        {"metin": "Ali arkadasina soz verdigi bakimi aksatmadi."},
                    ],
                }
            ],
        }

        result = enforce_all(payload)

        self.assertGreaterEqual(len(result["kitap_ozeti"].split()), 70)
        self.assertEqual("evidence_based_medium_summary", result["ozet_turu"])
        self.assertTrue(verify_summary_hash_consistency(result)["hash_consistency_pass"])
        self.assertEqual([], regression_fail_rules(result))


if __name__ == "__main__":
    unittest.main()
