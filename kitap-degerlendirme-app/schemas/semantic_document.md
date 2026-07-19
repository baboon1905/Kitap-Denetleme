SemanticDocument — Şema Taslağı

Amaç
-----
OCR çıktısından doğrudan özet üretmek yerine metnin yapısal ve anlamsal temsili `SemanticDocument` içinde saklanır. Katmanlar bu yapıyı okur ve üzerine kendi çıkarımlarını ekler.

Yapı (özet)
------------
- `metadata`: {title, author, language, source_file, pages}
- `paragraphs`: liste of {id, page, text, start_offset, end_offset, tokens}
- `sections`: liste of {id, title, paragraphs: [paragraph_ids], level}
- `dialogues`: liste of {id, speaker_candidate, spans: [paragraph_ids or offsets], text}
- `scene_boundaries`: liste of {id, start_paragraph, end_paragraph, confidence}
- `time_markers`: liste of {id, text, normalized_time, page, confidence}
- `locations`: liste of {id, mention_texts, normalized_name, page_spread, confidence}
- `characters`: liste of {id, canonical_name, aliases, mentions: [paragraph_ids], roles, entity_id}
- `relations`: liste of {id, source_char_id, target_char_id, relation_type, evidence}
- `chapter_transitions`: liste of {id, from_chapter, to_chapter, page, evidence}

Ek Bilgiler
-----------
- Her öğe `confidence` alanı taşımalı.
- `tokens` alanı tokenize ve fold edilmiş token listesinin yanı sıra byte offsets içermelidir.
- `page_spread` sayfa aralığı / sayfa numarası veya 'spreads' olarak tutulmalı.

Kontrat
-------
- Bu şema `EntityGraph` ve `CanonicalEventGraph` girişidir.
- Şema JSON/JSON Schema + bir Python `dataclass`/Pydantic model seti ile temsil edilecek.
