"""Tests for Event Reconstructor — Sprint 9A"""
import unittest
from runtime_v7.event_reconstructor import (
    reconstruct_events,
    _extract_actors_from_text,
    _extract_action_verb,
    _detect_conflict,
    _detect_resolution,
)


class TestEventReconstructor(unittest.TestCase):
    """Test event reconstruction from evidence snippets."""

    def test_empty_evidence_returns_empty_events(self):
        """Empty evidence should return empty events list."""
        result = reconstruct_events(None)
        self.assertEqual(result['events'], [])
        self.assertEqual(result['event_sequence'], [])
        self.assertEqual(result['main_conflict'], '')

    def test_single_evidence_creates_one_event(self):
        """Single evidence item should create exactly one event."""
        evidence = {
            'setup': ['The hero begins his journey.']
        }
        result = reconstruct_events(evidence)
        self.assertEqual(len(result['events']), 1)
        self.assertIn('event_000', result['event_sequence'])

    def test_multiple_evidence_creates_ordered_sequence(self):
        """Multiple evidence items should create ordered sequence."""
        evidence = {
            'setup': ['Hero wakes up.'],
            'conflict': ['A monster appears.'],
            'resolution': ['Hero defeats monster.'],
        }
        result = reconstruct_events(evidence)
        self.assertEqual(len(result['events']), 3)
        self.assertEqual(len(result['event_sequence']), 3)
        self.assertEqual(result['event_sequence'], ['event_000', 'event_001', 'event_002'])

    def test_actors_extracted_from_characters(self):
        """Actors should be extracted using known characters."""
        characters = ['Orpheus', 'Eurydice', 'Hades']
        evidence = {
            'setup': ['Orpheus loved Eurydice deeply.']
        }
        result = reconstruct_events(evidence, characters=characters)
        event = result['events'][0]
        self.assertIn('Orpheus', event['actors'])
        self.assertIn('Eurydice', event['actors'])

    def test_source_sentence_ids_preserved(self):
        """source_sentence_id should be preserved in events."""
        evidence = {
            'setup': [
                {
                    'text': 'Hero wakes up.',
                    'source_sentence_id': 'p1:s1'
                }
            ]
        }
        result = reconstruct_events(evidence)
        event = result['events'][0]
        self.assertIn('p1:s1', event['source_sentence_ids'])

    def test_raw_evidence_not_copied_verbatim_as_action(self):
        """Raw evidence should not be copied verbatim into action field."""
        evidence_text = 'According to the text, the hero faced many challenges.'
        evidence = {'conflict': [evidence_text]}
        result = reconstruct_events(evidence)
        event = result['events'][0]
        # Action should be extracted, not full text
        self.assertNotEqual(event['action'], evidence_text)
        self.assertTrue(len(event['action']) < len(evidence_text))

    def test_conflict_candidate_detected(self):
        """Conflict indicators should mark event as conflict."""
        evidence = {
            'conflict': ['The hero faced a terrible problem and great danger.']
        }
        result = reconstruct_events(evidence)
        event = result['events'][0]
        self.assertTrue(event['conflict'])

    def test_resolution_candidate_detected(self):
        """Resolution indicators should be detected."""
        evidence = {
            'resolution': ['Finally, the hero succeeded and learned the lesson.']
        }
        result = reconstruct_events(evidence)
        # resolution should be captured at top level
        self.assertTrue(len(result['resolution']) > 0)

    def test_deterministic_output(self):
        """Same input should always produce same output."""
        characters = ['Alice', 'Bob']
        evidence = {
            'setup': ['Alice and Bob meet.'],
            'conflict': ['They disagree on important matters.'],
        }
        result1 = reconstruct_events(evidence, characters=characters)
        result2 = reconstruct_events(evidence, characters=characters)
        self.assertEqual(result1['events'], result2['events'])
        self.assertEqual(result1['event_sequence'], result2['event_sequence'])

    def test_input_not_mutated(self):
        """Original evidence dict should not be mutated."""
        original_evidence = {
            'setup': ['Hero starts journey.'],
            'conflict': ['Dragon appears.'],
        }
        import copy
        evidence_copy = copy.deepcopy(original_evidence)
        reconstruct_events(original_evidence)
        self.assertEqual(original_evidence, evidence_copy)

    def test_event_has_required_fields(self):
        """Each event should have all required fields."""
        evidence = {'setup': ['Something happens.']}
        result = reconstruct_events(evidence)
        event = result['events'][0]
        required_fields = [
            'event_id', 'actors', 'action', 'object', 'goal',
            'conflict', 'result', 'location_or_context',
            'importance', 'supporting_evidence_ids', 'source_sentence_ids'
        ]
        for field in required_fields:
            self.assertIn(field, event, f"Missing field: {field}")

    def test_importance_score_in_valid_range(self):
        """Importance score should be between 0 and 1."""
        evidence = {
            'setup': ['Small detail.'],
            'conflict': ['Major problem with consequence.'],
            'resolution': ['Hero succeeds with joy.'],
        }
        result = reconstruct_events(evidence)
        for event in result['events']:
            self.assertGreaterEqual(event['importance'], 0.0)
            self.assertLessEqual(event['importance'], 1.0)

    def test_extraction_with_dict_evidence_items(self):
        """Evidence items as dicts should be handled."""
        evidence = {
            'events': [
                {
                    'text': 'The hero made a decision.',
                    'source_sentence_id': 'p5:s3'
                },
                {
                    'text': 'The hero embarked on the journey.',
                    'source_sentence_id': 'p6:s1'
                }
            ]
        }
        result = reconstruct_events(evidence)
        self.assertEqual(len(result['events']), 2)
        self.assertIn('p5:s3', result['events'][0]['source_sentence_ids'])
        self.assertIn('p6:s1', result['events'][1]['source_sentence_ids'])

    def test_helper_extract_actors(self):
        """Test actor extraction helper."""
        characters = ['Orpheus', 'Eurydice', 'Hades']
        text = "Orpheus loved Eurydice deeply, despite Hades' opposition."
        actors = _extract_actors_from_text(text, characters)
        self.assertIn('Orpheus', actors)
        self.assertIn('Eurydice', actors)

    def test_helper_extract_action_verb(self):
        """Test action verb extraction helper."""
        text = "The hero decided to fight the dragon bravely."
        action = _extract_action_verb(text)
        self.assertTrue(len(action) > 0)
        self.assertLess(len(action), len(text))

    def test_helper_detect_conflict(self):
        """Test conflict detection helper."""
        conflict_text = "The hero faced a serious problem and great danger."
        no_conflict_text = "The hero walked in the garden."
        self.assertTrue(_detect_conflict(conflict_text))
        self.assertFalse(_detect_conflict(no_conflict_text))

    def test_helper_detect_resolution(self):
        """Test resolution detection helper."""
        resolution_text = "Finally, the hero succeeded and learned the truth."
        no_resolution_text = "The hero was walking through the forest."
        self.assertTrue(_detect_resolution(resolution_text))
        self.assertFalse(_detect_resolution(no_resolution_text))

    def test_quality_score_present(self):
        """Reconstruction quality score should be present."""
        evidence = {
            'setup': ['Hero begins.'],
            'conflict': ['Danger appears.'],
            'resolution': ['Hero triumphs.']
        }
        result = reconstruct_events(evidence)
        self.assertIn('event_reconstruction_quality', result)
        self.assertGreaterEqual(result['event_reconstruction_quality'], 0.0)
        self.assertLessEqual(result['event_reconstruction_quality'], 1.0)

    def test_no_internal_fields_in_output(self):
        """Output should not contain internal fields."""
        evidence = {'setup': ['Hero wakes.']}
        result = reconstruct_events(evidence)
        for event in result['events']:
            self.assertNotIn('_raw_evidence', event)
            self.assertNotIn('_section', event)

    def test_main_conflict_extracted(self):
        """Main conflict should be extracted from conflict section."""
        evidence = {
            'setup': ['Setup text'],
            'conflict': ['The main conflict occurs here.'],
            'resolution': ['Resolution text']
        }
        result = reconstruct_events(evidence)
        self.assertTrue(len(result['main_conflict']) > 0)
        self.assertIn('main conflict', result['main_conflict'].lower())

    def test_resolution_extracted(self):
        """Resolution should be extracted from resolution section."""
        evidence = {
            'setup': ['Setup'],
            'resolution': ['The hero finally succeeded.']
        }
        result = reconstruct_events(evidence)
        self.assertTrue(len(result['resolution']) > 0)

    def test_empty_dict_evidence_safe(self):
        """Empty evidence dict should be handled safely."""
        result = reconstruct_events({})
        self.assertEqual(result['events'], [])
        self.assertEqual(result['event_sequence'], [])

    def test_with_turkish_text(self):
        """Turkish text with special characters should work."""
        evidence = {
            'setup': ['Kahraman yolculuğuna başlıyor.'],
            'conflict': ['Tehlikeli bir çatışma başlıyor.'],
        }
        result = reconstruct_events(evidence)
        self.assertEqual(len(result['events']), 2)
        self.assertTrue(result['events'][1]['conflict'])


if __name__ == '__main__':
    unittest.main()
