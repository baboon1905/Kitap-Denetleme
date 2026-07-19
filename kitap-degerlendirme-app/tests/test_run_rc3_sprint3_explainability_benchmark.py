import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_rc3_sprint3_explainability_benchmark import build_explainability_benchmark


class TestRunRc3Sprint3ExplainabilityBenchmark(unittest.TestCase):
    def test_build_explainability_benchmark(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / 'rc3_sprint3_explainability_benchmark_results.json'
            verification_path = Path(tmp_dir) / 'rc3_sprint3_final_verification.json'
            result = build_explainability_benchmark(output_path=output_path, verification_path=verification_path)

            self.assertEqual(result['total_cases'], 3)
            self.assertEqual(result['total_explanations'], 6)
            self.assertGreaterEqual(result['avg_explanation_coverage'], 0.0)
            self.assertTrue(result['schema_valid_all'])
            self.assertTrue(result['deterministic_all'])
            self.assertFalse(result['production_output_changed_any'])
            self.assertTrue(result['equal_without_shadow_all'])

            self.assertTrue(verification_path.exists())
            verification = json.loads(verification_path.read_text(encoding='utf-8'))
            self.assertEqual(verification['sprint'], 'RC3 Sprint 3 — Semantic Explainability Layer')
            self.assertTrue(verification['benchmark_artifact_created'])
            self.assertTrue(verification['final_verification_created'])


if __name__ == '__main__':
    unittest.main()
