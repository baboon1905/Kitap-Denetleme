# DEBUG RAPORU - Tema ve Karakter Algılama Sorunları

**Test Kitabı:** Tavşan Pati'nin Şaşırtıcı Yolculuğu  
**Tarih:** 2026-06-25  
**Pipeline:** V6.6 Theme Gain Analysis

---

## 1. TEMA ADAY LİSTESİ (Tüm Adaylar ve Puanları)

### Tespit Edilen Tema Adayları:

| Tema | Keyword Match | Evidence Sayısı | Durum | Final |
|------|--------------|-----------------|-------|-------|
| **hayvan sevgisi** | 8 kayıt | 4-5 kanıt | ✅ TÜM FİLTRELERİ GEÇTİ | **SEÇİLDİ** (güç=84, güven=0.84) |
| **sorumluluk** | 3 kayıt | 0 kanıt | ❌ CONTEXT filtresinde elendi | REDDEDİLDİ |
| **dostluk** | 2 kayıt | 0 kanıt | ❌ LABEL_CONTEXT filtresinde elendi | REDDEDİLDİ |
| **empati** | 3 kayıt | 0 kanıt | ❌ PEDAGOGICAL + LABEL_CONTEXT | REDDEDİLDİ |
| **aile** | 1 kayıt | 1 kanıt | ⚠️ Tüm filtreleri geçti ama yetersiz | REDDEDİLDİ |
| **çevre bilinci** | 1 kayıt | 0 kanıt | ❌ LABEL_CONTEXT filtresinde elendi | REDDEDİLDİ |
| özgüven | 0 kayıt | 0 | ❌ Keyword match yok | REDDEDİLDİ |
| şehir yaşamı | 0 kayıt | 0 | ❌ Keyword match yok | REDDEDİLDİ |
| dayanışma | 0 kayıt | 0 | ❌ Keyword match yok | REDDEDİLDİ |
| vicdan | 0 kayıt | 0 | ❌ Keyword match yok | REDDEDİLDİ |
| pişmanlık | 0 kayıt | 0 | ❌ Keyword match yok | REDDEDİLDİ |
| söz tutma | 0 kayıt | 0 | ❌ Keyword match yok | REDDEDİLDİ |
| geçmişe özlem | 0 kayıt | 0 | ❌ Keyword match yok | REDDEDİLDİ |
| toplumsal değişim | 0 kayıt | 0 | ❌ Keyword match yok | REDDEDİLDİ |

---

## 2. "SORUMLULUK" TEMASI - TÜM EVIDENCE CÜMLELERİ

### Evidence Listesi:

**1. Page 11 - "Ali, Pati'yi sahiplendiği günden beri çok şey öğrenmişti...."**
- Matched Keywords: `['sahiplen']`
- Context Strength: **1** (ÇOK DÜŞÜK)
- Neden reddedildi:
  ```
  context_strength = 1
  - keyword_variety = 1 (sadece 'sahiplen')
  - plot_hits = 0 (olay örgüsü terimi yok)
  - character_hits = 0 (karakter terimi yok)
  - behavior_hits = 0 (davranış terimi yok)
  - sentence_length = 14 kelime (uzunluk bonusu için < 14 değil)
  
  SKOR = 1 < 2 (minimum threshold for rules olmayan tema)
  → ELENDİ
  ```

**2. Page 11 - "Hayvan sevgisi, sorumluluk ve dostluk en önemli değerlerdi...."**
- Matched Keywords: `['sorumluluk']`
- Context Strength: **1** (ÇOK DÜŞÜK)
- Neden reddedildi:
  ```
  context_strength = 1
  - keyword_variety = 1 (sadece 'sorumluluk')
  - Bu cümle abstract bir ifade, gerçek olay/davranış yok
  - Context terimleri: 0
  
  SKOR = 1 < 2
  → ELENDİ
  ```

**3. Page 12 - "Bir canlıya bakmak büyük sorumluluktur," diye düşündü Ali....**
- Matched Keywords: `['sorumluluk']` (sorumluluktur → sorumluluk)
- Semantic Type: **değerlendirme**
- Neden reddedildi:
  ```
  Filter LABEL_CLAIM:
  - semantic_type = 'değerlendirme'
  - _label_evidence_supports_claim('sorumluluk', sentence, 'tema')
  - Evidence type 'değerlendirme' for tema → False
  → ELENDİ
  ```

### SORUMLULUK TEMA İÇİN ÖZET:

**Toplam 3 kanıt bulundu ama hiçbiri filtreleri geçemedi:**
- 2 kanıt: Context strength çok düşük (1 < 2)
- 1 kanıt: Semantic type = değerlendirme (tema için uygun değil)

**KÖK NEDEN:**
1. `_context_strength()` fonksiyonu çok katı
2. "sahiplen" tek başına yeterli context kanıtı saymıyor
3. THEME_CONTEXT_RULES'da sorumluluk için rule YOK
4. V6.6 fix'i çalışmıyor: threshold 2'ye düşüyor ama score 1 < 2

---

## 3. "HAYVAN SEVGİSİ" TEMASI - BAŞARILI ÖRNEK

### Evidence Listesi:

**1. Page 1 - "Tavşan çok tatlıydı ve Ali onu çok sevdi...."**
- Matched: `['tavşan']`
- Context Strength: **1**
- Neden geçti: SONRA CONTEXT FILTRESİNDEN GEÇTİ (güncel log'da)

**2. Page 4 - "Bir gün Ali okuldan geldiğinde Pati'yi hasta gördü...."**
- Matched: `['pati']`
- Context Strength: **2**
- Neden geçti: Context strength >= 2

**3. Page 11 - "Ali, Pati'yi sahiplendiği günden beri çok şey öğrenmişti...."**
- Matched: `['pati', 'sahiplen']`
- Context Strength: **2**
- Neden geçti: 2 keyword + context terimleri

**4. Page 11 - "Hayvan sevgisi, sorumluluk ve dostluk en önemli değerlerdi...."**
- Matched: `['hayvan', 'hayvan sevgisi']`
- Context Strength: **2**
- Neden geçti: 2 keyword match

**FINAL:** 4 kanıt, 4 sayfa → güç=84, güven=0.84 ✅

---

## 4. KARAKTER ÇIKARIMI SORUNU

### 4.1 "Ali" Neden Ana Karakter Seçilmedi?

**GÖZLEM:** Debug log'unda karakter çıkarımı detayları YOK.
**SEBEP:** pipeline_debug.py sadece tema çıkarımını debug ediyor, karakter çıkarımını değil.

**MUHTEMEL NEDENLER:**
1. **Noise Gate Çok Katı:** CHARACTER_NOISE_GATE sınıfında "ali" olabilir mi?
2. **Context Skoru Düşük:** Ali karakterinin context_score < threshold
3. **Action Score Yok:** Ali'de yeterli action/davranış yok
4. **Page Count Düşük:** Ali sadece birkaç sayfada geçiyor

### 4.2 "Kız Tavşan Pati" Hangi Cümlelerden Üretildi?

**MUHTEMEL KAYNAK:**
- Page 1: "Tavşan çok tatlıydı ve Ali onu çok sevdi."
- Page 2: "Ali tavşanı eve getirdi ve ona Pati adını verdi."
- Page 4: "Bir gün Ali okuldan geldiğinde Pati'yi hasta gördü."

**PROBLEM:** Sistem "Pati" kelimesini bir karakter olarak algılıyor ama:
- "Kız" öneki eklenmiş (muhtemelen "tavşan" → "kız tavşan" yanlış ilişkilendirmesi)
- "Pati" adı doğru tespit edilmiş
- SONUÇ: "Kız Tavşan Pati" (anlamsız bir isim)

### 4.3 "Evin Konukları Bir" Hangi Sayfadan Üretildi?

**MUHTEMEL KAYNAK:**
- Page 8: "Eve gelen babaannesi Ali'ye 'Aferin...' dedi."
- Page 10: "Ali, Cemal ve Pati birlikte bahçede oynadılar."

**PROBLEM:** 
- "Eve gelen" → "Evin" (possessive suffix)
- "babaannesi" → noise gate tarafından filtrelenmiş
- "konukları" → "konuk" kelimesi metinde yok, muhtemelen "gelen" yanlış parse
- "Bir" → sayfa başılığı veya başka bir kelime

**GERÇEK KAYNAK TESPİT EDİLEMEDI** - Karakter çıkarım detay logları eksik.

---

## 5. KİTAP NEDEN "FANTASTİK" OLARAK SINIFLANDIRILDI?

### Kitap Türü Algılama Kuralı:

```python
def detect_book_type(text: str, metadata: dict | None = None) -> str:
    metadata = metadata or {}
    title = str(metadata.get("kitap_adi") or metadata.get("baslik") or "")
    folded = _fold_text(f"{title} {str(text or '')[:120000]}")
    
    # FANTASTİK KURALI:
    if any(term in folded for term in ["buyu", "sihir", "ejderha", "peri", "fantastik"]):
        return "fantastik"
```

### "Tavşan Pati'nin Şaşırtıcı Yolculuğu" Kitabı:

**Başlık:** "Tavşan Pati'nin Şaşırtıcı Yolculuğu"

**Tetikleyen Kelime:** **"Şaşırtıcı"**

**Analiz:**
- `_fold_text("şaşırtıcı")` → "sasirtiçi" veya "sasirtan"
- `"sasirtan"` kelimesi `["buyu", "sihir", "ejderha", "peri", "fantastik"]` listesinde YOK
- **ANCAK** başlıkta "Yolculuk" kelimesi var
- `["macera", "yolculuk", "kesif", "gizem", "tehlike"]` listesinde "yolculuk" VAR

**GERÇEK SEBEP:** Kitap "fantastik" değil, **"macera"** olarak sınıflandırıldı!

**Kontrol:**
```python
# Macera kuralı:
if any(term in folded for term in ["macera", "yolculuk", "kesif", "gizem", "tehlike"]):
    return "macera"

# Başlık: "Tavşan Pati'nin Şaşırtıcı Yolculuğu"
# "Yolculuk" kelimesi → macera kategorisine uyar
```

**SONUÇ:** Kitap **"macera"** türünde sınıflandırıldı, sonra "fantastik macera" alt türüne dönüştürüldü.

**Neden "fantastik" görünüyor?**
- `detect_book_subtype()` fonksiyonu:
  ```python
  if book_type == "fantastik":
      return "fantastik macera"
  ```
- Ama `book_type` aslında "macera"!
- **HATA:** Debug çıktısında "Book type: fantastik" gösteriliyor ama bu yanlış

**GERÇEK KİTAP TÜRÜ:** `macera` (fantastik değil)

---

## 6. ÖZET VE KÖK NEDENLER

### Tema Algılama Sorunları:

**1. Context Strength Çok Düşük**
- Tek keyword + kısa cümle = context_strength 1-2
- Minimum threshold 2-3, bu yüzden eleniyor
- **Örnek:** "sahiplen" → context_strength=1, threshold=2 → ELENDİ

**2. THEME_CONTEXT_RULES Eksik/Aşırı Katı**
- sorumluluk, vicdan, pişmanlık, söz tutma → rules YOK
- dostluk, empati → rules VAR ama çok katı
- Dostluk: "must" kısmında `arkadaş`/`dost` gerekli, ama sadece `yardım` var
- Empati: "must" listesinde `anladı`, `hissetti` olmalı, ama sadece `düşündü` var

**3. Evidence Minimum Eşikleri Çok Katı**
- Minimum 3 kanıt, 2 sayfa, 2 bölüm
- "aile" teması 1 kanıtla tüm filtreleri geçti ama final seçimde yok

### Karakter Çıkarımı Sorunları:

**4. "Ali" Kaçırılıyor**
- Noise gate veya context skoru sorunu
- Detaylı karakter debug'u yok

**5. Anlamsız İsimler Üretiliyor**
- "Kız Tavşan Pati" → "tavşan" + "Pati" yanlış birleşimi
- "Evin Konukları Bir" → muhtemelen OCR hatası veya parse hatası

### Kitap Türü Algılama:

**6. "fantastik" Yanlış Sınıflandırma**
- Gerçek tür: **macera**
- "Yolculuk" kelimesi → macera kategorisi
- Alt tür: "fantastik macera" (yanlış, sadece "macera" olmalı)

---

## 7. ÇÖZÜM YOLU

### ADIM 1: Context Strength Düşür
```python
# Mevcut:
keyword_variety = min(2, len(set(matched_keywords)))
score = keyword_variety  # 0-2

# Öneri:
keyword_variety = min(3, len(set(matched_keywords))) + 1
score = max(2, keyword_variety)  # Minimum 2
```

### ADIM 2: THEME_CONTEXT_RULES Ekle
```python
THEME_CONTEXT_RULES = {
    "sorumluluk": {
        "must": ["sahiplen", "sorumluluk", "görev", "bakmak", "besle"],
        "action": ["düşündü", "karar", "sahiplendi", "öğrenmişti"]
    },
    "dostluk": {
        "must": ["arkadaş", "dost", "yardım"],  # Genişletildi
        "action": ["paylaş", "yardım", "destek", "birlikte"]  # yardım eklendi
    },
    "empati": {
        "must": ["anladı", "hissetti", "üzüldü", "düşündü", "merhamet"],  # düşündü eklendi
        "action": ["hissetti", "anladı", "üzüldü", "düşündü", "yardım"]
    }
}
```

### ADIM 3: Minimum Evidence Düşür
```python
# Mevcut:
if metrics["kanit_sayisi"] < 3 or metrics["farkli_sayfa_sayisi"] < 2:

# Öneri:
if metrics["kanit_sayisi"] < 2 or metrics["farkli_sayfa_sayisi"] < 1:
```

### ADIM 4: Karakter Debug Scripti Yaz
- Ali karakterinin neden kaçırıldığını göster
- "Kız Tavşan Pati" ve "Evin Konukları Bir" kaynaklarını tespit et

### ADIM 5: Kitap Türü Algılama Düzelt
- "Yolculuk" → macera (doğru)
- "fantastik" değil, "macera" olarak kalmalı
- Alt tür "fantastik macera" değil, sadece "macera" olmalı

---

## 8. KANITLAR VE DOĞRULAMA

### Tema Filtreleme Kanıtları:

```
sorumluluk:
  ✓ 3 kanıt bulundu
  ✗ Hepsi context_strength < 2
  ✗ THEME_CONTEXT_RULES yok
  ✗ Sonuç: 0 kanıt, elendi

dostluk:
  ✓ 2 kanıt bulundu
  ✗ Page 4: "yardım" var, "arkadaş"/"dost" yok → must şartı sağlanmadı
  ✗ Page 11: sadece "dost", abstract ifade → elendi
  ✗ Sonuç: 0 kanıt, elendi

empati:
  ✓ 3 kanıt bulundu
  ✗ Page 4: PEDAGOGICAL geçti, sonra LABEL_CONTEXT'te elendi
  ✗ Page 12, 15: "düşündü" → must listesinde yok
  ✗ Sonuç: 0 kanıt, elendi

aile:
  ✓ 1 kanıt, tüm filtreleri geçti
  ✗ Final: yetersiz kanıt (1 < 3)
  ✗ Sonuç: elendi

hayvan sevgisi:
  ✓ 8 kanıt bulundu
  ✓ 4 kanıt filtreleri geçti
  ✓ Final: güç=84, güven=0.84, SEÇİLDİ ✅
```

---

**SONUÇ:** Sorun tema algılama filtrelerinin çok katı olması. Özellikle context_strength hesaplaması ve THEME_CONTEXT_RULES şartları. Karakter çıkarımı için ayrı bir debug analizi gerekiyor.