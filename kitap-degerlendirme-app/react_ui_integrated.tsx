/**
 * Maarif Modeli - React Komponentleri (API Entegre)
 * KitapYukleme ve AnalizSonucu komponentleri App'e bağlı
 */

import React, { useState } from 'react';

// ============================================================================
// KİTAP YÜKLEME - Dosya Seçim ve Konfigürasyon (API Entegre)
// ============================================================================
export const KitapYukleme: React.FC<{
  onUpload: (file: File, metadata: any) => void;
  loading: boolean;
  profiller: any[];
}> = ({ onUpload, loading, profiller }) => {
  const [formData, setFormData] = useState({
    dosya: null as File | null,
    baslik: '',
    yazar: '',
    yayinevi: '',
    yasGrubu: '9-12',
    profil: 'hibrit',
  });

  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFormData({ ...formData, dosya: e.target.files[0] });
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files) {
      setFormData({ ...formData, dosya: e.dataTransfer.files[0] });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.dosya) {
      alert('Lütfen bir dosya seçin');
      return;
    }
    onUpload(formData.dosya, {
      baslik: formData.baslik || formData.dosya.name,
      yazar: formData.yazar,
      yayinevi: formData.yayinevi,
      yasGrubu: formData.yasGrubu,
      profil: formData.profil,
    });
  };

  return (
    <div className="kitap-yukleme">
      <h1>📤 Kitap Yükleme</h1>

      <form onSubmit={handleSubmit} className="upload-form">
        {/* Dosya Yükleme - Drag & Drop */}
        <div className="form-group">
          <label>📁 Dosya Seç (PDF/DOCX/EPUB)</label>
          <div
            className={`file-upload-area ${dragActive ? 'dragover' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <p>📎 Dosyayı buraya sürükleyin veya tıklayın</p>
            <input
              type="file"
              accept=".pdf,.docx,.epub"
              onChange={handleFileChange}
              style={{ display: 'none' }}
              id="file-input"
              disabled={loading}
            />
            <label htmlFor="file-input" style={{ cursor: 'pointer' }}>
              Dosya Seçin
            </label>
          </div>
          {formData.dosya && (
            <div className="file-list">
              <li>
                <span>✅ {formData.dosya.name}</span>
                <span>{(formData.dosya.size / 1024).toFixed(2)} KB</span>
              </li>
            </div>
          )}
        </div>

        {/* Kitap Bilgileri */}
        <div className="form-group">
          <label>Kitap Başlığı (İsteğe bağlı)</label>
          <input
            type="text"
            value={formData.baslik}
            onChange={(e) => setFormData({ ...formData, baslik: e.target.value })}
            placeholder="Örn: Çocuk Macerası"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label>Yazar (İsteğe bağlı)</label>
          <input
            type="text"
            value={formData.yazar}
            onChange={(e) => setFormData({ ...formData, yazar: e.target.value })}
            placeholder="Örn: Ahmet Yazar"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label>Yayınevi (İsteğe bağlı)</label>
          <input
            type="text"
            value={formData.yayinevi}
            onChange={(e) => setFormData({ ...formData, yayinevi: e.target.value })}
            placeholder="Örn: Örnek Yayınevi"
            disabled={loading}
          />
        </div>

        {/* Analiz Parametreleri */}
        <div className="form-row">
          <div className="form-group">
            <label>👧 Hedef Yaş Grubu</label>
            <select
              value={formData.yasGrubu}
              onChange={(e) => setFormData({ ...formData, yasGrubu: e.target.value })}
              disabled={loading}
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
              disabled={loading}
            >
              <option value="maarif_meb">Maarif/MEB (Sıkı)</option>
              <option value="hibrit">Hibrit (Dengeli) - Önerilen</option>
              <option value="editoryal">Editoryal (Esnek)</option>
              <option value="hassas_veli">Hassas Veli (Çok Sıkı)</option>
            </select>
          </div>
        </div>

        {/* Gönder Butonu */}
        <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !formData.dosya}
          >
            {loading ? '⏳ Yükleniyor...' : '🚀 Analiz Et'}
          </button>
        </div>
      </form>
    </div>
  );
};

// ============================================================================
// ANALİZ SONUÇLARI (API Entegre)
// ============================================================================
export const AnalizSonucu: React.FC<{
  result: any;
  onDownloadReport: () => void;
  loading: boolean;
}> = ({ result, onDownloadReport, loading }) => {
  const analiz = result.analiz_sonucu || result;
  const skor = Number(analiz.final_skor ?? 0);
  const karar = analiz.karar || { seviye: '?', simge: '❓', renk: 'gray' };
  const kategoriler = analiz.kategori_bulgulari || {};
  const maarifProfiller = analiz.maarif_profilleri || {};
  const profil = result.metadata?.profil || analiz.profil || 'Hibrit';
  const yasGrubu = result.metadata?.yasGrubu || analiz.yas_grubu || 'Belirtilmedi';

  // Risk seviyesini belirle
  const getRiskLevel = () => {
    if (skor <= 20) return { class: 'uygun', text: '✅ Uygun' };
    if (skor <= 40) return { class: 'dikkat', text: '✔️ Düşük Risk' };
    if (skor <= 60) return { class: 'dikkat', text: '⚠️ Dikkat' };
    if (skor <= 80) return { class: 'revizyon', text: '🔴 Revizyon' };
    return { class: 'revizyon', text: '❌ Uygun Değil' };
  };

  const riskLevel = getRiskLevel();
  const skorYuvarlanmis = Math.round(skor);

  return (
    <div className="analiz-sonucu">
      <h1>📊 Analiz Sonuçları</h1>

      {/* BAŞLIK */}
      <div className="result-header">
        <div className="score-display">
          <div
            className="score-circle"
            aria-label={`Risk analiz puanı ${skorYuvarlanmis} / 100`}
          >
            <div className="score-circle-content">
              <span className="score-value">{skorYuvarlanmis}</span>
              <span className="score-total">/100</span>
              <span className="score-label">Risk Analiz Puanı</span>
            </div>
          </div>
          <div className="score-info">
            <h2>{result.dosya}</h2>
            <div className={`decision-badge ${riskLevel.class}`}>
              {riskLevel.text}
            </div>
            <div className="risk-score-summary">
              <strong>Kitap Risk Analiz Puanı</strong>
              <span>{skorYuvarlanmis}/100</span>
              <small>
                {skorYuvarlanmis === 0
                  ? 'Risk puanı oluşturan problemli bağlam tespit edilmedi.'
                  : 'Puan yükseldikçe editoryal kontrol ihtiyacı artar.'}
              </small>
            </div>
            <p>
              <strong>Profil:</strong> {profil}
            </p>
            <p>
              <strong>Yaş Grubu:</strong> {yasGrubu}
            </p>
            <button
              className="btn-primary"
              onClick={onDownloadReport}
              disabled={loading}
              style={{ marginTop: '1rem' }}
            >
              {loading ? '⏳ Hazırlanıyor...' : '📥 Rapor İndir (PDF)'}
            </button>
          </div>
        </div>
      </div>

      {/* KATEGORİ BULGULARI */}
      {Object.keys(kategoriler).length > 0 && (
        <div className="kategori-table">
          <h2>📋 Kategori Bulguları</h2>
          <table>
            <thead>
              <tr>
                <th>Kategori</th>
                <th>Bulgu Sayısı</th>
                <th>Risk Seviyesi</th>
                <th>Yüzde</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(kategoriler).map(([kategori, data]: [string, any]) => {
                const puan = data.puan || 0;
                const yuzde = (puan / 5) * 100;
                return (
                  <tr key={kategori}>
                    <td className="kategori-name">{kategori}</td>
                    <td>{data.toplam_bulgu || 0}</td>
                    <td>
                      <div className="risk-bar">
                        <div
                          className="risk-bar-fill"
                          style={{ width: `${yuzde}%` }}
                        ></div>
                      </div>
                    </td>
                    <td>{yuzde.toFixed(0)}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* MAARIF PROFİLLERİ */}
      {Object.keys(maarifProfiller).length > 0 && (
        <div>
          <h2>🎓 Maarif Profilleri</h2>
          <div className="maarif-grid">
            {Object.entries(maarifProfiller)
              .sort(([, a]: [string, any], [, b]: [string, any]) => {
                const puanA = typeof a === 'object' ? Number(a.puan ?? a.skor ?? 0) : Number(a ?? 0);
                const puanB = typeof b === 'object' ? Number(b.puan ?? b.skor ?? 0) : Number(b ?? 0);
                return puanB - puanA;
              })
              .slice(0, 5)
              .map(([profil, veri]: [string, any]) => {
                const profilAdi = typeof veri === 'object'
                  ? (veri.profil_adi || profil)
                  : profil;
                const puan = typeof veri === 'object'
                  ? Number(veri.puan ?? veri.skor ?? 0)
                  : Number(veri ?? 0);
                const bulguSayisi = typeof veri === 'object'
                  ? Number(veri.bulgu_sayisi ?? 0)
                  : 0;

                return (
                  <div key={profil} className="profil-card">
                    <h4>✨ {profilAdi}</h4>
                    <div className="profil-score">{puan}/5</div>
                    <div className="profil-desc">
                      {bulguSayisi > 0
                        ? `${bulguSayisi} bulgu ile destekleniyor.`
                        : 'Belirgin bulgu tespit edilmedi.'}
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      )}

      {/* KRİTİK BULGULAR */}
      {skor >= 60 && (
        <div className="kritik-bulgular">
          <h3>⚠️ Kritik Bulgular</h3>
          <ul className="bulgu-list">
            {Object.entries(kategoriler)
              .filter(([, data]: [string, any]) => data.puan >= 3)
              .map(([kategori, data]: [string, any]) => (
                <li key={kategori}>
                  <strong>{kategori}</strong> kategorisinde {data.toplam_bulgu} bulgu
                  tespit edildi.
                </li>
              ))}
          </ul>
        </div>
      )}

      {/* İŞLEMLER */}
      <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
        <button className="btn-secondary">📝 Detaylı Rapor</button>
        <button className="btn-secondary">🔄 Başka Profille Analiz Et</button>
        <button className="btn-secondary">💾 Analizi Kaydet</button>
      </div>
    </div>
  );
};
