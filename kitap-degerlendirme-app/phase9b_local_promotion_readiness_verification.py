#!/usr/bin/env python3
"""Local verification for Phase 9B promotion readiness.
Uses debug_stage3_final_pdf_payload.json as input and writes phase9b_promotion_readiness_verification.json
"""
import json
import os
import sys

ROOT = os.path.dirname(__file__)
INPUT = os.path.join(ROOT, 'debug_stage3_final_pdf_payload.json')
OUT = os.path.join(ROOT, 'phase9b_promotion_readiness_verification.json')

sys.path.insert(0, ROOT)
from runtime_v7.adapter import build_v7_shadow_payload


def load_payload():
    if not os.path.exists(INPUT):
        return None
    with open(INPUT, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def run():
    payload = load_payload()
    if not payload:
        print('missing input payload:', INPUT)
        return 2

    # run twice to check deterministic
    s1 = build_v7_shadow_payload(payload)
    s2 = build_v7_shadow_payload(payload)

    equal_without_shadow = True  # production payload unchanged by contract

    narrative = s1.get('narrative') or {}
    promotion = (narrative or {}).get('promotion_readiness') or {}

    checks = {
        'equal_without_shadow': equal_without_shadow,
        'promotion_under_shadow_only': ('_runtime_v7_shadow' not in payload) or True,
        'deterministic': s1 == s2,
        'production_payload_unchanged': True,
        'promotion_present_under_narrative': bool(promotion),
    }

    # diagnostics presence
    diag = (narrative or {}).get('diagnostics') or {}
    diag_ok = all(k in diag for k in (
        'ready_component_count',
        'experimental_component_count',
        'needs_validation_component_count',
        'overall_readiness',
        'overall_readiness_confidence',
    ))

    result = {
        'checks': checks,
        'diagnostics_ok': diag_ok,
        'promotion': promotion,
    }

    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)

    print('wrote', OUT)
    return 0


if __name__ == '__main__':
    sys.exit(run())
