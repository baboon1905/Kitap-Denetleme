RC2 Sprint 5 — Pattern Activation: Revize Edilmiş Tasarım

Amaç
- "Shadow-first" mimarisini koruyarak `pattern activation` listesinin RC2 canonical shadow semantic output'unun bir parçası haline getirilmesi. Runner sadece bu listeyi okuyacak; inference, substring arama veya ikinci semantic engine çalıştırılmayacak.

1) Pattern activation alanının yeri
- Kesin karar: `_runtime_v7_shadow['semantic']['pattern_activations']` — bu RC2 canonical semantic output alanı olacaktır.
  - Gerekçe: semantic verilerle aynı bağlamda bulunması analiz izlenebilirliğini ve tüketici (runner) için net erişimi sağlar. Shadow kökünü kirletmez; yalnızca gözetim/monitoring için ek veri içerir.

2) Her kayıt için önerilen minimum alanlar (zorunlu)
- `pattern_id` (string) — pattern tanımlayıcısı
- `category` (string) — pattern sınıflaması/kategorisi (ör. "engagement","comprehension")
- `status` (string) — activation durumu; örnek değerler: `active` | `candidate` | `rejected`
- `raw_confidence` (float 0.0-1.0) — detector/monitor tarafından üretilen ham skor
- `calibrated_confidence` (float 0.0-1.0) — opsiyonel; Confidence Engine tarafından kalibre edilmiş skor
- `evidence_count` (int) — aynı pattern için bulunan bağımsız kanıt sayısı
- `source` (string) — hangi alan/nesneden elde edildiği (ör. `summary_ir`, `theme_clusters[2]`, `narrative.paragraph.4`, `raw_text:page:3`)
- `algorithm_version` (string) — kullanılmış pattern/cihaz/engine versiyonu

3) Opsiyonel alanlar
- `match_snippet` (string) — kısa, kırpılmış örnek metin (PII riski varsa maskelenebilir)
- `matched_spans` (array of {page:int,start:int,end:int}) — gerekliyse konum verisi

4) Monitoring metadata (özet)
- `_runtime_v7_shadow['semantic']['monitoring']` yalnızca özet metrikleri taşıyacak:
  - `last_run_iso`: ISO-8601 timestamp
  - `status`: "ok" | "partial" | "error"
  - `errors`: opsiyonel kısa liste (kısa kod veya açıklama)
  - `pattern_library_version`: string
  - `confidence_engine_version`: string
- Rasyonel: pattern-bazlı bilgiler `pattern_activations` içinde kalmalı; `monitoring` sadece koşu sağlığı ve sürüm bilgilerini sağlar.

5) Confidence taşıma ve format
- Taşınacak: hem `raw_confidence` hem opsiyonel `calibrated_confidence`.
- Format: float 0..1; deterministiklik için iki ondalık basamakta yuvarlama önerilir (ör. 0.65).
- `algorithm_version` ile hangi parametre/sürümün kullanıldığı kaydedilecek.

6) Production output neden etkilenmeyecek?
- Shadow-only prensibi uygulanır: `pattern_activations` yalnızca `_runtime_v7_shadow` içinde yer alır ve üretim veri yollarındaki temel analiz/özet alanları değiştirilmez.
- `V7_SHADOW_MODE` devre dışıysa alan üretilmez. Bu nedenle üretim çıktıları (ör. PDF bytes, API response body minus shadow) aynı kalır.

7) `equal_without_shadow` korunması
- Mantık: üretim çıktıları, shadow eklenmiş/eklenmemiş aynı olmalıdır. Dolayısıyla runner karşılaştırması shadow dışarı alındıktan sonra yapılır.
- Uygulama: shadow-only alanlardan kaynaklı farklar ignore edilir; adapter üretim alanlarını değiştirmemelidir.

8) Determinism korunması için kurallar
- `pattern_activations` liste sıralaması sabit olmalı (örn. önce `pattern_id` ile alfabetik, sonra `source`).
- Confidence değerleri sabit hassasiyete yuvarlanmalı (örn. 2 ondalık) ve floating-point farklılıkları minimize edilmeli.
- Confidence Engine ve monitor deterministik çalışmalı; rastgelelik varsa sabit seed uygulanmalı.
- Timestamps/çalışma meta verileri karşılaştırma dışında tutulmalı veya normalize edilmelidir.

Ek Notlar
- Boyut: `match_snippet` mümkünse kısa tutulmalı; matched_spans yalnız gerektiğinde eklenmeli.
- Gizlilik: match_snippet içinde PII varsa maskelenmeli veya opsiyonel tutulmalı.
- Versiyonlama: `pattern_library_version` ve `confidence_engine_version` zorunlu metadata olarak tutulmalı.
- Geriye dönük uyumluluk: eski shadow'larda alan yoksa runner boş liste veya `activated_patterns: 0` ile çalışmalı.

Sonraki adım (isteğe bağlı, henüz yapılmayacak)
- Kullanıcının onayı ile adapter tarafında `pattern_activations` üretimi için patch hazırlanacak; patch hazırlanması, test veya commit işlemleri kullanıcı izni gerektirir.


