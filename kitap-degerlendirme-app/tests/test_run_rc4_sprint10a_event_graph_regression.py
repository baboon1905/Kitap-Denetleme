import json
import subprocess
import sys
import unittest
from pathlib import Path


class TestRunRc4Sprint10aEventGraphRegression(unittest.TestCase):
    def test_artifact_generates_file_and_structure(self):
        script_path = Path(__file__).parent.parent / 'run_rc4_sprint10a_event_graph_regression.py'
        output_file = Path(__file__).parent.parent / 'rc4_sprint10a_event_graph_results.json'

        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(script_path.parent),
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(output_file.exists(), 'Output artifact was not created')

        with open(output_file, 'r', encoding='utf-8') as handle:
            data = json.load(handle)

        self.assertIn('books', data)
        self.assertIn('aggregate_metrics', data)
        self.assertEqual(data['aggregate_metrics']['deterministic'], True)
        self.assertEqual(data['aggregate_metrics']['production_output_changed_any'], False)
        self.assertEqual(data['aggregate_metrics']['runtime_pipeline_bound_any'], False)

    def test_aggregate_metrics_expectations(self):
        script_path = Path(__file__).parent.parent / 'run_rc4_sprint10a_event_graph_regression.py'
        output_file = Path(__file__).parent.parent / 'rc4_sprint10a_event_graph_results.json'

        subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(script_path.parent),
            capture_output=True,
            text=True,
            check=True,
        )

        with open(output_file, 'r', encoding='utf-8') as handle:
            data = json.load(handle)

        aggregate = data['aggregate_metrics']

        self.assertEqual(aggregate['total_books'], 3)
        self.assertEqual(aggregate['total_input_events'], 87)
        self.assertGreater(aggregate['total_event_groups'], 0)
        self.assertLess(aggregate['total_event_groups'], aggregate['total_input_events'])
        self.assertTrue(aggregate['deterministic'])
        self.assertFalse(aggregate['production_output_changed_any'])
        self.assertFalse(aggregate['runtime_pipeline_bound_any'])

    def test_runner_uses_full_reconstructed_event_lists(self):
        output_file = Path(__file__).parent.parent / 'rc4_sprint10a_event_graph_results.json'
        source_file = Path(__file__).parent.parent / 'rc4_sprint9b_event_reconstruction_results.json'

        with open(output_file, 'r', encoding='utf-8') as handle:
            data = json.load(handle)

        with open(source_file, 'r', encoding='utf-8') as handle:
            source_data = json.load(handle)

        source_books = source_data.get('books', [])
        for book_result, source_book in zip(data['books'], source_books):
            expected_count = len(source_book.get('reconstructed_events', []))
            self.assertEqual(book_result['input_event_count'], expected_count)

    def test_first_5_events_are_not_used_as_input(self):
        output_file = Path(__file__).parent.parent / 'rc4_sprint10a_event_graph_results.json'

        with open(output_file, 'r', encoding='utf-8') as handle:
            data = json.load(handle)

        for book in data['books']:
            if book['input_event_count'] > 0:
                self.assertGreater(book['input_event_count'], 5)
        self.assertEqual(data['aggregate_metrics']['total_input_events'], 87)
        self.assertTrue(data['aggregate_metrics']['deterministic'])


if __name__ == '__main__':
    unittest.main()
