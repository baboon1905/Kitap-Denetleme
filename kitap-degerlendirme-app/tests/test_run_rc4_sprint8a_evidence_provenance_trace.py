import unittest
import json
from run_rc4_sprint8a_evidence_provenance_trace import build_rc4_sprint8a_evidence_provenance_report


class TestRunRc4Sprint8aEvidenceProvenanceTrace(unittest.TestCase):
    def setUp(self):
        self.sample_books = [
            {
                "book_id": "book-trace-1",
                "title": "Trace Book",
                "summary_ir": {
                    "title": "Trace Book",
                    "central_entities": ["Elif"],
                    "themes": ["courage"],
                    "places": ["village"],
                    "temporal_context": "modern",
                    "key_events": ["Elif leaves home."],
                    "evidence_snippets": {
                        "setup": ["For example, she lived in a small village."],
                        "conflict": ["According to the story, a storm arrived."],
                        "resolution": ["Finally, she found shelter."],
                    },
                },
            }
        ]

    def test_trace_report_structure(self):
        result = build_rc4_sprint8a_evidence_provenance_report(self.sample_books)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["sprint"], "RC4 Sprint 8A — Evidence Provenance Trace")
        self.assertEqual(result["total_books"], 1)
        self.assertTrue(result["shadow_only"])
        self.assertFalse(result["production_output_changed"])
        self.assertIsInstance(result["books"], list)

    def test_book_entry_contains_expected_sections(self):
        result = build_rc4_sprint8a_evidence_provenance_report(self.sample_books)
        book = result["books"][0]
        self.assertIn("raw_evidence", book)
        self.assertIn("synthesized_evidence", book)
        self.assertIn("builder_input", book)
        self.assertIn("builder_output", book)
        self.assertIn("final_report_output", book)
        self.assertIn("summary_surfaces", book["final_report_output"])

    def test_evidence_synthesis_removes_markers(self):
        result = build_rc4_sprint8a_evidence_provenance_report(self.sample_books)
        synthesized_conflict = result["books"][0]["synthesized_evidence"]["conflict"][0]
        self.assertNotIn("For example", synthesized_conflict["synthesized"])
        self.assertNotIn("According to", synthesized_conflict["synthesized"])

    def test_builder_output_includes_narrative(self):
        result = build_rc4_sprint8a_evidence_provenance_report(self.sample_books)
        builder_output = result["books"][0]["builder_output"]
        self.assertIn("narrative", builder_output)
        self.assertIn("sections", builder_output)
        self.assertIn("metadata", builder_output)
        self.assertGreater(len(builder_output["narrative"]), 0)

    def test_deterministic_report(self):
        result1 = build_rc4_sprint8a_evidence_provenance_report(self.sample_books)
        result2 = build_rc4_sprint8a_evidence_provenance_report(self.sample_books)
        self.assertEqual(json.dumps(result1, sort_keys=True), json.dumps(result2, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
