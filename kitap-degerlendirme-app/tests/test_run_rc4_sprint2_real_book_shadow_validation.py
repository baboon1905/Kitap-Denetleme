import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_rc4_sprint2_real_book_shadow_validation import build_real_book_shadow_validation_artifact


class TestRunRc4Sprint2RealBookShadowValidation(unittest.TestCase):
    def test_build_real_book_shadow_validation_artifact(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / 'rc4_sprint2_real_book_shadow_validation_results.json'
            artifact = build_real_book_shadow_validation_artifact(output_path=output_path)

            self.assertEqual(artifact['total_books'], 3)
            self.assertTrue(artifact['generated_at'] == '1970-01-01T00:00:00Z')
            self.assertTrue(artifact['all_shadow_validation_ready'])
            self.assertFalse(artifact['semantic_pipeline_called_any'])
            self.assertFalse(artifact['production_output_changed_any'])
            self.assertFalse(artifact['runtime_pipeline_bound_any'])
            self.assertTrue(artifact['deterministic'])

            saved = json.loads(output_path.read_text(encoding='utf-8'))
            self.assertEqual(saved, artifact)


if __name__ == '__main__':
    unittest.main()
