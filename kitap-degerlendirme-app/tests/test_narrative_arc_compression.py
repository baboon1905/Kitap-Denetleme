import json
import subprocess
import sys
import unittest
from pathlib import Path

from runtime_v7.event_graph_builder import build_event_graph


class TestNarrativeArcCompression(unittest.TestCase):
    def test_build_event_graph_returns_narrative_arcs(self):
        events = [
            {
                'event_id': 'event_000',
                'actors': ['Kristof', 'Kolomb'],
                'action': 'Karaya ulaşmak için yelken açtım',
                'goal': 'Batıya yolculuk',
                'conflict': False,
                'result': 'Yolculuk başladı',
                'importance': 0.8,
                'source_sentence_ids': ['s1'],
            },
            {
                'event_id': 'event_001',
                'actors': ['Kristof', 'Kolomb'],
                'action': 'Mürettebatın morale ihtiyacı vardı',
                'goal': 'Batıya yolculuk',
                'conflict': False,
                'result': 'Yolculuk başladı',
                'importance': 0.7,
                'source_sentence_ids': ['s2'],
            },
            {
                'event_id': 'event_002',
                'actors': ['Kristof', 'Kolomb'],
                'action': 'Fırtına nedeniyle umudunu kaybetti',
                'goal': 'Batıya yolculuk',
                'conflict': True,
                'result': 'Umutsuzluk arttı',
                'importance': 0.9,
                'source_sentence_ids': ['s3'],
            },
            {
                'event_id': 'event_003',
                'actors': ['Kristof', 'Kolomb'],
                'action': 'Karaya ulaştı',
                'goal': 'Batıya yolculuk',
                'conflict': True,
                'result': 'Karaya ulaşıldı',
                'importance': 1.0,
                'source_sentence_ids': ['s4'],
            },
        ]

        result = build_event_graph(events)

        self.assertIn('arcs', result)
        self.assertGreaterEqual(len(result['arcs']), 1)
        arc = result['arcs'][0]
        self.assertIn('arc_id', arc)
        self.assertIn('title', arc)
        self.assertIn('actors', arc)
        self.assertIn('objective', arc)
        self.assertIn('conflict', arc)
        self.assertIn('progression', arc)
        self.assertIn('resolution', arc)
        self.assertIn('supporting_events', arc)
        self.assertIn('source_sentence_ids', arc)
        self.assertIn('importance', arc)
        self.assertTrue(arc['title'])


class TestNarrativeArcSemanticHeuristics(unittest.TestCase):
    def test_build_event_graph_uses_semantic_fields_for_title_and_objective(self):
        events = [
            {
                'event_id': 'event_000',
                'actors': ['Kristof', 'Kolomb'],
                'action': 'Karaya ulaşmak için yelken açtım',
                'goal': 'Batıya yolculuk',
                'object': 'Yeni dünya',
                'location_or_context': 'Atlas Okyanusu',
                'conflict': False,
                'result': 'Yolculuk başladı',
                'importance': 0.8,
                'source_sentence_ids': ['s1'],
            },
            {
                'event_id': 'event_001',
                'actors': ['Kristof', 'Kolomb'],
                'action': 'Fırtına nedeniyle umudum sarsıldı',
                'goal': 'Batıya yolculuk',
                'object': 'Yeni dünya',
                'location_or_context': 'Atlas Okyanusu',
                'conflict': True,
                'result': 'Umutsuzluk arttı',
                'importance': 0.9,
                'source_sentence_ids': ['s2'],
            },
            {
                'event_id': 'event_002',
                'actors': ['Kristof', 'Kolomb'],
                'action': 'Karaya ulaştık',
                'goal': 'Batıya yolculuk',
                'object': 'Yeni dünya',
                'location_or_context': 'Karayipler',
                'conflict': True,
                'result': 'Karaya ulaşıldı',
                'importance': 1.0,
                'source_sentence_ids': ['s3'],
            },
        ]

        result = build_event_graph(events)
        self.assertGreaterEqual(len(result['arcs']), 1)
        arc = result['arcs'][0]
        self.assertNotEqual(arc['title'], 'Yeni Bir Aşama')
        self.assertNotEqual(arc['objective'], 'Narrative objective')
        self.assertNotEqual(arc['resolution'], 'Resolution pending')


class TestRunRc4Sprint10cNarrativeArcRegression(unittest.TestCase):
    def test_regression_script_writes_expected_arc_artifact(self):
        script_path = Path(__file__).parent.parent / 'run_rc4_sprint10c_narrative_arc_regression.py'
        output_file = Path(__file__).parent.parent / 'rc4_sprint10c_narrative_arc_results.json'

        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(script_path.parent),
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(output_file.exists(), 'Narrative arc regression artifact was not created')

        with open(output_file, 'r', encoding='utf-8') as handle:
            data = json.load(handle)

        self.assertEqual(data['aggregate_metrics']['total_books'], 3)
        self.assertEqual(data['aggregate_metrics']['total_input_events'], 87)
        self.assertGreater(data['aggregate_metrics']['total_arc_count'], 0)
        self.assertLess(data['aggregate_metrics']['total_arc_count'], data['aggregate_metrics']['total_input_events'])
        for book in data['books']:
            if book['event_count'] > 0:
                self.assertGreaterEqual(book['arc_count'], 12)
                self.assertLessEqual(book['arc_count'], 18)
        self.assertTrue(data['aggregate_metrics']['deterministic'])


if __name__ == '__main__':
    unittest.main()
