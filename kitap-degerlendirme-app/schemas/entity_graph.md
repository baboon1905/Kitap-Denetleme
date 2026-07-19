EntityGraph — Şema ve Çıkarım Kuralları

Amaç
-----
Metinden çıkarılan varlıkları (kişiler, yerler, nesneler, kuruluşlar, vb.) yapılandırılmış düğümler halinde saklamak; daha sonra olay çıkarımı ve anlatı planlayıcılarına sağlam, kitap-bağımsız sinyaller sağlamak.

EntityNode alanları
-------------------
- `id` : string — benzersiz düğüm kimliği
- `type` : string — sınıf (PERSON, PLACE, OBJECT, ORG, TITLE, ANIMAL, OTHER)
- `aliases` : list[string] — farklı yazım/ünvan/rumuz formları
- `mentions` : list[{paragraph_id, page, span_start, span_end, text}]
- `page_spread` : {min_page, max_page}
- `dialogues` : list[{dialogue_id, speaker_confidence}]
- `actions` : list[{action_verb, evidences: [evidence_refs], confidence}]
- `relations` : list[{target_entity_id, relation_type, evidence_refs}]
- `agency_score` : float — aktif rol alma eğilimi (0..1)
- `decision_score` : float — karar verme eğilimi (0..1)
- `conflict_score` : float — çatışma içinde olma eğilimi (0..1)
- `narrative_weight` : float — anlattaki önemi (0..1)
- `title_match` : float — başlıkla örtüşme skoru (0..1)
- `book_type_bias` : dict — türlere göre bias/score_map
- `confidence` : float — düğümün genel güveni (0..1)

Çıkarım İlkeleri (yüksek seviye)
--------------------------------
- `aliases` otomatik olarak birleştirilir: küçük edit-distance, fold/normalize eşleşmeleri, unvan çıkarımı.
- `mentions` kaynaklardan (SemanticDocument.paragraphs/dialogues) toplanır; her mention için kanıt referansı saklanır.
- `actions` event çıkarımıyla bağlantılıdır: bir varlığın 'action' listesi `CanonicalEventGraph` oluşturulurken kullanılacak.
- `agency_score`, `decision_score`, `conflict_score` gibi skorlama, mention bağlamı ve eylem türlerine göre istatistiksel olarak hesaplanır.
- `title_match` başlık/altbaşlık match'ına dayanır; yüksek match, varlığın merkez karakter olma olasılığını artırır.

Kontrat
-------
- `EntityGraph` JSON-serializable olacaktır.
- `EntityGraph` üretimi yalnızca `SemanticDocument` girdisine dayanmalı; kitap başlığına özel kurallar içermemelidir.

IZLEME
-----
- Gerçek operasyonlarda, `EntityGraph` çıkarıcısı hem rule-based (ner, regex) hem de ML tabanlı sinyalleri birleştirecek hibrit bir yaklaşım kullanmalıdır.
