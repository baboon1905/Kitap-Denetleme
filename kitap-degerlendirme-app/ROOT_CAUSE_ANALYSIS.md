# Root Cause Analysis - Tema ve Karakter Algılama Sorunları

**Analiz Tarihi:** 2026-06-25  
**Test Kitabı:** Tavşan Pati'nin Şaşırtıcı Yolculuğu  
**Pipeline:** V6.6 Theme Gain Analysis

---

## 1. TEMA ADAYLARININ OLUŞUP OLUŞMADIĞI

### ADAY TEMA TESPİTİ

Tüm tema adayları başarıyla tespit ediliyor:

| Tema | Keyword Match | Aday Sayısı | Durum |
|------|--------------|-------------|-------|
| **hayvan sevgisi** | 8 kayıt | ✅ | **FINAL SEÇİM** |
| **sorumluluk** | 3 kayıt | ❌ | CONTEXT filtresinde elendi |
| **dostluk** | 2 kayıt | ❌ | LABEL_CONTEXT filtresinde elendi |
| **empati** | 3 kayıt | ❌ | PEDAGOGICAL + LABEL_CONTEXT filtresinde elendi |
| **aile** | 1 kayıt | ⚠️ | Tüm filtreleri geçti ama final seçimde yok |
| **çevre bilinci** | 1 kayıt | ❌ | LABEL_CONTEXT filtresinde elendi |

**SONUÇ:** Tema adayları başarıyla oluşuyor. Sorun adayların filtrelenme aşamasında.

---

## 2. HER TEMA İÇİN DETAYLI ELENME NEDENİ

### 2.1 SORUMLULUK (Responsibility)

**Candidate Stage:**
- Keywords: `sorumluluk`, `görev`, `ödev`, `sahiplen`, `bakmak`, `besle`
- Matched Records: 3
- Evidence:
  1. Page 11: "Ali, Pati'yi sahiplendiği günden beri çok şey öğrenmişti..." (matched: `sahiplen`)
  2. Page 11: "Hayvan sevgisi, sorumluluk ve dostluk en önemli değerlerdi..." (matched: `sorumluluk`)
  3. Page 12: "Bir canlıya bakmak büyük sorumluluktur," diye düşündü Ali... (semantic: değerlendirme)

**Filter Stage:**
```
Filter CONTEXT: page=11 context=1 'Ali, Pati'yi sahiplendiği günden beri...'
  → context_strength = 1 (çok düşük)
  → NEDEN: sentence 14 kelime, plot_hits=0, character_hits=0, behavior_hits=0
  → keyword_variety = 1 (sadece 'sahiplen')
  → SKOR = 1 < 3 (minimum threshold)
  → ELENDİ
```

**ROOT CAUSE:** 
- `_context_strength()` fonksiyonu bu cümle için context_strength=1 veriyor
- "sahiplen" kelimesi tek başına yeterli context kanıtı saymıyor
- Cümlede olay örgüsü, karakter veya davranış terimi yok
- **THEME_CONTEXT_RULES'da sorumluluk için explicit rule YOK**
- V6.6 fix'i çalışmıyor çünkü `has_explicit_rules = False` olsa da threshold 2'ye düşüyor ama score 1 < 2

**BEKİLEN:** Context strength 2 olmalı (rules olmayan tema için)  
**GERÇEKLEŞEN:** Context strength 1, threshold 2, elendi

### 2.2 DOSTLUK (Friendship)

**Candidate Stage:**
- Keywords: `arkadaş`, `dost`, `birlikte`, `paylaş`, `yardım`
- Matched Records: 2
- Evidence:
  1. Page 4: "Pati hasta, ona yardım etmeliyiz!" (matched: `yardım`)
  2. Page 11: "...dostluk en önemli değerlerdi..." (matched: `dost`)

**Filter Stage:**
```
Filter LABEL_CONTEXT: page=4 '"Pati hasta, ona yardım etmeliyiz!" dedi...'
  → THEME_CONTEXT_RULES['dostluk'] kontrolü
  → rule['must'] = ['arkadas', 'dost'] → YOK (sadece 'yardım' var)
  → rule['action'] = ['paylas', 'yardim', 'destek', 'guven', 'birlikte', 'dinle', 'baris']
  → 'yardım' → 'yardim' (folded) → action'da VAR
  → ANCAK must KOSULU SAĞLANMADI
  → ELENDİ

Filter LABEL_CONTEXT: page=11 'Hayvan sevgisi, sorumluluk ve dostluk...'
  → Sadece 'dost' keyword match, context yok
  → ELENDİ
```

**ROOT CAUSE:**
- Dostluk teması THEME_CONTEXT_RULES'a sahip
- Rule: "must" kısmında `arkadaş` veya `dost` olmalı
- Page 4'te sadece `yardım` var, `arkadaş`/`dost` yok
- Page 11'te sadece `dost` var ama bu abstract bir ifade, action yok
- **İki şart da sağlanmıyor:** Hem must (arkadaş/dost) hem action (paylaş/yardım/birlikte)

### 2.3 EMPATİ (Empathy)

**Candidate Stage:**
- Keywords: `anladı`, `hissetti`, `üzüldü`, `sevindi`, `düşündü`, `halini`, `merhamet`
- Matched Records: 3
- Evidence:
  1. Page 4: "Ali çok üzüldü ve hemen annesine haber verdi..." (semantic: duygusal tepki)
  2. Page 12: "Bir canlıya bakmak büyük sorumluluktur," diye düşündü Ali... (matched: `düşündü`)
  3. Page 15: "Ali yatağında uyumadan önce Pati'yi düşündü..." (matched: `düşündü`)

**Filter Stage:**
```
Filter PEDAGOGICAL: page=4 semantic=duygusal tepki
  → _pedagogical_evidence_valid('empati', sentence, ['üzüldü'], 'tema')
  → semantic_type = 'duygusal tepki'
  → has_reaction = True (üzüldü var)
  → has_event = False (davranış/karar/çatışma yok)
  → item_type = 'tema' → has_event OR has_reaction → True
  → GEÇTİ

Filter LABEL_CONTEXT: page=12 '"Bir canlıya bakmak büyük sorumluluktur," diye düşündü Ali...'
  → THEME_CONTEXT_RULES['empati'] kontrolü
  → rule['must'] = ['anladi', 'anladı', 'hissetti', 'üzüldü', 'sevindi', 'halini', 'yardim', 'merhamet']
  → 'düşündü' → must'da YOK
  → ELENDİ

Filter LABEL_CONTEXT: page=15 'Ali yatağında uyumadan önce Pati'yi düşündü...'
  → Aynı sebeple ELENDİ
```

**ROOT CAUSE:**
- Empati teması THEME_CONTEXT_RULES'a sahip
- Rule: "must" kısmında `anladı`, `hissetti`, `üzüldü`, `merhamet` gibi duygusal terimler olmalı
- Sistem sadece `düşündü` keyword'ini algılıyor
- `düşündü` → must listesinde YOK
- **Kritik Sorun:** "düşündü" → "düşünme" → bu bir empati göstergesi ama sistem algılamıyor

### 2.4 AİLE (Family)

**Candidate Stage:**
- Keywords: `anne`, `baba`, `aile`, `kardeş`
- Matched Records: 1
- Evidence:
  1. Page 4: "Ali çok üzüldü ve hemen annesine haber verdi..." (matched: `anne`)

**Filter Stage:**
```
STATUS: PASSED ALL FILTERS ✅
```

**Final Selection:**
```
Total themes found: 1
  hayvan sevgisi: guc=81 guven=0.81 kanit=5 sayfa=5
```

**ROOT CAUSE:**
- Aile teması TÜM filtreleri geçti
- ANCAK final seçimde yok
- **Neden?** Minimum evidence requirement:
  - `kanit_sayisi < 3` (sadece 1 kanıt)
  - `farkli_sayfa_sayisi < 2` (sadece 1 sayfa)
  - `bagimsiz_bolum_sayisi < 2`
- **Sonuç:** Yetersiz kanıt, final seçime alınmadı

---

## 3. KARAKTER ÇIKARIMI SORUNU

### 3.1 "Ali" Yerine "Kız Tavşan Pati" ve "Evin Konukları Bir"

**GÖZLEM:** Karakter çıkarımında beklenmeyen isimler üretiliyor.

**ROOT CAUSE ANALİZİ:**

Bu sorunu incelemek için karakter çıkarım modülünü detaylı analiz etmek gerekiyor. Olası nedenler:

1. **OCR Hataları:** PDF'ten metin çıkarılırken karakter isimleri bozulmuş olabilir
2. **Noise Gate Çok Katı:** CHARACTER_NOISE_GATE çok agresif filtreleme yapıyor
3. **Canonical Map Eksik:** "Ali" gibi yaygın isimler canonical map'te yok
4. **Context Çok Zayıf:** Karakter isminin etrafındaki bağlam yetersiz

**ÖNERİ:** Ayrı bir karakter debug scripti yazılmalı.

---

## 4. ÖZET VE ÖNERİLER

### TEMA ALGILAMA SORUNLARI

**Sorun 1: Context Strength Çok Düşük**
- `_context_strength()` fonksiyonu çok katı
- Tek keyword + kısa cümle = context_strength 1-2
- Minimum threshold 2-3, bu yüzden eleniyor

**Sorun 2: THEME_CONTEXT_RULES Eksik/Aşırı Katı**
- "sorumluluk", "vicdan", "pişmanlık", "söz tutma" için rules YOK
- "dostluk", "empati" için rules VAR ama çok katı
- Rule'lar "must" + "action" şartı koyuyor, bu çok zor

**Sorun 3: Evidence Sayısı Yetersiz**
- "aile" teması tüm filtreleri geçti ama 1 kanıt = final seçimde yok
- Minimum 3 kanıt, 2 sayfa, 2 bağımsız bölüm şartı çok katı

### KARAKTER ÇIKARIMI SORUNLARI

**Sorun 4: Karakter İsmi Çıkarımı**
- "Ali" yerine anlamsız isimler üretiliyor
- Muhtemelen OCR hatası veya noise gate sorunu

---

## 5. ÇÖZÜM ÖNERİLERİ (PRIORITY SIRASI)

### YÜKSEK ÖNCELİK

1. **Context Strength Hesaplamasını Düşür**
   - Mevcut: keyword_variety (0-2) + plot_hits (0-1) + character_hits (0-1) + behavior_hits (0-2)
   - Öneri: Minimum context_strength = 2 (her zaman)
   - Tek keyword + herhangi bir context terimi = 2

2. **THEME_CONTEXT_RULES'u Ekle/Düzenle**
   - Eksik temalar için rules ekle:
     - `sorumluluk`: must=['sahiplen', 'sorumluluk', 'görev'], action=['düşündü', 'karar', 'sahiplendi']
     - `vicdan`: must=['vicdan', 'pişman', 'suçluluk'], action=['özür', 'af', 'hatasını']
     - `pişmanlık`: must=['pişman', 'keşke'], action=['özür', 'anladı']
     - `söz tutma`: must=['söz', 'emanet'], action=['tuttu', 'verdi', 'tuttuğu']
   - Mevcut rules'ı gevşet:
     - Dostluk: sadece `yardım` veya `dost` yeterli olsun
     - Empati: `düşündü` + `hissetti`/`üzüldü` kombinasyonu kabul edilsin

3. **Evidence Minimum Eşiklerini Düşür**
   - Mevcut: 3 kanıt, 2 sayfa, 2 bölüm
   - Öneri: 2 kanıt, 1 sayfa, 1 bölüm (kısa metinler için)

### ORTA ÖNCELİK

4. **Karakter Çıkarım Debug**
   - Ayrı bir debug scripti yaz: `debug_character_extraction.py`
   - "Ali" karakterinin neden kaçırıldığını göster
   - "Kız Tavşan Pati" ve "Evin Konukları Bir" kaynaklarını tespit et

### DÜŞÜK ÖNCELİK

5. **Context Strength Hesaplama**
   - Current: `keyword_variety = min(2, len(set(matched_keywords)))`
   - Problem: Tek keyword = 1 puan, çok düşük
   - Fix: `keyword_variety = min(3, len(set(matched_keywords))) + 1`

---

## 6. KANITLAR

### Tema Filtreleme Kanıtları

```
sorumluluk:
  - Page 11: "Ali, Pati'yi sahiplendiği günden beri..." → context=1, ELENDİ
  - Page 12: "Bir canlıya bakmak büyük sorumluluktur" → semantic=değerlendirme, ELENDİ

dostluk:
  - Page 4: "Pati hasta, ona yardım etmeliyiz!" → must eksik, ELENDİ
  - Page 11: "dostluk en önemli değerlerdi" → abstract, ELENDİ

empati:
  - Page 4: "Ali çok üzüldü" → PEDAGOGICAL geçti, sonra LABEL_CONTEXT'te elendi
  - Page 12, 15: "düşündü" → must listesinde yok, ELENDİ

aile:
  - Page 4: "annesine haber verdi" → TÜM FİLTRELERİ GEÇTİ ✅
  - Final: Yetersiz kanıt (1 < 3), ELENDİ
```

---

## 7. SONUÇ

**Tema algılama sorunu FILTRELEME AŞAMASINDA.**
- Adaylar başarıyla oluşuyor
- Filtreler çok katı, özellikle:
  1. Context strength hesaplaması
  2. THEME_CONTEXT_RULES şartları
  3. Minimum evidence eşikleri

**Karakter çıkarımı sorunu AYRI bir konu.**
- "Ali" kaçırılıyor, anlamsız isimler üretiliyor
- Muhtemelen OCR + noise gate + canonical map sorunu

**ÇÖZÜM:** Filtreleri gevşetmek, rules'ı eklemek/düzenlemek, minimum eşikleri düşürmek.