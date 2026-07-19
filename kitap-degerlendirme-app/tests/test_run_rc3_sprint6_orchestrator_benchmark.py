import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_rc3_sprint6_orchestrator_benchmark import build_orchestrator_benchmark


class TestRunRc3Sprint6OrchestratorBenchmark(unittest.TestCase):
    def test_build_orchestrator_benchmark(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / 'rc3_sprint6_orchestrator_benchmark_results.json'
            verification_path = Path(tmp_dir) / 'rc3_sprint6_final_verification.json'
            result = build_orchestrator_benchmark(output_path=output_path, verification_path=verification_path)

            self.assertEqual(result['total_cases'], 3)
            self.assertTrue(result['stage_order_consistent'])
            self.assertTrue(result['deterministic_all'])
            self.assertFalse(result['production_output_changed_any'])
            self.assertTrue(result['equal_without_shadow_all'])

            verification = json.loads(verification_path.read_text(encoding='utf-8'))
            self.assertEqual(verification['sprint'], 'RC3 Sprint 6 — Semantic Orchestrator')
            self.assertTrue(verification['benchmark_artifact_created'])
            self.assertTrue(verification['final_verification_created'])


if __name__ == '__main__':
    unittest.main()
