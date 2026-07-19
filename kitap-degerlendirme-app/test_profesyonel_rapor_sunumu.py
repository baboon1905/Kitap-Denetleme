import io
import os

from PyPDF2 import PdfReader

from theme_gain_analysis import analyze_theme_gain, build_pdf_report, build_teacher_report_payload, build_word_report, generate_teacher_report_pdf, prepare_theme_report_payload, _evidence_quality, _normalize_report_score_inflation, _reliability_level, _teacher_specificity_assessment


SUMMARY = """Giriş:
Anlatıcı yıllar sonra çocukluğunun geçtiği mahalleye döner. Eski sokakları, yağmur altındaki evleri ve aile anılarını hatırlar.

Gelişme:
Eski mahalle kültürü komşular, esnaf ve okul çevresi üzerinden görünür olur. Çiçek Abla, Tuna Abi ve Sibel Öğretmen mahalle sıcaklığını taşıyan kişilerdir.

Temel Çatışma:
Yeni şehirleşme ile eski mahalle düzeni karşı karşıya gelir. Anlatıcı değişen sokaklarda geçmişe özlem duyar.

Karakter İlişkileri:
Aile ve komşuluk ilişkileri anlatıcının çocukluk anıları içinde kurulur. Anne, baba, Suna ve komşular ortak geçmişi görünür kılar.

Genel Sonuç:
Kitap, şehirleşme karşısında kaybolan mahalle kültürünü ve geçmişe özlemi anlatır."""


def sample_payload():
    evidences = [
        {"sayfa": index, "alinti": f"Anlatıcı mahallede ailesi ve komşularıyla eski günleri hatırlayan güçlü sahne {index}.", "baglam_gucu": 3, "kanit_turu": "olay_sahnesi"}
        for index in range(1, 6)
    ]
    return {
        "kitap_adi": "Gökyüzünü Kaybeden Şehir",
        "yazar": "Test",
        "hedef_yas_grubu": "10-12 yaş",
        "kitap_ozeti": SUMMARY,
        "ozet_guven_skoru": 0.9,
        "ozet_somutluk_skoru": 0.8,
        "ozet_uzunlugu": len(SUMMARY.split()),
        "tema_analizi": [
            {
                "ad": "geçmişe özlem",
                "tema_gucu": 82,
                "guven_skoru": 0.82,
                "kanit_sayisi": 5,
                "farkli_sayfa_sayisi": 5,
                "baglam_gucu": 3,
                "kanitlar": evidences,
            }
        ],
        "deger_analizi": [
            {
                "ad": "çevre duyarlılığı",
                "tema_gucu": 38,
                "guven_skoru": 0.38,
                "kanit_sayisi": 1,
                "farkli_sayfa_sayisi": 1,
                "baglam_gucu": 1,
                "kanitlar": [{"sayfa": 2, "alinti": "Çevre sözcüğü yalnızca evin çevresi anlamında geçer.", "baglam_gucu": 1}],
            }
        ],
        "kazanim_analizi": [
            {
                "ad": "karakter analizi yapma",
                "tur": "kazanım",
                "tema_gucu": 76,
                "guven_skoru": 0.76,
                "kanit_sayisi": 3,
                "farkli_sayfa_sayisi": 3,
                "baglam_gucu": 3,
                "kanitlar": evidences[:3],
            }
        ],
        "ana_karakterler": [
            {"karakter_adi": "Anlatıcı", "rolu": "ana", "anlatici_mi": True, "guven_skoru": 0.9, "karakter_iliskileri": "İlişki bilgisi sınırlı."},
            {"karakter_adi": "Sibel Öğretmen", "rolu": "yan", "guven_skoru": 0.7, "karakter_iliskileri": "İlişki bilgisi sınırlı."},
        ],
        "zayif_eslesmeler": [
            {"ad": "çevre duyarlılığı", "tema_gucu": 38, "kanit_sayisi": 1, "baglam_gucu": 1}
        ],
        "rapor_build_id": "test-build-visible-only-in-dev",
    }


payload = sample_payload()
word_html = build_word_report(payload).getvalue().decode("utf-8")

assert "Yönetici Özeti" in word_html
assert "Gökyüzünü Kaybeden Şehir" in word_html
assert "Yeterli güvenle belirlenemedi" in word_html, word_html
assert "manuel inceleme" in word_html.casefold(), word_html
assert "Yeterli tema kanıtı bulunamadı" in word_html, word_html
assert "<h3>geçmişe özlem | Puan" not in word_html, word_html
assert "Zayıf Eşleşmeler" in word_html, word_html
assert "Hedef yas/sinif: 10-12 yaş" in word_html, word_html

assert word_html.count("Anlatıcı mahallede ailesi ve komşularıyla") <= 3, word_html
assert "Karakter İşlevi" in word_html, word_html
assert "<th>İlişki</th>" not in word_html, word_html
assert "<th>Başlık</th><th>Güç</th><th>Sebep</th>" in word_html, word_html
assert "<h3>çevre duyarlılığı | Puan" not in word_html, word_html
assert "Kanıt Kalitesi: Yüksek" not in word_html, word_html
for score_label in ["Tema Kalitesi", "Kanıt Kalitesi", "Karakter Derinliği", "Pedagojik Kullanılabilirlik", "Veri Güvenilirliği", "Genel Rapor Skoru"]:
    assert score_label in word_html, word_html
assert "Rapor Güven Skoru" in word_html, word_html
assert "Pedagojik Değerlendirme" in word_html, word_html
assert "Kalite Denetimi" in word_html, word_html

old_app_env = os.environ.get("APP_ENV")
old_flask_env = os.environ.get("FLASK_ENV")
os.environ["APP_ENV"] = "production"
os.environ.pop("FLASK_ENV", None)
try:
    pdf_bytes = build_pdf_report(payload).getvalue()
    production_word_html = build_word_report(payload).getvalue().decode("utf-8")
finally:
    if old_app_env is None:
        os.environ.pop("APP_ENV", None)
    else:
        os.environ["APP_ENV"] = old_app_env
    if old_flask_env is None:
        os.environ.pop("FLASK_ENV", None)
    else:
        os.environ["FLASK_ENV"] = old_flask_env

pdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(pdf_bytes)).pages)
assert "Rapor Build ID" not in pdf_text, pdf_text
assert "test-build-visible-only-in-dev" not in pdf_text, pdf_text
for hidden_text in ["Özet Güven Skoru", "Dinamik Güven", "Tekrar Yoğunluğu", "Ana Tema Güven"]:
    assert hidden_text not in pdf_text, pdf_text
    assert hidden_text not in production_word_html, production_word_html

teacher_payload = build_teacher_report_payload(payload)
assert len(teacher_payload["kisa_ogretmen_ozeti"].split()) >= 100, teacher_payload["kisa_ogretmen_ozeti"]
assert "Çiçek Abla, Tuna Abi ve Sibel Öğretmen" not in teacher_payload["kisa_ogretmen_ozeti"]
assert len(teacher_payload["kullanilabilecek_dersler"]) >= 2, teacher_payload
assert len(teacher_payload["kitaba_ozel_etkinlikler"]) == 5, teacher_payload
assert len(teacher_payload["ogretmen_notlari"]) == 4, teacher_payload
for recommendation_context in ["şehirleşme", "mahalle kültürü", "aidiyet", "geçmiş ile günümüz"]:
    assert recommendation_context in teacher_payload["neden_oneriyoruz"], teacher_payload["neden_oneriyoruz"]
assert teacher_payload["kitaba_ozguluk"]["skor"] >= 70, teacher_payload["kitaba_ozguluk"]
assert not teacher_payload["kitaba_ozguluk"]["uyari"], teacher_payload["kitaba_ozguluk"]
for expected_question_context in ["Mahalle kültürünün değişmesi", "Bülent'in çocukluk mahallesine", "eski mahalle yaşamı"]:
    assert any(expected_question_context in question for question in teacher_payload["tartisma_sorulari"]), teacher_payload["tartisma_sorulari"]
generic_specificity = _teacher_specificity_assessment(
    payload,
    ["Ana karakter nasıl davranmıştır?", "Siz olsaydınız ne yapardınız?", "Kitabın ana fikri nedir?"],
    ["Bir poster hazırlayın.", "Grup çalışması yapın.", "Kısa bir yazı yazın."],
)
assert generic_specificity["genel_icerik_orani"] > 0.70, generic_specificity
assert generic_specificity["uyari"], generic_specificity
teacher_pdf_bytes = generate_teacher_report_pdf(payload).getvalue()
teacher_text = "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(teacher_pdf_bytes)).pages)
for forbidden_text in [
    "Rapor Build ID",
    "Build ID",
    "Ana Tema Gücü",
    "Ana Tema Güven",
    "Özet Güven Skoru",
    "Özet Somutluk Skoru",
    "Özet Uzunluğu",
    "Özet Kanıtlarının Yayıldığı Sayfa Sayısı",
    "Kalite Kontrol",
    "Puan",
    "Güven",
    "Tema Gücü",
    "Kanıt",
    "Kanıt Sayısı",
    "Farklı Sayfa",
    "Farklı Sayfa Sayısı",
    "Bağlam Gücü",
    "Tekrar Yoğunluğu",
    "Kanıt Kalitesi",
    "Dinamik Güven Skoru",
    "Dinamik Güven",
    "Analiz Guvenilirlik Ozeti",
    "Kalite Denetimi",
    "Sayfa 1",
    "Tema ve Kazanım Analizi",
]:
    assert forbidden_text not in teacher_text, (forbidden_text, teacher_text)
for expected_text in [
    "Öğretmen Kitap Rehberi",
    "Kitap Bilgileri",
    "Hedef yaş/sınıf bilgisi",
    "10-12 yaş",
    "Öne Çıkan Temalar",
    "geçmişe özlem",
    "Öğrenci Kazanımları",
    "karakter analizi yapma",
    "Hangi Derslerde Kullanılabilir?",
    "Türkçe",
    "Sosyal Bilgiler",
    "Kitaba Özel Etkinlik Önerileri",
    "Mahalle hafızası röportajı",
    "Sınıf İçi Tartışma Soruları",
    "Desteklenen beceriler:",
    "Uygun etkinlik türleri:",
    "Yaş/sınıf düzeyi:",
    "Bu Kitabı Neden Öneriyoruz?",
    "geçmiş ile günümüz yaşam biçimlerini",
]:
    assert expected_text in teacher_text, (expected_text, teacher_text)


def inflated_payload():
    payload = sample_payload()
    strong_evidence = [
        {
            "sayfa": index,
            "alinti": f"Bülent çocukluk mahallesinde şehirleşme, geçmişe özlem, aile ilişkileri, komşuluk, mahalle kültürü, değişim ve aidiyet duygusunu gösteren bağımsız olay sahnesi {index}.",
            "baglam_gucu": 5,
            "kanit_turu": "olay_sahnesi",
        }
        for index in range(1, 7)
    ]
    theme_names = ["şehirleşme", "geçmişe özlem", "aile ilişkileri", "komşuluk", "mahalle kültürü", "değişim", "aidiyet"]
    gain_names = ["olay örgüsünü yorumlama", "karakter analizi yapma", "tema belirleme", "çıkarım yapma", "metin karşılaştırma", "eleştirel düşünme", "okuduğunu anlama"]
    payload["tema_analizi"] = [
        {"ad": name, "tema_gucu": 99 - index, "guven_skoru": 0.98, "kanit_sayisi": 6, "farkli_sayfa_sayisi": 6, "baglam_gucu": 5, "kanitlar": strong_evidence}
        for index, name in enumerate(theme_names)
    ]
    payload["kazanim_analizi"] = [
        {"ad": name, "tema_gucu": 99 - index, "guven_skoru": 0.98, "kanit_sayisi": 6, "farkli_sayfa_sayisi": 6, "baglam_gucu": 5, "kanitlar": strong_evidence}
        for index, name in enumerate(gain_names)
    ]
    payload["ana_karakterler"] = [
        {"karakter_adi": "Bülent", "rolu": "ana", "anlatici_mi": True, "guven_skoru": 0.91, "karakter_iliskileri": "İlişki bilgisi sınırlı."},
        {"karakter_adi": "Çiçek Abla", "rolu": "yan", "guven_skoru": 0.90, "karakter_iliskileri": "İlişki bilgisi sınırlı."},
    ]
    return payload


inflated = _normalize_report_score_inflation(inflated_payload())
theme_scores = [item["tema_gucu"] for item in inflated["tema_analizi"]]
gain_scores = [item["tema_gucu"] for item in inflated["kazanim_analizi"]]
assert theme_scores[0] <= 100, theme_scores
assert theme_scores[1] <= 95, theme_scores
assert theme_scores[2] <= 90, theme_scores
assert max(theme_scores[3:]) <= 85, theme_scores
assert sum(score >= 90 for score in gain_scores) <= 3, gain_scores
if len(gain_scores) > 3:
    assert max(gain_scores[3:]) <= 84, gain_scores
assert _evidence_quality(inflated["tema_analizi"][0]) == "Yüksek", inflated["tema_analizi"][0]

cognitive_payload = sample_payload()
cognitive_payload["kazanim_analizi"] = [
    {
        "ad": "okuduğunu anlama",
        "tema_gucu": 98,
        "guven_skoru": 0.98,
        "kanit_sayisi": 5,
        "farkli_sayfa_sayisi": 5,
        "baglam_gucu": 5,
        "kanitlar": [
            {
                "sayfa": index,
                "alinti": f"Bülent olaydan sonra kısa bir değerlendirme yaptı {index}.",
                "baglam_gucu": 5,
                "kanit_turu": "olay_sahnesi",
                "kanit_agirligi": 1.0,
            }
            for index in range(1, 6)
        ],
    }
]
cognitive_prepared = prepare_theme_report_payload(cognitive_payload)
assert cognitive_prepared["kazanim_analizi"][0]["tema_gucu"] <= 89, cognitive_prepared["kazanim_analizi"]
assert cognitive_prepared["kazanim_analizi"][0].get("ust_duzey_kazanim_tavan_kurali") is True, cognitive_prepared["kazanim_analizi"]

assert _reliability_level(95) == "Cok Guvenilir"
assert _reliability_level(85) == "Guvenilir"
assert _reliability_level(75) == "Dikkatli Kullan"
assert _reliability_level(69) == "Manuel Inceleme"

missing_target_payload = sample_payload()
missing_target_payload.pop("hedef_yas_grubu", None)
missing_target_html = build_word_report(missing_target_payload).getvalue().decode("utf-8")
assert "Hedef yas/sinif bilgisi: belirtilmemis." in missing_target_html, missing_target_html
assert "Hedef yas/sinif verisi belirtilmemis" in missing_target_html, missing_target_html
assert "Yonetici ozeti hedef yas/sinif satirini icermiyor." not in missing_target_html, missing_target_html
assert "Yonetici ozeti hedef yas/sinif bilgisini icermiyor." not in missing_target_html, missing_target_html

abstract_payload = sample_payload()
abstract_payload["tema_analizi"] = [
    {
        "ad": "empati",
        "tema_gucu": 96,
        "guven_skoru": 0.96,
        "kanit_sayisi": 5,
        "farkli_sayfa_sayisi": 5,
        "baglam_gucu": 5,
        "kanitlar": [
            {
                "sayfa": index,
                "alinti": f"Bülent, Suna'nın üzüldüğünü fark etti ve onu anladı {index}.",
                "baglam_gucu": 5,
                "kanit_turu": "olay_sahnesi",
                "anahtarlar": ["empati", "halini", "üzüldü"],
            }
            for index in range(1, 6)
        ],
    }
]
abstract_prepared = prepare_theme_report_payload(abstract_payload)
assert abstract_prepared["tema_analizi"][0]["tema_gucu"] <= 89, abstract_prepared["tema_analizi"]

false_theme_payload = sample_payload()
false_theme_payload["tema_analizi"] = [
    {
        "ad": "empati",
        "tema_gucu": 96,
        "guven_skoru": 0.96,
        "kanit_sayisi": 1,
        "farkli_sayfa_sayisi": 1,
        "baglam_gucu": 5,
        "kanitlar": [
            {
                "sayfa": 1,
                "alinti": "Öğretmenimize sormayı düşündük fakat sonra vazgeçtik.",
                "baglam_gucu": 5,
                "kanit_turu": "olay_sahnesi",
                "anahtarlar": ["düşündük"],
            }
        ],
    }
]
false_prepared = prepare_theme_report_payload(false_theme_payload)
assert not false_prepared.get("tema_analizi") or false_prepared["tema_analizi"][0]["tema_gucu"] < 50, false_prepared["tema_analizi"]

overlap_payload = sample_payload()
shared_evidence = [
    {
        "sayfa": index,
        "alinti": f"Bülent mahallede ailesiyle değişimi değerlendirip eski komşuluk ilişkilerini karşılaştıran güçlü olay sahnesi {index}.",
        "baglam_gucu": 5,
        "kanit_turu": "olay_sahnesi",
    }
    for index in range(1, 6)
]
overlap_payload["tema_analizi"] = [
    {"ad": "şehirleşme", "tema_gucu": 94, "guven_skoru": 0.94, "kanit_sayisi": 5, "farkli_sayfa_sayisi": 5, "baglam_gucu": 5, "kanitlar": shared_evidence}
]
overlap_payload["kazanim_analizi"] = [
    {"ad": "olay örgüsünü yorumlama", "tema_gucu": 93, "guven_skoru": 0.93, "kanit_sayisi": 5, "farkli_sayfa_sayisi": 5, "baglam_gucu": 5, "kanitlar": shared_evidence}
]
overlap_prepared = prepare_theme_report_payload(overlap_payload)
assert overlap_prepared.get("kazanim_analizi"), overlap_prepared.get("kazanim_analizi")
assert overlap_prepared["kazanim_analizi"][0]["tema_gucu"] <= 89, overlap_prepared.get("kazanim_analizi")
assert overlap_prepared["kazanim_analizi"][0].get("ust_duzey_kazanim_tavan_kurali") is True, overlap_prepared.get("kazanim_analizi")

assert "Analiz Guvenilirlik Ozeti" in word_html, word_html
for reliability_label in ["Ozet Kalitesi", "Karakter Kalitesi", "Tema Kalitesi", "Kazanim Kalitesi", "Deger Kalitesi", "Maarif Kalitesi"]:
    assert reliability_label in word_html, word_html
assert "Kanit Guvenilirlik Skoru" in word_html, word_html
assert "Belirgin ili" not in word_html, word_html
assert "liÅŸki bilgisi sÄ±nÄ±rlÄ±" not in word_html, word_html

fake_match_text = """
--- SAYFA 1 ---
Ã–ÄŸretmenimize sormayÄ± dÃ¼ÅŸÃ¼ndÃ¼k fakat sonra vazgeÃ§tik.
--- SAYFA 2 ---
Birileri taÅŸÄ±ndÄ± oraya.
--- SAYFA 3 ---
Orada bir Ã§aycÄ±nÄ±n olduÄŸunu fark ettim.
"""

fake_result = analyze_theme_gain(fake_match_text, {"kitap_adi": "Sahte EÅŸleÅŸme Testi", "yazar": "Test"})
fake_gains = {item.get("ad") for item in fake_result.get("kazanim_analizi", [])}
assert "empati kurma" not in fake_gains, fake_result.get("kazanim_analizi")
assert "karakter analizi yapma" not in fake_gains, fake_result.get("kazanim_analizi")
assert "okuduÄŸunu anlama" not in fake_gains, fake_result.get("kazanim_analizi")
