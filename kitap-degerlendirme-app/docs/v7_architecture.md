V7 Production Architecture — Tasarım ve Başarı Kriterleri

Amaç
-----
Kitap Analiz Sistemi'ni production seviyesine taşımak: book-independent, hard-code-free, regression-safe bir Book Analysis Engine oluşturmak.

Başarı Kriterleri
-----------------
- Benchmark kitap setindeki (Tavşan Pati, Büyülü Yastıklar, Benim Adım Kristof Kolomb, Gökyüzünü Kaybeden Şehir) analizler her commit sonrası çalıştırıldığında kabul edilebilir kalite göstermeli.
- Yeni eklenen, daha önce görülmemiş herhangi bir kitap benzer kaliteyle analiz edilebilmeli.
- Hiçbir yerde kitap-özel (= hard-coded) koşullar bulunmayacak.
- Sistem katmanlı olacak; her katman tek sorumluluk prensibini takip edecek.
- Quality Gate yalnızca doğrulama yapar (PASS/WARNING/FAIL); output değiştirmez.

Temel İlkeler
--------------
1. Hard-code yasaktır. (Kodda kitap başlığına, karakter adına, pdf adı gibi sabit karşılaştırmalar olmayacak.)
2. Kitap bağımsız mimari: kurallar veri modelinden türetilir, kitap isimlerinden değil.
3. Her katmanın tek sorumluluğu vardır. Katmanlar: OCR → SemanticDocument → BookTypeClassifier → NarrativeTypeClassifier → EntityGraph → CanonicalEventGraph → NarrativeGraph → StoryArcPlanner → SummaryIR → SurfaceRealizer → Renderer → QualityGate → ReportBuilder

Benchmark ve Regression
-----------------------
- İlk benchmark seti: Tavşan Pati, Büyülü Yastıklar, Benim Adım Kristof Kolomb, Gökyüzünü Kaybeden Şehir.
- Minimum havuz: 30 kitap (çeşitli türler). Her commit sonrası benchmark otomasyonu çalıştırılmalı.

Quality Gate
------------
Quality Gate'ın rolü: girişteki `SummaryIR`, `EntityGraph`, `EventGraph` gibi yapıları doğrulamak. Gate'in çıktısı üç seviyeden biri olur: PASS, WARNING, FAIL. Gate hiçbir şeyi değiştirmez.

Dokümantasyon ve Sürdürme
-------------------------
- Tüm veri modelleri `schemas/` altında tanımlanacak.
- Her modülün input/output kontratı açıkça yazılacak.
