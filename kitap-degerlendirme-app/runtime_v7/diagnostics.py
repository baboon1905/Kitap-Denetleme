from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from .typing import StatusLiteral


def create_quality_contract_diagnostics() -> Dict[str, Any]:
    return {
        "status": "PASS",
        "issues": [],
        "risk_categories": [],
        "diagnostics": {
            "source": "runtime_v7_adapter_phase2",
        },
        "checked_at": "",
        "schema_version": "v1",
    }


def create_adapter_error_diagnostics(message: str) -> Dict[str, Any]:
    return {
        "status": "WARNING",
        "issues": [
            {
                "code": "runtime_v7_adapter_error",
                "message": message,
            }
        ],
        "risk_categories": ["adapter_error"],
        "diagnostics": {
            "error_message": message,
            "source": "runtime_v7_adapter_phase2",
            "built_at": datetime.now().isoformat(timespec="seconds"),
        },
        "checked_at": datetime.now().isoformat(timespec="seconds"),
        "schema_version": "v1",
    }
