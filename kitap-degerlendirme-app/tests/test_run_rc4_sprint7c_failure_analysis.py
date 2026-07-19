import os
import sys
import json
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from run_rc4_sprint7c_failure_analysis import build_rc4_sprint7c_failure_analysis_artifact


class TestRunRc4Sprint7cFailureAnalysis(unittest.TestCase):
    def setUp(self):
        self.sample_input = {
            "sprint": "RC4 Sprint 7B — Real Report Regression Validation",
            "generated_at": "1970-01-01T00:00:00Z",
            "total_books": 3,
            "passed_count": 0,
            "failed_count": 3,
            "average_summary_quality_score": 52.967,
            "average_coherence": 0.317,
            "average_concreteness_score": 0.021,
            "shadow_only": True,
            "production_output_changed": False,
            "deterministic": True,
            "runtime_pipeline_bound": False,
            "books": [
                {
                    "title": "Tavşan Pati",
                    "evaluation": {
                        "summary_quality_score": 76.7,
                        "coherence": 0.267,
                        "concreteness_score": 0.01,
                        "conflict_present": True,
                        "resolution_present": True,
                        "main_message_present": True,
                        "evidence_concatenation_detected": False,
                        "character_presence": 1.0,
                    },
                },
                {
                    "title": "Büyülü Yastıklar",
                    "evaluation": {
                        "summary_quality_score": 49.6,
                        "coherence": 0.417,
                        "concreteness_score": 0.045,
                        "conflict_present": False,
                        "resolution_present": True,
                        "main_message_present": False,
                        "evidence_concatenation_detected": False,
                        "character_presence": 1.0,
                    },
                },
                {
                    "title": "Benim Adım Kristof Kolomb",
                    "evaluation": {
                        "summary_quality_score": 32.6,
                        "coherence": 0.267,
                        "concreteness_score": 0.009,
                        "conflict_present": False,
                        "resolution_present": False,
                        "main_message_present": True,
                        "evidence_concatenation_detected": False,
                        "character_presence": 1.0,
                    },
                },
            ],
        }

    def test_artifact_generates_file_and_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.json"
            output_path = Path(tmpdir) / "rc4_sprint7c_failure_analysis.json"
            input_path.write_text(json.dumps(self.sample_input, ensure_ascii=False), encoding="utf-8")
            artifact = build_rc4_sprint7c_failure_analysis_artifact(input_path=input_path, output_path=output_path)

            self.assertTrue(output_path.exists())
            self.assertEqual(artifact["total_books"], 3)
            self.assertIn("books", artifact)
            self.assertEqual(len(artifact["books"]), 3)

    def test_total_books_and_failed_books(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.json"
            output_path = Path(tmpdir) / "rc4_sprint7c_failure_analysis.json"
            input_path.write_text(json.dumps(self.sample_input, ensure_ascii=False), encoding="utf-8")
            artifact = build_rc4_sprint7c_failure_analysis_artifact(input_path=input_path, output_path=output_path)

            self.assertEqual(artifact["total_books"], 3)
            self.assertEqual(artifact["failed_books"], 3)

    def test_root_cause_fields_populated(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.json"
            output_path = Path(tmpdir) / "rc4_sprint7c_failure_analysis.json"
            input_path.write_text(json.dumps(self.sample_input, ensure_ascii=False), encoding="utf-8")
            artifact = build_rc4_sprint7c_failure_analysis_artifact(input_path=input_path, output_path=output_path)

            for book in artifact["books"]:
                self.assertIn("likely_root_causes", book)
                self.assertTrue(book["likely_root_causes"])
                self.assertIn("recommended_fix_area", book)
                self.assertTrue(book["recommended_fix_area"])

    def test_recommended_next_action_exists(self):
        artifact = build_rc4_sprint7c_failure_analysis_artifact(input_path=self._write_sample_input())
        self.assertIn("recommended_next_action", artifact)
        self.assertTrue(artifact["recommended_next_action"])

    def test_deterministic_true(self):
        artifact = build_rc4_sprint7c_failure_analysis_artifact(input_path=self._write_sample_input())
        self.assertTrue(artifact["deterministic"])

    def _write_sample_input(self):
        tmpdir = tempfile.mkdtemp()
        input_path = Path(tmpdir) / "input.json"
        input_path.write_text(json.dumps(self.sample_input, ensure_ascii=False), encoding="utf-8")
        return input_path


if __name__ == "__main__":
    unittest.main()
