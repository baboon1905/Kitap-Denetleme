# RC3 Sprint 4 — Semantic Acceptance Gates

Amaç: Shadow semantic çıktılarının production'a aday olup olamayacağını objektif kalite kapıları ile değerlendirmek.

## Scope
- Mevcut shadow semantic çıktıları (pattern activations, confidence, evidence ranking, explainability, delta analysis) kullanarak kabul/red/inceleme kararları üretmek.
- Her shadow karar için bir acceptance gate sonucu üretmek: accepted, review, rejected.
- Kararların nedenini izlenebilir ve deterministik hale getirmek.
- Production output üzerinde değişiklik yapmadan, shadow-first yaklaşımı koruyarak karar mekanizmasını tanımlamak.

## Non-goals
- Yeni semantic analiz üretmek.
- Production output üzerinde değişiklik yapmak.
- SummaryIR / PDF / Teacher / Word kaynaklarını değiştirmek.
- Yeni endpoint, route veya deployment eklemek.
- Kitap adına özel heuristic geliştirmek.
- Yeni confidence, ranking veya delta üretimi yapmak.
- Runtime pipeline'ı production'a bağlamak.

## Inputs
- Canonical pattern activations
- Existing confidence values
- Evidence ranking results
- Explainability outputs
- Shadow vs production delta analysis
- Deterministic metadata required for traceability

## Gate decision model
- Her pattern veya semantic karar için tek bir gate sonucu üretilir.
- Sonuçlar şu üç kategoriden birine düşer:
  - accepted: yeterli destek, yeterli güven ve kabul edilebilir delta/coverage durumu varsa
  - review: destek var ama net karar verilemeyecek kadar zayıf veya çelişkili ise
  - rejected: yeterli destek yoksa, güven zayıfsa veya kalite kriterleri karşılanmıyorsa
- Karar mantığı, mevcut sinyallerin birleşimiyle tanımlanır; yeni sinyal üretimi yoktur.

## Acceptance signals
- Pattern activation support
  - Aktivasyon var mı?
  - Aktivasyon durumu ne? (active/candidate vb.)
- Confidence signal
  - Mevcut confidence değeri yeterli mi?
  - Güven seviyesi kabul edilebilir mi?
- Evidence ranking signal
  - Rank seviyesi yeterli mi?
  - Evidence count ve source weight yeterli mi?
- Explainability signal
  - Açıklama var mı?
  - Açıklama yeterince destekleyici mi?
- Delta signal
  - Coverage delta kabul edilebilir mi?
  - Overlap / delta durumu karar için uygun mu?

## Decision schema
- Her karar için aşağıdaki alanlar saklanır:
  - `pattern_id`
  - `decision`: accepted | review | rejected
  - `reasoning`: kısa neden açıklaması
  - `supporting_signals`: kararın destekleyen sinyaller listesi
  - `confidence_level`: high | medium | low
  - `trace`: kararın izlenebilir adımları

## Decision trace
- Kararın hangi mevcut sinyalden türetildiği açık olmalıdır.
- Trace, sıralı bir açıklama listesi şeklinde tutulur.
- Trace, upstream çıktılarla (activations, ranking, explainability, delta) bağlantılı olmalıdır.

## Determinism rules
- Aynı input için her zaman aynı karar üretilmelidir.
- Rastgele veya zaman tabanlı bilgi içermemelidir.
- Sıralama ve karar kriterleri sabit olmalıdır.
- Karar çıktısı stabil ve tekrarlanabilir olmalıdır.

## Production safety
- Production output değişmemelidir.
- Shadow-first yaklaşım korunmalıdır.
- SummaryIR / PDF / Teacher / Word kaynakları değişmemelidir.
- `equal_without_shadow == true` korunmalıdır.
- Yeni endpoint, deployment veya production route eklenmemelidir.

## Verification artefacts
- Determinism verification
- Production safety verification
- Gate decision schema compliance report
- Decision trace completeness report

## Benchmark artefacts
- Acceptance gate benchmark summary
- Per-case decision outcomes
- Deterministic decision consistency report

## Acceptance criteria
- Gate module yalnızca karar verir ve shadow-only alanlarda saklanır.
- Aynı input tekrarlandığında kararlar aynı kalır.
- Decision schema gerekli alanları içerir.
- Production safety kontrolleri başarısız olmaz.
- Kitap-spesifik heuristic kullanılmaz.
- Kararlar mevcut sinyallerden trace edilebilir olur.

## Failure criteria
- Production output değişirse.
- `equal_without_shadow` bozulursa.
- Kararlar deterministik olmazsa.
- Decision schema gerekli alanları içermezse.
- Gate kararları mevcut sinyallerden trace edilemezse.
- Kitap-özel heuristic kullanılırsa.
