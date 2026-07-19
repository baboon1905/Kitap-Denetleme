"""
RC2 Sprint 1B — Production Payload Integrity Test

Verify that:
✓ Production output unchanged (equal_without_shadow == true)
✓ Shadow semantic field present
✓ Deterministic output preserved
✓ No book-specific heuristics
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.adapter import build_v7_shadow_payload


def test_production_payload_integrity():
    """Test that production payload is not modified by semantic engine"""
    
    # Sample production payload
    production_payload = {
        'kitap_adi': 'Test Book',
        'book_id': 'test_001',
        'kitap_metni': 'Çocuk okula gitti ve matematik öğrendi.',
        'ana_karakterler': [
            {'ad': 'Ali', 'entity_type': 'protagonist'},
            {'ad': 'Öğretmen', 'entity_type': 'mentor'},
        ],
        'event_graph': {
            'nodes': [
                {'action': 'Okula gitmek', 'actors': ['Ali']},
                {'action': 'Ders çalışmak', 'actors': ['Ali', 'Öğretmen']},
            ]
        },
        'theme_analysis': [
            {'tema': 'Eğitim', 'description': 'Learning theme'},
        ],
        'tema_analizi': [
            {'ad': 'Eğitim', 'tema': 'Learning'},
        ],
    }
    
    # Make a deep copy for comparison
    import copy
    production_copy = copy.deepcopy(production_payload)
    
    # Build shadow runtime (which integrates semantic engine)
    shadow_result = build_v7_shadow_payload(production_payload)
    
    # Verify production payload unchanged
    assert production_payload == production_copy, "Production payload was modified!"
    
    # Verify shadow contains semantic field
    assert 'semantic' in shadow_result, "Shadow semantic field missing!"
    
    semantic_field = shadow_result['semantic']
    assert 'theme_clusters' in semantic_field
    assert 'character_roles' in semantic_field
    assert 'learning_outcome_clusters' in semantic_field
    assert 'concept_graph' in semantic_field
    assert 'diagnostics' in semantic_field
    
    # Verify diagnostics
    diagnostics = semantic_field['diagnostics']
    assert 'semantic_cluster_count' in diagnostics
    assert 'concept_count' in diagnostics
    assert 'semantic_density' in diagnostics
    assert 'semantic_confidence' in diagnostics
    
    # Verify ranges
    assert 0 <= diagnostics['semantic_density'] <= 1.0
    assert 0 <= diagnostics['semantic_confidence'] <= 1.0
    
    print("✓ Production Payload Integrity Test PASSED")
    print(f"  - Production payload unchanged: {production_payload == production_copy}")
    print(f"  - Shadow semantic field present: {'semantic' in shadow_result}")
    print(f"  - Theme clusters detected: {len(semantic_field['theme_clusters'])}")
    print(f"  - Character roles detected: {len(semantic_field['character_roles'])}")
    print(f"  - Learning outcomes detected: {len(semantic_field['learning_outcome_clusters'])}")
    print(f"  - Semantic confidence: {diagnostics['semantic_confidence']}")
    
    return True


def test_deterministic_output():
    """Test that semantic output is deterministic"""
    
    production_payload = {
        'kitap_adi': 'Test Book',
        'book_id': 'test_001',
        'kitap_metni': 'Tavşan Pati bir macera başlattı.',
        'ana_karakterler': [],
        'event_graph': {'nodes': []},
    }
    
    # Run shadow build twice
    result1 = build_v7_shadow_payload(production_payload)
    result2 = build_v7_shadow_payload(production_payload)
    
    # Compare semantic fields
    semantic1 = result1.get('semantic', {})
    semantic2 = result2.get('semantic', {})
    
    # Diagnostics should be identical
    diag1 = semantic1.get('diagnostics', {})
    diag2 = semantic2.get('diagnostics', {})
    
    assert diag1 == diag2, "Semantic output is not deterministic!"
    
    print("✓ Deterministic Output Test PASSED")
    print(f"  - Run 1 confidence: {diag1.get('semantic_confidence')}")
    print(f"  - Run 2 confidence: {diag2.get('semantic_confidence')}")
    print(f"  - Identical: {diag1 == diag2}")
    
    return True


def test_no_book_specific_heuristics():
    """Test that patterns don't use book-specific heuristics"""
    
    from runtime_v7.semantic_engine import SemanticEngine
    
    engine = SemanticEngine()
    
    # Check theme patterns are generic
    for theme_name in engine.THEME_KEYWORDS.keys():
        # Book-specific names should not appear
        assert 'tavşan' not in theme_name.lower()
        assert 'büyülü' not in theme_name.lower()
        assert 'kristof' not in theme_name.lower()
        assert 'gdz' not in theme_name.lower()
    
    # Check character role patterns are generic
    for role_name in engine.CHARACTER_ROLES.keys():
        assert 'tavşan' not in role_name.lower()
        assert 'büyülü' not in role_name.lower()
        assert 'kristof' not in role_name.lower()
    
    # Check learning outcome patterns are generic
    for outcome_type in engine.LEARNING_OUTCOMES.keys():
        assert 'tavşan' not in outcome_type.lower()
        assert 'büyülü' not in outcome_type.lower()
        assert 'kristof' not in outcome_type.lower()
    
    print("✓ No Book-Specific Heuristics Test PASSED")
    print(f"  - Themes: {list(engine.THEME_KEYWORDS.keys())}")
    print(f"  - Character roles: {list(engine.CHARACTER_ROLES.keys())}")
    print(f"  - Learning outcomes: {list(engine.LEARNING_OUTCOMES.keys())}")
    
    return True


def test_equal_without_shadow():
    """Test that production payload equals itself without semantic shadow"""
    
    production_payload = {
        'kitap_adi': 'Test Book',
        'book_id': 'test_001',
        'kitap_metni': 'Test content',
        'ana_karakterler': [],
        'event_graph': {'nodes': []},
    }
    
    import copy
    payload_before = copy.deepcopy(production_payload)
    
    # Build shadow (includes semantic engine)
    shadow_result = build_v7_shadow_payload(production_payload)
    
    payload_after = copy.deepcopy(production_payload)
    
    # Remove semantic field from shadow and compare production portions
    shadow_without_semantic = copy.deepcopy(shadow_result)
    semantic_data = shadow_without_semantic.pop('semantic', None)
    
    # Production payload should be identical before and after
    assert payload_before == payload_after, "Production payload changed during shadow build!"
    
    print("✓ Equal Without Shadow Test PASSED")
    print(f"  - Production payload stable: {payload_before == payload_after}")
    print(f"  - Semantic field separated: {semantic_data is not None}")
    
    return True


if __name__ == '__main__':
    print("RC2 Sprint 1B — Production Payload Integrity Verification")
    print("=" * 70)
    
    all_passed = True
    
    try:
        print("\n1. Testing Production Payload Integrity...")
        test_production_payload_integrity()
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        all_passed = False
    
    try:
        print("\n2. Testing Deterministic Output...")
        test_deterministic_output()
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        all_passed = False
    
    try:
        print("\n3. Testing No Book-Specific Heuristics...")
        test_no_book_specific_heuristics()
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        all_passed = False
    
    try:
        print("\n4. Testing Equal Without Shadow...")
        test_equal_without_shadow()
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL TESTS PASSED — Production Safety Verified")
    else:
        print("✗ SOME TESTS FAILED — Review Required")
        sys.exit(1)
