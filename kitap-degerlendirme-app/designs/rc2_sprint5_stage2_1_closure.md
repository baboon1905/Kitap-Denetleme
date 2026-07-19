**Stage 2.1 — Semantic Monitor Closure**

Kısa teknik özet ve kapanış notları.

**1. Confidence ownership**
- Confidence hesaplamasının tek sahibi `Confidence Engine` olarak netleştirildi. Semantic Monitor artık yeni confidence üretmez veya pattern-level ağırlıkla yeniden kalibrasyon yapmaz. Monitor, upstream tarafından sağlanan `raw_confidence` ve `calibrated_confidence` değerlerini tüketir ve aggregate eder.

**2. Semantic Monitor sorumluluğu**
- Grouping: `matches` öğelerini `pattern_id` bazında gruplar.
- Aggregation: Upstream tarafından sağlanan confidence değerlerinin (varsa) ortalamasını alır; yeni confidence üretmez.
- Monitoring: pattern başına metrikler (match_count, activation_rate, fp_risk, vs.) ve kalite kapıları üretir.
- Canonical serialization: deterministik, canonical `pattern_activations` listesi ve `pattern_monitoring` özetini üretir.

**3. Adapter sorumluluğu**
- Adapter, upstream payload içindeki `pattern_activations` (eğer varsa) alanını normalize eder ve `_runtime_v7_shadow['semantic']['pattern_activations']` içinde taşır.
- Adapter inference yapmaz, confidence üretmez veya pattern tanımı değiştirmez.

**4. Runner sorumluluğu**
- Runner şu anda değiştirilmedi; mevcut davranış korunur.
- Gelecekte runner, canonical `pattern_activations` listesini doğrudan okuyacak şekilde güncellenecektir (Stage 3 planı).

**5. Canonical `pattern_activations` yaşam döngüsü**
- Üretim hattı: Confidence Engine -> Match üreticileri -> Semantic Monitor (generate_canonical_activations) -> (opsiyonel) Adapter taşıma -> Shadow (`_runtime_v7_shadow`).
- Semantic Monitor: tüketir (matches), aggregate eder, canonical listeyi yazar.
- Adapter: canonical listeyi shadow'a kopyalar (normalize eder).
- Runner (ileride): shadow içindeki canonical listeyi kullanarak substring-arama çakışmalarını kaldıracak.

**6. Production isolation nasıl korunuyor?**
- Adapter ve Runner için hiçbir davranış değişikliği uygulanmadı; Monitor yalnızca ayrı monitoring artifactleri ve shadow-ötesi canonical veriler üretir.
- `verification.production_output_changed` ve `equal_without_shadow` flagleri korunacak; monitor tarafı ayrı artifact dosyalarına yazılır.

**7. `equal_without_shadow` neden korunuyor?**
- Amaç: production endpoint çıktılarının (shadow hariç) değişmemesini garanti etmek. Shadow-first yaklaşımına sadakat için monitor ve adapter değişiklikleri non-intrusive olmalıdır. Bu nedenle adapter yalnızca canonical veriyi taşır; üretim çıktısı aynı kalır.

**8. Determinism nasıl korunuyor?**
- `pattern_activations` listesi deterministik sıralanır (ör. `(pattern_id, source)` anahtarına göre). Confidenceler yuvarlanır ve aggregate hesaplama deterministik metriklerle sınırlıdır. Bu, iki tekrar çalıştırmada aynı canonical shadow elde edilmesini destekler.

---

**Stage 2.2 — Entegrasyon Planı (yüksek seviye)**

Amaç: Semantic Monitor tarafından üretilen canonical `pattern_activations` listesini production runtime pipeline'a güvenli, aşamalı ve izlenebilir şekilde bağlamak. Runner değişikliği Stage 3'e saklanacak.

Adımlar:
1. Opt-in veri üretimi (monitor side): Runtime analiz akışında monitor çağrısı eklensin ancak sonuçlar sadece monitoring artifactlerine yazılsın (henüz payload'a inject edilmesin). İzleme ve kalite kapıları toplanır.
2. Shadow taşıma denetimi: Adapter mevcut normalize/taşıma kodu ile upstream'den gelen `pattern_activations` alanını shadow'a kopyalıyor mu doğrula; test kitaplıkları ile birkaç örnek çalıştır.
3. Staging runtime (okuma-only): Bir staging endpoint veya test runner oluşturup monitor çıktılarının pipeline içinde doğru yere yazıldığını doğrula; production davranışı bozulmasın.
4. Canary wiring (sınırlı scope): gerçek pipeline içinde küçük bir canary (ör. %1 kitap) için `payload['pattern_activations']` monitor çıktısı ile doldurulur, adapter normalize eder; verification/benchmark takip edilir.
5. Observability + Quality Gates: `pattern_monitoring` özetleri, `quality_gates` ve benchmark sonuçları merkezi dashboard/artefakt depolamaya gönderilsin.
6. Rollback planı: Canary metriklerinde anomali gözlenirse pipeline hızlıca eski davranışa dönebilmelidir (adapter yalnızca upstream taşıma yapmaya devam eder).

Acceptance criteria (Stage 2.2 tamamlanması için):
- Monitor canonical listesini üretir ve artifact olarak saklar.
- Adapter canonical listeyi normalize edip shadow'a taşıyabilir.
- Production output (shadow hariç) değişmez; `equal_without_shadow` doğrulanır.
- Determinism doğrulanır (iki ardışık run aynı shadow üretir).
- Quality gates ve monitoring artifactleri otomatik olarak oluşturulur.

Riskler & hafifletmeler:
- Risk: Upstream match üreticileri confidenceleri tutarlı sağlamayabilir — mitigasyon: Stage 2.2'de schema ve required-field validasyonları ekle (monitor hata listesine düşsün).
- Risk: Canary'de beklenmeyen artefakt büyüklüğü — mitigasyon: canary küçük hacimle başlat.

Notlar:
- Bu belge implementasyon değişikliği içermez; sadece Stage 2.1 kapanışı ve Stage 2.2 entegrasyon planını özetler.
