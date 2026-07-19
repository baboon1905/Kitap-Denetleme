# MEB TTK Kriterleri - DETAYLI BULGU SİSTEMİ KURULUMU

**Tarih:** 2026-06-08  
**Amaç:** PDF raporlarında "Millî ve Manevi Değerler 4/5 Risk" gibi yazıldığında, tam olarak **hangi sayfalarda, hangi cümlelerinde risk olduğunu** gösterme

---

## 📋 Oluşturulan Modüller

### 1. `meb_bulgu_toplama.py` ⭐
**Amaç:** Metindeki riskli bölümleri tara ve toplayıcı

**Çıktı Örneği:**
```
[!] MİLLÎ GÜVENLIK
  1. BULGU
     Sayfa: Bilinmiyor
     Alıntı: "...PKK'nın direniş mücadelesinden bahsediyor. Siz de katılabilirsiniz..."
     Risk: 5/5 (Özendirme çağrısı)
     Önerilen Revizyon: KALDIRMALI - Bu içerik yayınlanmamalı
```

### 2. `meb_basit_raporlayici.py` ⭐⭐
**Amaç:** PDF raporuna entegre edilecek raporlama sistemi

**Kullanım:**
```python
from meb_basit_raporlayici import MEBBulgularıRaporlayıcı

raporlayıcı = MEBBulgularıRaporlayıcı()
rapor_elemanları = raporlayıcı.olustur_meb_raporu(evaluator_sonucu)
# PDF'e ekle: doc.build(rapor_elemanları)
```

### 3. `meb_entegrasyon.py` ⭐⭐⭐
**Amaç:** Evaluator sonuçlarına otomatik MEB bulgularını ekle

**Kullanım:**
```python
from meb_entegrasyon import ekle_meb_bulgularini

# Evaluator sonucu al
sonuc = evaluator.meb_kriterleri_degerlendirmesi(metin)

# Bulguları ekle
sonuc = ekle_meb_bulgularini(sonuc, metin, sayfa_haritasi)

# Şimdi raporlamaya geç
rapor_elemanları = raporlayıcı.olustur_meb_raporu(sonuc)
```

---

## 🔧 İmplementasyon Adımları

### Adım 1: Evaluator'da MEB bulgularını topla

**`evaluator_maarif.py`'de değişiklik:**

```python
from meb_entegrasyon import ekle_meb_bulgularini

class MaarifDegerlendiricisi:
    def analiz_yap(self, metin: str, ...) -> dict:
        # ... mevcut kod ...
        
        # MEB TTK Kriterleri Değerlendirmesi
        meb_degerlendirmesi = self.meb_kriterleri_degerlendirmesi(metin_normalized, profil)
        
        # YENİ: Bulguları ekle
        meb_degerlendirmesi = ekle_meb_bulgularini(
            meb_degerlendirmesi,
            metin_normalized,
            sayfa_haritasi=None  # PDF'den alınan sayfa haritası
        )
        
        return {
            "meb_degerlendirmesi": meb_degerlendirmesi,
            # ... diğer çıktılar ...
        }
```

### Adım 2: Report Generator'da detaylı bölüm oluştur

**`report_generator.py`'de değişiklik:**

```python
from meb_basit_raporlayici import MEBBulgularıRaporlayıcı

class RaporOlusturucu:
    def _olustur_meb_ttk_bolumu(self, sonuclar: dict) -> list:
        raporlayıcı = MEBBulgularıRaporlayıcı()
        return raporlayıcı.olustur_meb_raporu(sonuclar)
```

### Adım 3: PDF'de Sayfa Numaralarını Takip Etme

**`pdf_processor.py`'de:**

```python
def cikart_sayfa_haritasi(pdf_path: str) -> list:
    """
    PDF'i oku ve şu formatda sayfa haritası dön:
    [(metin_başlangıç_pozisyonu, metin_bitiş_pozisyonu, sayfa_no), ...]
    """
    sayfa_haritasi = []
    pos = 0
    
    for sayfa_no, metin in pdf_pages.items():
        bas = pos
        pos += len(metin)
        son = pos
        sayfa_haritasi.append((bas, son, sayfa_no))
    
    return sayfa_haritasi
```

---

## 📊 Çıktı Örneği

### Eski Rapor (Sorunlu)
```
4. MEB TTK KRITERLERI
┌──────────────────────────────────┬──────────┬────────┐
│ Kriter                           │ Durum    │ Risk   │
├──────────────────────────────────┼──────────┼────────┤
│ Millî ve Manevi Değerler         │ Orta     │ 4/5    │
└──────────────────────────────────┴──────────┴────────┘

MEB Uyum Puanı: 50/100 → Koşullu
Sonuç: Kitap koşullu olarak MEB kriterlerine uygun olabilir.
       İşaretli bölümler kontrol edilmelidir.

[PROBLEM: Hangi bölümler?? 😕]
```

### Yeni Rapor (Çözülmüş)
```
4. MEB TTK KRITERLERI
┌──────────────────────────────────┬──────────┬────────┐
│ Kriter                           │ Durum    │ Risk   │
├──────────────────────────────────┼──────────┼────────┤
│ Millî ve Manevi Değerler         │ Orta     │ 4/5    │
└──────────────────────────────────┴──────────┴────────┘

MEB Uyum Puanı: 50/100 → Koşullu

4.1 DETAYLI BULGU ANALIZI

- Millî ve Manevi Değerler

  Bulgu 1: (Sayfa 15)
  Alıntı: "...Karakterler hiçbir aile bağı göstermemiştir..."
  Sebebi: Aile değeri eksikliği (Risk: 2/5)
  Revizyon: Aile ilişkisini güçlendir.

  Bulgu 2: (Sayfa 23)
  Alıntı: "...Vatan mefhumu artık eski kalıptır..."
  Sebebi: Vatan değeri aşağılanması (Risk: 3/5)
  Revizyon: İfadeyi bağlam ekleyerek güçlendir.

[ÇÖZÜM: Sayfa 15 ve 23'te tam bölümler belirtildi! 🎯]
```

---

## 🧪 Test Senaryoları

### Test 1: Basit Uygun Kitap
```python
metin = "Atatürk büyük lider. Aile önemli. Vatan bizimdir."

sonuc = evaluator.meb_kriterleri_degerlendirmesi(metin)
sonuc = ekle_meb_bulgularini(sonuc, metin)

assert sonuc['meb_puani'] >= 75
assert len(sonuc['meb_bulgulari']) == 0
print("✅ TEST 1 GEÇTI")
```

### Test 2: Riskli Kitap
```python
metin = """
PKK'nın direniş mücadelesinden bahsediyor. 
Siz de katılabilirsiniz. Kadınlar bilim yapamaz.
"""

sonuc = evaluator.meb_kriterleri_degerlendirmesi(metin)
sonuc = ekle_meb_bulgularini(sonuc, metin)

# En az 3 kriter riskli olmalı
assert len(sonuc['meb_bulgulari']) >= 3
assert sonuc['meb_puani'] < 50
print("✅ TEST 2 GEÇTI")
```

---

## 📁 Dosya Yapısı

```
kitap-degerlendirme-app/
├── meb_bulgu_toplama.py          [Yeni] Riskli bölümleri tara
├── meb_basit_raporlayici.py      [Yeni] PDF raporlama modülü
├── meb_entegrasyon.py            [Yeni] Evaluator entegrasyonu
│
├── evaluator_maarif.py           [DEĞIŞTIR] ekle_meb_bulgularini() çağrı ekle
├── report_generator.py           [DEĞIŞTIR] MEBBulgularıRaporlayıcı kullan
└── pdf_processor.py              [OPSIYONEL] Sayfa haritası çıkart
```

---

## ⚡ Hızlı Başlangıç

### 1. Sistemi Test Et
```bash
cd kitap-degerlendirme-app

# Bulgu toplama testi
python meb_bulgu_toplama.py

# Raporlama testi
python meb_basit_raporlayici.py

# Entegrasyon testi
python meb_entegrasyon.py
```

### 2. Evaluator'a Entegre Et
Dosya: `evaluator_maarif.py`, satır ~110 (analiz_yap metodunun sonunda)

```python
# YENİ KOD EKLE:
from meb_entegrasyon import ekle_meb_bulgularini

# analiz_yap metodunda:
meb_degerlendirmesi = ekle_meb_bulgularini(
    meb_degerlendirmesi,
    metin,
    sayfa_haritasi=None
)
```

### 3. Report Generator'a Entegre Et
Dosya: `report_generator.py`, satır ~450

```python
# YENİ KOD EKLE:
from meb_basit_raporlayici import MEBBulgularıRaporlayıcı

# _olustur_meb_ttk_bolumu metodunun başında:
raporlayıcı = MEBBulgularıRaporlayıcı()
return raporlayıcı.olustur_meb_raporu(sonuclar)
```

---

## 🔍 Sorun Giderme

### Problem: Bulguların sayfa numarası "Bilinmiyor"
**Çözüm:** `pdf_processor.py`'de sayfa haritası çıkart ve entegrasyon çağrısında geç

```python
sayfa_haritasi = cikart_sayfa_haritasi(pdf_path)
sonuc = ekle_meb_bulgularini(sonuc, metin, sayfa_haritasi)
```

### Problem: Türkçe karakterlerde hata
**Çözüm:** Python dosyasının başında şu satırı ekle

```python
# -*- coding: utf-8 -*-
```

### Problem: Çok fazla bulgu (100+)
**Çözüm:** Filtre ekle (`meb_entegrasyon.py`'de)

```python
# Max 5 bulgu per kritere
bulgular = bulgular[:5]
```

---

## 📞 Sıkça Sorulan Sorular

**S: Neden bulguların alıntısı 120 karakter?**
A: PDF'de yer tasarrufu için. Gerekirse `meb_entegrasyon.py` satır 140'ta artırabilirsiniz.

**S: Yanlış bulgu toplandığını fark ettim**
A: `meb_entegrasyon.py`'de `ayristi_belirtiler`, `teror_belirtiler` vb. listeleri düzenleyin.

**S: Bulguların sıralaması değişti**
A: Alfabetik sıralamayı PDF'de ayarlamak için `meb_basit_raporlayici.py` satır 110'u değiştirin.

---

## ✅ Kontrol Listesi

- [ ] 3 yeni Python dosyası (`meb_bulgu_toplama.py`, `meb_basit_raporlayici.py`, `meb_entegrasyon.py`) eklendi
- [ ] Test komutları çalıştırıldı ve başarılı
- [ ] `evaluator_maarif.py`'e `ekle_meb_bulgularini()` entegre edildi
- [ ] `report_generator.py`'de `MEBBulgularıRaporlayıcı` kullanılıyor
- [ ] PDF raporlarında 4.1 "Detaylı Bulgu Analizi" bölümü çıkıyor
- [ ] Her bulgu için sayfa, alıntı ve revizyon önerisi görülüyor

---

**Sonuç:** Artık editörler raporları açtığında, her risk için **hangi sayfada, hangi cümlede, neden riskli olduğunu ve nasıl düzeltileceğini** tam olarak görebilirler! 🎯

---

*Son güncelleme: 2026-06-08*
