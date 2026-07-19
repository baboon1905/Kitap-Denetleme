#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEB TTK Detaylı Bulgu Raporlama Sistemi
PDF raporuna entegre edilecek modül
"""

from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors


class MEBBulgularıRaporlayıcı:
    """MEB kriterleri için detaylı bulgu raporlayıcı"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
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
    
    def olustur_genisletilmis_meb_bolumu(self, sonuclar: dict, pdf_text: str = "") -> list:
        """
        Genişletilmiş MEB TTK bölümü oluştur
        - Özet tablosu
        - Her kriterin detaylı bulguları (varsa)
        - Revizyon önerileri
        """
        
        elements = []
        
        # ===== BASLIK =====
        baslik_stili = ParagraphStyle(
            'BaslikStili',
            parent=self.styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12
        )
        
        metin_stili = ParagraphStyle(
            'MetinStili',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6
        )
        
        riskli_stili = ParagraphStyle(
            'RiskliStili',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#c00000'),
            spaceAfter=4
        )
        
        normal_stili = ParagraphStyle(
            'NormalStili',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            leftIndent=20
        )
        
        elements.append(Paragraph("<b>4. MEB TTK Kriterleri Analizi</b>", baslik_stili))
        elements.append(Spacer(1, 0.15 * inch))
        
        # ===== ÖZETİ TABLO =====
        meb_eval = sonuclar.get('meb_degerlendirmesi', {})
        meb_kriterler = meb_eval.get('meb_kriterler', {})
        meb_puani = meb_eval.get('meb_puani', 50)
        meb_karar = meb_eval.get('genel_karar', '⚠️ Bilinmiyor')
        
        # Özet tablosu
        tablo_veriler = [["Kriter", "Durum", "Risk"]]
        
        for kriter_key, kriter_adi in self.kriterler.items():
            if kriter_key in meb_kriterler:
                kriter_data = meb_kriterler[kriter_key]
                karar = kriter_data.get('karar', 'Bilinmiyor')
                risk = kriter_data.get('risk', 0)
                
                # Risk seviyesine göre sembol
                if risk <= 1:
                    durum_simgesi = "✅"
                elif risk <= 2:
                    durum_simgesi = "✔️"
                elif risk <= 3:
                    durum_simgesi = "⚠️"
                else:
                    durum_simgesi = "🔴"
                
                tablo_veriler.append([
                    kriter_adi,
                    f"{durum_simgesi} {karar}",
                    f"{risk}/5"
                ])
        
        tablo = Table(tablo_veriler, colWidths=[2.55 * inch, 2.0 * inch, 0.95 * inch])
        tablo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        elements.append(tablo)
        elements.append(Spacer(1, 0.15 * inch))
        
        # ===== MEB PUANI VE KARAR =====
        elements.append(Paragraph(
            f"<b>MEB Uyum Puanı:</b> {meb_puani}/100 → {meb_karar}",
            metin_stili
        ))
        elements.append(Spacer(1, 0.08 * inch))
        
        if meb_puani >= 75:
            sonuc_metni = ("✅ <b>UYGUN</b> - Kitap MEB Talim ve Terbiye Kurulu kriterlerine "
                          "uygun bulunmuştur. Yayına hazır.")
        elif meb_puani >= 50:
            sonuc_metni = ("✔️ <b>KOŞULLU</b> - Kitap koşullu olarak MEB kriterlerine uygun "
                          "olabilir. Aşağıdaki işaretli bölümler kontrol ve düzeltilmelidir.")
        elif meb_puani >= 25:
            sonuc_metni = ("⚠️ <b>REVIZYON GEREKLİ</b> - Kitabın MEB kriterlerine uygun hale "
                          "gelmesi için önemli düzeltmeler gereklidir.")
        else:
            sonuc_metni = ("❌ <b>UYGUN DEĞİL</b> - Kitap mevcut haliyle MEB Talim ve Terbiye "
                          "Kurulu kriterlerine uygun değildir. Yayınlanması önerilmez.")
        
        elements.append(Paragraph(sonuc_metni, riskli_stili))
        elements.append(Spacer(1, 0.15 * inch))
        
        # ===== DETAYLI BULGULARIN OLMASI DURUMUNDA =====
        meb_bulgulari = sonuclar.get('meb_bulgulari', {})
        
        if meb_bulgulari and any(meb_bulgulari.values()):
            elements.append(Paragraph("<b>4.1 Detaylı Bulgu Analizi</b>", baslik_stili))
            elements.append(Spacer(1, 0.1 * inch))
            
            for kriter_key, bulgular_listesi in meb_bulgulari.items():
                if bulgular_listesi:  # Eğer bu kriterin bulgusu varsa
                    kriter_adi = self.kriterler.get(kriter_key, kriter_key)
                    
                    # Kriter başlığı
                    elements.append(Paragraph(
                        f"<b>🔸 {kriter_adi}</b>",
                        ParagraphStyle(
                            'KriterBaslık',
                            parent=metin_stili,
                            fontSize=11,
                            textColor=colors.HexColor('#c00000'),
                            spaceBefore=6,
                            spaceAfter=6
                        )
                    ))
                    
                    # Her bulgu
                    for i, bulgu in enumerate(bulgular_listesi, 1):
                        # Sayfa + alinti
                        if bulgu.get('sayfa', 0) > 0:
                            sayfa_str = f"(Sayfa {bulgu['sayfa']})"
                        else:
                            sayfa_str = "(Sayfa Bilinmiyor)"
                        
                        elements.append(Paragraph(
                            f"<b>Bulgu {i}:</b> {sayfa_str}",
                            normal_stili
                        ))
                        
                        # Alıntı
                        quote_text = bulgu.get('alinți', '')[:150]
                        elements.append(Paragraph(
                            f"<i>Alinti:</i> \"{quote_text}\"",
                            ParagraphStyle(
                                'Alinți',
                                parent=normal_stili,
                                fontSize=9,
                                textColor=colors.HexColor('#666666')
                            )
                        ))
                        
                        # Sebebi ve risk
                        sebebi = bulgu.get('sebebi', 'Bilinmiyor')
                        risk = bulgu.get('risk_puani', 0)
                        elements.append(Paragraph(
                            f"<i>Sebebi:</i> {sebebi} (Risk: {risk}/5)",
                            normal_stili
                        ))
                        
                        # Önerilen revizyon
                        revizyon = bulgu.get('onerili_revizyon', '')
                        elements.append(Paragraph(
                            f"<b>Revizyon:</b> {revizyon}",
                            ParagraphStyle(
                                'Revizyon',
                                parent=normal_stili,
                                textColor=colors.HexColor('#006000'),
                                fontSize=9
                            )
                        ))
                        
                        elements.append(Spacer(1, 0.08 * inch))
                    
                    elements.append(Spacer(1, 0.08 * inch))
        
        # ===== SONUÇ ÖNERISI =====
        elements.append(Paragraph("<b>4.2 Sonuç ve Öneriler</b>", baslik_stili))
        elements.append(Spacer(1, 0.08 * inch))
        
        if meb_puani >= 75:
            oneriler = [
                "Kitap MEB standartlarına uygundur ve yayınlamaya hazırdır.",
                "Okul kütüphanelerine ve sınıflara önerilen kitaplar listesine eklenebilir."
            ]
        elif meb_puani >= 50:
            oneriler = [
                "Yukarıda belirtilen bulguların yazarla birlikte incelenmesi gerekmektedir.",
                "Riskli bölümlerin bağlamsal analizi yapılarak revizyon gerçekleştirilmesi tavsiye edilir.",
                "Düzeltmelerden sonra yeniden değerlendirme yapılmalıdır."
            ]
        else:
            oneriler = [
                "Kitabın yayınlanabilmesi için önemli yapısal değişiklikler gereklidir.",
                "Yazarla birlikte MEB kriterlerine uygun hale getirme çalışması yapılmalıdır.",
                "Alternatif kaynakların değerlendirilmesi önerilir."
            ]
        
        for oneri in oneriler:
            elements.append(Paragraph(f"• {oneri}", normal_stili))
        
        elements.append(Spacer(1, 0.15 * inch))
        
        return elements


# ÖRNEK KULLANIM
if __name__ == "__main__":
    raporlayıcı = MEBBulgularıRaporlayıcı()
    
    # Örnek sonuç
    test_sonucu = {
        'meb_degerlendirmesi': {
            'meb_kriterler': {
                'anayasa': {'karar': 'Uyumlu', 'risk': 0},
                'milli_guvenlik': {'karar': 'Temiz', 'risk': 0},
                'esitlik': {'karar': 'Uygun', 'risk': 0},
                'milli_manevi': {'karar': 'Orta', 'risk': 4},
                'guvenlik': {'karar': 'Uygun', 'risk': 0},
                'bilimsel': {'karar': 'Doğru', 'risk': 0},
                'reklam': {'karar': 'Hafif', 'risk': 1},
                'dil': {'karar': 'Temiz', 'risk': 0},
            },
            'meb_puani': 50,
            'genel_karar': '✔️ Koşullu'
        },
        'meb_bulgulari': {
            'milli_manevi': [
                {
                    'sayfa': 15,
                    'alinți': 'Karakterler hiçbir aile bağı göstermemiştir.',
                    'sebebi': 'Aile değeri eksikliği',
                    'risk_puani': 2,
                    'onerili_revizyon': 'Aile ili ilişkisini güçlendir.'
                },
                {
                    'sayfa': 23,
                    'alinți': 'Vatan mefhumu artık eski kalıptır.',
                    'sebebi': 'Vatan değeri aşağılanması',
                    'risk_puani': 3,
                    'onerili_revizyon': 'Ifadeyi bağlam ekleyerek güçlendir.'
                }
            ],
            'reklam': [
                {
                    'sayfa': 42,
                    'alinți': 'iPhone en iyi teknoloji ürünüdür.',
                    'sebebi': 'Marka tanıtımı',
                    'risk_puani': 1,
                    'onerili_revizyon': 'Marka adını sil, genel referans yapılsın.'
                }
            ]
        }
    }
    
    elements = raporlayıcı.olustur_genisletilmis_meb_bolumu(test_sonucu)
    
    print("✅ Rapor elemanları başarıyla oluşturuldu!")
    print(f"Toplam {len(elements)} element oluşturuldu.")
