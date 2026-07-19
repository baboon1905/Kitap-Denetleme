import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_rc4_sprint3_real_book_shadow_execution import build_real_book_shadow_execution_artifact


class TestRunRc4Sprint3RealBookShadowExecution(unittest.TestCase):
    def test_build_real_book_shadow_execution_artifact(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / 'rc4_sprint3_real_book_shadow_execution_results.json'
            artifact = build_real_book_shadow_execution_artifact(output_path=output_path)

            self.assertEqual(artifact['total_books'], 3)
            self.assertTrue(artifact['all_shadow_execution_completed'])
            self.assertTrue(artifact['orchestrator_called_all'])
            self.assertTrue(artifact['stage_order_consistent'])
            self.assertTrue(artifact['deterministic_all'])
            self.assertFalse(artifact['production_output_changed_any'])
            self.assertFalse(artifact['runtime_pipeline_bound_any'])

            saved = json.loads(output_path.read_text(encoding='utf-8'))
            self.assertEqual(saved, artifact)


if __name__ == '__main__':
    unittest.main()
