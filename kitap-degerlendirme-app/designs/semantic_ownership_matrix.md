**Semantic Ownership Matrix**

Tek sayfalık sorumluluk matrisi (katmanlar ve kısa açıklamalar).

| Katman | Sorumluluk | Yapmaması Gereken |
|---|---:|---|
| Pattern Library | Pattern tanımları, metadata, `id`, `category` | Confidence hesaplamak, runtime inference yapmak |
| Confidence Engine | Pattern eşlemeleri için `raw_confidence` ve `calibrated_confidence` üretmek | Canonical serialization veya monitoring kararları almak |
| Semantic Monitor | Grouping, aggregation, monitoring metrikleri, canonical serialization (`pattern_activations`, `pattern_monitoring`) | Confidence üretmek veya pattern inference yapmak |
| Adapter | Upstream `pattern_activations` normalize etmek ve `_runtime_v7_shadow` içine taşımak | Inference veya yeni confidence üretmek; production output’u değiştirmek |
| Runner | Analiz akışını çalıştırmak, mevcut tüketici davranışını sürdürmek, benchmark/okuma | Runner, canonical activation listesini okumak için Stage 3'ten önce davranış değiştirmemeli |

Kısa not: Bu matris, Stage 2 sonrası hedef halini yansıtır. Her katman için açık sınırlar, entegrasyon sırasında toplantıda teyit edilmelidir.
