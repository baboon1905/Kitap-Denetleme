import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from runtime_v7.adapter import build_v7_shadow_payload


def test_runtime_v7_shadow_audit_adapter_integration():
    payload = {"kitap_adi": "Test Book", "ana_karakterler": []}
    production_payload = dict(payload)

    shadow_payload = {"_runtime_v7_shadow": build_v7_shadow_payload(payload)}

    assert "shadow_audit" not in production_payload
    assert "_runtime_v7_shadow" in shadow_payload
    assert isinstance(shadow_payload["_runtime_v7_shadow"], dict)
    assert "narrative" in shadow_payload["_runtime_v7_shadow"]
    assert isinstance(shadow_payload["_runtime_v7_shadow"]["narrative"], dict)
    assert "shadow_audit" in shadow_payload["_runtime_v7_shadow"]["narrative"]
    assert "shadow_audit" not in shadow_payload
    assert "shadow_audit" not in shadow_payload["_runtime_v7_shadow"]

    shadow_audit = shadow_payload["_runtime_v7_shadow"]["narrative"]["shadow_audit"]
    assert isinstance(shadow_audit, dict)
    assert "summary" in shadow_audit
    assert "findings" in shadow_audit
    assert isinstance(shadow_audit["findings"], list)

    first = {"_runtime_v7_shadow": build_v7_shadow_payload(payload)}
    second = {"_runtime_v7_shadow": build_v7_shadow_payload(payload)}
    assert first == second
