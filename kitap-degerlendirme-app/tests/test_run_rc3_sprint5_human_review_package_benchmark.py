import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_rc3_sprint5_human_review_package_benchmark import build_human_review_package_benchmark


class TestRunRc3Sprint5HumanReviewPackageBenchmark(unittest.TestCase):
    def test_build_human_review_package_benchmark(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / 'rc3_sprint5_human_review_package_benchmark_results.json'
            verification_path = Path(tmp_dir) / 'rc3_sprint5_final_verification.json'
            result = build_human_review_package_benchmark(output_path=output_path, verification_path=verification_path)

            self.assertEqual(result['total_cases'], 3)
            self.assertEqual(result['total_review_items'], 6)
            self.assertTrue(result['schema_valid_all'])
            self.assertTrue(result['deterministic_all'])
            self.assertFalse(result['production_output_changed_any'])
            self.assertTrue(result['equal_without_shadow_all'])

            verification = json.loads(verification_path.read_text(encoding='utf-8'))
            self.assertEqual(verification['sprint'], 'RC3 Sprint 5 — Human Review Package')
            self.assertTrue(verification['benchmark_artifact_created'])
            self.assertTrue(verification['final_verification_created'])


if __name__ == '__main__':
    unittest.main()
