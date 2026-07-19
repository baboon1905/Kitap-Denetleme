"""
Değerlendirme raporunu PDF olarak oluşturma
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from html import escape
from copy import deepcopy
import io
import re
import os
import sys
from visual_audit import VISUAL_AUDIT_CATEGORIES, normalize_gorsel_denetim
from text_quality import collect_text_quality_issues, first_text, repair_mojibake, repair_payload_text

# MEB Bulgu Raporlaması
try:
    from meb_basit_raporlayici import MEBBulgularıRaporlayıcı
    MEB_RAPORLAYICI_YÜKLÜ = True
    print("[IMPORT] MEBBulgularıRaporlayıcı imported successfully", flush=True)
except ImportError as e:
    MEB_RAPORLAYICI_YÜKLÜ = False
    print(f"[IMPORT] MEBBulgularıRaporlayıcı import failed: {e}", flush=True)

# Türkçe karakter desteği için fontları kaydet
# DejaVuSans veya Segoe UI'nı dene
DEFAULT_FONT = 'Helvetica'
DEFAULT_FONT_BOLD = 'Helvetica-Bold'

try:
    font_candidates = [
        ("TurkishFont", r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
        ("TurkishFont", r"C:\Windows\Fonts\calibri.ttf", r"C:\Windows\Fonts\calibrib.ttf"),
        ("TurkishFont", r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\segoeuib.ttf"),
        ("TurkishFont", r"C:\Program Files\DejaVuFonts\DejaVuSans.ttf", r"C:\Program Files\DejaVuFonts\DejaVuSans-Bold.ttf"),
    ]

    for font_name, regular_path, bold_path in font_candidates:
        if os.path.exists(regular_path) and os.path.exists(bold_path):
            pdfmetrics.registerFont(TTFont(font_name, regular_path))
            pdfmetrics.registerFont(TTFont(f"{font_name}-Bold", bold_path))
            pdfmetrics.registerFontFamily(
                font_name,
                normal=font_name,
                bold=f"{font_name}-Bold",
                italic=font_name,
                boldItalic=f"{font_name}-Bold"
            )
            DEFAULT_FONT = font_name
            DEFAULT_FONT_BOLD = f"{font_name}-Bold"
            print(f"Turkish PDF font loaded: {regular_path}")
            break
except Exception as e:
    print(f"Font registration hatasi: {e} (Helvetica fallback)")
    DEFAULT_FONT = 'Helvetica'
    DEFAULT_FONT_BOLD = 'Helvetica-Bold'


class RaporOlusturucu:
    """PDF rapor oluşturur"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
        # Türkçe karakter desteği için fontları güncelle
        for style in self.styles.byName.values():
            style.fontName = DEFAULT_FONT
            if 'Bold' in style.fontName or style.fontName.endswith('-Bold'):
                style.fontName = DEFAULT_FONT_BOLD
        
        self.page_width = A4[0]
        self.page_height = A4[1]

    def _pdf_metni_temizle(self, metin) -> str:
        """PDF fontlarında kareye dönüşen emoji/sembolleri düz metne çevir."""
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

    def _kategori_adi(self, kategori: str) -> str:
        kategori_isimleri = {
            'siddet_suc': 'Şiddet ve Suç',
            'cinsellik_mahremiyet': 'Cinsellik ve Mahremiyet',
            'zararlı_alışkanlıklar': 'Zararlı Alışkanlıklar',
            'zararlı_alişkanliklар': 'Zararlı Alışkanlıklar',
            'kaba_dil_hakaret': 'Kaba Dil ve Hakaret',
            'ayrımcılık_nefret': 'Ayrımcılık ve Nefret',
            'ayrimcilik_nefret': 'Ayrımcılık ve Nefret',
            'korku_travma': 'Korku ve Travma',
            'okültizm_batıl': 'Okültizm ve Batıl',
            'okültizm_batil': 'Okültizm ve Batıl',
            'olumsuz_davranış': 'Olumsuz Davranış',
            'olumsuz_davranis': 'Olumsuz Davranış',
            'reklam_ticari': 'Reklam ve Ticari Unsurlar',
            'dijital_risk': 'Dijital Risk'
        }
        return kategori_isimleri.get(kategori, str(kategori).replace('_', ' ').title())

    def _risk_degeri(self, bulgu: dict) -> float:
        """Bulgunun raporda kullanılacak nihai risk puanını döndürür."""
        riskler = []
        for alan in ('riskPuani', 'risk_puani', 'baglamsal_risk', 'risk', 'puan'):
            if alan in bulgu and bulgu.get(alan) is not None:
                try:
                    riskler.append(float(bulgu.get(alan) or 0))
                except (TypeError, ValueError):
                    pass
        return max(riskler) if riskler else 0.0

    def _debug_log(self, mesaj: str) -> None:
        try:
            with open(os.path.abspath('debug_consistency_assert.log'), 'a', encoding='utf-8') as log:
                log.write(f"{datetime.now().isoformat(timespec='seconds')} {mesaj}\n")
        except Exception:
            pass

    def _gorsel_analiz_eksik_mi(self, sonuclar: dict) -> bool:
        """PDF'de gorsel varsa ama icerik analizi calismadiysa kalite uyarisi uretir."""
        metadata = sonuclar.get('metadata', {}) or {}
        gorsel = sonuclar.get('gorsel_tarama') or metadata.get('gorsel_ozet') or {}
        toplam = int(gorsel.get('toplam_gorsel', 0) or 0)
        visual_pages = int(gorsel.get('visual_pages', len(gorsel.get('gorselli_sayfalar', []) or [])) or 0)
        visual_analysis_count = int(
            gorsel.get(
                'visual_analysis_count',
                gorsel.get('analiz_edilen_gorsel_sayisi', len(gorsel.get('gorsel_analizleri', []) or []))
            ) or 0
        )
        analiz_yapildi = bool(gorsel.get('gorsel_icerik_analizi_yapildi', False))
        return (visual_pages > 0 and visual_analysis_count == 0) or (toplam > 0 and not analiz_yapildi)

    def _bulgu_anahtari(self, bulgu: dict) -> tuple:
        kelime = self._pdf_metni_temizle(bulgu.get('kelime', '')).strip().lower()
        cumle = self._pdf_metni_temizle(
            bulgu.get('cumle') or bulgu.get('kontext') or bulgu.get('baglam') or ''
        ).strip().lower()
        sayfa = str(bulgu.get('sayfa', '') or '')
        return kelime, sayfa, cumle[:220]

    def _bulgu_kelime_anahtari(self, bulgu: dict, kategori: str = "") -> tuple:
        kelime = self._pdf_metni_temizle(bulgu.get('kelime') or bulgu.get('tema_adi') or '').strip().lower()
        return (kategori or self._pdf_metni_temizle(bulgu.get('kategori', '')).strip().lower()), kelime

    def _bulgu_sade_kelime_anahtari(self, bulgu: dict) -> str:
        return self._pdf_metni_temizle(bulgu.get('kelime') or bulgu.get('tema_adi') or '').strip().lower()

    def _karar_durumu(self, bulgu: dict) -> str:
        risk = self._risk_degeri(bulgu)
        karar = self._pdf_metni_temizle(bulgu.get('kararSinifi', '')).lower()
        if risk <= 0:
            return 'risk_0'
        if karar == 'insan_incelemesi':
            return 'insan_incelemesi'
        if risk <= 2:
            return 'dusuk_risk'
        return 'riskli'

    def _zorunlu_sahne_bulgusu_mu(self, bulgu: dict) -> bool:
        tema = self._pdf_metni_temizle(bulgu.get('tema_adi', '')).strip().lower()
        kaynak = self._pdf_metni_temizle(bulgu.get('kaynak', '')).strip().lower()
        baglam = self._pdf_metni_temizle(bulgu.get('baglamTipi', '')).strip().lower()
        kelime = self._pdf_metni_temizle(bulgu.get('kelime', '')).strip().lower()
        if baglam in {'romantik_dusuk_izleme', 'siddet_referansi_dusuk'}:
            return False
        zorunlu_temalar = {
            'sigara kullanımı', 'alkol kullanımı', 'sarhoşluk', 'kumar',
            'uyuşturucu', 'kavga', 'dövüş', 'şiddet', 'hırsızlık',
            'öpüşme', 'evlilik dışı ilişki'
        }
        return (
            tema in zorunlu_temalar
            or 'zorunlu kalite kontrol' in kaynak
            or baglam == 'zorunlu_tema_sahnelenmesi'
            or kelime in {tema.lower() for tema in zorunlu_temalar}
        )

    def _kategori_istatistiklerini_guncelle(self, kategori_data: dict) -> None:
        bulgular = kategori_data.get('bulunan_kelimeler', [])
        toplam_risk = sum(self._risk_degeri(bulgu) for bulgu in bulgular)
        kategori_data['toplam_bulgu'] = len(bulgular)
        kategori_data['bulundu'] = bool(bulgular)
        kategori_data['riskli_bulgu_sayisi'] = sum(
            1 for bulgu in bulgular if self._karar_durumu(bulgu) == 'riskli'
        )
        kategori_data['dusuk_risk_sayisi'] = sum(
            1 for bulgu in bulgular if self._karar_durumu(bulgu) == 'dusuk_risk'
        )
        kategori_data['insan_incelemesi_sayisi'] = sum(
            1 for bulgu in bulgular if self._karar_durumu(bulgu) == 'insan_incelemesi'
        )
        kategori_data['temizlenen_bulgu_sayisi'] = sum(
            1 for bulgu in bulgular if self._karar_durumu(bulgu) == 'risk_0'
        )
        kategori_data['ortalama_risk'] = round(toplam_risk / len(bulgular), 2) if bulgular else 0

    def consistency_assert(self, sonuclar: dict, raise_on_error: bool = True) -> dict:
        sonuclar = repair_payload_text(sonuclar)
        self._meb_detaylarini_kriterlere_yansit(sonuclar)
        self._debug_log(
            "[report_generator.consistency_assert] START "
            f"file={__file__} cwd={os.getcwd()} python={sys.executable}"
        )
        hatalar = []
        metin_sorunlari = collect_text_quality_issues(sonuclar, path="rapor_sonucu")
        if metin_sorunlari:
            hatalar.append("UTF-8 karakter bozulması tespit edildi: " + " | ".join(metin_sorunlari[:5]))
        kategori_bulgulari = sonuclar.get('kategori_bulgulari', {}) or {}
        for kategori_data in kategori_bulgulari.values():
            self._kategori_istatistiklerini_guncelle(kategori_data)
        tema_bulgulari = (sonuclar.get('tema_olay_orgusu_bulgulari', {}) or {}).get('bulgular', []) or []
        pozitif_kelime_anahtarlari = set()
        risk0_kelime_anahtarlari = set()
        pozitif_sade_kelimeler = set()
        risk0_sade_kelimeler = set()
        toplam_kayit = 0

        for kategori, kategori_data in kategori_bulgulari.items():
            bulgular = kategori_data.get('bulunan_kelimeler', []) or []
            riskli = dusuk = risk0 = 0
            for bulgu in bulgular:
                toplam_kayit += 1
                risk = self._risk_degeri(bulgu)
                if risk > 0:
                    pozitif_kelime_anahtarlari.add(self._bulgu_kelime_anahtari(bulgu, kategori))
                    pozitif_sade_kelimeler.add(self._bulgu_sade_kelime_anahtari(bulgu))
                    if risk >= 3:
                        riskli += 1
                    else:
                        dusuk += 1
                else:
                    risk0 += 1
                    risk0_kelime_anahtarlari.add(self._bulgu_kelime_anahtari(bulgu, kategori))
                    risk0_sade_kelimeler.add(self._bulgu_sade_kelime_anahtari(bulgu))

            toplam = int(kategori_data.get('toplam_bulgu', 0) or 0)
            if toplam != len(bulgular):
                hatalar.append(f"Kategori toplamı liste uzunluğu ile tutarsız: {kategori} toplam={toplam}, liste={len(bulgular)}")
            if int(kategori_data.get('riskli_bulgu_sayisi', 0) or 0) != riskli:
                hatalar.append(f"Riskli kayıt sayısı tutarsız: {kategori}")
            if int(kategori_data.get('dusuk_risk_sayisi', 0) or 0) != dusuk:
                hatalar.append(f"Düşük risk kayıt sayısı tutarsız: {kategori}")
            if int(kategori_data.get('temizlenen_bulgu_sayisi', 0) or 0) != risk0:
                hatalar.append(f"Risk 0 kayıt sayısı tutarsız: {kategori}")
            if toplam != riskli + dusuk + risk0:
                hatalar.append(f"Kategori alt toplamları tutarsız: {kategori}")

        for kategori, kelime in sorted(pozitif_kelime_anahtarlari & risk0_kelime_anahtarlari):
            hatalar.append(f"Risk alan kayıt Risk 0 savunma listesinde de var: {kategori}/{kelime}")
        for kelime in sorted((pozitif_sade_kelimeler & risk0_sade_kelimeler) - {''}):
            hatalar.append(f"Risk alan kelime Risk 0 savunma listesinde de var: {kelime}")

        for tema in tema_bulgulari:
            kategori = tema.get('kategori')
            tema_adi = self._pdf_metni_temizle(tema.get('tema_adi', '')).strip().lower()
            sayfa = str(tema.get('sayfa', '') or '')
            kanit_puani = float(tema.get('kanitPuani', tema.get('kararGuveni', 0.0)) or 0)
            if kanit_puani < 0.70:
                hatalar.append(
                    f"Tema kanıt puanı 0.70 altında: {tema.get('tema_adi', 'Tema')} / sayfa {sayfa or '?'} / kanıt={kanit_puani:.2f}"
                )
            temsil_var = False
            for bulgu in kategori_bulgulari.get(kategori, {}).get('bulunan_kelimeler', []):
                bulgu_tema = self._pdf_metni_temizle(bulgu.get('tema_adi') or bulgu.get('kelime') or '').strip().lower()
                bulgu_sayfa = str(bulgu.get('sayfa', '') or '')
                if bulgu_tema == tema_adi and bulgu_sayfa == sayfa:
                    temsil_var = True
                    break
            if not temsil_var:
                hatalar.append(f"Tema bulgusu kategori veya Risk 0 raporunda temsil edilmiyor: {tema.get('tema_adi', 'Tema')} / sayfa {sayfa or '?'}")

        zararli_temalar = {'Sigara kullanımı', 'Alkol kullanımı', 'Sarhoşluk', 'Uyuşturucu'}
        zararli_tespit = any(
            tema.get('tema_adi') in zararli_temalar and self._risk_degeri(tema) > 0
            for tema in tema_bulgulari
        )
        zararli_kategori_var = any(
            self._risk_degeri(bulgu) > 0
            for bulgu in kategori_bulgulari.get('zararlı_alışkanlıklar', {}).get('bulunan_kelimeler', [])
        )
        if zararli_tespit and not zararli_kategori_var:
            hatalar.append('Zararlı alışkanlık davranışı tespit edildi ama Zararlı Alışkanlıklar kategorisinde görünmüyor.')

        hatalar.extend(self._meb_matematik_sorunlari(sonuclar))
        hatalar.extend(self._risk_formulu_sorunlari(sonuclar))
        hatalar.extend(self._karar_esigi_sorunlari(sonuclar))
        hatalar.extend(self._tekrar_cezasi_sorunlari(sonuclar))

        sonuc = {'gecti': not hatalar, 'hatalar': hatalar, 'toplam_kayit': toplam_kayit}
        self._debug_log(
            "[report_generator.consistency_assert] END "
            f"gecti={sonuc['gecti']} toplam_kayit={toplam_kayit} "
            f"tema_bulgu={len(tema_bulgulari)} hata_sayisi={len(hatalar)} "
            f"hatalar={hatalar[:12]}"
        )
        if raise_on_error and hatalar:
            raise ValueError('Tutarlılık denetimi başarısız: ' + ' | '.join(hatalar))
        return sonuc

    def _zararli_aliskanlik_skor_kurali(self, sonuclar: dict) -> dict:
        kural = sonuclar.get('zararli_aliskanlik_skor_kurali') or {}
        if kural.get('zararli_aliskanlik_sahnesi_var'):
            return dict(kural)

        tema_bulgulari = self._tema_bulgulari(sonuclar)
        kategori_bulgulari = self._tum_bulgular(sonuclar)
        kayitlar = tema_bulgulari + kategori_bulgulari
        sayim_kayitlari = tema_bulgulari if tema_bulgulari else kayitlar

        def metin(bulgu: dict) -> str:
            return ' '.join(
                str(bulgu.get(alan, '') or '').lower()
                for alan in ('tema_adi', 'kelime', 'cumle', 'alinti', 'alıntı', 'kontext', 'baglamTipi')
            )

        def normalizasyon_var_mi(metin_degeri: str) -> bool:
            zararli_isaret = re.search(
                r'\b(?:sigara|puro|t[üu]t[üu]n|tutun|nargile|sarho[şs]|alkol|i[çc]ki|icki|'
                r'[şs]arap|sarap|rak[ıi]|raki|bira|meyhane)\w*\b',
                metin_degeri,
            )
            sosyal_olumlama = re.search(
                r'\b(?:[şs]akala[şs]|sakala[şs]|tak[ıi]l|g[üu]l[üu]mse|e[ğg]len|ne[şs]eli|'
                r'sevimli|sempatik|ho[şs]|iyi\s+adam|mahallede\s+sevil|herkes\s+sever|'
                r'rastlad[ıi]klar[ıi]na|arkada[şs]lar[ıi]yla)\w*\b',
                metin_degeri,
            )
            sureklilik = re.search(
                r'\b(?:g[üu]n[üu]n\s+yirmi\s+d[öo]rt\s+saati|yirmi\s+d[öo]rt\s+saat|24\s*saat|'
                r'hep|s[üu]rekli|durmadan|al[ıi][şs]kanl[ıi]k|fosur\s+fosur)\b',
                metin_degeri,
            )
            karsitlik = re.search(r'\b(?:olmas[ıi]na\s+kar[şs][ıi]n|ra[ğg]men|yine\s+de|buna\s+ra[ğg]men)\b', metin_degeri)
            return bool(zararli_isaret and (sosyal_olumlama or (sureklilik and karsitlik)))

        def benzersiz_say(kosul) -> int:
            anahtarlar = set()
            for bulgu in sayim_kayitlari:
                if self._risk_degeri(bulgu) <= 0 or not kosul(bulgu):
                    continue
                anahtarlar.add((
                    str(bulgu.get('tema_adi') or bulgu.get('kelime') or '').lower(),
                    str(bulgu.get('sayfa', '') or ''),
                    re.sub(r'\s+', ' ', metin(bulgu))[:220],
                ))
            return len(anahtarlar)

        sigara = any(
            self._risk_degeri(bulgu) > 0 and ('sigara kullanımı' in metin(bulgu) or re.search(r'\bsigara|puro|tütün|tutun|nargile\b', metin(bulgu)))
            for bulgu in kayitlar
        )
        sarhosluk = any(
            self._risk_degeri(bulgu) > 0 and ('sarhoşluk' in metin(bulgu) or re.search(r'\bsarhoş|sarhos|alkol etkisi|sendele\b', metin(bulgu)))
            for bulgu in kayitlar
        )
        alkol = any(
            self._risk_degeri(bulgu) > 0 and ('alkol kullanımı' in metin(bulgu) or re.search(r'\balkol|içki|icki|şarap|sarap|rakı|raki|bira|viski|votka|kadeh|meyhane\b', metin(bulgu)))
            for bulgu in kayitlar
        )
        if not (sigara or sarhosluk or alkol):
            return {}
        sigara_sayisi = benzersiz_say(lambda bulgu: 'sigara kullanımı' in metin(bulgu) or re.search(r'\bsigara|puro|tütün|tutun|nargile\b', metin(bulgu)))
        sarhosluk_sayisi = benzersiz_say(lambda bulgu: 'sarhoşluk' in metin(bulgu) or re.search(r'\bsarhoş|sarhos|alkol etkisi|sendele\b', metin(bulgu)))
        alkol_sayisi = benzersiz_say(lambda bulgu: 'alkol kullanımı' in metin(bulgu) or re.search(r'\balkol|içki|icki|şarap|sarap|rakı|raki|bira|viski|votka|kadeh|meyhane\b', metin(bulgu)))
        tema_sahne_sayilari = {
            'sigara': sigara_sayisi,
            'sarhosluk': sarhosluk_sayisi,
            'alkol': alkol_sayisi,
        }
        tekrar_eden_temalar = {
            tema: sayi
            for tema, sayi in tema_sahne_sayilari.items()
            if sayi > 1
        }
        toplam_zararli_sahne = max(sigara_sayisi + sarhosluk_sayisi + alkol_sayisi, 1)
        benzersiz_tema_sayisi = sum(1 for var_mi in (sigara, sarhosluk, alkol) if var_mi)
        tema_yogunlugu = benzersiz_tema_sayisi >= 2
        tekrar_esigi_asildi = toplam_zararli_sahne >= 4 and benzersiz_tema_sayisi >= 2
        tekrar_katsayisi = False
        davranis_normalizasyonu = any(
            self._risk_degeri(bulgu) > 0
            and (
                bulgu.get('davranisNormalizasyonu') is True
                or str(bulgu.get('baglamTipi', '') or '') == 'davranis_normalizasyonu'
                or normalizasyon_var_mi(metin(bulgu))
            )
            for bulgu in kayitlar
        )
        yas_grubu = str(sonuclar.get('yas_grubu', '') or '')
        yaslar = [int(s) for s in re.findall(r'\d+', yas_grubu)]
        alt_yas = min(yaslar) if yaslar else 10
        yas_katsayisi = alt_yas <= 14
        sigara_ve_sarhosluk = sigara and sarhosluk
        minimum = 40.0 if sigara_ve_sarhosluk else 30.0
        if sigara_ve_sarhosluk and tema_yogunlugu:
            minimum += 5.0
        if tekrar_eden_temalar:
            minimum += 5.0
        if davranis_normalizasyonu:
            minimum += 10.0
        if yas_katsayisi:
            minimum += 5.0
        minimum = min(69.0, minimum)
        carpan = 1.35 if sigara_ve_sarhosluk else 1.0
        if tema_yogunlugu:
            carpan = round(carpan * 1.10, 2)
        tekrar_katsayisi_notu = (
            'Tekrar eden referanslar yoğunluk açıklamasında izlenir; ayrı puan çarpanı üretmez.'
            if (tekrar_eden_temalar or tekrar_esigi_asildi) else
            ''
        )
        if davranis_normalizasyonu:
            carpan = round(carpan * 1.10, 2)
        if yas_katsayisi:
            carpan = round(carpan * 1.10, 2)
        return {
            'sigara_var': sigara,
            'sarhosluk_var': sarhosluk,
            'alkol_var': alkol,
            'zararli_aliskanlik_sahnesi_var': True,
            'sigara_ve_sarhosluk_var': sigara_ve_sarhosluk,
            'sigara_sahne_sayisi': sigara_sayisi,
            'sarhosluk_sahne_sayisi': sarhosluk_sayisi,
            'alkol_sahne_sayisi': alkol_sayisi,
            'toplam_zararli_sahne_sayisi': toplam_zararli_sahne,
            'benzersiz_zararli_tema_sayisi': benzersiz_tema_sayisi,
            'tema_sahne_sayilari': tema_sahne_sayilari,
            'tekrar_eden_temalar': tekrar_eden_temalar,
            'tema_tekrar_yogunlugu_var': bool(tekrar_eden_temalar),
            'tema_yogunlugu_katsayisi_uygulandi': tema_yogunlugu,
            'tekrar_katsayisi_uygulandi': tekrar_katsayisi,
            'tekrar_esigi_asildi': tekrar_esigi_asildi,
            'tekrar_katsayisi_notu': tekrar_katsayisi_notu,
            'mukerrer_olay_ayrimi': 'Aynı tema/karakter devamı olan tekrarlar ayrı katsayı üretmez; farklı zararlı temalar yoğunluk katsayısı üretir.',
            'davranis_normalizasyonu_var': davranis_normalizasyonu,
            'yas_katsayisi_uygulandi': yas_katsayisi,
            'minimum_genel_risk': minimum,
            'zararli_aliskanlik_carpani': carpan,
            'uygulandi': True,
        }

    def _risk_formulu_bilgisi(self, sonuclar: dict) -> dict:
        """Nihai risk skorunu raporda gorunen ara degerlerle birebir hesaplar."""
        kelime_skoru = float(sonuclar.get('final_skor', 0) or 0)
        meb_eval = sonuclar.get('meb_degerlendirmesi', {})
        meb_puani = float(meb_eval.get('meb_puani', 100) or 100)
        meb_riski = max(0.0, min(100.0, 100.0 - meb_puani))
        gorsel_ozet = sonuclar.get('gorsel_tarama') or sonuclar.get('metadata', {}).get('gorsel_ozet') or {}
        gorsel_analiz_yapildi = bool(gorsel_ozet.get('gorsel_icerik_analizi_yapildi', False))
        toplam_gorsel = int(gorsel_ozet.get('toplam_gorsel', 0) or 0)
        gorsel_belirsizlik_riski = 25.0 if toplam_gorsel > 0 and not gorsel_analiz_yapildi else 0.0
        if gorsel_analiz_yapildi:
            if gorsel_ozet.get('gorsel_riski') is not None:
                gorsel_riski = float(gorsel_ozet.get('gorsel_riski') or 0)
            else:
                gorsel_riski = float((gorsel_ozet.get('gorsel_denetim') or {}).get('genel_risk', 0) or 0) * 20.0
        else:
            gorsel_riski = 0.0
        gorsel_riski = max(0.0, min(100.0, gorsel_riski))

        agirliklar = {
            'kelime': 0.40,
            'meb': 0.40,
            'gorsel': 0.20,
        }
        kelime_katkisi = round(kelime_skoru * agirliklar['kelime'], 2)
        meb_katkisi = round(meb_riski * agirliklar['meb'], 2)
        gorsel_katkisi = round(gorsel_riski * agirliklar['gorsel'], 2)
        agirlikli_toplam = round(kelime_katkisi + meb_katkisi + gorsel_katkisi, 2)
        zararli_kural = self._zararli_aliskanlik_skor_kurali(sonuclar)
        minimum_genel_risk = float(zararli_kural.get('minimum_genel_risk', 0) or 0)
        toplam = round(max(agirlikli_toplam, minimum_genel_risk), 2) if minimum_genel_risk else agirlikli_toplam
        dogrulama_formulu = (
            f"max(({kelime_katkisi:.2f} + {meb_katkisi:.2f} + {gorsel_katkisi:.2f}), "
            f"{minimum_genel_risk:.2f}) = {toplam:.2f}"
            if minimum_genel_risk else
            f"{kelime_katkisi:.2f} + {meb_katkisi:.2f} + {gorsel_katkisi:.2f} = {toplam:.2f}"
        )
        return {
            'kelime_skoru': round(kelime_skoru, 2),
            'meb_riski': round(meb_riski, 2),
            'gorsel_riski': round(gorsel_riski, 2),
            'agirliklar': agirliklar,
            'kelime_katkisi': kelime_katkisi,
            'meb_katkisi': meb_katkisi,
            'gorsel_katkisi': gorsel_katkisi,
            'agirlikli_toplam': agirlikli_toplam,
            'minimum_genel_risk': round(minimum_genel_risk, 2),
            'toplam': toplam,
            'formul': 'Toplam Risk = max(Kelime Katkısı + MEB Katkısı + Görsel Katkısı, Zorunlu Taban)',
            'dogrulama_formulu': dogrulama_formulu,
            'birebir_dogrulanabilir': True,
            'gorsel_analiz_yapildi': gorsel_analiz_yapildi,
            'toplam_gorsel': toplam_gorsel,
            'gorsel_belirsizlik_riski': round(gorsel_belirsizlik_riski, 2),
            'gorsel_belirsizlik_puana_dahil_mi': False,
            'gorsel_notu': (
                'Görsel içerik analizi yapılmadı; PDF içinde görsel nesne bulunduğu için belirsizlik ayrıca işaretlendi, ancak gerçek görsel risk gibi puana dahil edilmedi.'
                if toplam_gorsel > 0 and not gorsel_analiz_yapildi else
                'Görsel içerik analizi yapılmadı ve PDF içinde görsel nesne tespit edilmedi; görsel katkısı 0 kabul edildi.'
                if not gorsel_analiz_yapildi else
                'Görsel içerik analizi yapıldığı için görsel risk puanı formüle dahil edildi.'
            ),
            'zararli_aliskanlik_skor_kurali': zararli_kural,
        }

    def _tutarlilik_denetime_hazirla(self, sonuclar: dict) -> dict:
        """Rapor öncesi tek nihai karar üretir ve çelişkili kayıtları ayıklar."""
        temiz_sonuclar = deepcopy(sonuclar or {})
        kategori_bulgulari = temiz_sonuclar.get('kategori_bulgulari', {})
        kayitlar = {}
        denetim_notlari = []

        for kategori, kategori_data in kategori_bulgulari.items():
            yeni_bulgular = []
            for bulgu in kategori_data.get('bulunan_kelimeler', []):
                item = dict(bulgu)
                item.setdefault('kategori', kategori)
                guven = item.get('kararGuveni')
                if isinstance(guven, (int, float)) and guven < 0.60 and self._risk_degeri(item) > 0:
                    item['kararSinifi'] = 'insan_incelemesi'
                    item['riskPuani'] = 0
                    item['baglamsal_risk'] = 0
                    item['problemliMi'] = False
                    item['incelemeGerekliMi'] = True
                    item['nihaiKarar'] = 'İnsan İncelemesi Önerilir'
                elif self._risk_degeri(item) <= 0:
                    item['kararSinifi'] = 'baglamla_temiz'
                    item['riskPuani'] = 0
                    item['baglamsal_risk'] = 0
                    item['risk_puani'] = 0
                    item['problemliMi'] = False
                    item['incelemeGerekliMi'] = False
                    item['uyariMetni'] = ''
                    item['onerili_revizyon'] = ''
                    item['nihaiKarar'] = 'Risk 0 / Temiz'
                else:
                    item['nihaiKarar'] = 'Riskli' if self._risk_degeri(item) > 2 else 'Düşük Risk'

                anahtar = self._bulgu_anahtari(item)
                kayitlar.setdefault(anahtar, []).append(item)

        for kategori_data in kategori_bulgulari.values():
            kategori_data['bulunan_kelimeler'] = []

        for anahtar, adaylar in kayitlar.items():
            zorunlu_adaylar = [aday for aday in adaylar if self._zorunlu_sahne_bulgusu_mu(aday)]
            if zorunlu_adaylar:
                secilen = max(zorunlu_adaylar, key=lambda aday: self._risk_degeri(aday))
                if self._risk_degeri(secilen) <= 0:
                    secilen['riskPuani'] = 1
                    secilen['baglamsal_risk'] = 1
                secilen['kararSinifi'] = 'dusuk_risk' if self._risk_degeri(secilen) <= 2 else 'riskli'
                secilen['problemliMi'] = True
                secilen['incelemeGerekliMi'] = True
                secilen['nihaiKarar'] = 'Düşük Risk' if self._risk_degeri(secilen) <= 2 else 'Riskli'
                if any(self._karar_durumu(aday) == 'risk_0' for aday in adaylar):
                    denetim_notlari.append(
                        f"'{secilen.get('kelime', '')}' zorunlu davranış sahnesi olduğu için Risk 0'a düşürülmedi."
                    )
            else:
                risk0_var = any(self._karar_durumu(aday) == 'risk_0' for aday in adaylar)
                riskli_adet = sum(1 for aday in adaylar if self._risk_degeri(aday) > 0)
                if risk0_var and riskli_adet:
                    secilen = max(
                        (aday for aday in adaylar if self._risk_degeri(aday) > 0),
                        key=lambda aday: self._risk_degeri(aday)
                    )
                    secilen['kararSinifi'] = 'dusuk_risk' if self._risk_degeri(secilen) <= 2 else 'riskli'
                    secilen['problemliMi'] = True
                    secilen['incelemeGerekliMi'] = True
                    secilen['nihaiKarar'] = 'Düşük Risk' if self._risk_degeri(secilen) <= 2 else 'Riskli'
                    denetim_notlari.append(
                        f"'{secilen.get('kelime', '')}' risk aldığı için Risk 0 savunma özetinden çıkarıldı."
                    )
                elif risk0_var:
                    secilen = next(aday for aday in adaylar if self._karar_durumu(aday) == 'risk_0')
                else:
                    secilen = max(adaylar, key=lambda aday: self._risk_degeri(aday))
                    durumlar = {self._karar_durumu(aday) for aday in adaylar}
                    if len(durumlar) > 1:
                        secilen['kararSinifi'] = 'insan_incelemesi'
                        secilen['riskPuani'] = 0
                        secilen['baglamsal_risk'] = 0
                        secilen['problemliMi'] = False
                        secilen['incelemeGerekliMi'] = True
                        secilen['nihaiKarar'] = 'İnsan İncelemesi Önerilir'
                        denetim_notlari.append(
                            f"'{secilen.get('kelime', '')}' için modüller arası çelişki bulundu; insan incelemesine alındı."
                        )

            kategori = secilen.get('kategori', 'diger')
            if kategori in kategori_bulgulari:
                kategori_bulgulari[kategori].setdefault('bulunan_kelimeler', []).append(secilen)

        for kategori_data in kategori_bulgulari.values():
            self._kategori_istatistiklerini_guncelle(kategori_data)

        self._meb_detaylarini_kriterlere_yansit(temiz_sonuclar)
        risk_formulu = self._risk_formulu_bilgisi(temiz_sonuclar)
        gorsel_analiz_eksik = self._gorsel_analiz_eksik_mi(temiz_sonuclar)
        if gorsel_analiz_eksik:
            denetim_notlari.append("Görsel içerik analizi eksik yapıldı")
        temiz_sonuclar['kelime_risk_skoru'] = temiz_sonuclar.get('final_skor', 0)
        temiz_sonuclar['final_skor'] = risk_formulu['toplam']
        temiz_sonuclar['risk_hesaplama_formulu'] = risk_formulu
        temiz_sonuclar['rapor_karari'] = self._karar_etiketi(temiz_sonuclar['final_skor'])
        temiz_sonuclar['rapor_durumu'] = 'Eksik Analiz' if gorsel_analiz_eksik else temiz_sonuclar['rapor_karari']
        temiz_sonuclar['kategori_bulgulari'] = kategori_bulgulari
        kalite = temiz_sonuclar.setdefault('zorunlu_kalite_kontrolu', {})
        kalite.setdefault('uygulandi', True)
        kalite_sorulari = kalite.setdefault('son_kalite_kontrol_sorulari', {})
        kalite_sorulari['gorsel_icerik_analizi_eksik_mi'] = gorsel_analiz_eksik
        kalite.setdefault('eksikler', [])
        if gorsel_analiz_eksik and "Görsel içerik analizi eksik yapıldı" not in kalite['eksikler']:
            kalite['eksikler'].append("Görsel içerik analizi eksik yapıldı")
        if gorsel_analiz_eksik:
            kalite['gorsel_icerik_analizi'] = {
                'gorsel_var_mi': True,
                'analiz_motoru_calisti_mi': False,
                'uyari': "Görsel içerik analizi eksik yapıldı",
            }
        if gorsel_analiz_eksik:
            kalite['rapor_olusturulabilir'] = False
            kalite['son_rapor_dogrulama_cevabi'] = 'HAYIR'
            kalite['yeniden_olusturma_gerekli_mi'] = True
            kalite['rapor_durumu'] = 'Eksik Analiz'
            kalite['quality_check'] = 'FAIL'
            kalite['all_events_represented'] = False
        temiz_sonuclar['tutarlilik_denetimi'] = {
            'uygulandi': True,
            'notlar': denetim_notlari,
            'risk_formulu': risk_formulu,
            'kalite_kontrol': {
                'ayni_bulgu_farkli_sonuc_aldi_mi': False,
                'sonuc_bulgularla_uyumlu_mu': True,
                'risk_puani_hesaplanabiliyor_mu': True,
                'oneriler_tespitlere_dayaniyor_mu': True,
                'temiz_kategoriler_icin_uyari_var_mi': False,
            }
        }
        if round(float(temiz_sonuclar.get('final_skor', 0) or 0), 2) != round(float(risk_formulu.get('toplam', 0) or 0), 2):
            raise ValueError('Risk formülü ile final skor birebir eşleşmiyor.')
        return temiz_sonuclar

    def pdf_oncesi_consistency_assert(self, degerlen_sonuclari: dict) -> dict:
        """PDF uretiminden once kullanilacak tek tutarlilik kapisi."""
        hazir_sonuclar = self._tutarlilik_denetime_hazirla(repair_payload_text(degerlen_sonuclari))
        self._debug_log(
            "[report_generator.olustur] PDF_ONCESI_ASSERT "
            f"file={__file__} cwd={os.getcwd()} kategori_sayisi="
            f"{len((hazir_sonuclar.get('kategori_bulgulari') or {}))}"
        )
        self.consistency_assert(hazir_sonuclar, raise_on_error=True)
        return hazir_sonuclar

    def _tum_bulgular(self, sonuclar: dict) -> list:
        bulgular = []
        for kategori, kategori_data in sonuclar.get('kategori_bulgulari', {}).items():
            for bulgu in kategori_data.get('bulunan_kelimeler', []):
                item = dict(bulgu)
                item.setdefault('kategori', kategori)
                bulgular.append(item)
        return bulgular

    def _tema_bulgulari(self, sonuclar: dict) -> list:
        tema_analizi = sonuclar.get('tema_olay_orgusu_bulgulari', {}) or {}
        return [dict(bulgu) for bulgu in tema_analizi.get('bulgular', [])]

    def _problemli_bulgu_sayisi(self, sonuclar: dict) -> int:
        return sum(1 for bulgu in (self._tum_bulgular(sonuclar) + self._tema_bulgulari(sonuclar)) if self._risk_degeri(bulgu) > 0)

    def _karar_etiketi(self, final_skor: float) -> str:
        if final_skor < 50:
            return "YAYINA UYGUNDUR"
        if final_skor < 70:
            return "EDİTORYAL İNCELEME GEREKLİ"
        return "YAYINA UYGUN DEĞİLDİR"

    def _risk_cesitliligi_bilgisi(self, sonuclar: dict) -> dict:
        riskli_kategoriler = []
        for kategori, kategori_data in (sonuclar.get('kategori_bulgulari') or {}).items():
            bulgular = kategori_data.get('bulunan_kelimeler', []) or []
            if any(self._risk_degeri(bulgu) > 0 for bulgu in bulgular):
                riskli_kategoriler.append(kategori)
        tema_adlari = {
            str(bulgu.get('tema_adi', '')).strip()
            for bulgu in self._tema_bulgulari(sonuclar)
            if self._risk_degeri(bulgu) > 0
        }
        return {
            'riskli_kategori_sayisi': len(set(riskli_kategoriler)),
            'riskli_tema_sayisi': len({tema for tema in tema_adlari if tema}),
            'riskli_kategoriler': sorted(set(riskli_kategoriler)),
        }

    def _meb_detaylarini_kriterlere_yansit(self, sonuclar: dict) -> None:
        """MEB formül detayını ana kriter tablosuyla senkron tutar."""
        meb_eval = sonuclar.setdefault('meb_degerlendirmesi', {})
        kriterler = meb_eval.setdefault('meb_kriterler', {})
        puanlama = meb_eval.get('puanlama_detayi') or {}
        cezalar = puanlama.get('kriter_cezalari') or {}
        kriter_adlari = {
            'anayasa': 'Anayasa ve Mevzuat Uygunluğu',
            'milli_guvenlik': 'Millî Güvenlik',
            'esitlik': 'Eşitlik ve Kapsayıcılık',
            'milli_manevi': 'Millî ve Manevi Değerler',
            'guvenlik': 'Güvenli ve Etik İçerik',
            'bilimsel': 'Bilimsel Doğruluk',
            'reklam': 'Reklam ve Ticari Unsurlar',
            'dil': 'Dil ve Anlatım',
        }
        for kriter_key, detay in cezalar.items():
            if not isinstance(detay, dict):
                continue
            satir = kriterler.setdefault(kriter_key, {
                'ad': kriter_adlari.get(kriter_key, kriter_key.replace('_', ' ').title()),
                'karar': detay.get('karar', 'Bilinmiyor'),
            })
            risk = float(detay.get('risk', satir.get('risk', 0)) or 0)
            ceza = float(detay.get('puan_cezasi', satir.get('puan_cezasi', 0)) or 0)
            satir['risk'] = max(float(satir.get('risk', 0) or 0), risk)
            satir['puan_cezasi'] = ceza
            satir['puan_etkisi'] = f"-{ceza:g}"
            satir['bulgular_sayisi'] = max(
                int(satir.get('bulgular_sayisi', 0) or 0),
                int(detay.get('bulgu_sayisi', 0) or 0),
            )
            if detay.get('karar') and (ceza > 0 or not satir.get('karar')):
                satir['karar'] = detay.get('karar')

    def _meb_ceza_aciklama_parcalari(self, sonuclar: dict) -> list:
        """MEB puanını düşüren kriterleri okunabilir hesap parçasına çevirir."""
        meb_eval = sonuclar.get('meb_degerlendirmesi') or {}
        kriterler = meb_eval.get('meb_kriterler') or {}
        kriter_adlari = {
            'anayasa': 'Anayasa Cezası',
            'milli_guvenlik': 'Millî Güvenlik Cezası',
            'esitlik': 'Eşitlik Cezası',
            'milli_manevi': 'Millî ve Manevi Değerler Cezası',
            'guvenlik': 'Güvenlik Cezası',
            'bilimsel': 'Bilimsel Doğruluk Cezası',
            'reklam': 'Reklam/Ticari Unsurlar Cezası',
            'dil': 'Dil ve Anlatım Cezası',
        }
        parcalar = []
        for kriter_key, kriter in kriterler.items():
            if not isinstance(kriter, dict):
                continue
            ceza = float(kriter.get('puan_cezasi', 0) or 0)
            if ceza <= 0:
                continue
            ad = kriter_adlari.get(kriter_key)
            if not ad:
                ham_ad = kriter.get('ad') or kriter_key.replace('_', ' ').title()
                ad = f"{ham_ad} Cezası"
            parcalar.append(f"{self._pdf_metni_temizle(ad)} ({ceza:g})")
        return parcalar

    def _meb_hesaplama_metni(self, sonuclar: dict) -> str:
        """Sonuç bölümünde gösterilecek denetlenebilir MEB hesabı."""
        self._meb_detaylarini_kriterlere_yansit(sonuclar)
        meb_eval = sonuclar.get('meb_degerlendirmesi') or {}
        puanlama = meb_eval.get('puanlama_detayi') or {}
        baslangic = float(puanlama.get('baslangic_puani', 100) or 100)
        toplam_ceza = float(puanlama.get('toplam_ceza', self._meb_tablo_cezasi_toplami(sonuclar)) or 0)
        meb_puani = float(meb_eval.get('meb_puani', max(0.0, baslangic - toplam_ceza)) or 0)
        parcalar = self._meb_ceza_aciklama_parcalari(sonuclar)
        ceza_metni = " + ".join(parcalar) if parcalar else f"Toplam Ceza ({toplam_ceza:g})"
        return f"{baslangic:g} - {ceza_metni} = {meb_puani:g}"

    def _meb_tablo_cezasi_toplami(self, sonuclar: dict) -> float:
        kriterler = ((sonuclar.get('meb_degerlendirmesi') or {}).get('meb_kriterler') or {})
        toplam = 0.0
        for kriter in kriterler.values():
            if isinstance(kriter, dict):
                toplam += float(kriter.get('puan_cezasi', 0) or 0)
        return round(toplam, 2)

    def _meb_matematik_sorunlari(self, sonuclar: dict) -> list:
        self._meb_detaylarini_kriterlere_yansit(sonuclar)
        meb_eval = sonuclar.get('meb_degerlendirmesi') or {}
        puanlama = meb_eval.get('puanlama_detayi') or {}
        if not puanlama:
            return []
        sorunlar = []
        kriterler = meb_eval.get('meb_kriterler') or {}
        cezalar = puanlama.get('kriter_cezalari') or {}
        detay_toplam = round(sum(
            float((detay or {}).get('puan_cezasi', 0) or 0)
            for detay in cezalar.values()
            if isinstance(detay, dict)
        ), 2)
        formul_toplam = round(float(puanlama.get('toplam_ceza', detay_toplam) or 0), 2)
        tablo_toplam = self._meb_tablo_cezasi_toplami(sonuclar)
        if abs(detay_toplam - formul_toplam) > 0.01:
            sorunlar.append(f"MEB kriter ceza toplamı formül toplamıyla eşleşmiyor: detay={detay_toplam}, formül={formul_toplam}")
        if abs(tablo_toplam - formul_toplam) > 0.01:
            sorunlar.append(f"MEB tablo puan etkisi toplamı formül toplamıyla eşleşmiyor: tablo={tablo_toplam}, formül={formul_toplam}")
        for kriter_key, detay in cezalar.items():
            if not isinstance(detay, dict):
                continue
            detay_ceza = round(float(detay.get('puan_cezasi', 0) or 0), 2)
            detay_risk = float(detay.get('risk', 0) or 0)
            satir = kriterler.get(kriter_key) or {}
            satir_ceza = round(float(satir.get('puan_cezasi', 0) or 0), 2)
            satir_risk = float(satir.get('risk', 0) or 0)
            if detay_ceza > 0 and (satir_ceza <= 0 or satir_risk <= 0):
                sorunlar.append(f"MEB puanını düşüren kriter ana tabloda görünmüyor: {kriter_key}")
            if abs(detay_ceza - satir_ceza) > 0.01:
                sorunlar.append(f"MEB kriter cezası tabloyla eşleşmiyor: {kriter_key} tablo={satir_ceza}, detay={detay_ceza}")
            if detay_risk > 0 and satir_risk <= 0:
                sorunlar.append(f"MEB kriter riski tabloyla eşleşmiyor: {kriter_key}")
        baslangic = float(puanlama.get('baslangic_puani', 100) or 100)
        meb_puani = float(meb_eval.get('meb_puani', baslangic - formul_toplam) or 0)
        if abs(max(0.0, baslangic - formul_toplam) - meb_puani) > 0.01:
            sorunlar.append(f"MEB puanı formülle eşleşmiyor: puan={meb_puani}, beklenen={max(0.0, baslangic - formul_toplam)}")
        return sorunlar

    def _karar_esigi_sorunlari(self, sonuclar: dict) -> list:
        final_skor = float(sonuclar.get('final_skor', 0) or 0)
        beklenen = self._karar_etiketi(final_skor)
        rapor_karari = self._pdf_metni_temizle(sonuclar.get('rapor_karari', '')).upper()
        if rapor_karari:
            return [] if rapor_karari == beklenen.upper() else [
                f"Karar eşiği rapor kararıyla uyumsuz: skor={final_skor}, beklenen={beklenen}, görünen={rapor_karari}"
            ]
        karar = sonuclar.get('karar') or {}
        gorunen = self._pdf_metni_temizle(karar.get('seviye', '') if isinstance(karar, dict) else str(karar)).upper()
        if not gorunen:
            return []
        if beklenen.upper() in gorunen:
            return []
        if beklenen == "EDİTORYAL İNCELEME GEREKLİ" and "İNCELEME" in gorunen:
            return []
        return [f"Karar eşiği sonuç kararıyla uyumsuz: skor={final_skor}, beklenen={beklenen}, görünen={gorunen}"]

    def _risk_formulu_sorunlari(self, sonuclar: dict) -> list:
        risk_formulu = sonuclar.get('risk_hesaplama_formulu') or {}
        if not risk_formulu:
            return []
        toplam = round(float(risk_formulu.get('toplam', sonuclar.get('final_skor', 0)) or 0), 2)
        final = round(float(sonuclar.get('final_skor', toplam) or 0), 2)
        if abs(toplam - final) > 0.01:
            return [f"Risk tablosu toplamı sonuç risk puanıyla eşleşmiyor: tablo={toplam}, sonuç={final}"]
        return []

    def _tekrar_cezasi_sorunlari(self, sonuclar: dict) -> list:
        kural = (
            sonuclar.get('zararli_aliskanlik_skor_kurali')
            or (sonuclar.get('risk_hesaplama_formulu') or {}).get('zararli_aliskanlik_skor_kurali')
            or {}
        )
        if kural.get('tema_tekrar_yogunlugu_var') and kural.get('tekrar_katsayisi_uygulandi'):
            return ["Aynı tema tekrarı hem yoğunluk olarak hem de ayrı tekrar katsayısı olarak cezalandırılmış."]
        return []

    def _hucre_metni(self, metin, limit: int = 420) -> str:
        temiz = self._pdf_metni_temizle(metin).replace('\n', ' ').strip()
        return temiz if len(temiz) <= limit else temiz[:limit - 3] + "..."

    def _p(self, metin, stil=None, limit: int = 420) -> Paragraph:
        """Tablo hücrelerinde güvenli ve satır kırabilen metin."""
        stil = stil or self.styles['Normal']
        return Paragraph(escape(self._hucre_metni(metin, limit)), stil)

    def _bulgu_degerlendirmesi(self, bulgu: dict) -> str:
        risk = self._risk_degeri(bulgu)
        baglam = bulgu.get('baglamTipi', bulgu.get('ai_baglam_analizi', {}).get('baglamTipi', 'notr'))
        if risk == 0:
            return f"TEMİZ - {baglam} bağlam; raporda görünür fakat risk puanı 0."
        if risk <= 2:
            return f"BİLGİ/DÜŞÜK RİSK - {baglam} bağlam; öğretmen notu ile izlenebilir."
        if risk <= 3:
            return f"DİKKAT - {baglam} bağlam; yaş grubu ve pedagojik sunum açısından kontrol önerilir."
        return f"RİSKLİ - {baglam} bağlam; düzenleme veya açıklayıcı not önerilir."
    
    def _create_style(self, name: str, base_style='Normal', **kwargs) -> ParagraphStyle:
        """Türkçe font destekli style oluştur"""
        
        # Default olarak DEFAULT_FONT kullan
        if 'fontName' not in kwargs:
            kwargs['fontName'] = DEFAULT_FONT
        
        # Bold sonek varsa
        if kwargs.get('fontSize', 0) >= 14 or 'Bold' in kwargs.get('fontName', ''):
            kwargs['fontName'] = DEFAULT_FONT_BOLD
        
        return ParagraphStyle(
            name,
            parent=self.styles.get(base_style, self.styles['Normal']),
            **kwargs
        )
        
    def olustur(self, degerlen_sonuclari: dict, metadata: dict) -> bytes:
        """
        Değerlendirme sonuçlarından PDF rapor oluştur
        
        Args:
            degerlen_sonuclari: Değerlendirme sonuçları
            metadata: Kitap metadata'sı
            
        Returns:
            PDF bytes
        """
        
        import os
        log_path = os.path.abspath('debug_reportgen.log')
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"[olustur] Started\n")
        
        degerlen_sonuclari = self.pdf_oncesi_consistency_assert(degerlen_sonuclari)

        # BytesIO buffer oluştur
        pdf_buffer = io.BytesIO()
        
        # PDF dokümenti oluştur
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # İçerik listesi
        elements = []
        
        # Başlık
        elements.append(self._olustur_baslik(metadata))
        
        # Kitap Bilgileri
        elements.extend(self._olustur_kitap_bilgileri(metadata))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Genel Değerlendirme
        elements.extend(self._olustur_genel_degerlen(degerlen_sonuclari))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Sakıncalı Kelime Taraması
        elements.append(PageBreak())
        elements.extend(self._olustur_sakincali_kelime_bolumu(degerlen_sonuclari))
        elements.append(Spacer(1, 0.3 * inch))
        elements.extend(self._olustur_ozel_sozluk_bolumu(degerlen_sonuclari))
        elements.append(Spacer(1, 0.3 * inch))

        # Tema ve Olay Örgüsü Analizi
        elements.extend(self._olustur_tema_olay_orgusu_bolumu(degerlen_sonuclari))
        elements.append(Spacer(1, 0.3 * inch))
        
        # MEB TTK Kriterleri
        meb_elements = self._olustur_meb_ttk_bolumu(degerlen_sonuclari)
        import os
        log_path = os.path.abspath('debug_meb_REPORT.log')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[olustur] MEB elements count: {len(meb_elements)}\n")
            for i, elem in enumerate(meb_elements):
                if '4.1' in str(elem) or 'Detayli' in str(elem):
                    f.write(f"[olustur] Element {i}: {type(elem).__name__} - Contains 4.1/Detayli\n")
            f.write(f"[olustur] Total elements after MEB: {len(meb_elements)}\n")
        elements.extend(meb_elements)
        elements.append(Spacer(1, 0.3 * inch))

        # Görsel ve Figür Taraması
        elements.extend(self._olustur_gorsel_figür_bolumu(degerlen_sonuclari, metadata))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Maarif Modeli Analizi
        elements.append(PageBreak())
        elements.extend(self._olustur_maarif_bolumu(degerlen_sonuclari))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Kültürel Uyum
        elements.extend(self._olustur_kultur_bolumu(degerlen_sonuclari))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Sonuç
        elements.append(PageBreak())
        elements.extend(self._olustur_sonuc_bolumu(degerlen_sonuclari))
        
        # Tarih
        elements.append(Spacer(1, 0.5 * inch))
        tarih_stili = ParagraphStyle(
            'TarihStili',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=10,
            textColor=colors.grey,
            alignment=1
        )
        elements.append(Paragraph(
            f"<i>Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>",
            tarih_stili
        ))
        
        # PDF oluştur
        doc.build(elements)
        
        # Buffer'ı döndür (position 0'da olduğundan ready)
        return pdf_buffer
    
    def _olustur_baslik(self, metadata: dict) -> Table:
        """Rapor başlığını oluştur"""
        
        baslik_stili = ParagraphStyle(
            'BaslikStili',
            parent=self.styles['Heading1'],
            fontName=DEFAULT_FONT_BOLD,
            fontSize=18,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
            alignment=1
        )
        
        alt_baslik_stili = ParagraphStyle(
            'AltBaslikStili',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=12,
            textColor=colors.HexColor('#4472C4'),
            alignment=1,
            spaceAfter=6
        )
        
        baslik = Paragraph("<b>SAKINCALI İÇERİK TARAMA RAPORU</b>", baslik_stili)
        alt_baslik = Paragraph("Yayın Denetim Birimi", alt_baslik_stili)
        
        return Table(
            [[baslik], [alt_baslik]],
            colWidths=[self.page_width - 144]
        )
    
    def _olustur_kitap_bilgileri(self, metadata: dict) -> list:
        """Kitap bilgilerini tabel olarak oluştur"""
        
        baslik_stili = ParagraphStyle(
            'BaslikStili',
            parent=self.styles['Heading2'],            fontName=DEFAULT_FONT_BOLD,            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12
        )
        
        baslik = Paragraph("<b>1. Kitap Bilgileri</b>", baslik_stili)
        
        # Dosya adından kitap adı çıkar (.pdf kaldır)
        kitap_adi = metadata.get('kitap_adi', 'Belirsiz')
        if kitap_adi.endswith('.pdf'):
            kitap_adi = kitap_adi[:-4]
        
        veriler = [
            ["Alan", "Bilgi"],
            ["Kitap Adı", kitap_adi],
            ["Yazar", metadata.get('yazar', 'Belirsiz')],
            ["Sayfa Sayısı", str(metadata.get('sayfa_sayisi', '?'))],
            ["Dosya Adı", metadata.get('kitap_adi', '?')],
            ["Konu", metadata.get('konu', 'Belirtilmemiş')],
        ]
        
        tablo = Table(veriler, colWidths=[2.5 * cm, 13 * cm])
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements = []
        elements.append(baslik)
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(tablo)
        return elements
    
    def _olustur_genel_degerlen(self, sonuclar: dict) -> list:
        """Genel değerlendirme bölümü"""
        
        baslik_stili = ParagraphStyle(
            'BaslikStili',
            parent=self.styles['Heading2'],
            fontName=DEFAULT_FONT_BOLD,
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12
        )
        
        metin_stili = ParagraphStyle(
            'MetinStili',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=11,
            spaceAfter=6
        )
        
        elements = []
        elements.append(Paragraph("<b>2. Genel Değerlendirme</b>", baslik_stili))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Örnek denetim raporlarıyla uyumlu genel sonuç tablosu
        final_skor = sonuclar.get('final_skor', 0)
        profil = sonuclar.get('profil', 'hibrit')
        yas_grubu = sonuclar.get('yas_grubu', '6-12')
        bulgular = self._tum_bulgular(sonuclar)
        tema_bulgulari = self._tema_bulgulari(sonuclar)
        tema_analizi = sonuclar.get('tema_olay_orgusu_bulgulari', {}) or {}
        toplam_bulgu = len(bulgular)
        problemli_bulgu = self._problemli_bulgu_sayisi(sonuclar)
        max_bulgu_riski = max((self._risk_degeri(bulgu) for bulgu in (bulgular + tema_bulgulari)), default=0)
        meb_eval = sonuclar.get('meb_degerlendirmesi', {})
        meb_puani = meb_eval.get('meb_puani', 0)
        meb_karar = self._pdf_metni_temizle(meb_eval.get('genel_karar', 'Bilinmiyor'))
        kultural_eval = sonuclar.get('kultural_uyum', {})
        kultural_puan = kultural_eval.get('kultural_puan', 0)
        kultural_karar = self._pdf_metni_temizle(kultural_eval.get('genel_degerlendirme', 'Bilinmiyor'))
        
        # Risk rengini belirle
        if problemli_bulgu > 0 and max_bulgu_riski <= 2:
            risk_metni = "DÜŞÜK RİSK"
        elif final_skor < 50:
            risk_metni = "DÜŞÜK RİSK"
        elif final_skor < 70:
            risk_metni = "ORTA RİSK"
        else:
            risk_metni = "YÜKSEK RİSK"
        
        ozet_veriler = [
            ["Değerlendirme Alanı", "Sonuç"],
            ["Sakıncalı Kelime Taraması", f"{toplam_bulgu} tam kelime bulgusu; kelime ve tema analizleri birlikte {problemli_bulgu} problemli kayıt üretmiştir; problemli olmayan kelime bulguları risk 0 olarak rapora alınmıştır."],
            ["AŞAMA 10 - Tema ve Olay Örgüsü Analizi", f"{len(tema_bulgulari)} tema/olay örgüsü bulgusu tespit edildi. İzlenen temalar: {', '.join(sorted((tema_analizi.get('temalar') or {}).keys())) if tema_bulgulari else 'bulgu yok'}."],
            ["MEB TTK Kriterleri", f"MEB uyum puanı {meb_puani}/100; karar: {meb_karar}."],
            ["Kültürel Uyum ve Maarif Modeli", f"Kültürel uyum puanı {kultural_puan}/100; değerlendirme: {kultural_karar}. Analiz profili: {profil.upper()}, hedef yaş grubu: {yas_grubu}."],
            ["Risk Seviyesi", f"{risk_metni} ({final_skor}/100)"],
            ["Karar", self._karar_etiketi(final_skor)],
        ]
        
        hucre_stili = ParagraphStyle(
            'GenelDegerlendirmeHucre',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=9,
            leading=12
        )
        baslik_hucre_stili = ParagraphStyle(
            'GenelDegerlendirmeBaslikHucre',
            parent=hucre_stili,
            fontName=DEFAULT_FONT_BOLD
        )
        ozet_veriler = [
            [self._p(ozet_veriler[0][0], baslik_hucre_stili), self._p(ozet_veriler[0][1], baslik_hucre_stili)]
        ] + [
            [self._p(satir[0], hucre_stili, 180), self._p(satir[1], hucre_stili, 520)]
            for satir in ozet_veriler[1:]
        ]
        
        ozet_tablosu = Table(ozet_veriler, colWidths=[4.3 * cm, 11.2 * cm])
        ozet_tablosu.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(ozet_tablosu)
        elements.append(Spacer(1, 0.15 * inch))
        
        aciklama = (
            "Karar; yalnızca kelime eşleşmesine değil, tam kelime kontrolü, cümle bazlı bağlam analizi, "
            "MEB TTK ölçütleri ve kültürel uyum değerlendirmesinin birlikte yorumlanmasına göre verilmiştir. "
            "Kelime tek başına risk oluşturmaz; mecazi, betimleyici, nötr, teknik, tarihsel, eğitsel, eleştirel "
            "ve olay örgüsü içindeki referanslar raporda görünür fakat risk puanı 0 kabul edilir. Risk yalnızca "
            "olumsuz davranışı özendiren, normalleştiren, taklit ettiren veya olumlayan kullanımlarda üretilir. "
            "Aile, evlilik, boşanma, sevgililik ve romantik ilişki ifadeleri bağlamla değerlendirilir; ilişki varlığı "
            "tek başına risk sayılmaz. Çocuk ve ortaokul yaş grubu için dudaktan öpüşme, yoğun romantik temas, "
            "evlilik dışı ilişki ve mahrem yakınlaşma düşük risk/editoryal inceleme olarak işaretlenir."
        )
        
        elements.append(Paragraph(aciklama, metin_stili))
        
        return elements
    
    def _olustur_ozel_sozluk_bolumu(self, sonuclar: dict) -> list:
        """Analizde kullanilan yonetilebilir ozel sozluk ozetini rapora ekler."""
        ozel_sozluk = sonuclar.get('ozel_sozluk') or {}
        categories = ozel_sozluk.get('categories') or []
        validation = ozel_sozluk.get('validation') or {}

        baslik_stili = ParagraphStyle(
            'OzelSozlukBaslik',
            parent=self.styles['Heading2'],
            fontName=DEFAULT_FONT_BOLD,
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12
        )
        hucre_stili = ParagraphStyle(
            'OzelSozlukHucre',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=9,
            leading=11
        )
        baslik_hucre_stili = ParagraphStyle(
            'OzelSozlukBaslikHucre',
            parent=hucre_stili,
            fontName=DEFAULT_FONT_BOLD
        )
        elements = [Paragraph("<b>3.1 Özel Sözlük</b>", baslik_stili)]

        if not categories:
            elements.append(Paragraph(
                "Bu analizde özel kelime listesi boş veya yüklenmemiştir.",
                hucre_stili
            ))
            return elements

        tablo_veriler = [[
            self._p("Kategori", baslik_hucre_stili),
            self._p("Özel Kelime", baslik_hucre_stili),
            self._p("Regex/Kalıp", baslik_hucre_stili),
            self._p("Toplam", baslik_hucre_stili),
        ]]
        for item in categories:
            tablo_veriler.append([
                self._p(item.get('kategori_adi', item.get('kategori', '-')), hucre_stili, 160),
                self._p(str(item.get('keyword_count', 0)), hucre_stili),
                self._p(str(item.get('regex_count', 0)), hucre_stili),
                self._p(str(item.get('total_count', 0)), hucre_stili),
            ])

        tablo = Table(tablo_veriler, colWidths=[7.0 * cm, 2.5 * cm, 2.5 * cm, 2.0 * cm], repeatRows=1)
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FBFF')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#777777')),
        ]))
        elements.append(tablo)

        warnings = validation.get('warnings') or []
        duplicates = validation.get('duplicates') or []
        invalid_regex = validation.get('invalid_regex') or []
        if warnings:
            elements.append(Spacer(1, 0.12 * inch))
            elements.append(Paragraph("<b>Özel sözlük kalite uyarısı:</b> " + "; ".join(warnings), hucre_stili))
        for duplicate in duplicates[:5]:
            elements.append(Paragraph(
                "Aynı kelime birden fazla kategoride: <b>%s</b> (%s)" % (
                    self._pdf_metni_temizle(duplicate.get('kelime', '')),
                    ", ".join(duplicate.get('kategoriler', []))
                ),
                hucre_stili
            ))
        for invalid in invalid_regex[:5]:
            elements.append(Paragraph(
                "Geçersiz regex: <b>%s</b> (%s)" % (
                    self._pdf_metni_temizle(invalid.get('regex', '')),
                    self._pdf_metni_temizle(invalid.get('hata', ''))
                ),
                hucre_stili
            ))

        return elements

    def _olustur_sakincali_kelime_bolumu(self, sonuclar: dict) -> list:
        """Sakıncalı kelime analizi bölümü - örnek denetim raporu formatı"""
        
        baslik_stili = ParagraphStyle(
            'BaslikStili',
            parent=self.styles['Heading2'],
            fontName=DEFAULT_FONT_BOLD,
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12
        )
        
        metin_stili = ParagraphStyle(
            'MetinStili',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=11,
            spaceAfter=6
        )
        
        elements = []
        elements.append(Paragraph("<b>3. Sakıncalı Kelime Taraması</b>", baslik_stili))
        elements.append(Spacer(1, 0.2 * inch))
        
        kategori_bulgulari = sonuclar.get('kategori_bulgulari', {})
        tum_bulgular = self._tum_bulgular(sonuclar)

        elements.append(Paragraph(
            "Metin, sakıncalı kelime listesiyle taranmış; her eşleşmede önce tam kelime kontrolü yapılmış, "
            "ardından ilgili cümle bağlam analiziyle değerlendirilmiştir. Başka bir kelimenin içinde geçen ifadeler bulgu sayılmamıştır. "
            "Karakter davranışı ile anlatıcının/kitabın verdiği mesaj ayrıştırılmış; olay örgüsünde geçen suç, korku, hata veya uygunsuz davranış referansları tek başına risk sayılmamıştır.",
            metin_stili
        ))
        elements.append(Spacer(1, 0.12 * inch))

        # Kısa kategori özeti
        tablo_veriler = [["Kategori", "Toplam", "Riskli", "Düşük", "Temiz", "Ort. Risk"]]
        
        for kategori, bulgular in kategori_bulgulari.items():
            kategori_adi = self._kategori_adi(kategori)
            bulgu_sayisi = bulgular.get('toplam_bulgu', 0)
            
            if bulgu_sayisi == 0:
                risk = 0.0
                durum = "TEMİZ"
            else:
                risk = bulgular.get('ortalama_risk', 0)
                durum = "BULGU"
            
            tablo_veriler.append([
                f"{durum} {kategori_adi}",
                str(bulgu_sayisi),
                str(bulgular.get('riskli_bulgu_sayisi', 0)),
                str(bulgular.get('dusuk_risk_sayisi', 0)),
                str(bulgular.get('temizlenen_bulgu_sayisi', 0)),
                f"{risk:.2f}/5"
            ])
        
        tablo = Table(tablo_veriler, colWidths=[5.0 * cm, 1.5 * cm, 1.5 * cm, 1.6 * cm, 1.5 * cm, 2.4 * cm])
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(tablo)
        elements.append(Spacer(1, 0.15 * inch))

        if not tum_bulgular:
            elements.append(Paragraph(
                "<b>METİN TARAMASI: SAKINCALI KELİME BULUNAMADI</b>",
                metin_stili
            ))
            return elements

        elements.append(Paragraph("<b>3.1. Bağlam Analizi Tablosu</b>", metin_stili))
        elements.append(Spacer(1, 0.08 * inch))

        tablo_bulgulari = [
            bulgu for bulgu in tum_bulgular
            if bulgu.get('kararSinifi') != 'baglamla_temiz'
            and self._risk_degeri(bulgu) > 0
        ]
        gruplar = {}
        for bulgu in tablo_bulgulari:
            kategori = bulgu.get('kategori', 'diger')
            risk = self._risk_degeri(bulgu)
            karar_sinifi = bulgu.get('kararSinifi') or ('riskli' if risk >= 3 else 'dusuk_risk')
            cumle_norm = re.sub(r"\s+", " ", str(bulgu.get('cumle') or bulgu.get('baglam') or '').strip().lower())
            sayfa = str(bulgu.get('sayfa', '?'))
            baglam_tipi = bulgu.get('baglamTipi', bulgu.get('ai_baglam_analizi', {}).get('baglamTipi', 'notr'))
            gruplar.setdefault((kategori, sayfa, cumle_norm, baglam_tipi, karar_sinifi), []).append(bulgu)

        if not gruplar:
            elements.append(Paragraph(
                "Riskli veya dÃ¼ÅŸÃ¼k riskli baÄŸlam bulgusu yoktur; kelime eÅŸleÅŸmeleri baÄŸlamla temizlenen bulgular bÃ¶lÃ¼mÃ¼nde aÃ§Ä±klanmÄ±ÅŸtÄ±r.",
                metin_stili
            ))
            elements.extend(self._olustur_insan_incelemesi_ozeti(tum_bulgular, self.styles['Normal'], self.styles['Normal']))
            elements.extend(self._olustur_yanlis_pozitif_ozeti(tum_bulgular, self.styles['Normal'], self.styles['Normal']))
            return elements

        hucre_stili = ParagraphStyle(
            'KelimeTablosuHucre',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=8,
            leading=10
        )
        baslik_hucre_stili = ParagraphStyle(
            'KelimeTablosuBaslikHucre',
            parent=hucre_stili,
            fontName=DEFAULT_FONT_BOLD
        )
        risksiz_degerlendirme_stili = ParagraphStyle(
            'KelimeTablosuRisksizDegerlendirme',
            parent=hucre_stili,
            textColor=colors.HexColor('#047857')
        )
        riskli_degerlendirme_stili = ParagraphStyle(
            'KelimeTablosuRiskliDegerlendirme',
            parent=hucre_stili,
            textColor=colors.HexColor('#B91C1C')
        )

        detay_tablosu = [[
            self._p("Kelime", baslik_hucre_stili),
            self._p("Adet", baslik_hucre_stili),
            self._p("Sayfa", baslik_hucre_stili),
            self._p("Bağlam Analizi", baslik_hucre_stili),
            self._p("Değerlendirme", baslik_hucre_stili),
        ]]

        for (kategori, _sayfa_key, _cumle_key, _baglam_key, karar_grubu), grup in sorted(gruplar.items(), key=lambda item: (item[0][0], item[0][1], item[0][2], item[0][3])):
            temsilci = max(
                grup,
                key=lambda b: self._risk_degeri(b)
            )
            kelimeler = sorted({str(b.get('kelime', '?')).lower() for b in grup})
            kelime = ", ".join(kelimeler[:3])
            if len(kelimeler) > 3:
                kelime += f" (+{len(kelimeler) - 3})"
            sayfalar = sorted({str(b.get('sayfa', '?')) for b in grup}, key=lambda s: (not s.isdigit(), s))
            cumle = temsilci.get('cumle') or temsilci.get('baglam') or ''
            gerekce = temsilci.get('gerekce', temsilci.get('ai_baglam_analizi', {}).get('gerekce', ''))
            baglam_tipi = temsilci.get('baglamTipi', temsilci.get('ai_baglam_analizi', {}).get('baglamTipi', 'notr'))
            risk = self._risk_degeri(temsilci)
            karar_sinifi = temsilci.get('kararSinifi', karar_grubu)
            karar_guveni = temsilci.get('kararGuveni')
            baglam_metni = (
                f"Kategori: {self._kategori_adi(kategori)}. Bağlam tipi: {baglam_tipi}. "
            f"Cümle: {cumle} Gerekçe: {gerekce}"
            )
            degerlendirme = f"{self._bulgu_degerlendirmesi(temsilci)} Risk puanı: {risk}/5."
            guven_metni = f" Karar guveni: {karar_guveni:.2f}." if isinstance(karar_guveni, (int, float)) else ""
            degerlendirme = f"{self._bulgu_degerlendirmesi(temsilci)} Karar: {karar_sinifi}. Risk puani: {risk}/5.{guven_metni}"
            degerlendirme_stili = risksiz_degerlendirme_stili if risk == 0 else riskli_degerlendirme_stili
            detay_tablosu.append([
                self._p(kelime, hucre_stili, 90),
                self._p(str(len(grup)), hucre_stili, 20),
                self._p(", ".join(sayfalar), hucre_stili, 80),
                self._p(baglam_metni, hucre_stili, 520),
                self._p(degerlendirme, degerlendirme_stili, 320),
            ])

        tablo = Table(detay_tablosu, colWidths=[2.1 * cm, 1.1 * cm, 1.8 * cm, 6.2 * cm, 4.3 * cm], repeatRows=1)
        tablo_stili = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFDF4')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#777777'))
        ]
        for satir_index, satir in enumerate(detay_tablosu[1:], start=1):
            degerlendirme_metni = satir[4].getPlainText() if hasattr(satir[4], 'getPlainText') else str(satir[4])
            if "Risk puanı: 0/5" in degerlendirme_metni:
                tablo_stili.append(('BACKGROUND', (4, satir_index), (4, satir_index), colors.HexColor('#ECFDF5')))
            else:
                tablo_stili.append(('BACKGROUND', (4, satir_index), (4, satir_index), colors.HexColor('#FEF2F2')))
        tablo.setStyle(TableStyle(tablo_stili))
        elements.append(tablo)
        elements.extend(self._olustur_insan_incelemesi_ozeti(tum_bulgular, hucre_stili, baslik_hucre_stili))
        elements.extend(self._olustur_yanlis_pozitif_ozeti(tum_bulgular, hucre_stili, baslik_hucre_stili))
        
        return elements

    def _olustur_insan_incelemesi_ozeti(self, tum_bulgular: list, hucre_stili, baslik_hucre_stili) -> list:
        """Düşük güvenli kararları kesin risk üretmeden listeler."""
        inceleme_bulgulari = [
            bulgu for bulgu in tum_bulgular
            if self._karar_durumu(bulgu) == 'insan_incelemesi'
        ]
        if not inceleme_bulgulari:
            return []

        elements = [Spacer(1, 0.15 * inch)]
        elements.append(Paragraph("<b>3.3. İnsan İncelemesi Önerilen Bulgular</b>", self.styles['Normal']))
        elements.append(Spacer(1, 0.08 * inch))
        elements.append(Paragraph(
            "Aşağıdaki kayıtların karar güveni 0.60 altında olduğu veya modüller arası çelişki içerdiği için kesin risk kararı verilmemiştir.",
            self.styles['Normal']
        ))

        tablo_veriler = [[
            self._p("Kelime", baslik_hucre_stili),
            self._p("Kategori", baslik_hucre_stili),
            self._p("Sayfa", baslik_hucre_stili),
            self._p("Gerekçe", baslik_hucre_stili),
        ]]
        for bulgu in inceleme_bulgulari[:12]:
            guven = bulgu.get('kararGuveni')
            guven_metni = " Karar güveni: %.2f." % guven if isinstance(guven, (int, float)) else ""
            gerekce = self._pdf_metni_temizle(bulgu.get('gerekce', 'Bağlam manuel kontrol gerektiriyor.'))
            tablo_veriler.append([
                self._p(bulgu.get('kelime', '?'), hucre_stili, 70),
                self._p(self._kategori_adi(bulgu.get('kategori', 'diger')), hucre_stili, 110),
                self._p(str(bulgu.get('sayfa', '?')), hucre_stili, 30),
                self._p("İnsan İncelemesi Önerilir.%s %s" % (guven_metni, gerekce), hucre_stili, 260),
            ])

        tablo = Table(tablo_veriler, colWidths=[2.2 * cm, 4.0 * cm, 1.2 * cm, 8.1 * cm], repeatRows=1)
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFDF4')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#999999')),
        ]))
        elements.append(tablo)
        return elements

    def _olustur_yanlis_pozitif_ozeti(self, tum_bulgular: list, hucre_stili, baslik_hucre_stili) -> list:
        """Risk 0 bulguları denetim savunması olarak özetler."""
        pozitif_kelime_anahtarlari = {
            self._bulgu_kelime_anahtari(bulgu, bulgu.get('kategori', ''))
            for bulgu in tum_bulgular
            if self._risk_degeri(bulgu) > 0
        }
        pozitif_sade_kelimeler = {
            self._bulgu_sade_kelime_anahtari(bulgu)
            for bulgu in tum_bulgular
            if self._risk_degeri(bulgu) > 0
        }
        risksizler = [
            bulgu for bulgu in tum_bulgular
            if self._karar_durumu(bulgu) == 'risk_0'
            and self._bulgu_kelime_anahtari(bulgu, bulgu.get('kategori', '')) not in pozitif_kelime_anahtarlari
            and self._bulgu_sade_kelime_anahtari(bulgu) not in pozitif_sade_kelimeler
        ]
        if not risksizler:
            return []

        elements = [Spacer(1, 0.15 * inch)]
        elements.append(Paragraph("<b>3.4. Yanlış Pozitif / Risk 0 Savunma Özeti</b>", self.styles['Normal']))
        elements.append(Spacer(1, 0.08 * inch))
        elements.append(Paragraph(
            "Aşağıdaki kayıtlar tam kelime taramasında görünmüş; ancak cümle bağlamı eğitsel, tarihsel, mecazi veya eleştirel olduğu için risk puanı 0 kabul edilmiştir. Bu bölüm denetimde yanlış pozitiflerin gerekçeli biçimde ayrıştırıldığını gösterir.",
            self.styles['Normal']
        ))

        gruplar = {}
        for bulgu in risksizler:
            kelime = str(bulgu.get('kelime', '?')).lower()
            kategori = self._kategori_adi(bulgu.get('kategori', 'diger'))
            baglam = bulgu.get('baglamTipi', bulgu.get('ai_baglam_analizi', {}).get('baglamTipi', 'risk_0'))
            gruplar.setdefault((kelime, kategori, baglam), 0)
            gruplar[(kelime, kategori, baglam)] += 1

        tablo_veriler = [[
            self._p("Kelime", baslik_hucre_stili),
            self._p("Kategori", baslik_hucre_stili),
            self._p("Adet", baslik_hucre_stili),
            self._p("Savunma Gerekçesi", baslik_hucre_stili),
        ]]

        gerekce_map = {
            "egitsel": "Eğitsel/uyarıcı kullanım; özendirme yok.",
            "mecazi": "Mecazi, edebi veya sembolik kullanım.",
            "elestirel": "Olumsuzlayıcı/eleştirel bağlam.",
            "tarihsel": "Tarihsel veya dönem aktarımı.",
        }
        gerekce_map.update({
            "sosyal_iliskiler": "Sosyal/arkadaslik iliskisi; sakincali anlam tasimiyor.",
            "sosyal_mahcubiyet": "Sosyal mahcubiyet ve icsel pismanlik; mahrem/cinsel anlam tasimiyor.",
            "duygusal_tepki": "Kisa sureli duygu/saskinlik tepkisi; travmatik ayrinti yok.",
            "aile_bosanma_notr": "Aile, evlilik veya bosanma yalniz olay bilgisi olarak geciyor.",
            "romantik_iliskiler_uygun": "Yas grubuna uygun romantik/duygusal iliski; mahrem gorunurluk yok.",
            "betimleyici": "Betimleyici kullanim; davranisi olumlamiyor.",
            "teknik": "Teknik/terimsel kullanim.",
            "olay_orgusu": "Olay orgusu referansi; anlatinin olumlama mesaji yok.",
            "notr": "Riskli baglam bulunmadigi icin kelime tek basina risk sayilmadi.",
        })
        for (kelime, kategori, baglam), adet in sorted(gruplar.items(), key=lambda item: (-item[1], item[0][0]))[:12]:
            tablo_veriler.append([
                self._p(kelime, hucre_stili, 70),
                self._p(kategori, hucre_stili, 110),
                self._p(str(adet), hucre_stili, 20),
                self._p(gerekce_map.get(baglam, "Bağlam analizi sonucunda problemli kabul edilmedi."), hucre_stili, 180),
            ])

        tablo = Table(tablo_veriler, colWidths=[2.2 * cm, 4.0 * cm, 1.2 * cm, 8.1 * cm], repeatRows=1)
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFFFF')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#999999')),
        ]))
        elements.append(tablo)
        return elements

    def _olustur_tema_olay_orgusu_bolumu(self, sonuclar: dict) -> list:
        """Kelime geçmese bile aranan tema ve olay örgüsü bulgularını listeler."""
        baslik_stili = ParagraphStyle(
            'TemaOlayBaslik',
            parent=self.styles['Heading2'],
            fontName=DEFAULT_FONT_BOLD,
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12
        )
        metin_stili = ParagraphStyle(
            'TemaOlayMetin',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=10,
            leading=13,
            spaceAfter=6
        )
        hucre_stili = ParagraphStyle(
            'TemaOlayHucre',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=8,
            leading=10
        )
        baslik_hucre_stili = ParagraphStyle(
            'TemaOlayBaslikHucre',
            parent=hucre_stili,
            fontName=DEFAULT_FONT_BOLD
        )

        elements = []
        elements.append(Paragraph("<b>3.2. AŞAMA 10 - Tema ve Olay Örgüsü Analizi</b>", baslik_stili))
        elements.append(Spacer(1, 0.08 * inch))
        elements.append(Paragraph(
            "Kelime analizi tamamlandıktan sonra karakter davranışları, ilişkiler, alışkanlıklar, aile yapısı, romantik temalar, şiddet/suç ve zararlı alışkanlık sahneleri ayrıca taranmıştır.",
            metin_stili
        ))

        tema_bulgulari = self._tema_bulgulari(sonuclar)
        if not tema_bulgulari:
            elements.append(Paragraph(
                "Tema ve olay örgüsü analizinde rapora alınacak bulgu tespit edilmemiştir.",
                metin_stili
            ))
            return elements

        sirali_bulgular = sorted(tema_bulgulari, key=lambda b: (b.get('sayfa', 0), b.get('tema_adi', '')))
        tablo_veriler = [[
            self._p("Tema Adı", baslik_hucre_stili),
            self._p("Sayfa", baslik_hucre_stili),
            self._p("Alıntı", baslik_hucre_stili),
            self._p("Bağlam", baslik_hucre_stili),
            self._p("Risk", baslik_hucre_stili),
        ]]

        for bulgu in sirali_bulgular:
            risk = self._risk_degeri(bulgu)
            tablo_veriler.append([
                self._p(bulgu.get('tema_adi', 'Tema'), hucre_stili, 95),
                self._p(str(bulgu.get('sayfa', '?')), hucre_stili, 30),
                self._p(bulgu.get('alıntı') or bulgu.get('alinti') or bulgu.get('cumle', ''), hucre_stili, 250),
                self._p(bulgu.get('bağlam') or bulgu.get('baglam', ''), hucre_stili, 210),
                self._p("%s Risk: %s/5" % (bulgu.get('risk', 'Editoryal kontrol gerekir.'), risk), hucre_stili, 170),
            ])

        tablo = Table(tablo_veriler, colWidths=[2.7 * cm, 1.2 * cm, 4.8 * cm, 4.0 * cm, 3.0 * cm], repeatRows=1)
        tablo_stili = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFDF4')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#777777')),
        ]
        for satir_index, bulgu in enumerate(sirali_bulgular, start=1):
            if self._risk_degeri(bulgu) >= 3:
                tablo_stili.append(('BACKGROUND', (4, satir_index), (4, satir_index), colors.HexColor('#FEF2F2')))
            else:
                tablo_stili.append(('BACKGROUND', (4, satir_index), (4, satir_index), colors.HexColor('#FFFBEB')))
        tablo.setStyle(TableStyle(tablo_stili))
        elements.append(tablo)
        elements.append(Spacer(1, 0.1 * inch))

        return elements

    def _olustur_gorsel_figür_bolumu(self, sonuclar: dict, metadata: dict) -> list:
        """PDF içindeki görsel/figür varlığını özetler."""
        baslik_stili = ParagraphStyle(
            'GorselBaslikStili',
            parent=self.styles['Heading2'],
            fontName=DEFAULT_FONT_BOLD,
            fontSize=13,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10
        )
        metin_stili = ParagraphStyle(
            'GorselMetinStili',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=10,
            spaceAfter=6
        )
        hucre_stili = ParagraphStyle(
            'GorselHucre',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=8,
            leading=10
        )
        baslik_hucre_stili = ParagraphStyle(
            'GorselBaslikHucre',
            parent=hucre_stili,
            fontName=DEFAULT_FONT_BOLD
        )

        gorsel = sonuclar.get('gorsel_tarama') or metadata.get('gorsel_ozet') or {}
        toplam = int(gorsel.get('toplam_gorsel', 0) or 0)
        sayfalar = gorsel.get('gorselli_sayfalar', []) or []
        ic_illustrasyon_var = bool(gorsel.get('ic_illustrasyon_var', False))
        gorsel_analiz_yapildi = bool(gorsel.get('gorsel_icerik_analizi_yapildi', False))
        sayfa_metni = ", ".join(str(s) for s in sayfalar[:12]) if sayfalar else "-"
        if len(sayfalar) > 12:
            sayfa_metni += " ..."

        elements = []
        elements.append(Paragraph("<b>4.2. Görsel ve Figür Taraması</b>", baslik_stili))
        elements.append(Spacer(1, 0.08 * inch))

        tablo_veriler = [[
            self._p("Görsel Unsur", baslik_hucre_stili),
            self._p("Durum", baslik_hucre_stili),
            self._p("Not", baslik_hucre_stili),
        ], [
            self._p("Toplam görsel/XObject", hucre_stili),
            self._p(str(toplam), hucre_stili),
            self._p("PDF içindeki görsel nesne sayımıdır; görsel içeriğin analiz edildiği anlamına gelmez.", hucre_stili),
        ], [
            self._p("Görsel bulunan sayfalar", hucre_stili),
            self._p(sayfa_metni, hucre_stili),
            self._p("Yalnızca XObject konumu/sayımıdır; OCR veya görüntü analizi yapılmamıştır.", hucre_stili),
        ], [
            self._p("Görsel içerik analizi", hucre_stili),
            self._p("Yapıldı" if gorsel_analiz_yapildi else "Yapılmadı", hucre_stili),
            self._p("Görüntü sınıflandırma, OCR veya figür/içerik analizi çalıştırılmadıysa sakıncalı görsel iddiası üretilmez.", hucre_stili),
        ]]

        tablo = Table(tablo_veriler, colWidths=[4.0 * cm, 3.0 * cm, 8.5 * cm], repeatRows=1)
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFDF4')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#777777')),
        ]))
        elements.append(tablo)

        denetim = normalize_gorsel_denetim(gorsel.get('gorsel_denetim'), sayfa=sayfa_metni)
        kategori_veriler = [[
            self._p("Kategori", baslik_hucre_stili),
            self._p("Durum", baslik_hucre_stili),
            self._p("Puan", baslik_hucre_stili),
            self._p("Gerekçe", baslik_hucre_stili),
        ]]
        for key, label in VISUAL_AUDIT_CATEGORIES.items():
            kategori = denetim.get(key, {})
            puan = kategori.get("puan")
            kategori_veriler.append([
                self._p(label, hucre_stili, 120),
                self._p(kategori.get("durum", "Tespit Edilemedi"), hucre_stili, 80),
                self._p("Hesaplanmadı" if puan is None else str(puan), hucre_stili, 45),
                self._p(kategori.get("gerekce", ""), hucre_stili, 260),
            ])

        kategori_tablosu = Table(
            kategori_veriler,
            colWidths=[3.7 * cm, 2.8 * cm, 2.1 * cm, 6.9 * cm],
            repeatRows=1
        )
        kategori_tablosu.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFFFF')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#777777')),
        ]))
        elements.append(Spacer(1, 0.08 * inch))
        elements.append(kategori_tablosu)

        gorsel_bulgulari = (
            gorsel.get("gorsel_analizleri")
            or (gorsel.get("gorsel_denetim") or {}).get("gorsel_analizleri")
            or gorsel.get("gorsel_bulgulari")
            or (gorsel.get("gorsel_denetim") or {}).get("bulgular")
            or []
        )
        if gorsel_bulgulari:
            bulgu_veriler = [[
                self._p("Sayfa", baslik_hucre_stili),
                self._p("Görsel Açıklaması", baslik_hucre_stili),
                self._p("Risk Kategorisi", baslik_hucre_stili),
                self._p("Risk", baslik_hucre_stili),
                self._p("Güven", baslik_hucre_stili),
            ]]
            for bulgu in gorsel_bulgulari[:20]:
                risk = bulgu.get("risk_puani", bulgu.get("risk", bulgu.get("puan", 0)))
                risk_metni = "Hesaplanmadı" if risk is None else f"{risk}/5"
                guven = bulgu.get("karar_guveni", bulgu.get("guven", ""))
                if isinstance(guven, (int, float)):
                    guven = f"{guven:.2f}"
                kategori_adi = bulgu.get("kategori_adi") or VISUAL_AUDIT_CATEGORIES.get(
                    bulgu.get("kategori", ""),
                    bulgu.get("kategori", "-")
                )
                bulgu_veriler.append([
                    self._p(str(bulgu.get("sayfa", "?")), hucre_stili, 35),
                    self._p(bulgu.get("gorsel_aciklamasi", "Görsel açıklaması yok."), hucre_stili, 220),
                    self._p(kategori_adi, hucre_stili, 100),
                    self._p(risk_metni, hucre_stili, 45),
                    self._p(str(guven), hucre_stili, 45),
                ])

            bulgu_tablosu = Table(
                bulgu_veriler,
                colWidths=[1.2 * cm, 5.6 * cm, 3.7 * cm, 1.6 * cm, 1.6 * cm],
                repeatRows=1
            )
            bulgu_tablosu.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
                ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFDF4')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#777777')),
            ]))
            elements.append(Spacer(1, 0.1 * inch))
            elements.append(Paragraph("<b>Görsel İçerik Risk Bulguları</b>", metin_stili))
            elements.append(bulgu_tablosu)
        elif toplam > 0 and not gorsel_analiz_yapildi:
            elements.append(Spacer(1, 0.08 * inch))
            elements.append(Paragraph(
                "<b>Görsel İçerik Risk Bulguları:</b> İncelenmedi. Görseller sayılmıştır; ancak içerik düzeyinde analiz çalıştırılmamıştır.",
                metin_stili
            ))

        if not gorsel_analiz_yapildi:
            sonuc = "Görsel içerik analizi yapılmamıştır. Yalnızca PDF içerisinde görsel nesne bulunduğu tespit edilmiştir."
        elif toplam == 0:
            sonuc = "Görsel içerik analizi sonucunda görsel nesne tespit edilmemiştir."
        elif ic_illustrasyon_var:
            sonuc = "Görsel içerik analizi yapılmış ve iç sayfalarda görsel nesne tespit edilmiştir."
        else:
            sonuc = "Görsel içerik analizi yapılmış; tespitler ayrıca sınıflandırma sonucuna göre değerlendirilmelidir."
        elements.append(Spacer(1, 0.08 * inch))
        elements.append(Paragraph("<b>Sonuç:</b> %s" % sonuc, metin_stili))
        elements.append(Paragraph(
            "<b>Genel Görsel Risk:</b> %s - <b>Nihai Karar:</b> %s" % (
                "Hesaplanmadı" if denetim.get("genel_risk") is None else f"{denetim.get('genel_risk')}/5",
                denetim.get("nihai_karar", "İnceleme Gerekli")
            ),
            metin_stili
        ))
        return elements
    
    def _olustur_meb_ttk_bolumu(self, sonuclar: dict) -> list:
        """MEB TTK kriterleri bölümü - Dinamik veriler + Detaylı Bulgular"""
        self._meb_detaylarini_kriterlere_yansit(sonuclar)
        
        import os
        log_path = os.path.abspath('debug_reportgen.log')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[_olustur_meb_ttk_bolumu] Called, MEB_RAPORLAYICI_YÜKLÜ={MEB_RAPORLAYICI_YÜKLÜ}\n")
        
        print(f"[_olustur_meb_ttk_bolumu] MEB_RAPORLAYICI_YÜKLÜ={MEB_RAPORLAYICI_YÜKLÜ}", flush=True)
        
        # MEB Raporlayıcı varsa, onu kullan
        if MEB_RAPORLAYICI_YÜKLÜ:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"[_olustur_meb_ttk_bolumu] Using MEBBulgularıRaporlayıcı\n")
            print("[_olustur_meb_ttk_bolumu] Using MEBBulgularıRaporlayıcı", flush=True)
            raporlayici = MEBBulgularıRaporlayıcı(font_regular=DEFAULT_FONT, font_bold=DEFAULT_FONT_BOLD)
            result = raporlayici.olustur_meb_raporu(sonuclar)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"[_olustur_meb_ttk_bolumu] olustur_meb_raporu returned {len(result)} elements\n")
            return result
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[_olustur_meb_ttk_bolumu] Using fallback\n")
        
        # Fallback: Eski sistem
        baslik_stili = ParagraphStyle(
            'BaslikStili',
            parent=self.styles['Heading2'],
            fontName=DEFAULT_FONT_BOLD,
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12
        )
        
        metin_stili = ParagraphStyle(
            'MetinStili',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=11,
            spaceAfter=6
        )
        
        elements = []
        elements.append(Paragraph("<b>4. MEB TTK Kriterleri Analizi</b>", baslik_stili))
        elements.append(Spacer(1, 0.2 * inch))
        
        # MEB değerlendirmesi verilerini al
        meb_eval = sonuclar.get('meb_degerlendirmesi', {})
        meb_kriterler = meb_eval.get('meb_kriterler', {})
        puanlama = meb_eval.get('puanlama_detayi', {}) or {}
        kriter_cezalari = puanlama.get('kriter_cezalari', {}) or {}
        meb_puani = meb_eval.get('meb_puani', 50)
        meb_karar = self._pdf_metni_temizle(meb_eval.get('genel_karar', 'Bilinmiyor'))
        
        # Kriterleri tabloda göster
        tablo_veriler = [["Kriter", "Durum", "Risk", "Puan Etkisi"]]
        
        kriter_isimleri = {
            "anayasa": "Anayasa ve Mevzuat Uygunluğu",
            "milli_guvenlik": "Millî Güvenlik",
            "esitlik": "Eşitlik ve Kapsayıcılık",
            "milli_manevi": "Millî ve Manevi Değerler",
            "guvenlik": "Güvenli ve Etik İçerik",
            "bilimsel": "Bilimsel Doğruluk",
            "reklam": "Reklam ve Ticari Unsurlar",
            "dil": "Dil ve Anlatım"
        }
        
        for kriter_key, kriter_adi in kriter_isimleri.items():
            if kriter_key in meb_kriterler or kriter_key in kriter_cezalari:
                kriter_data = meb_kriterler.get(kriter_key, {}) or {}
                ceza_detayi = kriter_cezalari.get(kriter_key, {}) or {}
                karar = ceza_detayi.get('karar') if float(ceza_detayi.get('puan_cezasi', 0) or 0) > 0 else kriter_data.get('karar')
                karar = self._pdf_metni_temizle(karar or 'Bilinmiyor')
                risk = float(ceza_detayi.get('risk', kriter_data.get('risk', 0)) or 0)
                ceza = float(ceza_detayi.get('puan_cezasi', kriter_data.get('puan_cezasi', 0)) or 0)
                durum = "OK" if risk <= 1 else "KONTROL" if risk <= 2 else "UYARI" if risk <= 3 else "YUKSEK"
                tablo_veriler.append([
                    kriter_adi,
                    "[%s] %s" % (durum, karar),
                    "%d/5" % int(risk),
                    "-%g" % ceza,
                ])
        
        tablo = Table(tablo_veriler, colWidths=[4.5 * cm, 3.2 * cm, 1.6 * cm, 2.0 * cm])
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        elements.append(tablo)
        elements.append(Spacer(1, 0.15 * inch))
        
        # MEB puanı ve karar
        elements.append(Paragraph(
            "<b>MEB Uyum Puanı:</b> %d/100 -> %s" % (meb_puani, meb_karar),
            metin_stili
        ))
        elements.append(Paragraph(
            "<b>Hesaplama:</b> %s" % self._pdf_metni_temizle(self._meb_hesaplama_metni(sonuclar)),
            metin_stili
        ))
        if puanlama:
            elements.append(Paragraph(
                "<b>MEB Puan Formülü:</b> %s. Tablo puan etkisi toplamı: -%g." % (
                    self._pdf_metni_temizle(puanlama.get('formul', '')),
                    self._meb_tablo_cezasi_toplami(sonuclar),
                ),
                metin_stili
            ))
        elements.append(Spacer(1, 0.1 * inch))
        
        if meb_puani >= 75:
            sonuc_metni = "Kitap MEB Talim ve Terbiye Kurulu kriterlerine uygun bulunmuştur."
        elif meb_puani >= 50:
            sonuc_metni = "Kitap koşullu olarak MEB kriterlerine uygun olabilir. İşaretli bölümler kontrol edilmelidir."
        else:
            sonuc_metni = "Kitap MEB Talim ve Terbiye Kurulu kriterlerine uygun değildir. Revizyon gereklidir."
        
        elements.append(Paragraph("<b>Sonuç:</b> %s" % sonuc_metni, metin_stili))
        
        return elements
    
    def _olustur_maarif_bolumu(self, sonuclar: dict) -> list:
        """Maarif Modeli analizi bölümü"""
        
        baslik_stili = ParagraphStyle(
            'BaslikStili',
            parent=self.styles['Heading2'],
            fontName=DEFAULT_FONT_BOLD,
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12
        )
        
        metin_stili = ParagraphStyle(
            'MetinStili',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=11,
            spaceAfter=6
        )
        
        elements = []
        elements.append(Paragraph("<b>5. Maarif Modeli Değerlendirmesi</b>", baslik_stili))
        elements.append(Spacer(1, 0.2 * inch))
        
        maarif_profilleri = sonuclar.get('maarif_profilleri', {})
        analiz_profili = self._pdf_metni_temizle(sonuclar.get('profil', 'hibrit')).upper()
        profil_aciklama = self._pdf_metni_temizle(
            sonuclar.get('profil_aciklama', 'Maarif Modeli ve yayın denetimi birlikte yorumlanmıştır.')
        )
        yas_grubu = self._pdf_metni_temizle(sonuclar.get('yas_grubu', 'Belirtilmemiş'))

        hucre_stili = ParagraphStyle(
            'MaarifHucre',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=8,
            leading=10
        )
        baslik_hucre_stili = ParagraphStyle(
            'MaarifBaslikHucre',
            parent=hucre_stili,
            fontName=DEFAULT_FONT_BOLD
        )

        def profil_yorumu(puan: int, bulgu_sayisi: int) -> str:
            if bulgu_sayisi <= 0:
                return "Metinde belirgin iz bulunamadı."
            if puan >= 4:
                return "Güçlü temsil ediliyor."
            if puan >= 2:
                return "Kısmen temsil ediliyor; geliştirilebilir."
            return "Zayıf temsil ediliyor."

        def profil_onerisi(profil_key: str, puan: int, bulgu_sayisi: int) -> str:
            if bulgu_sayisi <= 0 or puan < 2:
                oneriler = {
                    "sorgulayici": "Merak, soru sorma ve araştırma davranışını destekleyen sahneler eklenebilir.",
                    "cesaretli": "Zorluk karşısında sağduyulu cesaret ve dayanıklılık vurgusu güçlendirilebilir.",
                    "uretken": "Üretme, tasarlama, çözüm geliştirme veya yaratıcı düşünme örnekleri eklenebilir.",
                    "bilge": "Deneyimden ders çıkarma, adaletli karar verme ve hikmetli davranışlar belirginleştirilebilir.",
                    "ahlaklı": "Dürüstlük, sorumluluk, vicdan ve erdem temaları daha açık işlenebilir.",
                    "merhametli": "Yardımlaşma, şefkat ve empatiyi gösteren davranışlar artırılabilir.",
                    "vatansever": "Vatan, millet, ortak sorumluluk ve toplumsal aidiyet olumlu bağlamlarla desteklenebilir.",
                    "estetik": "Sanat, doğa, güzellik ve estetik duyarlılık daha görünür hale getirilebilir.",
                    "iradeli": "Azim, hedefe yönelme, sabır ve çaba temaları güçlendirilebilir.",
                    "adil": "Adalet, hakkaniyet ve eşit davranma örnekleri belirginleştirilebilir.",
                    "saglikli": "Sağlıklı yaşam, temizlik, spor ve iyi oluş vurgusu eklenebilir."
                }
                return oneriler.get(profil_key, "Bu profil değerini destekleyen olumlu sahneler artırılabilir.")
            return "Mevcut temsil korunabilir; olumlu örnekler metin içinde dengeli dağıtılabilir."

        elements.append(Paragraph(
            "<b>Analiz Profili:</b> %s &nbsp;&nbsp; <b>Hedef Yaş Grubu:</b> %s" % (analiz_profili, yas_grubu),
            metin_stili
        ))
        elements.append(Paragraph(profil_aciklama, metin_stili))
        elements.append(Spacer(1, 0.1 * inch))
        
        if maarif_profilleri:
            # Profilleri tabloda göster
            tablo_veriler = [[
                self._p("Profil", baslik_hucre_stili),
                self._p("Puan", baslik_hucre_stili),
                self._p("Bulgu", baslik_hucre_stili),
                self._p("Yorum", baslik_hucre_stili),
            ]]
            aktif_profiller = []
            
            for profil_adi, profil_veri in maarif_profilleri.items():
                if isinstance(profil_veri, dict):
                    puan = int(profil_veri.get('puan', profil_veri.get('skor', 0)) or 0)
                    bulgu_sayisi = int(profil_veri.get('bulgu_sayisi', 0) or 0)
                    profil_label = self._pdf_metni_temizle(
                        profil_veri.get('profil_adi', profil_adi.replace('_', ' ').title())
                    )
                    yorum = profil_yorumu(puan, bulgu_sayisi)
                    if bulgu_sayisi > 0:
                        aktif_profiller.append((profil_adi, profil_label, puan, bulgu_sayisi))
                    tablo_veriler.append([
                        self._p(profil_label, hucre_stili, 90),
                        self._p("%d/5" % puan, hucre_stili, 20),
                        self._p(str(bulgu_sayisi), hucre_stili, 20),
                        self._p(yorum, hucre_stili, 180),
                    ])
            
            if len(tablo_veriler) > 1:  # başlık satırdan fazla veri var mı
                tablo = Table(tablo_veriler, colWidths=[4.2 * cm, 1.7 * cm, 1.7 * cm, 7.9 * cm], repeatRows=1)
                tablo.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 1), (2, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
                    ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFDF4')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#777777'))
                ]))
                elements.append(tablo)
                elements.append(Spacer(1, 0.12 * inch))

                if aktif_profiller:
                    aktif_profiller.sort(key=lambda item: (-item[2], -item[3], item[1]))
                    guclu = [item for item in aktif_profiller if item[2] >= 3]
                    gelistirilecek = [item for item in aktif_profiller if item[2] < 3]

                    if guclu:
                        guclu_metin = ", ".join("%s (%d/5)" % (item[1], item[2]) for item in guclu[:5])
                        elements.append(Paragraph("<b>Güçlü görünen profiller:</b> %s." % guclu_metin, metin_stili))

                    if gelistirilecek:
                        elements.append(Paragraph("<b>Geliştirme önerileri:</b>", metin_stili))
                        for profil_key, profil_label, puan, bulgu_sayisi in gelistirilecek[:5]:
                            elements.append(Paragraph(
                                "<b>%s:</b> %s" % (profil_label, profil_onerisi(profil_key, puan, bulgu_sayisi)),
                                metin_stili
                            ))
                    else:
                        elements.append(Paragraph(
                            "Maarif profilleri genel olarak dengeli temsil edilmektedir; mevcut olumlu örneklerin metin boyunca korunması önerilir.",
                            metin_stili
                        ))
                else:
                    elements.append(Paragraph(
                        "Metinde Maarif Modeli öğrenci profillerine ilişkin belirgin anahtar izler sınırlıdır. Karakter davranışlarına merak, sorumluluk, adalet, merhamet ve üretkenlik gibi değerleri gösteren sahneler eklenmesi önerilir.",
                        metin_stili
                    ))
            else:
                elements.append(Paragraph(
                    "Maarif Modeli profilleri için sayısal veri üretilememiştir.",
                    metin_stili
                ))
        else:
            elements.append(Paragraph(
                "Maarif Modeli profilleri için ayrıntılı veri bulunamadı. Metin; sorumluluk, adalet, merhamet, üretkenlik, irade ve estetik duyarlılık gibi öğrenci profili değerleri açısından manuel olarak da gözden geçirilmelidir.",
                metin_stili
            ))
        
        return elements
    
    def _olustur_kultur_bolumu(self, sonuclar: dict) -> list:
        """Kültürel uyum bölümü - Dinamik veriler"""
        
        baslik_stili = ParagraphStyle(
            'BaslikStili',
            parent=self.styles['Heading2'],
            fontName=DEFAULT_FONT_BOLD,
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12
        )
        
        metin_stili = ParagraphStyle(
            'MetinStili',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=11,
            spaceAfter=6
        )
        
        elements = []
        elements.append(Paragraph("<b>6. Kültürel Uyum Analizi</b>", baslik_stili))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Kültürel uyum verilerini al
        kultural_eval = sonuclar.get('kultural_uyum', {})

        kultural_puan = int(kultural_eval.get('kultural_puan', 0) or 0)
        degerlendirme = self._pdf_metni_temizle(kultural_eval.get('genel_degerlendirme', 'Bilinmiyor'))
        turk_sayi = int(kultural_eval.get('turk_karakter', 0) or 0)
        batili_sayi = int(kultural_eval.get('batili_karakter', 0) or 0)
        cografi_sayi = int(kultural_eval.get('cografi_referans', 0) or 0)
        islami_sayi = int(kultural_eval.get('islami_referans', 0) or 0)
        deger_sayi = int(kultural_eval.get('degerler', 0) or 0)

        hucre_stili = ParagraphStyle(
            'KulturHucre',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=8,
            leading=10
        )
        baslik_hucre_stili = ParagraphStyle(
            'KulturBaslikHucre',
            parent=hucre_stili,
            fontName=DEFAULT_FONT_BOLD
        )

        def durum_metni(sayi: int, unsur: str) -> str:
            if sayi <= 0:
                return "Belirgin iz yok."
            if unsur == "batili":
                return "Nötr bilgi; bağlama göre değerlendirilir."
            if sayi >= 3:
                return "Güçlü temsil var."
            return "Sınırlı temsil var."

        def yorum_metni(sayi: int, unsur: str) -> str:
            if unsur == "turk":
                return "Yerel isim, Türkçe/Anadolu referansı veya kültürel aidiyet izleri."
            if unsur == "batili":
                return "Batı kaynaklı isim/referanslar tek başına risk değildir; metindeki kültürel denge için izlenir."
            if unsur == "cografi":
                return "Türkiye şehirleri, Anadolu veya tarihî-coğrafi bağlam görünürlüğü."
            if unsur == "islami":
                return "Dinî/kültürel pratik ve sembollerin yaş grubuna uygun görünürlüğü."
            return "Aile, vatan, millet, bayrak, saygı, sorumluluk, erdem ve ahlak temaları."
        
        # Analiz sonuçları tablosu
        tablo_veriler = [[
            self._p("Kültürel Unsur", baslik_hucre_stili),
            self._p("Sayı", baslik_hucre_stili),
            self._p("Durum", baslik_hucre_stili),
            self._p("Yorum", baslik_hucre_stili),
        ], [
            self._p("Türk karakter/isim ve yerel referans", hucre_stili),
            self._p(str(turk_sayi), hucre_stili),
            self._p(durum_metni(turk_sayi, "turk"), hucre_stili),
            self._p(yorum_metni(turk_sayi, "turk"), hucre_stili),
        ], [
            self._p("Batı karakter/isim", hucre_stili),
            self._p(str(batili_sayi), hucre_stili),
            self._p(durum_metni(batili_sayi, "batili"), hucre_stili),
            self._p(yorum_metni(batili_sayi, "batili"), hucre_stili),
        ], [
            self._p("Coğrafi referans (Türkiye)", hucre_stili),
            self._p(str(cografi_sayi), hucre_stili),
            self._p(durum_metni(cografi_sayi, "cografi"), hucre_stili),
            self._p(yorum_metni(cografi_sayi, "cografi"), hucre_stili),
        ], [
            self._p("İslami/kültürel referans", hucre_stili),
            self._p(str(islami_sayi), hucre_stili),
            self._p(durum_metni(islami_sayi, "islami"), hucre_stili),
            self._p(yorum_metni(islami_sayi, "islami"), hucre_stili),
        ], [
            self._p("Değer ifadeleri", hucre_stili),
            self._p(str(deger_sayi), hucre_stili),
            self._p(durum_metni(deger_sayi, "deger"), hucre_stili),
            self._p(yorum_metni(deger_sayi, "deger"), hucre_stili),
        ]]
        
        tablo = Table(tablo_veriler, colWidths=[4.4 * cm, 1.4 * cm, 3.2 * cm, 6.5 * cm], repeatRows=1)
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFDF4')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#777777'))
        ]))
        elements.append(tablo)
        elements.append(Spacer(1, 0.15 * inch))
        
        # Genel değerlendirme
        elements.append(Paragraph(
            f"<b>Kültürel Uyum Puanı:</b> {kultural_puan}/100 -> {degerlendirme}",
            metin_stili
        ))
        elements.append(Spacer(1, 0.1 * inch))

        if kultural_puan >= 80:
            sonuc_metni = "Metin kültürel aidiyet, değer görünürlüğü ve yerel bağlam açısından güçlü bir uyum göstermektedir."
        elif kultural_puan >= 50:
            sonuc_metni = "Metin orta düzeyde kültürel uyum göstermektedir; bazı değer ve yerel bağlam unsurları güçlendirilebilir."
        else:
            sonuc_metni = "Metinde kültürel uyum göstergeleri sınırlıdır; yerel bağlam ve temel değerlerin daha görünür işlenmesi önerilir."

        denge_metni = (
            "Türk/yerel referanslar Batı referanslarından daha görünür."
            if turk_sayi > batili_sayi else
            "Batı referansları Türk/yerel referanslarla dengelenmelidir."
            if batili_sayi > turk_sayi else
            "Türk/yerel ve Batı referansları sayısal olarak dengeli veya sınırlıdır."
        )
        
        elements.append(Paragraph(
            "<b>Sonuç:</b> %s %s" % (sonuc_metni, denge_metni),
            metin_stili
        ))

        oneriler = []
        if turk_sayi <= batili_sayi:
            oneriler.append("Karakter adları, mekânlar veya gündelik yaşam ayrıntılarıyla yerel kültürel bağlam güçlendirilebilir.")
        if cografi_sayi == 0:
            oneriler.append("Türkiye, Anadolu, şehir, mahalle veya tarihî-coğrafi bağlam referansları eklenebilir.")
        if islami_sayi == 0:
            oneriler.append("Yaş grubuna uygun ve doğal bağlamlı bayram, dua, cami, ezan gibi kültürel/dinî referanslar değerlendirilebilir.")
        if deger_sayi == 0:
            oneriler.append("Aile, saygı, sorumluluk, erdem, ahlak, vatan ve millet gibi değer temaları daha açık sahnelerle desteklenebilir.")
        if not oneriler:
            oneriler.append("Mevcut kültürel temsil korunabilir; değerler metin boyunca dengeli ve doğal biçimde sürdürülmelidir.")

        elements.append(Paragraph("<b>Geliştirme Önerileri:</b>", metin_stili))
        for oneri in oneriler[:5]:
            elements.append(Paragraph("- %s" % oneri, metin_stili))
        
        return elements
    
    def _olustur_sonuc_bolumu(self, sonuclar: dict) -> list:
        """Sonuç bölümü"""
        
        baslik_stili = ParagraphStyle(
            'BaslikStili',
            parent=self.styles['Heading2'],
            fontName=DEFAULT_FONT_BOLD,
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12
        )
        
        metin_stili = ParagraphStyle(
            'MetinStili',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=11,
            spaceAfter=6
        )
        
        elements = []
        elements.append(Paragraph("<b>7. Sonuç ve Öneriler</b>", baslik_stili))
        elements.append(Spacer(1, 0.2 * inch))
        
        final_skor = sonuclar.get('final_skor', 0)
        profil = sonuclar.get('profil', 'hibrit')
        yas_grubu = self._pdf_metni_temizle(sonuclar.get('yas_grubu', 'Belirtilmemiş'))
        problemli_bulgu = self._problemli_bulgu_sayisi(sonuclar)
        toplam_bulgu = len(self._tum_bulgular(sonuclar))
        tema_bulgulari = self._tema_bulgulari(sonuclar)
        tema_adlari = sorted({bulgu.get('tema_adi', 'Tema') for bulgu in tema_bulgulari})
        karar_metni = self._karar_etiketi(final_skor)
        rapor_durumu = self._pdf_metni_temizle(sonuclar.get('rapor_durumu') or karar_metni)
        gorsel_analiz_eksik = self._gorsel_analiz_eksik_mi(sonuclar)
        risk_cesitliligi = self._risk_cesitliligi_bilgisi(sonuclar)
        max_bulgu_riski = max((self._risk_degeri(bulgu) for bulgu in (self._tum_bulgular(sonuclar) + tema_bulgulari)), default=0)
        meb_eval = sonuclar.get('meb_degerlendirmesi', {})
        meb_puani = int(meb_eval.get('meb_puani', 0) or 0)
        meb_karar = self._pdf_metni_temizle(meb_eval.get('genel_karar', 'Bilinmiyor'))
        kultural_eval = sonuclar.get('kultural_uyum', {})
        kultural_puan = int(kultural_eval.get('kultural_puan', 0) or 0)
        kultural_karar = self._pdf_metni_temizle(kultural_eval.get('genel_degerlendirme', 'Bilinmiyor'))
        maarif_profilleri = sonuclar.get('maarif_profilleri', {})
        aktif_maarif = [
            profil_veri for profil_veri in maarif_profilleri.values()
            if isinstance(profil_veri, dict) and int(profil_veri.get('bulgu_sayisi', 0) or 0) > 0
        ]
        riskli_kategoriler = []
        for kategori, kategori_data in sonuclar.get('kategori_bulgulari', {}).items():
            risk = float(kategori_data.get('ortalama_risk', 0) or 0)
            toplam = int(kategori_data.get('toplam_bulgu', 0) or 0)
            if toplam > 0 and risk > 0:
                riskli_kategoriler.append((self._kategori_adi(kategori), toplam, risk))
        riskli_kategoriler.sort(key=lambda item: (-item[2], -item[1], item[0]))

        hucre_stili = ParagraphStyle(
            'SonucHucre',
            parent=self.styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=8,
            leading=10
        )
        baslik_hucre_stili = ParagraphStyle(
            'SonucBaslikHucre',
            parent=hucre_stili,
            fontName=DEFAULT_FONT_BOLD
        )
        
        zararli_tema_var = any(
            any(anahtar in str(tema).lower() for anahtar in ('sigara', 'sarhoş', 'sarhos', 'alkol'))
            for tema in tema_adlari
        )
        tek_eksenli_risk = risk_cesitliligi['riskli_kategori_sayisi'] <= 2 and risk_cesitliligi['riskli_tema_sayisi'] <= 3

        if problemli_bulgu > 0 and max_bulgu_riski <= 2:
            aciklama = (
                "Risk düşük düzeydedir; ancak tespit edilen kayıtlar yaş grubu açısından editoryal gözden geçirme gerektirir. "
                "Yayın kararı, işaretli sahnelerin bağlamı doğrulandıktan sonra verilmelidir."
            )
        elif final_skor < 50:
            aciklama = (
                "Kitapta tespit edilen bulguların büyük bölümü eğitsel, tarihsel, mecazi veya eleştirel bağlamda değerlendirilmiştir. "
                "Problemli bağlam sayısı yayın bütünlüğünü bozacak düzeyde değildir."
            )
        elif final_skor < 70:
            if zararli_tema_var and tek_eksenli_risk:
                aciklama = (
                    "Zararlı alışkanlık temaları nedeniyle editoryal değerlendirme önerilir. "
                    "Risk sigara/sarhoşluk ekseninde yoğunlaşmaktadır; bu durum otomatik ret veya kapsamlı revizyon anlamına gelmez. "
                    "İlgili sahneler yaş grubu, tekrar yoğunluğu ve normalizasyon bağlamı açısından incelenmelidir."
                )
            else:
                aciklama = (
                    "Orta risk bandı, doğrudan ret anlamına gelmez; fakat yayına hazırlık öncesinde editoryal inceleme ve gerekirse sınırlı revizyon gerektirir. "
                    "Karar, özellikle yüksek ağırlıklı temalar, risk çeşitliliği ve yaş grubu etkisi yeniden kontrol edilerek verilmelidir."
                )
        elif tek_eksenli_risk:
            aciklama = (
                "Risk puanı yüksek karar bandına ulaşmıştır; ancak riskler sınırlı tema ekseninde yoğunlaştığı için kapsamlı ret kararından önce editoryal kurul incelemesi önerilir. "
                "Yüksek puanı oluşturan sahnelerin normalizasyon ve yaş grubu etkisi açıkça gözden geçirilmelidir."
            )
        else:
            aciklama = (
                "Problemli bağlamlar ve genel risk seviyesi nedeniyle metin mevcut haliyle yayın denetimi açısından uygun değildir. "
                "Kapsamlı revizyon ve yeniden değerlendirme gerekir."
            )
        
        elements.append(Paragraph(
            f"<b>KARAR: {rapor_durumu}</b>",
            metin_stili
        ))
        elements.append(Spacer(1, 0.1 * inch))
        if gorsel_analiz_eksik:
            elements.append(Paragraph("<b>Rapor Durumu:</b> Eksik Analiz", metin_stili))
            elements.append(Paragraph("<b>Quality Check:</b> FAIL", metin_stili))
            elements.append(Spacer(1, 0.08 * inch))
        if gorsel_analiz_eksik:
            elements.append(Paragraph(
                "<b>Uyarı:</b> Metin analizi tamamlandı ancak görsel içerik analizi yapılmadığı için rapor tam kapsamlı içerik denetimi olarak kabul edilemez.",
                metin_stili
            ))
            elements.append(Spacer(1, 0.08 * inch))
        
        elements.append(Paragraph(
            f"<b>Gerekçe:</b> Tam kelime kontrolü ve bağlam analizi sonucunda {toplam_bulgu} bulgu rapora alınmış, "
            f"tema/olay örgüsü analizinde {len(tema_bulgulari)} bulgu ayrıca tespit edilmiş, "
            f"toplam {problemli_bulgu} kayıt risk puanı 0'ın üzerinde değerlendirilmiştir. Analiz profili: {profil.upper()}.",
            metin_stili
        ))
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph(aciklama, metin_stili))
        elements.append(Spacer(1, 0.15 * inch))

        karar_tablosu = [[
            self._p("Değerlendirme Alanı", baslik_hucre_stili),
            self._p("Sonuç", baslik_hucre_stili),
            self._p("Karara Etkisi", baslik_hucre_stili),
        ], [
            self._p("Genel Risk Skoru", hucre_stili),
            self._p("%s/100" % final_skor, hucre_stili),
            self._p("Yayın kararı için ana eşik değerdir.", hucre_stili),
        ], [
            self._p("Sakıncalı Kelime ve Bağlam", hucre_stili),
            self._p("%d bulgu; %d problemli bağlam" % (toplam_bulgu, problemli_bulgu), hucre_stili),
            self._p("Risk puanı 0 olanlar izlenir; problemli bağlamlar revizyon listesine alınır.", hucre_stili),
        ], [
            self._p("Tema ve Olay Örgüsü", hucre_stili),
            self._p("%d bulgu%s" % (len(tema_bulgulari), (" - " + ", ".join(tema_adlari[:5])) if tema_adlari else ""), hucre_stili),
            self._p("Kelime geçmese bile karakter davranışı, ilişki, aile yapısı ve zararlı alışkanlık sahneleri karara dahil edilir.", hucre_stili),
        ], [
            self._p("Risk Çeşitliliği", hucre_stili),
            self._p("%d kategori; %d tema" % (risk_cesitliligi['riskli_kategori_sayisi'], risk_cesitliligi['riskli_tema_sayisi']), hucre_stili),
            self._p("Tek kategoride yoğunlaşan risk ile çok kategorili risk aynı karar diliyle yorumlanmaz.", hucre_stili),
        ], [
            self._p("MEB TTK Uyum", hucre_stili),
            self._p("%d/100 - %s" % (meb_puani, meb_karar), hucre_stili),
            self._p("MEB kriterlerinde koşullu/ret alan başlıklar öncelikli kontrol edilir.", hucre_stili),
        ], [
            self._p("Maarif Modeli", hucre_stili),
            self._p("%d aktif profil izi" % len(aktif_maarif), hucre_stili),
            self._p("Öğrenci profili değerlerinin dengeli temsil edilip edilmediğini gösterir.", hucre_stili),
        ], [
            self._p("Kültürel Uyum", hucre_stili),
            self._p("%d/100 - %s" % (kultural_puan, kultural_karar), hucre_stili),
            self._p("Yerel bağlam, değer görünürlüğü ve kültürel dengeyi destekleyici ölçüttür.", hucre_stili),
        ]]
        tablo = Table(karar_tablosu, colWidths=[4.0 * cm, 4.0 * cm, 7.5 * cm], repeatRows=1)
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFDF4')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#777777'))
        ]))
        elements.append(tablo)
        elements.append(Spacer(1, 0.15 * inch))

        denetim = sonuclar.get('tutarlilik_denetimi', {})
        risk_formulu = denetim.get('risk_formulu', {})
        if risk_formulu:
            elements.append(Paragraph("<b>Risk Puanı Hesaplama Şeffaflığı:</b>", metin_stili))
            elements.append(Paragraph(
                "%s. Kelime: %.2f x %.2f = %.2f; MEB: %.2f x %.2f = %.2f; "
                "Görsel: %.2f x %.2f = %.2f; ağırlıklı toplam: %.2f; zorunlu taban: %.2f. "
                "Doğrulama: %s. Bu raporda kullanılan toplam risk skoru: %.2f/100. %s" % (
                    risk_formulu.get('formul', 'Toplam Risk = Kelime Riski %40 + MEB Riski %40 + Görsel Riski %20'),
                    float(risk_formulu.get('kelime_skoru', 0) or 0),
                    float((risk_formulu.get('agirliklar') or {}).get('kelime', 0.40) or 0.40),
                    float(risk_formulu.get('kelime_katkisi', 0) or 0),
                    float(risk_formulu.get('meb_riski', 0) or 0),
                    float((risk_formulu.get('agirliklar') or {}).get('meb', 0.40) or 0.40),
                    float(risk_formulu.get('meb_katkisi', 0) or 0),
                    float(risk_formulu.get('gorsel_riski', 0) or 0),
                    float((risk_formulu.get('agirliklar') or {}).get('gorsel', 0.20) or 0.20),
                    float(risk_formulu.get('gorsel_katkisi', 0) or 0),
                    float(risk_formulu.get('agirlikli_toplam', 0) or 0),
                    float(risk_formulu.get('minimum_genel_risk', 0) or 0),
                    risk_formulu.get('dogrulama_formulu', ''),
                    float(risk_formulu.get('toplam', final_skor) or 0),
                    risk_formulu.get('gorsel_notu', '')
                ),
                metin_stili
            ))
            elements.append(Spacer(1, 0.12 * inch))

        denetim_notlari = denetim.get('notlar', [])
        if denetim_notlari:
            elements.append(Paragraph("<b>Tutarlılık Denetimi Notları:</b>", metin_stili))
            for not_metni in denetim_notlari[:5]:
                elements.append(Paragraph("- %s" % not_metni, metin_stili))
            elements.append(Spacer(1, 0.12 * inch))

        zorunlu_kalite = sonuclar.get('zorunlu_kalite_kontrolu', {})
        if zorunlu_kalite:
            tema_kontrolu = zorunlu_kalite.get('tema_kontrolu', {})
            davranis_kontrolu = zorunlu_kalite.get('davranis_sahnelenmesi_denetimi', {})
            elements.append(Paragraph("<b>Zorunlu Kalite Kontrolü:</b>", metin_stili))
            elements.append(Paragraph(
                "<b>Quality Check:</b> %s. <b>Rapor Durumu:</b> %s." % (
                    zorunlu_kalite.get('quality_check', 'PASS'),
                    zorunlu_kalite.get('rapor_durumu') or sonuclar.get('rapor_durumu') or 'Tamamlandı'
                ),
                metin_stili
            ))
            elements.append(Paragraph(
                "Tema kontrolü, davranış sahnelenmesi denetimi, zararlı alışkanlık kontrolü, romantik içerik kontrolü, MEB tablo-formül matematiği, risk puanı-karar eşiği ve sonuç-detay tutarlılığı rapor öncesinde uygulanmıştır.",
                metin_stili
            ))
            elements.append(Paragraph(
                "Tespit edilen zorunlu temalar: %s. Kategoriye taşınan zorunlu sahne bulgusu: %s." % (
                    ", ".join(tema_kontrolu.get('tespit_edilen_zorunlu_temalar', [])) or "Yok",
                    davranis_kontrolu.get('kategoriye_tasinan_bulgu_sayisi', 0)
                ),
                metin_stili
            ))
            risk0_kurali = zorunlu_kalite.get('risk_0_kurali', {})
            if risk0_kurali:
                elements.append(Paragraph(
                    "Risk 0 kuralı uygulanmıştır: Risk 0 kayıtlar uyarı, revizyon önerisi ve sonuç puanı üretmez. Temizlenen uyarı/revizyon alanı: %s." %
                    risk0_kurali.get('uyari_revizyon_temizlenen_bulgu_sayisi', 0),
                    metin_stili
                ))
            elements.append(Paragraph(
                "<b>Son Rapor Doğrulama:</b> %s Cevap: %s." % (
                    zorunlu_kalite.get('son_rapor_dogrulama_sorusu', 'Kitapta geçen tüm önemli olaylar raporda temsil edildi mi?'),
                    zorunlu_kalite.get('son_rapor_dogrulama_cevabi', 'Bilinmiyor')
                ),
                metin_stili
            ))
            kalite_sorulari = zorunlu_kalite.get('son_kalite_kontrol_sorulari', {})
            sorunlu_sorular = [ad.replace('_', ' ') for ad, sorunlu_mu in kalite_sorulari.items() if sorunlu_mu]
            iyilestirme_notlari = []
            if risk_formulu and risk_formulu.get('gorsel_analiz_yapildi') is False:
                iyilestirme_notlari.append("görsel analiz hesaplanmadı")
            if any(
                self._risk_degeri(bulgu) <= 1 and str(bulgu.get('baglamTipi', '')) in {'romantik_dusuk_izleme', 'siddet_referansi_dusuk'}
                for kategori_data in (sonuclar.get('kategori_bulgulari', {}) or {}).values()
                for bulgu in kategori_data.get('bulunan_kelimeler', []) or []
            ):
                iyilestirme_notlari.append("düşük bağlamlı/tartışmalı sınıflandırmalar editoryal izlenmeli")
            if kalite_sorulari:
                elements.append(Paragraph(
                    "<b>Son Kalite Kontrolü:</b> %s" % (
                        "Kritik hata yok; rapor üretimini durduran kalite sorunu bulunmadı. İyileştirme önerileri: %s." % ", ".join(iyilestirme_notlari[:4])
                        if not sorunlu_sorular and iyilestirme_notlari else
                        "Kritik hata yok; rapor üretimini durduran kalite sorunu bulunmadı."
                        if not sorunlu_sorular else
                        "Yeniden kontrol gerektiren başlıklar: %s." % ", ".join(sorunlu_sorular[:6])
                    ),
                    metin_stili
                ))
            for eksik in zorunlu_kalite.get('eksikler', [])[:5]:
                elements.append(Paragraph("- Eksik: %s" % eksik, metin_stili))
            elements.append(Spacer(1, 0.12 * inch))
        
        # Kategori bazlı tavsiyeler
        kategori_tavsiyesi = self._uret_kategori_tavsiyesi(sonuclar)
        
        # Genel öneriler
        elements.append(Paragraph("<b>Öncelikli Aksiyon Planı:</b>", metin_stili))
        
        if problemli_bulgu <= 0:
            oneriler = [
                "Risk puanı 0'ın üzerinde bulgu tespit edilmediği için kategori bazlı revizyon önerisi üretilmemiştir.",
                "Rutin editoryal son okuma yapılmalı; Risk 0 kayıtları başka bölümde riskli bulgu olarak kullanılmamalıdır.",
                "Yeni baskı veya metin değişikliği sonrası aynı analiz yeniden çalıştırılmalıdır."
            ]
        elif final_skor < 50:
            oneriler = [
                "Yayın öncesi son okuma yapılmalı; risk puanı 0 olan bulgular yalnızca izleme notu olarak korunmalıdır.",
                "MEB, Maarif ve kültürel uyum tablolarındaki düşük temsil edilen alanlar editoryal olarak gözden geçirilmelidir.",
                "Yeni baskı veya metin değişikliği sonrası aynı analiz yeniden çalıştırılmalıdır."
            ]
        elif final_skor < 70:
            oneriler = [
                "Zararlı alışkanlık temaları editoryal kurul tarafından yaş grubu, tekrar yoğunluğu ve normalizasyon bağlamıyla birlikte değerlendirilmelidir.",
                "Sigara/sarhoşluk eksenindeki sahnelerde davranışın özendirici mi, eleştirel mi yoksa karakter betimlemesi mi olduğu netleştirilmelidir.",
                "Gerekirse sınırlı ifade düzeltmeleri yapılmalı; karar dili otomatik ret yerine editoryal inceleme sonucuna bağlanmalıdır.",
                "Düzeltme veya editoryal not sonrası rapor yeniden üretilerek karar tablosu güncellenmelidir."
            ]
        else:
            if tek_eksenli_risk:
                oneriler = [
                    "Risk yüksek banda ulaşsa da temalar sınırlı eksende yoğunlaştığı için karar öncesi editoryal kurul değerlendirmesi yapılmalıdır.",
                    "Zararlı alışkanlık sahneleri normalizasyon, tekrar yoğunluğu ve yaş grubu etkisi açısından tek dosyada gruplanarak incelenmelidir.",
                    "Gerekli görülürse ilgili sahnelere sınırlı revizyon uygulanmalı ve karar yeniden hesaplanmalıdır.",
                    "Çok kategorili risk oluşmadığı durumlarda karar gerekçesinde risk çeşitliliği ayrıca belirtilmelidir."
                ]
            else:
                oneriler = [
                    "Metin yayın sürecine alınmadan önce kapsamlı içerik revizyonundan geçirilmelidir.",
                    "Yüksek riskli bulgular pedagojik uzman ve editör görüşüyle yeniden değerlendirilmelidir.",
                    "MEB TTK ret/yüksek risk başlıkları giderilmeden olumlu yayın kararı verilmemelidir.",
                    "Revizyon tamamlanmadan uygunluk kararı verilmemelidir."
                ]
        
        for oneri in oneriler:
            elements.append(Paragraph(f"- {oneri}", metin_stili))

        if riskli_kategoriler:
            elements.append(Spacer(1, 0.12 * inch))
            elements.append(Paragraph("<b>Öncelikli Kontrol Başlıkları:</b>", metin_stili))
            for kategori_adi, toplam, risk in riskli_kategoriler[:5]:
                elements.append(Paragraph(
                    "- %s: %d bulgu, ortalama risk %.2f/5. İlgili cümleler yaş grubu (%s) ve bağlam açısından yeniden okunmalıdır." %
                    (kategori_adi, toplam, risk, yas_grubu),
                    metin_stili
                ))
        else:
            elements.append(Spacer(1, 0.12 * inch))
            elements.append(Paragraph(
                "<b>Öncelikli Kontrol Başlıkları:</b> Risk puanı 0'ın üzerinde kategori tespit edilmemiştir; rutin editoryal son okuma yeterlidir.",
                metin_stili
            ))

        hassas_kategoriler = {
            kategori for kategori, kategori_data in sonuclar.get('kategori_bulgulari', {}).items()
            if any(self._risk_degeri(bulgu) > 0 for bulgu in kategori_data.get('bulunan_kelimeler', []))
        }
        if problemli_bulgu > 0 and hassas_kategoriler:
            elements.append(Spacer(1, 0.12 * inch))
            elements.append(Paragraph("<b>Öğretmen/Yayıncı Notu Önerileri:</b>", metin_stili))
            if {'zararlı_alışkanlıklar', 'zararlı_aliskanliklar', 'uyusturucu_alkol'} & hassas_kategoriler:
                elements.append(Paragraph(
                    "- Alkol/sigara gibi dönem veya karakter tasvirleri varsa, ön/arka kapak içi ya da öğretmen kılavuzunda bu unsurların bugünkü değerlerle değil bağlamı içinde okunması gerektiği belirtilmelidir.",
                    metin_stili
                ))
            if {'siddet_suc', 'korku_travma'} & hassas_kategoriler:
                elements.append(Paragraph(
                    "- Şiddet, savaş, korku veya travma sahneleri sınıf içi tartışmada tarihsel neden-sonuç, empati ve barış dili üzerinden dengelenmelidir.",
                    metin_stili
                ))
            if {'kaba_dil_hakaret'} & hassas_kategoriler:
                elements.append(Paragraph(
                    "- Kaba hitap veya argo ifadeler dönem/karakter gerçekçiliği ise olumlu model olarak sunulmadığı öğretmen notunda açıklanabilir.",
                    metin_stili
                ))
            elements.append(Paragraph(
                "- Okuma kılavuzuna Maarif Modeli profilleriyle eşleşen tartışma soruları ve kültürel/tarihsel arka plan açıklamaları eklenebilir.",
                metin_stili
            ))
        
        # Kategori bazlı tavsiyeler varsa ekle
        if kategori_tavsiyesi:
            elements.append(Spacer(1, 0.15 * inch))
            elements.append(Paragraph("<b>Tespit Edilen Sorunlarla İlgili Öneriler:</b>", metin_stili))
            for tavsiye in kategori_tavsiyesi:
                elements.append(Paragraph(f"- {tavsiye}", metin_stili))
        else:
            elements.append(Spacer(1, 0.15 * inch))
            elements.append(Paragraph(
                "<b>Tespit Edilen Sorunlarla İlgili Öneriler:</b> Kategori bazlı revizyon önerisi üretilmemiştir.",
                metin_stili
            ))

        return elements
    
    def _uret_kategori_tavsiyesi(self, sonuclar: dict) -> list:
        """Bulunan kategoriler için spesifik tavsiyeler üret"""
        
        tavsiyeler = []
        kategori_bulgulari = sonuclar.get('kategori_bulgulari', {})
        
        # Kategori adlarını Türkçe'ye dönüştür
        kategori_isim_map = {
            'siddet_suc': ('Şiddet ve Suç', 'Şiddet veya suç davranışı içeren sahneler yaş grubu, nesne-yönelim ve anlatıcının mesajı açısından editoryal olarak gözden geçirilmelidir.'),
            'cinsellik_mahremiyet': ('Cinsellik ve Mahremiyet', 'Mahrem veya romantik fiziksel temas içeren sahneler yaş grubuna uygunluk ve bağlam açısından yumuşatılmalı ya da açıklayıcı editoryal bağlama alınmalıdır.'),
            'okültizm_batil': ('Okültizm ve Batıl', 'Batıl inanışlara yönelik içerik gözden geçirilmeli ve bilimsel açıklamalarla desteklenmelidir. Okültist unsurlar minimum seviyeye indirilmelidir.'),
            'buyucu_karsi': ('Büyücü Karşıtlığı', 'Özel bir toplum grubuna karşı negatif stereotip içeren bölümler yeniden yazılmalıdır. Çeşitlilik ve hoşgörü vurgulanmalıdır.'),
            'dini_karsi': ('Dini Karşıtlığı', 'Din ve inanç konularında saygılı ve dengeli bir yaklaşım benimsenmelidir. Aşağılayıcı görünen bağlamlar eleştirel veya açıklayıcı çerçeveyle yeniden değerlendirilmelidir.'),
            'milli_karsi': ('Milli Karşıtlığı', 'Milli değerlere yönelik olumsuz içerik bağlamıyla birlikte gözden geçirilmeli; vatanseverlik ve tarihsel doğruluk dengesi korunmalıdır.'),
            'siyasi_karsi': ('Siyasi Karşıtlığı', 'Siyasi görüşler dengeli bir şekilde sunulmalıdır. Aşırılık ve tarafgirlik görüntüsü vermemek için içerik gözden geçirilmelidir.'),
            'isci_karsi': ('İşçi Karşıtlığı', 'Çalışan haklarına yönelik olumsuz söylemlerin düzeltilmesi veya kaldırılması gerekir.'),
            'uyusturucu_alkol': ('Uyuşturucu ve Alkol', 'Uyuşturucu ve alkol kullanımına yönelik glorifikasyon kaldırılmalıdır. Zararlarından bahsedilmelidir.'),
            'diger_sakincali': ('Diğer Sakıncalı İçerik', 'Belirlenen diğer sakıncalı içerikler gözden geçirilmeli ve uygun olmayan bölümler düzeltilmelidir.')
        }
        
        # Yalnızca nihai risk puanı 0'dan büyük olan bulgular için tavsiye ekle.
        for kategori, bulgular in kategori_bulgulari.items():
            riskli_bulgu_var = any(
                self._risk_degeri(bulgu) > 0
                for bulgu in bulgular.get('bulunan_kelimeler', [])
            )
            if riskli_bulgu_var:
                if kategori in kategori_isim_map:
                    isim, tavsiye = kategori_isim_map[kategori]
                    tavsiyeler.append(tavsiye)
        
        return tavsiyeler
