#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEB TTK Detayli Bulgu Raporlama - Basit Versiyon
"""

from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from html import escape
import re
from text_quality import first_text, repair_mojibake


class MEBBulgularıRaporlayıcı:
    """MEB kriterler için detayli bulgu raporlayici"""
    
    def __init__(self, font_regular="Helvetica", font_bold="Helvetica-Bold"):
        self.styles = getSampleStyleSheet()
        self.font_regular = font_regular
        self.font_bold = font_bold
        self.kriterler = {
            "anayasa": "Anayasa ve Mevzuat Uygunluğu",
            "milli_guvenlik": "Millî Güvenlik",
            "esitlik": "Eşitlik ve Kapsayıcılık",
            "milli_manevi": "Millî ve Manevi Değerler",
            "guvenlik": "Güvenli ve Etik İçerik",
            "bilimsel": "Bilimsel Doğruluk",
            "reklam": "Reklam ve Ticari Unsurlar",
            "dil": "Dil ve Anlatım"
        }

    def _pdf_metni_temizle(self, metin) -> str:
        if metin is None:
            return ""
        return repair_mojibake(metin)

        temiz = str(metin)
        for _ in range(2):
            if not re.search(r"(?:Ã.|Ä.|Å.|â.|ð.|ğŸ)", temiz):
                break
            duzeltilmis = None
            for kaynak_kodlama in ("latin1", "cp1252"):
                try:
                    aday = temiz.encode(kaynak_kodlama).decode("utf-8")
                    if len(aday) >= max(1, int(len(temiz) * 0.6)):
                        duzeltilmis = aday
                        break
                except (UnicodeEncodeError, UnicodeDecodeError):
                    continue
            if not duzeltilmis or duzeltilmis == temiz:
                break
            temiz = duzeltilmis
        replacements = {
            "✅": "[Uygun]",
            "✔️": "[Düşük Risk]",
            "✔": "[Düşük Risk]",
            "⚠️": "[Uyarı]",
            "⚠": "[Uyarı]",
            "❌": "[Uygun Değil]",
            "🔴": "[Revizyon]",
            "ℹ️": "[Bilgi]",
            "ℹ": "[Bilgi]",
            "→": "->",
            "•": "-",
        }
        for eski, yeni in replacements.items():
            temiz = temiz.replace(eski, yeni)
        temiz = temiz.replace("Uretken", "Üretken")
        return temiz

    def _alinti_temizle(self, metin) -> str:
        temiz = self._pdf_metni_temizle(metin)
        temiz = temiz.replace("›", "ı").replace("‹", "İ")
        temiz = re.sub(r"(?<=[A-Za-zÇĞİÖŞÜçğıöşü])\s*-\s+(?=[A-Za-zÇĞİÖŞÜçğıöşü])", "", temiz)
        temiz = temiz.replace("[", "").replace("]", "")
        temiz = " ".join(temiz.split())
        return temiz

    def _hucre_metni(self, metin, limit: int = 420) -> str:
        temiz = self._pdf_metni_temizle(metin)
        temiz = " ".join(temiz.split())
        return temiz if len(temiz) <= limit else temiz[:limit - 3] + "..."

    def _sayiya_cevir(self, deger, varsayilan: int = 0) -> int:
        try:
            if deger is None or deger == "":
                return varsayilan
            return int(float(deger))
        except (TypeError, ValueError):
            return varsayilan

    def _bulgu_listesi(self, deger) -> list:
        if isinstance(deger, list):
            return [item for item in deger if isinstance(item, dict)]
        if isinstance(deger, dict):
            return [deger]
        return []

    def _bulgu_alintisi(self, bulgu: dict) -> str:
        return self._alinti_temizle(first_text(
            bulgu.get('alinti'),
            bulgu.get('alıntı'),
            bulgu.get('alininti'),
            bulgu.get('quote'),
            bulgu.get('cumle'),
            bulgu.get('kontext'),
            bulgu.get('baglam'),
        ))

    def _alinti_havuzu(self, sonuclar: dict) -> dict:
        havuz = {}

        def ekle(kayit: dict, kategori: str = "") -> None:
            quote = self._bulgu_alintisi(kayit)
            if not quote:
                return
            sayfa = str(kayit.get('sayfa', '') or '')
            adlar = {
                self._pdf_metni_temizle(kayit.get('tema_adi', '')).strip().lower(),
                self._pdf_metni_temizle(kayit.get('kelime', '')).strip().lower(),
                kategori.strip().lower(),
            }
            for ad in {ad for ad in adlar if ad}:
                havuz.setdefault((sayfa, ad), quote)
                havuz.setdefault(('', ad), quote)
            if sayfa:
                havuz.setdefault((sayfa, ''), quote)

        for bulgu in ((sonuclar.get('tema_olay_orgusu_bulgulari') or {}).get('bulgular') or []):
            if isinstance(bulgu, dict):
                ekle(bulgu, str(bulgu.get('kategori', '') or ''))
        for kategori, kategori_data in (sonuclar.get('kategori_bulgulari') or {}).items():
            for bulgu in (kategori_data or {}).get('bulunan_kelimeler', []) or []:
                if isinstance(bulgu, dict):
                    ekle(bulgu, str(kategori))
        return havuz

    def _havuzdan_alinti_bul(self, bulgu: dict, kriter_key: str, havuz: dict) -> str:
        sayfa = str(bulgu.get('sayfa', '') or '')
        adaylar = [
            self._pdf_metni_temizle(bulgu.get('tema_adi', '')).strip().lower(),
            self._pdf_metni_temizle(bulgu.get('kelime', '')).strip().lower(),
            self._kriter_kategori_eslesmesi(kriter_key),
            '',
        ]
        for aday in adaylar:
            quote = havuz.get((sayfa, aday)) or havuz.get(('', aday))
            if quote:
                return quote
        return ""

    def _kriter_kategori_eslesmesi(self, kriter_key: str) -> str:
        return {
            'guvenlik': 'zararlı_alışkanlıklar',
            'milli_manevi': 'cinsellik_mahremiyet',
            'dil': 'kaba_dil_hakaret',
            'esitlik': 'ayrımcılık_nefret',
        }.get(kriter_key, '')

    def _p(self, metin, stil=None, limit: int = 420) -> Paragraph:
        stil = stil or self.styles['Normal']
        return Paragraph(escape(self._hucre_metni(metin, limit)), stil)

    def _risk_durumu(self, risk: int) -> tuple:
        if risk <= 0:
            return "TEMİZ", "Risk tespit edilmedi."
        if risk <= 1:
            return "BİLGİ", "Düşük düzeyli editoryal kontrol yeterlidir."
        if risk <= 2:
            return "KONTROL", "Bağlam ve yaş grubu açısından kontrol önerilir."
        if risk <= 3:
            return "UYARI", "Pedagojik ve editoryal düzeltme gerektirebilir."
        return "YÜKSEK", "Yayın öncesi ayrıntılı revizyon gerektirir."

    def _kriter_aciklamasi(self, kriter_key: str) -> str:
        aciklamalar = {
            "anayasa": "Metin; hukuk düzeni, anayasal bütünlük ve mevzuata aykırı yönlendirme açısından değerlendirilir.",
            "milli_guvenlik": "Terör, şiddet örgütü, güvenliği zedeleyen çağrı veya özendirme izlenimi veren anlatımlar incelenir.",
            "esitlik": "Ayrımcı, dışlayıcı, aşağılayıcı veya nefret söylemine yaklaşan ifadeler kontrol edilir.",
            "milli_manevi": "Aile, değerler, toplumsal hassasiyetler ve millî-manevi bütünlükle çatışabilecek anlatımlar değerlendirilir.",
            "guvenlik": "Çocuk güvenliği, zararlı alışkanlıklar, şiddet, taklit edilebilir eylem ve etik riskler incelenir.",
            "bilimsel": "Bilimsel doğruluk, hurafe, yanlış bilgi veya yanıltıcı anlatım ihtimali kontrol edilir.",
            "reklam": "Marka, ticari yönlendirme, satın alma çağrısı veya dış bağlantı riski değerlendirilir.",
            "dil": "Kaba dil, argo, hakaret, yaş grubuna uygun olmayan ifade ve anlatım tonu kontrol edilir."
        }
        return aciklamalar.get(kriter_key, "Bu kriter altında tespit edilen içerikler bağlamıyla birlikte değerlendirilir.")

    def _duzeltme_onerisi(self, kriter_key: str, sebebi: str = "", risk: int = 0) -> str:
        sebep_lower = self._pdf_metni_temizle(sebebi).lower()
        dusuk_risk = self._sayiya_cevir(risk) <= 2
        if "özendir" in sebep_lower or "ozendir" in sebep_lower or "taklit" in sebep_lower:
            return "Özendirici veya taklit ettirici tonu kaldırın; davranışın sonucu ve sakıncası açıkça verilsin."
        if "kufur" in sebep_lower or "küfür" in sebep_lower or "argo" in sebep_lower or "hakaret" in sebep_lower:
            return "Kaba/argo ifadeyi yaş grubuna uygun, nötr ve edebî bir karşılıkla değiştirin."
        if "şiddet" in sebep_lower or "siddet" in sebep_lower or "grafik" in sebep_lower:
            if dusuk_risk:
                return "Sahneyi yaş grubu açısından editoryal olarak kontrol edin; sonucu, duyguyu ve güvenli mesajı belirginleştirin."
            return "Şiddet ayrıntısını azaltın; sahneyi sonuç, duygu ve güvenli mesaj üzerinden yeniden kurun."
        if "marka" in sebep_lower or "satın" in sebep_lower or "satin" in sebep_lower:
            return "Marka veya ticari çağrıyı eğitsel bağlama alın; gerekiyorsa genel bir nesne/kurum adı kullanın."

        oneriler = {
            "anayasa": "İfade hukuki ve toplumsal bağlamıyla açıklanmalı; yönlendirici veya meşrulaştırıcı ton kaldırılmalıdır.",
            "milli_guvenlik": "Riskli çağrı, örgüt övgüsü veya eylem tarifi varsa açık eleştirel bağlama alınmalı; yüksek riskte yeniden yazılmalıdır.",
            "esitlik": "Ayrımcı dili nötrleştirin; farklılıklara saygıyı belirginleştiren bir ifade ekleyin.",
            "milli_manevi": "Sahneyi değerleri zedelemeyecek biçimde yeniden yazın; gerekirse olumlu karşı davranış veya açıklayıcı not ekleyin.",
            "guvenlik": "Çocuk okur için taklit edilebilir ayrıntıları azaltın; güvenli davranış ve sonuç bilgisini güçlendirin.",
            "bilimsel": "Yanlış veya belirsiz bilgiyi doğrulanabilir kaynakla düzeltin; hurafe izlenimi varsa açıklayıcı bağlam ekleyin.",
            "reklam": "Ticari yönlendirme ve marka vurgusunu eğitsel bağlamla sınırlandırın; eğitim dışı bağlantıları sadeleştirin.",
            "dil": "Kaba, aşağılayıcı veya yaş grubuna uygun olmayan ifadeyi sade ve uygun bir dille değiştirin."
        }
        if risk >= 4:
            return oneriler.get(kriter_key, "Riskli bölüm revize edilmeli ve yeniden denetime alınmalıdır.")
        return oneriler.get(kriter_key, "Bölüm bağlamıyla birlikte kontrol edilmeli; gerekirse açıklama veya yumuşatma yapılmalıdır.")
    
    def olustur_meb_raporu(self, sonuclar: dict) -> list:
        """Genisletilmis MEB TTK bolumu olustur"""
        
        import os
        log_path = os.path.abspath('debug_meb_SIMPLE.log')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[olustur_meb_raporu] Called\n")
        
        elements = []
        
        # STIL TANIMLAMA
        baslik_stili = ParagraphStyle(
            'BaslikStili',
            parent=self.styles['Heading2'],
            fontName=self.font_bold,
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12
        )
        
        metin_stili = ParagraphStyle(
            'MetinStili',
            parent=self.styles['Normal'],
            fontName=self.font_regular,
            fontSize=11,
            spaceAfter=6
        )
        hucre_stili = ParagraphStyle(
            'MEBHucre',
            parent=self.styles['Normal'],
            fontName=self.font_regular,
            fontSize=8,
            leading=10
        )
        baslik_hucre_stili = ParagraphStyle(
            'MEBBaslikHucre',
            parent=hucre_stili,
            fontName=self.font_bold
        )
        
        # BASLIK
        elements.append(Paragraph("<b>4. MEB TTK Kriterleri Analizi</b>", baslik_stili))
        elements.append(Spacer(1, 0.15 * inch))
        
        # OZET TABLO
        meb_eval = sonuclar.get('meb_degerlendirmesi', {})
        meb_kriterler = meb_eval.get('meb_kriterler', {})
        puanlama = meb_eval.get('puanlama_detayi', {}) or {}
        kriter_cezalari = puanlama.get('kriter_cezalari', {}) or {}
        meb_puani = self._sayiya_cevir(meb_eval.get('meb_puani', 50), 50)
        meb_karar = self._pdf_metni_temizle(meb_eval.get('genel_karar', 'Bilinmiyor'))

        for kriter_key, ceza_detayi in kriter_cezalari.items():
            if not isinstance(ceza_detayi, dict):
                continue
            ceza = self._sayiya_cevir(ceza_detayi.get('puan_cezasi', 0), 0)
            if ceza <= 0:
                continue
            kriter_data = meb_kriterler.setdefault(kriter_key, {})
            kriter_data['risk'] = max(
                self._sayiya_cevir(kriter_data.get('risk', 0), 0),
                self._sayiya_cevir(ceza_detayi.get('risk', 0), 0),
            )
            kriter_data['puan_cezasi'] = ceza
            if ceza_detayi.get('karar'):
                kriter_data['karar'] = ceza_detayi.get('karar')
        
        tablo_veriler = [[
            self._p("Kriter", baslik_hucre_stili),
            self._p("Risk", baslik_hucre_stili),
            self._p("Puan Etkisi", baslik_hucre_stili),
            self._p("Durum", baslik_hucre_stili),
            self._p("Denetim Notu", baslik_hucre_stili),
        ]]
        
        tum_kriterler = dict(self.kriterler)
        for kriter_key in set(meb_kriterler) | set(kriter_cezalari):
            tum_kriterler.setdefault(kriter_key, kriter_key.replace('_', ' ').title())

        for kriter_key, kriter_adi in tum_kriterler.items():
            if kriter_key in meb_kriterler or kriter_key in kriter_cezalari:
                kriter_data = meb_kriterler.get(kriter_key, {}) or {}
                ceza_detayi = kriter_cezalari.get(kriter_key, {}) or {}
                ceza = self._sayiya_cevir(ceza_detayi.get('puan_cezasi', kriter_data.get('puan_cezasi', 0)), 0)
                karar_kaynagi = ceza_detayi.get('karar') if ceza > 0 and ceza_detayi.get('karar') else kriter_data.get('karar', 'Bilinmiyor')
                karar = self._pdf_metni_temizle(karar_kaynagi)
                risk = self._sayiya_cevir(ceza_detayi.get('risk', kriter_data.get('risk', 0)), 0)
                durum, denetim_notu = self._risk_durumu(risk)
                
                tablo_veriler.append([
                    self._p(kriter_adi, hucre_stili, 160),
                    self._p("%d/5" % risk, hucre_stili, 20),
                    self._p("-%d" % ceza, hucre_stili, 35),
                    self._p("%s - %s" % (durum, karar), hucre_stili, 180),
                    self._p(denetim_notu, hucre_stili, 240),
                ])
        
        tablo = Table(tablo_veriler, colWidths=[1.35 * inch, 0.42 * inch, 0.62 * inch, 1.18 * inch, 1.93 * inch], repeatRows=1)
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFDF4')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#777777')),
        ]))
        elements.append(tablo)
        elements.append(Spacer(1, 0.15 * inch))
        
        # MEB PUANI
        elements.append(Paragraph(
            "<b>MEB Uyum Puanı:</b> %d/100 -> %s" % (meb_puani, meb_karar),
            metin_stili
        ))
        if puanlama:
            baslangic = self._sayiya_cevir(puanlama.get('baslangic_puani', 100), 100)
            toplam_ceza = self._sayiya_cevir(puanlama.get('toplam_ceza', 0), 0)
            ceza_parcalari = []
            for kriter_key, kriter_data in meb_kriterler.items():
                ceza = self._sayiya_cevir((kriter_data or {}).get('puan_cezasi', 0), 0)
                if ceza <= 0:
                    continue
                etiket = "Güvenlik Cezası" if kriter_key == "guvenlik" else "%s Cezası" % self.kriterler.get(kriter_key, kriter_key.replace('_', ' ').title())
                ceza_parcalari.append("%s (%d)" % (self._pdf_metni_temizle(etiket), ceza))
            ceza_metni = " + ".join(ceza_parcalari) if ceza_parcalari else "Toplam Ceza (%d)" % toplam_ceza
            elements.append(Paragraph(
                "<b>Hesaplama:</b> %d - %s = %d" % (baslangic, ceza_metni, meb_puani),
                metin_stili
            ))
        elements.append(Spacer(1, 0.1 * inch))
        
        if puanlama:
            elements.append(Paragraph(
                "<b>MEB Puan Formülü:</b> %s. Başlangıç puanı: %s, toplam ceza: %s, tablo puan etkisi toplamı: -%s." % (
                    self._pdf_metni_temizle(puanlama.get('formul', '')),
                    self._pdf_metni_temizle(puanlama.get('baslangic_puani', 100)),
                    self._pdf_metni_temizle(puanlama.get('toplam_ceza', 0)),
                    self._pdf_metni_temizle(sum(
                        self._sayiya_cevir((kriter or {}).get('puan_cezasi', 0), 0)
                        for kriter in meb_kriterler.values()
                        if isinstance(kriter, dict)
                    )),
                ),
                metin_stili
            ))
            guvenlik_cezasi = ((puanlama.get('kriter_cezalari') or {}).get('guvenlik') or {}).get('puan_cezasi', 0)
            if self._sayiya_cevir(guvenlik_cezasi, 0) > 0:
                kalibrasyon_notu = self._pdf_metni_temizle(puanlama.get(
                    'kalibrasyon_notu',
                    'Tek kriter otomatik -50 üretmez; ceza bulgu şiddeti, tekrar/tema yoğunluğu, yaş grubu ve normalizasyon bağlamıyla kademeli hesaplanır.'
                ))
                elements.append(Paragraph(
                    "<b>Puanlama Notu:</b> Güvenli ve Etik İçerik kritik kriterdir; ancak cezası sabit -50 olarak değil kademeli uygulanır. Bu raporda kriter -%s puan ceza üretmiştir. %s" %
                    (self._pdf_metni_temizle(guvenlik_cezasi), kalibrasyon_notu),
                    metin_stili
                ))
            elements.append(Spacer(1, 0.1 * inch))

        # KARAR VE SONUC
        if meb_puani >= 75:
            sonuc = "UYGUN - Kitap MEB Talim ve Terbiye Kurulu kriterlerine uygun bulunmuştur."
        elif meb_puani >= 50:
            sonuc = "KOŞULLU - Kitap koşullu olarak MEB kriterlerine uygun olabilir. İşaretli bölümler kontrol edilmelidir."
        elif meb_puani >= 25:
            sonuc = "REVİZYON - Kitabın MEB kriterlerine uygun hale gelmesi için önemli düzeltmeler gereklidir."
        else:
            sonuc = "UYGUN DEĞİL - Kitap mevcut haliyle MEB kriterlerine uygun değildir."
        
        elements.append(Paragraph("<b>Sonuç:</b> " + sonuc, metin_stili))
        
        # DETAYLI BULGULAR
        meb_eval = sonuclar.get('meb_degerlendirmesi', {})
        meb_bulgulari = meb_eval.get('meb_bulgulari', {})
        meb_kriterler = meb_eval.get('meb_kriterler', {})
        alinti_havuzu = self._alinti_havuzu(sonuclar)
        
        import os
        debug_path = os.path.abspath('debug_meb_SIMPLE.log')
        
        with open(debug_path, 'a', encoding='utf-8') as f:
            f.write(f"[4.1] STEP1: meb_bulgulari={bool(meb_bulgulari)}, count={len(meb_bulgulari)}\n")
            f.write(f"[4.1] STEP2: meb_kriterler keys={list(meb_kriterler.keys())}\n")
        
        # Eğer detaylı bulgular yoksa, meb_kriterlerden risk > 0 olanları kullan
        if not (meb_bulgulari and any(meb_bulgulari.values())):
            with open(debug_path, 'a', encoding='utf-8') as f:
                f.write(f"[4.1] STEP3: Fallback tetikleniyor\n")
            meb_bulgulari = {}
            for kriter_key, kriter_info in meb_kriterler.items():
                risk = self._sayiya_cevir(kriter_info.get('risk', 0), 0)
                if risk > 0:
                    with open(debug_path, 'a', encoding='utf-8') as f:
                        f.write(f"[4.1] STEP4: {kriter_key}: risk={risk} ekleniyor\n")
                    # Risk var ise, bu kriteri bulgu olarak ekle
                    meb_bulgulari[kriter_key] = [{
                        'bulgu': self._pdf_metni_temizle(kriter_info.get('karar', 'Uyarı')),
                        'sebebi': 'Kriter Risk: %d/5' % risk,
                        'alinti': '',
                        'sayfa': 0,
                        'risk_puani': risk,
                        'onerili_revizyon': self._duzeltme_onerisi(kriter_key, kriter_info.get('karar', ''), risk)
                    }]
        
        with open(debug_path, 'a', encoding='utf-8') as f:
            f.write(f"[4.1] STEP5: Final: {len(meb_bulgulari)} items, render={bool(meb_bulgulari and any(meb_bulgulari.values()))}\n")

        meb_bulgulari = {
            kriter_key: [
                bulgu for bulgu in bulgular_listesi
                if self._sayiya_cevir(bulgu.get('risk_puani', 0), 0) > 0
                and self._sayiya_cevir(meb_kriterler.get(kriter_key, {}).get('risk', 0), 0) > 0
            ]
            for kriter_key, bulgular_listesi in meb_bulgulari.items()
            for bulgular_listesi in [self._bulgu_listesi(bulgular_listesi)]
        }
        meb_bulgulari = {k: v for k, v in meb_bulgulari.items() if v}
        
        if meb_bulgulari and any(meb_bulgulari.values()):
            with open(debug_path, 'a', encoding='utf-8') as f:
                f.write(f"[4.1] STEP6: Rendering 4.1 section with {len(meb_bulgulari)} criteria\n")
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph("<b>4.1 Riskli Kriterlerin Ayrıntılı Analizi</b>", baslik_stili))
            elements.append(Spacer(1, 0.1 * inch))
            elements.append(Paragraph(
                "Aşağıdaki bulgular, risk puanı alan MEB TTK kriterleri için alıntı, gerekçe ve uygulanabilir düzeltme önerisiyle birlikte verilmiştir.",
                metin_stili
            ))
            
            for kriter_key, bulgular_listesi in meb_bulgulari.items():
                if bulgular_listesi:
                    kriter_adi = self.kriterler.get(kriter_key, kriter_key)
                    kriter_risk = self._sayiya_cevir(meb_kriterler.get(kriter_key, {}).get('risk', 0), 0)
                    kriter_karar = self._pdf_metni_temizle(meb_kriterler.get(kriter_key, {}).get('karar', 'Bilinmiyor'))
                    durum, risk_notu = self._risk_durumu(kriter_risk)
                    
                    elements.append(Paragraph(
                        "<b>%s - %s (%d/5)</b>" % (kriter_adi, durum, kriter_risk),
                        ParagraphStyle(
                            'KriterBaslik',
                            parent=metin_stili,
                            fontSize=11,
                            textColor=colors.HexColor('#c00000'),
                            spaceBefore=6
                        )
                    ))

                    elements.append(Paragraph(
                        "<b>Kriter Açıklaması:</b> %s" % self._kriter_aciklamasi(kriter_key),
                        metin_stili
                    ))
                    elements.append(Paragraph(
                        "<b>Risk Gerekçesi:</b> %s Karar notu: %s" % (risk_notu, kriter_karar),
                        metin_stili
                    ))

                    detay_veriler = [[
                        self._p("Sayfa", baslik_hucre_stili),
                        self._p("Alıntı", baslik_hucre_stili),
                        self._p("Risk Açıklaması", baslik_hucre_stili),
                        self._p("Tavsiye / Düzeltme", baslik_hucre_stili),
                    ]]

                    for i, bulgu in enumerate(bulgular_listesi, 1):
                        sayfa = bulgu.get('sayfa', 0)
                        if sayfa > 0:
                            sayfa_str = "S. %d" % sayfa
                        else:
                            sayfa_str = "-"

                        quote = self._bulgu_alintisi(bulgu) or self._havuzdan_alinti_bul(bulgu, kriter_key, alinti_havuzu)
                        sebebi = self._pdf_metni_temizle(bulgu.get('sebebi', 'Bilinmiyor'))
                        risk = self._sayiya_cevir(bulgu.get('risk_puani', 0), 0)
                        revizyon = self._pdf_metni_temizle(bulgu.get('onerili_revizyon', ''))
                        if not revizyon:
                            revizyon = self._duzeltme_onerisi(kriter_key, sebebi, risk)

                        detay_veriler.append([
                            self._p(sayfa_str, hucre_stili, 20),
                            self._p(quote or "Alıntı bilgisi bulunamadı.", hucre_stili, 360),
                            self._p("Bulgu %d: %s Risk: %d/5." % (i, sebebi, risk), hucre_stili, 260),
                            self._p(revizyon, hucre_stili, 280),
                        ])

                    detay_tablosu = Table(
                        detay_veriler,
                        colWidths=[0.5 * inch, 2.0 * inch, 1.45 * inch, 1.55 * inch],
                        repeatRows=1
                    )
                    detay_tablosu.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F2F2F2')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFFFF')),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#999999')),
                    ]))
                    elements.append(detay_tablosu)
                    elements.append(Spacer(1, 0.12 * inch))
        
        return elements


# TEST
if __name__ == "__main__":
    raporlayici = MEBBulgularıRaporlayıcı()
    
    test_sonucu = {
        'meb_degerlendirmesi': {
            'meb_kriterler': {
                'anayasa': {'karar': 'Uyumlu', 'risk': 0},
                'milli_guvenlik': {'karar': 'Temiz', 'risk': 0},
                'esitlik': {'karar': 'Uygun', 'risk': 0},
                'milli_manevi': {'karar': 'Orta', 'risk': 4},
                'guvenlik': {'karar': 'Uygun', 'risk': 0},
                'bilimsel': {'karar': 'Dogru', 'risk': 0},
                'reklam': {'karar': 'Hafif', 'risk': 1},
                'dil': {'karar': 'Temiz', 'risk': 0},
            },
            'meb_puani': 50,
            'genel_karar': 'KOSULLU'
        },
        'meb_bulgulari': {
            'milli_manevi': [
                {
                    'sayfa': 15,
                    'alininti': 'Karakterler hicbir aile bagi gostermemistir.',
                    'sebebi': 'Aile degeri eksikligi',
                    'risk_puani': 2,
                    'onerili_revizyon': 'Aile ili iliskisini guclendirin.'
                },
                {
                    'sayfa': 23,
                    'alininti': 'Vatan mefhumu artik eski kalipdir.',
                    'sebebi': 'Vatan degeri asagilanmasi',
                    'risk_puani': 3,
                    'onerili_revizyon': 'Ifadeyi baglam ekleyerek guclendirin.'
                }
            ],
            'reklam': [
                {
                    'sayfa': 42,
                    'alininti': 'iPhone en iyi teknoloji urunudur.',
                    'sebebi': 'Marka tanitimi',
                    'risk_puani': 1,
                    'onerili_revizyon': 'Marka adini sil, genel referans yapilsin.'
                }
            ]
        }
    }
    
    elements = raporlayici.olustur_meb_raporu(test_sonucu)
    
    print("BASARILI - Rapor elemanlari olusturuldu!")
    print("Toplam %d element" % len(elements))
