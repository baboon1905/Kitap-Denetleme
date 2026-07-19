import io

from PyPDF2 import PdfReader

from theme_gain_analysis import analyze_theme_gain, build_pdf_report, build_word_report, prepare_theme_report_payload, summary_quality_issues


def section_body(summary: str, heading: str) -> str:
    lines = summary.replace("\r\n", "\n").split("\n")
    collecting = False
    parts = []
    headings = {"Giriş", "Gelişme", "Temel Çatışma", "Karakter İlişkileri", "Genel Sonuç"}
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.endswith(":") and stripped[:-1] in headings:
            if collecting:
                break
            collecting = stripped[:-1] == heading
            continue
        if collecting:
            parts.append(stripped)
    return " ".join(parts).strip()


def sentence_count(text: str) -> int:
    return len([part for part in text.replace("!", ".").replace("?", ".").split(".") if len(part.split()) >= 4])


sample_text = """
--- SAYFA 1 ---
ISBN 978-1-234-56789-0 Yayın hakları saklıdır. Birinci baskı ve yazar biyografisi bu sayfada yer alır.
--- SAYFA 2 ---
Bülent okulun bahçesinde kaybolan defterini aramaya başladı. Arkadaşlarının ne bildiğini anlamak için sınıfta dikkatle konuştu.
--- SAYFA 3 ---
Çiçek Abla ona acele etmeden düşünmesini söyledi. Tuna Abi de mahallede gördüklerini anlatarak Bülent'in arayışına destek oldu.
--- SAYFA 4 ---
Bülent yeni ipuçları buldukça hem sevindi hem de yanlış birini suçlamaktan çekindi. Sibel Öğretmen sınıfta herkesin birbirini dinlemesi gerektiğini anlattı.
--- SAYFA 5 ---
Arayış ilerledikçe Bülent defter meselesinin arkadaşlık ve sorumlulukla bağlantılı olduğunu fark etti. Olaylar çözülmeye yaklaşırken çocuklar birbirlerine daha dikkatli davranmaya başladı.
--- SAYFA 6 ---
Son bölümde Bülent yaşadıklarından daha sabırlı olmayı öğrenir. Final ayrıntısı verilmeden hikaye dayanışma ve güven duygusuyla kapanışa yönelir.
"""


result = analyze_theme_gain(sample_text, {"baslik": "Defterin Peşinde", "yazar": "Test Yazar"}, "9-12", "standart")
summary = result["kitap_ozeti"]

assert "Metindeki olay izleri" not in summary
assert "noktasına işaret ediyor" not in summary
assert "kanıt" not in summary.lower()
assert "Sayfa" not in summary
assert "ISBN" not in summary
assert "Yayın hakları" not in summary
assert "baskı" not in summary.lower()
assert "yazar biyografisi" not in summary.lower()
for template_phrase in [
    "gündelik düzen",
    "merak ettiği durum",
    "belirsizlikle baş eder",
    "ilişki ağı",
    "öğretmenin sınıfta",
]:
    assert template_phrase not in summary.lower()

for required_heading in ["Giriş", "Gelişme", "Temel Çatışma", "Karakter İlişkileri", "Genel Sonuç"]:
    body = section_body(summary, required_heading)
    assert body, required_heading
    assert sentence_count(body) >= 3, required_heading

assert sentence_count(summary) >= 15
assert not summary_quality_issues(summary), summary_quality_issues(summary)
assert result["olay_akisi"], "Olay Akışı boş olamaz"
assert len(result["olay_akisi"]) >= 4
assert all(item.get("baslik") and item.get("metin") for item in result["olay_akisi"])
assert result["ozet_somutluk_skoru"] > 0
assert len(result["ozet_olay_kumeleri"]) >= 3

bad_summary = """Giriş:
Metindeki olay izleri, ISBN 978-1-234-56789-0 noktasına işaret ediyor.
"""
assert summary_quality_issues(bad_summary)

single_sentence_summary = """Giriş:
Bülent defterini arar.

Gelişme:
Bülent defterini arar.

Temel Çatışma:
Bülent defterini arar.

Karakter İlişkileri:
Bülent defterini arar.

Genel Sonuç:
Bülent defterini arar.
"""
assert summary_quality_issues(single_sentence_summary)

memory_text = """
--- SAYFA 1 ---
Yayın hakları saklıdır. ISBN 978-1-234-56789-0. Yazar biyografisi ve baskı bilgisi.
--- SAYFA 2 ---
Anlatıcı yıllar sonra çocukluğunun geçtiği sokağa döner. Yağmur altında yürürken eski mahallesini hatırlar.
--- SAYFA 3 ---
Sokaktaki evler değişmiş, eski komşuların çoğu gitmiştir. Şehirleşme mahalledeki eski düzeni silmeye başlamıştır.
--- SAYFA 4 ---
Babası, annesi ve kardeşi Suna ile yaşadığı çocukluk günleri anıların içinde belirir. Çiçek abla, Dilek ve Çilek mahalledeki eski yakınlığı hatırlatır.
--- SAYFA 5 ---
Mahalle esnafı, komşular ve sokakta oynayan çocuklar geçmiş hayatın canlı parçaları olarak anlatılır. Anlatıcı eski mahalle ile yeni şehir arasındaki farkı daha çok hisseder.
--- SAYFA 6 ---
Son bölümde yağmur, sokak ve anılar iç içe geçer. Final ayrıntısı verilmeden kaybolan mahalle kültürünün bıraktığı duygu öne çıkar.
"""

memory_result = analyze_theme_gain(memory_text, {"baslik": "Sokağa Dönüş", "yazar": "Test Yazar"}, "9-12", "standart")
memory_summary = memory_result["kitap_ozeti"]
for template_phrase in [
    "gündelik düzen",
    "temel ihtiyaç",
    "merak ettiği durum",
    "belirsizlikle baş eder",
    "ilişki ağı",
    "öğretmenin sınıfta",
]:
    assert template_phrase not in memory_summary.lower()

concrete_terms = [
    "sokak", "mahalle", "yağmur", "çocukluk", "baba", "anne",
    "Suna", "Çiçek abla", "değişim", "şehirleşme", "anı",
]
assert sum(1 for term in concrete_terms if term.lower() in memory_summary.lower()) >= 3
assert "dostluk temas" not in memory_summary.lower()
assert "şehirye" not in memory_summary.lower()
assert "ve ve" not in memory_summary.lower()
assert "ile ile" not in memory_summary.lower()
assert "kardeşi ve kardeşi" not in memory_summary.lower()
assert "kardeşi suna ve kardeşi" not in memory_summary.lower()
assert "çiçek ana karakterdir" not in memory_summary.lower()
assert "anlatıcı" in memory_summary.lower()
assert sum(1 for term in concrete_terms if term.lower() in memory_summary.lower()) >= 5
assert memory_result["olay_akisi"], "Olay Akışı boş olamaz"
assert len(memory_result["olay_akisi"]) >= 4
assert all(item.get("baslik") and item.get("metin") for item in memory_result["olay_akisi"])
assert len(memory_result["ozet_olay_kumeleri"]) >= 3
assert memory_result["ozet_somutluk_skoru"] >= 0.6
assert {"aile", "mahalle_sokak", "degisim_sehirlesme"}.issubset(set(memory_result["ozet_olay_kumeleri"]))
for required_heading in ["Giriş", "Gelişme", "Temel Çatışma", "Karakter İlişkileri", "Genel Sonuç"]:
    body = section_body(memory_summary, required_heading)
    assert sentence_count(body) >= 3, required_heading
assert not summary_quality_issues(memory_summary), summary_quality_issues(memory_summary)

thin_text = """
--- SAYFA 1 ---
Mahalle değişti. Şehirleşme eski mahalleyi değiştirdi.
--- SAYFA 2 ---
Mahallede eski düzen değişti. Şehirleşme sokakları farklılaştırdı.
--- SAYFA 3 ---
Yeni şehir görüntüsü eski mahalle görüntüsünü geride bıraktı.
"""
thin_result = analyze_theme_gain(thin_text, {"baslik": "Dar Özet"}, "9-12", "standart")
assert thin_result["kitap_ozeti"] == "Özet güvenilir üretilemedi."
assert not thin_result["olay_akisi"]

missing_metadata_result = analyze_theme_gain(memory_text, {}, "9-12", "standart")
assert missing_metadata_result["ozet_guven_skoru"] < memory_result["ozet_guven_skoru"]
assert memory_result["ozet_kalite_kontrol"]["metadata_kalitesi"] > missing_metadata_result["ozet_kalite_kontrol"]["metadata_kalitesi"]
assert "karakter_tutarliligi" in memory_result["ozet_kalite_kontrol"]

gokyuzu_text = """
--- SAYFA 1 ---
Benim adım Bülent. Yıllar sonra çocukluğumun geçtiği sokağa döndüm ve yağmur altında eski mahalleyi hatırlıyorum.
--- SAYFA 2 ---
Annem, Bülent hemen eve gelir misin yavrum diye seslenirdi. O sesi duyunca çocukluğumun kapıları açıldı.
--- SAYFA 3 ---
Bülent sokakta yürürken babasının dükkânını, annesini ve kardeşi Suna'yı düşündü.
--- SAYFA 4 ---
Çiçek Abla mahallede anılırdı. Çiçek çocukların yanından geçti. Çiçek kapının önünde bekledi.
--- SAYFA 5 ---
Tuna Abi sokakta çocuklara yardım ederdi. Sibel Öğretmen okulda Bülent'i dinlerdi.
--- SAYFA 6 ---
Emrullah Efendi babanın dükkânı önünde selam verir, mahalle esnafı eski günleri anlatırdı.
--- SAYFA 7 ---
Bülent değişen şehir karşısında eski sokakların kaybolduğunu fark ettim diye düşündü.
--- SAYFA 8 ---
Sonunda Bülent çocukluk anılarının yeni şehirde nasıl eksildiğini gördüm diyerek geçmişe baktı.
"""

gokyuzu_result = analyze_theme_gain(gokyuzu_text, {"baslik": "Gökyüzünü Kaybeden Şehir", "yazar": "Test"}, "9-12", "standart")
gokyuzu_payload = prepare_theme_report_payload(gokyuzu_result)
assert gokyuzu_payload["kitap_ozeti"], gokyuzu_payload
assert gokyuzu_payload["kitap_ozeti"] != "Özet güvenilir üretilemedi.", gokyuzu_payload
assert gokyuzu_payload["ozet_uzunlugu"] >= 200, gokyuzu_payload["kitap_ozeti"]
assert "ozet_kalite_hatalari" in gokyuzu_payload, gokyuzu_payload
assert "anlatıcı" in gokyuzu_payload["kitap_ozeti"].lower(), gokyuzu_payload["kitap_ozeti"]

tolerated_summary = """Giriş:
Anlatıcı yıllar sonra sokağa döner ve yağmur altında çocukluk anılarını hatırlar. Mahalle, evler, baba, anne ve kardeşi Suna üzerinden eski günler yeniden görünür. Bu dönüş, bugünkü şehir görüntüsüyle çocuklukta kalan sokak hayatını yan yana getirir.

Gelişme:
Sokakta karşılaştığı değişim, anlatıcının çocuklukta tanıdığı komşular, esnaf ve Çiçek Abla gibi kişileri düşünmesine yol açar. Tuna Abi, Sibel Öğretmen ve Emrullah Efendi gibi figürler mahalle hayatının okul, dükkân ve komşuluk çevresini tamamlar. Babanın dükkânı, okul yolu ve kapı önleri geçmişin somut durakları olarak belirir.

Temel Çatışma:
Temel karşıtlık eski mahalle düzeni ile yeni şehirleşme arasındadır. Anlatıcı değişen sokakları gördükçe çocukluk, aile ve komşuluk bağlarının artık aynı biçimde sürmediğini fark eder. Yağmur altında yapılan yürüyüş, bu kayıp duygusunu daha görünür hale getirir.

Karakter İlişkileri:
Bülent'in annesi, babası, kardeşi Suna, Çiçek Abla, Tuna Abi, Sibel Öğretmen ve Emrullah Efendi ile bağı anılar üzerinden kurulur. Bu kişiler tek tek büyük maceralar yaşamaz; mahalle, okul, dükkân ve sokak çevresindeki ortak geçmişi görünür kılar. Çiçek Abla ve diğer yan figürler, anlatıcının hafızasında mahalle sıcaklığını taşıyan kişiler olarak kalır.

Genel Sonuç:
Son bölüm, finali açık etmeden geçmişe özlem, mahalle kültürü ve şehirleşme karşıtlığını belirginleştirir. Yağmur, sokak ve anı duygusu anlatıcının bugünden geçmişe bakışını taşır. Kitap, kaybolan mahalle sıcaklığını ve değişen şehir karşısındaki iç sızısını öğretmenin sınıfta tartışabileceği somut bir olay akışıyla verir."""

tolerated_payload = prepare_theme_report_payload({
    "kitap_ozeti": tolerated_summary,
    "ozet_guven_skoru": 0.94,
    "ozet_somutluk_skoru": 0.82,
    "ozet_uzunlugu": len(tolerated_summary.split()),
})
assert tolerated_payload["kitap_ozeti"] != "Özet güvenilir üretilemedi.", tolerated_payload
assert tolerated_payload["ozet_guven_skoru"] == 0.68, tolerated_payload
assert tolerated_payload["ozet_kalite_hatalari"], tolerated_payload

mostly_forbidden_summary = """Giriş:
ISBN 978-1-234-56789-0 yayın hakları ve baskı bilgisi.
Gelişme:
Yazar biyografisi, künye ve yayıncı bilgisi.
Temel Çatışma:
ISBN, telif metni ve baskı bilgisi.
Karakter İlişkileri:
Yazar biyografisi ve yayınevi bilgisi.
Genel Sonuç:
Künye ve telif metinleri."""

forbidden_payload = prepare_theme_report_payload({
    "kitap_ozeti": mostly_forbidden_summary,
    "ozet_guven_skoru": 0.9,
    "ozet_somutluk_skoru": 0.9,
    "ozet_uzunlugu": len(mostly_forbidden_summary.split()),
})
assert forbidden_payload["kitap_ozeti"] == "Özet güvenilir üretilemedi.", forbidden_payload
assert forbidden_payload["ozet_yasak_icerik_orani"] > 0.5, forbidden_payload

ui_valid_summary = """Giriş:
Anlatıcı yıllar sonra çocukluğunun geçtiği sokağa döner ve yağmur altında eski mahalleyi hatırlar. Sokak, evler, baba, anne ve kardeşi Suna üzerinden geçmiş yeniden görünür. Bu başlangıç, bugünkü şehir görüntüsü ile çocuklukta kalan mahalle düzenini yan yana getirir. Okur daha ilk bölümde anlatıcının yalnızca bir yere değil, anılarla dolu bir zamana döndüğünü anlar.

Gelişme:
Anlatıcının yürüyüşü ilerledikçe aile, okul, komşular ve esnaf çevresi daha belirgin hale gelir. Çiçek Abla, Tuna Abi, Sibel Öğretmen ve Emrullah Efendi gibi kişiler mahalledeki eski yakınlığı ve gündelik hayatı tamamlar. Babanın dükkânı, okul yolu ve kapı önleri anıların somut durakları olarak anlatılır. Bu kişiler ana olayın yerine geçmez; anlatıcının çocukluk dünyasını görünür kılan yan figürler olarak kalır.

Temel Çatışma:
Kitabın temel karşıtlığı eski mahalle düzeni ile yeni şehirleşme arasındadır. Anlatıcı değişen sokakları gördükçe çocukluk, aile ve komşuluk bağlarının artık aynı biçimde sürmediğini fark eder. Yağmur altında yapılan yürüyüş, kaybolan mahalle kültürünün bıraktığı eksilme duygusunu güçlendirir. Çatışma büyük bir maceradan çok geçmişin sıcaklığı ile bugünün değişmiş şehir görüntüsü arasında kurulur.

Karakter İlişkileri:
Bülent'in annesi, babası, kardeşi Suna, Çiçek Abla, Tuna Abi, Sibel Öğretmen ve Emrullah Efendi ile bağı anılar üzerinden kurulur. Bu ilişkiler aile, okul, dükkân ve sokak çevresindeki ortak geçmişi görünür kılar. Çiçek Abla ve diğer yan figürler, anlatıcının hafızasında mahalle sıcaklığını taşıyan kişiler olarak önem kazanır. İlişkiler, tek bir kişinin özel macerasından çok birlikte yaşanmış bir mahalle hayatını anlatır.

Genel Sonuç:
Son bölüm, finali açık etmeden geçmişe özlem, mahalle kültürü ve şehirleşme karşıtlığını belirginleştirir. Yağmur, sokak ve anı duygusu anlatıcının bugünden geçmişe bakışını taşır. Kitap, kaybolan mahalle sıcaklığını ve değişen şehir karşısındaki iç sızısını somut olaylar ve kişiler üzerinden anlaşılır kılar. Öğretmen için metnin ana yönü, anlatıcının çocukluk anılarıyla şehirleşme arasındaki duygusal karşılaşmadır."""

ui_payload = {
    "kitap_adi": "Gökyüzünü Kaybeden Şehir",
    "kitap_ozeti": ui_valid_summary,
    "ozet_guven_skoru": 0.91,
    "ozet_somutluk_skoru": 0.8,
    "ozet_uzunlugu": len(ui_valid_summary.split()),
    "olay_akisi": [
        {"baslik": "Başlangıç", "metin": "Anlatıcı yıllar sonra sokağa döner."},
        {"baslik": "Gelişen Olaylar", "metin": "Mahalle, aile, okul ve esnaf anıları açılır."},
        {"baslik": "Dönüm Noktası", "metin": "Yeni şehirleşme ile eski mahalle karşı karşıya gelir."},
        {"baslik": "Sonuç", "metin": "Geçmişe özlem ve değişim duygusu öne çıkar."},
    ],
}

prepared_ui_payload = prepare_theme_report_payload(ui_payload)
assert prepared_ui_payload["kitap_ozeti"] == ui_valid_summary, prepared_ui_payload
assert prepared_ui_payload["kitap_ozeti"] != "Özet güvenilir üretilemedi.", prepared_ui_payload
assert prepared_ui_payload["ozet_kalite_kontrol"].get("gecerli_ui_ozeti_korundu") is True, prepared_ui_payload

word_html = build_word_report(ui_payload).getvalue().decode("utf-8")
assert "Özet güvenilir üretilemedi" not in word_html, word_html
assert "Anlatıcı yıllar sonra çocukluğunun geçtiği sokağa döner" in word_html, word_html

pdf_bytes = build_pdf_report(ui_payload).getvalue()
pdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(pdf_bytes)).pages)
assert "Özet güvenilir üretilemedi" not in pdf_text, pdf_text
assert "Anlatıcı yıllar sonra" in pdf_text, pdf_text
