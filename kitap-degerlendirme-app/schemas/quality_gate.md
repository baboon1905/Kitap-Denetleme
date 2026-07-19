Quality Gate — Kontrat ve Doğrulayıcı Kuralları

Amaç
-----
Quality Gate `SummaryIR`, `EntityGraph`, `CanonicalEventGraph` ve `StoryArc` gibi ara yapıları doğrular ve üretime gönderilmeden önce PASS/WARNING/FAIL sonuçları üretir. Gate hiçbir şeyi değiştirmez.

Girdi
-----
- `summary_ir` : JSON-serializable `SummaryIR` örneği (bak: `schemas/summary_ir.md`)

Kontroller (örnek)
------------------
- `forbidden_phrases`: output içinde yasaklı ifadeler var mı? — varsa FAIL
- `summary_length`: minimum kelime sayısını sağlayıp sağlamadığı — yetersizse WARNING
- `confidence`: `summary_ir.confidence` eşiğin altındaysa WARNING
- `event_graph` ve `entity_graph` boş mu? — eğer evrensel olarak boşsa WARNING; kritik eksikliklerde FAIL
- `summary_sections`: her segmentin en az 1 event içermesi; yoksa WARNING
- `quote_ratio`: özet içindeki direkt alıntı oranı çok yüksekse WARNING

Çıktı
-----
- `status`: one of `PASS`, `WARNING`, `FAIL`
- `issues`: list of kısa diagnostic string'ler
- `details`: opsiyonel daha ayrıntılı kontrol verileri

Davranış
-------
- Gate deterministic çalışmalıdır.
- Gate yalnızca doğrulama yapar; gerçek düzeltmeler farklı pipeline adımlarında yapılmalıdır.
