import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_rc4_sprint4_ground_truth_dataset import build_ground_truth_dataset_artifact


class TestRunRc4Sprint4GroundTruthDataset(unittest.TestCase):
    def test_build_ground_truth_dataset_artifact(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / 'rc4_sprint4_ground_truth_dataset.json'
            artifact = build_ground_truth_dataset_artifact(output_path=output_path)

            self.assertEqual(artifact['total_books'], 3)
            self.assertEqual(artifact['dataset_version'], '1.0')
            self.assertEqual(artifact['generated_at'], '1970-01-01T00:00:00Z')
            self.assertTrue(all(book['review_status'] == 'pending' for book in artifact['books']))
            self.assertTrue(all('reviewer_id' in book for book in artifact['books']))

            saved = json.loads(output_path.read_text(encoding='utf-8'))
            self.assertEqual(saved, artifact)


if __name__ == '__main__':
    unittest.main()
