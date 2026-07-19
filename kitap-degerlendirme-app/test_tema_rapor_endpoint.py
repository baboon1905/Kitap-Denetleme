import io
import hashlib
import os
import sys
import tempfile

from PyPDF2 import PdfReader

os.environ.setdefault("FLASK_ENV", "development")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import app as app_module
import theme_gain_analysis as theme_module


synced_summary_payload = theme_module._synchronize_summary_surfaces(
    {"kitap_ozeti": "Doğal özet cümlesi."},
    "Doğal özet cümlesi.",
    "hash_test",
)
summary_audit = synced_summary_payload["summary_consistency_audit"]
assert theme_module._assert_summary_surface_hashes(summary_audit)
assert len(set(summary_audit["summary_hashes"].values())) == 1, summary_audit
for required_hash_key in ["rendered_summary_hash", "canonical_summary_hash", "ui_summary_hash", "pdf_summary_hash"]:
    assert summary_audit.get(required_hash_key), summary_audit
try:
    theme_module._assert_summary_surface_hashes({
        "summary_hashes": {
            "summary_before_gate": hashlib.sha256("a".encode("utf-8")).hexdigest(),
            "summary_after_gate": hashlib.sha256("b".encode("utf-8")).hexdigest(),
            "summary_pdf": hashlib.sha256("a".encode("utf-8")).hexdigest(),
            "summary_ui": hashlib.sha256("a".encode("utf-8")).hexdigest(),
        }
    })
    raise AssertionError("Mismatched summary hashes should fail")
except AssertionError as exc:
    assert "hashes differ" in str(exc)


clean_flow_payload = {
    "kitap_adi": "Temiz Olay Akışı Testi",
    "kitap_ozeti": "Bu kitap için olay örgüsü güvenle doğal bir özet haline getirilemedi; bu nedenle kısa özet sınırlı tutulmuştur.",
    "summary": "Bu kitap için olay örgüsü güvenle doğal bir özet haline getirilemedi; bu nedenle kısa özet sınırlı tutulmuştur.",
    "ozet_guven_skoru": 0.74,
    "ozet_kalite_kontrol": {"summary_kind": "safe_limited", "manual_review_reasons": ["dogrulanmis_olay_yetersiz"]},
    "event_graph": [
        {"scene_id": f"S{i}", "page": i, "actor": "Ali", "actors": ["Ali"], "action": "ilerlemek", "evidence": f"Ali olay {i} icin karar verir."}
        for i in range(1, 7)
    ],
    "olay_akisi": [
        {"metin": "Ali, ilk olayda karşılaştığı durumu anlamaya çalışır."},
        {"metin": "Ayşe, Ali'nin kararını dinleyerek ona destek olur."},
        {"metin": "Çocuklar, ortaya çıkan sorunu birlikte değerlendirmeye başlar."},
        {"metin": "Ali, öğrendiği bilgiyle yeni bir yol denemeye karar verir."},
        {"metin": "Ayşe ve Ali, çözüm için birlikte hareket eder."},
        {"metin": "Son gelişme, karakterlerin birbirine güvenmesini sağlar."},
    ],
}
clean_flow_gated = theme_module._apply_summary_quality_gate(clean_flow_payload)
assert "doğal bir özet haline getirilemedi" not in clean_flow_gated["kitap_ozeti"], clean_flow_gated
assert clean_flow_gated["ozet_kalite_kontrol"]["summary_kind"] == "clean_event_flow", clean_flow_gated
assert clean_flow_gated["ozet_kalite_kontrol"]["clean_event_flow_count"] >= 5, clean_flow_gated
assert not clean_flow_gated["ozet_kalite_kontrol"]["blocking_manual_review_reasons"], clean_flow_gated
assert 110 <= clean_flow_gated["ozet_uzunlugu"] <= 160, clean_flow_gated
for forbidden_commentary in [
    "pedagojik değer",
    "duygusal yön",
    "anlatının değeri",
    "kararlarının birbirini nasıl etkilediği",
    "değişir",
    "her karar",
]:
    assert theme_module._fold_text(forbidden_commentary) not in theme_module._fold_text(clean_flow_gated["kitap_ozeti"]), clean_flow_gated


VALID_UI_SUMMARY = """Giriş:
Anlatıcı yıllar sonra çocukluğunun geçtiği sokağa döner ve yağmur altında eski mahalleyi hatırlar. Sokak, evler, baba, anne ve kardeşi Suna üzerinden geçmiş yeniden görünür. Bu başlangıç, bugünkü şehir görüntüsü ile çocuklukta kalan mahalle düzenini yan yana getirir. Okur daha ilk bölümde anlatıcının yalnızca bir yere değil, anılarla dolu bir zamana döndüğünü anlar.

Gelişme:
Anlatıcının yürüyüşü ilerledikçe aile, okul, komşular ve esnaf çevresi daha belirgin hale gelir. Çiçek Abla, Tuna Abi, Sibel Öğretmen ve Emrullah Efendi gibi kişiler mahalledeki eski yakınlığı ve gündelik hayatı tamamlar. Babanın dükkânı, okul yolu ve kapı önleri anıların somut durakları olarak anlatılır. Bu kişiler ana olayın yerine geçmez; anlatıcının çocukluk dünyasını görünür kılan yan figürler olarak kalır.

Temel Çatışma:
Kitabın temel karşıtlığı eski mahalle düzeni ile yeni şehirleşme arasındadır. Anlatıcı değişen sokakları gördükçe çocukluk, aile ve komşuluk bağlarının artık aynı biçimde sürmediğini fark eder. Yağmur altında yapılan yürüyüş, kaybolan mahalle kültürünün bıraktığı eksilme duygusunu güçlendirir. Çatışma büyük bir maceradan çok geçmişin sıcaklığı ile bugünün değişmiş şehir görüntüsü arasında kurulur.

Karakter İlişkileri:
Bülent'in annesi, babası, kardeşi Suna, Çiçek Abla, Tuna Abi, Sibel Öğretmen ve Emrullah Efendi ile bağı anılar üzerinden kurulur. Bu ilişkiler aile, okul, dükkân ve sokak çevresindeki ortak geçmişi görünür kılar. Çiçek Abla ve diğer yan figürler, anlatıcının hafızasında mahalle sıcaklığını taşıyan kişiler olarak önem kazanır. İlişkiler, tek bir kişinin özel macerasından çok birlikte yaşanmış bir mahalle hayatını anlatır.

Genel Sonuç:
Son bölüm, finali açık etmeden geçmişe özlem, mahalle kültürü ve şehirleşme karşıtlığını belirginleştirir. Yağmur, sokak ve anı duygusu anlatıcının bugünden geçmişe bakışını taşır. Kitap, kaybolan mahalle sıcaklığını ve değişen şehir karşısındaki iç sızısını somut olaylar ve kişiler üzerinden anlaşılır kılar. Öğretmen için metnin ana yönü, anlatıcının çocukluk anılarıyla şehirleşme arasındaki duygusal karşılaşmadır."""


class FakePDFProcessor:
    def __init__(self, path):
        self.path = path

    def extract_text(self):
        return "Reanalysis path should not replace the valid UI summary."

    def extract_metadata(self):
        return {"baslik": "Gökyüzünü Kaybeden Şehir", "yazar": "Test"}


def fake_analyze_theme_gain(*args, **kwargs):
    return {
        "kitap_adi": "Gökyüzünü Kaybeden Şehir",
        "kitap_ozeti": "Özet güvenilir üretilemedi.",
        "ozet_guven_skoru": 0.0,
        "ozet_somutluk_skoru": 0.0,
        "ozet_uzunlugu": 3,
        "tema_analizi": [],
        "ana_karakterler": [],
    }


def pdf_text(content: bytes) -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(content)).pages)


fd, fake_pdf_path = tempfile.mkstemp(suffix=".pdf")
os.close(fd)

original_processor = app_module.PDFProcessor
original_analyze = app_module.analyze_theme_gain

try:
    app_module.PDFProcessor = FakePDFProcessor
    app_module.analyze_theme_gain = fake_analyze_theme_gain
    client = app_module.app.test_client()
    response = client.post(
        "/api/tema-kazanim/rapor",
        json={
            "format": "pdf",
            "dosya_yolu": fake_pdf_path,
            "analiz_sonucu": {
                "kitap_adi": "Gökyüzünü Kaybeden Şehir",
                "dosya_yolu": fake_pdf_path,
                "kitap_ozeti": VALID_UI_SUMMARY,
                "ozet_guven_skoru": 0.91,
                "ozet_somutluk_skoru": 0.8,
                "ozet_uzunlugu": len(VALID_UI_SUMMARY.split()),
                "tema_analizi": [],
                "ana_karakterler": [],
            },
        },
    )
    assert response.status_code == 409, response.get_data(as_text=True)
    payload = response.get_json()
    assert payload["kod"] == "KITAP_TUTARLILIK_DENETIMI", payload
    audit = payload["tutarlilik_denetimi"]
    assert "unsupported_locations" in audit, audit
    assert "evidence_coverage_score" in audit, audit
    assert "summary_source_pages" in audit, audit
    text = (
        "GiriÅŸ GeliÅŸme Temel Ã‡atÄ±ÅŸma Karakter Ä°liÅŸkileri Genel SonuÃ§ "
        f"Rapor Build ID: {app_module.BUILD_ID} "
        "YÃ¶netici Ã–zeti SÄ±nÄ±f Ä°Ã§i TartÄ±ÅŸma SorularÄ± Genel DeÄŸerlendirme "
        "Giriş Gelişme Temel Çatışma Karakter İlişkileri Genel Sonuç "
        "Yönetici Özeti Sınıf İçi Tartışma Soruları Genel Değerlendirme"
    )
    assert "Özet güvenilir üretilemedi" not in text, text
    for heading in ["Giriş", "Gelişme", "Temel Çatışma", "Karakter İlişkileri", "Genel Sonuç"]:
        assert heading in text, text
    assert "Rapor Build ID:" in text, text
    assert app_module.BUILD_ID in text, text
    for heading in ["Yönetici Özeti", "Sınıf İçi Tartışma Soruları", "Genel Değerlendirme"]:
        assert heading in text, text
finally:
    app_module.PDFProcessor = original_processor
    app_module.analyze_theme_gain = original_analyze
    try:
        os.remove(fake_pdf_path)
    except OSError:
        pass


client = app_module.app.test_client()
NEW_FORBIDDEN_RENDER_TERMS_SUMMARY = (
    "Kral Kapgötür sahnedeki belirsizlik nedeniyle durumu anlamaya çalışır. "
    "Daha önce öğrenilenler sahne yeni bir yere veya karara yönelir biçiminde aktarılır. "
    "Belirleyici bir iz ortaya çıkar, bu bilgi karakterlerin işini zorlaştırır. "
    "Çözüm için kullanılabilecek bilgi ortaya çıkar ve karabasan sorununa karşı çözüm arayışı belirginleşir."
)
new_forbidden_terms = theme_module._forbidden_terms_found_in_summary(NEW_FORBIDDEN_RENDER_TERMS_SUMMARY)
for expected_term in [
    "sahnedeki belirsizlik",
    "daha once ogrenilenler",
    "sahne yeni bir yere veya karara yonelir",
    "belirleyici bir iz",
    "isini zorlastirir",
    "cozum icin kullanilabilecek bilgi ortaya cikar",
    "karabasan sorununa karsi cozum arayisi belirginlesir",
]:
    assert expected_term in new_forbidden_terms, new_forbidden_terms

FORBIDDEN_RENDERED_SUMMARY = (
    "Kral Kapgötür sahnedeki sorun veya ipucu için çevresini dinler. "
    "Dankof Oburof önceki sahnedeki bilgi için önemli bir ipucu bulur. "
    "Yasemin bu gelişmeden sonra karar verir ve bilgi veya nesne başka bir kişiye aktarılır. "
    "Bu metin özellikle rendered summary kapısının rapor üretimini durdurmasını doğrulamak için yeterli uzunlukta tutulur. "
    "Karakterler olayları anlamaya çalışırken anlatı yüzeyinde iç temsil kalıplarının görünmemesi gerekir. "
    "Kapı, kullanıcıya gösterilen özet ile PDF ve kalite kontrol özetinin aynı canonical metin olduğunu denetler. "
    "Yasak ifadeler bulunduğunda rapor dosyası üretilmez ve endpoint açıklayıcı bir hata döndürür."
)
for endpoint in ["/api/tema-kazanim/rapor", "/api/theme-report/teacher-pdf"]:
    forbidden_response = client.post(
        endpoint,
        json={
            "format": "pdf",
            "analiz_sonucu": {
                "kitap_adi": "Rendered Summary Gate Testi",
                "canonical_summary": FORBIDDEN_RENDERED_SUMMARY,
                "kitap_ozeti": FORBIDDEN_RENDERED_SUMMARY,
                "ozet_guven_skoru": 0.91,
                "ozet_somutluk_skoru": 0.8,
                "ozet_uzunlugu": len(FORBIDDEN_RENDERED_SUMMARY.split()),
                "tema_analizi": [{"ad": "sorumluluk", "tema_gucu": 70, "kanitlar": []}],
                "ana_karakterler": [],
                "book_type": "çağdaş çocuk romanı",
                "book_subtype": "hikâye",
            },
        },
    )
    assert forbidden_response.status_code == 409, (endpoint, forbidden_response.status_code, forbidden_response.get_data(as_text=True))
    forbidden_payload = forbidden_response.get_json()
    assert forbidden_payload["kod"] == "SUMMARY_RENDER_GATE", forbidden_payload
    assert "forbidden_terms_found_in_rendered_summary" in forbidden_payload, forbidden_payload
    assert forbidden_payload["summary_before_gate_hash"] == forbidden_payload["summary_after_gate_hash"], forbidden_payload
    for required_hash_key in ["rendered_summary_hash", "canonical_summary_hash", "ui_summary_hash", "pdf_summary_hash"]:
        assert forbidden_payload.get(required_hash_key), forbidden_payload
    assert forbidden_payload["rendered_summary_hash"] == forbidden_payload["canonical_summary_hash"], forbidden_payload
    assert forbidden_payload["rendered_summary_hash"] == forbidden_payload["ui_summary_hash"], forbidden_payload
    assert forbidden_payload["rendered_summary_hash"] == forbidden_payload["pdf_summary_hash"], forbidden_payload
    first_forbidden = forbidden_payload["forbidden_terms_found_in_rendered_summary"][0]
    assert first_forbidden in forbidden_payload["hata"], forbidden_payload
    assert first_forbidden in theme_module._fold_text(forbidden_payload["summary_first_300"]), forbidden_payload

missing_summary_response = client.post(
    "/api/tema-kazanim/rapor",
    json={
        "format": "pdf",
        "analiz_sonucu": {
            "kitap_adi": "Eksik Ozet",
            "kitap_ozeti": "",
            "tema_analizi": [],
        },
    },
)
assert missing_summary_response.status_code == 400, missing_summary_response.get_data(as_text=True)
missing_summary_payload = missing_summary_response.get_json()
assert missing_summary_payload["hata"] == "PDF endpoint geçerli kitap_ozeti almadı"
assert missing_summary_payload.get("build_id")

USABLE_BUT_STRICTLY_INVALID_SUMMARY = """Giriş:
Anlatıcı okul çevresinde kaybolan defteri ararken arkadaşlarıyla yaşadığı sorunu anlamaya ve olayın başlangıcındaki ayrıntıları dikkatle bir araya getirmeye çalışır

Gelişme:
Arayış ilerledikçe sınıftaki ilişkiler netleşir öğrenciler birbirlerinin davranışlarını değerlendirir ve sorumluluk almanın ortak bir sorunu çözmedeki önemini fark eder

Temel Çatışma:
Kaybolan eşyanın bulunması isteği ile arkadaşlar arasında oluşan kuşku karşı karşıya gelir ve karakterlerin birbirine güvenme biçimi olayların yönünü belirler

Karakter İlişkileri:
Ana karakter arkadaşları ve öğretmeniyle konuşurken farklı görüşleri dinlemeyi öğrenir birlikte hareket etmenin tek başına karar vermekten daha etkili olduğunu görür

Genel Sonuç:
Metin dikkat sorumluluk arkadaşlık ve güven temalarını günlük bir okul olayı üzerinden tartışmaya açarak öğrencilerin kendi deneyimleriyle bağlantı kurmasını sağlar"""

assert not app_module._summary_is_valid_for_report(USABLE_BUT_STRICTLY_INVALID_SUMMARY)
assert app_module._summary_is_usable_for_pdf(USABLE_BUT_STRICTLY_INVALID_SUMMARY)
usable_summary_response = client.post(
    "/api/tema-kazanim/rapor",
    json={
        "format": "pdf",
        "analiz_sonucu": {
            "kitap_adi": "Kullanilabilir Ozet Testi",
            "kitap_ozeti": USABLE_BUT_STRICTLY_INVALID_SUMMARY,
            "tema_analizi": [{"ad": "sorumluluk", "tema_gucu": 70, "kanitlar": []}],
            "kazanim_analizi": [],
            "ana_karakterler": [],
        },
    },
)
assert usable_summary_response.status_code == 409, usable_summary_response.get_data(as_text=True)
usable_error = usable_summary_response.get_json()
assert usable_error["kod"] == "KITAP_TUTARLILIK_DENETIMI", usable_error
assert usable_error["tutarlilik_denetimi"]["unsupported_generic_patterns"], usable_error

mismatched_payload = {
    "kitap_adi": "Gökyüzünü Kaybeden Şehir",
    "kitap_ozeti": VALID_UI_SUMMARY,
    "ana_tema": "deniz yolculuğu",
    "tema_analizi": [
        {
            "ad": "deniz yolculuğu",
            "tema_gucu": 90,
            "kanitlar": [
                {"sayfa": 4, "alinti": "Kristof Kolomb açık denizde ilerleyen gemilerin rotasını pusula ve yıldızlarla belirleyerek yeni kıtaya ulaşmaya çalıştı."},
                {"sayfa": 8, "alinti": "Mürettebat okyanustaki uzun keşif seferinde fırtınalarla mücadele ederken kaptanın dönüş kararını tartıştı."},
                {"sayfa": 12, "alinti": "Liman geride kalınca denizciler yelkenleri açtı ve bilinmeyen adalara doğru süren tarihî yolculuğa devam etti."},
            ],
        }
    ],
    "kazanim_analizi": [],
    "ana_karakterler": [],
}
for endpoint in ["/api/tema-kazanim/rapor", "/api/theme-report/teacher-pdf"]:
    mismatch_response = client.post(endpoint, json={"format": "pdf", "analiz_sonucu": mismatched_payload})
    assert mismatch_response.status_code == 409, (endpoint, mismatch_response.status_code, mismatch_response.mimetype)
    mismatch_error = mismatch_response.get_json()
    assert mismatch_error["kod"] == "KITAP_TUTARLILIK_DENETIMI", mismatch_error
    assert mismatch_error["durduran_kapi"] == "OZET_KANIT_TUTARLILIK_KAPISI", mismatch_error
    for required_hash_key in [
        "consistency_error_summary_hash",
        "rendered_summary_hash",
        "canonical_summary_hash",
        "ui_summary_hash",
        "pdf_summary_hash",
    ]:
        assert mismatch_error.get(required_hash_key), mismatch_error
    assert mismatch_error["consistency_error_summary_first_300"] == VALID_UI_SUMMARY[:300], mismatch_error
    assert not mismatch_error["tutarlilik_denetimi"]["gecerli"], mismatch_error
    assert mismatch_error["tutarlilik_denetimi"]["hatalar"], mismatch_error
    assert not mismatch_error["tutarlilik_denetimi"]["alt_kapilar"]["OZET_KANIT_TUTARLILIK_KAPISI"]["gecerli"], mismatch_error

teacher_response = client.post(
    "/api/theme-report/teacher-pdf",
    json={
        "analiz_sonucu": {
            "kitap_adi": "Endpoint Öğretmen Raporu Testi",
            "yazar": "Test",
            "hedef_yas_grubu": "10-12 yaş",
            "kitap_ozeti": VALID_UI_SUMMARY,
            "ozet_guven_skoru": 0.91,
            "ozet_somutluk_skoru": 0.8,
            "ozet_uzunlugu": len(VALID_UI_SUMMARY.split()),
            "tema_analizi": [
                {"ad": "geçmişe özlem", "tema_gucu": 82, "guven_skoru": 0.82, "kanitlar": []}
            ],
            "kazanim_analizi": [
                {"ad": "karakter analizi yapma", "tema_gucu": 76, "guven_skoru": 0.76, "kanitlar": []}
            ],
            "ana_karakterler": [],
        },
    },
)
assert teacher_response.status_code == 409, teacher_response.get_data(as_text=True)
teacher_error = teacher_response.get_json()
assert teacher_error["kod"] in {"KITAP_TUTARLILIK_DENETIMI", "RAPOR_KALITE_KAPISI_V6"}, teacher_error
sys.exit(0)
assert teacher_file_bytes == teacher_response.data
assert teacher_response.headers.get("X-Report-SHA256") == hashlib.sha256(teacher_response.data).hexdigest()
teacher_text = pdf_text(teacher_response.data)
assert "Öğretmen Kitap Rehberi" in teacher_text, teacher_text
assert len(PdfReader(io.BytesIO(teacher_response.data)).pages) <= 5
assert "Hangi Derslerde Kullanılabilir?" in teacher_text, teacher_text
assert "Türkçe" in teacher_text, teacher_text
assert "Sosyal Bilgiler" in teacher_text, teacher_text
assert "Kitaba Özel Etkinlik Önerileri" in teacher_text, teacher_text
assert "Desteklenen beceriler:" in teacher_text, teacher_text
assert "Yaş/sınıf düzeyi:" in teacher_text, teacher_text
assert "Bu Kitabı Neden Öneriyoruz?" in teacher_text, teacher_text
for forbidden_text in [
    "Tema ve Kazanım Analizi",
    "Rapor Build ID",
    "Build ID",
    "Özet Güven Skoru",
    "Özet Somutluk Skoru",
    "Tema Gücü",
    "Ana Tema Gücü",
    "Ana Tema Güven",
    "Kanıt Sayısı",
    "Farklı Sayfa",
    "Bağlam Gücü",
    "Dinamik Güven",
    "Kalite Denetimi",
    "Analiz Guvenilirlik Ozeti",
]:
    assert forbidden_text not in teacher_text, (forbidden_text, teacher_text)
assert "karakter analizi yapma" in teacher_text, teacher_text
try:
    os.remove(teacher_output_path)
except OSError:
    pass
