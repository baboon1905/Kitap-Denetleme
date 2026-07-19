# Benchmark durumu

Eski `lib.summary_ir`, `lib.surface_realizer` ve `lib.quality_gate` prototiplerine
bağlı benchmark runner kaldırılmıştır. Bu modüller production kodunda veya Git
geçmişinde bulunmamaktadır.

Güncel summary, quality gate ve narrative davranışları test paketiyle doğrulanır:

```powershell
python -m pytest tests
```

Projection ve consistency regresyonlarını ayrıca çalıştırmak için:

```powershell
python -m unittest `
  tests.test_report_projection_helper `
  tests.test_canonical_entity_fragment_mismatches `
  tests.test_consistency_evidence_surface
```
