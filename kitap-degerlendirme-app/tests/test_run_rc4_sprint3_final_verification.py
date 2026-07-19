import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_rc4_sprint3_final_verification import build_final_verification


class TestRunRc4Sprint3FinalVerification(unittest.TestCase):
    def test_build_final_verification(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / 'rc4_sprint3_final_verification.json'
            verification = build_final_verification(
                output_path=output_path,
                execution_artifact_path=Path(__file__).parent.parent / 'rc4_sprint3_real_book_shadow_execution_results.json',
            )

            self.assertEqual(verification['sprint'], 'RC4 Sprint 3 — Real Book Shadow Execution')
            self.assertTrue(verification['plan_created'])
            self.assertEqual(verification['execution_tests_passed'], 6)
            self.assertTrue(verification['artifact_producer_test_passed'])
            self.assertTrue(verification['shadow_execution_results_created'])
            self.assertEqual(verification['total_books'], 3)
            self.assertTrue(verification['all_shadow_execution_completed'])
            self.assertTrue(verification['orchestrator_called_all'])
            self.assertTrue(verification['stage_order_consistent'])
            self.assertTrue(verification['deterministic_all'])
            self.assertFalse(verification['production_output_changed_any'])
            self.assertFalse(verification['runtime_pipeline_bound_any'])

            saved = json.loads(output_path.read_text(encoding='utf-8'))
            self.assertEqual(saved, verification)


if __name__ == '__main__':
    unittest.main()
