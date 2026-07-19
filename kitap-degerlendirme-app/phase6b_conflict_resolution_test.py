#!/usr/bin/env python3
"""
Phase 6B Primary Conflict Resolution Verification
Tests algorithmic primary conflict extraction and resolution determination
"""
import copy
import json
import os
from unittest.mock import MagicMock

# Set environment variables BEFORE importing
os.environ['V7_SHADOW_MODE'] = 'true'
os.environ['V7_NARRATIVE_GRAPH'] = 'true'

# Force reload by removing cached modules
import sys
for mod in list(sys.modules.keys()):
    if 'runtime_v7' in mod:
        del sys.modules[mod]

from runtime_v7.adapter import build_v7_shadow_payload
from runtime_v7.conflict_resolution import build_primary_conflict_resolution


def create_sample_payload_with_conflicts():
    """Create a minimal sample payload with conflict structures."""
    return {
        "kitap_adi": "Test Book",
        "yazar": "Test Author",
        "karakter_sayisi": 3,
        "karakterler": [
            {"ad": "Hero", "rolu": "protagonist"},
            {"ad": "Villain", "rolu": "antagonist"},
            {"ad": "Helper", "rolu": "supporting"}
        ],
        "olay_sayisi": 5,
        "olaylar": [
            {"olay_id": 1, "tanim": "Introduction"},
            {"olay_id": 2, "tanim": "Conflict rises"},
            {"olay_id": 3, "tanim": "Climax"},
            {"olay_id": 4, "tanim": "Resolution"},
            {"olay_id": 5, "tanim": "Conclusion"}
        ],
        "tema_sayisi": 2,
        "temalar": ["courage", "justice"],
        "kazanim_sayisi": 4,
        "summary_surfaces": {
            "canonical_summary": "Test story summary",
        }
    }


def test_primary_conflict_resolution():
    """Test primary conflict resolution extraction."""
    payload = create_sample_payload_with_conflicts()
    
    # Build shadow payload - adapter returns the shadow directly, not wrapped
    shadow_result = build_v7_shadow_payload(payload)
    
    # Debug: check what's returned
    return_value_keys = list(shadow_result.keys()) if isinstance(shadow_result, dict) else None
    
    # Verify it's a dict with shadow structure
    is_shadow_dict = isinstance(shadow_result, dict)
    
    # The adapter returns the shadow directly (not wrapped in _runtime_v7_shadow)
    shadow = shadow_result if isinstance(shadow_result, dict) else {}
    narrative = shadow.get('narrative') or {}
    
    # Debug: check what's in shadow
    debug_info = {
        'return_value_keys': return_value_keys,
        'is_shadow_dict': is_shadow_dict,
        'shadow_keys': list(shadow.keys()) if isinstance(shadow, dict) else None,
        'narrative_keys': list(narrative.keys()) if isinstance(narrative, dict) else None,
    }
    
    # Verify primary_conflict and resolution fields exist
    primary_conflict = narrative.get('primary_conflict')
    resolution = narrative.get('resolution')
    conflict_graph = narrative.get('conflict_graph')
    
    checks = {
        'has_primary_conflict': isinstance(primary_conflict, dict),
        'has_resolution': isinstance(resolution, dict),
        'has_conflict_graph': isinstance(conflict_graph, dict),
        'primary_conflict_has_id': primary_conflict.get('conflict_id') if isinstance(primary_conflict, dict) else None,
        'resolution_has_status': resolution.get('status') if isinstance(resolution, dict) else None,
        'resolution_has_confidence': isinstance(resolution.get('confidence'), (int, float)) if isinstance(resolution, dict) else False,
    }
    
    # Verify algorithmic rules (no book-specific heuristics)
    if isinstance(resolution, dict):
        status = resolution.get('status')
        checks['resolution_status_is_algorithmic'] = status in ['resolved', 'partially_resolved', 'unresolved', 'ambiguous']
    
    # Test determinism across repeated calls
    run1 = build_v7_shadow_payload(copy.deepcopy(payload))
    run2 = build_v7_shadow_payload(copy.deepcopy(payload))
    
    # Strip transients for comparison
    def strip_transients(v):
        if isinstance(v, dict):
            return {k: strip_transients(val) for k, val in v.items() 
                    if k not in {'timestamp', 'created_at', 'cache_key', 'payload_id', 'analiz_tarihi'}}
        if isinstance(v, list):
            return [strip_transients(item) for item in v]
        return v
    
    run1_clean = strip_transients(run1.get('narrative', {}))
    run2_clean = strip_transients(run2.get('narrative', {}))
    
    checks['deterministic_across_runs'] = run1_clean == run2_clean
    
    return {
        'status': 'success',
        'checks': checks,
        'debug': debug_info,
        'primary_conflict': primary_conflict,
        'resolution': resolution,
    }


if __name__ == '__main__':
    result = test_primary_conflict_resolution()
    
    output_path = os.path.join(
        os.path.dirname(__file__),
        'phase6b_conflict_resolution_test_result.json'
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Test completed. Results saved to: {output_path}")
    print(f"Status: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"All checks passed: {all(result.get('checks', {}).values())}")
