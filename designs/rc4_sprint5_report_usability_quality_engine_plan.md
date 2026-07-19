# RC4 Sprint 5 — Report Usability & Quality Engine

Amaç: Kitabı okumayan öğretmen, veli veya editör raporu okuyunca kitap hakkında gerçek ve güvenilir bir fikir sahibi olabilsin; tema ve kazanımlar net, tutarlı ve pedagojik olsun.

## Scope
- Kitap özeti, tema raporu, öğretmen raporu ve Word yapılarını kapsayan kalite iyileştirmeleri.
- Kitap anlatısını özetleyen, kanıt cümlelerini yapıştırmayan rapor üretimi.
- Tematik uyumun ve pedagojik kazanım açıklığının artırılması.
- Karakter doğruluğunu destekleyen genel algoritma iyileştirmeleri.
- Shadow-first, deterministik, equal_without_shadow gereksinimlerinin korunması.

## Non-goals
- Kitap adına özel heuristic geliştirmek.
- Yeni endpoint, route veya deployment açmak.
- Production output üzerinde kontrolsüz değişiklik yapmak.
- Belirli bir kitap için özel düzeltmeler uygulamak.
- SummaryIR / PDF / Teacher / Word çıktılarının yapısını bozmak.
- Yeni semantic model veya pattern eklemek.

## Observed report quality failures
- Özet, kitap metnini değil kanıt cümlelerini tekrarlıyor.
- Tema raporu ve öğretmen raporu ile özet arasında ana tema uyumsuzlukları var.
- Öğrenme kazanımları çok genel veya soyut kalıyor.
- Karakter sınıflandırmalarında ana ve yan karakter ayrımı hatalı.
- Rapor, kitabı okumayan kişiye yeterli karar desteği sağlamıyor.

## Summary quality requirements
- Özet kitap anlatısını açıkça ve özlü biçimde aktarmalı.
- Özet cümleleri kitap içeriğini referanslayıp uygun bağlamda özetlemeli.
- Kanıt cümleleri doğrudan yapıdan ziyade destekleyici olarak kullanılmalı.
- Özet, kitapla ilgili kilit fikirleri ve anlatı akışını net ifade etmeli.

## Theme clarity requirements
- Ana temalar açık, anlaşılır ve rapor boyunca tutarlı olmalı.
- Tema raporu ile öğretmen raporu aynı ana tema setini paylaşmalı.
- Temalar pedagojik hedeflere ve kitap içeriğine uygun olmalı.
- Tema ifadeleri hem özet hem de öğretmen raporu için aynı anlamları taşımalı.

## Learning outcome clarity requirements
- Kazanımlar açık, somut ve öğretim hedefine uygun olmalı.
- Öğrenme kazanımları kitabın çocuklara ne kazandıracağına odaklanmalı.
- Kazanımlar, çok genel veya belirsiz ifadelerden kaçınmalı.
- Kazanımlar tema ve rapor tutarlılığıyla uyumlu olmalı.

## Character correctness requirements
- Karakter rolü tanımları ana ve yan karakterleri doğru ayırt etmeli.
- Karakter rolü analizi kitap adındaki kişi adlarından etkilenmemeli.
- Karakter profilleri raporun diğer bölümleriyle tutarlı olmalı.
- Yan karakterler ve ana karakterler arasında roller net biçimde ayrılmalı.

## Cross-report consistency requirements
- Özet, tema raporu, öğretmen raporu ve Word çıktıları aynı kalite kaynağına dayanmalı.
- Aynı kitap için tüm raporlar ortak tematik ve pedagojik çerçevelerle hizalanmalı.
- Tutarsızlıklar, kalite motoru tarafından tespit edilip azaltılmalı.
- Rapor teslimatı tek bir kullanıcı algısı sunmalı.

## Proposed quality engine
- Rapor üretimindeki kalite sorunlarını algılayan ve düzelten genel bir kalite motoru tasarlanacak.
- Motor, summary, theme, learning outcome ve character katmanlarını ortak bir kalite skorlamasıyla koordine edecek.
- Kalite motoru shadow pipeline içinde çalışacak ve üretim outputunu değiştirmeyecek.
- Motor, özet içeriğinin anlatı sorumluluğunu ve tematik uyumu doğruladığına dair kontrol noktaları içerecek.

## Quality scoring model
- Özet doğruluğu: Kitap anlatısını temsil etme derecesi.
- Tema uyumu: Özet, tema raporu ve öğretmen raporu arasındaki tutarlılık.
- Kazanım netliği: Öğrenme kazanımlarının somut ve pedagojik olması.
- Karakter doğruluğu: Ana/yan karakter rollerinin doğru tanımlanması.
- Rapor kullanılabilirliği: Kitabı okumayan kullanıcı için karar destek düzeyi.
- Model belirli eşiklerle score hesaplayacak, kaynakları shadow-only olarak değerlendirecek.

## Regression books
- Daha önce tespit edilmiş gerçek kitap örnekleri üzerine odaklanacak regresyon vakaları.
- Özette kanıt cümlesi kopyalayan kitap raporları.
- Tema uyumsuzluğu gösteren kitap raporları.
- Kazanımlarının yetersiz kaldığı kitap raporları.
- Karakter rolleri yanlış sınıflandırılan kitap örnekleri.

## Verification artefacts
- `rc4_sprint5_report_usability_quality_engine_verification.json`
- İçerik:
  - sprint
  - plan_created
  - quality_engine_tests_passed
  - regression_tests_passed
  - verification_artifact_created
  - deterministic_all
  - production_output_changed_any
  - equal_without_shadow_all
  - runtime_pipeline_bound_any

## Benchmark artefacts
- `rc4_sprint5_report_usability_quality_engine_benchmark_results.json`
- İçerik:
  - summary quality metrics
  - theme consistency metrics
  - learning outcome clarity metrics
  - character correctness metrics
  - cross-report consistency metrics
  - determinism ve safety göstergeleri

## Acceptance criteria
- Özetler kitap anlatısını yansıtıyor.
- Tema ve kazanım ifadeleri rapor boyunca tutarlı.
- Karakter rolü çözümlemesi isabetli.
- Rapor, kitabı okumayan okura karar desteği sağlıyor.
- Production output kontrolsüz değişmiyor.
- Shadow-first, deterministik ve equal_without_shadow gereksinimleri korunuyor.
- SummaryIR / PDF / Teacher / Word yapıları bozulmuyor.

## Failure criteria
- Özetler hâlâ kanıt cümlelerini kopyalıyorsa.
- Tema raporu ve özet arasında tutarsızlık devam ediyorsa.
- Kazanımlar hâlâ genel ya da yetersizse.
- Karakter rolü hataları rapor kalitesini bozuyorsa.
- Rapor, kitabı okumayan kişiye karar desteği vermiyorsa.
- Production output beklenmedik şekilde değişmişse.
- Shadow-first, deterministik veya equal_without_shadow koşulları bozulmuşsa.
