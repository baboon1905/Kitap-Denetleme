# RC4 Sprint 1 — Real Book Validation Dataset

Amaç: Gerçek kitaplar üzerinde shadow semantic pipeline’ı değerlendirmek için küçük ama kontrollü bir validasyon veri seti hazırlamak.

## Scope
- RC3’te kurulan semantic shadow pipeline’ın gerçek kitaplar üzerinde doğrulanması için kontrol edilmiş bir veri seti seçmek.
- Veri seti, sadece shadow semantic çıktılarının üretildiği, production çıktısının değişmediği ve runtime pipeline’a bağlanmadığı koşullarda kullanılacak.
- Validasyon veri seti, kitap başlıklarından bağımsız, genel semantic kalite sinyallerine dayanarak seçilecek.
- Veri seti tanımı, gerekli metadata ve doğrulama alanları belge halinde sunulacak.

## Non-goals
- Production output üzerinde hiçbir değişiklik yapmak.
- Runtime production entegrasyonu eklemek.
- Yeni endpoint veya route oluşturmak.
- Kitap adına özel heuristikler veya özel vaka kuralları tanımlamak.
- Yeni semantic algoritmalar veya üretimler eklemek.
- Veri setini geniş kapsamlı benchmark’a dönüştürmek; amaç sadece kontrollü validasyon datasetidir.

## Dataset selection criteria
- Gerçek kitaplardan oluşan, temsil yeteneği olan küçük bir örneklem olmalı.
- Veri seti, RC3’te kullanılan shadow pipeline’ın mevcut input formatını desteklemeli.
- Seçilen kitapların kaynakları, kullanım hakkına uygun ve analize açık olmalı.
- Kitapların semantic içerikleri, RC3 pattern library ve bağlamına uygun olmalı.
- Veri seti, aşırı optimize edilmiş ya da üretim verisiyle eşleşecek şekilde seçilmemeli; gerçek dünya çeşitliliği hedeflenmeli.

## Book diversity criteria
- Tür çeşitliliği: kurgu / kurgu dışı, eğitim / edebiyat / çocuk / genç / kültürel içerik.
- İçerik uzunluğu: kısa, orta ve uzun kitapları kapsayacak şekilde dengelenmiş.
- Dilsel çeşitlilik: Türkçe içeriğe dayalı varyasyon ve farklı anlatım stilleri.
- Tematik çeşitlilik: macera, dostluk, dayanıklılık, merhamet, umut gibi farklı ana temalar.
- Yapısal çeşitlilik: özet, tema listesi, karakter rolleri veya anlatım metni gibi farklı semantik input biçimleri.

## Required metadata
- `book_id`: benzersiz, üretim davranışıyla ilişkili olmayan anahtar.
- `book_title`: sadece insan referansı için kullanılacak; seçime özel heuristic olarak kullanılmayacak.
- `author` veya `source`: veri kaynağının izlenebilirliği için minimal bilgi.
- `language`: içeriğin dilini belirtir.
- `content_type`: kurgu / kurgu dışı / eğitim / çocuk vb.
- `data_source`: kaynağın sınıfı (örnek: açık erişimli kitap, eğitim koleksiyonu, örnek veri seti).
- `selection_reason`: neden veri setine alındığını açıklayan kısa not.
- `validation_tags`: dataset içindeki özel amaçlı alt grupları işaretlemek için etiketler.

## Human review fields
- `review_case_id`: insan inceleme sürecinde referans için benzersiz kimlik.
- `review_notes`: insan doğrulayıcıların kullandığı gözlem açıklamaları.
- `validation_decision`: review sırasında alınan sonuçlar (örnek: pass, fail, needs_review).
- `reviewer_role`: incelemenin hangi rol tarafından yapıldığını belirtir.
- `review_timestamp`: incelenme zamanı, ancak deterministik pipeline çıktısına dahil edilmeyecek; sadece doğrulama kaydı olarak saklanmalı.
- `review_focus`: insanın baktığı ana kalite alanları (örnek: semantic coverage, explanation adequacy, delta safety).

## Shadow output fields
- `pattern_matches`: RC3 pattern match producer çıktısı.
- `confidence`: pattern match confidence değerleri.
- `pattern_activations`: canonical activation çıktıları.
- `ranked_evidence`: semantic evidence sıralaması.
- `explanations`: explainability layer sonuçları.
- `acceptance_decisions`: acceptance gate kararları.
- `human_review_package`: human review paketi sonuçları.
- `delta_analysis`: shadow vs production delta analiz sonuçları.
- `safety`: `shadow_only`, `production_output_changed`, `equal_without_shadow`, `orchestrator_enabled` gibi metadata.
- `stage_order`: iş akışı adımlarının sabit sırasını kaydeden liste.

## Validation metrics
- `production_output_changed`: her zaman false olmalı.
- `equal_without_shadow`: her zaman true olmalı.
- `deterministic_all`: aynı input için tekrarlanabilir çıktılar olmalı.
- `stage_order_consistent`: tüm vakalarda sabit RC3 aşama sırası korunmalı.
- `pattern_match_coverage`: seçilen kitaplar için toplam pattern match sayıları.
- `explanation_presence`: her vaka için explainability çıktısı var mı.
- `acceptance_decision_consistency`: aynı vaka tekrar çalıştırıldığında kabul/gözden geçirme/reddetme kararları aynı olmalı.
- `dataset_diversity_compliance`: seçilen kitapların çeşitlilik kriterlerine uyumu.
- `human_review_alignment`: insan incelemesi ile shadow çıktılarının tutarlılığı.

## Determinism rules
- Shadow pipeline çıktıları sabit olmalı; rastgelelik veya zaman bağımlı bilgi içermemeli.
- Aynı `book_id` ve aynı input metadata ile tekrarlandığında sonuçlar eşit olmalı.
- Çıktı sıralamaları, JSON alanları ve liste sıralamaları stabil olmalı.
- Deterministiklik doğrulaması benchmark veya final verification artefaktlerinde belgelemeli.

## Production safety
- Production sonuçları hiçbir zaman değişmeyecek.
- Shadow-first prensibi korunacak; production akışı dışında ek davranış yok.
- Runtime production entegrasyonu yapılmayacak.
- Yeni endpoint, route veya deployment eklenmeyecek.
- `equal_without_shadow == true` korunacak.
- Veri seti seçimi kitap adına özel heuristic içermeyecek.

## Benchmark artefacts
- `rc4_sprint1_real_book_validation_dataset_benchmark_results.json`: dataset validasyon ölçümlerini içerir.
- İçerik: total_cases, stage_order_consistent, deterministic_all, production_output_changed_any, equal_without_shadow_all, pattern_match_coverage, explanation_presence, acceptance_decision_consistency.
- Her vakaya ait özet satırları ve genel tutarlılık metrikleri.

## Verification artefacts
- `rc4_sprint1_real_book_validation_dataset_final_verification.json`: sprint kapanış doğrulaması.
- İçerik: sprint adı, plan_created, dataset_ready, benchmark_artifact_created, final_verification_created, production_output_changed_any, equal_without_shadow_all, deterministic_all, runtime_pipeline_bound, new_algorithm_added.
- Ek doğrulama: dataset seçim kriterleri ve production safety kontrolleri sağlandı.

## Acceptance criteria
- Tasarlanan veri seti RC4 hedeflerine uygun olmalı.
- Plan, gerçek kitaplarda shadow validation için yeterli bilgi içermeli.
- Production safety ve shadow-first kuralları açıkça tanımlanmış olmalı.
- Determinism ve equal_without_shadow gereksinimleri plan kapsamında net olmalı.
- Yeni endpoint/route, runtime entegrasyonu veya kitap-spesifik heuristic yok.
- Plan dokümanı `designs/rc4_sprint1_real_book_validation_dataset_plan.md` olarak oluşturulmuş olmalı.

## Failure criteria
- Plan gerçek kitap validasyonu için yetersiz veya belirsiz olursa.
- Production safety kuralları tam tanımlanmamışsa.
- Determinism veya equal_without_shadow koşulları atlanmışsa.
- Dataset seçiminde kitap adına özel heuristic veya üretim davranışı etkileyen kriterler varsa.
- Benchmark ve verification artefaktları plan aşamasında bile olsa kontrol edilmemişse.
