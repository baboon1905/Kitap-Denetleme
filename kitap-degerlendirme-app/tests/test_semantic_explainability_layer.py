import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.semantic_explainability_layer import build_semantic_explanations


class TestSemanticExplainabilityLayer(unittest.TestCase):
    def test_same_input_same_explanation(self):
        activations = [
            {
                'pattern_id': 'theme_adventure',
                'status': 'active',
                'evidence_count': 2,
                'source': 'summary_ir.themes',
                'raw_confidence': 0.55,
                'calibrated_confidence': 0.59,
            }
        ]
        
        first = build_semantic_explanations(activations)
        second = build_semantic_explanations(activations)
        self.assertEqual(first, second)

    def test_empty_input_empty_explanation(self):
        self.assertEqual(build_semantic_explanations([]), [])

    def test_confidence_fields_unchanged_in_input(self):
        activations = [
            {
                'pattern_id': 'theme_adventure',
                'status': 'active',
                'evidence_count': 2,
                'source': 'summary_ir.themes',
                'raw_confidence': 0.55,
                'calibrated_confidence': 0.59,
            }
        ]
        original = copy.deepcopy(activations)
        
        build_semantic_explanations(activations)
        self.assertEqual(activations, original)

    def test_ranking_fields_unchanged_in_input(self):
        ranked = [
            {
                'pattern_id': 'theme_adventure',
                'rank': 1,
                'rank_score': 4.5,
                'ranking_signals': {'evidence_count': 2, 'source_weight': 0.8},
            }
        ]
        original = copy.deepcopy(ranked)
        
        build_semantic_explanations([], ranked)
        self.assertEqual(ranked, original)

    def test_delta_fields_unchanged_in_input(self):
        delta = {
            'coverage_delta': 0.5,
            'overlap_score': 0.6,
        }
        original = copy.deepcopy(delta)
        
        build_semantic_explanations([], [], delta)
        self.assertEqual(delta, original)

    def test_no_book_specific_heuristic(self):
        activations = [
            {
                'pattern_id': 'theme_adventure',
                'status': 'active',
                'evidence_count': 2,
                'source': 'summary_ir.themes',
                'raw_confidence': 0.55,
                'calibrated_confidence': 0.59,
            }
        ]
        
        explanations = build_semantic_explanations(activations)
        explanation_text = str(explanations).lower()
        
        self.assertNotIn('kitap', explanation_text)
        self.assertNotIn('book', explanation_text)
        self.assertNotIn('specific', explanation_text)

    def test_explanation_structure(self):
        activations = [
            {
                'pattern_id': 'theme_friendship',
                'status': 'active',
                'evidence_count': 3,
                'source': 'semantic.theme_clusters',
                'raw_confidence': 0.65,
                'calibrated_confidence': 0.70,
            }
        ]
        ranked = [
            {
                'pattern_id': 'theme_friendship',
                'rank': 1,
                'rank_score': 5.2,
                'ranking_signals': {'evidence_count': 3, 'source_weight': 1.0, 'semantic_density': 0.1, 'cluster_support': 1},
            }
        ]
        
        explanations = build_semantic_explanations(activations, ranked)
        self.assertEqual(len(explanations), 1)
        
        expl = explanations[0]
        self.assertIn('pattern_id', expl)
        self.assertIn('decision', expl)
        self.assertIn('reasoning', expl)
        self.assertIn('supporting_signals', expl)
        self.assertIn('confidence_level', expl)
        self.assertIn('rank_context', expl)
        self.assertIn('audit_trail', expl)
        
        self.assertEqual(expl['pattern_id'], 'theme_friendship')
        self.assertIn('active', expl['decision'].lower())
        self.assertIn('semantic', expl['reasoning'].lower())


if __name__ == '__main__':
    unittest.main()
