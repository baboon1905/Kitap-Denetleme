import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.semantic_orchestrator import run_semantic_orchestrator


class TestSemanticOrchestrator(unittest.TestCase):
    def test_empty_input_safe(self):
        result = run_semantic_orchestrator(payload={}, production_payload={}, feature_flags={'semantic_orchestrator_enabled': True})
        self.assertEqual(result['pattern_matches'], [])
        self.assertEqual(result['pattern_activations'], [])
        self.assertEqual(result['human_review_package'], [])
        self.assertTrue(result['safety']['shadow_only'])

    def test_deterministic_output(self):
        payload = {'summary_ir': {'themes': ['Adventure and friendship']}}
        prod = {'summary_ir': {'themes': ['Adventure and friendship']}}
        first = run_semantic_orchestrator(payload=payload, production_payload=prod, feature_flags={'semantic_orchestrator_enabled': True})
        second = run_semantic_orchestrator(payload=copy.deepcopy(payload), production_payload=copy.deepcopy(prod), feature_flags={'semantic_orchestrator_enabled': True})
        self.assertEqual(first['pattern_matches'], second['pattern_matches'])
        self.assertEqual(first['pattern_activations'], second['pattern_activations'])
        self.assertEqual(first['human_review_package'], second['human_review_package'])

    def test_stage_order_is_preserved(self):
        result = run_semantic_orchestrator(payload={'summary_ir': {'themes': ['Adventure and friendship']}}, production_payload={'summary_ir': {'themes': ['Adventure and friendship']}}, feature_flags={'semantic_orchestrator_enabled': True})
        self.assertEqual(result['stage_order'], [
            'pattern_match_producer',
            'confidence_engine',
            'semantic_monitor',
            'evidence_ranking',
            'explainability',
            'acceptance_gate',
            'human_review_package',
            'shadow_production_delta',
        ])

    def test_context_is_preserved(self):
        result = run_semantic_orchestrator(payload={'summary_ir': {'themes': ['Macera ve dostluk']}, 'semantic': {'theme_clusters': ['Dostluk ve dayanışma']}}, production_payload={'summary_ir': {'themes': ['Macera ve dostluk']}}, feature_flags={'semantic_orchestrator_enabled': True})
        self.assertTrue(any(item.get('pattern_id') == 'theme_adventure' for item in result['pattern_matches']))
        self.assertTrue(any(item.get('pattern_id') == 'theme_friendship' for item in result['pattern_matches']))

    def test_production_payload_not_modified(self):
        production_payload = {'summary_ir': {'themes': ['Adventure and friendship']}}
        original = copy.deepcopy(production_payload)
        run_semantic_orchestrator(payload={'summary_ir': {'themes': ['Adventure and friendship']}}, production_payload=production_payload, feature_flags={'semantic_orchestrator_enabled': True})
        self.assertEqual(production_payload, original)

    def test_shadow_only(self):
        result = run_semantic_orchestrator(payload={'summary_ir': {'themes': ['Adventure and friendship']}}, production_payload={'summary_ir': {'themes': ['Adventure and friendship']}}, feature_flags={'semantic_orchestrator_enabled': True})
        self.assertTrue(result['safety']['shadow_only'])
        self.assertFalse(result['safety']['production_output_changed'])
        self.assertTrue(result['safety']['equal_without_shadow'])


if __name__ == '__main__':
    unittest.main()
