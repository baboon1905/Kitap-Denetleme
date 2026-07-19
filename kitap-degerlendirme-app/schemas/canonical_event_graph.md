Canonical Event Graph — Şema ve Çıkarım Kuralları

Amaç
-----
Metinden çıkarılan olayları (`events`) tek tip, canonical bir biçimde temsil etmek. Bu yapı `NarrativeGraph` ve `StoryArcPlanner` için birincil giriş olacaktır.

Event alanları (zorunlu/opsiyonel)
--------------------------------
- `id` (string) — benzersiz olay kimliği
- `actor` (string) — olayın başlıca öznesi (entity id referansı veya canonical name)
- `action` (string) — fiil/eylem (lemma/folded form)
- `object` (string|null) — eğer varsa nesne
- `goal` (string|null) — olayın amacı/niyeti
- `conflict` (string|null) — engel/çatışma öğesi
- `decision` (string|null) — karar bilgisi varsa
- `outcome` (string|null) — sonuç/sonrasal durumu özetleyen ifade
- `evidence` (list[{page, paragraph_id, span_start, span_end, text}]) — kanıt referansları
- `page` (int|null)
- `importance` (float 0..1) — göreli önem skoru
- `story_position` (string|null) — başlangıç/orta/dönüm/çözüm vb. (heuristic)
- `confidence` (float 0..1)

Çıkarım İlkeleri (yüksek seviyede)
---------------------------------
- `action`, `object`, `goal` alanları önce kural tabanlı (dependency parsing + verb lemma) yöntemle çıkarılır; belirsizlik durumunda ML tabanlı etiketleyiciye devredilir.
- `actor` eşleştirmesi `EntityGraph` içindeki düğümlerle yapılır; en yakın mention ile bağlanır.
- `importance` istatistiksel: mention sayısı, page_spread, title_match gibi faktörlerin ağırlıklı kombinasyonu.
- `story_position` heuristics: kitap boyunca olayın konumu (normalized page / total_pages) ve kelime/anahtar kelime sinyalleriyle belirlenir.

Kontrat
-------
- `CanonicalEventGraph` JSON-serializable olmalı.
- Çıkarım pipeline'ı `SemanticDocument` + `EntityGraph` kullanarak deterministic, test edilebilir adımlar içerecek.

Örnek kullanım
--------------
1. `SemanticDocument` analiz edilir ve olası eylem cümleleri tespit edilir.
2. Her eylem cümlesi için candidate `event` oluşturulur.
3. `EntityGraph`'dan `actor`/`object` referansları eşlenir.
4. `importance` ve `confidence` hesaplanır.
5. `CanonicalEventGraph` üretimi tamamlanır ve `NarrativeGraph`'a verilir.
