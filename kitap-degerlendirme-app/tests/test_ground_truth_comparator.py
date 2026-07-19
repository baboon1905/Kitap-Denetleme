import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.ground_truth_comparator import build_ground_truth_comparison


class TestGroundTruthComparator(unittest.TestCase):
    def test_empty_inputs(self):
        result = build_ground_truth_comparison([], [])
        self.assertEqual(result['matched_patterns'], [])
        self.assertEqual(result['shadow_only_patterns'], [])
        self.assertEqual(result['human_only_patterns'], [])
        self.assertEqual(result['precision'], 0.0)
        self.assertEqual(result['recall'], 0.0)
        self.assertEqual(result['f1_score'], 0.0)

    def test_perfect_match(self):
        result = build_ground_truth_comparison(['a', 'b'], ['a', 'b'])
        self.assertEqual(result['matched_patterns'], ['a', 'b'])
        self.assertEqual(result['shadow_only_patterns'], [])
        self.assertEqual(result['human_only_patterns'], [])
        self.assertEqual(result['precision'], 1.0)
        self.assertEqual(result['recall'], 1.0)
        self.assertEqual(result['f1_score'], 1.0)

    def test_partial_match(self):
        result = build_ground_truth_comparison(['a', 'b', 'c'], ['a', 'd'])
        self.assertEqual(result['matched_patterns'], ['a'])
        self.assertEqual(result['shadow_only_patterns'], ['b', 'c'])
        self.assertEqual(result['human_only_patterns'], ['d'])
        self.assertAlmostEqual(result['precision'], 1/3)
        self.assertAlmostEqual(result['recall'], 1/2)
        self.assertAlmostEqual(result['f1_score'], 2/5)

    def test_no_overlap(self):
        result = build_ground_truth_comparison(['a', 'b'], ['c', 'd'])
        self.assertEqual(result['matched_patterns'], [])
        self.assertEqual(result['shadow_only_patterns'], ['a', 'b'])
        self.assertEqual(result['human_only_patterns'], ['c', 'd'])
        self.assertEqual(result['precision'], 0.0)
        self.assertEqual(result['recall'], 0.0)
        self.assertEqual(result['f1_score'], 0.0)

    def test_deterministic_output(self):
        shadow = ['b', 'a', 'c']
        human = ['c', 'a', 'd']
        first = build_ground_truth_comparison(shadow, human)
        second = build_ground_truth_comparison(copy.deepcopy(shadow), copy.deepcopy(human))
        self.assertEqual(first, second)

    def test_input_mutate_ed(self):
        shadow = ['a', 'b']
        human = ['a', 'c']
        original_shadow = copy.deepcopy(shadow)
        original_human = copy.deepcopy(human)
        build_ground_truth_comparison(shadow, human)
        self.assertEqual(shadow, original_shadow)
        self.assertEqual(human, original_human)


if __name__ == '__main__':
    unittest.main()
