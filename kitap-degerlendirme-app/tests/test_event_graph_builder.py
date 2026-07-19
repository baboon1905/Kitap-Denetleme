import json
import unittest

from runtime_v7.event_graph_builder import build_event_graph


class TestEventGraphBuilder(unittest.TestCase):
    def test_groups_events_with_same_actor_goal_and_conflict(self):
        reconstructed_events = [
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
                'action': 'searched the cave',
                'goal': 'find treasure',
                'conflict': False,
                'importance': 0.8,
            },
            {
                'event_id': 'event_002',
                'actors': ['Bob'],
                'action': 'fought the dragon',
                'goal': 'save the village',
                'conflict': True,
                'importance': 1.0,
            },
        ]

        result = build_event_graph(reconstructed_events)

        self.assertEqual(len(result['event_groups']), 2)
        self.assertEqual(result['event_groups'][0]['chronology'], ['event_000', 'event_001'])
        self.assertEqual(result['event_groups'][1]['chronology'], ['event_002'])
        self.assertEqual(result['event_groups'][0]['actors'], ['Alice'])
        self.assertEqual(result['event_groups'][0]['main_event'], 'entered the forest')

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
        self.assertEqual(result1['event_groups'][0]['supporting_events'], ['event_001'])
        self.assertIn('group_', result1['event_groups'][0]['group_id'])


if __name__ == '__main__':
    unittest.main()
