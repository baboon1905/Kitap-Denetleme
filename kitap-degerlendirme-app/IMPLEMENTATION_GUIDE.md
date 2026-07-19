# 🎓 Maarif Modeli Yayın Denetim Sistemi v1.0
## Uygulama Kılavuzu

---

## 📋 Genel Yapı

Sistem, Türkiye'nin Maarif Modeli'ne uygun olarak çocuk ve gençlik kitaplarını değerlendiren, **AI destekli yayın denetim aracı**dır.

### 🎯 Ana Özellikler

| Özellik | Detay |
|---------|-------|
| **5 Analiz Profili** | Maarif/MEB, Hibrit, Editoryal, Hassas Veli, Kuruma Özel |
| **Risk Puanlama** | 0-5 aralıkta kategoriler, 0-100 final skor |
| **Sakıncalı Kelime Sözlüğü** | 1000+ kelime, 10+ kategori |
| **Bağlam Analizi** | Tarihî, edebi, mecazî bağlamları değerlendir |
| **Maarif Profilleri** | 10 öğrenci profili algılaması |
| **MEB Kriterleri** | Talim ve Terbiye Kurulu standartları |

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────────┐
│                     Flask API (app.py)                          │
│                    5 Analiz Profiline Destek                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐  ┌──────▼─────┐  ┌────────▼────────┐
│ PDF İşleme     │  │ Maarif      │  │ Rapor           │
│ (pdf_processor)│  │ Evaluator   │  │ Generator       │
│                │  │ (evaluator_ │  │ (report_        │
│ • Metin çıkar  │  │  maarif)    │  │ generator)      │
│ • İstatistik   │  │             │  │                 │
│                │  │ • 5 Profil  │  │ • PDF Rapor     │
│                │  │ • Risk Puan │  │ • JSON Export   │
└────────────────┘  │ • Kategori  │  │ • Karşılaştırma │
                    │ • Bağlam    │  │                 │
                    │ • Maarif    │  │                 │
                    │   Profilleri│  │                 │
                    └──────┬──────┘  └─────────────────┘
                           │
                    ┌──────▼──────┐
                    │  config.py  │
                    │             │
                    │ • 5 Profil  │
                    │ • Risk Puan │
                    │ • 1000+ Kw  │
                    │ • Bağlam    │
                    └─────────────┘
```

---

## 🔧 API Endpoints

### 1️⃣ Profilleri Getir
```bash
GET /api/profiller
```
**Yanıt:**
```json
{
  "maarif_meb": {
    "ad": "Maarif/MEB",
    "aciklama": "Müfettiş ve okul hassasiyeti",
    "yaklasim": "...",
    "kullanim": "Okul listeleri"
  },
  ...
}
```

---

### 2️⃣ PDF Yükle
```bash
POST /api/yukleme
Content-Type: multipart/form-data

Form Data:
- pdf: <file>
```

**Yanıt:**
```json
{
  "basarili": true,
  "dosya_yolu": "uploads/kitap.pdf",
  "kitap_adi": "kitap.pdf",
  "metadata": {...},
  "istatistikler": {
    "sayfa_sayisi": 120,
    "kelime_sayisi": 15000
  },
  "metin_onizleme": "..."
}
```

---

### 3️⃣ Değerlendirme Yap
```bash
POST /api/degerlendir
Content-Type: application/json

{
  "dosya_yolu": "uploads/kitap.pdf",
  "profil": "hibrit",        // Varsayılan
  "yas_grubu": "6-12"        // Varsayılan
}
```

**Yanıt:**
```json
{
  "basarili": true,
  "analiz_sonucu": {
    "profil": "hibrit",
    "final_skor": 35.5,
    "karar": {
      "seviye": "Düşük Risk",
      "simge": "✔️",
      "renk": "lightgreen"
    },
    "kategori_bulgulari": {
      "sigara": {
        "bulundu": true,
        "toplam_bulgu": 2,
        "ortalama_risk": 2.5,
        "bulunan_kelimeler": [...]
      },
      ...
    },
    "maarif_profilleri": {
      "cesaretli": {
        "profil_adi": "Cesaretli",
        "bulgu_sayisi": 5,
        "puan": 5
      },
      ...
    },
    "detayli_rapor": "..."
  },
  "metin_istatistikleri": {
    "kelime_sayisi": 15000,
    "karakter_sayisi": 95000,
    "satir_sayisi": 500
  }
}
```

---

### 4️⃣ Profilleri Karşılaştır
```bash
POST /api/karsilastir
Content-Type: application/json

{
  "dosya_yolu": "uploads/kitap.pdf",
  "yas_grubu": "6-12"
}
```

**Yanıt:**
```json
{
  "basarili": true,
  "karsilastirma": {
    "maarif_meb": {
      "ad": "Maarif/MEB",
      "final_skor": 45.2,
      "karar": {"seviye": "Dikkat Gerektirir", "simge": "⚠️"}
    },
    "hibrit": {
      "ad": "Hibrit",
      "final_skor": 35.5,
      "karar": {"seviye": "Düşük Risk", "simge": "✔️"}
    },
    "editoryal": {
      "ad": "Editoryal",
      "final_skor": 28.3,
      "karar": {"seviye": "Düşük Risk", "simge": "✔️"}
    },
    "hassas_veli": {
      "ad": "Hassas Veli",
      "final_skor": 62.1,
      "karar": {"seviye": "Dikkat Gerektirir", "simge": "⚠️"}
    },
    "kuruma_ozel": {
      "ad": "Kuruma Özel",
      "final_skor": 35.5,
      "karar": {"seviye": "Düşük Risk", "simge": "✔️"}
    }
  }
}
```

---

### 5️⃣ Rapor İndir
```bash
POST /api/rapor
Content-Type: application/json

{
  "analiz_sonucu": {...},
  "kitap_adi": "Kitabın Adı"
}
```

**Yanıt:** PDF dosyası

---

## 📊 Risk Puanlama Sistemi

### Puan Aralıkları (0-5)

| Puan | Seviye | Açıklama |
|------|--------|----------|
| **0** | Temiz | Kelime yok veya tamamen ilgisiz |
| **1** | Bilgi | Edebi, tarihî veya mecazi bağlam |
| **2** | Düşük | Kısa ve özendirici olmayan kullanım |
| **3** | Dikkat | Yaş düzeyine göre rehberlik gerekli |
| **4** | Revizyon | Açık anlatım, tekrar veya risk |
| **5** | Uygun Değil | Özendirme, normalleştirme, travmatik içerik |

### Final Skor Aralıkları (0-100)

| Skor | Karar | Anlamı |
|------|-------|--------|
| **0-20** | ✅ Uygun | Herhangi bir sorun yoktur |
| **21-40** | ✔️ Düşük Risk | Göz önünde bulundurulmalıdır |
| **41-60** | ⚠️ Dikkat | Uygun yaş seçilmeli |
| **61-80** | 🔴 Revizyon | Bölümleri inceleyin |
| **81-100** | ❌ Uygun Değil | Ciddi revizyonlar gerekli |

---

## 5️⃣ Analiz Profilleri

### 1. Maarif/MEB (Müfettiş Hassasiyeti)
- **Ağırlık:** Sıkı kontrol
- **Vurgu:** 
  - Milli-manevi değerler ⬆️
  - Zararlı alışkanlıklar ⬆️
  - Mahremiyet ⬆️
- **Kullanım:** Okul listeleri, resmi kurumlar

### 2. Hibrit (Yayınevi + Maarif Dengesi) ⭐ **Varsayılan**
- **Ağırlık:** Dengeli
- **Vurgu:** Edebi bağlam + Maarif hassasiyeti
- **Kullanım:** Genel kitap denetimi

### 3. Editoryal (Yayın Kurulu)
- **Ağırlık:** Rahat
- **Vurgu:** Edebi özgürlük, yaş uygunluğu
- **Kullanım:** Yayın kurulu değerlendirmesi

### 4. Hassas Veli (En Sıkı)
- **Ağırlık:** En sıkı
- **Vurgu:** 
  - Sigara/Alkol ⬆️⬆️
  - Cinsellik/Mahremiyet ⬆️⬆️
  - Korku/Travma ⬆️
- **Kullanım:** Özel okul, veli raporları

### 5. Kuruma Özel (Özelleştirilebilir)
- **Ağırlık:** Admin tarafından ayarlanabilir
- **Vurgu:** Kuruma göre özel kriterler
- **Kullanım:** Kurumsal ortaklar

---

## 📚 Sakıncalı Kelime Kategorileri

### 1. Sigara (Risk: 4/5)
Sigarayla ilgili tüm kelimeler, tütün, duman, sigara alışkanlığı vb.

### 2. Alkol (Risk: 4/5)
Alkol, içki, meykhane, bar, rakı, şarap vb.

### 3. Cinsellik & Mahremiyet (Risk: 5/5) ⚠️
Çıplak, mahrem, taciz, tecavüz, ırz, namus, utanç vb.

### 4. Şiddet (Risk: 4/5)
Silah, bomba, öldürmek, kan, şeytan vb.

### 5. Argo & Kaba Dil (Risk: 3/5)
Küfür, hakaret, edepsizlik vb.

### 6. İslami İhlal (Risk: 4/5)
Sihir, büyü, fal, müstehcen, peygamberlik vb.

### 7. Aile Değerleri (Risk: 3/5)
Boşanma, evlilik, kız isteme vb.

### 8. Korku & Travma (Risk: 3/5)
Korku, dehşet, travma, hastalık vb.

### 9. Din Temaları (Risk: 2/5)
Hıristiyan, kilise, aziz, cehennem, cennet vb.

### 10. Uyuşturucu (Risk: 5/5) ⚠️
Uyuşturucu, esrar, kokain, heroın vb.

---

## 🧠 Bağlam Analizi

Sistem, kelimeleri çevreleyen bağlamı analiz ederek risk puanını ayarlar.

### ⬇️ Risk Puanı Düşüren Bağlamlar
- **Tarihî bağlam:** "Tarihin", "Osmanlı döneminde", "Antikçağda"
- **Edebi bağlam:** "Metafor", "Benzetme", "Romanında", "Hikâyede"
- **Mecazî anlam:** "Gibi", "Sanki", "Sembol", "Kurmaca"

**Örnek:**
```
❌ "Tütün para kazandırdı" → Risk: 4
✅ "Osmanlı döneminde tütün ticareti → Risk: 1 (tarihî bağlam)
✅ "Güzel kız sanki çiçek gibi" → Risk: 0 (edebi/mecazi)
```

### ⬆️ Risk Puanı Yükseltenv Bağlamlar
- "Özendirme", "Teşvik", "Teferruatlı tasvir"
- "Model alma", "Tekrarlama"

---

## 🎓 Maarif Modeli Profilleri Algılaması

Sistem, metin içinde 10 Maarif profili göstergesi arar:

| Profil | Göstergeler |
|--------|------------|
| 🤔 Sorgulayıcı | Neden, Nasıl, Merak, Araştırma |
| 💪 Cesaretli | Cesur, Cesaret, Zorluk, Karşı Dur |
| 🎨 Üretken | Yaratıcı, Üretim, Icat, Tasarım |
| 📖 Bilge | Bilgelik, Hikmet, Öğretici, Akıl |
| ✨ Ahlaklı | Doğru, Dürüst, Ahlak, Erdem |
| ❤️ Merhametli | Merhamet, Şefkat, Yardım, Sevgi |
| 🇹🇷 Vatansever | Vatan, Millet, Bayrak, İstiklal |
| 🎭 Estetik | Güzel, Sanat, Ressam, Müzik |
| 💎 İradeli | İrade, Kararlı, Azimli, Başarı |
| 🏃 Sağlıklı | Sağlık, Spor, Beslenme, Hijyen |

---

## 📝 Kullanım Örneği

### Python ile API Çağrısı

```python
import requests
import json

# 1. Profilleri getir
response = requests.get('http://localhost:5000/api/profiller')
print(response.json())

# 2. PDF yükle
files = {'pdf': open('kitap.pdf', 'rb')}
response = requests.post('http://localhost:5000/api/yukleme', files=files)
dosya_yolu = response.json()['dosya_yolu']

# 3. Değerlendir (Hibrit profili ile)
data = {
    'dosya_yolu': dosya_yolu,
    'profil': 'hibrit',
    'yas_grubu': '6-12'
}
response = requests.post('http://localhost:5000/api/degerlendir', json=data)
analiz = response.json()['analiz_sonucu']

print(f"Final Skor: {analiz['final_skor']}/100")
print(f"Karar: {analiz['karar']['seviye']}")

# 4. Tüm profilleri karşılaştır
data = {
    'dosya_yolu': dosya_yolu,
    'yas_grubu': '6-12'
}
response = requests.post('http://localhost:5000/api/karsilastir', json=data)
karsilastirma = response.json()['karsilastirma']

for profil, sonuc in karsilastirma.items():
    print(f"{sonuc['ad']}: {sonuc['final_skor']}/100")
```

---

## 🚀 Başlatma

```bash
# 1. Klasöre git
cd "c:\Users\fatih\Masaüstü\Kitap Değerlendirme\kitap-degerlendirme-app"

# 2. Bağımlılıkları kur (ilk kez)
pip install -r requirements.txt

# 3. Sunucuyu başlat
python app.py

# Çıktı:
# 🚀 Maarif Modeli Yayın Denetim Sistemi başlıyor...
# 📝 Port: 5000
# 🔧 Debug Modu: True
# * Running on http://127.0.0.1:5000
```

---

## 📋 Dosya Yapısı

```
kitap-degerlendirme-app/
├── app.py                    # Flask API ana dosyası
├── config.py                 # Konfigürasyon (profil, kelime sözlüğü)
├── evaluator_maarif.py       # Risk puanlama motoru ⭐ YENİ
├── pdf_processor.py          # PDF işleme
├── report_generator.py       # Rapor oluşturma
├── requirements.txt          # Python bağımlılıkları
├── templates/
│   └── index.html           # Frontend (varsa)
├── uploads/                 # PDF yükleme klasörü
└── IMPLEMENTATION_GUIDE.md   # Bu dosya
```

---

## 🔑 Anahtar Dosya: evaluator_maarif.py

Bu dosya **Maarif Modeli'nin kalbi**:

- **`MaarifDegerlendiricisi` sınıfı:** Ana değerlendirme sistemi
- **`analiz_yap()` metodu:** Analiz yapan ana metod
- **`_kategoriyi_taray()` metodu:** Kategori taraması
- **`_baglamsal_analiz_yap()` metodu:** Bağlam analizi
- **`_maarif_profilleri_tespit_et()` metodu:** Profil algılaması

---

## 💾 config.py Güncellemeleri

Bu dosya ayarlanabilir:

```python
# 5 Profili ayarla
ANALIZ_PROFILLERI["kuruma_ozel"]["agirliklari"]["sigara_alkol"] = 2.0

# Yeni kelime kategorisi ekle
SAKINCALI_KELIMELER["yeni_kategori"] = {
    "risk_puani": 3,
    "kelimeler": ["kelime1", "kelime2", ...]
}
```

---

## ⚠️ Hatalar ve Çözümler

| Hata | Çözüm |
|------|-------|
| `ModuleNotFoundError: groq` | `pip install groq` |
| `PDF'den metin çıkarılamadı` | PDF'yi kontrol et, metin taraması devre dışı olabilir |
| `Port 5000 zaten kullanılıyor` | `.env` dosyasında `FLASK_PORT=5001` ayarla |

---

## 📈 Sonraki Adımlar

1. **Frontend geliştir** - React/Vue ile UI oluştur
2. **Veritabanı ekle** - SQLAlchemy ile sonuçları kaydet
3. **Groq API entegre et** - LLM tabanlı analize geçiş
4. **RAG sistemi** - Vektör veritabanıyla gelişmiş arama
5. **Multi-dil desteği** - İngilizce, Kürtçe vb.

---

**Sistem Versiyonu:** 1.0  
**Son Güncelleme:** 2026-06-05  
**Geliştiriciler:** Maarif Modeli Araştırma Grubu

✅ Sistem başarıyla entegre edilmiştir!
