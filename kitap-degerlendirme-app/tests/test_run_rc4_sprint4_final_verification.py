import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_rc4_sprint4_final_verification import build_final_verification


class TestRunRc4Sprint4FinalVerification(unittest.TestCase):
    def test_build_final_verification(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dataset = Path(tmp_dir) / 'rc4_sprint4_ground_truth_dataset.json'
            temp_comparison = Path(tmp_dir) / 'rc4_sprint4_ground_truth_comparison_results.json'
            temp_output = Path(tmp_dir) / 'rc4_sprint4_final_verification.json'

            # Copy the existing artifacts to temporary files for isolated verification
            src_dir = Path(__file__).parent.parent
            dataset_src = src_dir / 'rc4_sprint4_ground_truth_dataset.json'
            comparison_src = src_dir / 'rc4_sprint4_ground_truth_comparison_results.json'
            temp_dataset.write_text(dataset_src.read_text(encoding='utf-8'), encoding='utf-8')
            temp_comparison.write_text(comparison_src.read_text(encoding='utf-8'), encoding='utf-8')

            verification = build_final_verification(
                output_path=temp_output,
                ground_truth_dataset_path=temp_dataset,
                comparison_results_path=temp_comparison,
            )

            self.assertEqual(verification['sprint'], 'RC4 Sprint 4 — Human Ground Truth Validation')
            self.assertTrue(verification['plan_created'])
            self.assertEqual(verification['ground_truth_builder_tests_passed'], 6)
            self.assertTrue(verification['ground_truth_dataset_artifact_test_passed'])
            self.assertEqual(verification['comparator_tests_passed'], 6)
            self.assertTrue(verification['comparison_artifact_test_passed'])
            self.assertTrue(verification['ground_truth_dataset_created'])
            self.assertTrue(verification['comparison_results_created'])
            self.assertEqual(verification['total_books'], 3)
            self.assertEqual(verification['average_precision'], 0.5555555555555555)
            self.assertEqual(verification['average_recall'], 1.0)
            self.assertEqual(verification['average_f1_score'], 0.7111111111111111)
            self.assertTrue(verification['deterministic'])
            self.assertFalse(verification['production_output_changed'])
            self.assertFalse(verification['shadow_pipeline_called'])
            self.assertFalse(verification['semantic_orchestrator_called'])
            self.assertFalse(verification['runtime_pipeline_bound'])

            saved = json.loads(temp_output.read_text(encoding='utf-8'))
            self.assertEqual(saved, verification)


if __name__ == '__main__':
    unittest.main()
