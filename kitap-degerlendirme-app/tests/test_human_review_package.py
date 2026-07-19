import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.human_review_package import build_human_review_package


class TestHumanReviewPackage(unittest.TestCase):
    def test_same_input_same_package(self):
        pattern_activations = [{'pattern_id': 'theme_adventure', 'status': 'active', 'raw_confidence': 0.55, 'calibrated_confidence': 0.59, 'evidence_count': 2}]
        ranked_evidence = [{'pattern_id': 'theme_adventure', 'rank_score': 6.0, 'rank': 1}]
        semantic_explanations = [{'pattern_id': 'theme_adventure', 'reasoning': 'clear support', 'supporting_signals': ['evidence_count=2']}] 
        acceptance_decisions = [{'pattern_id': 'theme_adventure', 'decision': 'accepted', 'decision_score': 1.0}]
        delta_analysis = {'coverage_delta': 0.2, 'overlap_score': 0.8}

        first = build_human_review_package(pattern_activations, ranked_evidence, semantic_explanations, acceptance_decisions, delta_analysis)
        second = build_human_review_package(pattern_activations, ranked_evidence, semantic_explanations, acceptance_decisions, delta_analysis)
        self.assertEqual(first, second)

    def test_empty_input_empty_package(self):
        self.assertEqual(build_human_review_package([], [], [], [], {}), [])

    def test_input_not_mutated(self):
        pattern_activations = [{'pattern_id': 'theme_adventure', 'status': 'active', 'raw_confidence': 0.55, 'calibrated_confidence': 0.59, 'evidence_count': 2}]
        ranked_evidence = [{'pattern_id': 'theme_adventure', 'rank_score': 6.0, 'rank': 1}]
        semantic_explanations = [{'pattern_id': 'theme_adventure', 'reasoning': 'clear support', 'supporting_signals': ['evidence_count=2']}] 
        acceptance_decisions = [{'pattern_id': 'theme_adventure', 'decision': 'accepted', 'decision_score': 1.0}]
        delta_analysis = {'coverage_delta': 0.2, 'overlap_score': 0.8}
        original = copy.deepcopy((pattern_activations, ranked_evidence, semantic_explanations, acceptance_decisions, delta_analysis))

        build_human_review_package(pattern_activations, ranked_evidence, semantic_explanations, acceptance_decisions, delta_analysis)
        self.assertEqual((pattern_activations, ranked_evidence, semantic_explanations, acceptance_decisions, delta_analysis), original)

    def test_missing_explanation_results_in_review_recommendation(self):
        package = build_human_review_package(
            [{'pattern_id': 'theme_courage', 'status': 'candidate', 'raw_confidence': 0.45, 'calibrated_confidence': 0.51, 'evidence_count': 1}],
            [{'pattern_id': 'theme_courage', 'rank_score': 2.0, 'rank': 2}],
            [],
            [{'pattern_id': 'theme_courage', 'decision': 'review', 'decision_score': 0.5}],
            {'coverage_delta': 0.0, 'overlap_score': 0.3},
        )
        self.assertEqual(package[0]['review_recommendation'], 'review_human')

    def test_accepted_decision_results_in_approve_candidate(self):
        package = build_human_review_package(
            [{'pattern_id': 'theme_resilience', 'status': 'active', 'raw_confidence': 0.72, 'calibrated_confidence': 0.75, 'evidence_count': 3}],
            [{'pattern_id': 'theme_resilience', 'rank_score': 6.0, 'rank': 1}],
            [{'pattern_id': 'theme_resilience', 'reasoning': 'clear support', 'supporting_signals': ['evidence_count=3']}],
            [{'pattern_id': 'theme_resilience', 'decision': 'accepted', 'decision_score': 1.0}],
            {'coverage_delta': 0.2, 'overlap_score': 0.9},
        )
        self.assertEqual(package[0]['review_recommendation'], 'approve_candidate')

    def test_no_book_specific_heuristic(self):
        package = build_human_review_package(
            [{'pattern_id': 'theme_adventure', 'status': 'active', 'raw_confidence': 0.7, 'calibrated_confidence': 0.72, 'evidence_count': 2}],
            [{'pattern_id': 'theme_adventure', 'rank_score': 5.0, 'rank': 1}],
            [{'pattern_id': 'theme_adventure', 'reasoning': 'support', 'supporting_signals': ['evidence_count=2']}],
            [{'pattern_id': 'theme_adventure', 'decision': 'review', 'decision_score': 0.5}],
            {'coverage_delta': 0.1, 'overlap_score': 0.7},
        )
        joined = ' '.join(str(item) for item in package).lower()
        self.assertNotIn('book', joined)
        self.assertNotIn('kitap', joined)


if __name__ == '__main__':
    unittest.main()
