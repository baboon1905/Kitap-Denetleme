import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from run_rc4_sprint7b_real_report_regression_validation import (
    build_rc4_sprint7b_real_report_regression_validation_artifact,
    BOOK_REGRESSION_CASES,
)


class TestRunRc4Sprint7bRealReportRegressionValidation(unittest.TestCase):
    def test_artifact_generates_file_and_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "rc4_sprint7b_real_report_regression_validation.json"
            artifact = build_rc4_sprint7b_real_report_regression_validation_artifact(output_path=output_path)
            self.assertTrue(output_path.exists())
            self.assertEqual(artifact["total_books"], 3)
            self.assertIn("books", artifact)
            self.assertEqual(len(artifact["books"]), 3)

    def test_all_books_present_and_count_matches(self):
        artifact = build_rc4_sprint7b_real_report_regression_validation_artifact()
        titles = [book["title"] for book in artifact["books"]]
        self.assertCountEqual(
            titles,
            [case["title"] for case in BOOK_REGRESSION_CASES],
        )
        self.assertEqual(artifact["total_books"], 3)

    def test_deterministic_output_is_true(self):
        artifact = build_rc4_sprint7b_real_report_regression_validation_artifact()
        self.assertTrue(artifact["deterministic"])

    def test_production_output_changed_is_false(self):
        artifact = build_rc4_sprint7b_real_report_regression_validation_artifact()
        self.assertFalse(artifact["production_output_changed"])

    def test_shadow_only_is_true(self):
        artifact = build_rc4_sprint7b_real_report_regression_validation_artifact()
        self.assertTrue(artifact["shadow_only"])

    def test_result_evaluations_have_expected_fields(self):
        artifact = build_rc4_sprint7b_real_report_regression_validation_artifact()
        for book in artifact["books"]:
            self.assertIn("evaluation", book)
            for key in [
                "summary_quality_score",
                "coverage",
                "coherence",
                "passed",
                "concreteness_score",
            ]:
                self.assertIn(key, book["evaluation"], f"Missing evaluation field {key}")

    def test_some_books_pass_and_some_may_fail(self):
        artifact = build_rc4_sprint7b_real_report_regression_validation_artifact()
        self.assertEqual(artifact["passed_count"] + artifact["failed_count"], artifact["total_books"])
        self.assertGreaterEqual(artifact["passed_count"], 0)
        self.assertGreaterEqual(artifact["failed_count"], 0)

    def test_summary_ir_preserved_for_each_book(self):
        artifact = build_rc4_sprint7b_real_report_regression_validation_artifact()
        for book in artifact["books"]:
            self.assertIn("summary_ir", book)
            self.assertIsInstance(book["summary_ir"], dict)
            self.assertGreater(len(book["summary_ir"]), 0)


if __name__ == "__main__":
    unittest.main()
