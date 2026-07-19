"""
Kitap Bazlı Örnek Analiz Raporları
4 Farklı Kitap Türü ile Detaylı Örnekler
"""

import json
from datetime import datetime

# ============================================================================
# ÖRNEK 1: ÇOCUK HİKAYESİ / 8+ YAŞ
# ============================================================================

COCUK_HIKAYESI = {
    "kitap_bilgileri": {
        "baslik": "Küçük Kaplan'ın Macerası",
        "yazar": "Örnek Yazar",
        "yayinevi": "Çocuk Yayıncılık A.Ş.",
        "basim_yili": 2024,
        "yas_grubu": "8+ yaş",
        "toplam_sayfa": 96,
        "isbn": "978-975-234-567-8"
    },
    "analiz_ozeti": {
        "profil_analizi": "Hibrit (Önerilen)",
        "final_skor": 32,
        "karar": "✔️ Düşük Risk - Veli Rehberliğiyle Uygun",
        "bolgeler": {
            "maarif_meb": 42,
            "hibrit": 32,
            "editoryal": 18,
            "hassas_veli": 54,
            "kuruma_ozel": 35
        }
    },
    "bulgular": [
        {
            "kategori": "Korku & Travma",
            "bulgu_sayisi": 2,
            "sayfa_ornekleri": [25, 67],
            "risk": 2,
            "ornekler": [
                {
                    "sayfa": 25,
                    "alinti": "Karanlık orman çok korkutucu görünüyordu",
                    "bağlam": "Kaplan yolunu kaybetmiş ormanda yürüyordu",
                    "ai_yorum": "Çocuk hikayesi bağlamında normal korku unsuru, çok hafif",
                    "sonuç": "Düşük risk (Risk: 2/5)"
                }
            ]
        },
        {
            "kategori": "Kaba Dil & Hakaret",
            "bulgu_sayisi": 1,
            "sayfa_ornekleri": [45],
            "risk": 1,
            "ornekler": [
                {
                    "sayfa": 45,
                    "alinti": "Aptal gökkuşağı, nereden bildiğini sorabildim",
                    "bağlam": "Çocuk kahraman kızlı karakterin konuşması",
                    "ai_yorum": "Karakterin kişiliği göstermek için kullanılmış, çok hafif",
                    "sonuç": "Çok Düşük Risk (Risk: 1/5)"
                }
            ]
        }
    ],
    "maarif_profilleri": {
        "sorgulayici": 5,
        "cesaretli": 4,
        "uretken": 3,
        "bilge": 2,
        "ahlaklı": 4,
        "merhametli": 4,
        "vatansever": 3,
        "estetik": 4,
        "iradeli": 5,
        "saglikli": 3
    },
    "maarif_uyum_puani": 76,
    "meb_kriterleri": {
        "anayasa": {"risk": 0, "karar": "Uyumlu"},
        "milli_guvenlik": {"risk": 0, "karar": "Temiz"},
        "esitlik": {"risk": 0, "karar": "Uygun"},
        "milli_manevi": {"risk": 1, "karar": "Orta"},
        "guvenlik": {"risk": 1, "karar": "Uygun"},
        "bilimsel": {"risk": 0, "karar": "Doğru"},
        "reklam": {"risk": 0, "karar": "Temiz"},
        "dil": {"risk": 1, "karar": "Dikkat"}
    },
    "meb_puani": 77,
    "oneriler": [
        "S.25: Korku sahnesi normaldir ancak ebeveyn rehberliği faydalı olabilir",
        "S.45: Hafif argo; çocuk karakterinin yaşına uygun, problem olmasa da",
        "Öğretmen için: Hikaye arkadaşlık, cesaret ve azim temalarını destekliyor",
        "Veli için: 7-8 yaş çocukla birlikte okumak ideal, karakter tartışmaları yapabilir"
    ],
    "karar_ozeti": """
Bu kitap 8+ yaş grubu için uygundur. Çocuk karakterlerinin başarı hikayesi, 
cesaret ve arkadaşlık temalarını destekler. Hafif korku unsurları ve 
minimal argo, hikaye anlatımında doğal bulunmaktadır. Veli rehberliğiyle 
7 yaş çocuklara da okutulabilir.

🌟 GÜÇ YÖNLERI: Maarif profilleri (Cesaretli, İradeli), 
karakterlerin pozitif yönelimleri, doğa sevgisi.

⚠️ DİKKAT: Korku unsurları sensitif çocuklarla konuşulmalı.
"""
}

# ============================================================================
# ÖRNEK 2: GENÇLIK ROMANI / 14+ YAŞ
# ============================================================================

GENCLIK_ROMANI = {
    "kitap_bilgileri": {
        "baslik": "Gizli Sevgi",
        "yazar": "Sebnem Yazarı",
        "yayinevi": "Gençlik Yayınları Ltd.",
        "basim_yili": 2024,
        "yas_grubu": "14+ yaş",
        "toplam_sayfa": 248,
        "isbn": "978-975-456-789-0"
    },
    "analiz_ozeti": {
        "profil_analizi": "Hibrit (Önerilen)",
        "final_skor": 45,
        "karar": "⚠️ Dikkat Gerektirir - Fark Profil Seçimine Göre Değişir",
        "bolgeler": {
            "maarif_meb": 62,
            "hibrit": 45,
            "editoryal": 28,
            "hassas_veli": 75,
            "kuruma_ozel": 50
        }
    },
    "bulgular": [
        {
            "kategori": "Cinsellik & Mahremiyet",
            "bulgu_sayisi": 3,
            "risk": 3,
            "ornekler": [
                {
                    "sayfa": 89,
                    "alinti": "Onun elleri omuzlarımda… kalp atışlarım hızlandı",
                    "bağlam": "Gençlik romanında ilk öpüşme sahnesi",
                    "ai_yorum": "Dönemsel ergenlik teması, mahrem değil, edebi bağlamda ok",
                    "sonuç": "Orta Risk (Risk: 3/5)"
                },
                {
                    "sayfa": 156,
                    "alinti": "Yalnız kaldığımız odada hava ağırlaştı",
                    "bağlam": "Çift arasındaki gerginlik, başka açık tanım yok",
                    "ai_yorum": "Muğlak ifade, ergenlik romanında sık görülen, özendirme yok",
                    "sonuç": "Düşük-Orta Risk (Risk: 2/5)"
                }
            ]
        },
        {
            "kategori": "Olumsuz Davranış Modeli",
            "bulgu_sayisi": 4,
            "risk": 2,
            "ornekler": [
                {
                    "sayfa": 123,
                    "alinti": "Gizli ağlayan kitapla baş başa yalnızlığımı paylaştım",
                    "bağlam": "Sosyal izolasyon, yalnızlık teması",
                    "ai_yorum": "Ergen depresyonunun tanımı yapılsa da, negatif normalizasyon yok",
                    "sonuç": "Dikkat (Risk: 2/5)"
                }
            ]
        }
    ],
    "maarif_profilleri": {
        "sorgulayici": 3,
        "cesaretli": 2,
        "uretken": 3,
        "bilge": 2,
        "ahlaklı": 2,
        "merhametli": 3,
        "vatansever": 1,
        "estetik": 4,
        "iradeli": 2,
        "saglikli": 1
    },
    "maarif_uyum_puani": 43,
    "meb_kriterleri": {
        "anayasa": {"risk": 0, "karar": "Uyumlu"},
        "milli_guvenlik": {"risk": 0, "karar": "Temiz"},
        "esitlik": {"risk": 1, "karar": "Dikkat"},
        "milli_manevi": {"risk": 2, "karar": "Zayıf"},
        "guvenlik": {"risk": 2, "karar": "Uyarı"},
        "bilimsel": {"risk": 0, "karar": "Doğru"},
        "reklam": {"risk": 0, "karar": "Temiz"},
        "dil": {"risk": 1, "karar": "Dikkat"}
    },
    "meb_puani": 48,
    "oneriler": [
        "Hibrit profilde 14+ için uygun, ancak 12-13 yaş için daha sıkı denetim önerilir",
        "Maarif/MEB profilde 62/100; hassas okullar danışman/veli bilgisini almalıdır",
        "Editoryal profilde 28/100; yayınevi 14+ kitle için normal başarılı roman",
        "S.89: Kısaca açık olsa da, 14+ yaş grubunun beklentisi; başka masalı yok",
        "S.123: Yalnızlık teması gerçekçi ancak, çözüm önerisinin (arkadaş destek) eklenmesi iyi olurdu"
    ],
    "karar_ozeti": """
Bu kitap 14+ yaş grubuna uygundur. Ergenlik, ilk aşk, yalnızlık ve 
aile çatışması temaları yaşa uygun şekilde işlenmiştir. 

Seçilen profil önemlıdir:
• Hibrit & Editoryal: 14+ UYGUN
• Maarif/MEB: 12-13 yaş için UYARILI, 14+ KOŞULLU
• Hassas Veli: 14+ (KOŞULLU), 12-13 yaş UYGUN DEĞİL

🌟 GÜÇLÜ YÖNLER: Ergen psikolojisinin doğru temsili, 
dost/aile desteğinin öneminin vurgulanması.

⚠️ UYARILAR: Sosyal izolasyon normalleştirilmeden, 
çözüm odaklı kurgu tercih edilmeliydi.
"""
}

# ============================================================================
# ÖRNEK 3: TARİHÎ ROMAN / 12+ YAŞ
# ============================================================================

TARIFI_ROMAN = {
    "kitap_bilgileri": {
        "baslik": "Millî Mücadele'nin Kahramanları",
        "yazar": "Tarih Yazarı",
        "yayinevi": "Eğitim Yayınları",
        "basim_yili": 2023,
        "yas_grubu": "12+ yaş",
        "toplam_sayfa": 312,
        "isbn": "978-975-678-901-2"
    },
    "analiz_ozeti": {
        "profil_analizi": "Maarif/MEB (Uygun Profil)",
        "final_skor": 38,
        "karar": "✔️ Düşük Risk - Tarihî Bağlam Korunmuş",
        "bolgeler": {
            "maarif_meb": 38,
            "hibrit": 28,
            "editoryal": 15,
            "hassas_veli": 52,
            "kuruma_ozel": 35
        }
    },
    "bulgular": [
        {
            "kategori": "Şiddet & Suç",
            "bulgu_sayisi": 12,
            "risk": 4,
            "ornekler": [
                {
                    "sayfa": 156,
                    "alinti": "Osmanlı birliklerinin top sesleri şehri sarsıyordu",
                    "bağlam": "1920 Millî Mücadele savaş sahnesi, tarihî gerçek",
                    "ai_yorum": "Tarihî bağlamda gerçek savaş, horlama/grafik detay yok",
                    "sonuç": "Tarihî Referans (Risk: 0/5 - Maarif'te -1)"
                },
                {
                    "sayfa": 234,
                    "alinti": "Ölüm sahasında ölen askerler için dua ediliyordu",
                    "bağlam": "Ölüm, fakat hüzünlü ve saygılı tasvir",
                    "ai_yorum": "Ölüm temas olsa da kurgu değil, gerçek (Maarif düşük risk)",
                    "sonuç": "Tarihî Anlatım (Risk: 1/5)"
                }
            ]
        },
        {
            "kategori": "Vatanseverlik & Milli Değerler",
            "bulgu_sayisi": 28,
            "risk": -2,  # Olumsuz risk = Pozitif katkı
            "ornekler": [
                {
                    "sayfa": 78,
                    "alinti": "Vatan için can vermek onur sayılırdı",
                    "bağlam": "Kahramanların vatan sevgisi",
                    "ai_yorum": "Pozitif maarif teması: Vatanseverlik, sorumluluk",
                    "sonuç": "Maarif Uyumlu (+2 Maarif puanı)"
                }
            ]
        }
    ],
    "maarif_profilleri": {
        "sorgulayici": 4,
        "cesaretli": 5,
        "uretken": 3,
        "bilge": 4,
        "ahlaklı": 5,
        "merhametli": 3,
        "vatansever": 5,  # Maximal puan!
        "estetik": 3,
        "iradeli": 5,
        "saglikli": 2
    },
    "maarif_uyum_puani": 84,  # Çok Yüksek
    "meb_kriterleri": {
        "anayasa": {"risk": 0, "karar": "Uyumlu"},
        "milli_guvenlik": {"risk": 0, "karar": "Temiz"},
        "esitlik": {"risk": 0, "karar": "Uygun"},
        "milli_manevi": {"risk": 0, "karar": "Güçlü"},
        "guvenlik": {"risk": 1, "karar": "Tarihî"},
        "bilimsel": {"risk": 0, "karar": "Doğru"},
        "reklam": {"risk": 0, "karar": "Temiz"},
        "dil": {"risk": 0, "karar": "Temiz"}
    },
    "meb_puani": 90,  # Çok Yüksek
    "oneriler": [
        "Bu kitap Maarif/MEB profili için ideal örnektir",
        "S.156-234: Savaş sahneleri tarihî bağlamda uygulandığı için risk minimal",
        "Vatanseverlik temaları (28 örnek) doğru ve değerli bir şekilde ele alınmıştır",
        "Okul kütüphanesi için 6. sınıf+ için TÜM okulların alması önerilir",
        "Öğretmen notu: Sınıf tartışması için ideal, Maarif profili: Cesaretli, İradeli"
    ],
    "karar_ozeti": """
Bu kitap Maarif/MEB modeline göre HARIKA FİT'TİR (90/100).

Tarihî bağlamda savaş unsurları tamamen uygulandığında:
• Şiddet sahneleri = Tarihî Gerçeklik (Risk -1)
• Ölüm temaları = Saygılı Tutum (Risk 0-1)
• Vatanseverlik = Maarif Modeli Hedefi (Bonus +2)

12+ yaş grubunun sosyal çalışmalar ve tarih müfredatıyla doğrudan 
uyumluluk göstermektedir.

🏆 ÖZELLİKLER:
- Maarif profilleri: Cesaretli 5/5, Vatansever 5/5, İradeli 5/5
- MEB Kriterleri: 8/8 Geçti
- Maarif Uyum: 84/100
- Önerilen: 10/10

✅ KARAR: OKUL KÜTÜPHANESİ OKUMALARI İÇİN ŞIDDETLE ÖNERİLİR
"""
}

# ============================================================================
# ÖRNEK 4: FANTASTIK HİKAYE / 10+ YAŞ
# ============================================================================

FANTASTIK_HIKAYE = {
    "kitap_bilgileri": {
        "baslik": "Büyülü Krallığın Sırları",
        "yazar": "Masal Yazarı",
        "yayinevi": "Fantastik Yayınları",
        "basim_yili": 2024,
        "yas_grubu": "10+ yaş",
        "toplam_sayfa": 180,
        "isbn": "978-975-789-012-3"
    },
    "analiz_ozeti": {
        "profil_analizi": "Hibrit (Önerilen)",
        "final_skor": 35,
        "karar": "✔️ Düşük Risk - Fantastik Kurgu Bağlamında Güvenli",
        "bolgeler": {
            "maarif_meb": 42,
            "hibrit": 35,
            "editoryal": 22,
            "hassas_veli": 55,
            "kuruma_ozel": 38
        }
    },
    "bulgular": [
        {
            "kategori": "Okültizm & Batıl İnanç",
            "bulgu_sayisi": 5,
            "risk": 2,
            "ornekler": [
                {
                    "sayfa": 45,
                    "alinti": "Büyücü elini kaldırdı ve ışık patladı",
                    "bağlam": "Fantastik kurgu dünyasında sihir unsuru",
                    "ai_yorum": "Sihir = Fantastik yaratıcı öğe, gerçekmiş gibi yönlendirme yok",
                    "sonuç": "Fantastik Referans (Risk: 0/5)"
                },
                {
                    "sayfa": 89,
                    "alinti": "Cadının kurulu ritüelini takip etmedim",
                    "bağlam": "Hikaye içinde negatif karakter (cadi), cezalandırılıyor",
                    "ai_yorum": "Cadı negatif tasvir edilmiş, ritual öğretimi yok",
                    "sonuç": "Edebi Unsur (Risk: 1/5)"
                }
            ]
        },
        {
            "kategori": "Korku & Travma",
            "bulgu_sayisi": 3,
            "risk": 2,
            "ornekler": [
                {
                    "sayfa": 123,
                    "alinti": "Karanlık kaleyi yaklaşırken çocuk korktu",
                    "bağlam": "Fantastik kurgu kaşesi, gerçekmiş sugestiyonu yok",
                    "ai_yorum": "Fantastik korku atmosferi, çocuk hikayesi standartı",
                    "sonuç": "Kurgu Korkunun (Risk: 1/5)"
                }
            ]
        }
    ],
    "maarif_profilleri": {
        "sorgulayici": 4,
        "cesaretli": 4,
        "uretken": 5,  # Yaratıcılık teması
        "bilge": 3,
        "ahlaklı": 4,
        "merhametli": 3,
        "vatansever": 2,
        "estetik": 5,  # Hayal dünyası
        "iradeli": 4,
        "saglikli": 3
    },
    "maarif_uyum_puani": 72,
    "meb_kriterleri": {
        "anayasa": {"risk": 0, "karar": "Uyumlu"},
        "milli_guvenlik": {"risk": 0, "karar": "Temiz"},
        "esitlik": {"risk": 1, "karar": "Kontrol"},
        "milli_manevi": {"risk": 1, "karar": "Dikkat"},
        "guvenlik": {"risk": 1, "karar": "Kurgu"},
        "bilimsel": {"risk": 0, "karar": "Fantastik"},
        "reklam": {"risk": 0, "karar": "Temiz"},
        "dil": {"risk": 0, "karar": "Temiz"}
    },
    "meb_puani": 71,
    "oneriler": [
        "10+ yaş grubuna uygun, 8-9 yaş için ebeveyn rehberliğine bırak",
        "Sihir/cadı unsurları fantastik kurgu içinde tamamen ok; gerçekmiş yönlendirme yok",
        "Yaratıcılık ve estetik temaları güçlü (Üretken 5/5, Estetik 5/5)",
        "Korkulu sahneler fantastik ortamda uygun seviyede",
        "Öğretmen notu: Hayal gücünü geliştirme etkinlikleri için ideal"
    ],
    "karar_ozeti": """
Bu kitap 10+ yaş grubuna uygundur. Fantastik unsurlar (sihir, cadı, 
büyülü krallık) edebi ve kurgu bağlamında tamamen güvenli şekilde 
sunulmuştur.

✅ GÜVENLİ FANTASTIK ÖĞELERİ:
- Sihir = Yaratıcı unsur (Risk 0/5)
- Cadı = Negatif karakter, cezalandırıldı (Risk 1/5)
- Korku = Fantastik atmosfer, çocuk hikayesi (Risk 1/5)

🌟 MAARIF MODELİ PROFILLERI:
- Üretken: 5/5 (Yaratıcı kurgu)
- Estetik: 5/5 (Hayal dünyası)
- Cesaretli: 4/5 (Kahramanın zorlukları aşması)

📚 OKUL UYGUNLUĞU: % 100
Kütüphane, sınıf okumaları, bireysel okuma için ideal.

⚠️ UYARI: Sensitif çocuklara ilk olarak ebeveyn rehberliğiyle 
(9 yaş da mümkün) başlamak tavsiye edilir.

✅ KARAR: TÜMLÜKLÜ UYGUN - KÜTÜPHANEYE ALIMI ÖNERİLİR
"""
}

# ============================================================================
# KARŞILAŞTIRMA TABLOSU
# ============================================================================

KARSILASTIRMA = """
┌─────────────────────┬──────────┬────────┬────────┬──────────────────────┐
│ Kitap Türü          │ Yaş Gr.  │ Skor   │ Karar  │ En İyi Profil        │
├─────────────────────┼──────────┼────────┼────────┼──────────────────────┤
│ Çocuk Hikayesi      │ 8+       │ 32/100 │ ✔️     │ Hibrit (32)          │
│                     │          │        │ Uygun  │ Editoryal (18)       │
│                     │          │        │        │                      │
│ Gençlik Romanı      │ 14+      │ 45/100 │ ⚠️     │ Editoryal (28) ✅    │
│                     │          │        │ Dikkat │ Hibrit (45)          │
│                     │          │        │        │ Hassas Veli (75) ⚠️  │
│                     │          │        │        │                      │
│ Tarihî Roman        │ 12+      │ 38/100 │ ✔️     │ Maarif/MEB (38) ✅   │
│                     │          │        │ Uygun  │ Hibrit (28)          │
│                     │          │        │        │ Editoryal (15) ✅    │
│                     │          │        │        │                      │
│ Fantastik Hikaye    │ 10+      │ 35/100 │ ✔️     │ Hibrit (35) ✅       │
│                     │          │        │ Uygun  │ Editoryal (22)       │
│                     │          │        │        │                      │
└─────────────────────┴──────────┴────────┴────────┴──────────────────────┘

BULGULAR KARŞILAŞTIRMASI
─────────────────────────

┌─────────────┬───────────────────────────────────────────────────────────┐
│ Kategori    │ Çocuk | Gençlik | Tarihî | Fantastik                     │
├─────────────┼───────────────────────────────────────────────────────────┤
│ Şiddet      │ ✓ 0   │ ✗ 2     │ ★ 4*  │ ✓ 0                           │
│ Cinsellik   │ 0     │ ✓ 3     │ 0     │ 0                             │
│ Zararlı Alı │ 0     │ ✓ 2     │ 0     │ 0                             │
│ Kaba Dil    │ ✓ 1   │ 0       │ 0     │ 0                             │
│ Okültizm    │ 0     │ 0       │ 0     │ ✓ 2                           │
│ Korku       │ ✓ 2   │ 0       │ ✓ 1   │ ✓ 2                           │
│ Olumsuz Dav │ 0     │ ✓ 4     │ 0     │ 0                             │
└─────────────┴───────────────────────────────────────────────────────────┘

NOT: ★ = Tarihî bağlam, risk azaltma uygulanmış

MAARIF PROFİLLERİ KARŞILAŞTIRMASI
──────────────────────────────────

Profil        │ Çocuk H. │ Gençlik R. │ Tarihî R. │ Fantastik H.
──────────────┼──────────┼────────────┼───────────┼──────────────
Sorgulayıcı   │ 5/5 ✅   │ 3/5        │ 4/5 ✅    │ 4/5 ✅
Cesaretli     │ 4/5      │ 2/5        │ 5/5 ✅    │ 4/5 ✅
Üretken       │ 3/5      │ 3/5        │ 3/5       │ 5/5 ✅
Bilge         │ 2/5      │ 2/5        │ 4/5 ✅    │ 3/5
Ahlaklı       │ 4/5 ✅   │ 2/5        │ 5/5 ✅    │ 4/5 ✅
Merhametli    │ 4/5 ✅   │ 3/5        │ 3/5       │ 3/5
Vatansever    │ 3/5      │ 1/5        │ 5/5 ✅    │ 2/5
Estetik       │ 4/5 ✅   │ 4/5 ✅     │ 3/5       │ 5/5 ✅
İradeli       │ 5/5 ✅   │ 2/5        │ 5/5 ✅    │ 4/5 ✅
Sağlıklı      │ 3/5      │ 1/5        │ 2/5       │ 3/5
───────────────┴──────────┴────────────┴───────────┴──────────────
UYUM PUANI    │ 77/100   │ 43/100     │ 84/100    │ 72/100
"""

if __name__ == "__main__":
    print("=" * 80)
    print("KİTAP BAZLI ÖRNEK ANALİZ RAPORLARI")
    print("=" * 80)
    
    print("\n" + "=" * 80)
    print("ÖRNEK 1: ÇOCUK HİKAYESİ / 8+ YAŞ")
    print("=" * 80)
    print(json.dumps(COCUK_HIKAYESI, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("ÖRNEK 2: GENÇLIK ROMANI / 14+ YAŞ")
    print("=" * 80)
    print(json.dumps(GENCLIK_ROMANI, indent=2, ensure_ascii=False)[:500])
    print("... (kısaltılmış)")
    
    print("\n" + "=" * 80)
    print("ÖRNEK 3: TARİHÎ ROMAN / 12+ YAŞ")
    print("=" * 80)
    print(json.dumps(TARIFI_ROMAN, indent=2, ensure_ascii=False)[:500])
    print("... (kısaltılmış)")
    
    print("\n" + "=" * 80)
    print("ÖRNEK 4: FANTASTIK HİKAYE / 10+ YAŞ")
    print("=" * 80)
    print(json.dumps(FANTASTIK_HIKAYE, indent=2, ensure_ascii=False)[:500])
    print("... (kısaltılmış)")
    
    print("\n" + KARSILASTIRMA)
