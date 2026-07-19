# RC4 Sprint 2 — Real Book Shadow Validation

Amaç: Validation dataset içindeki kitapları shadow semantic pipeline’dan geçirerek gerçek kitap bazlı kalite metrikleri üretmek.

## Scope
- RC4 Sprint 1 datasetindeki kitaplar üzerinden mevcut shadow semantic pipeline’ı çalıştırmak.
- Üretilen shadow sonuçlar ile her kitap için kalite metrikleri ve aggregate ölçümler elde etmek.
- Çıktılar sadece shadow katmanında tutulacak ve production çıkışına hiç dokunulmayacak.
- Plan, input gereksinimleri ve beklenen artefaktları tanımlayacak.

## Non-goals
- Production output üzerinde değişiklik yapmak.
- Runtime production entegrasyonu eklemek.
- Yeni endpoint, route veya deployment oluşturmak.
- Kitap adına özel heuristicler geliştirmek.
- Yeni semantic algoritmalar, yeni patternler veya yeni confidence/ranking/explainability/acceptance üretmek.
- Validation dataset üretmek; bu sprint sadece mevcut datasetin shadow doğrulamasını yapacak.

## Inputs
- RC4 Sprint 1 tarafından oluşturulmuş validation dataset.
- Mevcut semantic shadow pipeline modülleri.
- Pattern library ve mevcut confidence/ranking/explainability/acceptance şemaları.
- Shadow run için deterministik sistem konfigürasyonları.

## Validation dataset fields
- `book_id`
- `isbn`
- `title`
- `publisher`
- `grade`
- `genre`
- `language`
- `page_count`
- `validation_status`
- `human_review_status`
- `dataset_version`
- `generated_at`

## Shadow pipeline fields
- `pattern_matches`
- `confidence`
- `pattern_activations`
- `ranked_evidence`
- `explanations`
- `acceptance_decisions`
- `human_review_package`
- `delta_analysis`
- `safety` metadata: `shadow_only`, `production_output_changed`, `equal_without_shadow`, `orchestrator_enabled`
- `stage_order`

## Per-book metrics
- `pattern_match_count`
- `pattern_activation_count`
- `ranked_evidence_count`
- `explanation_count`
- `acceptance_decision_count`
- `human_review_item_count`
- `delta_analysis_present`
- `production_output_changed` (her zaman false)
- `equal_without_shadow` (her zaman true)
- `determinisitic_run` (her kitap için tekrar üretilebilirlik)

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
- Aynı validation dataset ve aynı shadow konfigürasyon ile çıktı her zaman aynı olmalı.
- Rastgele veya zaman bağımlı bilgi kullanılmamalı.
- Liste sıralamaları ve meta değerler stabil olmalı.
- Per-book metric hesapları tutarlı olmalı.

## Production safety
- Production output değişmeyecek.
- Shadow-first korunacak.
- Runtime production entegrasyonu yapılmayacak.
- Yeni endpoint/route eklenmeyecek.
- Kitap adına özel heuristic yok.
- `equal_without_shadow == true` korunacak.
- Mevcut semantic modüller yalnızca shadow çalıştırılacak.

## Benchmark artefacts
- `rc4_sprint2_shadow_validation_benchmark_results.json`
- İçerik: aggregate metricler, determinism kontrol raporu, stage order tutarlılığı, üretim güvenlik durumu.
- Her kitap için özet metrik satırları ve toplamlar.

## Verification artefacts
- `rc4_sprint2_final_verification.json`
- İçerik: sprint, plan_created, shadow_validation_tests_passed, benchmark_artifact_created, final_verification_created, stage_order_consistent, deterministic_all, production_output_changed_any, equal_without_shadow_all, runtime_pipeline_bound.
- Shadow pipeline çağrısı sadece kontrollü validation için ve production tarafına bağlı olmadan gerçekleştiği doğrulanmalı.

## Acceptance criteria
- Shadow validation işlemi sadece planlanan dataset içindeki kitaplar için yapılmalı.
- Çıktılar production alanına dokunmadan shadow’da kalmalı.
- Determinism ve `equal_without_shadow` korunmalı.
- Benchmark ve verification artefaktları planlanan formatta tanımlanmalı.
- Yeni endpoint, route veya kitap-spesifik heuristic yok.

## Failure criteria
- Production output değişirse.
- `equal_without_shadow` bozulursa.
- Deterministik çıktı sağlanmazsa.
- Shadow validation planlanan alanların dışına çıkarsa.
- Yeni semantic algoritma veya pattern eklenirse.
- Runtime pipeline production’a bağlanırsa.
