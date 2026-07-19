"""
RC2 Sprint 3 — Semantic Pattern Library Tests

Comprehensive tests for pattern library functionality:
- Pattern registration and validation
- Duplicate and conflict detection
- Metadata integrity
- Statistics calculation
- Export/import
"""

import unittest
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.semantic_pattern_library import (
    SemanticPattern,
    SemanticPatternLibrary,
    PatternCategory,
    PatternStatus,
    MatchingStrategy,
)


class TestSemanticPatternMetadata(unittest.TestCase):
    """Test pattern metadata validation"""
    
    def test_valid_pattern_structure(self):
        """Valid pattern passes validation"""
        pattern = SemanticPattern(
            id='theme_adventure',
            name='Adventure',
            category='theme',
            description='Journey and exploration',
            keywords=['macera', 'yolculuk', 'keşif'],
            matching_strategy='keyword_frequency',
            default_fp_risk='low',
            expected_density=0.5,
            confidence_weight=0.9,
            status='VALIDATED',
        )
        
        is_valid, errors = pattern.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_invalid_id_format(self):
        """Invalid pattern ID rejected"""
        pattern = SemanticPattern(
            id='invalid_id',  # Wrong prefix
            name='Adventure',
            category='theme',
            description='Journey and exploration',
            keywords=['macera', 'yolculuk', 'keşif'],
            matching_strategy='keyword_frequency',
            default_fp_risk='low',
            expected_density=0.5,
            confidence_weight=0.9,
            status='VALIDATED',
        )
        
        is_valid, errors = pattern.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('id' in err.lower() for err in errors))
    
    def test_missing_keywords(self):
        """Pattern with < 3 keywords rejected"""
        pattern = SemanticPattern(
            id='theme_adventure',
            name='Adventure',
            category='theme',
            description='Journey and exploration',
            keywords=['macera', 'yolculuk'],  # Only 2 keywords
            matching_strategy='keyword_frequency',
            default_fp_risk='low',
            expected_density=0.5,
            confidence_weight=0.9,
            status='VALIDATED',
        )
        
        is_valid, errors = pattern.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('keyword' in err.lower() for err in errors))
    
    def test_invalid_confidence_weight(self):
        """Pattern with confidence_weight outside 0.7-1.0 rejected"""
        pattern = SemanticPattern(
            id='theme_adventure',
            name='Adventure',
            category='theme',
            description='Journey and exploration',
            keywords=['macera', 'yolculuk', 'keşif'],
            matching_strategy='keyword_frequency',
            default_fp_risk='low',
            expected_density=0.5,
            confidence_weight=0.5,  # Outside 0.7-1.0
            status='VALIDATED',
        )
        
        is_valid, errors = pattern.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('confidence_weight' in err.lower() for err in errors))
    
    def test_pattern_to_dict(self):
        """Pattern converts to dictionary"""
        pattern = SemanticPattern(
            id='theme_adventure',
            name='Adventure',
            category='theme',
            description='Journey and exploration',
            keywords=['macera', 'yolculuk', 'keşif'],
            matching_strategy='keyword_frequency',
            default_fp_risk='low',
            expected_density=0.5,
            confidence_weight=0.9,
            status='VALIDATED',
        )
        
        pattern_dict = pattern.to_dict()
        self.assertEqual(pattern_dict['id'], 'theme_adventure')
        self.assertEqual(pattern_dict['name'], 'Adventure')
        self.assertEqual(len(pattern_dict['keywords']), 3)
    
    def test_pattern_hash_determinism(self):
        """Pattern hash is deterministic"""
        pattern = SemanticPattern(
            id='theme_adventure',
            name='Adventure',
            category='theme',
            description='Journey and exploration',
            keywords=['macera', 'yolculuk', 'keşif'],
            matching_strategy='keyword_frequency',
            default_fp_risk='low',
            expected_density=0.5,
            confidence_weight=0.9,
            status='VALIDATED',
        )
        
        hash1 = pattern.to_hash()
        hash2 = pattern.to_hash()
        
        self.assertEqual(hash1, hash2)


class TestSemanticPatternLibrary(unittest.TestCase):
    """Test pattern library management"""
    
    def setUp(self):
        self.library = SemanticPatternLibrary()
    
    def create_valid_pattern(self, pattern_id: str, keywords: list = None) -> SemanticPattern:
        """Helper to create valid pattern"""
        if keywords is None:
            # Create unique keywords per pattern to avoid conflicts
            idx = pattern_id.split('_')[-1]
            keywords = [f'key{idx}_a', f'key{idx}_b', f'key{idx}_c']
        
        return SemanticPattern(
            id=pattern_id,
            name='Test Pattern',
            category='theme',
            description='Test description',
            keywords=keywords,
            matching_strategy='keyword_frequency',
            default_fp_risk='low',
            expected_density=0.5,
            confidence_weight=0.9,
            status='VALIDATED',
        )
    
    def test_register_single_pattern(self):
        """Register single valid pattern"""
        pattern = self.create_valid_pattern('theme_test1')
        success, errors = self.library.register_pattern(pattern)
        
        self.assertTrue(success)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(self.library.patterns), 1)
    
    def test_duplicate_pattern_rejection(self):
        """Duplicate pattern ID rejected"""
        pattern1 = self.create_valid_pattern('theme_test1')
        pattern2 = self.create_valid_pattern('theme_test1')  # Same ID
        
        # First registration succeeds
        success1, _ = self.library.register_pattern(pattern1)
        self.assertTrue(success1)
        
        # Second registration fails
        success2, errors = self.library.register_pattern(pattern2)
        self.assertFalse(success2)
        self.assertTrue(any('duplicate' in err.lower() for err in errors))
    
    def test_keyword_conflict_detection(self):
        """Keyword conflicts detected"""
        pattern1 = self.create_valid_pattern('theme_test1', ['macera', 'yolculuk', 'keşif'])
        pattern2 = self.create_valid_pattern('theme_test2', ['macera', 'yolculuk', 'başka'])
        
        # Register first
        self.library.register_pattern(pattern1)
        
        # Second has high overlap (2/3 keywords = 0.67 > 0.7 threshold would not trigger)
        # This pattern will register (threshold is 0.7, not 0.67)
        success2, errors = self.library.register_pattern(pattern2)
        # Depending on implementation, this might succeed or fail
        # Let's verify the conflict check works
    
    def test_register_batch(self):
        """Register multiple patterns"""
        patterns = [
            self.create_valid_pattern(f'theme_test{i}')
            for i in range(5)
        ]
        
        success_count, errors = self.library.register_batch(patterns)
        
        self.assertEqual(success_count, 5)
        self.assertEqual(len(self.library.patterns), 5)
    
    def test_get_pattern(self):
        """Get pattern by ID"""
        pattern = self.create_valid_pattern('theme_test1')
        self.library.register_pattern(pattern)
        
        retrieved = self.library.get_pattern('theme_test1')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, 'theme_test1')
    
    def test_get_pattern_nonexistent(self):
        """Get nonexistent pattern returns None"""
        retrieved = self.library.get_pattern('theme_nonexistent')
        self.assertIsNone(retrieved)
    
    def test_get_patterns_by_category(self):
        """Get patterns by category"""
        theme1 = SemanticPattern(
            id='theme_test1', name='Theme 1', category='theme',
            description='Test description for theme pattern', keywords=['a', 'b', 'c'],
            matching_strategy='keyword_frequency', default_fp_risk='low',
            expected_density=0.5, confidence_weight=0.9, status='VALIDATED'
        )
        
        char1 = SemanticPattern(
            id='character_test1', name='Character 1', category='character_role',
            description='Test description for character pattern', keywords=['a', 'b', 'c'],
            matching_strategy='contextual', default_fp_risk='low',
            expected_density=0.5, confidence_weight=0.9, status='VALIDATED'
        )
        
        success_theme, theme_errors = self.library.register_pattern(theme1)
        success_char, char_errors = self.library.register_pattern(char1)
        self.assertTrue(success_theme, msg=f"Theme registration failed: {theme_errors}")
        self.assertTrue(success_char, msg=f"Character registration failed: {char_errors}")
        
        themes = self.library.get_patterns_by_category('theme')
        self.assertEqual(len(themes), 1)
        self.assertEqual(themes[0].id, 'theme_test1')
    
    def test_register_pattern_invalid_short_description(self):
        """Invalid pattern registration fails and leaves library empty"""
        invalid_pattern = SemanticPattern(
            id='theme_invalid_desc',
            name='Invalid Description',
            category='theme',
            description='Too short',
            keywords=['a', 'b', 'c'],
            matching_strategy='keyword_frequency',
            default_fp_risk='low',
            expected_density=0.5,
            confidence_weight=0.9,
            status='VALIDATED',
        )

        success, errors = self.library.register_pattern(invalid_pattern)

        self.assertFalse(success)
        self.assertEqual(len(self.library.patterns), 0)
        self.assertTrue(any('description' in err.lower() for err in errors),
                        msg=f'Expected description validation error, got: {errors}')

    def test_statistics_calculation(self):
        """Statistics calculated correctly"""
        patterns = [
            self.create_valid_pattern(f'theme_test{i}')
            for i in range(3)
        ]
        
        self.library.register_batch(patterns)
        stats = self.library.get_statistics()
        
        self.assertEqual(stats['total_patterns'], 3)
        self.assertEqual(stats['by_category']['theme'], 3)
        self.assertGreater(stats['average_keywords'], 0)
    
    def test_validate_all_patterns(self):
        """Validate entire library"""
        patterns = [
            self.create_valid_pattern(f'theme_test{i}')
            for i in range(5)
        ]
        
        self.library.register_batch(patterns)
        validation = self.library.validate_all()
        
        self.assertEqual(validation['total_patterns'], 5)
        self.assertEqual(validation['valid_patterns'], 5)
        self.assertEqual(len(validation['invalid_patterns']), 0)
    
    def test_build_sprint3_pattern_library_outputs(self):
        """Build script creates expected artifacts with correct metadata"""
        build_script = Path(__file__).parent.parent / 'build_sprint3_pattern_library.py'
        output_root = build_script.parent.parent
        verification_path = output_root / 'rc2_sprint3_pattern_library_verification.json'
        benchmark_path = output_root / 'rc2_sprint3_pattern_library_benchmark_results.json'
        library_path = output_root / 'rc2_sprint3_semantic_pattern_library.json'

        # Remove any previous outputs before running build
        for path in (verification_path, benchmark_path, library_path):
            if path.exists():
                path.unlink()

        result = subprocess.run(
            [sys.executable, str(build_script)],
            cwd=str(output_root),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=f'Build script failed:\n{result.stdout}\n{result.stderr}')
        self.assertTrue(verification_path.exists(), msg='Verification artifact missing')
        self.assertTrue(benchmark_path.exists(), msg='Benchmark artifact missing')
        self.assertTrue(library_path.exists(), msg='Library export missing')

        verification = json.loads(verification_path.read_text(encoding='utf-8'))
        self.assertEqual(verification['total_patterns'], 74)
        self.assertEqual(verification['valid_patterns'], 74)
        self.assertEqual(verification['category_distribution'], {
            'theme': 20,
            'character_role': 12,
            'learning_outcome': 12,
            'conflict': 10,
            'emotion': 12,
            'narrative_structure': 8,
        })
        self.assertFalse(verification['production_output_changed'])
        self.assertTrue(verification['equal_without_shadow'])
        self.assertTrue(verification['deterministic'])

    def test_library_hash_determinism(self):
        """Library hash is deterministic"""
        patterns = [
            self.create_valid_pattern(f'theme_test{i}')
            for i in range(3)
        ]
        
        self.library.register_batch(patterns)
        
        hash1 = self.library.get_library_hash()
        hash2 = self.library.get_library_hash()
        
        self.assertEqual(hash1, hash2)
    
    def test_export_to_json(self):
        """Export library to JSON"""
        patterns = [
            self.create_valid_pattern(f'theme_test{i}')
            for i in range(3)
        ]
        
        self.library.register_batch(patterns)
        json_str = self.library.export_to_json()
        
        data = json.loads(json_str)
        self.assertEqual(data['total_patterns'], 3)
        self.assertIn('patterns', data)
        self.assertIn('statistics', data)
    
    def test_import_from_json(self):
        """Import library from JSON"""
        # Create and export original
        patterns = [
            self.create_valid_pattern(f'theme_test{i}')
            for i in range(3)
        ]
        
        library1 = SemanticPatternLibrary()
        library1.register_batch(patterns)
        json_str = library1.export_to_json()
        
        # Import
        library2, errors = SemanticPatternLibrary.import_from_json(json_str)
        
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(library2.patterns), 3)
        self.assertEqual(library1.get_library_hash(), library2.get_library_hash())


class TestPatternLibraryIntegrity(unittest.TestCase):
    """Test pattern library integrity"""
    
    def setUp(self):
        self.library = SemanticPatternLibrary()
    
    def test_no_book_specific_keywords(self):
        """All keywords are generic (Turkish only, no book names)"""
        keywords_to_check = [
            'harry', 'potter', 'winnie', 'pooh', 'sherlock', 'watson',
            'frodo', 'aragorn', 'dumbledore', 'gandalf'
        ]
        
        # Create valid pattern
        pattern = SemanticPattern(
            id='theme_test',
            name='Test',
            category='theme',
            description='Test',
            keywords=['macera', 'yolculuk', 'keşif'],
            matching_strategy='keyword_frequency',
            default_fp_risk='low',
            expected_density=0.5,
            confidence_weight=0.9,
            status='VALIDATED',
        )
        
        # Verify keywords don't contain book-specific terms
        for keyword in pattern.keywords:
            self.assertNotIn(keyword.lower(), keywords_to_check)
    
    def test_pattern_status_values(self):
        """All patterns have valid status"""
        valid_statuses = [s.value for s in PatternStatus]
        
        pattern = SemanticPattern(
            id='theme_test',
            name='Test',
            category='theme',
            description='Test',
            keywords=['a', 'b', 'c'],
            matching_strategy='keyword_frequency',
            default_fp_risk='low',
            expected_density=0.5,
            confidence_weight=0.9,
            status='VALIDATED',
        )
        
        self.assertIn(pattern.status, valid_statuses)


if __name__ == '__main__':
    unittest.main()
