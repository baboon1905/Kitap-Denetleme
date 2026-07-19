/**
 * Maarif API İstemcisi
 * React komponentlerinden API'ye istekleri yönetir
 */

const API_BASE = 'http://127.0.0.1:5000/api';

async function fetchWithTimeout(url, options = {}, timeoutMs = 120000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } catch (error) {
    if (error && error.name === 'AbortError') {
      throw new Error('İstek zaman aşımına uğradı. Analiz beklenenden uzun sürdü; lütfen daha küçük bir PDF deneyin veya sunucu loglarını kontrol edin.');
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

// Sağlık kontrolü
export async function checkHealth() {
  try {
    const response = await fetchWithTimeout(`${API_BASE.replace('/api', '')}/health`, {}, 10000);
    return response.ok;
  } catch (e) {
    console.error('Health check failed:', e);
    return false;
  }
}

// Profilleri getir
export async function getProfiller() {
  try {
    const response = await fetchWithTimeout(`${API_BASE}/profiller`, {}, 20000);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (e) {
    console.error('Profilleri getirme hatası:', e);
    throw e;
  }
}

// Dosya yükle
export async function uploadFile(file, metadata) {
  const formData = new FormData();
  formData.append('pdf', file);
  formData.append('baslik', metadata.baslik || file.name);
  formData.append('yazar', metadata.yazar || '');
  formData.append('yayinevi', metadata.yayinevi || '');

  try {
    const response = await fetchWithTimeout(`${API_BASE}/yukleme`, {
      method: 'POST',
      body: formData
    }, 120000);

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (e) {
    console.error('Dosya yükleme hatası:', e);
    throw e;
  }
}

// Analiz yap
export async function analyzeFile(dosya_yolu, profil, yasGrubu) {
  try {
    const response = await fetchWithTimeout(`${API_BASE}/degerlendir`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dosya_yolu,
        profil,
        yas_grubu: yasGrubu
      })
    }, 180000);

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (e) {
    console.error('Analiz hatası:', e);
    throw e;
  }
}

// PDF Rapor oluştur
export async function generateReport(kitap_adi, analiz_sonucu) {
  try {
    const response = await fetch(`${API_BASE}/rapor`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        kitap_adi,
        analiz_sonucu
      })
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.blob();
  } catch (e) {
    console.error('Rapor oluşturma hatası:', e);
    throw e;
  }
}

// Profil karşılaştırması
export async function compareProfiles(dosya_yolu, profiller) {
  try {
    const response = await fetch(`${API_BASE}/karsilastir`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dosya_yolu,
        profiller
      })
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (e) {
    console.error('Profil karşılaştırma hatası:', e);
    throw e;
  }
}

// Sözlüğe terim ekle
export async function addTerm(kategori, terim, riskPuani) {
  try {
    const response = await fetch(`${API_BASE}/kelime-ekle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        kategori,
        terim,
        risk_puani: riskPuani
      })
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (e) {
    console.error('Terim ekleme hatası:', e);
    throw e;
  }
}

// Profil güncelle
export async function updateProfile(profil_adi, parametreler) {
  try {
    const response = await fetch(`${API_BASE}/profil-guncelle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        profil_adi,
        parametreler
      })
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (e) {
    console.error('Profil güncelleme hatası:', e);
    throw e;
  }
}

// Custom profil oluştur
export async function createCustomProfile(ad, parametreler) {
  try {
    const response = await fetch(`${API_BASE}/custom-profil-olustur`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ad,
        parametreler
      })
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (e) {
    console.error('Custom profil oluşturma hatası:', e);
    throw e;
  }
}
