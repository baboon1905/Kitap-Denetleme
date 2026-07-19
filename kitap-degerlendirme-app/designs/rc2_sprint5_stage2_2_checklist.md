RC2 Sprint 5 — Stage 2.2 Integration Checklist

Bu belge sadece Stage 2.2 entegrasyonunun operasyonel kontrol listesidir. Implementasyon veya kod örneği içermez.

Prerequisites
- Confirmed Stage 2.1 closure document present and accepted.
- `pattern_activations` schema agreed (required/optional fields) and versioned.
- Confidence Engine contract (field names, types, calibration semantics) signed off.
- Monitoring artifacts storage location and retention policy defined.
- Access and permissions for staging/canary environments verified.

Runtime touch points
- Match producers: where `matches` are emitted (service/process names, topics, files).
- Confidence Engine: service endpoint or library location that emits `raw_confidence` and `calibrated_confidence`.
- Semantic Monitor: invocation point in pipeline (module, service, or job) and artifact write path.
- Adapter: location where `payload['pattern_activations']` may be read and normalized into `_runtime_v7_shadow`.
- Observability: logs, metrics, and artifact collectors that will receive `pattern_monitoring` outputs.

Integration order
1. Validate schemas and contracts (Pattern Library, Confidence Engine, Monitor input/output).
2. Deploy Semantic Monitor to staging (non-invasive mode: produce artifacts only).
3. Verify Monitor artifact writes (monitoring, quality_gates, benchmark files) for test inputs.
4. Confirm Adapter normalize/transport behavior for upstream `pattern_activations` (no payload injection yet).
5. Perform staging end-to-end dry-run (monitor artifacts only) and validate outputs.
6. Canary wiring (small volume) to populate `payload['pattern_activations']` from Monitor outputs for selected runs.
7. Observe metrics, quality gates, and verification artifacts; proceed to broader rollout if green.

Validation order
1. Schema validation: ensure every `match` includes required identifiers and confidence fields (or monitor logs missing-field errors).
2. Artifact presence: `pattern_monitoring`, `quality_gates`, and canonical `pattern_activations` files exist per run.
3. Content sanity: counts (pattern_count, activated_count) consistent with expectations for canary set.
4. Determinism check: run same input twice; canonicals identical (hash/CRC or exact equality ignoring timestamps).
5. Production-output isolation: verify `verification.production_output_changed` remains `False` and `equal_without_shadow` is `True`.
6. Quality gates: ensure `review/watch` lists are reasonable and finite; no unbounded growth.

Rollback strategy
- Criteria to trigger rollback: acceptance criteria failures, spike in `review` flags, production output changes, or storage/latency regressions.
- Rollback action: disable Monitor-to-payload wiring (stop populating `payload['pattern_activations']`) and continue Adapter existing behavior.
- Fast path: revert canary routing or feature flag to previous behavior.
- Post-rollback: collect diffs/artifacts for RCA and patch before reattempt.

Smoke test plan
- Scope: small, content-rich sample set (3–10 items) that previously demonstrated activations.
- Steps: run monitor in staging, validate canonical artifacts exist, confirm one known-positive pattern appears active.
- Metrics to observe: artifact write success, activated_count > 0 (if expected), no failures/exceptions logged.

Benchmark plan
- Scope: representative sample (N items matching production profile) run in staging/canary.
- Metrics: end-to-end latency impact, artifact size, storage write throughput, CPU/memory of Monitor and Adapter, determinism checks.
- Acceptance thresholds: latency increase < 5% (configurable), artifact sizes within storage limits, no excessive retry/error rates.

Acceptance criteria
- Monitor produces canonical `pattern_activations` and `pattern_monitoring` artifacts consistently for test and canary runs.
- `equal_without_shadow` remains `True` and `production_output_changed` remains `False` for canary runs.
- Determinism: two identical inputs produce identical canonical outputs (ignoring timestamp fields).
- No significant latency or resource regression in canary scope.
- Quality gates do not show mass failures (e.g., > 10% of patterns flagged `review` unexpectedly).

Failure criteria
- Missing or malformed artifacts from Monitor.
- `production_output_changed` becomes `True` or `equal_without_shadow` becomes `False`.
- Determinism breach: identical inputs yield non-equal canonicals beyond timestamp differences.
- Canary metrics exceed thresholds (latency, error rate, storage growth).

Production safety checklist
- Feature flags or routing controls in place to enable/disable Monitor-to-payload wiring.
- Canary size limited and configurable.
- Monitoring/alerting configured for: artifact write failures, monitoring errors, spike in `review` flags, latency regressions.
- Rollback playbook accessible and rehearsed by the team.
- Schema validation tool runs before wiring; missing-field reports are surfaced to the team.

Notes
- This document is the operational gate for Stage 2.2. No runtime wiring or runner modifications should occur until this checklist items are green and owners sign off.
