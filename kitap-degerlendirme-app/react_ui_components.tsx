/**
 * Maarif Modeli Yayın Denetim Sistemi - React UI Komponentleri
 * 7 Ana Ekran (Dashboard, Yükleme, Sonuç, Bulgu, Sözlük, Profil, PDF Önizleme)
 */

import React, { useState } from 'react';

// ============================================================================
// 1. DASHBOARD - Genel Bakış
// ============================================================================
export const Dashboard: React.FC = () => {
  const [stats] = useState({
    toplamKitap: 1245,
    tamamlananAnaliz: 1098,
    yuksekRiskRapor: 147,
    sonAnalizler: [
      { kitap: 'Çocuk Macerası', profil: 'Hibrit', skor: 35, tarih: '2024-06-05' },
      { kitap: 'Tarihî Savaşlar', profil: 'Maarif/MEB', skor: 52, tarih: '2024-06-04' },
    ]
  });

  return (
    <div className="dashboard">
      <h1>📊 Maarif Modeli Dashboard</h1>
      
      {/* İstatistik Kartları */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>{stats.toplamKitap}</h3>
          <p>Toplam Kitap</p>
        </div>
        <div className="stat-card">
          <h3>{stats.tamamlananAnaliz}</h3>
          <p>Tamamlanan Analiz</p>
        </div>
        <div className="stat-card alert">
          <h3>{stats.yuksekRiskRapor}</h3>
          <p>🔴 Yüksek Risk</p>
        </div>
      </div>

      {/* Son Analizler */}
      <div className="recent-analyses">
        <h2>🕐 Son Analizler</h2>
        <table>
          <thead>
            <tr>
              <th>Kitap Adı</th>
              <th>Profil</th>
              <th>Risk Skoru</th>
              <th>Karar</th>
              <th>Tarih</th>
              <th>İşlem</th>
            </tr>
          </thead>
          <tbody>
            {stats.sonAnalizler.map((analiz, i) => (
              <tr key={i}>
                <td>{analiz.kitap}</td>
                <td>{analiz.profil}</td>
                <td>
                  <span className={`score score-${Math.ceil(analiz.skor / 20)}`}>
                    {analiz.skor}/100
                  </span>
                </td>
                <td>
                  {analiz.skor <= 20 && '✅ Uygun'}
                  {analiz.skor > 20 && analiz.skor <= 40 && '✔️ Düşük Risk'}
                  {analiz.skor > 40 && analiz.skor <= 60 && '⚠️ Dikkat'}
                  {analiz.skor > 60 && analiz.skor <= 80 && '🔴 Revizyon'}
                  {analiz.skor > 80 && '❌ Uygun Değil'}
                </td>
                <td>{analiz.tarih}</td>
                <td>
                  <button className="btn-small">Rapor İndir</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Profil Bazlı Risk Dağılımı */}
      <div className="risk-distribution">
        <h2>📈 Profil Bazlı Risk Dağılımı</h2>
        <div className="chart-placeholder">
          {/* Burada chart.js veya recharts kullanabilirsiniz */}
          <p>📊 Grafik (Çubuk Chart) - Profil bazlı ortalama riskler</p>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// 2. KİTAP YÜKLEME - Dosya Seçim ve Konfigürasyon
// ============================================================================
export const KitapYukleme: React.FC = () => {
  const [formData, setFormData] = useState<{ dosya: File | null; baslik: string; yazar: string; yayinevi: string; yasGrubu: string; profil: string; kurumProfili: string }>({
    dosya: null,
    baslik: '',
    yazar: '',
    yayinevi: '',
    yasGrubu: '9-12',
    profil: 'hibrit',
    kurumProfili: 'standart'
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFormData({ ...formData, dosya: e.target.files[0] });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Yükleme başladı:', formData);
    // API çağrısı yapılacak
  };

  return (
    <div className="kitap-yukleme">
      <h1>📤 Kitap Yükleme</h1>

      <form onSubmit={handleSubmit} className="upload-form">
        {/* Dosya Yükleme */}
        <div className="form-group">
          <label>📁 Dosya Seç (PDF/DOCX/EPUB)</label>
          <input
            type="file"
            accept=".pdf,.docx,.epub"
            onChange={handleFileChange}
            required
          />
          {formData.dosya && <p>✅ {formData.dosya.name}</p>}
        </div>

        {/* Kitap Bilgileri */}
        <div className="form-group">
          <label>Kitap Başlığı</label>
          <input
            type="text"
            value={formData.baslik}
            onChange={(e) => setFormData({ ...formData, baslik: e.target.value })}
            placeholder="Örn: Çocuk Macerası"
          />
        </div>

        <div className="form-group">
          <label>Yazar</label>
          <input
            type="text"
            value={formData.yazar}
            onChange={(e) => setFormData({ ...formData, yazar: e.target.value })}
            placeholder="Örn: Ahmet Yazar"
          />
        </div>

        <div className="form-group">
          <label>Yayınevi</label>
          <input
            type="text"
            value={formData.yayinevi}
            onChange={(e) => setFormData({ ...formData, yayinevi: e.target.value })}
            placeholder="Örn: Örnek Yayınevi"
          />
        </div>

        {/* Analiz Parametreleri */}
        <div className="form-row">
          <div className="form-group">
            <label>👧 Hedef Yaş Grubu</label>
            <select
              value={formData.yasGrubu}
              onChange={(e) => setFormData({ ...formData, yasGrubu: e.target.value })}
            >
              <option value="6-10">6-10 yaş</option>
              <option value="10-15">10-15 yaş</option>
              <option value="15-18">15-18 yaş</option>
              <option value="18+">18+ yaş</option>
            </select>
          </div>

          <div className="form-group">
            <label>📋 Analiz Profili</label>
            <select
              value={formData.profil}
              onChange={(e) => setFormData({ ...formData, profil: e.target.value })}
            >
              <option value="maarif_meb">Maarif/MEB (Sıkı)</option>
              <option value="hibrit">Hibrit (Dengeli) - Önerilen</option>
              <option value="editoryal">Editoryal (Esnek)</option>
              <option value="hassas_veli">Hassas Veli (Çok Sıkı)</option>
            </select>
          </div>

          <div className="form-group">
            <label>🏢 Kurum Profili</label>
            <select
              value={formData.kurumProfili}
              onChange={(e) => setFormData({ ...formData, kurumProfili: e.target.value })}
            >
              <option value="standart">Standart</option>
              <option value="okul">Okul</option>
              <option value="yayinevi">Yayınevi</option>
              <option value="kutuphaneBellendi">Kütüphane</option>
            </select>
          </div>
        </div>

        <button type="submit" className="btn-primary">🚀 Analizi Başlat</button>
      </form>
    </div>
  );
};

// ============================================================================
// 3. ANALİZ SONUCU - Sonuç Görüntüleme
// ============================================================================
export const AnalizSonucu: React.FC = () => {
  const [analiz] = useState({
    finalSkor: 42,
    karar: '⚠️ Dikkat Gerektirir',
    kategoriVeRiskler: [
      { kategori: 'Şiddet & Suç', bulgu: 2, risk: 3, durum: '⚠️' },
      { kategori: 'Korku & Travma', bulgu: 3, risk: 2, durum: '✔️' },
    ],
    maarifPuanlari: {
      sorgulayici: 3,
      cesaretli: 4,
      uretken: 3,
      bilge: 2,
      ahlaklı: 4,
      merhametli: 3,
      vatansever: 5,
      estetik: 2,
      iradeli: 3,
      saglikli: 2
    },
    kritikBulgular: [
      { sayfa: 12, alinti: '"Ölüm sahnesi"', kategori: 'Korku', onem: 'Orta' },
      { sayfa: 45, alinti: '"Savaş jeliği"', kategori: 'Şiddet', onem: 'Orta' }
    ]
  });

  const maarifOrt = Object.values(analiz.maarifPuanlari).reduce((a, b) => a + b) / 10;

  return (
    <div className="analiz-sonucu">
      <h1>📊 Analiz Sonuçları</h1>

      {/* Genel Risk Kartı */}
      <div className={`risk-card risk-${Math.ceil(analiz.finalSkor / 20)}`}>
        <h2>Risk Skoru</h2>
        <div className="score-display">{analiz.finalSkor}/100</div>
        <p>{analiz.karar}</p>
      </div>

      {/* Kategori Grafikleri */}
      <div className="kategoriler">
        <h2>📋 Kategori Analizi</h2>
        <table>
          <thead>
            <tr>
              <th>Kategori</th>
              <th>Bulgu</th>
              <th>Risk</th>
              <th>Durumu</th>
            </tr>
          </thead>
          <tbody>
            {analiz.kategoriVeRiskler.map((kat, i) => (
              <tr key={i}>
                <td>{kat.kategori}</td>
                <td>{kat.bulgu}</td>
                <td>{kat.risk}/5</td>
                <td>{kat.durum}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Maarif Profilleri */}
      <div className="maarif-profilleri">
        <h2>🎓 Maarif Modeli Profilleri (Ort: {maarifOrt.toFixed(1)}/5)</h2>
        <div className="profil-grid">
          {Object.entries(analiz.maarifPuanlari).map(([profil, puan]) => (
            <div key={profil} className="profil-card">
              <div className="profil-name">{profil.replace('_', ' ').toUpperCase()}</div>
              <div className="profil-score">{puan}/5</div>
              <div className="profil-bar">
                <div style={{ width: `${(puan / 5) * 100}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Kritik Bulgular */}
      <div className="kritik-bulgular">
        <h2>🔴 Kritik Bulgular ({analiz.kritikBulgular.length})</h2>
        {analiz.kritikBulgular.map((bulgu, i) => (
          <div key={i} className="bulgu-item">
            <strong>Sayfa {bulgu.sayfa}:</strong> {bulgu.alinti}
            <span className="badge">{bulgu.kategori}</span>
          </div>
        ))}
      </div>

      {/* İşlem Düğmeleri */}
      <div className="actions">
        <button className="btn-primary">📥 PDF Rapor İndir</button>
        <button className="btn-secondary">📧 E-posta Gönder</button>
        <button className="btn-secondary">🔄 Farklı Profille Analiz Et</button>
      </div>
    </div>
  );
};

// ============================================================================
// 4. BULGU İNCELEME - Detaylı İnceleme ve Onay
// ============================================================================
export const BulguInceleme: React.FC = () => {
  const [bulgu] = useState({
    sayfa: 45,
    alinti: '"Keskin bıçak kaptanın tarafından atılmıştı"',
    kategori: 'Şiddet & Suç',
    risk: 3,
    baglamAliciSozler: ['tarihî savaş', 'kurgu', 'alegerik'],
    aiYorumlama: 'Tarihî bağlamda gerçek risk taşımamaktadır.',
    incelemeNotu: 'Bağlamsal analiz yapılmış, yanlış pozitif değil',
    revizyonNotu: 'Sayfalandırma: S.45 / Yazarı: Ahmet / İnsan Denetçi: Onaylandı'
  });

  return (
    <div className="bulgu-inceleme">
      <h1>🔍 Bulgu İnceleme Sistemi</h1>

      <div className="bulgu-detay">
        <div className="header">
          <h2>Sayfa {bulgu.sayfa}: {bulgu.kategori}</h2>
          <span className={`risk-badge risk-${bulgu.risk}`}>{bulgu.risk}/5 Risk</span>
        </div>

        {/* Alıntı */}
        <div className="section">
          <h3>📖 Alıntı</h3>
          <blockquote>{bulgu.alinti}</blockquote>
        </div>

        {/* Bağlamsal Sözcükler */}
        <div className="section">
          <h3>🔗 Bağlamsal Sözcükler</h3>
          <div className="tags">
            {bulgu.baglamAliciSozler.map((tag, i) => (
              <span key={i} className="tag">{tag}</span>
            ))}
          </div>
        </div>

        {/* AI Yorumu */}
        <div className="section ai-yorum">
          <h3>🤖 AI Yorumu</h3>
          <p>{bulgu.aiYorumlama}</p>
        </div>

        {/* İnceleme Notu */}
        <div className="section">
          <h3>📝 İnceleme Notu</h3>
          <textarea defaultValue={bulgu.incelemeNotu} readOnly></textarea>
        </div>

        {/* Revizyon Notu */}
        <div className="section">
          <h3>✏️ Revizyon Notu</h3>
          <textarea defaultValue={bulgu.revizyonNotu}></textarea>
        </div>

        {/* İnsan Denetçi Onayı */}
        <div className="approval-section">
          <h3>👤 İnsan Denetçi Onayı</h3>
          <div className="checkbox-group">
            <label>
              <input type="checkbox" defaultChecked /> ✅ Doğru Tespit
            </label>
            <label>
              <input type="checkbox" /> ❌ Yanlış Pozitif
            </label>
            <label>
              <input type="checkbox" /> ⚠️ Gözden Geçirilmeli
            </label>
          </div>
        </div>

        {/* Düğmeler */}
        <div className="actions">
          <button className="btn-success">✅ Onayla ve Kaydet</button>
          <button className="btn-warning">⚠️ Gözden Geçir</button>
          <button className="btn-danger">❌ Reddет</button>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// 5. SÖZLÜK YÖNETİMİ - Terim Yönetimi
// ============================================================================
export const SozlukYonetimi: React.FC = () => {
  const [yeniTerim, setYeniTerim] = useState({
    ifade: '',
    kategori: 'zararlı_alışkanlıklar',
    riskPuani: 3,
    yasKatsayisi: 1.0,
    yanlisPozitifKurali: ''
  });

  return (
    <div className="sozluk-yonetimi">
      <h1>📚 Sözlük Yönetimi</h1>

      {/* Yeni Terim Ekleme */}
      <div className="yeni-terim-form">
        <h2>➕ Yeni Terim Ekle</h2>

        <div className="form-group">
          <label>İfade/Kelime</label>
          <input
            type="text"
            value={yeniTerim.ifade}
            onChange={(e) => setYeniTerim({ ...yeniTerim, ifade: e.target.value })}
            placeholder="Örn: sigara içmek"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Kategori</label>
            <select
              value={yeniTerim.kategori}
              onChange={(e) => setYeniTerim({ ...yeniTerim, kategori: e.target.value })}
            >
              <option value="siddet_suc">Şiddet & Suç</option>
              <option value="cinsellik_mahremiyet">Cinsellik & Mahremiyet</option>
              <option value="zararlı_alışkanlıklar">Zararlı Alışkanlıklar</option>
              <option value="kaba_dil_hakaret">Kaba Dil & Hakaret</option>
            </select>
          </div>

          <div className="form-group">
            <label>Risk Puanı (0-5)</label>
            <input
              type="range"
              min="0"
              max="5"
              value={yeniTerim.riskPuani}
              onChange={(e) => setYeniTerim({ ...yeniTerim, riskPuani: parseInt(e.target.value) })}
            />
            <span>{yeniTerim.riskPuani}/5</span>
          </div>

          <div className="form-group">
            <label>Yaş Katsayısı</label>
            <input
              type="number"
              step="0.1"
              value={yeniTerim.yasKatsayisi}
              onChange={(e) => setYeniTerim({ ...yeniTerim, yasKatsayisi: parseFloat(e.target.value) })}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Yanlış Pozitif Kuralı (Hangi bağlamda risk değildir?)</label>
          <textarea
            value={yeniTerim.yanlisPozitifKurali}
            onChange={(e) => setYeniTerim({ ...yeniTerim, yanlisPozitifKurali: e.target.value })}
            placeholder="Örn: Tarihî bağlamda, savaş kurgusu içinde..."
          ></textarea>
        </div>

        <button className="btn-primary">➕ Terimi Ekle</button>
      </div>

      {/* Mevcut Terimler */}
      <div className="terimler-listesi">
        <h2>📖 Kategoriye Göre Terimler</h2>
        <div className="terim-kategorileri">
          {['Zararlı Alışkanlıklar (600+)', 'Ayrımcılık (600+)', 'Korku (600+)'].map((kat, i) => (
            <div key={i} className="terim-kat">
              <h3>{kat}</h3>
              <p>Toplam terim sayısını görmek için genişlet</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// 6. PROFİL YÖNETİMİ - Ağırlık Ayarı
// ============================================================================
export const ProfilYonetimi: React.FC = () => {
  const [profiller, setProfiller] = useState({
    maarif_meb: {
      ad: 'Maarif/MEB',
      agirliklar: {
        siddet: 1.2,
        cinsellik: 1.4,
        zararlı_alış: 1.3,
      }
    }
  });

  return (
    <div className="profil-yonetimi">
      <h1>⚙️ Profil Yönetimi</h1>

      <div className="profiller-grid">
        {Object.entries(profiller).map(([key, profil]) => (
          <div key={key} className="profil-editor">
            <h2>{profil.ad}</h2>
            
            {Object.entries(profil.agirliklar).map(([kategori, agirlik]) => (
              <div key={kategori} className="agirlik-kontrol">
                <label>{kategori.replace('_', ' ')}</label>
                <input
                  type="range"
                  min="0.5"
                  max="2"
                  step="0.1"
                  defaultValue={agirlik as number}
                />
                <span>{agirlik}×</span>
              </div>
            ))}

            <button className="btn-success">💾 Kaydet</button>
          </div>
        ))}
      </div>

      {/* Kuruma Özel Profil Oluştur */}
      <div className="yeni-profil">
        <h2>➕ Yeni Kuruma Özel Profil</h2>
        <input type="text" placeholder="Profil Adı" />
        <button className="btn-primary">Profil Oluştur</button>
      </div>
    </div>
  );
};

// ============================================================================
// 7. PDF RAPOR ÖNİZLEMESİ
// ============================================================================
export const PDFRaporOnizlemesi: React.FC = () => {
  return (
    <div className="pdf-onizleme">
      <h1>📄 PDF Rapor Önizlemesi</h1>

      <div className="onizleme-container">
        <div className="pdf-sayfa">
          <div className="kapak">
            <h1>🏛️ Maarif Modeli Yayın Denetim Raporu</h1>
            <p>Kitap: Çocuk Macerası</p>
            <p>Yazar: Örnek Yazar</p>
            <p>Analiz Profili: Hibrit</p>
            <p>Tarih: 05.06.2024</p>
          </div>

          <div className="sayfa-2">
            <h2>1. KİTAP BİLGİLERİ</h2>
            <table>
              <tr>
                <td><strong>Başlık</strong></td>
                <td>Çocuk Macerası</td>
              </tr>
              <tr>
                <td><strong>Yazar</strong></td>
                <td>Örnek Yazar</td>
              </tr>
            </table>
          </div>

          <div className="sayfa-3">
            <h2>2. GENEL KARAR</h2>
            <p className="karar">⚠️ Dikkat Gerektirir - Risk Skoru: 42/100</p>
          </div>
        </div>

        <div className="toolbar">
          <button className="btn-primary">📥 İndir</button>
          <button className="btn-secondary">🖨️ Yazdır</button>
          <button className="btn-secondary">📧 E-posta Gönder</button>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// MAIN APP ROUTER
// ============================================================================
export const MaarifApp: React.FC = () => {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'yukleme':
        return <KitapYukleme />;
      case 'sonuc':
        return <AnalizSonucu />;
      case 'bulgu':
        return <BulguInceleme />;
      case 'sozluk':
        return <SozlukYonetimi />;
      case 'profil':
        return <ProfilYonetimi />;
      case 'pdf':
        return <PDFRaporOnizlemesi />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="maarif-app">
      {/* Navigasyon */}
      <nav className="navbar">
        <div className="logo">
          🏛️ Maarif Modeli Yayın Denetim
        </div>
        <ul className="nav-menu">
          <li>
            <button onClick={() => setCurrentPage('dashboard')} className={currentPage === 'dashboard' ? 'active' : ''}>
              📊 Dashboard
            </button>
          </li>
          <li>
            <button onClick={() => setCurrentPage('yukleme')} className={currentPage === 'yukleme' ? 'active' : ''}>
              📤 Yükleme
            </button>
          </li>
          <li>
            <button onClick={() => setCurrentPage('sonuc')} className={currentPage === 'sonuc' ? 'active' : ''}>
              📋 Sonuç
            </button>
          </li>
          <li>
            <button onClick={() => setCurrentPage('bulgu')} className={currentPage === 'bulgu' ? 'active' : ''}>
              🔍 Bulgular
            </button>
          </li>
          <li>
            <button onClick={() => setCurrentPage('sozluk')} className={currentPage === 'sozluk' ? 'active' : ''}>
              📚 Sözlük
            </button>
          </li>
          <li>
            <button onClick={() => setCurrentPage('profil')} className={currentPage === 'profil' ? 'active' : ''}>
              ⚙️ Profil
            </button>
          </li>
          <li>
            <button onClick={() => setCurrentPage('pdf')} className={currentPage === 'pdf' ? 'active' : ''}>
              📄 PDF
            </button>
          </li>
        </ul>
      </nav>

      {/* İçerik */}
      <main className="main-content">
        {renderPage()}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>© 2024 Türkiye Yüzyılı Maarif Modeli - Yayın Denetim Sistemi v2.0</p>
      </footer>
    </div>
  );
};

export default MaarifApp;
