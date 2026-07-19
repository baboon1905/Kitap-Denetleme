"""
Otomatik PDF Rapor Şablonu Generator
ReportLab ile Maarif Modeli Yayın Denetim Raporları
12 Bölüm Yapısı
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    Image, PageBreak, KeepTogether, PageTemplate, Frame
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import json
from datetime import datetime


class MaarifPDFRaporuGeneratoru:
    """
    12 Bölümlü Kurumsal Yayın Denetim Raporu Üreticisi
    """
    
    def __init__(self, dosya_adi="Rapor.pdf"):
        self.dosya_adi = dosya_adi
        self.styles = getSampleStyleSheet()
        self._ozel_stiller_ekle()
    
    def _ozel_stiller_ekle(self):
        """Maarif Modeli için özel stil tanımla"""
        
        # Başlık stili
        self.styles.add(ParagraphStyle(
            name='KitapBasligi',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1F4788'),  # Koyu mavi
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Bölüm başlığı
        self.styles.add(ParagraphStyle(
            name='BolumBasligi',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2E5C8A'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#D0D0D0'),
            borderWidth=1,
            borderPadding=6
        ))
        
        # Normal paragraf
        self.styles.add(ParagraphStyle(
            name='RaporParagrafi',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))
        
        # Karar stili (emoji ile)
        self.styles.add(ParagraphStyle(
            name='KararStili',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#D32F2F'),
            fontName='Helvetica-Bold',
            spaceAfter=6
        ))
    
    def kapak_sayfasi_olustur(self, kitap_bilgileri: dict):
        """
        1. KAPAK SAYFASI
        Kitap adı, yazar, yayınevi, analiz profili, tarih
        """
        
        elements = []
        
        # Boş alan
        elements.append(Spacer(1, 1.5*inch))
        
        # Kurum logosu alanı (yer tutucu)
        elements.append(Paragraph(
            "🏛️ TÜRKİYE YÜZYıLı MAARIF MODELİ",
            self.styles['KitapBasligi']
        ))
        elements.append(Paragraph(
            "Yayın Denetim Sistemi",
            self.styles['Heading2']
        ))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Kitap Bilgileri
        kitap_tablo = [
            ["BAŞLIK:", kitap_bilgileri.get('baslik', 'Bilinmiyor')],
            ["YAZAR:", kitap_bilgileri.get('yazar', 'Bilinmiyor')],
            ["YAYINEVI:", kitap_bilgileri.get('yayinevi', 'Bilinmiyor')],
            ["BASIM YILI:", str(kitap_bilgileri.get('basim_yili', ''))],
            ["HEDEF YAŞ:", kitap_bilgileri.get('yas_grubu', 'Bilinmiyor')],
        ]
        
        tablo = Table(kitap_tablo, colWidths=[2*inch, 4*inch])
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F0F7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(tablo)
        elements.append(Spacer(1, 0.5*inch))
        
        # Analiz Bilgileri
        elements.append(Paragraph("<b>ANALIZ BİLGİLERİ</b>", self.styles['BolumBasligi']))
        
        analiz_tablo = [
            ["Analiz Profili:", kitap_bilgileri.get('profil', 'hibrit')],
            ["Kurum Profili:", kitap_bilgileri.get('kurum_profili', 'Standart')],
            ["Analiz Tarihi:", datetime.now().strftime("%d.%m.%Y %H:%M")],
            ["Denetçi Adı:", kitap_bilgileri.get('detenci_adi', 'Sistem')],
        ]
        
        tablo2 = Table(analiz_tablo, colWidths=[2*inch, 4*inch])
        tablo2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(tablo2)
        elements.append(Spacer(1, 1*inch))
        
        elements.append(Paragraph(
            "Rapor Tarihi: " + datetime.now().strftime("%d.%m.%Y"),
            self.styles['Normal']
        ))
        
        return elements + [PageBreak()]
    
    def kitap_bilgileri_olustur(self, kitap_bilgileri: dict):
        """2. KİTAP BİLGİLERİ"""
        elements = []
        
        elements.append(Paragraph("1. KİTAP BİLGİLERİ", self.styles['BolumBasligi']))
        
        bilgi_tablo = [
            ["Başlık", kitap_bilgileri.get('baslik', '-')],
            ["Yazar(lar)", kitap_bilgileri.get('yazar', '-')],
            ["Yayınevi", kitap_bilgileri.get('yayinevi', '-')],
            ["Basım Yılı", str(kitap_bilgileri.get('basim_yili', '-'))],
            ["Toplam Sayfa", str(kitap_bilgileri.get('toplam_sayfa', '-'))],
            ["Hedef Yaş Grubu", kitap_bilgileri.get('yas_grubu', '-')],
            ["ISBN", kitap_bilgileri.get('isbn', '-')],
            ["Basım Numarası", str(kitap_bilgileri.get('basim_no', '-'))],
        ]
        
        tablo = Table(bilgi_tablo, colWidths=[2*inch, 4*inch])
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(tablo)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def yonetici_ozeti_olustur(self, analiz_sonucu: dict):
        """3. YÖNETICI ÖZETİ"""
        elements = []
        
        elements.append(Paragraph("2. YÖNETICI ÖZETİ", self.styles['BolumBasligi']))
        
        ozet_metni = f"""
        Bu kitap {analiz_sonucu.get('yas_grubu', '9-12')} yaş grubu için değerlendirilmiştir.
        Kullanılan analiz profili: <b>{analiz_sonucu.get('profil_adi', 'Hibrit')}</b>
        <br/><br/>
        <b>Genel Bulgu:</b> Kitapta {analiz_sonucu.get('toplam_bulgu', 0)} 
        sakıncalı ifade tespit edilmiştir. Bunlar {analiz_sonucu.get('toplam_kategori', 0)} 
        farklı risk kategorisine dağılmaktadır.
        <br/><br/>
        <b>Temel Riskler:</b> {analiz_sonucu.get('ana_riskler', 'Bilgisiz')}
        <br/><br/>
        <b>Önerilen Karar:</b> Bu raporun sonundaki kararları ve önerileri lütfen inceleyiniz.
        """
        
        elements.append(Paragraph(ozet_metni, self.styles['RaporParagrafi']))
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def genel_karar_ve_risk_olustur(self, analiz_sonucu: dict):
        """3. GENEL KARAR VE RİSK SKORU"""
        elements = []
        
        elements.append(Paragraph("3. GENEL KARAR VE RİSK SKORU", self.styles['BolumBasligi']))
        
        skor = analiz_sonucu.get('final_skor', 0)
        karar = analiz_sonucu.get('karar', {})
        
        # Risk skoru kutusu
        skor_metni = f"<font size=14><b>RİSK SKORU: {skor}/100</b></font>"
        elements.append(Paragraph(skor_metni, self.styles['KararStili']))
        
        karar_metni = f"<font size=12><b>KARAR: {karar.get('simge', '❓')} {karar.get('seviye', 'Bilinmiyor')}</b></font>"
        elements.append(Paragraph(karar_metni, self.styles['KararStili']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Karar açıklaması
        aciklama = {
            "0-20": "Bu kitap seçilen profil için uygun bulunmuştur. Herhangi bir düzeltme gerekmemektedir.",
            "21-40": "Bu kitap seçilen profil için düşük risk taşımaktadır. Önerilen notlara göz atınız.",
            "41-60": "Bu kitapta dikkat edilmesi gereken içerik bulunmaktadır. Lütfen bulgular bölümünü inceleyiniz.",
            "61-80": "Bu kitapta revizyon gereken bölümler bulunmaktadır. Zorunlu düzeltmeler bölümünü inceleyiniz.",
            "81-100": "Bu kitap seçilen profil için uygun değildir. Kapsamlı revizyonlar gereklidir."
        }
        
        # Aralık bul
        if skor <= 20:
            aralik = "0-20"
        elif skor <= 40:
            aralik = "21-40"
        elif skor <= 60:
            aralik = "41-60"
        elif skor <= 80:
            aralik = "61-80"
        else:
            aralik = "81-100"
        
        elements.append(Paragraph(
            f"<i>{aciklama.get(aralik, 'Bilgisiz')}</i>",
            self.styles['RaporParagrafi']
        ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def sakinacali_icerik_bulgusu_olustur(self, bulgular: dict):
        """4. SAKINCALI İÇERİK BULGUSU"""
        elements = []
        
        elements.append(Paragraph("4. SAKINCALI İÇERİK BULGUSU", self.styles['BolumBasligi']))
        
        # Kategori tablosu
        basliklar = ["Kategori", "Bulgu Sayısı", "Risk Puanı", "Durumu"]
        satirlar = [basliklar]
        
        for kategori, bulgu_data in bulgular.items():
            if bulgu_data.get('bulundu', False):
                satirlar.append([
                    kategori.replace('_', ' ').title(),
                    str(bulgu_data.get('toplam_bulgu', 0)),
                    f"{bulgu_data.get('risk_puani', 0)}/5",
                    "🔴 Riskli" if bulgu_data.get('risk_puani', 0) >= 4 else "⚠️ Uyarı"
                ])
        
        if len(satirlar) > 1:
            tablo = Table(satirlar, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch])
            tablo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(tablo)
        else:
            elements.append(Paragraph(
                "<i>Sakıncalı içerik tespit edilmemiştir.</i>",
                self.styles['RaporParagrafi']
            ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def yanlis_pozitifler_olustur(self, yanlislar: list):
        """5. YANLIŞ POZİTİFLER"""
        elements = []
        
        elements.append(Paragraph("5. YANLIŞ POZİTİFLER", self.styles['BolumBasligi']))
        
        if yanlislar:
            elements.append(Paragraph(
                "<b>Aşağıdaki kelimeler bağlamsal analiz sonucunda gerçek risk taşımamıştır:</b>",
                self.styles['RaporParagrafi']
            ))
            
            for i, yanlis in enumerate(yanlislar[:10], 1):
                elements.append(Paragraph(
                    f"{i}. <b>{yanlis['kelime']}</b> - {yanlis['sebep']}",
                    self.styles['RaporParagrafi']
                ))
        else:
            elements.append(Paragraph(
                "<i>Yanlış pozitif tespit edilmemiştir.</i>",
                self.styles['RaporParagrafi']
            ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def maarif_profilleri_olustur(self, profiller: dict):
        """7. MAARIF MODELİ ÖĞRENCİ PROFİLİ UYUMU"""
        elements = []
        
        elements.append(Paragraph("6. MAARIF MODELİ ÖĞRENCİ PROFİLİ UYUMU", self.styles['BolumBasligi']))
        
        profil_tablo = [["Profil Adı", "Puan", "Sonuç"]]
        
        for profil_adi, profil_data in profiller.items():
            puan = profil_data.get('puan', 0)
            sonuc = "✅ Güçlü" if puan >= 4 else "✔️ Orta" if puan >= 2 else "⚠️ Zayıf"
            profil_tablo.append([
                profil_data.get('profil_adi', profil_adi).replace('_', ' ').title(),
                f"{puan}/5",
                sonuc
            ])
        
        tablo = Table(profil_tablo, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(tablo)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def meb_kriterleri_olustur(self, meb_sonuclari: dict):
        """8. MEB KRİTERLERİ MATRİSİ"""
        elements = []
        
        elements.append(Paragraph("7. MEB KRİTERLERİ MATRİSİ", self.styles['BolumBasligi']))
        
        meb_tablo = [["Kriter", "Risk", "Karar"]]
        
        for kriter_key, kriter_data in meb_sonuclari.items():
            meb_tablo.append([
                kriter_data.get('ad', kriter_key),
                f"{kriter_data.get('risk', 0)}/5",
                kriter_data.get('karar', 'Bilinmiyor')
            ])
        
        tablo = Table(meb_tablo, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D32F2F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFEBEE')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(tablo)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def zorunlu_duzenlemeler_olustur(self, duzenlemeler: list):
        """9. ZORUNLU DÜZELTMELER"""
        elements = []
        
        elements.append(Paragraph("8. ZORUNLU DÜZELTMELER", self.styles['BolumBasligi']))
        
        if duzenlemeler:
            for i, duzeltme in enumerate(duzenlemeler, 1):
                elements.append(Paragraph(
                    f"<b>{i}. Sayfa {duzeltme.get('sayfa', '?')}:</b>",
                    self.styles['Normal']
                ))
                elements.append(Paragraph(
                    f"<i>Orijinal:</i> {duzeltme.get('orijinal', 'Bilgisiz')[:100]}",
                    self.styles['RaporParagrafi']
                ))
                elements.append(Paragraph(
                    f"<i>Önerilen:</i> {duzeltme.get('onerilen', 'Bilgisiz')[:100]}",
                    self.styles['RaporParagrafi']
                ))
                elements.append(Spacer(1, 0.1*inch))
        else:
            elements.append(Paragraph(
                "<i>Zorunlu düzeltme gerekli değildir.</i>",
                self.styles['RaporParagrafi']
            ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def onerilen_duzenlemeler_olustur(self, oneriler: list):
        """10. ÖNERİLEN DÜZELTMELER"""
        elements = []
        
        elements.append(Paragraph("9. ÖNERİLEN DÜZELTMELER", self.styles['BolumBasligi']))
        
        if oneriler:
            for i, oneri in enumerate(oneriler, 1):
                elements.append(Paragraph(
                    f"<b>{i}. {oneri.get('baslik', 'Öneri')}</b>",
                    self.styles['Normal']
                ))
                elements.append(Paragraph(
                    f"{oneri.get('aciklama', 'Açıklama yok')}",
                    self.styles['RaporParagrafi']
                ))
                elements.append(Spacer(1, 0.1*inch))
        else:
            elements.append(Paragraph(
                "<i>Ek öneriler bulunmamaktadır.</i>",
                self.styles['RaporParagrafi']
            ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def ogretmen_veli_notlari_olustur(self, notlar: dict):
        """11. ÖĞRETMEN/VELİ İÇİN KULLANIM NOTLARI"""
        elements = []
        
        elements.append(Paragraph("10. ÖĞRETMEN/VELİ İÇİN KULLANIM NOTLARI", self.styles['BolumBasligi']))
        
        # Öğretmen notları
        if notlar.get('ogretmen'):
            elements.append(Paragraph("<b>Öğretmen İçin:</b>", self.styles['Normal']))
            elements.append(Paragraph(
                notlar.get('ogretmen', 'Not yok'),
                self.styles['RaporParagrafi']
            ))
        
        # Veli notları
        if notlar.get('veli'):
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph("<b>Veli İçin:</b>", self.styles['Normal']))
            elements.append(Paragraph(
                notlar.get('veli', 'Not yok'),
                self.styles['RaporParagrafi']
            ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def detenci_onay_olustur(self, detenci_bilgileri: dict):
        """12. DENETÇİ ONAY SAYFASI"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("11. DENETÇİ ONAY", self.styles['BolumBasligi']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        onay_metni = f"""
        <b>Rapor Bilgileri:</b><br/>
        Rapor Tarihi: {datetime.now().strftime("%d.%m.%Y %H:%M")}<br/>
        Denetçi Adı: {detenci_bilgileri.get('ad', 'Bilgisiz')}<br/>
        Unvan: {detenci_bilgileri.get('unvan', 'Bilgisiz')}<br/>
        Kurum: {detenci_bilgileri.get('kurum', 'Bilgisiz')}<br/>
        <br/>
        <b>İmza Yeri:</b><br/><br/><br/>
        _____________________<br/>
        <i>Denetçi İmzası ve Mühürü</i>
        """
        
        elements.append(Paragraph(onay_metni, self.styles['RaporParagrafi']))
        
        return elements
    
    def rapor_uret(self, kitap_bilgileri: dict, analiz_sonucu: dict, 
                   meb_sonuclari: dict = None, detenci_bilgileri: dict = None):
        """
        12 Bölümlü Tam Rapor Üret
        """
        
        elements = []
        
        # 1. Kapak
        elements.extend(self.kapak_sayfasi_olustur(kitap_bilgileri))
        
        # 2. Kitap Bilgileri
        elements.extend(self.kitap_bilgileri_olustur(kitap_bilgileri))
        
        # 3. Yönetici Özeti
        elements.extend(self.yonetici_ozeti_olustur(analiz_sonucu))
        
        # 4. Genel Karar
        elements.extend(self.genel_karar_ve_risk_olustur(analiz_sonucu))
        
        # 5. Sakıncalı İçerik
        elements.extend(self.sakinacali_icerik_bulgusu_olustur(
            analiz_sonucu.get('kategori_bulgulari', {})
        ))
        
        # 6. Yanlış Pozitifler
        elements.extend(self.yanlis_pozitifler_olustur(
            analiz_sonucu.get('yanlis_pozitifler', [])
        ))
        
        # 7. Maarif Profilleri
        elements.extend(self.maarif_profilleri_olustur(
            analiz_sonucu.get('maarif_profilleri', {})
        ))
        
        # 8. MEB Kriterleri
        if meb_sonuclari:
            elements.extend(self.meb_kriterleri_olustur(
                meb_sonuclari.get('meb_kriterler', {})
            ))
        
        # 9. Zorunlu Düzeltmeler
        elements.extend(self.zorunlu_duzenlemeler_olustur(
            analiz_sonucu.get('zorunlu_duzenlemeler', [])
        ))
        
        # 10. Önerilen Düzeltmeler
        elements.extend(self.onerilen_duzenlemeler_olustur(
            analiz_sonucu.get('onerilen_duzenlemeler', [])
        ))
        
        # 11. Öğretmen/Veli Notları
        elements.extend(self.ogretmen_veli_notlari_olustur(
            analiz_sonucu.get('notlar', {})
        ))
        
        # 12. Denetçi Onayı
        if detenci_bilgileri:
            elements.extend(self.detenci_onay_olustur(detenci_bilgileri))
        
        # PDF Oluştur
        doc = SimpleDocTemplate(
            self.dosya_adi,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=36
        )
        
        doc.build(elements)
        
        return self.dosya_adi


# Kullanım örneği
if __name__ == "__main__":
    
    # Örnek veri
    kitap = {
        'baslik': 'Çocuk Macerası',
        'yazar': 'Örnek Yazar',
        'yayinevi': 'Örnek Yayınevi',
        'basim_yili': 2024,
        'toplam_sayfa': 150,
        'yas_grubu': '9-12',
        'isbn': '978-1-234567-89-0',
        'profil': 'hibrit',
        'detenci_adi': 'Ahmet Bey'
    }
    
    analiz = {
        'final_skor': 35,
        'karar': {'simge': '✔️', 'seviye': 'Düşük Risk'},
        'toplam_bulgu': 3,
        'toplam_kategori': 2,
        'ana_riskler': 'Hafif korku unsurları',
        'kategori_bulgulari': {
            'korku_travma': {'bulundu': True, 'toplam_bulgu': 2, 'risk_puani': 2},
            'kaba_dil': {'bulundu': True, 'toplam_bulgu': 1, 'risk_puani': 1}
        },
        'yanlis_pozitifler': [],
        'maarif_profilleri': {
            'cesur': {'profil_adi': 'Cesaretli', 'puan': 4}
        },
        'notlar': {
            'ogretmen': 'Sınıf ortamında kullanılabilir, ancak öğretmen yönlendirmesi tavsiye edilir.',
            'veli': 'Çocukla birlikte okumak daha faydalı olacaktır.'
        },
        'zorunlu_duzenlemeler': [],
        'onerilen_duzenlemeler': [
            {'baslik': 'Sayfa 45', 'aciklama': 'Korku unsurı daha yumuşak ifade edilebilir.'}
        ]
    }
    
    meb = {
        'meb_kriterler': {
            'anayasa': {'ad': 'Anayasa', 'risk': 0, 'karar': 'Uyumlu'},
            'milli_guvenlik': {'ad': 'Millî Güvenlik', 'risk': 0, 'karar': 'Temiz'}
        }
    }
    
    detenci = {
        'ad': 'Ahmet Kaya',
        'unvan': 'Yayın Denetmeni',
        'kurum': 'MEB Yayın Denetim Merkezi'
    }
    
    # Rapor üret
    generator = MaarifPDFRaporuGeneratoru("Ornek_Rapor.pdf")
    dosya = generator.rapor_uret(kitap, analiz, meb, detenci)
    print(f"✅ Rapor oluşturuldu: {dosya}")
