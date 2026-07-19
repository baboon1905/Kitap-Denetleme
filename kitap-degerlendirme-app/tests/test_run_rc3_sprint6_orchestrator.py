import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_rc3_sprint6_orchestrator import build_orchestrator_artifact


class TestRunRc3Sprint6Orchestrator(unittest.TestCase):
    def test_build_orchestrator_artifact(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / 'rc3_sprint6_orchestrator_results.json'
            artifact = build_orchestrator_artifact(output_path=output_path)

            self.assertTrue(artifact['orchestrator_enabled'])
            self.assertEqual(artifact['pattern_matches_count'], 9)
            self.assertEqual(artifact['pattern_activations_count'], 5)
            self.assertEqual(artifact['ranked_evidence_count'], 5)
            self.assertEqual(artifact['explanations_count'], 5)
            self.assertEqual(artifact['acceptance_decisions_count'], 5)
            self.assertEqual(artifact['human_review_items_count'], 5)
            self.assertTrue(artifact['delta_analysis_present'])
            self.assertTrue(artifact['deterministic'])
            self.assertFalse(artifact['production_output_changed'])
            self.assertTrue(artifact['equal_without_shadow'])

            saved = json.loads(output_path.read_text(encoding='utf-8'))
            self.assertEqual(saved['pattern_matches_count'], artifact['pattern_matches_count'])


if __name__ == '__main__':
    unittest.main()
