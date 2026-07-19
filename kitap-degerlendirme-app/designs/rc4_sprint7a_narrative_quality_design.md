# RC4 Sprint 7A: Gerçek Anlatı Kalitesi ve Semantik Karakterizasyon

**Tarih:** 2026-07-08  
**Amaç:** Özet kalitesini Quality Engine puanı yerine gerçek anlatı kalitesi ölçütüne göre yükseltmek.

---

## 1. Temel Ilkeler

### 1.1 Hedef Okuyucu Senaryosu
- **Senaryo:** Kitabı okumayan bir öğretmen, yapılan özet okuyarak kitap hakkında doğru fikir sahibi olmalı.
- **Başarı Kriteri:** Özet okuyarak karakterleri, olayları, mesajı ve temel çatışmayı anlamış olması.

### 1.2 Yasak Optimizasyonlar
- Anahtar kelime doldurma
- Yapay cümle yapıları
- Puân oyununun gerektirdiği tekrar ve redundans
- Skor-odaklı fine-tuning

### 1.3 Zorunlu Prensipler
- Gerçek, tutarlı anlatı akışı
- Olay sırası ve kronoloji korunmalı
- Evidence cümleleri doğal şekilde entegre edilmeli
- Tema bölümü sadece adlardan değil, kitaptaki yeri ve örneklerden bahsetmeli

---

## 2. Özet Yapısı (Yeni)

Özet şu bölümlerden oluşacak:

### 2.1 Setup (Giriş)
```
[Ana karakter ismi] [başlangıç durumu]. 
[Kitabın geçtiği yer/zaman].
[Karakterin hedefi/sorunu].
```

Örnek:
```
Elif, henüz bilmediği bir yolculuğa çıkmaya karar veriyor. Kitap, küçük bir köyde başlıyor. 
Elif'in amacı kayıp olan ağabeysini bulmak.
```

### 2.2 Central Conflict (Ana Çatışma)
```
[Karakterin karşılaştığı ilk sorun].
[Sorunu ortaya çıkaran neden].
[Bu sorunun karakteri nasıl etkilediği].
```

### 2.3 Key Events (Ana Olaylar)
```
Her olay:
- [Olay nedir]
- [Bu olayda hangi karakter rol oynuyor]
- [Karakteri nasıl etkiledi]
- [Sonraki olaya nasıl bağlantılı]

Minimum 3-4 olay. Kronolojik sırada.
```

### 2.4 Major Themes with Context (Temalar ve Bağlamı)
```
Her tema için:
[Tema adı]:
- Kitapta nasıl işlendiği
- Hangi olaylarla gösterildiği
- Hangi karakterlerle ilişkili olduğu

Örnek:
Cesaret:
- Elif'in korkmuş olmasına rağmen yola çıkması
- Dağda karşılaştığı tehlikede cesaret göstermesi
- Ağabeyini kurtarabilmesi için aldığı riskler
```

### 2.5 Resolution (Sonuç)
```
[Çatışma nasıl çözüldü]
[Karakterin başında neler değişti]
[Kitabın sonu]
```

### 2.6 Main Message (Ana Mesaj)
```
Özet bir tümce halinde özetteki ana konu ve öğrenilen ders.
```

---

## 3. Character Resolver Geliştirmesi

### 3.1 Sorun
Mevcut builder karakterleri doğru tanımlamıyor:
- Kitap adını karakter zannetme
- Yer adını karakter adı sanma
- Tarihî kişi adlarını anlamama

### 3.2 Çözüm: Entity Type Detection

```python
class CharacterResolver:
    def resolve_entities(summary_ir, raw_entities):
        """
        summary_ir'dan:
        - central_entities: ana karakterler
        - places: yerler
        - temporal_context: zaman dilimi
        - historical_figures: tarihî kişiler (varsa)
        
        raw_entities'i ayıkla:
        1. Places listesinde var mı? → yer olarak işaretle
        2. Historical figures'da var mı? → tarihî kişi olarak işaretle
        3. Central entities'de var mı? → karakter olarak işaretle
        4. Eğer belirsiz → "karakter adı bilinmiyor" şeklinde genelleştir
        """
```

### 3.3 Kurrallar
- Karakterin adı varsa: `[Karakter adı]`
- Karakterin adı yoksa: `ana karakter`, `genç kahraman`, vb.
- Yer adı: asla karakter adı gibi kullanma
- Kitap adı: metne ekleme

---

## 4. Evidence Integration (Kanıt Entegrasyonu)

### 4.1 Mevcut Sorun
Evidence snippetleri yapay görünüyor, cümlelerin ortasına sokuluyor.

### 4.2 Çözüm: Evidence Synthesis

```python
def synthesize_evidence(snippets, theme_or_event):
    """
    Evidence snippetlerinden:
    1. Teknik kelimeleri çıkar (for example, according to...)
    2. Asıl olayı/detayı ekstrak et
    3. Tema/olaya uygun bir cümle yapısı bul
    4. Natural bir şekilde özetin içine konumlandır
    
    Örnek:
    Input snippet: "She overcomes a storm and discovers her strength."
    Output: "Bir fırtınada karşılaşan Elif, içindeki gücü keşfeder."
    
    Context: Key Events bölümünde kullanılır.
    """
```

---

## 5. Tema Detaylılaştırması

### 5.1 Yapı

```python
def build_theme_section(theme_name, summary_ir, key_events):
    """
    theme_name: "cesaret" vs.
    
    Output:
    "Cesaret, kitabın ana temasıdır. 
    Elif'in köyünü terk edip ağabeyini aramaya karar vermesi cesaret göstergesi.
    Dağda yaşlı kişiyi kurtarması, cesaretin karşılığını gösterir.
    Son bölümde, Elif'in kararını savunması ve onu başında tutması 
    gelişkin bir cesaret portresini tamamlar."
    """
```

### 5.2 Algoritma
1. Theme'ın tanımını bul
2. İlgili key events'i bağla
3. Her eventten bir örnek cümle oluştur
4. Karakterin tema karşısında evrimini göster

---

## 6. Implementation Plan

### Phase 1: Character Resolver (Sprint 7A.1)
- **Dosya:** `runtime_v7/character_resolver.py`
- **Test:** `tests/test_character_resolver.py`
- **Çıktı:** Entity type detection fonksiyonu

### Phase 2: Evidence Synthesizer (Sprint 7A.2)
- **Dosya:** `runtime_v7/evidence_synthesizer.py`
- **Test:** `tests/test_evidence_synthesizer.py`
- **Çıktı:** Evidence entegrasyonu fonksiyonu

### Phase 3: Narrative Restructuring (Sprint 7A.3)
- **Dosya:** Mevcut `narrative_summary_builder.py` güncellemesi
- **Test:** `tests/test_narrative_summary_builder.py` güncellemesi
- **Çıktı:** Yeni, semantik-aware summary yapısı

### Phase 4: Theme Detailer (Sprint 7A.4)
- **Dosya:** `runtime_v7/theme_detailer.py`
- **Test:** `tests/test_theme_detailer.py`
- **Çıktı:** Context-aware tema açıklamaları

### Phase 5: Integration & Verification (Sprint 7A.5)
- **Dosya:** `run_rc4_sprint7a_narrative_quality_check.py`
- **Test:** `tests/test_run_rc4_sprint7a_narrative_quality_check.py`
- **Çıktı:** RC4 Sprint 7A artifact

---

## 7. Kalite Ölçütleri (Non-Engine)

### 7.1 Anlatı Bütünlüğü
- [ ] Olaylar kronolojik sırada
- [ ] Çatışmanın başlangıcı, ortası, sonu açık
- [ ] Karakterin değişimi/gelişimi görülüyor

### 7.2 Detay ve Yeterlilik
- [ ] En az 3-4 ayrı olay belirtilmiş
- [ ] Her tema için en az 1-2 örnek
- [ ] Sonuç karakterin durumunu değiştiriyor

### 7.3 Doğruluk
- [ ] Karakter adları doğru kullanılmış
- [ ] Yerleri karakter adı sanılmamış
- [ ] Olay sırası kitabla eşleşiyor

### 7.4 Okurluk
- [ ] Cümle yapısı doğal
- [ ] Yapay anahtar kelime yığını yok
- [ ] Anlamı açık ve net

---

## 8. Shadow-Only Constraint

- Tüm değişiklikler `runtime_v7/` modullerinde yapılacak
- Production output hiç değişmeyecek
- Pipeline bağlanmayacak
- Test artifact'ları oluşturulacak

---

## 9. Örnek Çıktı (Hedef)

```
Kitap: Dağın Ötesi

Elif, bir küçük köyde yaşayan, kız kardeşi için kaynaklar toplamaya çalışan bir çocuk.
Köy, Anadolu'nun ortasındaki dağlık bir bölge. Elif'in amacı, kayıp olan ağabeyini bulmak.

Ana Çatışma:
Elif, ağabeyinin dağda olduğunu duysa da, hiçkimse onu aramaya gitmek istemiyor. 
Köyde, dağ tehlikeli ve bilinmeyen bir yer olarak görülüyor. 
Elif'in yalnız gitmesi yasak.

Ana Olaylar:
1. Elif, yaşlı Dede'yle tanışıyor. Dede onu yolda rehberlik etmeye razı oluyor.
2. Dağda bir fırtına sırasında, Elif ve Dede mağarada sığınak alıyorlar.
3. Mağarada eski bir harita buluyorlar. Ağabeyinin dağın diğer tarafında olduğu işaret edilmiş.
4. Elif, dağı geçerken korkuya karşı durarak ağabeyine ulaşıyor.

Temalar:
Cesaret: Elif'in köyüne karşı çıkması, ailesi olmayan bir çocuğu yola katması, 
ve fırtınada arkadaşını terk etmemesi cesaretin göstergesi.

Dayanışma: Dede ile Elif arasındaki bağ, iki yabancının birbirini nasıl kurtardığını gösterir.

Sonuç:
Elif ağabeyini bulmuş ama o kalmak istemiyor. Elif ağabeyine köye dönmeyi teklif ediyor. 
Ağabeyi reddediyor ancak Elif'in büyüdüğünü görerek gurur duyuyor. 
Elif ve Dede köye geri dönüyorlar.

Ana Mesaj:
Bir çocuğun cesaret ve dayanışmayla ailesi için yaptığı fedakarlık, 
hatta başarı sağlamamış olsa bile insanı nasıl olgunlaştırır.
```

---

## 10. Başarı Kriteri

Sprint 7A başarılı sayılacak:
- [ ] Character Resolver test'leri geçiyor (Phase 1)
- [ ] Evidence Synthesizer test'leri geçiyor (Phase 2)
- [ ] Narrative Builder yeni yapıyla test'leri geçiyor (Phase 3)
- [ ] Theme Detailer test'leri geçiyor (Phase 4)
- [ ] Örnek özet insan tarafından okunabilir ve doğru (Phase 5)
- [ ] Production output değişmemiş
- [ ] Tüm testler geçiyor

---

**Not:** Quality Engine puanı başarı kriteri DEĞİLDİR. Amacımız gerçek okuyucu memnuniyeti ve doğruluktur.
