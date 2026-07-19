/**
 * Maarif Modeli - Ana Uygulama
 * React komponentleri + API entegrasyonu
 */

import React, { useState, useEffect } from 'react';
import { Dashboard } from './react_ui_components';
import { KitapYukleme, AnalizSonucu } from './react_ui_integrated';

const API_BASE = '/api'; // Vite proxy kullan

// Inline API functions
const api = {
  async checkHealth() {
    try {
      const response = await fetch(`/health`); // Flask root endpoint
      return response.ok;
    } catch (e) {
      console.error('Health check failed:', e);
      return false;
    }
  },

  async getProfiller() {
    try {
      const response = await fetch(`${API_BASE}/profiller`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (e) {
      console.error('Profilleri getirme hatası:', e);
      throw e;
    }
  },

  async uploadFile(file: File, metadata: any) {
    const formData = new FormData();
    formData.append('pdf', file);
    formData.append('baslik', metadata.baslik || file.name);
    formData.append('yazar', metadata.yazar || '');
    formData.append('yayinevi', metadata.yayinevi || '');

    try {
      const response = await fetch(`${API_BASE}/yukleme`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (e) {
      console.error('Dosya yükleme hatası:', e);
      throw e;
    }
  },

  async analyzeFile(dosya_yolu: string, profil: string, yasGrubu: string) {
    try {
      const response = await fetch(`${API_BASE}/degerlendir`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dosya_yolu,
          profil,
          yas_grubu: yasGrubu
        })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (e) {
      console.error('Analiz hatası:', e);
      throw e;
    }
  },

  async generateReport(kitap_adi: string, analiz_sonucu: any) {
    try {
      const response = await fetch(`${API_BASE}/rapor`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          kitap_adi,
          analiz_sonucu
        })
      });

      if (!response.ok) {
        let message = `HTTP ${response.status}`;
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
          const payload = await response.json();
          const eksikler = Array.isArray(payload.eksikler) && payload.eksikler.length
            ? ` Eksikler: ${payload.eksikler.join('; ')}`
            : '';
          message = `${payload.detay || payload.hata || message}${eksikler}`;
        }
        throw new Error(message);
      }
      return await response.blob();
    } catch (e) {
      console.error('Rapor oluşturma hatası:', e);
      throw e;
    }
  },

  async getCustomKeywords() {
    const response = await fetch(`${API_BASE}/kelime-yonetimi`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  },

  async addCustomTerm(kategori: string, terim: string, tip: string) {
    const response = await fetch(`${API_BASE}/ozel-kelimeler/terim`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ kategori, terim, tip })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  },

  async deleteCustomTerm(kategori: string, terim: string, tip: string) {
    const response = await fetch(`${API_BASE}/ozel-kelimeler/terim`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ kategori, terim, tip })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  },

  async moveCustomTerm(kaynak_kategori: string, hedef_kategori: string, terim: string, tip: string) {
    const response = await fetch(`${API_BASE}/ozel-kelimeler/tasi`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ kaynak_kategori, hedef_kategori, terim, tip })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  },

  async importCustomKeywords(data: any) {
    const response = await fetch(`${API_BASE}/ozel-kelimeler`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  },

  async updateCustomTerm(payload: any) {
    const response = await fetch(`${API_BASE}/kelime-yonetimi/ozel`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  },

  async setSystemTermActive(kategori: string, terim: string, active: boolean) {
    const response = await fetch(`${API_BASE}/kelime-yonetimi/sistem/aktif`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ kategori, terim, active })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  },

  async analyzeThemeGain(dosya_yolu: string, metadata: any) {
    const response = await fetch(`${API_BASE}/tema-kazanim/analiz`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dosya_yolu,
        kitap_adi: metadata?.baslik,
        yazar: metadata?.yazar,
        yas_grubu: metadata?.yasGrubu || '',
        ozet_turu: metadata?.ozetTuru || 'standart'
      })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  },

  async saveThemeGain(analiz_sonucu: any) {
    const response = await fetch(`${API_BASE}/tema-kazanim/kaydet`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ analiz_sonucu })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  },

  async downloadThemeGainReport(analiz_sonucu: any, format: 'pdf' | 'word', ozet_turu = 'standart', reportType = 'detailed') {
    const visibleSummary = (
      analiz_sonucu?.canonical_summary ||
      ''
    );
    // TODO: Backend SummaryIR-derived summary yüzeyleri kararlı hale geldiğinde
    // frontend bu kopyalama mantığını kaldırabilir.
    const reportPayload = {
      ...(analiz_sonucu || {}),
      canonical_summary: visibleSummary,
      kitap_ozeti: visibleSummary,
      book_summary: visibleSummary,
      ozet: visibleSummary,
      summary: visibleSummary
    };
    const reportEndpoint = reportType === 'teacher'
      ? `${API_BASE}/theme-report/teacher-pdf`
      : `${API_BASE}/tema-kazanim/rapor`;
    const response = await fetch(reportEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ analiz_sonucu: reportPayload, format, ozet_turu, report_type: reportType })
    });
    if (!response.ok) {
      let message = `HTTP ${response.status}`;
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        const payload = await response.json();
        const reportErrors = payload?.tutarlilik_denetimi?.hatalar || payload?.kalite_kapisi?.hatalar || payload?.ozet_kalite_hatalari;
        const consistencyDetail = Array.isArray(reportErrors) && reportErrors.length
          ? ` ${reportErrors.join(' ')}`
          : '';
        message = `${payload.hata || payload.detay || message}${consistencyDetail}`;
      }
      throw new Error(message);
    }
    if (reportType === 'teacher') {
      const generator = response.headers.get('X-Report-Generator');
      const version = response.headers.get('X-Teacher-Report-Version');
      if (generator !== 'generate_teacher_report_pdf' || !version) {
        throw new Error('Eski backend öğretmen raporu döndürdü. Flask sunucusunu yeniden başlatın.');
      }
    }
    return await response.blob();
  }
};

type AppView = 'dashboard' | 'yukleme' | 'sonuc' | 'bulgu' | 'sozluk' | 'profil' | 'rapor' | 'ayarlar' | 'temaKazanim';

const OzelKelimeYonetimi: React.FC = () => {
  const [payload, setPayload] = useState<any>(null);
  const [kategori, setKategori] = useState('');
  const [terim, setTerim] = useState('');
  const [tip, setTip] = useState<'keywords' | 'regex'>('keywords');
  const [status, setStatus] = useState('');

  const load = async () => {
    const data = await api.getCustomKeywords();
    setPayload(data);
    if (!kategori && data.categories?.[0]?.key) setKategori(data.categories[0].key);
  };

  useEffect(() => {
    load().catch((err) => setStatus(`Özel sözlük yüklenemedi: ${err.message}`));
  }, []);

  const refreshFromResponse = (data: any) => {
    setPayload(data);
    setStatus('Kaydedildi');
  };

  const handleAdd = async () => {
    if (!kategori || !terim.trim()) return;
    const data = await api.addCustomTerm(kategori, terim.trim(), tip);
    refreshFromResponse(data);
    setTerim('');
  };

  const handleDelete = async (cat: string, value: string, itemType: string) => {
    const data = await api.deleteCustomTerm(cat, value, itemType);
    refreshFromResponse(data);
  };

  const handleMove = async (cat: string, value: string, itemType: string, target: string) => {
    if (!target || target === cat) return;
    const data = await api.moveCustomTerm(cat, target, value, itemType);
    refreshFromResponse(data);
  };

  const handleImport = async (file: File | null) => {
    if (!file) return;
    const text = await file.text();
    const parsed = JSON.parse(text);
    const data = await api.importCustomKeywords(parsed);
    refreshFromResponse(data);
  };

  const exportJson = () => {
    window.open(`${API_BASE}/ozel-kelimeler/export`, '_blank');
  };

  const categories = payload?.categories || [];
  const customData = payload?.data || {};
  const validation = payload?.validation || {};

  return (
    <section className="settings-page">
      <div className="settings-header">
        <div>
          <h2>Ayarlar · Özel Kelime Yönetimi</h2>
          <p>Kod değiştirmeden kelime, çoklu ifade ve regex kalıpları yönetin.</p>
        </div>
        <div className="settings-actions">
          <label className="btn-secondary import-button">
            İçe Aktar
            <input type="file" accept="application/json,.json" onChange={(e) => handleImport(e.target.files?.[0] || null)} />
          </label>
          <button className="btn-secondary" onClick={exportJson}>Dışa Aktar</button>
          <button className="btn-primary" onClick={() => load()}>Yenile</button>
        </div>
      </div>

      {status && <div className="info-banner">{status}</div>}
      {validation.warnings?.length > 0 && (
        <div className="warning-banner">
          {validation.warnings.join(' ')}
        </div>
      )}

      <div className="custom-keyword-form">
        <select value={kategori} onChange={(e) => setKategori(e.target.value)}>
          {categories.map((cat: any) => (
            <option key={cat.key} value={cat.key}>{cat.label}</option>
          ))}
        </select>
        <select value={tip} onChange={(e) => setTip(e.target.value as 'keywords' | 'regex')}>
          <option value="keywords">Kelime / ifade</option>
          <option value="regex">Regex</option>
        </select>
        <input
          value={terim}
          onChange={(e) => setTerim(e.target.value)}
          placeholder={tip === 'regex' ? 'Örn: silah[ıi]n[ıi]\\s+çekti' : 'Örn: alkollü araç kullandı'}
        />
        <button className="btn-primary" onClick={handleAdd}>Ekle</button>
      </div>

      <div className="custom-summary-grid">
        {categories
          .filter((cat: any) => customData[cat.key])
          .map((cat: any) => {
            const bucket = customData[cat.key] || { keywords: [], regex: [] };
            return (
              <div className="custom-category" key={cat.key}>
                <header>
                  <h3>{cat.label}</h3>
                  <span>{(bucket.keywords?.length || 0) + (bucket.regex?.length || 0)} kayıt</span>
                </header>
                <div className="term-group">
                  <strong>Kelime / ifade</strong>
                  {(bucket.keywords || []).map((item: string) => (
                    <div className="term-row" key={`kw-${cat.key}-${item}`}>
                      <span>{item}</span>
                      <select onChange={(e) => handleMove(cat.key, item, 'keywords', e.target.value)} defaultValue="">
                        <option value="">Kategori değiştir</option>
                        {categories.map((target: any) => <option key={target.key} value={target.key}>{target.label}</option>)}
                      </select>
                      <button onClick={() => handleDelete(cat.key, item, 'keywords')}>Sil</button>
                    </div>
                  ))}
                </div>
                <div className="term-group">
                  <strong>Regex</strong>
                  {(bucket.regex || []).map((item: string) => (
                    <div className="term-row" key={`rx-${cat.key}-${item}`}>
                      <code>{item}</code>
                      <select onChange={(e) => handleMove(cat.key, item, 'regex', e.target.value)} defaultValue="">
                        <option value="">Kategori değiştir</option>
                        {categories.map((target: any) => <option key={target.key} value={target.key}>{target.label}</option>)}
                      </select>
                      <button onClick={() => handleDelete(cat.key, item, 'regex')}>Sil</button>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
      </div>
    </section>
  );
};

const KelimeYonetimi: React.FC = () => {
  const [payload, setPayload] = useState<any>(null);
  const [status, setStatus] = useState('');
  const [form, setForm] = useState<any>({ kategori: '', terim: '', tip: 'keywords', active: true });
  const [editing, setEditing] = useState<any>(null);
  const [filters, setFilters] = useState<any>({
    search: '',
    kategori: '',
    risk: '',
    active: '',
    kaynak: '',
  });

  const load = async () => {
    const data = await api.getCustomKeywords();
    setPayload(data);
    if (!form.kategori && data.categories?.[0]?.key) {
      setForm((current: any) => ({ ...current, kategori: data.categories[0].key }));
    }
  };

  useEffect(() => {
    load().catch((err) => setStatus(`Kelime listesi yüklenemedi: ${err.message}`));
  }, []);

  const categories = payload?.categories || [];
  const records = payload?.records || [];
  const validation = payload?.validation || {};

  const filtered = records.filter((record: any) => {
    const text = `${record.term} ${record.kategori_adi} ${record.kaynak}`.toLowerCase();
    if (filters.search && !text.includes(filters.search.toLowerCase())) return false;
    if (filters.kategori && record.kategori !== filters.kategori) return false;
    if (filters.risk !== '' && String(record.risk_puani) !== String(filters.risk)) return false;
    if (filters.active !== '' && String(record.active) !== filters.active) return false;
    if (filters.kaynak && record.kaynak !== filters.kaynak) return false;
    return true;
  });

  const systemRecords = filtered.filter((record: any) => record.kaynak === 'Sistem');
  const customRecords = filtered.filter((record: any) => record.kaynak === 'Özel');

  const refresh = (data: any, message = 'Kaydedildi') => {
    setPayload(data);
    setStatus(message);
    setEditing(null);
  };

  const submitCustom = async () => {
    if (!form.kategori || !form.terim.trim()) return;
    const data = editing
      ? await api.updateCustomTerm({
          kategori: form.kategori,
          terim: form.terim.trim(),
          tip: form.tip,
          active: form.active,
          eski_kategori: editing.kategori,
          eski_terim: editing.term,
          eski_tip: editing.tip,
        })
      : await api.addCustomTerm(form.kategori, form.terim.trim(), form.tip);
    refresh(data);
    setForm({ ...form, terim: '', active: true });
  };

  const editCustom = (record: any) => {
    setEditing(record);
    setForm({
      kategori: record.kategori,
      terim: record.term,
      tip: record.tip || (record.risk_turu === 'Regex' ? 'regex' : 'keywords'),
      active: record.active,
    });
  };

  const toggleRecord = async (record: any) => {
    const active = !record.active;
    const data = record.kaynak === 'Sistem'
      ? await api.setSystemTermActive(record.kategori, record.term, active)
      : await api.updateCustomTerm({
          kategori: record.kategori,
          terim: record.term,
          tip: record.tip,
          active,
          eski_kategori: record.kategori,
          eski_terim: record.term,
          eski_tip: record.tip,
        });
    refresh(data, active ? 'Aktif edildi' : 'Pasifleştirildi');
  };

  const deleteCustom = async (record: any) => {
    const data = await api.deleteCustomTerm(record.kategori, record.term, record.tip);
    refresh(data, 'Silindi');
  };

  const handleImport = async (file: File | null) => {
    if (!file) return;
    const parsed = JSON.parse(await file.text());
    const data = await api.importCustomKeywords(parsed);
    refresh(data, 'İçe aktarıldı');
  };

  const renderTable = (title: string, rows: any[], source: 'Sistem' | 'Özel') => (
    <section className="keyword-section">
      <header>
        <h3>{title}</h3>
        <span>{rows.length} kayıt</span>
      </header>
      <div className="keyword-table-wrap">
        <table className="keyword-table">
          <thead>
            <tr>
              <th>Kelime / ifade</th>
              <th>Kategori</th>
              <th>Risk türü</th>
              <th>Risk</th>
              <th>Bağlam kuralı</th>
              <th>Durum</th>
              <th>Kaynak</th>
              <th>Son güncelleme</th>
              <th>İşlem</th>
            </tr>
          </thead>
          <tbody>
            {rows.slice(0, 700).map((record: any) => (
              <tr key={record.id}>
                <td>{record.term}</td>
                <td>{record.kategori_adi}</td>
                <td>{record.risk_turu}</td>
                <td>{record.risk_puani}/5</td>
                <td>{record.baglam_kurali}</td>
                <td>{record.active ? 'Aktif' : 'Pasif'}</td>
                <td>{record.kaynak}</td>
                <td>{record.updated_at || '-'}</td>
                <td className="keyword-actions">
                  <button onClick={() => toggleRecord(record)}>{record.active ? 'Pasifleştir' : 'Aktif yap'}</button>
                  {source === 'Özel' && <button onClick={() => editCustom(record)}>Düzenle</button>}
                  {source === 'Özel' && <button onClick={() => deleteCustom(record)}>Sil</button>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {rows.length > 700 && <p className="table-note">Performans için ilk 700 kayıt gösteriliyor; arama/filtre ile daraltabilirsiniz.</p>}
    </section>
  );

  return (
    <section className="settings-page keyword-management">
      <div className="settings-header">
        <div>
          <h2>Ayarlar · Kelime Yönetimi</h2>
          <p>Sistem kelimelerini görüntüleyin, pasifleştirin ve özel kelimeleri yönetin.</p>
        </div>
        <div className="settings-actions">
          <label className="btn-secondary import-button">
            İçe Aktar
            <input type="file" accept="application/json,.json" onChange={(e) => handleImport(e.target.files?.[0] || null)} />
          </label>
          <button className="btn-secondary" onClick={() => window.open(`${API_BASE}/ozel-kelimeler/export`, '_blank')}>Dışa Aktar</button>
          <button className="btn-secondary" onClick={() => window.open(`${API_BASE}/kelime-yonetimi/export-excel`, '_blank')}>Excel'e Aktar</button>
          <button className="btn-primary" onClick={load}>Yenile</button>
        </div>
      </div>

      {status && <div className="info-banner">{status}</div>}
      {validation.warnings?.length > 0 && <div className="warning-banner">{validation.warnings.join(' ')}</div>}

      <div className="custom-keyword-form">
        <select value={form.kategori} onChange={(e) => setForm({ ...form, kategori: e.target.value })}>
          {categories.map((cat: any) => <option key={cat.key} value={cat.key}>{cat.label}</option>)}
        </select>
        <select value={form.tip} onChange={(e) => setForm({ ...form, tip: e.target.value })}>
          <option value="keywords">Kelime / ifade</option>
          <option value="regex">Regex</option>
        </select>
        <input value={form.terim} onChange={(e) => setForm({ ...form, terim: e.target.value })} placeholder="Kelime, ifade veya regex" />
        <label className="inline-toggle">
          <input type="checkbox" checked={form.active} onChange={(e) => setForm({ ...form, active: e.target.checked })} />
          Aktif
        </label>
        <button className="btn-primary" onClick={submitCustom}>{editing ? 'Güncelle' : 'Ekle'}</button>
        {editing && <button className="btn-secondary" onClick={() => { setEditing(null); setForm({ ...form, terim: '', active: true }); }}>Vazgeç</button>}
      </div>

      <div className="keyword-filters">
        <input placeholder="Kelime ara" value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} />
        <select value={filters.kategori} onChange={(e) => setFilters({ ...filters, kategori: e.target.value })}>
          <option value="">Tüm kategoriler</option>
          {categories.map((cat: any) => <option key={cat.key} value={cat.key}>{cat.label}</option>)}
        </select>
        <select value={filters.risk} onChange={(e) => setFilters({ ...filters, risk: e.target.value })}>
          <option value="">Tüm risk puanları</option>
          {[0, 1, 2, 3, 4, 5].map((risk) => <option key={risk} value={risk}>{risk}/5</option>)}
        </select>
        <select value={filters.active} onChange={(e) => setFilters({ ...filters, active: e.target.value })}>
          <option value="">Aktif + pasif</option>
          <option value="true">Aktif</option>
          <option value="false">Pasif</option>
        </select>
        <select value={filters.kaynak} onChange={(e) => setFilters({ ...filters, kaynak: e.target.value })}>
          <option value="">Sistem + Özel</option>
          <option value="Sistem">Sistem</option>
          <option value="Özel">Özel</option>
        </select>
      </div>

      {renderTable('1. Sistem Kelimeleri', systemRecords, 'Sistem')}
      {renderTable('2. Özel Eklenen Kelimeler', customRecords, 'Özel')}
    </section>
  );
};

const TemaKazanimAnalizi: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [metadata, setMetadata] = useState<any>({ baslik: '', yazar: '', yasGrubu: '9-12', ozetTuru: 'standart' });
  const [result, setResult] = useState<any>(null);
  const [loadingLocal, setLoadingLocal] = useState(false);
  const [reportLoading, setReportLoading] = useState<'pdf' | 'word' | 'teacher' | null>(null);
  const [message, setMessage] = useState('');

  const runAnalysis = async () => {
    if (!file) {
      setMessage('Lütfen PDF dosyası seçin.');
      return;
    }
    setLoadingLocal(true);
    setMessage('');
    try {
      const upload = await api.uploadFile(file, metadata);
      const analysis = await api.analyzeThemeGain(upload.dosya_yolu, metadata);
      setResult(analysis.analiz_sonucu);
      setMessage('Tema ve kazanım analizi tamamlandı.');
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Analiz hatası');
    } finally {
      setLoadingLocal(false);
    }
  };

  const save = async () => {
    if (!result) return;
    const saved = await api.saveThemeGain(result);
    setMessage(`Analiz kaydedildi. Kayıt ID: ${saved.id}`);
  };

  const download = async (format: 'pdf' | 'word') => {
    if (!result || reportLoading) return;
    setReportLoading(format);
    setMessage(format === 'pdf' ? 'PDF rapor hazÄ±rlanÄ±yor...' : 'Word rapor hazÄ±rlanÄ±yor...');
    try {
      const blob = await api.downloadThemeGainReport(result, format, metadata.ozetTuru || result.ozet_turu || 'standart');
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${result.kitap_adi || 'tema_kazanim'}_tema_kazanim.${format === 'pdf' ? 'pdf' : 'doc'}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setMessage(format === 'pdf' ? 'PDF rapor indirildi.' : 'Word rapor indirildi.');
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Rapor olusturma hatasi');
    } finally {
      setReportLoading(null);
    }
  };

  const downloadTeacherReport = async () => {
    if (!result || reportLoading) return;
    setReportLoading('teacher');
    setMessage('Ogretmen raporu hazirlaniyor...');
    try {
      const blob = await api.downloadThemeGainReport(
        result,
        'pdf',
        metadata.ozetTuru || result.ozet_turu || 'standart',
        'teacher'
      );
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${result.kitap_adi || 'tema_kazanim'}_ogretmen_raporu.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setMessage('Ogretmen raporu indirildi.');
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Ogretmen raporu olusturma hatasi');
    } finally {
      setReportLoading(null);
    }
  };

  const list = (items: any[]) => (
    <ul>{(items || []).map((item, index) => <li key={index}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>)}</ul>
  );

  const themeRankingList = (items: any[]) => {
    if (!items || items.length === 0) {
      return <p className="muted-text">Yeterli tema kanıtı bulunamadı.</p>;
    }
    return (
      <ol className="theme-ranking-list">
        {items.slice(0, 3).map((item: any, index: number) => (
          <li key={`${item.ad || index}-${index}`}>
            <strong>{item.ad}</strong>
            <span>Tema Gücü: {item.tema_gucu ?? 0}</span>
            <span>Kanıt: {item.kanit_sayisi ?? 0}</span>
            <span>Farklı Sayfa: {item.farkli_sayfa_sayisi ?? 0}</span>
            <span>Güven: {item.guven_skoru ?? 0}</span>
          </li>
        ))}
      </ol>
    );
  };

  const evidenceList = (items: any[], labelKey = 'ad') => {
    if (!items || items.length === 0) {
      return <p className="muted-text">Yeterli metin kanıtı bulunamadı.</p>;
    }
    return (
      <div className="evidence-grid">
        {items.map((item: any, index: number) => (
          <article className="evidence-card" key={`${item[labelKey] || item.ad || index}-${index}`}>
            <header>
              <h4>{item[labelKey] || item.ad}</h4>
              <span>Güven: {item.guven_skoru ?? 0}</span>
            </header>
            <div className="evidence-meta">
              <span>Puan: {item.puan || item.eslesme_puani || 0}/5</span>
              <span>Kanıt Sayısı: {item.kanit_sayisi ?? (item.kanitlar || []).length}</span>
              <span>Farklı Sayfa Sayısı: {item.farkli_sayfa_sayisi ?? 0}</span>
              <span>Tema Gücü: {item.tema_gucu ?? 0}</span>
              <span>Güven Skoru: {item.guven_skoru ?? 0}</span>
            </div>
            {item.gerekce && <p>{item.gerekce}</p>}
            <ul>
              {(item.kanitlar || []).map((evidence: any, evIndex: number) => (
                <li key={evIndex}>
                  <strong>Sayfa {evidence.sayfa || '?'}:</strong> {evidence.alinti}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    );
  };

  return (
    <section className="theme-gain-page">
      <div className="settings-header">
        <div>
          <h2>Tema ve Kazanım Analizi</h2>
          <p>Bu bölüm sakıncalı içerik puanı üretmez; kitabın tema, değer ve eğitimsel katkı yönünü analiz eder.</p>
        </div>
      </div>

      <div className="theme-upload-panel">
        <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <input placeholder="Kitap adı" value={metadata.baslik} onChange={(e) => setMetadata({ ...metadata, baslik: e.target.value })} />
        <input placeholder="Yazar" value={metadata.yazar} onChange={(e) => setMetadata({ ...metadata, yazar: e.target.value })} />
        <select value={metadata.yasGrubu} onChange={(e) => setMetadata({ ...metadata, yasGrubu: e.target.value })}>
          <option value="6-8">6-8</option>
          <option value="9-12">9-12</option>
          <option value="12-15">12-15</option>
          <option value="15+">15+</option>
        </select>
        <select value={metadata.ozetTuru} onChange={(e) => setMetadata({ ...metadata, ozetTuru: e.target.value })}>
          <option value="kisa">Kısa Özet</option>
          <option value="standart">Standart Özet</option>
          <option value="ayrintili">Ayrıntılı Özet</option>
        </select>
        <button className="btn-primary" onClick={runAnalysis} disabled={loadingLocal}>{loadingLocal ? 'Analiz ediliyor...' : 'Analiz Et'}</button>
      </div>

      {message && <div className="info-banner">{message}</div>}

      {result && (
        <div className="theme-result">
          <div className="theme-actions">
            <button className="btn-primary" onClick={save} disabled={Boolean(reportLoading)}>Kaydet</button>
            <button className="btn-secondary" onClick={() => download('pdf')} disabled={Boolean(reportLoading)}>
              {reportLoading === 'pdf' ? 'PDF hazÄ±rlanÄ±yor...' : 'PDF Rapor'}
            </button>
            <button className="btn-secondary" onClick={() => download('word')} disabled={Boolean(reportLoading)}>
              {reportLoading === 'word' ? 'Word hazÄ±rlanÄ±yor...' : 'Word Rapor'}
            </button>
            <button className="btn-secondary" onClick={downloadTeacherReport} disabled={Boolean(reportLoading)}>
              {reportLoading === 'teacher' ? 'Ogretmen raporu hazirlaniyor...' : 'Ogretmen Raporu'}
            </button>
          </div>
          <section>
            <h3>Kitap Özeti</h3>
            <p>{result.canonical_summary || 'Kitap özeti üretilemedi.'}</p>
            <div className="evidence-meta">
              <span>Özet Güven Skoru: {result.ozet_guven_skoru ?? 0}</span>
              <span>Özet Somutluk Skoru: {result.ozet_somutluk_skoru ?? 0}</span>
              <span>Özet Uzunluğu: {result.ozet_uzunlugu ?? 0} kelime</span>
              <span>Özet Kanıtlarının Yayıldığı Sayfa Sayısı: {result.ozetin_dayandigi_sayfa_sayisi ?? 0}</span>
            </div>
            {result.olay_akisi?.length ? (
              <>
                <h4>Olay Akışı</h4>
                <ul>
                  {result.olay_akisi.slice(0, 6).map((item: any, index: number) => (
                    <li key={`${item.baslik || index}-${index}`}>
                      <strong>{item.baslik}</strong>: {item.metin}
                    </li>
                  ))}
                </ul>
              </>
            ) : null}
            <h4>Ana Karakterler</h4>
            {result.ana_karakterler?.length ? (
              <ul>
                {result.ana_karakterler.map((character: any, index: number) => (
                  <li key={`${character.ad || index}-${index}`}>
                    <strong>{character.karakter_adi || character.ad}</strong>
                    {` - Rolü: ${character.rolu || character.kategori || 'yan'}`}
                    {` - Metindeki Görünme Sayısı: ${character.metindeki_gorunme_sayisi ?? character.gecis_sayisi ?? 0}`}
                    {` - Geçtiği Sayfa Sayısı: ${character.gectigi_sayfa_sayisi ?? character.sayfa_sayisi ?? 0}`}
                    {character.guven_skoru !== undefined ? ` - Güven: ${character.guven_skoru}` : ''}
                    {(character.karakter_ozeti || character.rol) ? `: ${character.karakter_ozeti || character.rol}` : ''}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted-text">Metinden yeterli karakter adı çıkarılamadı.</p>
            )}
          </section>
          <section>
            <h3>Bu Kitabın İlk 3 Baskın Teması</h3>
            {themeRankingList(result.ilk_uc_baskin_tema)}
          </section>
          <section>
            <h3>Güçlü Temalar</h3>
            {themeRankingList(result.guclu_temalar)}
          </section>
          <section>
            <h3>Destekleyici Temalar</h3>
            {themeRankingList(result.destekleyici_temalar)}
          </section>
          <section>
            <h3>Kitabın Ana Teması</h3>
            <p>{result.ana_tema} {result.ana_tema_guven_skoru !== undefined ? `(Güven: ${result.ana_tema_guven_skoru})` : ''}</p>
          </section>
          <section>
            <h3>Tema Analizi ve Kanıtlar</h3>
            {evidenceList(result.tema_analizi)}
          </section>
          <section>
            <h3>Tema Çıkarım Gerekçesi</h3>
            {list(result.tema_cikarim_gerekcesi)}
          </section>
          <section>
            <h3>Temel Mesajlar</h3>
            {list(result.temel_mesajlar)}
          </section>
          <section>
            <h3>Öğrenci Kazanımları ve Kanıtlar</h3>
            {evidenceList(result.kazanim_analizi)}
          </section>
          <section>
            <h3>Maarif Modeli ile İlişki</h3>
            {evidenceList(result.maarif_profili_eslesmeleri, 'profil')}
          </section>
          <section>
            <h3>Değerler Eğitimi Karşılığı ve Kanıtlar</h3>
            {evidenceList(result.deger_analizi)}
          </section>
          <section>
            <h3>Ders İçi Kullanım Önerileri</h3>
            {list(result.ders_ici_kullanim_onerileri)}
          </section>
          <section>
            <h3>Öğretmen Notu</h3>
            <p>{result.ogretmen_notu}</p>
          </section>
        </div>
      )}
    </section>
  );
};

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<AppView>('dashboard');
  const [apiReady, setApiReady] = useState(false);
  const [profiller, setProfiller] = useState<any[]>([]);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // API'nin kullanılabilir olup olmadığını kontrol et
  useEffect(() => {
    const checkAPI = async () => {
      try {
        const isHealthy = await api.checkHealth();
        if (isHealthy) {
          setApiReady(true);
          // Profilleri yükle
          const data = await api.getProfiller();
          setProfiller(data);
        }
      } catch (err) {
        console.error('API connection failed:', err);
        setError('API sunucusu bağlanılamadı. Lütfen Flask sunucusunun çalıştığını kontrol edin.');
      }
    };

    checkAPI();
  }, []);

  // Dosya yükle ve analiz et
  const handleFileUpload = async (file: File, metadata: any) => {
    setLoading(true);
    setError(null);

    try {
      // 1. Dosyayı yükle
      console.log('📤 Dosya yükleniyor...');
      const uploadResponse = await api.uploadFile(file, metadata);
      console.log('✅ Dosya yüklendi:', uploadResponse);

      // 2. Analiz yap
      console.log('🔍 Analiz yapılıyor...');
      const analysisData = await api.analyzeFile(
        uploadResponse.dosya_yolu,
        metadata.profil || 'hibrit',
        metadata.yasGrubu || '9-12'
      );
      console.log('✅ Analiz tamamlandı:', analysisData);

      // Sonuçları kaydet
      setAnalysisResult({
        dosya: uploadResponse.dosya_yolu,
        metadata,
        ...analysisData
      });

      // Sonuç ekranına geç
      setCurrentView('sonuc');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Bilinmeyen hata';
      setError(`Hata: ${errorMsg}`);
      console.error('Upload/Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Rapor indir
  const handleDownloadReport = async () => {
    if (!analysisResult) return;

    setLoading(true);
    try {
      const blob = await api.generateReport(
        analysisResult.dosya,
        analysisResult.analiz_sonucu
      );

      // Blob'u indir
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${analysisResult.dosya}_rapor.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Bilinmeyen hata';
      setError(`Rapor indirme hatası: ${errorMsg}`);
      console.error('Report download error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* HEADER */}
      <header className="app-header">
        <div className="header-content">
          <h1>📚 Maarif Modeli - Yayın Denetim Sistemi</h1>
          <nav className="app-nav">
            <button
              onClick={() => setCurrentView('dashboard')}
              className={currentView === 'dashboard' ? 'nav-active' : ''}
            >
              Dashboard
            </button>
            <button
              onClick={() => setCurrentView('yukleme')}
              className={currentView === 'yukleme' ? 'nav-active' : ''}
            >
              Yükle
            </button>
            <button
              onClick={() => setCurrentView('temaKazanim')}
              className={currentView === 'temaKazanim' ? 'nav-active' : ''}
            >
              Tema ve Kazanım Analizi
            </button>
            {analysisResult && (
              <button
                onClick={() => setCurrentView('sonuc')}
                className={currentView === 'sonuc' ? 'nav-active' : ''}
              >
                Sonuçlar
              </button>
            )}
            <button
              onClick={() => setCurrentView('ayarlar')}
              className={currentView === 'ayarlar' ? 'nav-active' : ''}
            >
              Ayarlar
            </button>
          </nav>
          <div className="api-status">
            {apiReady ? (
              <span className="status-ok">🟢 API Bağlı</span>
            ) : (
              <span className="status-error">🔴 API Bağlantısı Yok</span>
            )}
          </div>
        </div>
      </header>

      {/* ERROR BANNER */}
      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* LOADING INDICATOR */}
      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>İşlem devam ediyor...</p>
        </div>
      )}

      {/* MAIN CONTENT */}
      <main className="app-main">
        {currentView === 'dashboard' && <Dashboard />}
        {currentView === 'yukleme' && (
          <KitapYukleme
            onUpload={handleFileUpload}
            loading={loading}
            profiller={profiller}
          />
        )}
        {currentView === 'temaKazanim' && <TemaKazanimAnalizi />}
        {currentView === 'sonuc' && analysisResult && (
          <AnalizSonucu
            result={analysisResult}
            onDownloadReport={handleDownloadReport}
            loading={loading}
          />
        )}
        {currentView === 'ayarlar' && <KelimeYonetimi />}
      </main>

      {/* FOOTER */}
      <footer className="app-footer">
        <p>© 2024 Maarif Modeli - Eğitim Denetim Sistemi | v1.0</p>
      </footer>
    </div>
  );
};

export default App;
