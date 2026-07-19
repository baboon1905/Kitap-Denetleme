import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from runtime_v7.summary_quality_engine import evaluate_summary_quality


class TestSummaryQualityEngine(unittest.TestCase):
    def test_empty_summary_fails(self):
        result = evaluate_summary_quality("")
        self.assertEqual(result["summary_quality_score"], 0.0)
        self.assertFalse(result["passed"])

    def test_very_short_summary_fails(self):
        result = evaluate_summary_quality("A short story about a girl.")
        self.assertLess(result["summary_quality_score"], 65.0)
        self.assertFalse(result["passed"])

    def test_evidence_concatenation_detected(self):
        summary = (
            "The book says the hero climbs the mountain. "
            "For example, he faces a storm. "
            "The author writes that he survives. "
            "According to the text, the village welcomes him."
        )
        result = evaluate_summary_quality(summary)
        self.assertTrue(result["evidence_concatenation_detected"])
        self.assertFalse(result["passed"])

    def test_good_narrative_summary_passes(self):
        summary = (
            "This story is about a lonely girl named Elif who lives in a forest village. "
            "She faces a challenge when a storm destroys her home, and she must help her family find shelter. "
            "In the end, the community works together and they build a safe new house, showing how courage and friendship win."
        )
        result = evaluate_summary_quality(summary, {"central_entities": ["Elif"], "themes": ["friendship"]})
        self.assertTrue(result["passed"])
        self.assertGreaterEqual(result["summary_quality_score"], 65.0)

    def test_good_summary_has_higher_coherence_than_bad_summary(self):
        bad = (
            "The book says the hero climbs the mountain. "
            "For example, he faces a storm. "
            "The author writes that he survives. "
            "According to the text, the village welcomes him."
        )
        good = (
            "This story is about a lonely girl named Elif who lives in a forest village. "
            "She faces a challenge when a storm destroys her home, and she must help her family find shelter. "
            "In the end, the community works together and they build a safe new house, showing how courage and friendship win."
        )
        self.assertGreater(
            evaluate_summary_quality(good, {"central_entities": ["Elif"], "themes": ["friendship"]})["coherence"],
            evaluate_summary_quality(bad)["coherence"],
        )

    def test_good_summary_has_higher_concreteness_than_bad_summary(self):
        bad = (
            "The book says the hero climbs the mountain. "
            "For example, he faces a storm. "
            "The author writes that he survives. "
            "According to the text, the village welcomes him."
        )
        good = (
            "This story is about a lonely girl named Elif who lives in a forest village. "
            "She faces a challenge when a storm destroys her home, and she must help her family find shelter. "
            "In the end, the community works together and they build a safe new house, showing how courage and friendship win."
        )
        self.assertGreater(
            evaluate_summary_quality(good, {"central_entities": ["Elif"], "themes": ["friendship"]})["concreteness_score"],
            evaluate_summary_quality(bad)["concreteness_score"],
        )

    def test_low_coherence_summary_fails(self):
        summary = (
            "This book is about Alice. "
            "The hero runs away. "
            "The end is happy."
        )
        result = evaluate_summary_quality(summary, {"central_entities": ["Alice"]})
        self.assertFalse(result["passed"])
        self.assertLess(result["coherence"], 0.4)

    def test_low_concreteness_summary_fails(self):
        summary = (
            "The story is about growth and feeling. "
            "It shows change and learning in general terms. "
            "The ending is positive."
        )
        result = evaluate_summary_quality(summary)
        self.assertFalse(result["passed"])
        self.assertLess(result["concreteness_score"], 0.06)

    def test_missing_character_lowers_score(self):
        summary = (
            "The story follows a village in winter where a challenge appears and the community must survive. "
            "It describes the struggle and the final outcome, but does not name the main person."
        )
        result = evaluate_summary_quality(summary, {"central_entities": ["Ali", "Veli"]})
        self.assertLess(result["character_presence"], 0.35)
        self.assertFalse(result["passed"])

    def test_missing_conflict_lowers_score(self):
        summary = (
            "This book tells about a child in a quiet village who spends days playing with friends. "
            "It explains the daily routine and the feelings of the child. "
            "At the end, everything remains peaceful and unchanged."
        )
        result = evaluate_summary_quality(summary, {"central_entities": ["child"]})
        self.assertFalse(result["conflict_present"])
        self.assertFalse(result["passed"])

    def test_repeated_sentences_lowers_score(self):
        summary = (
            "The hero travels to the river. "
            "The hero travels to the river. "
            "The hero travels to the river. "
            "The hero finds a new home."
        )
        result = evaluate_summary_quality(summary)
        self.assertGreater(result["repetition_score"], 0.0)
        self.assertFalse(result["passed"])

    def test_deterministic_output(self):
        summary = (
            "The book is about a small girl who wanders through the forest. "
            "She meets a kind teacher and learns to help her family. "
            "In the end she finds safety and happiness."
        )
        first = evaluate_summary_quality(summary, {"central_entities": ["girl"], "themes": ["help"]})
        second = evaluate_summary_quality(summary, {"central_entities": ["girl"], "themes": ["help"]})
        self.assertEqual(first, second)

    def test_input_not_mutated(self):
        summary = "A girl faces a storm and later learns to rebuild her house."
        summary_ir = {"central_entities": ["girl"], "themes": ["loss"]}
        clone = summary_ir.copy()
        evaluate_summary_quality(summary, summary_ir)
        self.assertEqual(summary_ir, clone)
