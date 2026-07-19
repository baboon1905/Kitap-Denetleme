# RC4 Sprint 5 — Report Quality Regression Fix

Amaç: Gerçek kitap analizlerinde ortaya çıkan üç kritik kalite problemini düzeltmek, genel algoritma iyileştirmeleriyle ürün rapor kalitesini yükseltmek ve shadow-only doğrulama modelini korumaktır.

## Scope
- Kitap özetleri, tema raporları ve öğretmen raporları arasındaki tutarsızlıkları ele almak.
- Kitap özetlerinin kitap içeriğini özetlemesi, kanıt cümlelerini yapıştırmaktan kaçınması için algoritma düzeltmeleri yapmak.
- Temel tema uyumsuzluklarını yakalayan ve gideren genel algoritmik iyileştirmeler uygulamak.
- Kitap adındaki kişi adı ve karakter rolü çözümlemesini kalite kapısında doğru şekilde ele almak.
- Mevcut shadow-first, deterministik ve equal_without_shadow gereksinimlerini korumak.

## Non-goals
- Kitap adına özel heuristic eklemek.
- Yeni endpoint, route veya deployment oluşturmak.
- Production output üzerinde kontrolsüz değişiklik yapmak.
- Shadow pipeline dışı yeni bir veri hattı kurmak.
- Ground truth karşılaştırma ya da benchmark veri üretmek; bu sprint algorítmik düzeltme odaklıdır.
- Yeni semantic pattern veya model eklemek.

## Observed failures
- Kitap özetleri analiz edilen kitapları özetlemek yerine kanıt cümlelerini olduğu gibi kopyalıyor.
- Tema raporu, öğretmen raporu ve özet arasında ana tema uyumsuzlukları var.
- Kitap adındaki kişi adı karakter rolü kalite kapısında yanlış yorumlanıyor ve yanlış rol etiketlerine yol açıyor.

## Summary quality defects
- Özet içeriği kitap anlatısından kopuyor.
- Ana temalar arasında tutarsız ifadeler yer alıyor.
- Özet ve rapor çıktıları arasında hedeflenen kitap teması görünmüyor.
- Karakter rolü analizinde kitap adı içerisindeki kişi adları hatalı şekilde işleniyor.

## Cross-report theme consistency defects
- Tema raporu anahtar temaları farklı bir biçimde sunuyor.
- Öğretmen raporu ile özet arasında tematik eşleşme zayıf kalıyor.
- Aynı kitapta çeşitli raporlar arasında ana tema adları ve vurguları aynı değil.
- Tema sonuçları tutarlı bir hikaye veya öğretim hedefi için hizalanmamış.

## Character title/name resolution defects
- Kitap adındaki kişi adı bilgisi, karakter rolü çözümünde yanlış aktarılıyor.
- Karakter rolü kalite kapısı, isim yerine unvan veya kitap adındaki bileşeni yanlış sınıflayabiliyor.
- Bu durum, raporlarda ana karakter rolü ve öğretmen açıklamalarında tutarsızlık üretiyor.

## Proposed algorithmic fixes
- Özet üretiminde kanıt cümlesi ersatzini azaltmak için özetleme modelinin kitap anlatısına odaklanmasını sağlayacak yapısal filtre eklemek.
- Tematik uyum düzeltmesi için özet, tema raporu ve öğretmen raporunun ortak ana tema seti üzerinden tutarlı bir şekilde yeniden değerlendirilmesi.
- Karakter rolü çözümlemesinde kitap adı ve karakter adı ayrımını güçlendirmek için isim-ayırma heuristiği yerine genel dilsel ayrıştırma sigortası uygulamak.
- Rapor çıktılarının ortak bir özetleyici tema profiline göre normalleştirilmesini sağlamak.
- Bu düzeltmeler mevcut shadow-only pipeline içinde gerçekleştirilecek ve üretim verisi değişmeden test edilecek.

## Regression test cases
- Özet içeriğinin kitap anlatısını özetlediğini doğrulayan vaka.
- Özetin kanıt cümlelerini kopyalamadığını kontrol eden vaka.
- Tema raporu ile öğretmen raporu arasındaki ana tema uyumunu test eden vaka.
- Özet ile tema raporu arasındaki ana tema tutarlılığını doğrulayan vaka.
- Kitap adındaki kişi adı kaynaklı karakter rolü hatasını yakalayan vaka.
- Deterministik ve shadow-only davranışı koruyan regresyon testi.

## Verification artefacts
- `rc4_sprint5_report_quality_regression_fix_verification.json`
- İçerik:
  - sprint
  - plan_created
  - algorithm_fix_tests_passed
  - regression_tests_passed
  - verification_artifact_created
  - production_output_changed_any
  - equal_without_shadow_all
  - deterministic_all
  - runtime_pipeline_bound_any

## Benchmark artefacts
- `rc4_sprint5_report_quality_regression_fix_benchmark_results.json`
- İçerik:
  - summary quality metrics
  - theme consistency metrics
  - character role resolution metrics
  - determinism kontrolü
  - production output safety göstergeleri

## Acceptance criteria
- Kitap özetleri kanıt cümlelerini doğrudan yapıştırmıyor, kitap anlatısını temsil ediyor.
- Tema raporu, öğretmen raporu ve özet arasında ana tema uyumu sağlanıyor.
- Karakter rolü çözümlemesi kitap adındaki kişi adlarında doğru çalışıyor.
- Shadow-only, deterministik ve equal_without_shadow güvenlik kuralları korunuyor.
- Algoritma genel düzeyde iyileştiriliyor; kitap özel heuristic eklenmiyor.
- Verification ve benchmark artefaktları tanımlanmış formatta planlanıyor.

## Failure criteria
- Özetler hâlâ kanıt cümlelerini yapıştırıyorsa.
- Tema raporu ve özet arasında ana tema uyumsuzluğu devam ediyorsa.
- Kitap adındaki kişi adı karakter rolü kalitesi hâlâ yanlış sınıflandırıyorsa.
- Production output uncontrolled değişiyorsa.
- Shadow-first veya deterministik gereksinimler bozuluyorsa.
- `equal_without_shadow` sağlanmıyorsa.
