import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_rc4_sprint4_ground_truth_comparison import build_ground_truth_comparison_artifact


class TestRunRc4Sprint4GroundTruthComparison(unittest.TestCase):
    def test_build_ground_truth_comparison_artifact(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / 'rc4_sprint4_ground_truth_comparison_results.json'
            artifact = build_ground_truth_comparison_artifact(output_path=output_path)

            self.assertEqual(artifact['total_books'], 3)
            self.assertIn('per_book_comparisons', artifact)
            self.assertIn('average_precision', artifact)
            self.assertIn('average_recall', artifact)
            self.assertIn('average_f1_score', artifact)
            self.assertTrue(artifact['deterministic'])
            self.assertFalse(artifact['production_output_changed'])
            self.assertFalse(artifact['shadow_pipeline_called'])
            self.assertFalse(artifact['semantic_orchestrator_called'])

            saved = json.loads(output_path.read_text(encoding='utf-8'))
            self.assertEqual(saved, artifact)


if __name__ == '__main__':
    unittest.main()
