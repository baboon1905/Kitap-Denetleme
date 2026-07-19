RC2 Sprint 5 — Stage 2 Integration Design

Amaç
- `pattern_activations` canonical listesini upstream Semantic Monitor tarafından runtime sırasında üretmek ve adapter aracılığıyla `shadow` payload'a güvenli, deterministik biçimde taşımak.
- Kurallar: adapter hiçbir yeni inference/hesaplama/pattern üretmeyecek; sadece taşıyıcı (canonical carrier) olacak. Runner sadece canonical listeyi okuyacak.

Kapsam
- Bu tasarım yalnızca mimari ve veri sözleşmesini tanımlar. İmplementasyon, test, smoke veya commit bu aşamada yapılmayacaktır.

Özet Akış
1. Semantic Pattern Library + Confidence Engine + Semantic Monitor (upstream) çalışır ve her kitap için canonical `pattern_activations` ile `pattern_monitoring` özetini üretir.
2. Runtime pipeline (ör. PDF extraction → semantic engine → monitor) monitörün ürettiği canonical listeyi üretim payload'una (ör. iş hattındaki bir mesaj, db alanı veya API response meta) ekler: örn. `payload['pattern_activations']` ve `payload['pattern_monitoring']`.
3. Adapter (`build_v7_shadow_payload`) bu payload alanlarını okuyup normalize eder (Stage 1 kuralları), shadow içine koyar: `_runtime_v7_shadow['semantic']['pattern_activations']` ve `_runtime_v7_shadow['semantic']['monitoring']`.
4. Runner yalnızca shadow içindeki `pattern_activations` listesini okur; substring arama ve ikinci inference tamamen kaldırılır.

Veri Sözleşmesi (API / Message)
- Upstream Monitor Üretimi (canonical form — örnek JSON öğe):
  {
    "pattern_id": "S3_P001",
    "category": "engagement",
    "status": "active",                // active | candidate | rejected
    "raw_confidence": 0.75,             // float 0..1
    "calibrated_confidence": 0.70,      // float 0..1
    "evidence_count": 2,                // int
    "source": "summary_ir",           // human-readable source token
    "algorithm_version": "v1.0",      // pattern library / monitor version (short)
    // optional:
    "match_snippet": "...",
    "matched_spans": [{"page":1,"start":10,"end":30}]
  }

- Monitoring özet (payload alanı `pattern_monitoring`):
  {
    "last_run_iso": "2026-07-06T12:00:00Z",
    "status": "ok",                    // ok | partial | error
    "errors": [],                        // kısa string list
    "pattern_library_version": "rc2-2026-07",
    "confidence_engine_version": "conf-v1"
  }

Adapter Davranışı (Stage 2 — gereksinimler)
- Adapter kesinlikle inference yapmaz. Yalnızca aşağıyı uygular:
  - Okur: `payload['pattern_activations']` veya alternatif anahtarlar (`_pattern_activations`).
  - Normalize eder: zorunlu alanları garanti eder, floatları round(2), boşsa [] atar.
  - Deterministik sıralama uygular: sort by `pattern_id`, then `source`.
  - Monitoring özetini sadece taşıyıcı olarak kopyalar/normalize eder (`last_run_iso`,`status`,`errors`,`pattern_library_version`,`confidence_engine_version`).
  - Hata durumunda shadow içinde güvenli defaultlar bırakır (boş liste ve monitoring.status="error").

Runner Davranışı
- Runner kodu substring arama veya kendi pattern inference'ını yapmayacak.
- Runner reads `_runtime_v7_shadow['semantic']['pattern_activations']` and consumes `pattern_id` + `calibrated_confidence` (or `raw_confidence` where needed).
- If field missing or empty → treat as zero activations.
- Runner must not change production output; only read shadow.

Determinism ve Testler
- Determinism kuralları (zorunlu):
  - Confidence değerleri 2 ondalık ile normalize edilecek.
  - Liste sıralaması sabit: (`pattern_id`, `source`).
  - Timestamps not used for deterministic equality — `equal_without_shadow` logic should strip or ignore `monitoring.last_run_iso`.
- Test plan (high-level; uygulanacaksa):
  - Unit test: provide payload with different field names (`id` vs `pattern_id`) and verify adapter normalizes.
  - Determinism test: run monitor output through adapter twice and ensure shadow identical.
  - Backwards compatibility: adapter should accept payloads without pattern fields and produce empty list.

Failure Modes ve Fallbacks
- Monitor failed / not present: adapter sets `pattern_activations` to [] and `monitoring.status` to `not_run` or `error`.
- Monitor produced partially (some malformed items): adapter normalizes valid items, drops invalid entries, sets `monitoring.status` to `partial` and adds short `errors` list.
- Upstream and adapter version mismatch: adapter should still accept fields; `monitoring.pattern_library_version` and `confidence_engine_version` enable tracing.

Security & Privacy
- `match_snippet` may contain PII: default policy is to treat it as optional and mask when necessary before persisting; recommend config flag to enable/disable snippet inclusion.
- Access control: shadow payloads should be restricted same as other diagnostic outputs.

Migration & Rollout Strategy
- Phase A (canary): enable monitor->payload population for a single book stream; adapter will copy list; runner still reads but in dry-run mode logs counts (no behavioral change).
- Phase B: enable runner to rely on canonical activations for downstream checks; disable substring fallback once stable.
- Rollback: if activations cause issues, stop monitor injection upstream; adapter will produce empty list and runner reverts to zero activations.

Observability
- Emit metrics: `monitoring.status` per run, `pattern_activations.count`, `pattern_activations.missing_count`, `normalization.errors`.
- Sample logs: on normalization error, log book_id + short error (no PII).

Versioning & Compatibility
- `pattern_library_version` and `confidence_engine_version` must be present in `pattern_monitoring`.
- Adapter records `algorithm_version` per activation as provided; long-term plan: separate `pattern_library_version` and `confidence_engine_version` in activation entries if needed.

Acceptance Criteria (Stage 2, design-level)
- Upstream monitor produces canonical list per contract.
- Adapter copies/normalizes canonical list to `_runtime_v7_shadow['semantic']['pattern_activations']` without inference.
- Runner reads only canonical list; substring search removed.
- Production outputs unchanged; `equal_without_shadow` preserved.
- Determinism rules applied and unit tests exist to validate normalization and determinism.

Sonraki adımlar (onay sonrası implementasyon akışı)
1. Implementasyon: upstream monitor emits canonical list (work in monitor repo).
2. Adapter: ensure normalized copy (we have Stage 1 code adjusted to normalize).
3. Runner: remove substring search and read canonical list.
4. Tests: unit + deterministic smoke runs.
5. Rollout: canary → full rollout.

Dosya: `designs/rc2_sprint5_stage2_integration_design.md`

Not: Şu anda hiçbir commit yapılmayacak; bu dosya tasarım içindir. Implementasyon için onayınızı bekliyorum.