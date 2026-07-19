# Kitap Denetleme

Türkiye Yüzyılı Maarif Modeli ve MEB Talim ve Terbiye Kurulu ölçütleri doğrultusunda kitap analizi ve yayın değerlendirmesi yapan React + Flask tabanlı web uygulaması.

## Proje açıklaması

Kitap Denetleme; PDF kitap içeriklerini analiz eder, tema ve kazanım ilişkilerini değerlendirir, içerik risklerini bağlam içinde inceler ve sonuçları Source, PDF ve Word raporları olarak sunar.

Sistem, yapay zekâ destekli analiz sonuçlarını kanıt yüzeyleri ve tutarlılık kontrolleriyle doğrulamayı amaçlar. Otomatik sonuçlar uzman değerlendirmesinin yerine geçmez.

## Özellikler

- PDF kitap metni çıkarımı ve analizi
- Tema ve öğrenme kazanımı değerlendirmesi
- MEB TTK ölçütlerine göre içerik kontrolü
- Bağlama duyarlı sakıncalı içerik taraması
- Karakter, olay örgüsü ve kanıt analizi
- Source, PDF ve Word rapor üretimi
- Rapor kanıtı ve özet tutarlılığı kontrolleri
- Canonical kişi ve mekân doğrulaması
- React tabanlı kullanıcı arayüzü
- Flask tabanlı API
- Regresyon ve kalite kapısı testleri

## Gereksinimler

- Python 3.11 önerilir
- Node.js 18 veya üzeri
- npm
- OpenAI API anahtarı
- Windows, Linux veya macOS

## Kurulum

Repository'yi klonlayın ve uygulama dizinine geçin:

```bash
git clone https://github.com/baboon1905/Kitap-Denetleme.git
cd Kitap-Denetleme/kitap-degerlendirme-app
```

Python sanal ortamını oluşturun:

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source venv/bin/activate
```

Bağımlılıkları yükleyin:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
npm install
```

Ortam dosyasını oluşturun:

```powershell
Copy-Item .env.example .env
```

`.env` içinde gerekli değerleri tanımlayın:

```dotenv
OPENAI_API_KEY=your-openai-api-key-here
FLASK_ENV=development
FLASK_PORT=5000
```

API anahtarlarını commit etmeyin.

## Geliştirme

Backend'i başlatın:

```bash
python app.py
```

Frontend geliştirme sunucusunu ayrı bir terminalde başlatın:

```bash
npm run dev
```

Frontend üretim derlemesi:

```bash
npm run build
```

Varsayılan Flask adresi `http://localhost:5000` şeklindedir.

## Kullanım

1. Analiz edilecek PDF kitabı seçin.
2. Kitap türünü ve gerekli değerlendirme seçeneklerini belirleyin.
3. Analizi başlatın.
4. Bulguları ve kanıtları inceleyin.
5. Source, PDF veya Word raporunu oluşturun.

## Testler

Hermetik test paketini çalıştırmak için:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Rapor projection ve consistency regresyonları:

```bash
python -m unittest \
  tests.test_report_projection_helper \
  tests.test_canonical_entity_fragment_mismatches \
  tests.test_consistency_evidence_surface
```

Bu üç paket toplam 11 regresyon testi içerir.

## API

Temel endpointler:

- `POST /api/yukleme` — PDF yükleme ve metadata çıkarımı
- `POST /api/degerlendir` — kitap değerlendirmesi
- `POST /api/rapor-olustur` — değerlendirme sonuçlarından rapor üretimi

## Güvenlik ve kullanım notları

- `.env` ve API anahtarları repository'ye eklenmemelidir.
- Yüklenen kitapların telif ve veri işleme izinleri kullanıcı sorumluluğundadır.
- Yapay zekâ tarafından üretilen analizler uzman incelemesiyle doğrulanmalıdır.
- Runtime, debug ve kullanıcı kitap çıktıları commit edilmemelidir.

## Lisans

Bu proje proprietary yazılımdır ve tüm hakları saklıdır. Kaynak kodun erişilebilir olması; kullanma, kopyalama, değiştirme, dağıtma veya ticari olarak değerlendirme izni vermez.

Ayrıntılar için [LICENSE](LICENSE) dosyasına bakın. Lisanslama talepleri için repository sahibiyle iletişime geçin.
