import unittest
from runtime_v7.event_reconstructor import reconstruct_events


class TestEventReconstructorSourceIdNormalization(unittest.TestCase):
    def test_extracts_source_id_from_multiple_candidate_fields(self):
        evidence = {
            'setup': [
                {
                    'text': 'The hero begins the journey.',
                    'sentence_id': 's-12',
                    'page': 3,
                }
            ]
        }
        result = reconstruct_events(evidence)
        event = result['events'][0]
        self.assertIn('s-12', event['source_sentence_ids'])

    def test_fallback_source_ids_are_generated_when_missing(self):
        evidence = {
            'events': [
                {'text': 'The hero acts.'},
                {'text': 'The hero resolves.'},
            ]
        }
        result = reconstruct_events(evidence, payload_file='sample.json', book_index=2)
        sources = [event['source_sentence_ids'][0] for event in result['events']]
        self.assertEqual(sources, [
            'sample.json:2:0',
            'sample.json:2:1',
        ])
        self.assertEqual(
            [event['supporting_evidence_ids'][0] for event in result['events']],
            sources,
        )


if __name__ == '__main__':
    unittest.main()
