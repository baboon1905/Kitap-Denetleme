# PHASE 3 Regression Baseline

Date: 2026-07-03
Flag: `V7_SUMMARY_IR_SOURCE=true`

Tested books (only these two):

- Büyülü Yastıklar
- Benim Adım Kristof Kolomb

Summary (concise):

- Büyülü Yastıklar
  - analiz: 200
  - /api/tema-kazanim/rapor?format=pdf: 200 (application/pdf)
  - /api/tema-kazanim/rapor?format=word: 200 (application/msword)
  - /api/theme-report/teacher-pdf: 200 (application/pdf)
  - forbidden_summary_surfaces: []
  - canonical_summary_ir_hash: c9d18fc618f25374b86d9f325a88b3b98b0fc7e24c29151ab15dae42bb1e49f3
  - summary_ui/pdf/teacher hashes: identical
  - surface_consistency: true
  - error body / traceback: none

- Benim Adım Kristof Kolomb
  - analiz: 200
  - /api/tema-kazanim/rapor?format=pdf: 200 (application/pdf)
  - /api/tema-kazanim/rapor?format=word: 200 (application/msword)
  - /api/theme-report/teacher-pdf: 200 (application/pdf)
  - forbidden_summary_surfaces: []
  - canonical_summary_ir_hash: d00e99c5a5e01ef3bba9a80765b399335abf717a8403292d7908ed4f1f3d26f3
  - summary_ui/pdf/teacher hashes: identical
  - surface_consistency: true
  - error body / traceback: none

Notes:
- Gökyüzünü Kaybeden Şehir was explicitly NOT run in this baseline.
- Full JSON output saved at `rerun_phase3b_two_books.json` in workspace root.
