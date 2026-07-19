# Artifact Rename Proposal (RC11)

This proposal is derived from `artifact_inventory_audit.json` and `artifact_inventory_audit.md`.
It lists recommended renames and consolidation actions to bring artifacts into compliance with the new Artifact Guidelines (verification vs benchmark separation).

Notes:
- This document contains *proposals only* — no files are modified or deleted by this change.
- Each entry: Current file, Current classification, Issue, Proposed new name / action, Risk level, RC2 action recommendation.

---

## A. Files to Keep As-Is (no immediate change)
- `rc11_fix1_title_narrator_verification.json` — verification — Compliant. Risk: Low.
- `rc11_fix2_theme_consistency_verification.json` — verification — Compliant. Risk: Low.
- `rc11_fix3_generic_classification_verification.json` — verification — Compliant (references benchmark file). Risk: Low.
- `rc11_fix3_classification_benchmark_results.json` — benchmark — Compliant. Risk: Low.

Recommendation: Leave these files unchanged; they follow the separation standard.

---

## B. Verification files that contain benchmark-like content (recommend split)
For these files the `verification` name is correct, but they contain full `books`/per-book results (benchmark data). Recommend: keep a slim verification file and create a companion benchmark file containing the `books` array and per-book outputs.

1) `phase10a_shadow_impact_verification.json`
- Current class: verification (contains `books`)
- Issue: Contains full per-book benchmark outputs under `books`.
- Proposed new benchmark file: `phase10a_shadow_impact_benchmark_results.json` (move `books` contents here).
- Keep verification file as `phase10a_shadow_impact_verification.json` but remove large `books` payload (keep summary: `all_ok`, checks, aggregated diagnostics).
- Risk: Medium — scripts may currently read `books` from the verification file. Consumers must be updated to read companion benchmark file.
- RC2 action: Split contents and add compatibility shim (read from verification, fall back to new benchmark file) for one release window.

2) `phase10b_promotion_candidates_verification.json`
- Same pattern. Proposed benchmark: `phase10b_promotion_candidates_benchmark_results.json`.
- Risk: Medium. RC2: split + backward-compat shim.

3) `phase10c_rollout_plan_verification.json`
- Proposed benchmark: `phase10c_rollout_plan_benchmark_results.json`.
- Risk: Medium.

4) `phase11a_shadow_audit_verification.json`
- Proposed benchmark: `phase11a_shadow_audit_benchmark_results.json`.
- Risk: Medium.

5) `phase12a_runtime_performance_baseline.json`
- Current class: unknown (contains `books`); this is effectively a benchmark/performance artifact.
- Proposed new name: `phase12a_runtime_performance_benchmark_results.json`.
- Risk: Low-Medium (renaming may break scripts expecting the old name). RC2: rename and add shim.

6) `phase4a_narrative_graph_verification.json`, `phase4b_narrative_quality_diagnostics.json`, `phase4c_narrative_stability_calibration.json`, `phase5a_narrative_chain_verification.json`, `phase5b_cause_effect_verification.json`, `phase6c_story_arc_classification_verification.json`, `phase7a_theme_validation_verification.json`, `phase7b_character_validation_verification.json`, `phase7c_learning_outcome_validation_verification.json`, `phase8a_validation_coverage_verification.json`, `phase8b_validation_confidence_verification.json`, `phase8c_quality_comparison_verification.json`, `phase9a_recommendation_engine_verification.json`, `phase9b_promotion_readiness_verification.json` —
- Current class: verification (contain `books` array or per-book outputs)
- Issue: Each contains benchmark-like `books` data.
- Proposed companion benchmark files: `phase4a_narrative_graph_benchmark_results.json` etc. (pattern: `phaseXX_<feature>_benchmark_results.json`).
- Risk: Medium. RC2 action: split + compatibility shim and update documentation.

Summary: Any verification file that has a top-level `books` or `timestamp` + `books` should have those per-book sections moved to a phase-level benchmark results file.

---

## C. Per-book files with nonstandard naming (recommend consolidation)
Several artifacts are created per-book using the book title in the filename, e.g.:
- `phase7a_theme_validation_verification_Tavşan_Pati.json`
- `phase7a_theme_validation_verification_Büyülü_Yastıklar.json`
- `phase7a_theme_validation_verification_Benim_Adım_Kristof_Kolomb.json`
- Similar pattern for `phase7b`, `phase7c`, `phase8a`, `phase9a`, `phase9b`, etc.

Problems:
- These per-book files duplicate the per-book results and are nonstandard (filename contains uppercase letters, diacritics, and spaces).
- Standard requires a single `phaseXX_feature_benchmark_results.json` containing per-book results under a `books` map.

Proposal:
- Consolidate per-book files into the phase benchmark file, e.g. move their content under the `books` key in `phase7a_theme_validation_benchmark_results.json`.
- Keep a single verification file `phase7a_theme_validation_verification.json` for the feature-level verification checks and aggregated pass/fail.

Example entry (proposed):
- Current: `phase7a_theme_validation_verification_Tavşan_Pati.json` (verification, nonstandard name)
- Proposed: migrate content into `phase7a_theme_validation_benchmark_results.json` under `books["Tavşan Pati"]`.
- Remove per-book filename from repo in RC2 after stakeholders confirm consumers are updated (or keep as backup folder `archive/`).
- Risk: High — consumers and tooling may depend on per-book file paths. Plan a staged migration (RC2) with shims.

RC2 action: Consolidate per-book files into the benchmark file and remove per-book filenames; update any tooling and CI.

---

## D. Benchmark files that appear verification-like (rare)
- `phase6b_conflict_resolution_test_result.json` — classification unknown, contains `checks`, `status`, `resolution` keys (verification-like). Proposed action: if this is a test-level verification outcome, rename to `phase6b_conflict_resolution_verification.json` and ensure the true benchmark outputs (if any) are separated to a `phase6b_conflict_resolution_benchmark_results.json`.
- Risk: Low-Medium.

---

## E. Naming normalization suggestions
- Use only lowercase ASCII for filenames with underscores, e.g. `phase7a_theme_validation_verification.json` and `phase7a_theme_validation_benchmark_results.json`.
- Avoid embedding book titles in filenames; instead use a `books` map inside benchmark results.
- If localized book titles are required for readability, store them only inside the JSON payloads, not filenames.

Risk level: Medium (renames affect automation).

---

## F. Migration plan (recommended timeline)
- RC1 (now): Introduce the Artifact Guidelines doc and CI governance test (done).
- RC2 (next release):
  - Create companion benchmark files for all verification files that currently embed `books` data.
  - Add compatibility shims in code/CI that detect old file locations and read from new benchmark files if present.
  - Deprecate per-book filenames (mark as deprecated for one release cycle).
- RC3:
  - Remove deprecated per-book files and shims once consumer tooling and external scripts have migrated.

---

## G. Example mapping table (representative)
- `phase10a_shadow_impact_verification.json` (verification with `books`) -> split into:
  - `phase10a_shadow_impact_verification.json` (keep summary only)
  - `phase10a_shadow_impact_benchmark_results.json` (move `books`)
  - Risk: Medium — update consumers.

- `phase7a_theme_validation_verification_Tavşan_Pati.json` (per-book) -> migrate into `phase7a_theme_validation_benchmark_results.json` under `books["Tavşan Pati"]` and remove per-book file in RC2.
  - Risk: High — per-file consumers must be updated.

- `phase12a_runtime_performance_baseline.json` -> rename to `phase12a_runtime_performance_benchmark_results.json` (benchmark).
  - Risk: Low-Medium.

---

## H. Recommendations to reduce migration risk
1. Implement read shim logic in the verification scripts: if `phaseXX_feature_verification.json` contains a `books` key, also write `phaseXX_feature_benchmark_results.json` automatically (for RC2), log deprecation warnings.
2. Add a CI job (small script) that validates presence of both artifacts after migration and fails if neither is present.
3. Notify stakeholders and update any internal documentation referencing specific file paths.
4. Provide a one-time migration script that consolidates per-book files into benchmark files and leaves a mapping manifest.

---

Prepared by: automated audit assistant
Date: 2026-07-06

## RC2 Backlog Recommendation

- Per-book JSON artefact dosyaları RC2’de konsolide edilebilir.
- Rename işlemleri için önce bir mapping manifest hazırlanmalı (eski dosya adı -> yeni dosya adı).
- Geriye dönük uyumluluk için eski dosya adlarından yeni dosya adlarına shim/mapping sağlanmalı ve en az bir sürüm boyunca korunmalı.
- CI naming enforcement (tests/test_artifact_governance.py gibi) RC2’de aktif hale getirilmeli.
- RC1.1’de hiçbir dosya taşınmayacak, yeniden adlandırılmayacak veya silinmeyecek; tüm değişiklikler RC2 backlog olarak planlanmalı.


