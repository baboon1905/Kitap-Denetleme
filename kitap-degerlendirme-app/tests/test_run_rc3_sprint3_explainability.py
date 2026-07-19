import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_rc3_sprint3_explainability import build_explainability_artifact


class TestRunRc3Sprint3Explainability(unittest.TestCase):
    def test_build_explainability_artifact(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / 'rc3_sprint3_explainability_results.json'
            artifact = build_explainability_artifact(output_path=output_path)

            self.assertEqual(artifact['total_explanations'], 4)
            self.assertEqual(artifact['explanation_coverage'], 1.0)
            self.assertTrue(artifact['explanation_schema_valid'])
            self.assertTrue(artifact['deterministic'])
            self.assertFalse(artifact['production_output_changed'])
            self.assertTrue(artifact['equal_without_shadow'])
            self.assertEqual(len(artifact['first_3_explanations']), 3)

            saved = json.loads(output_path.read_text(encoding='utf-8'))
            self.assertEqual(saved['total_explanations'], artifact['total_explanations'])
            self.assertEqual(saved['first_3_explanations'][0]['pattern_id'], artifact['first_3_explanations'][0]['pattern_id'])


if __name__ == '__main__':
    unittest.main()
