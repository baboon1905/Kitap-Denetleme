import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_rc3_sprint5_human_review_package import build_human_review_package_artifact


class TestRunRc3Sprint5HumanReviewPackage(unittest.TestCase):
    def test_build_human_review_package_artifact(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / 'rc3_sprint5_human_review_package_results.json'
            artifact = build_human_review_package_artifact(output_path=output_path)

            self.assertEqual(artifact['total_review_items'], 4)
            self.assertEqual(artifact['approve_candidate_count'], 1)
            self.assertEqual(artifact['review_human_count'], 3)
            self.assertEqual(artifact['reject_count'], 0)
            self.assertTrue(artifact['package_schema_valid'])
            self.assertTrue(artifact['deterministic'])
            self.assertFalse(artifact['production_output_changed'])
            self.assertTrue(artifact['equal_without_shadow'])

            saved = json.loads(output_path.read_text(encoding='utf-8'))
            self.assertEqual(saved['total_review_items'], artifact['total_review_items'])


if __name__ == '__main__':
    unittest.main()
