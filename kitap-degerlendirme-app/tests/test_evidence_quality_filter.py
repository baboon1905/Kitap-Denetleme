import unittest

from runtime_v7.evidence_quality_filter import (
    deduplicate_evidence,
    filter_summary_ir_evidence,
    is_noise,
    normalize_text,
)


class TestEvidenceQualityFilter(unittest.TestCase):
    def test_normalize_text_repairs_split_pdf_words(self):
        text = 'Çift li ğe gidecek.'
        normalized = normalize_text(text)
        self.assertIn('Çiftliğe', normalized)
        self.assertFalse('  ' in normalized)

    def test_is_noise_filters_page_headers_and_fragments(self):
        self.assertTrue(is_noise('Sayfa 47'))
        self.assertTrue(is_noise('PDF 3'))
        self.assertTrue(is_noise('...'))
        self.assertFalse(is_noise('Kahraman okula gidecek ve yeni bir arkadaş edinecek.'))

    def test_deduplicate_evidence_merges_same_text(self):
        items = [
            {'text': 'Kahraman okula gidecek.', 'source_sentence_id': 's1'},
            {'text': 'Kahraman okula gidecek.', 'source_sentence_id': 's2'},
            {'text': 'Kahraman eve dönecek.', 'source_sentence_id': 's3'},
        ]
        filtered, removed = deduplicate_evidence(items)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(removed, 1)
        self.assertEqual(filtered[0]['source_sentence_ids'], ['s1', 's2'])

    def test_deduplicate_evidence_merges_semantically_similar_text(self):
        items = [
            {'text': 'Kahraman okula gidiyor.', 'source_sentence_id': 's1'},
            {'text': 'Kahraman okula gidecek.', 'source_sentence_id': 's2'},
            {'text': 'Kahraman eve dönecek.', 'source_sentence_id': 's3'},
        ]
        filtered, removed = deduplicate_evidence(items)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(removed, 1)
        self.assertEqual(filtered[0]['source_sentence_ids'], ['s1', 's2'])

    def test_filter_summary_ir_evidence_contract_and_filtering(self):
        summary_ir = {
            'evidence_snippets': {
                'setup': [
                    'Sayfa 12',
                    {'text': 'Kahraman uyandı ve dışarı çıktı.', 'source_sentence_id': 's1'},
                ],
                'conflict': [
                    {'text': 'Kahraman kayboldu.', 'source_sentence_id': 's2'},
                    {'text': 'Sayfa 13'},
                ],
                'events': [
                    {'text': 'Kahraman kayboldu.', 'source_sentence_id': 's3'},
                    {'text': 'Kahraman kayboldu.', 'source_sentence_id': 's4'},
                    'Büyülü kapıdan geçti.',
                ],
                'resolution': [
                    'Sonunda eve döndü.',
                    '---',
                ],
            }
        }

        result = filter_summary_ir_evidence(summary_ir)
        self.assertIn('filtered_evidence', result)
        self.assertIn('metrics', result)
        self.assertEqual(result['metrics']['input_count'], 9)
        self.assertEqual(result['metrics']['output_count'], 5)
        self.assertEqual(result['metrics']['duplicates_removed'], 1)
        self.assertEqual(result['metrics']['noise_removed'], 3)
        self.assertEqual(result['metrics']['low_quality_removed'], 0)
        self.assertTrue(result['metrics']['avg_quality_score_before'] > 0)
        self.assertTrue(result['metrics']['avg_quality_score_after'] > 0)
        self.assertEqual(result['filtered_evidence']['setup'][0]['source_sentence_ids'], ['s1'])
        self.assertEqual(result['filtered_evidence']['conflict'][0]['source_sentence_ids'], ['s2'])
        self.assertTrue(any(set(item['source_sentence_ids']) == {'s3', 's4'} for item in result['filtered_evidence']['events']))
        for section, items in result['filtered_evidence'].items():
            for item in items:
                self.assertIn('semantic_score', item)
                self.assertIn('ocr_quality_score', item)
                self.assertIn('final_quality_score', item)
                self.assertIn('retained', item)
                self.assertEqual(item['removal_reason'], 'retained')

    def test_filter_summary_ir_evidence_removes_low_quality_fragmented_text(self):
        summary_ir = {
            'evidence_snippets': {
                'setup': [
                    {'text': 'am ca sı nan', 'source_sentence_id': 's1'},
                    {'text': 'Gerçek cümle doğru.', 'source_sentence_id': 's2'},
                    {'text': 'Gerçek cümle ikinci.', 'source_sentence_id': 's3'},
                ]
            }
        }

        result = filter_summary_ir_evidence(summary_ir)
        self.assertEqual(result['metrics']['input_count'], 3)
        self.assertEqual(result['metrics']['noise_removed'], 0)
        self.assertEqual(result['metrics']['low_quality_removed'], 1)
        self.assertEqual(result['metrics']['output_count'], 2)
        self.assertTrue(result['metrics']['avg_quality_score_after'] >= result['metrics']['avg_quality_score_before'])
        self.assertEqual(len(result['filtered_evidence']['setup']), 2)
        self.assertEqual(result['filtered_evidence']['setup'][0]['removal_reason'], 'retained')
        self.assertTrue(all(item['source_sentence_ids'] for item in result['filtered_evidence']['setup']))

    def test_filter_summary_ir_evidence_is_deterministic(self):
        summary_ir = {
            'evidence_snippets': {
                'events': [
                    {'text': 'Kahraman kahraman.', 'source_sentence_id': 's1'},
                    {'text': 'Kahraman kahraman.', 'source_sentence_id': 's2'},
                    {'text': 'Kahraman okula gidecek.', 'source_sentence_id': 's3'},
                ]
            }
        }
        first = filter_summary_ir_evidence(summary_ir)
        second = filter_summary_ir_evidence(summary_ir)
        self.assertEqual(first, second)
        self.assertEqual(first['filtered_evidence']['events'][0]['source_sentence_ids'], ['s1', 's2'])

    def test_filter_summary_ir_evidence_honors_section_minimum_retention(self):
        summary_ir = {
            'evidence_snippets': {
                'setup': [
                    {'text': f'Cümle {i} in setup.', 'source_sentence_id': f's{i}'}
                    for i in range(10)
                ],
            }
        }

        result = filter_summary_ir_evidence(summary_ir)
        self.assertEqual(result['metrics']['section_input_counts']['setup'], 10)
        self.assertGreaterEqual(result['metrics']['section_output_counts']['setup'], 5)
        self.assertEqual(result['metrics']['section_retention_shortfall_counts']['setup'], 0)
        self.assertEqual(result['metrics']['retention_shortfall_count'], 0)
        self.assertEqual(result['metrics']['retention_shortfall_reason'], '')
        self.assertTrue(all(item['retained'] for item in result['filtered_evidence']['setup']))
        self.assertEqual(len(result['filtered_evidence']['setup']), result['metrics']['section_output_counts']['setup'])

    def test_filter_summary_ir_evidence_preserves_source_sentence_ids_with_minimum_retention(self):
        summary_ir = {
            'evidence_snippets': {
                'events': [
                    {'text': 'Kahraman okula gidecek.', 'source_sentence_id': 's1'},
                    {'text': 'Kahraman eve dönecek.', 'source_sentence_id': 's2'},
                    {'text': 'Kahraman yüzme havuzuna gidecek.', 'source_sentence_id': 's3'},
                    {'text': 'Kahraman yüzme havuzuna dönecek.', 'source_sentence_id': 's4'},
                    {'text': 'Yeni kahraman ortaya çıkacak.', 'source_sentence_id': 's5'},
                    {'text': 'Oyuncular sahneye çıktı.', 'source_sentence_id': 's6'},
                ]
            }
        }

        result = filter_summary_ir_evidence(summary_ir)
        self.assertTrue(result['metrics']['section_input_counts']['events'] >= 6)
        self.assertGreaterEqual(result['metrics']['section_output_counts']['events'], 3)
        self.assertTrue(result['metrics']['source_sentence_ids_preserved'] if 'source_sentence_ids_preserved' in result['metrics'] else True)
        self.assertTrue(all(isinstance(item['source_sentence_ids'], list) for item in result['filtered_evidence']['events']))
        self.assertTrue(all(item['source_sentence_ids'] for item in result['filtered_evidence']['events']))


if __name__ == '__main__':
    unittest.main()
