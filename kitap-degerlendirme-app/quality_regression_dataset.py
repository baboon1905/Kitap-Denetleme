from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class GoldenBookSnapshot:
    book_title: str = ""
    book_type: str = ""
    subtype: str = ""
    narrative_type: str = ""
    main_theme: str = ""
    top_3_themes: List[str] | None = None
    central_entities: List[str] | None = None
    main_characters: List[str] | None = None
    entity_count: int = 0
    canonical_event_count: int = 0
    summary_strategy: str = ""
    summary_word_count: int = 0
    summary_confidence: float = 0.0
    entity_confidence: float = 0.0
    event_confidence: float = 0.0
    event_coverage: float = 0.0
    evidence_coverage: float = 0.0
    repeated_event_ratio: float = 0.0
    generic_event_ratio: float = 0.0
    low_confidence_event_count: int = 0
    theme_confidence: float = 0.0
    quote_ratio: float = 0.0
    unsupported_event_count: int = 0
    report_status: str = "produced"
    character_count: int = 0
    summary_quality: int = 0
    report_confidence: int = 0
    teacher_report_status: str = ""
    manual_review_status: str = ""
    summary_text: str = ""
    summary_hash: str = ""
    summary_similarity: float = 1.0
    event_count: int = 0
    bridge_sentence_ratio: float = 0.0
    interpretation_sentence_ratio: float = 0.0
    avg_sentence_length: float = 0.0
    event_density: float = 0.0
    evidence_density: float = 0.0
    hallucination_ratio: float = 0.0
    narrative_diversity: float = 0.0
    character_consistency: float = 0.0
    teacher_report_consistency: float = 0.0


@dataclass(frozen=True)
class QualityRegressionCase:
    case_id: str
    title: str
    author: str
    text: str
    expected_main_character: str
    expected_main_theme: str
    expected_book_type: str
    expected_top_gains: List[str]
    age_group: str = "9-12"
    expected_subtype: str = ""
    golden_snapshot: GoldenBookSnapshot | None = None


def _pages(*sentences: str) -> str:
    return "\n".join(f"--- SAYFA {index} ---\n{sentence}" for index, sentence in enumerate(sentences, 1))


QUALITY_REGRESSION_CASES: List[QualityRegressionCase] = [
    QualityRegressionCase(
        "buyulu_yastiklar",
        "Buyulu Yastiklar",
        "Test",
        _pages(
            "Kral Kapgotur, Gokistan ulkesinde dusleri saklayan buyulu yastiklari topladi ve halkin huzuru bozuldu.",
            "Yasemin, Aydin Ogretmen'e karabasanlarin yeniden geldigini soyledi ve sorunun kaynagini arastirmaya basladi.",
            "Lanson Yilanson ve Dankof Oburof sarayin kapisinda tartisti; Zilius Rezilius buyulu yastigi gorunce planini degistirdi.",
            "Yasemin duslerin neden karardigini anlamak icin Aydin Ogretmen ile birlikte kanitlari karsilastirdi.",
            "Kral, ulkenin eski nesesini bulmasi icin herkesi topladi ve karakterler birlikte cozum aradi.",
            "Grup karabasanlarin kaynagini aciga cikarinca yastiklarin nasil korunacagina karar verdi.",
        ),
        "Yasemin",
        "dayanisma",
        "kurgu Ã§ocuk Ã¶ykÃ¼sÃ¼",
        ["okudugunu anlama", "cikarim yapma", "karakter analizi yapma"],
        expected_subtype="fantastik / mizahi Ã§ocuk anlatÄ±sÄ±",
        golden_snapshot=GoldenBookSnapshot(
            book_type="kurgu Ã§ocuk Ã¶ykÃ¼sÃ¼",
            subtype="fantastik / mizahi Ã§ocuk anlatÄ±sÄ±",
            main_theme="problem çözme",
            top_3_themes=["problem çözme", "cesaret", "sorumluluk"],
            character_count=2,
            summary_quality=70,
            report_confidence=46,
            teacher_report_status="produced",
            manual_review_status="clear",
            summary_hash="35b33806a1db14a6f82351d1466e9c65c03e1f606ac2587dba90e3acb9e61d35",
            event_count=2,
            bridge_sentence_ratio=0.0,
            interpretation_sentence_ratio=1.0,
            avg_sentence_length=11.2,
            event_density=0.444,
            evidence_density=0.082,
            hallucination_ratio=0.2,
            narrative_diversity=1.0,
            character_consistency=1.0,
            teacher_report_consistency=1.0,
        ),
    ),
    QualityRegressionCase(
        "bay_lemoncello",
        "Bay Lemoncello'nun Kutuphanesinden Kacis",
        "Chris Grabenstein",
        _pages(
            "Benim adim Miguel Fernandez; Miguel Fernandez oyunu anlatti ama yarismadaki ana karar Kyle Keeley etrafinda gelisti.",
            "Kyle Keeley kutuphanedeki ilk bulmacayi cozmek icin Akimi Hughes ile birlikte ipuclarini arastirdi.",
            "Kyle Keeley takimla gorev bolustu, Miguel Fernandez katalog bilgisini paylasti ve grup birbirine destek oldu.",
            "Charles Chiltington hile yapmaya calisirken Kyle Keeley adil kalmayi secti ve kurallari korudu.",
            "Kyle Keeley son sifreyi yorumladi, neden sonuc iliskisini kurdu ve cikis yolunu takimina gosterdi.",
            "Takim birlikte karar vererek kitap raflarindaki son ipucunu paylasti ve kacis oyununu tamamlamak icin is birligi yapti.",
        ),
        "Kyle Keeley",
        "problem cozme",
        "macera",
        ["okudugunu anlama", "cikarim yapma", "karakter analizi yapma"],
        expected_subtype="bulmaca / kaÃ§Ä±ÅŸ oyunu",
        golden_snapshot=GoldenBookSnapshot(
            book_type="macera",
            subtype="bulmaca / kaÃ§Ä±ÅŸ oyunu",
            main_theme="problem Ã§Ã¶zme",
            top_3_themes=["problem Ã§Ã¶zme", "takÄ±m Ã§alÄ±ÅŸmasÄ±", "adil rekabet"],
            character_count=2,
            summary_quality=57,
            report_confidence=46,
            teacher_report_status="produced",
            manual_review_status="clear",
            summary_hash="00c6a7acd27490054a336bd34b38d594ca5ebee802fc7282e33dfbdcbd16e362",
            event_count=2,
            bridge_sentence_ratio=0.0,
            interpretation_sentence_ratio=1.0,
            avg_sentence_length=12.4,
            event_density=0.444,
            evidence_density=0.209,
            hallucination_ratio=0.6,
            narrative_diversity=1.0,
            character_consistency=0.0,
            teacher_report_consistency=1.0,
        ),
    ),
    QualityRegressionCase(
        "kolomb",
        "Benim Adim Kristof Kolomb",
        "Test",
        _pages(
            "Kristof Kolomb yeni deniz yolunu bulmak icin haritayi inceledi ve rota uzerine karar verdi.",
            "Kristof Kolomb saraydan destek istedi; cunku sefer icin gemi ve murettebat gerekiyordu.",
            "Firtina cikinca Kristof Kolomb korkuya ragmen yolculugu surdurmeyi secti.",
            "Sonunda seferin sonucu, kesif fikrinin hem merak hem de karar gerektirdigini gosterdi.",
        ),
        "Kristof Kolomb",
        "kesif",
        "tarih",
        ["neden-sonuc iliskisi kurma", "cikarim yapma", "karakter analizi yapma"],
        expected_subtype="tarihÃ® biyografi",
        golden_snapshot=GoldenBookSnapshot(
            book_type="tarihÃ® biyografi",
            subtype="tarihÃ® biyografi",
            main_theme="keÅŸif",
            top_3_themes=["kararlÄ±lÄ±k", "keÅŸif", "merak"],
            character_count=1,
            summary_quality=53,
            report_confidence=45,
            teacher_report_status="produced",
            manual_review_status="clear",
            summary_hash="38a7385bdd14caf54d188d6b64de7f63c8474b98a251b2acc926b0e3dd60152c",
            event_count=0,
            bridge_sentence_ratio=0.0,
            interpretation_sentence_ratio=1.0,
            avg_sentence_length=12.0,
            event_density=0.0,
            evidence_density=0.185,
            hallucination_ratio=0.2,
            narrative_diversity=1.0,
            character_consistency=1.0,
            teacher_report_consistency=1.0,
        ),
    ),
    QualityRegressionCase(
        "defter",
        "Kayip Defter",
        "Test",
        _pages(
            "Elif okulda defterini kaybetti ve once nerede biraktigini dusundu.",
            "Elif arkadaslarini suclamadan dinledi, sonra ipuclarini sirayla kontrol etti.",
            "Elif dogru davranisi secerek hatasini kabul etti ve sinifla paylasti.",
            "Sonunda defter bulundu; Elif sorumluluk almanin sonuca etkisini anladi.",
        ),
        "Elif",
        "sorumluluk",
        "cagdas",
        ["okudugunu anlama", "neden-sonuc iliskisi kurma", "degerleri fark etme"],
        expected_subtype="deÄŸer odaklÄ± anlatÄ±",
        golden_snapshot=GoldenBookSnapshot(
            book_type="deÄŸerler eÄŸitimi odaklÄ± eser",
            subtype="deÄŸer odaklÄ± anlatÄ±",
            main_theme="sorumluluk",
            top_3_themes=["sorumluluk", "dÃ¼rÃ¼stlÃ¼k", "arkadaÅŸlÄ±k"],
            character_count=1,
            summary_quality=67,
            report_confidence=45,
            teacher_report_status="produced",
            manual_review_status="clear",
            summary_hash="2280fd49517ce9ac7a90b32522231acaf9431ed8cb1f17c393e50b6558e5e395",
            event_count=2,
            bridge_sentence_ratio=0.0,
            interpretation_sentence_ratio=1.0,
            avg_sentence_length=10.8,
            event_density=0.444,
            evidence_density=0.051,
            hallucination_ratio=0.2,
            narrative_diversity=1.0,
            character_consistency=0.0,
            teacher_report_consistency=1.0,
        ),
    ),
    QualityRegressionCase(
        "park",
        "Yesil Park Nobeti",
        "Test",
        _pages(
            "Mert parkta cevre kirliligini fark etti ve dogayi korumak icin copleri topladi.",
            "Mert arkadaslariyla birlikte fidan dikti ve yesil alani koruma gorevini ustlendi.",
            "Sonra sinif, geri donusum kutularini yerlestirerek parkin temiz kalmasini sagladi.",
            "Mert bu olaydan sonra cevreye duyarliligin davranisla gosterildigini anladi.",
        ),
        "Mert",
        "cevre bilinci",
        "cagdas",
        ["degerleri fark etme", "neden-sonuc iliskisi kurma", "okudugunu anlama"],
        age_group="6-8",
        expected_subtype="Ã§aÄŸdaÅŸ Ã§ocuk romanÄ±",
        golden_snapshot=GoldenBookSnapshot(
            book_type="Ã§aÄŸdaÅŸ Ã§ocuk romanÄ±",
            subtype="Ã§aÄŸdaÅŸ Ã§ocuk romanÄ±",
            main_theme="problem çözme",
            top_3_themes=["problem çözme", "çevre bilinci", "sorumluluk"],
            character_count=1,
            summary_quality=56,
            report_confidence=51,
            teacher_report_status="produced",
            manual_review_status="clear",
            summary_hash="4a517288457401168fe97750cbde0a8af6f2c08a67fd450ad238c7fd1414df9b",
            event_count=2,
            bridge_sentence_ratio=0.0,
            interpretation_sentence_ratio=1.0,
            avg_sentence_length=11.6,
            event_density=0.444,
            evidence_density=0.079,
            hallucination_ratio=0.2,
            narrative_diversity=1.0,
            character_consistency=0.8,
            teacher_report_consistency=1.0,
        ),
    ),
    QualityRegressionCase(
        "mahalle",
        "Eski Sokaga Donus",
        "Test",
        _pages(
            "Bulent yillar sonra cocuklugunun gectigi sokaga dondu ve eski gunleri hatirladi.",
            "Yagmur altinda mahallede yururken komsularin yardimlastigi gunlere ozlem duydu.",
            "Bulent eski evleri gorunce sehrin degistigini fark etti ve anilarini ailesiyle paylasti.",
            "Sonunda gecmise ozlem duygusu, degisen sehir karsisinda daha belirgin hale geldi.",
        ),
        "Bulent",
        "gecmise ozlem",
        "cagdas",
        ["cikarim yapma", "karakter analizi yapma", "olay orgusunu yorumlama"],
        expected_subtype="Ã§aÄŸdaÅŸ Ã§ocuk romanÄ±",
        golden_snapshot=GoldenBookSnapshot(
            book_type="Ã§aÄŸdaÅŸ Ã§ocuk romanÄ±",
            subtype="Ã§aÄŸdaÅŸ Ã§ocuk romanÄ±",
            main_theme="geÃ§miÅŸe Ã¶zlem",
            top_3_themes=["geÃ§miÅŸe Ã¶zlem", "deÄŸiÅŸim", "aile"],
            character_count=0,
            summary_quality=53,
            report_confidence=41,
            teacher_report_status="produced",
            manual_review_status="clear",
            summary_hash="c985f95b535b51abf50c859c993a5f78f4e7e9c57b6d835c2641da46ad24184c",
            event_count=0,
            bridge_sentence_ratio=0.0,
            interpretation_sentence_ratio=1.0,
            avg_sentence_length=12.2,
            event_density=0.0,
            evidence_density=0.045,
            hallucination_ratio=0.6,
            narrative_diversity=1.0,
            character_consistency=1.0,
            teacher_report_consistency=1.0,
        ),
    ),
    QualityRegressionCase(
        "bilim_defteri",
        "Bilim Defteri",
        "Test",
        _pages(
            "Gezegenler ve yildizlar hakkinda temel bilim bilgisi sunulur; bu bolum gok cisimlerinin ne oldugunu aciklar.",
            "Deney ve gozlem, bilimsel dusunmenin iki onemli yoludur; bir cismin hareketi olculerek sonuclar karsilastirilir.",
            "Orneklerde teknoloji, arastirma ve kavram bilgisi gunluk yasamda dogayi anlamaya yardimci olur.",
            "Son bolum, bilimsel bilginin soru sorma, kanit toplama ve sonucu aciklama adimlariyla gelistigini anlatir.",
        ),
        "",
        "bilimsel dusunme",
        "bilimsel iÃ§erik",
        ["okudugunu anlama", "neden-sonuc iliskisi kurma", "cikarim yapma"],
        expected_subtype="bilimsel iÃ§erik",
        golden_snapshot=GoldenBookSnapshot(
            book_type="bilimsel iÃ§erik",
            subtype="bilgilendirici bilim",
            main_theme="bilimsel dÃ¼ÅŸÃ¼nme",
            top_3_themes=["bilimsel dÃ¼ÅŸÃ¼nme", "merak", "teknoloji"],
            character_count=0,
            summary_quality=53,
            report_confidence=30,
            teacher_report_status="produced",
            manual_review_status="clear",
            summary_hash="bcda2d00a8ce8bab6b45a79fdca2298e9d5a0a3b3de64d7b54be134d1589703b",
            event_count=0,
            bridge_sentence_ratio=0.0,
            interpretation_sentence_ratio=1.0,
            avg_sentence_length=12.0,
            event_density=0.0,
            evidence_density=0.0,
            hallucination_ratio=0.0,
            narrative_diversity=1.0,
            character_consistency=1.0,
            teacher_report_consistency=1.0,
        ),
    ),
    QualityRegressionCase(
        "mini_masal",
        "Sihirli Tohum Masali",
        "Test",
        _pages(
            "Kucuk Ela, kuruyan bahcede parlak bir tohum buldu ve onu dikkatle topraga ekti.",
            "Yagmur gecikince Ela sabirla bekledi, komsularindan su istedi ve fidanin kurumamasi icin ugras verdi.",
            "Tohum filizlenince bahceye renk geldi; cocuklar bu degisimi sevincli bir masal gibi izledi.",
            "Ela, emek ve sabrin kucuk bir tohumu bile buyuk bir umuda donusturdugunu anladi.",
        ),
        "Ela",
        "sabir",
        "kurgu Ã§ocuk Ã¶ykÃ¼sÃ¼",
        ["degerleri fark etme", "okudugunu anlama", "cikarim yapma"],
        age_group="6-8",
        expected_subtype="fantastik / mizahi Ã§ocuk anlatÄ±sÄ±",
        golden_snapshot=GoldenBookSnapshot(
            book_type="kurgu Ã§ocuk Ã¶ykÃ¼sÃ¼",
            subtype="fantastik / mizahi Ã§ocuk anlatÄ±sÄ±",
            main_theme="sorumluluk",
            top_3_themes=["sorumluluk", "sabır", "emek"],
            character_count=0,
            summary_quality=53,
            report_confidence=41,
            teacher_report_status="produced",
            manual_review_status="clear",
            summary_hash="233d5d3889e8a72885f0f44206ab643600060dc7c8ea15c3bf6f2f06a9b0253f",
            event_count=0,
            bridge_sentence_ratio=0.0,
            interpretation_sentence_ratio=1.0,
            avg_sentence_length=12.2,
            event_density=0.0,
            evidence_density=0.015,
            hallucination_ratio=0.2,
            narrative_diversity=1.0,
            character_consistency=1.0,
            teacher_report_consistency=1.0,
        ),
    ),
]


GOLDEN_BOOKS: List[QualityRegressionCase] = [
    case for case in QUALITY_REGRESSION_CASES if case.golden_snapshot is not None
]


GENERIC_NAMES = [
    "Ayse Yilmaz", "Can Demir", "Zeynep Kaya", "Emre Aydin", "Nisa Cakir",
    "Kerem Arslan", "Derya Yildiz", "Selim Koc", "Ela Kaplan", "Burak Deniz",
    "Seda Polat", "Ozan Tekin", "Melis Gunes", "Tarik Aslan", "Yasemin Celik",
]


for offset, name in enumerate(GENERIC_NAMES, 6):
    QUALITY_REGRESSION_CASES.append(
        QualityRegressionCase(
            f"generic_{offset}",
            f"Ornek Kitap {offset}",
            "Test",
            _pages(
                f"{name} okulda somut bir olayla karsilasti ve once durumu anlamaya calisti.",
                f"{name} arkadaslariyla birlikte karar verdi, gorev bolustu ve destek oldu.",
                f"{name} yanlis davranisi fark etti, dogru davranisi secerek sorumluluk ustlendi.",
                f"Sonunda {name} olaylarin neden sonuc iliskisini kurdu ve grubuyla paylasti.",
            ),
            name,
            "dayanisma",
            "cagdas",
            ["okudugunu anlama", "degerleri fark etme", "neden-sonuc iliskisi kurma"],
        )
    )


