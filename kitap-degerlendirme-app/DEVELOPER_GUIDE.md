# 🏛️ Maarif Modeli Yayın Denetim Sistemi - Geliştirici Rehberi

## 📋 Hızlı Başlangıç

### 1. **Backend Sistemi Başlat**
```bash
# Gerekli paketleri yükle
pip install -r requirements.txt

# Flask sunucusunu çalıştır
python app.py
# ➜ http://127.0.0.1:5000
```

### 2. **Sistem Sağlığını Kontrol Et**
```bash
curl http://127.0.0.1:5000/health
# ➜ {"status": "OK", "message": "Maarif Modeli...", "versiyon": "1.0"}
```

---

## 📁 Proje Yapısı ve Dosyalar

### **ÜZERİNDE ÇALIŞILMIŞ ✅ (TAMAMLANDI)**

| Dosya | Açıklama | Durum |
|-------|----------|-------|
| `config.py` | 10 kategori, 1115+ kelime, 5 profil, 8 MEB kriteri | ✅ HAZIR |
| `evaluator_maarif.py` | Temel analiz motoru | ✅ HAZIR |
| `pdf_rapor_generator_v2.py` | 12-bölümlü PDF rapor üreticisi | ✅ HAZIR |
| `app.py` | Flask API (6 endpoint) | ✅ HAZIR |
| `ai_prompts.py` | 7 LLM prompt | ✅ HAZIR |

### **BAŞLANMIŞ ⏳ (DEVAM ETTİRİLMESİ GEREKLI)**

| Dosya | Ne Yapılmalı | Deadline |
|-------|-------------|----------|
| `react_ui_components.tsx` | CSS styling + API integration | Week 2 |
| `rag_architecture.py` | Vector DB + Chunking implement | Week 3-4 |
| `ROADMAP_IMPLEMENTATION.py` | 6 aşama proje yönetimi | Tracking |
| `ORNEK_RAPORLAR.py` | 4 kitap örneği test | Week 2 |

---

## 🔧 YAPILMASI GEREKEN İŞLER (Priority)

### **🔴 ACIL (Bu Hafta)**

#### 1. **React Components'i CSS'e Döktür**
```typescript
// react_ui_components.tsx dosyasında placeholder class'lar var:
- .dashboard
- .stat-card
- .upload-form
- .btn-primary
- .risk-card
- .score-display
- .profil-grid

// Çözüm: Tailwind CSS veya Material-UI kullan
npm install @mui/material @emotion/react @emotion/styled
// veya
npm install -D tailwindcss postcss autoprefixer
```

#### 2. **PDF Endpoint'i Entegre Et**
```python
# app.py'a ekle:
from pdf_rapor_generator_v2 import MaarifPDFRaporuGeneratoru

@app.route('/api/rapor_generate', methods=['POST'])
def rapor_generate():
    data = request.json
    generator = MaarifPDFRaporuGeneratoru("output.pdf")
    generator.rapor_uret(
        data['kitap_bilgileri'],
        data['analiz_sonucu'],
        data['meb_sonuclari'],
        data['detenci_bilgileri']
    )
    return send_file("output.pdf")
```

#### 3. **Örnek Raporları Test Et**
```bash
python ORNEK_RAPORLAR.py
# Çıktı: 4 kitap için detaylı JSON raporlar
```

---

### **🟡 ÖNEMLİ (Haftalar 2-3)**

#### 4. **React Frontend'i API'ye Bağla**
```typescript
// KitapYukleme.tsx içinde:
const handleSubmit = async (e) => {
    const formData = new FormData();
    formData.append('file', state.dosya);
    formData.append('baslik', state.baslik);
    
    const response = await fetch('/api/yukleme', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    // Sonuç sayfasına yönlendir
};
```

#### 5. **RAG Mimarisi Tasarımını İndir**
```bash
# Başlık: rag_architecture.py
# İçerik:
#  - Vector DB seçimi (Pinecone/Qdrant/Weaviate)
#  - Turkish BERT embedding setup
#  - Chunking stratejisi (800-1200 token)
#  - Cache mekanizması
#  - Human-in-Loop sistem

# Hangisini seçersin?
# A) Pinecone (bulut, kolay, $)
# B) Qdrant (self-hosted, hızlı, ücretsiz)
# C) Weaviate (GraphQL, esnek, bulut/self)
```

#### 6. **Groq/OpenAI LLM Entegrasyonu**
```python
# ai_prompts.py + evaluator_maarif.py'ı birleştir
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ai_baglam_analizi(metin, kelime):
    prompt = BAGLAM_ANALIZI_PROMPTU.format(
        metin=metin,
        kelime=kelime
    )
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

---

### **🟢 İYE SAHIP (Haftalar 4+)**

#### 7. **Denetçi Onay Sistemi**
```python
@app.route('/api/bulgular/<bulgu_id>/onayla', methods=['POST'])
def onayla_bulgu(bulgu_id):
    data = request.json
    # data = {
    #   "durum": "onaylandı|reddedildi|gözden_geçirildi",
    #   "notu": "...",
    #   "denetçi": "Ahmet Bey"
    # }
    
    # 1. Veritabanında kaydet
    # 2. Cache güncelle
    # 3. Model feedback'i işle
    
    return {"status": "ok"}
```

#### 8. **Admin Paneli**
- Profil yönetimi (ağırlık ayarları)
- Sözlük yönetimi (yeni terim ekleme)
- Raporlar ve istatistikler
- Kullanıcı yönetimi

---

## 📊 API Reference

### **GET /health**
```bash
curl http://127.0.0.1:5000/health
# ➜ {"status": "OK", "versiyon": "1.0"}
```

### **GET /api/profiller**
```bash
curl http://127.0.0.1:5000/api/profiller
# ➜ [{ad: "Hibrit", ağırlıklar: {...}}, ...]
```

### **POST /api/yukleme**
```bash
curl -X POST -F "file=@kitap.pdf" http://127.0.0.1:5000/api/yukleme
# ➜ {"dosya_adi": "kitap_001.pdf", "status": "ok"}
```

### **POST /api/degerlendir**
```bash
curl -X POST http://127.0.0.1:5000/api/degerlendir \
  -H "Content-Type: application/json" \
  -d '{
    "dosya_adi": "kitap_001.pdf",
    "profil": "hibrit",
    "yas_grubu": "12-15"
  }'
# ➜ {final_skor: 42, karar: "⚠️", kategori_bulgulari: {...}, ...}
```

### **POST /api/rapor** (Geliştirme Gerekli)
```bash
curl -X POST http://127.0.0.1:5000/api/rapor \
  -H "Content-Type: application/json" \
  -d '{"analiz_sonucu": {...}}'
# ➜ PDF dosyası download
```

---

## 🧪 Test Komutları

```bash
# 1. Temel sözlük testi
python test_dictionary_deployment.py
# ➜ 6/6 testler geçti ✅

# 2. Örnek raporları görüntüle
python ORNEK_RAPORLAR.py
# ➜ 4 kitap örneği (Çocuk, Gençlik, Tarihî, Fantastik)

# 3. API endpoints'i test et
python test_api.py
# ➜ Tüm endpoints test edilir

# 4. Groq/OpenAI testi
python test_groq.py
# ➜ LLM bağlantısı kontrol edilir
```

---

## 🔑 Environment Variables

```bash
# .env dosyası oluştur:
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENV=us-west1-gcp

# Flask config
FLASK_ENV=development
DEBUG=True
```

---

## 📈 İlerleme Takibi

```
AŞAMA 1: MVP - TAMAMLANDI ✅ (100%)
├─ config.py: 1115+ terim
├─ evaluator_maarif.py: Temel motor
├─ pdf_rapor_generator_v2.py: PDF üreticisi
├─ app.py: 6 endpoint
└─ test_dictionary_deployment.py: 6/6 test GEÇTI

AŞAMA 2: AI Bağlam Analizi - BAŞLANMADI ⏳ (0%)
├─ Groq/OpenAI entegrasyonu
├─ False positive kuralları
├─ Cache mekanizması
└─ Haftalar: 3-4 (14 gün)

AŞAMA 3: Profil Sistemi - BAŞLANMADI ⏳ (20%)
├─ 5 profil optimizasyonu
├─ 8 MEB kriteri
├─ 10 Maarif profili
└─ Haftalar: 4-5

AŞAMA 4: RAG Mimarisi - BAŞLANMADI ⏳ (0%)
├─ Vector DB setup (Pinecone/Qdrant)
├─ Turkish BERT embedding
├─ Chunking (800-1200 token)
└─ Haftalar: 6-7

AŞAMA 5: React Frontend - DEVAM EDİYOR 🔄 (15%)
├─ 7 component design: ✅ HAZIR
├─ CSS styling: ⏳ GEREKLI
├─ API integration: ⏳ GEREKLI
└─ Haftalar: 7-8

AŞAMA 6: Prodüksyon - BAŞLANMADI ⏳ (0%)
├─ Human-in-Loop system
├─ Denetçi onay sistemi
├─ Performance monitoring
└─ Haftalar: 8-9
```

---

## 🎯 Kısa Vadeli Hedefler (Bu Hafta)

- [ ] React components'e CSS ekle (Material-UI veya Tailwind)
- [ ] PDF endpoint'i /api/rapor'a entegre et
- [ ] Örnek raporlar testini çalıştır
- [ ] Frontend-backend API call'larını test et

## 🌟 Orta Vadeli Hedefler (2-3 Hafta)

- [ ] Groq/OpenAI LLM entegrasyon
- [ ] Vector DB (Pinecone/Qdrant) setup
- [ ] Cache sistemi implementasyon
- [ ] Human-in-Loop denetçi sistemi

## 🚀 Uzun Vadeli Hedefler (Aylık)

- [ ] Production deployment
- [ ] 99.5% uptime SLA
- [ ] 1000+ concurrent users
- [ ] CI/CD pipeline

---

## 📞 Sorun Çözüm

### **Problem: "ModuleNotFoundError: No module named 'config'"**
```bash
# Çözüm: config.py aynı dizinde olduğundan emin ol
# Alternatif: sys.path.append('/path/to/app')
```

### **Problem: "Vector DB connection refused"**
```bash
# Docker ile local Qdrant başlat:
docker run -p 6333:6333 qdrant/qdrant

# veya Pinecone free tier kullan
pip install pinecone-client
```

### **Problem: "React components rendered but no styling"**
```bash
# CSS import eksik
import './styles/maarif-app.css'

# veya Material-UI theme prop'unu ekle
import { ThemeProvider } from '@mui/material/styles'
```

---

## 📚 Referanslar

- **Maarif Modeli**: [config.py](config.py) - Tüm sistem konfigürasyonu
- **Analiz Motoru**: [evaluator_maarif.py](evaluator_maarif.py) - Risk scoring
- **RAG Mimarisi**: [rag_architecture.py](rag_architecture.py) - Vector DB design
- **Örnek Raporlar**: [ORNEK_RAPORLAR.py](ORNEK_RAPORLAR.py) - 4 kitap örneği
- **Yol Haritası**: [ROADMAP_IMPLEMENTATION.py](ROADMAP_IMPLEMENTATION.py) - 6 aşama planı

---

## ✅ Kontrol Listesi

```
PRE-DEPLOYMENT:
[ ] Tüm testler yeşil (6/6)
[ ] API endpoints canlı
[ ] React components rendered
[ ] PDF generation working
[ ] Environment variables set
[ ] Database backups active
[ ] Logging configured
[ ] Security audit passed

DEPLOYMENT:
[ ] Blue-green setup
[ ] Load testing (1000 users)
[ ] Monitoring dashboard
[ ] Incident playbook ready
[ ] Support team trained
```

---

**Son Güncelleme:** 2024-06-05
**Sistem Sürümü:** v2.0
**İstatistik:** 1115+ terim, 5 profil, 8 MEB kriteri, 7 AI prompt, 7 React ekran
