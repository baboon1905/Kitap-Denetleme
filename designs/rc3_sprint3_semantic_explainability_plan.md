# RC3 Sprint 3 — Semantic Explainability Layer

Amaç: Shadow semantic kararlarının neden üretildiğini insan tarafından anlaşılır hale getirmek.

## Scope
- Shadow pipeline'ın (delta analyzer, evidence ranker, pattern activations) her aşamasında insan-okunur açıklamalar (explanations) üretmek.
- Açıklamalar, karar verilen her pattern, evidence ve rank için "neden" cevabı sağlamalıdır.
- Explanations yalnızca shadow-only alanlarında saklanacak; production output'a dokunmayacak.
- Amaç, shadow semantic çıktılarını audit ve validation için insan analitiğine açmak.

## Non-goals
- Production output üzerinde değişiklik yapmak.
- Yeni endpoint/route eklemek.
- PDF, summary_ir, teacher veya word kaynaklarını değiştirmek.
- Kitap adı veya tek kitap bazlı özel heuristic geliştirmek.
- Explanation altyapısını LLM veya dış model ile entegre etmek.
- Yeni deployment veya canlı trafik yönlendirmesi yapmak.
- Shadow pipeline dışında yeni semantic üretim mantığı kurmak.

## Inputs
- Shadow delta analysis sonuçları: coverage_delta, overlap_score, production_only_signals, shadow_only_signals.
- Shadow evidence ranking sonuçları: rank_score, ranking_signals (evidence_count, source_weight, semantic_density, cluster_support).
- Canonical pattern_activations: pattern_id, evidence_count, source, confidence alanları.
- Upstream pattern matching metadata: matched_keywords, match_snippet, pattern_category.
- Production payload karşılaştırma: production_only_signals, shadow_only_signals.

## Explainability sources
- **Delta explanations**: Neden shadow vs production'da fark var? (coverage artışı, overlap düşüklüğü, yeni signals)
- **Evidence ranking explanations**: Neden bu evidence 1. sıradaki? (evidence_count etkisi, source_weight derecesi, semantic_density katkısı, cluster_support)
- **Confidence explanations**: Upstream confidence alanlarından alınan mevcut explanations; yeniden hesaplama yok.
- **Pattern activation explanations**: Neden bu pattern seçildi? (hangi source'dan, kaç evidence, aggregate confidence, status)
- **Production delta explanations**: Neden production'da bu pattern yok ama shadow'da var? (shadow'nun ek coverage'ı, farklı source ağırlıkları)

## Explanation output schema
- Per activation/evidence/rank item için explanation nesnesi:
  - `decision`: Kısa karar özeti (ör. "Pattern seçildi", "Evidence en yüksek rank aldı")
  - `reasoning`: Neden açıklaması (ör. "Semantic source ağırlığı yüksek")
  - `supporting_signals`: Karar destekleyen sinyaller listesi (ör. [evidence_count: 3, source_weight: 1.0])
  - `confidence_level`: Açıklamanın kendisine olan güven (deterministik hesaplama)
  - `alternatives_considered`: Eğer varsa, neden diğer alternatifleri seçilmedi?
  - `audit_trail`: Hangi algoritmik adımlar takip edildi?
- Delta explanations:
  - `coverage_delta_reason`: Neden shadow coverage daha yüksek?
  - `overlap_delta_reason`: Neden overlap düşük?
  - `unique_signals_in_shadow`: Shadow'un ek kattığı sinyallerin açıklaması.

## Explanation rules
- Deterministic: Her açıklama, girdiye dayalı olarak her zaman aynı olmalıdır.
- Tersine çevrilebilir (traceable): Açıklama, upstream modulün (ranker, delta analyzer vb.) çıktısından doğrudan türetilmeli.
- Sabit şablon kullanma: Explanation template'leri hardcode edilmeli (ör. "Evidence #{N} ranked first due to source weight of {W} and evidence count of {C}").
- Book-agnostic: Açıklamalar herhangi bir kitap adı veya kitap-spesifik bilgi içermemeli.
- Signal-focused: Açıklamalar ranking signals, source types, evidence characteristics üzerine odaklanmalı.

## Determinism rules
- Tüm açıklamalar deterministik türetilmeli; random eleman veya timestamp içermemeli.
- Template interpolation için kullanılan değerler (evidence_count, source_weight, vb.) sabitlenmiş precision ile roundlanmalı.
- Explanation order (ör. explanation listeleri) deterministik sıralama kriteriyle stabil tutulmalı.
- Duplicate explanations otomatikman deduplicate edilmeli veya sadece bir kez saklanmalı.

## Production safety rules
- Hiçbir explanation production payload veya production-only alanı değiştirmemeli.
- Explanations yalnızca shadow-only alanlarında (ör. `_runtime_v7_shadow.explanations`) saklanmalı.
- `equal_without_shadow == true` korunmalı; explanations çıkarıldığında payload aynı olmalı.
- SummaryIR/PDF/Teacher/Word kaynaklarında herhangi bir değişim olmamalı.
- Yeni run script veya explanation üreticisi sadece diagnostic/benchmark artefact oluşturmalı.

## Verification artefacts
- `determinism` testleri: Aynı input için tekrarlanan explanation aynı olmalı.
- `production safety` testleri: Production payload hiçbir şekilde değişmemeli.
- `explanation coverage` raporu: Kaç activation/evidence/delta item açıklandı? Kaç tane açıklama olmadan kaldı?
- `explanation schema compliance` raporu: Üretilen explanations istenen schema'yı karşılıyor mu?
- `verification` JSON: `production_output_changed: false`, `equal_without_shadow: true`, `deterministic: true`.

## Benchmark artefacts
- `explanation_coverage_summary.json`: Activation başına explanation coverage, evidence başına explanation coverage.
- `explanation_quality_metrics.json`: Template match rate, determinism check pass rate, duplicate explanation count.
- `deterministic_explanation_benchmark.json`: Aynı input tekrar çalıştırıldığında explanation hash/fingerprint eşitliği.
- `explanation_examples.json`: Örnek explanations (ör. top 5 activation explanation, top 5 ranking explanation, top 3 delta explanation).
- `shadow_production_explanation_safety.json`: Production payload integrity checks, shadow-only storage checks.

## Acceptance criteria
- Explanations modülü shadow-only olarak çalışmalı.
- Aynı shadow input tekrarlandığında explanations tamamen aynı olmalı (deterministik).
- Üretilen explanation schema istenen alanları içermeli (decision, reasoning, supporting_signals, confidence_level).
- Production safety kontrolleri başarısız olmamalı.
- Kitap-özel heuristic kullanılmamış olmalı.
- Explanations, upstream modules (ranker, delta analyzer vb.) outputlarından traceable olmalı.

## Failure criteria
- Production payload veya production output'ta herhangi bir değişiklik varsa.
- Explanations deterministik değilse (aynı input'tan farklı explanation üretirse).
- Explanation schema beklenen alanları karşılamıyorsa.
- `equal_without_shadow` doğrulanamıyorsa.
- Explanations kitap adı veya kitap-spesifik bilgi içeriyorsa.
- Explanations upstream modules'dan trace edilemiyorsa.

---

Not: Bu plan sadece tasarımdır. Henüz implementasyon, test veya benchmark yapılmayacaktır.
