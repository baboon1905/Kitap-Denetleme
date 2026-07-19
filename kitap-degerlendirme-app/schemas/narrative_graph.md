Narrative Graph — Şema ve İlişki Kuralları

Amaç
-----
Olaylar arasındaki anlamsal ilişkileri (neden, sonuç, sağlar, çözer, duygusal etki vb.) yapısal olarak temsil etmek. `CanonicalEventGraph`'tan beslenir ve `StoryArcPlanner` için zengin bir ilişki ağı sağlar.

Temel İlişki Türleri
--------------------
- `causes` : eventA causes eventB (dolaysız sebep-sonuç)
- `enables` : eventA enables eventB (ön koşul / fırsat yaratır)
- `resolves` : eventA resolves eventB (çözüm niteliği)
- `contrasts` : eventA contrasts eventB (zıtlık veya karşıt tutum)
- `elaborates` : eventA elaborates eventB (detaylandırma)
- `emotional_payoff` : eventA -> emotional outcome for entity

Graph Yapısı
-------------
- `nodes`: event id'leri (CanonicalEvent ids)
- `edges`: liste of {from_event, to_event, relation_type, weight, evidence_refs}
- `clusters`: isteğe bağlı, arc segmentlerini veya sahne kümelerini tutar

Kurallar / Heuristics
---------------------
- `causes` genellikle kısa zaman aralığı ve eylem-nesne beraberliği ile güçlü olur; lexical causality işaretçileri (`because`, `sonuc`, `bu yüzden` vb.) kullanılır.
- `enables` bir olayın başka bir olay için koşul sağladığını gösterir (örn. bir keşif diğer eylemi mümkün kılar).
- `resolves` genellikle `decision`/`outcome` alanları ile ilişkilidir.
- `weight` hesaplanması: evidence sayısı, confidence ürünleri ve page_distance gibi faktörlerin kombinasyonu.

Kontrat
-------
- `NarrativeGraph` serialize edilebilir olmalı ve `StoryArcPlanner`'a doğrudan input verebilmeli.
- Tüm ilişki çıkarım adımları test edilebilir, deterministic ve mümkün olduğunca rule-first, ML-verify yaklaşımında olacak.
