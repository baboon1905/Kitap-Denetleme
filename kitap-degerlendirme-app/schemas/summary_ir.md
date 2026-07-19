SummaryIR — Şema ve Kontrat

Amaç
-----
`SummaryIR` (Intermediate Representation) Surface Realizer'a verilen tek kaynak olacak. Renderer hiçbir karar vermeyecek; tüm anlatı yapılandırması SummaryIR içinde tamamlanmış olmalı.

Alanlar
------
- `book_type` : string
- `narrative_type` : string
- `entity_graph` : dict (EntityGraph JSON)
- `event_graph` : dict (CanonicalEventGraph JSON)
- `story_arc` : dict (StoryArc plan output)
- `summary_sections` : list of {id, title, events: [event_ids], blurb}
- `themes` : list of {theme, weight}
- `evidence` : list of evidence refs (for diagnostics only; Realizer must NOT copy verbatim)
- `confidence` : float
- `diagnostics` : list[string]

Kontrat
-------
- `Surface Realizer` input olarak tam bir `SummaryIR` alır ve döndürülen `text` alanı doğal Türkçe, NFC-normalized, UTF-8 string olmalıdır.
- Realizer hiçbir `evidence` öğesini olduğu gibi kopyalamayacak; sadece özetleyici/paraphrase ifadeler kullanacaktır.
- Realizer `forbidden_phrases` listesinde yer alan ifadeleri üretmemelidir.

Forbidden phrases (örnek)
- bu adım anlatıdaki dengeleri değiştirir
- karakterlerin seçimleriyle başlayan gerilim
- daha dengeli bir kapanış
- olayları tek tek sıralamak yerine
- başlangıçtan kapanışa uzanan çizgi
- açısından yeni bir sonuç doğar
- durumun nedenini sorgular
- kararlı biçimde ilerler
- çevresindekilerle çözüm arar
- öğrendiği bilgiyi paylaşır
- meselenin iç yüzünü sezer
