Surface Realizer — Kontrat ve Kurallar

Amaç
-----
`Surface Realizer` `SummaryIR` alır ve doğal Türkçe metin üretir. Realizer çıktısı son kullanıcıya gösterilecek özet içeriğidir.

Kurallar
-------
- Asla `evidence` içindeki cümleleri kopyalamayacak; sadece paraphrase edecektir.
- Asla placeholder veya pipeline ifadeleri üretmeyecektir.
- Forbidden phrases listesi uygulanacaktır.
- Output UTF-8 NFC-normalized Türkçe string olmalıdır.

Kontrat
-------
- Input: `SummaryIR` (see `schemas/summary_ir.md`)
- Output: {"text": string, "sections": [{id, title, text}], "confidence": float, "diagnostics": [string]}
