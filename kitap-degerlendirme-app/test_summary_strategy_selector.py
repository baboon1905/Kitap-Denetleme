import unittest

from summary_strategy_selector import bridge_sentence_ratio, select_summary_strategy


class SummaryStrategySelectorTests(unittest.TestCase):
    def test_bridge_ratio_limits_strategy(self):
        summary = (
            "Ali yola cikti. "
            "Bu nedenle olaylar ayni sorun cevresinde ilerler. "
            "Ayse yardim etti. "
            "Boylece onceki bilgi bosa kalmaz. "
            "Son adim onceki girisimlerin karsiligini gosterir."
        )
        decision = select_summary_strategy(
            {
                "ozet_guven_skoru": 0.9,
                "event_graph": [{"evidence": "Ali yola cikti."}] * 6,
                "ana_karakterler": [{"ad": "Ali", "guven_skoru": 0.9}],
                "tema_analizi": [{"ad": "sorumluluk", "guven_skoru": 0.9}],
            },
            summary,
            {"event_completeness": 0.9},
        )
        self.assertGreater(bridge_sentence_ratio(summary), 0.35)
        self.assertEqual(decision.summary_strategy, "medium_safe_summary")

    def test_low_summary_confidence_does_not_block_report(self):
        decision = select_summary_strategy({"ozet_guven_skoru": 0.2}, "Kisa ozet.")
        self.assertEqual(decision.summary_strategy, "short_safe_summary")
        self.assertEqual(decision.report_blocking_reasons, [])

    def test_natural_summary_requires_confidence_and_event_count(self):
        decision = select_summary_strategy(
            {
                "ozet_guven_skoru": 0.92,
                "event_graph": [
                    {"evidence": f"Olay {index}.", "action": f"eylem {index}", "event_template_key": f"event:{index}"}
                    for index in range(5)
                ],
                "ana_karakterler": [{"ad": "Ela", "guven_skoru": 0.9}],
                "tema_analizi": [{"ad": "sabir", "guven_skoru": 0.9}],
            },
            "Ela tohumu eker. Ela bekler. Ela yardim ister. Tohum filizlenir. Bahce renklenir.",
            {"event_completeness": 0.9},
        )
        self.assertEqual(decision.summary_strategy, "natural_summary")

    def test_strong_theme_weak_events_uses_medium_safe_summary(self):
        decision = select_summary_strategy(
            {
                "ozet_guven_skoru": 0.35,
                "event_graph": [{"action": "durumun nedenini sormak", "generic_event": True}],
                "ana_karakterler": [{"ad": "Ali", "guven_skoru": 0.8}],
                "tema_analizi": [{"ad": "sorumluluk", "guven_skoru": 0.92}],
            },
            "Tema kanıtları güçlüdür ama olay akışı sınırlıdır.",
        )
        self.assertEqual(decision.summary_strategy, "medium_safe_summary")


if __name__ == "__main__":
    unittest.main()
