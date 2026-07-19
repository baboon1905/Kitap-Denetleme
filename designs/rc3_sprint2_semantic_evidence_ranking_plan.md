# RC3 Sprint 2 — Semantic Evidence Ranking

Amaç: Shadow semantic pattern activations için evidence kalitesini sıralamak.

## Scope
- Shadow pipeline tarafından üretilen `pattern_activations` ve ilgili evidence öğeleri üzerinde kalite sıralaması sağlamak.
- Sıralama yalnızca mevcut shadow çıktıları üzerinde çalışır; production çıktısı hiç değişmez.
- Amaç, aktivasyonların içindeki en güvenilir, en anlamlı kanıtları üst sıralara taşımak.

## Non-goals
- Production output üzerinde değişiklik yapmak.
- Yeni endpoint/route eklemek.
- PDF, summary_ir, teacher veya word kaynaklarını değiştirmek.
- Kitap adı/sadece tek kitap için özel heuristic geliştirmek.
- Yeni deployment veya canlı trafik yönlendirmesi yapmak.
- Shadow pipeline dışında yeni semantic üretim mantığı kurmak.

## Inputs
- Shadow `pattern_activations` veya `pattern_matches` içindeki evidence öğeleri.
- Upstream üretim metadata ve `shadow` diagnostics alanları.
- `summary_ir`, `narrative`, `semantic` orijinli match/snippet verileri.
- Mevcut confidence alanları (`raw_confidence`, `calibrated_confidence`, `confidence_level`) yalnızca ranking sinyali olarak kullanılabilir, ama confidence hesaplama yeni bir motor değil.

## Evidence sources
- `pattern_activations` içindeki `evidence` listeleri.
- `pattern_matches` öğelerinde yer alan `match_snippet`, `matched_keywords`, `source` bilgileri.
- `summary_ir`, `semantic`, `narrative` kaynak gösterimi ve açıklayıcı snippet textleri.
- Gölge pipeline’ın derecelendirme dışı metadata’ları (ör. `pattern_id`, `pattern_category`, `algorithm_version`).

## Ranking signals
- Evidence’nun `source` türü ve güvenilirlik derecesi.
- `matched_keywords` sayısı ve kalitesi.
- Match/snippet uzunluğu ve içerik zenginliği.
- `pattern_id` veya `pattern_category` bağlamında kullanılan kanıt türü.
- Confidence alanlarının varlığı ve yüksekliği (sadece sinyal, score hesaplama değil).
- Tekrarlanan veya özgün kanıtlar; duplicate/overlap olup olmadığı.
- Evidence öğesinin `reason`, `explanation` veya `recommendation` gibi açıklama alanları.

## Ranking output schema
- `evidence_rankings`: sıralı evidence listesi.
- Her entry için:
  - `pattern_id`
  - `evidence_id` veya deterministik anahtar
  - `source`
  - `matched_keywords`
  - `match_snippet`
  - `rank_score`
  - `rank_position`
  - `ranking_signals`: hangi sinyallerle sıralandığına dair kısa özet
- `canonical_activations` / `pattern_activations` içinde sıralı `evidence` listeleri döndürülürse, sıralama deterministic ve stabil olmalıdır.

## Determinism rules
- Aynı shadow input için sıralama her zaman aynı olmalı.
- `rank_score` hesapları deterministik olmalı; random veya zaman-temelli eleman içermeyecek.
- Sıralama işlemi için kullanılan tüm liste ve dict yapıları deterministik olarak sıralanmalı.
- Transient metadata (ör. timestamp, runtime durasyonu) çıkartılmalı veya normalize edilmeli.
- `evidence_id`/anahtarlar deterministik türetilmeli.

## Production safety rules
- Hiçbir modül doğrudan production payload veya production-only alanı değiştirmemeli.
- Shadow-only işlemler `shadow` tüneli veya `_runtime_v7_shadow` altındaki ek alanlarla sınırlı kalmalı.
- `equal_without_shadow == true` korunmalı.
- SummaryIR/PDF/Teacher/Word kaynaklarında herhangi bir değişim olmamalı.
- Yeni run script veya runner sadece diagnostic/benchmark artefact üretmeli, production davranışını etkilememeli.

## Verification artefacts
- `rule` tabanlı smoke testler: aynı input her zaman aynı ranking üretmeli.
- `production safety` testi: production payloadları değişmeden bırakmalı.
- `determinism` testi: tekrar çalıştırma sonrası fingerprint/çıktı eşitliği.
- `ranked evidence` örnek JSON raporları.
- `verification` JSON: `production_output_changed: false`, `equal_without_shadow: true`, `deterministic: true`.

## Benchmark artefacts
- `ranked_evidence_summary.json`: evidence sıralama dağılımları, top-N signal dağılımları.
- `per_pattern_ranking_metrics.json`: pattern bazında en güçlü kanıtların sayısı ve ortalama rank.
- `deterministic_ranking_benchmark.json`: aynı input için tekrar eden sıralama doğrulama sonuçları.
- `shadow_production_ranking_smoke.json`: canlı olmayan run sonuçları ve safety durumları.

## Acceptance criteria
- Ranking modülü shadow-only olarak çalışmalı.
- Aynı shadow input tekrarlandığında sıralama tamamen aynı olmalı.
- Üretilen ranking schema istenen alanları içermeli.
- Production safety kontrolleri başarısız olmamalı.
- Kitap-özel heuristic kullanılmamış olmalı.

## Failure criteria
- Production payload veya production output’ta herhangi bir değişiklik varsa.
- Ranking sıralaması deterministik değilse.
- Yeni evidence ranking modülü sadece belirli kitaplara veya patternlara özel kurallar kullanıyorsa.
- `equal_without_shadow` doğrulanamıyorsa.
- Sıralama sonuçları `rank_score` veya `rank_position` beklenen şemayı karşılamıyorsa.

---

Not: Bu plan sadece tasarımdır. Henüz implementasyon, test veya benchmark yapılmayacaktır.
