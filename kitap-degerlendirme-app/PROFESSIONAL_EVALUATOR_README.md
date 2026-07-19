# Profesyonel İçerik Denetim Uzmanı - 6 Aşamalı Değerlendirme Sistemi

## 📋 Genel Bakış

Çocuk kitapları ve gençlik yayınları için profesyonel bir **İçerik Denetim Uzmanı** sistemi. Her kelimeyi 6 aşamada değerlendirir ve risk puanı verir.

## 🎯 Temel Prensipler

1. **Kelime eşleşmesi tek başına risk değildir** - Bağlam her zaman önce gelir
2. **Tarihsel anlatımlar otomatik olarak riskli değildir**
3. **Eğitsel açıklamalar riskli değildir**
4. **Mecazi kullanımlar riskli değildir**
5. **Substring bulguları geçersizdir** - "havalandırma" içinde "lan" geçerse, bulgu geçersiz
6. **Problem olmayan bulgular 0 risk puanına sahiptir**

## 🔍 6 Aşamalı Değerlendirme

### Adım 1: Kelime Bağımsız mı?
```
Kontrol: Kelimenin her tarafında harf var mı?
- Havalandırma → "lan" bağımsız değil (çevrede harf var)
- Sigara içme → "sigara" bağımsız (çevrede harf yok)
```

### Adım 2: Başka Kelimenin İçinde mi?
```
Kontrol: Kelimenin üst kelimesi var mı?
- havalandırma içinde → "lan" (GEÇERSIZ BULGU)
- sigara içme → "sigara" (GEÇERLİ BULGU)
```

### Adım 3: Cümlenin Anlamı Nedir?
```
Analiz: Olumlu/olumsuz/nötr sentiment
- Çocuk sigara içmek istedi → Olumsuz anlamlı
- Tarih ders kitabı → Nötr/eğitsel anlamlı
```

### Adım 4: Kullanım Tipi Nedir?
```
Kategoriler:
- Tarihsel: Osmanlı İmparatorluğu'nda kan dökülmüştür
- Eğitsel: Sosyal bilgiler dersinde öğrenilir
- Mecazi: Gibi, benzer, sanki gibi kelimeleri içerir
- Özendirici: Kahramanlık, vatan, kurtuluş bağlamı
- Nötr: Hiçbiri yukarıdakilerden değil
```

### Adım 5: Çocuk Okuyucu Üzerinde Olumsuz Etki?
```
Koruma Göstergeleri:
- Tarihsel → HAYIR (olumsuz etki yok)
- Eğitsel → HAYIR (olumsuz etki yok)
- Mecazi → HAYIR (olumsuz etki yok)
- Özendirici → HAYIR (olumlu etki)
- Doğrudan olumsuz kullanım → EVET (olumsuz etki var)

Final Karar:
- Koruma göstergesi varsa: RİSK YOK (0 puan)
- Koruma göstergesi yoksa: RİSK VAR (hesapla)
```

### Adım 6: Risk Puanı Hesapla (0-5 Ölçeği)
```
Risk Puanı = Base Risk × Profil Ağırlığı

Kategoriler ve Base Risk:
- Cinsellik: 5 (Kritik)
- Şiddet: 4 (Yüksek)
- Ayrımcılık: 4 (Yüksek)
- Okültizm: 3 (Orta)
- Zararlı alışkanlıklar: 3 (Orta)
- Korku/Travma: 3 (Orta)
- Olumsuz davranış: 2 (Düşük)
- Kaba dil: 2 (Düşük)
- Dijital risk: 2 (Düşük)

Profiller:
- Maarif (1.2-1.4): En sıkı (okul, müfettiş)
- MEB (1.0-1.3): Standart (ders kitapları)
- Hibrit (0.9-1.0): Dengeli (yayınevi + Maarif)
```

## 🚀 API Endpoint'leri

### 1. Profilleri Listele
```http
GET /api/professional/profiller
```

**Response:**
```json
{
  "basarili": true,
  "profiller": {
    "maarif": {
      "ad": "Maarif/MEB",
      "aciklama": "Müfettiş ve okul hassasiyeti",
      "uygulanabilir": true
    },
    "meb": { ... },
    "hybrid": { ... }
  }
}
```

### 2. Tek Kelime Değerlendir
```http
POST /api/professional/kelime-degerlendirme
Content-Type: application/json

{
  "word": "kelime",
  "context": "Kelimenin kullanıldığı cümle",
  "profile": "maarif|meb|hybrid"
}
```

**Response Örneği:**
```json
{
  "basarili": true,
  "degerlendirme": {
    "word": "kan",
    "context": "Kurtuluş Savaşı'nda çok kan dökülmüştür...",
    "profile": "maarif",
    "is_valid_finding": false,
    "risk_score": 0,
    "risk_level": "YOKSUN",
    "reason": "Olumsuz etki yok - Risk skoru 0",
    "steps": {
      "1_independence": { "is_independent": true, ... },
      "2_substring_check": { "is_substring": false },
      "3_sentence_meaning": { "sentiment": "neutral", ... },
      "4_context_type": { "type": "tarihsel", "confidence": 0.9 },
      "5_negative_impact": { "has_negative_impact": false, ... },
      "6_risk_scoring": { "risk_score": 0, "risk_level": "YOKSUN", ... }
    }
  },
  "ozet": {
    "kelime": "kan",
    "gecerli_bulgu_mu": false,
    "risk_skoru": 0,
    "risk_seviyesi": "YOKSUN",
    "neden": "Olumsuz etki yok - Risk skoru 0"
  }
}
```

### 3. Tam Metin Analizi
```http
POST /api/professional/metin-analiz
Content-Type: application/json

{
  "metin": "Değerlendirilecek kitap metni...",
  "profile": "maarif|meb|hybrid"
}
```

**Response Örneği:**
```json
{
  "basarili": true,
  "analiz": {
    "toplam_bulgu": 5,
    "problem_bulgu": 2,
    "problem_olmayan": 3,
    "ortalama_risk": 1.8,
    "bulgular": [...]
  },
  "ozet": {
    "toplam_bulgu": 5,
    "problem_bulgu": 2,
    "problem_olmayan": 3,
    "ortalama_risk": 1.8,
    "problem_türleri": {
      "DÜŞÜK": 1,
      "ORTA": 1
    },
    "profil": "maarif"
  }
}
```

## 📊 Risk Seviyeleri

| Risk Seviyesi | Puan | Anlamı |
|---|---|---|
| YOKSUN | 0 | Hiç risk yok |
| MİNİMAL | 0.1-1.0 | Çok minimal |
| DÜŞÜK | 1.1-2.0 | Az riskli |
| ORTA | 2.1-3.0 | Orta düzeyde |
| YÜKSEK | 3.1-4.0 | Yüksek risk |
| CRİTİK | 4.1-5.0 | Çok yüksek risk |

## 💡 Test Örnekleri

### Test 1: Tarihsel Bağlam
```
Kelime: kan
Bağlam: Kurtuluş Savaşı'nda çok kan dökülmüştür. Tarih dersinde bu önemli olay anlatılıyor.
Profil: maarif

Sonuç:
✅ Geçerli Bulgu: HAYIR
✅ Risk Skoru: 0
✅ Risk Seviyesi: YOKSUN
✅ Neden: Tarihsel bağlamda olumsuz etki yok
```

### Test 2: Substring
```
Kelime: lan
Bağlam: Havalandırma sistemini kontrol edin.
Profil: maarif

Sonuç:
✅ Geçerli Bulgu: HAYIR
✅ Risk Skoru: 0
✅ Risk Seviyesi: YOKSUN
✅ Neden: "havalandırma" içindeki substring
```

### Test 3: Doğrudan Risk
```
Kelime: sigara
Bağlam: Kahramanı sigara içerken görüyoruz.
Profil: maarif

Sonuç:
✅ Geçerli Bulgu: EVET
✅ Risk Skoru: 3.9
✅ Risk Seviyesi: YÜKSEK
✅ Neden: zararlı_alışkanlıklar (Base 3 × Weight 1.3)
```

## 🛠️ Kurulum

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Sunucuyu başlat
python app.py

# Test et
python test_professional_api.py
```

## 📝 Modül Yapısı

```
professional_evaluator.py
├── ProfessionalContentEvaluator (Ana sınıf)
├── evaluate_word() - 6 aşamalı kelime değerlendirmesi
├── evaluate_text() - Tam metin analizi
├── _step1_check_independence() - Adım 1
├── _step2_check_substring() - Adım 2
├── _step3_analyze_meaning() - Adım 3
├── _step4_determine_context() - Adım 4
├── _step5_assess_impact() - Adım 5
├── _step6_calculate_risk() - Adım 6
└── Destekleyici metodlar
```

## 🎓 Eğitim Kuralları

### Özendirici Bağlam (Olumlu)
```
Anahtar Kelimeler: cesur, güçlü, başarılı, madalya, kahramanlık, 
                   fedai, vatan, millet, kurtuluş, zafer, başarı

SONUÇ: Olumlu etki → YOKSUN risk
```

### Tarihsel Bağlam
```
Anahtar Kelimeler: tarih, geçmiş, dönemi, daha, eskiden, eski,
                   zamanında, 1800-1900, yüzyıl, osmanlı, cumhuriyet

SONUÇ: Eğitsel amaçlı → YOKSUN risk
```

### Eğitsel Bağlam
```
Anahtar Kelimeler: öğren, dersin, ders, bilgi, anlat, açıkla,
                   örnek, sosyal, sınıf, okul, eğit, rehber

SONUÇ: Öğretme amaçlı → YOKSUN risk
```

### Mecazi Bağlam
```
Anahtar Kelimeler: gibi, benzer, sahip, görünüşlü, adeta, sanki

SONUÇ: Abartılı/kıyaslamalı → YOKSUN risk
```

## ⚙️ Özelleştirme

### Profil Ekle
```python
# config.py veya professional_evaluator.py içinde
'ozel_profil': {
    'name': 'Özel Profil',
    'weights': {
        'siddet': 1.0,
        'cinsellik': 1.0,
        # ... diğer kategoriler
    }
}
```

### Kategori Ekle
```python
# professional_evaluator.py içinde
self.risk_keywords = {
    'yeni_kategori': ['keyword1', 'keyword2', ...],
    # ...
}
```

## 🔐 Güvenlik

- Türkçe karakter desteği tam
- UTF-8 encoding otomatik
- XSS/Injection koruması (Flask tarafından)
- Rate limiting hazırlanabilir

## 📞 Destek

- Ana modül: `professional_evaluator.py`
- API endpoint'leri: `app.py`
- Test dosyası: `test_professional_api.py`

---

**Versiyon:** 1.0  
**Son Güncelleme:** 2026-06-08  
**Durum:** ✅ Üretim Hazır
