import unittest

from runtime_v7.event_reconstructor import reconstruct_events


class TestEventSemanticEnrichment(unittest.TestCase):
    def test_reconstruct_events_enriches_semantic_fields_deterministically(self):
        evidence = {
            'setup': [
                'Kolomb, Atlas Okyanusu üzerinde batıya doğru yelken açtı.',
            ],
            'conflict': [
                'Fırtına nedeniyle mürettebat umudunu kaybetti.',
            ],
            'events': [
                'Karaya ulaştık ve yeni bir dünya keşfettik.',
            ],
            'resolution': [
                'Yolculuk başarıyla sonuçlandı.',
            ],
        }

        result = reconstruct_events(evidence, payload_file='test_payload', book_index=1)
        self.assertIn('events', result)
        self.assertGreaterEqual(len(result['events']), 4)

        first = result['events'][0]
        self.assertEqual(first['actors'], ['Kolomb'])
        self.assertEqual(first['action'], 'batıya doğru yelken açtı')
        self.assertEqual(first['object'], '')
        self.assertEqual(first['location_or_context'], 'Atlas Okyanusu')
        self.assertEqual(first['goal'], 'batıya yolculuk')
        self.assertEqual(first['cause'], '')
        self.assertEqual(first['effect'], '')
        self.assertLess(first['cause_confidence'], 0.5)
        self.assertLess(first['effect_confidence'], 0.5)
        self.assertEqual(first['narrative_function'], 'setup')
        self.assertEqual(first['temporal_marker'], 'beginning')
        self.assertEqual(first['resolution_state'], 'unresolved')

        # new extra tests for Turkish goal/object/location extraction
        helper_event = next(event for event in result['events'] if event['action'] == 'batıya doğru yelken açtı')
        self.assertEqual(helper_event['goal'], 'batıya yolculuk')
        self.assertEqual(helper_event['location_or_context'], 'Atlas Okyanusu')

        search_event = next(event for event in result['events'] if event['object'] == 'Yeni bir dünya')
        self.assertEqual(search_event['action'], 'karaya ulaştı')
        self.assertEqual(search_event['location_or_context'], '')
        self.assertEqual(search_event['goal'], 'karaya ulaşma')

        place_event = next(event for event in result['events'] if event['narrative_function'] == 'resolution')
        self.assertTrue(place_event['location_or_context'] == '' or isinstance(place_event['location_or_context'], str))

        conflict_event = next(event for event in result['events'] if event['conflict'])
        self.assertEqual(conflict_event['cause'], 'fırtına')
        self.assertEqual(conflict_event['effect'], 'mürettebat umudunu kaybetti')
        self.assertGreaterEqual(conflict_event['cause_confidence'], 0.5)
        self.assertGreaterEqual(conflict_event['effect_confidence'], 0.5)
        self.assertEqual(conflict_event['narrative_function'], 'inciting_incident')

        resolution_event = next(event for event in result['events'] if event.get('result'))
        self.assertTrue(resolution_event['result'])
        self.assertEqual(resolution_event['narrative_function'], 'resolution')
        self.assertEqual(resolution_event['resolution_state'], 'resolved')
        self.assertEqual(resolution_event['effect'], '')
        self.assertLess(resolution_event['effect_confidence'], 0.5)

        for event in result['events']:
            self.assertTrue(event['source_sentence_ids'])
            self.assertEqual(event['source_sentence_ids'], [event['supporting_evidence_ids'][0]])

        second_run = reconstruct_events(evidence, payload_file='test_payload', book_index=1)
        self.assertEqual(result['events'], second_run['events'])

    def test_turkish_goal_object_location_patterns(self):
        evidence = {
            'events': [
                'Ona yardım etmek için bir plan yaptılar.',
                'Çocuklar okulda bir kitap buldular.',
            ]
        }

        result = reconstruct_events(evidence, payload_file='test_payload', book_index=2)
        self.assertEqual(len(result['events']), 2)

        goal_event = result['events'][0]
        self.assertEqual(goal_event['goal'], 'ona yardım etmek')
        self.assertEqual(goal_event['object'], 'Bir plan')
        self.assertEqual(goal_event['location_or_context'], '')

        location_event = result['events'][1]
        self.assertEqual(location_event['location_or_context'], 'okulda')
        self.assertEqual(location_event['object'], 'Bir kitap')
        self.assertNotIn('okulda', location_event['actors'])

    def test_turkish_object_false_positives_are_filtered(self):
        evidence = {
            'events': [
                'Annesi, “Peki, Eren’in ailesi Pati’yi isteyecek mi bakalım?” diye sordu.',
                'El birliği yaparsak mutlaka bir çare buluruz.” “Ben bir şey düşündüm!” diye atıldı Yasemin.',
                'Barcelona’da bana karşı çok dostça davranan Fernando haftalarca beni görmeyi reddetti.',
            ]
        }

        result = reconstruct_events(evidence, payload_file='test_payload', book_index=4)
        self.assertEqual(len(result['events']), 3)

        self.assertEqual(result['events'][0]['object'], '')
        self.assertEqual(result['events'][1]['object'], '')
        self.assertEqual(result['events'][2]['object'], '')
        self.assertEqual(result['events'][2]['location_or_context'], 'Barcelona')

    def test_turkish_cause_effect_extraction_handles_causal_phrases(self):
        evidence = {
            'events': [
                'Geceleri düş görebildikleri için sizi sevmiyorlar.',
                'Bir süre sonra bunun bir şenlik ateşi olduğunu anladık.',
                'Bu üzücü tabloya rağmen, bu adalar, bitki örtüsü, hayvan topluluğu ve halkı açısından bana göre dünyanın en güzel yeriydi.',
            ]
        }

        result = reconstruct_events(evidence, payload_file='test_payload', book_index=3)
        self.assertEqual(len(result['events']), 3)

        causal_event = result['events'][0]
        self.assertEqual(causal_event['cause'], 'geceleri düş görebildikleri')
        self.assertEqual(causal_event['effect'], 'sizi sevmiyorlar')
        self.assertGreaterEqual(causal_event['cause_confidence'], 0.5)
        self.assertGreaterEqual(causal_event['effect_confidence'], 0.5)

        no_effect_event = result['events'][1]
        self.assertEqual(no_effect_event['cause'], '')
        self.assertEqual(no_effect_event['effect'], '')
        self.assertLess(no_effect_event['effect_confidence'], 0.5)
        self.assertNotEqual(no_effect_event['effect'], 'yeni bilgi edinimi')

        negative_contrast_event = result['events'][2]
        self.assertEqual(negative_contrast_event['cause'], '')
        self.assertEqual(negative_contrast_event['effect'], '')
        self.assertLess(negative_contrast_event['cause_confidence'], 0.5)
        self.assertLess(negative_contrast_event['effect_confidence'], 0.5)


if __name__ == '__main__':
    unittest.main()
