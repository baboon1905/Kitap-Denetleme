# Kitap Değerlendirme Sistemi

Türkiye Yüzyılı Maarif Modeli kriterlerine göre kitap değerlendirmesi yapan web uygulaması.

## Özellikler

✅ **PDF Analizi** - Kitapları PDF formatından analiz eder
✅ **Sakıncalı İçerik Taraması** - Sakıncalı kelimeleri bağlam analizi ile değerlendirir
✅ **Maarif Modeli Uyumu** - 10 profil öğrenci profiline göre değerlendirir
✅ **MEB TTK Kriterleri** - Talim ve Terbiye Kurulu kriterlerine uygunluk kontrolü
✅ **Kültürel Analiz** - Türk-İslam değerlerine ve kültürel uyuma göre değerlendirme
✅ **PDF Rapor** - Sonuçları otomatik PDF rapor olarak oluşturur

## Gereksinimler

- Python 3.9+
- Flask
- OpenAI API anahtarı

## Kurulum

### 1. Python Yükleme

Windows'ta Python yoksa [python.org](https://www.python.org/downloads/) adresinden indirin ve kurun.

Kurulum sırasında **"Add Python to PATH"** seçeneğini işaretleyin.

### 2. Proje Dosyalarını Klonla

```bash
cd c:\Users\fatih\Masaüstü\Kitap Değerlendirme\kitap-degerlendirme-app
```

### 3. Virtual Environment Oluştur

```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### 5. Ortam Değişkenlerini Ayarla

`.env.example` dosyasını `.env` olarak kopyalayın:

```bash
copy .env.example .env
```

`.env` dosyasını açıp OpenAI API anahtarınızı ekleyin:

```
OPENAI_API_KEY=sk-...your-key-here...
FLASK_ENV=development
FLASK_PORT=5000
```

### 6. Uygulamayı Başlat

```bash
python app.py
```

Tarayıcıda açın: `http://localhost:5000`

## Kullanım

1. **PDF Seç** - Değerlendirilecek kitabın PDF dosyasını seçin
2. **Kitap Türü** - Kitabın türünü seçin (Çocuk Kitabı, Ders Kitabı, Roman vb.)
3. **Değerlendir** - Değerlendirme işlemini başlatın
4. **Rapor İndir** - Değerlendirme sonuçlarını PDF olarak indirin

## Değerlendirme Kriterleri

### Maarif Modeli (10 Profil)
- Sorgulayıcı
- Cesaretli
- Üretken
- Bilge
- Ahlaklı
- Merhametli
- Vatansever
- Estetik
- İradeli
- Sağlıklı

### MEB TTK Kriterleri
- 1.1 Anayasa ve Mevzuat Uygunluğu
- 1.2 Millî Güvenlik
- 1.3 Eşitlik ve Kapsayıcılık
- 1.4 Millî ve Manevi Değerler
- 1.5 Güvenli ve Etik İçerik
- 1.6 Bilimsel Doğruluk
- 1.7 Reklam ve Ticari Unsurlar
- 1.9 Çevre ve Sürdürülebilir Yaşam

## Dosya Yapısı

```
kitap-degerlendirme-app/
├── app.py                 # Flask ana sunucusu
├── config.py             # Konfigürasyon ve kriterler
├── pdf_processor.py      # PDF işleme
├── evaluator.py          # OpenAI ile değerlendirme
├── report_generator.py   # PDF rapor oluşturma
├── requirements.txt      # Python bağımlılıkları
├── .env.example          # Ortam değişkenleri şablonu
├── templates/
│   └── index.html       # Web arayüzü
└── uploads/             # Yüklenen PDF dosyaları (otomatik oluşturulur)
```

## Sorun Giderme

### "OPENAI_API_KEY not found"
- `.env` dosyasını kontrol edin
- OpenAI API anahtarını doğru biçimde girin

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### "PDF reading error"
- PDF dosyasının bozuk olmadığından emin olun
- UTF-8 biçiminde kaydedilmesini deneyin

## API Endpoints

### POST /api/yukleme
PDF dosyası yükler ve metadata çıkartır

### POST /api/degerlendir
Kitabı değerlendirir

### POST /api/rapor-olustur
Değerlendirme sonuçlarından PDF rapor oluşturur

## Lisans

MIT License

## Yazar

Yayın Denetim Birimi
