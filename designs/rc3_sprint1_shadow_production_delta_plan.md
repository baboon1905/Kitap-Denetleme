# RC3 Sprint 1 — Shadow vs Production Delta Analysis

Amaç: Shadow semantic output ile mevcut production output arasında kalite ve kapsama farkını ölçmek.

## Scope
- Shadow zincirinden üretilen semantic çıktılar ile production çıktılarının doğrudan karşılaştırılması.
- Karşılaştırma yalnızca veriye dayalı kalite ve kapsama metrikleri ile sınırlıdır (ör. coverage, precision/recall-benzeri ölçümler, overlap).
- Karşılaştırma, `summary_ir`, `narrative`, `semantic` kaynaklarından üretilen pattern/activation ve monitor sonuçlarına odaklanır.
- Shadow çalışması "shadow-only"; production çıktısı hiçbir koşulda değişmez.

## Non-goals
- Production üzerinde hiçbir deployment veya canlı değişiklik yapma.
- Yeni endpoint/route ekleme.
- Kitap-adına özgü heuristic'ler geliştirme veya uygulama.
- Confidence motorunun devredilmesi/yeniden uygulanması; confidenceler yalnızca `SemanticConfidenceEngine` tarafından sağlanacaktır.
- Uzun vadeli otomatik deployment, A/B testi veya trafik yönlendirmesi.

## Inputs
- Production payloads: mevcut üretim çıktıları (özetler, etiketler, mevcut semantic alanlar).
- Shadow outputs: `pattern_matches`, `pattern_activations`, `pattern_monitoring` ve confidence zenginleştirilmiş çıktılar (runtime_v7 zinciri tarafından üretilen gölge çıktılar).
- Sabit test fixtures: deterministik örnek girdiler (unit test fixtures) ve küçük, temsilî veri setleri.
- Metadata: kitap kimlikleri, analiz meta (zaman damgası normalizasyonu kuralları vs.).

## Shadow semantic fields
- `pattern_matches`: `pattern_id`, `matched_keywords`, `match_snippet`, `source` (summary_ir/narrative/semantic)
- `raw_confidence`, `calibrated_confidence`, `confidence_level`, `confidence_explanation`
- `pattern_activations` / `canonical_activations`: activation-level özetler, evidence listeleri
- `pattern_monitoring`: aggregate izleme yapıları (counts, last_run_iso — deterministik olarak normalize edilmiş)
- `semantic_annotations` / `semantic_labels` — varsa canonical biçime dönüştürülmüş ek açıklamalar

## Production comparison fields
- Production tarafındaki mevcut semantic / summary alanları:
  - `summary_ir` (üretim özeti)
  - `teacher_annotations` veya `editor_labels` (varsa)
  - `semantic_labels`, `topics`, `tags`, `keywords`
  - `short_summary` / `abstract` (varsa)
- Karşılaştırma, yukarıdaki production alanlarla gölge tarafından üretilen eşdeğer semantic çıktılar arasında yapılır (ör. `pattern_activations` ⇄ `semantic_labels`).

## Delta metrics
- Coverage: Shadow'un yakaladığı unique pattern/label oranı vs production.
- Overlap / Jaccard similarity: matched keyword setlerinin ve label kümelerinin kesişim / birleşim oranı.
- Precision-like / recall-like proxies: production etiketleri referans alınarak shadow aktivasyonlarının doğruluk oranı (veya tersine).
- Activation parity: aynı girdide activation var/yok eşleşme oranı (binary parity).
- Confidence delta: `raw_confidence` ve `calibrated_confidence` dağılım farkları, kalibrasyon sapmaları.
- Rank correlation: top-K activation sıralamalarının korelasyonu (Spearman/Kendall).
- Determinism check: aynı girdiden tekrar üretimde tam eşitlik (checksum/hash) sağlanması.
- False positive / false negative proxies: insan doğrulama veya kurallara dayalı küçük sampling ile ölçülecek.
- Aggregate deltas: per-book ve global dağılım farkları (mean/median/std).

## Risk controls
- Shadow-only çalışma: hiçbir üretim değişikliği.
- Feature flag / gate: `RC3_*` adında yeni gate kullanılacaksa bile başlangıçta kapalı tutulur; ancak bu sprintte yeni gate eklememeye öncelik ver.
- Determinism enforcement: transient alanlar canonicalize edilecek (ör. `last_run_iso` reset), output sıraları sabitlenecek.
- Sample-size limits: ilk çalışmalar küçük, temsilî veri setleri üzerinde yapılır.
- Logging ve diagnostics sadece `_runtime_v7_shadow` altında saklanır; production payloadlara yazılmaz.
- Fallback: eğer karşılaştırma pipeline'ı hata verirse, hiçbir üretim verisi etkilenmez ve hata yalnızca diagnostic alanlarda raporlanır.

## Determinism requirements
- Tekrarlanabilirlik: aynı girdi için gölge pipeline her zaman bit-for-bit aynı canonical output üretmeli (ör. JSON canonicalization + sorted lists + normalized timestamps).
- Transient metadata çıkarımı: `last_run_iso`, local debug IDs, runtime durations gibi alanlar canonical çıktılarda veya karşılaştırma anahtarlarda yer almamalı.
- Deterministic sorting: activation ve evidence listeleri stabil bir, belirlenmiş kritere göre sıralanmalı.
- Hash/checksum: canonicalized JSON üzerinde bir checksum veya stable fingerprint üretilecek ve karşılaştırmalarda kullanılacak.

## Verification artefacts
- Canary run JSON örnekleri: gate-open ve gate-closed canary çıktıları.
- Determinism test fixtures: `same_input_produces_same_output` unit testleri ve test-vaka girdileri.
- Gate-closed smoke: gölge alanların production payload içinde gözükmediğini doğrulayan check.
- Delta report: sample başına ve aggregate metricleri gösteren JSON/CSV raporları.

## Benchmark artefacts
- Per-book delta CSV/JSON: coverage, overlap, confidence-delta, rank-correlation.
- Aggregate histograms: confidence dağılımları (production vs shadow), activation count distributions.
- Example activations: ilk 10 pozitif/negatif örneklerle birlikte insan incelenmesi için örnek paketler.
- Reproducible run logs: kullanılan input fixture listesi ve çalıştırma parametreleri (sürüm etiketleri, feature-flag durumları).

## Acceptance criteria
- Production output değişmez: production payloadlarda hiçbir fark tespit edilmez (`equal_without_shadow == true`).
- Deterministik: repeat runlarda canonical checksum/ fingerprint aynı olmalı.
- Shadow bilgi artışı: shadow en azından X ad. (örnek) ek activation veya coverage artışı gösterir; (sayılar sprint sırasında kararlaştırılır).
- Kalite koruması: shadow tarafındaki yüksek confidence aktivasyonlar insan incelemede kabul edilebilir olmalı (ör.: örnek denetimde ≥ 70% doğruluk).
- Risk şartı: hiçbir book-specific heuristic veya sabit kural uygulanmamış olmalı.

## Failure criteria
- Production çıktısında herhangi bir değişiklik gözlenirse (prod değişti) — sprint başarısız sayılır.
- Determinism sağlanamaz; aynı girdiden tekrar tutarlı sonuç alınamıyorsa.
- Shadow çıktıları, insan örnek denetimde açıkça yanlış veya yanıltıcı sonuçlar veriyorsa (örnekleme ile belirlenen eşik altındaysa).
- Shadow pipeline, production metadata veya payloadlarına yazma, değiştirme eğiliminde ise.

---

Not: Bu plan sadece dokümentasyondur — henüz implementasyon, test, benchmark veya commit yapılmayacaktır. Bir sonraki adımınız onaysa, planın altındaki ölçümler (ör. kabul eşikleri için kesin sayısal eşikler) sprint başlangıcında kararlaştırılacaktır.
