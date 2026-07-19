# RC4 Sprint 10A Summary

## Scope
- Added a regression-only runner for event graph compression using the Sprint 9B reconstruction artifact.
- Added acceptance tests for artifact generation and aggregate metrics.
- Kept the implementation shadow-only and deterministic.

## Files Added
- [run_rc4_sprint10a_event_graph_regression.py](run_rc4_sprint10a_event_graph_regression.py)
- [rc4_sprint10a_event_graph_results.json](rc4_sprint10a_event_graph_results.json)
- [tests/test_run_rc4_sprint10a_event_graph_regression.py](tests/test_run_rc4_sprint10a_event_graph_regression.py)

## Verification
- Command: `python -m pytest -q tests/test_event_graph_builder.py tests/test_run_rc4_sprint10a_event_graph_regression.py`
- Result: 4 passed in 0.47s

## Artifact Summary
- Total books: 3
- Total input events: 10
- Total event groups: 6
- Average compression ratio: 0.267
- Deterministic: true
- Production output changed any: false
- Runtime pipeline bound any: false
