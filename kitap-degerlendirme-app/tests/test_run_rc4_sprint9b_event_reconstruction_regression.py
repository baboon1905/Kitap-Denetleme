"""
Tests for RC4 Sprint 9B Event Reconstruction Regression Check
Verifies that event reconstruction works correctly on Sprint 8C regression books
"""

import unittest
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.event_reconstructor import reconstruct_events

class TestEventReconstructionRegression(unittest.TestCase):
    """Regression tests for event reconstruction on Sprint 8C books"""
    
    @classmethod
    def setUpClass(cls):
        """Load Sprint 8C data once for all tests"""
        cls.sprint8c_file = Path(__file__).parent.parent / 'rc4_sprint8c_mapping_integration_results.json'
        
        if cls.sprint8c_file.exists():
            with open(cls.sprint8c_file, 'r', encoding='utf-8') as f:
                cls.sprint8c_data = json.load(f)
                cls.books = cls.sprint8c_data.get('books', [])
        else:
            cls.books = []
    
    def test_artifact_generates_file_and_structure(self):
        """Verify that regression script produces output file with correct structure"""
        output_file = Path(__file__).parent.parent / 'rc4_sprint9b_event_reconstruction_results.json'
        
        # Run the regression
        import subprocess
        script_path = Path(__file__).parent.parent / 'run_rc4_sprint9b_event_reconstruction_regression.py'
        result = subprocess.run([
            sys.executable, str(script_path)
        ], cwd=str(script_path.parent), capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0, f"Script failed: {result.stderr}")
        self.assertTrue(output_file.exists(), "Output file not created")
        
        # Verify structure
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_keys = {'sprint', 'timestamp', 'books', 'aggregate_metrics'}
        self.assertTrue(required_keys.issubset(data.keys()), 
                       f"Missing required keys in output: {required_keys - data.keys()}")
    
    def test_total_books_equals_three(self):
        """Verify that all 3 regression books are processed"""
        output_file = Path(__file__).parent.parent / 'rc4_sprint9b_event_reconstruction_results.json'
        
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            book_count = data.get('aggregate_metrics', {}).get('total_books', 0)
            self.assertEqual(book_count, 3, "Expected three regression books")

    def test_full_event_lists_are_preserved_per_book(self):
        """Verify that each book carries the full reconstructed event list"""
        output_file = Path(__file__).parent.parent / 'rc4_sprint9b_event_reconstruction_results.json'

        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for book in data.get('books', []):
            self.assertIn('reconstructed_events', book, "Missing reconstructed_events payload")
            self.assertIsInstance(book['reconstructed_events'], list)
            self.assertEqual(book['reconstructed_event_count'], len(book['reconstructed_events']))
            self.assertIsInstance(book.get('first_5_events', []), list)

    def test_aggregate_total_is_based_on_full_event_lists(self):
        """Verify aggregate totals use the full reconstructed event list"""
        output_file = Path(__file__).parent.parent / 'rc4_sprint9b_event_reconstruction_results.json'

        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        aggregate = data.get('aggregate_metrics', {})
        full_count = sum(len(book.get('reconstructed_events', [])) for book in data.get('books', []))

        self.assertEqual(aggregate.get('total_reconstructed_events', 0), full_count)

    def test_source_preservation_uses_full_event_list(self):
        """Verify preservation metrics are computed from full event lists"""
        output_file = Path(__file__).parent.parent / 'rc4_sprint9b_event_reconstruction_results.json'

        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        aggregate = data.get('aggregate_metrics', {})
        self.assertGreater(aggregate.get('source_sentence_id_preservation_rate', 0.0), 0.0)
    
    def test_total_reconstructed_events_greater_than_zero(self):
        """Verify that events were reconstructed from evidence"""
        output_file = Path(__file__).parent.parent / 'rc4_sprint9b_event_reconstruction_results.json'
        
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            total_events = data.get('aggregate_metrics', {}).get('total_reconstructed_events', 0)
            self.assertGreater(total_events, 0, "No events were reconstructed")
    
    def test_source_sentence_id_preservation_rate_greater_than_zero(self):
        """Verify that source traceability is maintained"""
        output_file = Path(__file__).parent.parent / 'rc4_sprint9b_event_reconstruction_results.json'
        
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            preservation_rate = data.get('aggregate_metrics', {}).get(
                'source_sentence_id_preservation_rate', 0.0
            )
            self.assertGreater(preservation_rate, 0.0, 
                             "Source sentence IDs not preserved in events")
    
    def test_deterministic_true(self):
        """Verify that determinism flag is set"""
        output_file = Path(__file__).parent.parent / 'rc4_sprint9b_event_reconstruction_results.json'
        
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            deterministic = data.get('aggregate_metrics', {}).get('deterministic_verified', False)
            self.assertTrue(deterministic, "Determinism not verified")
    
    def test_production_output_changed_false(self):
        """Verify shadow-only constraint: production output not changed"""
        output_file = Path(__file__).parent.parent / 'rc4_sprint9b_event_reconstruction_results.json'
        
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            changed = data.get('aggregate_metrics', {}).get('production_output_changed', False)
            self.assertFalse(changed, "Production output was modified (shadow-only constraint violated)")
    
    def test_runtime_pipeline_bound_false(self):
        """Verify that module is not bound to pipeline"""
        output_file = Path(__file__).parent.parent / 'rc4_sprint9b_event_reconstruction_results.json'
        
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            bound = data.get('aggregate_metrics', {}).get('runtime_pipeline_bound', False)
            self.assertFalse(bound, "Module is bound to runtime pipeline (should be standalone)")
    
    def test_average_quality_in_valid_range(self):
        """Verify that quality scores are in valid 0-1 range"""
        output_file = Path(__file__).parent.parent / 'rc4_sprint9b_event_reconstruction_results.json'
        
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            avg_quality = data.get('aggregate_metrics', {}).get(
                'average_event_reconstruction_quality', -1
            )
            self.assertGreaterEqual(avg_quality, 0.0, "Quality score below 0")
            self.assertLessEqual(avg_quality, 1.0, "Quality score above 1")


class TestEventReconstructorDirectly(unittest.TestCase):
    """Direct tests of event reconstructor on sample data"""
    
    def test_sample_evidence_reconstruction(self):
        """Test event reconstruction on sample evidence"""
        evidence = [
            "Kristof Kolomb denizde krizi çözdü.",
            "Gemide tehlike ve korkuyla karşılaştılar.",
            "Sonunda kurtarıldılar ve mutlu oldular."
        ]
        characters = ["Kristof Kolomb"]
        themes = ["Adventure", "Discovery"]
        
        result = reconstruct_events(evidence, characters, themes)
        
        self.assertIn('events', result)
        self.assertIn('event_reconstruction_quality', result)
        self.assertGreater(len(result['events']), 0, "No events reconstructed")
        
        quality = result['event_reconstruction_quality']
        self.assertGreaterEqual(quality, 0.0)
        self.assertLessEqual(quality, 1.0)
    
    def test_empty_evidence_returns_empty_events(self):
        """Test that empty evidence produces empty event list"""
        result = reconstruct_events([], [], [])
        
        self.assertEqual(len(result['events']), 0)
        self.assertEqual(result['event_reconstruction_quality'], 0.0)
    
    def test_deterministic_output(self):
        """Test that identical input produces identical output"""
        evidence = ["Çocuk oyun oynadı.", "Oyunda kazandı."]
        characters = []
        themes = []
        
        result1 = reconstruct_events(evidence, characters, themes)
        result2 = reconstruct_events(evidence, characters, themes)
        
        # Convert to JSON and back for comparison (handles any differences in object identity)
        json1 = json.dumps(result1, sort_keys=True)
        json2 = json.dumps(result2, sort_keys=True)
        
        self.assertEqual(json1, json2, "Deterministic constraint violated")


if __name__ == '__main__':
    unittest.main(verbosity=2)
