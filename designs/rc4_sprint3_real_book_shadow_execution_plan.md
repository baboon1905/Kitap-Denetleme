# RC4 Sprint 3 — Real Book Shadow Execution

Amaç: Validation dataset içindeki kitapları gerçek semantic orchestrator shadow pipeline’dan geçirerek kitap bazlı semantic çıktılar üretmek.

## Scope
- RC4 Sprint 1’de hazırlanan validation dataset içindeki kitapları alıp RC4 Sprint 2A/B’da tanımlanan shadow validation skeletinin üzerine gerçek semantic orchestrator shadow pipeline çalıştırmak.
- Çıktılar kitap bazlı semantic sonuçlar olacak ve tüm işlemler shadow-only gerçekleştirilecek.
- Üretilen sonuçlar `equal_without_shadow == true` ve deterministiklik gereksinimlerine uygun olmalıdır.

## Non-goals
- Production output üzerinde değişiklik yapmak.
- Runtime production entegrasyonu eklemek.
- Yeni endpoint, route veya deployment oluşturmak.
- Kitap adına özel heuristicler geliştirmek.
- Yeni semantic algoritmalar veya patternler eklemek.
- Validation dataset üretmek.
- Shadow pipeline dışı başka bir veri işleme hattı kurmak.

## Inputs
- `rc4_sprint1_validation_dataset.json`
- Mevcut RC3 semantic orchestrator shadow pipeline modülleri.
- Pattern library, confidence, ranking, explainability, acceptance ve human review package mevcut veri yolları.
- Deterministik çalışma için sabit konfigürasyon ve feature flag ayarları.

## Validation dataset usage
- Dataset yalnızca kitap meta verilerini ve validation durumunu içerir.
- Her kitap için `book_id`, `isbn`, `title`, `publisher`, `grade`, `genre`, `language`, `page_count`, `validation_status`, `human_review_status` kullanılacak.
- Dataset içeriği değiştirilmeden shadow pipeline girişine dönüştürülecek.
- Veri setindeki her kitap için shadow çalıştırma sonucu ayrı ayrı üretilecek.

## Semantic orchestrator usage
- Mevcut `runtime_v7/semantic_orchestrator.py` ve ilgili RC3 modülleri kullanılacak.
- Orchestrator, shadow-only çalıştırılacak ve production payload ile output herhangi bir şekilde değiştirilmeyecek.
- Orchestrator çağrısı sırasında `semantic_orchestrator_enabled` feature flag belirlenip, `equal_without_shadow` koruyacak şekilde kullanılacak.
- `rc4_sprint2_real_book_shadow_validation_results.json` girdilerinden farklı olarak gerçek orchestrator çıktıları üretilecek.

## Per-book shadow output schema
- `book_id`
- `pattern_matches`
- `confidence`
- `pattern_activations`
- `ranked_evidence`
- `explanations`
- `acceptance_decisions`
- `human_review_package`
- `delta_analysis`
- `safety`: `shadow_only`, `production_output_changed`, `equal_without_shadow`, `orchestrator_enabled`
- `stage_order`
- `generated_at`: `1970-01-01T00:00:00Z`

## Aggregate metrics
- `total_books`
- `total_pattern_matches`
- `total_pattern_activations`
- `total_ranked_evidence`
- `total_explanations`
- `total_acceptance_decisions`
- `total_human_review_items`
- `books_with_delta_analysis`
- `stage_order_consistent`
- `deterministic_all`
- `production_output_changed_any`
- `equal_without_shadow_all`

## Determinism rules
- Aynı validation dataset ve sabit konfigurasyon ile çalıştırma her zaman aynı çıktıyı üretmelidir.
- Rastgelelik ya da zaman bağımlılığı kullanılmayacaktır.
- Liste sıralamaları, JSON alanları ve aggregate hesaplamalar sabit ve tekrarlanabilir olmalıdır.
- Orchestrator sonuçları her kitap için deterministik olmalıdır.

## Production safety
- Production output hiçbir şartta değişmemelidir.
- Shadow-first korumalıdır.
- Runtime production entegrasyonu yapılmayacaktır.
- Yeni endpoint veya route oluşturulmayacaktır.
- Kitap adına özel heuristic kullanılmayacaktır.
- `equal_without_shadow == true` korunmalıdır.
- Shadow çalıştırma sadece validation dataset için yapılacaktır.

## Benchmark artefacts
- `rc4_sprint3_real_book_shadow_execution_benchmark_results.json`
- İçerik: aggregate metricler, determinism kontrolü, stage order tutarlılığı, `production_output_changed_any`, `equal_without_shadow_all`.
- Per-book özet metrik satırları.

## Verification artefacts
- `rc4_sprint3_final_verification.json`
- İçerik: sprint, plan_created, shadow_execution_tests_passed, artifact_producer_test_passed, execution_results_created, total_books, stage_order_consistent, deterministic_all, production_output_changed_any, equal_without_shadow_all, runtime_pipeline_bound.
- Shadow pipeline execution güvenlik doğrulamaları.

## Acceptance criteria
- Mevcut orchestrator shadow pipeline kullanılarak kitap bazlı semantic çıktılar üretilebilir.
- Çıktılar shadow-only ve production output’a dokunmadan elde edilir.
- Determinism ve `equal_without_shadow` sağlanır.
- Benchmark ve verification artefaktları planlanan formatta tanımlanır.
- Kitap-spesifik heuristic yok.

## Failure criteria
- Production output değişirse.
- `equal_without_shadow` bozulursa.
- Deterministik çıktı garantilenmezse.
- Shadow pipeline gerçek production ile bağlanırsa.
- Orchestrator dışında yeni semantic analiz ya da pattern eklenirse.
