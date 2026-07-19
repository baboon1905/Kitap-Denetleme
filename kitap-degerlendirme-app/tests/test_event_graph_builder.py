import json
import unittest

from runtime_v7.event_graph_builder import build_event_graph, _generate_title, _infer_objective


class TestEventGraphBuilder(unittest.TestCase):
    def test_historical_exploration_graph_patterns_are_scoped(self):
        exploration_event = {
            'action': '',
            'object': 'Yeni dünya',
            'location_or_context': '',
        }
        unrelated_event = {
            'action': '',
            'object': 'Yeni bir oyun',
            'location_or_context': '',
        }

        self.assertEqual(_infer_objective(exploration_event), 'keşif')
        self.assertEqual(
            _generate_title(exploration_event, [], '', ''),
            'Yeni Dünyanın Keşfi',
        )
        self.assertEqual(_infer_objective(unrelated_event), '')
        self.assertNotEqual(
            _generate_title(unrelated_event, [], '', ''),
            'Yeni Dünyanın Keşfi',
        )

    def test_groups_events_into_narrative_arcs(self):
        reconstructed_events = [
            {
                'event_id': 'event_000',
                'actors': ['Alice'],
                'action': 'deniz yolculuğuna başladı',
                'goal': 'batıya yolculuk',
                'conflict': False,
                'importance': 0.7,
            },
            {
                'event_id': 'event_001',
                'actors': ['Alice'],
                'action': 'yelken açarak yolculuğa devam etti',
                'goal': 'batıya yolculuk',
                'conflict': False,
                'importance': 0.8,
            },
            {
                'event_id': 'event_002',
                'actors': ['Bob'],
                'action': 'karaya ulaştı',
                'goal': 'karaya ulaşma',
                'conflict': True,
                'importance': 1.0,
            },
        ]

        result = build_event_graph(reconstructed_events)

        self.assertEqual(len(result['arcs']), 2)
        self.assertEqual(result['arcs'][0]['progression'], ['event_000', 'event_001'])
        self.assertEqual(result['arcs'][1]['progression'], ['event_002'])
        self.assertEqual(result['arcs'][0]['actors'], ['Alice'])
        self.assertEqual(result['arcs'][0]['arc_id'], 'arc_000')

    def test_accepts_reconstructed_events_payload_and_is_deterministic(self):
        reconstructed_events = {
            'events': [
                {
                    'event_id': 'event_000',
                    'actors': ['Alice'],
                    'action': 'entered the forest',
                    'goal': 'find treasure',
                    'conflict': False,
                    'importance': 0.7,
                },
                {
                    'event_id': 'event_001',
                    'actors': ['Alice'],
                    'action': 'found a map',
                    'goal': 'find treasure',
                    'conflict': False,
                    'importance': 0.8,
                },
            ]
        }

        result1 = build_event_graph(reconstructed_events)
        result2 = build_event_graph(reconstructed_events)

        self.assertEqual(result1, result2)
        self.assertEqual(result1['arcs'][0]['supporting_events'], ['event_001'])
        self.assertEqual(result1['arcs'][0]['arc_id'], 'arc_000')


if __name__ == '__main__':
    unittest.main()
