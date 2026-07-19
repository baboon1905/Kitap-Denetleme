import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from run_rc4_sprint5_summary_quality_check import build_summary_quality_check_artifact


class TestRunRC4Sprint5SummaryQualityCheck(unittest.TestCase):
    def test_artifact_is_generated(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "rc4_sprint5_summary_quality_results.json"
            artifact = build_summary_quality_check_artifact(output_path=output_path)
            self.assertTrue(output_path.exists())
            self.assertEqual(artifact["total_cases"], 3)
            self.assertIn("per_case_results", artifact)

    def test_at_least_one_weak_summary_fails(self):
        artifact = build_summary_quality_check_artifact()
        self.assertGreater(artifact["failed_count"], 0)

    def test_good_summary_passes(self):
        artifact = build_summary_quality_check_artifact()
        good_case = next(
            case for case in artifact["per_case_results"] if case["case_id"] == "good-narrative-summary"
        )
        self.assertTrue(good_case["evaluation"]["passed"])

    def test_deterministic_true(self):
        artifact = build_summary_quality_check_artifact()
        self.assertTrue(artifact["deterministic"])

    def test_production_output_changed_false(self):
        artifact = build_summary_quality_check_artifact()
        self.assertFalse(artifact["production_output_changed"])
