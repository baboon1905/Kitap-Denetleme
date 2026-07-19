import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_rc3_sprint4_acceptance_gates import build_acceptance_gate_artifact


class TestRunRc3Sprint4AcceptanceGates(unittest.TestCase):
    def test_build_acceptance_gate_artifact(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / 'rc3_sprint4_acceptance_gates_results.json'
            artifact = build_acceptance_gate_artifact(output_path=output_path)

            self.assertEqual(artifact['total_decisions'], 4)
            self.assertEqual(artifact['accepted_count'], 1)
            self.assertEqual(artifact['review_count'], 3)
            self.assertEqual(artifact['rejected_count'], 0)
            self.assertTrue(artifact['decision_schema_valid'])
            self.assertTrue(artifact['deterministic'])
            self.assertFalse(artifact['production_output_changed'])
            self.assertTrue(artifact['equal_without_shadow'])
            self.assertEqual(len(artifact['first_3_decisions']), 3)

            written = json.loads(output_path.read_text(encoding='utf-8'))
            self.assertEqual(written['total_decisions'], artifact['total_decisions'])


if __name__ == '__main__':
    unittest.main()
