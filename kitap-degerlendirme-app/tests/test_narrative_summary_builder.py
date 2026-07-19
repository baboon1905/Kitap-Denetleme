import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from runtime_v7.narrative_summary_builder import build_narrative_summary
from runtime_v7.summary_quality_engine import evaluate_summary_quality


class TestNarrativeSummaryBuilder(unittest.TestCase):
    def test_empty_input_safe_output(self):
        result = build_narrative_summary()
        self.assertIsInstance(result, dict)
        self.assertIn("narrative_summary", result)
        self.assertIn("summary_sections", result)
        self.assertIsInstance(result["summary_sections"], dict)
        self.assertTrue(result["narrative_summary"] == "" or isinstance(result["narrative_summary"], str))

    def test_produces_all_required_sections(self):
        result = build_narrative_summary(
            summary_ir={"central_entities": ["Ali"]},
            characters=["Ali"],
            themes=["friendship"],
            evidence_snippets=["Ali faces a challenge and learns to help her family."],
        )
        self.assertIn("setup", result["summary_sections"])
        self.assertIn("main_conflict", result["summary_sections"])
        self.assertIn("key_events", result["summary_sections"])
        self.assertIn("resolution", result["summary_sections"])
        self.assertIn("main_message", result["summary_sections"])

    def test_does_not_concatenate_evidence_snippets(self):
        evidence = [
            "For example, Ali meets a fox.",
            "According to the story, the river is dangerous.",
        ]
        result = build_narrative_summary(characters=["Ali"], evidence_snippets=evidence)
        narrative = result["narrative_summary"]
        self.assertNotIn("For example", narrative)
        self.assertNotIn("According to", narrative)

    def test_includes_main_character_when_available(self):
        result = build_narrative_summary(characters=["Elif"], themes=["courage"])
        self.assertIn("Elif", result["narrative_summary"])

    def test_includes_main_conflict_when_available(self):
        result = build_narrative_summary(evidence_snippets=["The main character struggles with a dangerous storm."])
        self.assertIn("conflict", result["summary_sections"]["main_conflict"].lower())

    def test_includes_resolution_when_available(self):
        result = build_narrative_summary(evidence_snippets=["In the end, the family finds a solution and rebuilds the house."])
        self.assertIn("resolution", result["summary_sections"]["resolution"].lower())

    def test_deterministic_output(self):
        kwargs = {
            "summary_ir": {"central_entities": ["Elif"]},
            "characters": ["Elif"],
            "themes": ["friendship"],
            "evidence_snippets": ["A storm tests the family."]
        }
        first = build_narrative_summary(**kwargs)
        second = build_narrative_summary(**kwargs)
        self.assertEqual(first, second)

    def test_summary_quality_engine_passes_generated_good_summary(self):
        result = build_narrative_summary(
            summary_ir={"central_entities": ["Elif"], "themes": ["friendship"]},
            characters=["Elif"],
            themes=["courage", "friendship"],
            evidence_snippets=[
                "This story shows a girl overcoming a storm.",
                "She rebuilds her home and discovers strength."
            ],
        )
        quality = evaluate_summary_quality(result["narrative_summary"], {"central_entities": ["Elif"]})
        self.assertTrue(quality["passed"])


if __name__ == "__main__":
    unittest.main()
