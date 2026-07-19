Story Arc Planner — Şema ve Tür-Tabanlı Planlayıcı

Amaç
-----
`CanonicalEventGraph` ve `NarrativeGraph`'tan alınan sinyallerle, kitap türüne göre bir `story_arc` (başlangıç, çatışma, gelişme, dönüm, çözüm vb.) oluşturmak.

Çıktı (SummaryIR içinde kullanılacak)
---------------------------------
- `story_arc`: liste of {segment_id, label, events: [event_ids], summary_blurb, confidence}
- `book_type` ve `narrative_type` referansları
- `diagnostics`: neden bu olayların seçildiğine dair kısa açıklamalar

Tür Temelli Şablonlar (örnek)
-----------------------------
- `öykü` (fiction): ["başlangıç", "çatışma", "gelişme", "dönüm", "çözüm"]
- `biyografi`: ["erken dönem", "hedef", "engeller", "başarılar", "etki"]
- `masal`: ["eksiklik", "yardımcı", "denemeler", "dönüşüm", "ders"]
- `bilim`: ["konu", "açıklama", "örnek", "sonuç"]

Kurallar
-------
- Öncelik: yüksek `importance` ve `confidence` taşıyan canonical event'ler arc içindeki merkezi roller için seçilir.
- Zaman/konum heuristics: arc segmentleri için olayların page_spread ve normalized position kullanılır.
- Her segment için `summary_blurb` otomatik oluşturulur (kısa, 15-30 kelime) ve `SummaryIR` tarafından rafine edilir.

Test Edilebilirlik
------------------
- Planner deterministic kurgulanmalı; aynı girdiler aynı `story_arc` üretimini vermeli.
- Basit alt-örnekler için unit test'ler yazılmalı (ör. 5 olaylı input için her segmentte en az 1 event).
