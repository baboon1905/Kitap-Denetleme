# Artifact Guidelines

Bu belge proje seviyesinde `Verification` ve `Benchmark` artefact ayrımını tanımlar ve standartlaştırır.

## Verification Artefact

Amaç:

- Bir özelliğin doğru çalıştığını ve kabul kriterlerini karşıladığını kanıtlamak.

İçerir:

- Acceptance kriterleri
- Unit / regression doğrulamaları
- Deterministic kontroller
- `equal_without_shadow` kontrolleri
- Production leak (gölge bilgilerinin üretime sızmaması) kontrolleri

İçermez:

- Benchmark sonuçları
- Kitap bazlı analiz çıktılarını
- Performans raporlarını

## Benchmark Artefact

Amaç:

- Gerçek kitaplar üzerinde çalıştırıldığında ortaya çıkan sonuçları saklamak ve raporlamak.

İçerir:

- Benchmark kitap listesi
- Endpoint sonuçları (PDF / Word / Teacher vs)
- Performans ölçümleri
- Confidence, evidence_count, supporting_signals gibi sınıflandırma çıktıları
- Gerçek analiz çıktıları (shadow dahil)

İçermez:

- Feature-level verification-only metrikleri (ör. test listesi veya internal regression assertions)

## Dosya Ayrımı Standardı

- Her faz için iki ayrı dosya kullanılacaktır:

```
phaseXX_feature_verification.json
phaseXX_feature_benchmark_results.json
```

- Bu iki dosya hiçbir zaman birleştirilmez.

## Referans Alanı

- Verification dosyası içinde benchmark sonuçlarına referans olarak yalnızca bir dosya adı içerebilir:

```json
{ "benchmark_results_file": "phaseXX_feature_benchmark_results.json" }
```

- Ancak benchmark içeriği `verification` dosyalarında yer almaz.

## Neden

Single Responsibility Principle (artefact seviyesinde). Kod mimarisinde uyguladığımız net ayrımı dokümantasyon mimarisine de taşıyoruz.
