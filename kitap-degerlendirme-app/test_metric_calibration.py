from theme_gain_analysis import (
    _analysis_reliability_components,
    _apply_summary_quality_gate,
    _character_depth_score,
    _central_quality_metrics,
    _fold_text,
    _report_scores,
    _summary_quality_gate_metrics,
    _theme_quality_score,
    kitap_tutarlilik_denetimi,
    prepare_theme_report_payload,
)
from narrative_realizer import final_turkish_cleanup, narrative_realize
import unicodedata


summary = """Giriş:
Kristof Kolomb yeni bir deniz rotası bulmak için saraya gider. Kraliçe ile sefer planını görüşür. Haritaları inceleyerek yolculuğun hedefini belirler.

Gelişme:
Kolomb mürettebatıyla limandan ayrılır. Gemiler okyanusta fırtına ve yön bulma sorunlarıyla karşılaşır. Denizciler rota konusunda farklı kararları tartışır.

Temel Çatışma:
Mürettebat geri dönmek ister. Kristof Kolomb riskleri değerlendirip yolculuğu sürdürmeye karar verir. Hedefe ulaşma isteği ile denizdeki tehlikeler çatışır.

Karakter İlişkileri:
Kristof Kolomb mürettebatın kaygılarını dinler. Kral Fernando ve saray çevresi sefer hazırlığını değerlendirir. Denizciler zor koşullarda birlikte hareket eder.

Genel Sonuç:
Yolculuk coğrafi keşiflerin tarihsel sonuçlarını görünür kılar. Kararlılık ve merak alınan kararlar üzerinden işlenir. Eser keşiflerin farklı toplumlara etkisini tartışmaya açar."""

prepared = prepare_theme_report_payload({
    "kitap_adi": "Benim Adım Kristof Kolomb",
    "book_type": "tarihî biyografi",
    "kitap_ozeti": summary,
    "ozet_somutluk_skoru": 0,
    "ozet_guven_skoru": 0.8,
    "ana_tema": "kararlılık",
    "tema_analizi": [],
    "ana_karakterler": [],
})
assert prepared["ozet_somutluk_skoru"] > 0, prepared["ozet_kalite_kontrol"]
assert prepared["ozet_kalite_kontrol"].get("somutluk_skoru_yeniden_hesaplandi") is True

inflated_without_evidence = [
    {"ad": "tema 1", "tema_gucu": 95, "farkli_sayfa_sayisi": 0, "kanitlar": []},
    {"ad": "tema 2", "tema_gucu": 92, "farkli_sayfa_sayisi": 0, "kanitlar": []},
    {"ad": "tema 3", "tema_gucu": 90, "farkli_sayfa_sayisi": 0, "kanitlar": []},
]
evidence_backed = [
    {"ad": "kararlılık", "tema_gucu": 92, "farkli_sayfa_sayisi": 7, "kanit_guvenilirlik_skoru": 88, "kanitlar": [{"alinti": "x"}]},
    {"ad": "keşif", "tema_gucu": 84, "farkli_sayfa_sayisi": 6, "kanit_guvenilirlik_skoru": 82, "kanitlar": [{"alinti": "x"}]},
    {"ad": "dayanışma", "tema_gucu": 70, "farkli_sayfa_sayisi": 4, "kanit_guvenilirlik_skoru": 72, "kanitlar": [{"alinti": "x"}]},
]
assert _theme_quality_score(evidence_backed) > _theme_quality_score(inflated_without_evidence)
assert _theme_quality_score(inflated_without_evidence) < 80

kolomb_themes = [
    {"ad": "kararlılık", "tema_gucu": 99, "farkli_sayfa_sayisi": 7, "kanit_sayisi": 6, "kanit_guvenilirlik_skoru": 88, "kanitlar": [{"alinti": "Kolomb yolculuğa devam etme kararı verdi."}]},
    {"ad": "keşif", "tema_gucu": 95, "farkli_sayfa_sayisi": 6, "kanit_sayisi": 6, "kanit_guvenilirlik_skoru": 84, "kanitlar": [{"alinti": "Yeni bir deniz rotası keşfetmek için yola çıktı."}]},
    {"ad": "dayanışma", "tema_gucu": 76, "farkli_sayfa_sayisi": 5, "kanit_sayisi": 5, "kanit_guvenilirlik_skoru": 74, "kanitlar": [{"alinti": "Mürettebat zor koşullarda birlikte çalıştı."}]},
]
kolomb_context = {
    "book_type": "tarihî biyografi",
    "kitap_ozeti": summary,
}
kolomb_theme_quality = _theme_quality_score(kolomb_themes, kolomb_context)
kolomb_top_average = sum(item["tema_gucu"] for item in kolomb_themes) / 3
assert kolomb_theme_quality >= 80, kolomb_theme_quality
assert kolomb_theme_quality >= kolomb_top_average - 25, (kolomb_theme_quality, kolomb_top_average)

shallow_characters = [
    {"ad": "Kristof Kolomb", "ana_karakter_mi": True, "guven_skoru": 0.7},
] + [{"ad": f"Yan Kişi {index}", "guven_skoru": 0.5} for index in range(1, 8)]
quality = {"gecerli": True, "skor": 85}
assert _character_depth_score({}, shallow_characters, quality) < 90

scores = _report_scores({
    "tema_analizi": evidence_backed,
    "ana_karakterler": shallow_characters,
    "karakter_kalite_degerlendirmesi": quality,
})
assert scores["Tema Kalitesi"] == _theme_quality_score(evidence_backed, {
    "tema_analizi": evidence_backed,
    "ana_karakterler": shallow_characters,
    "karakter_kalite_degerlendirmesi": quality,
}), scores
assert scores["Karakter Derinliği"] < 90, scores

kolomb_report_payload = {
    "book_type": "tarihî biyografi",
    "kitap_ozeti": summary,
    "tema_analizi": kolomb_themes,
    "ilk_uc_baskin_tema": kolomb_themes,
    "ana_karakterler": shallow_characters,
    "karakter_kalite_degerlendirmesi": quality,
}
central_theme_quality = _central_quality_metrics(kolomb_report_payload)["Tema Kalitesi"]
reliability_theme_quality = _analysis_reliability_components(kolomb_report_payload)["Tema Kalitesi"]
assert central_theme_quality >= 80, central_theme_quality
assert reliability_theme_quality == central_theme_quality, (
    reliability_theme_quality,
    central_theme_quality,
)

clean_flow_summary = (
    "Mert sabah okul bahcesinde arkadaslariyla bulusur ve kaybolan defter icin birlikte arama baslatir, cunku defterde sinif calismasi icin gerekli notlar vardir. "
    "Ayse sinifta onceki konusmalari hatirlatir, bu nedenle grup kimin nerede oldugunu sirayla degerlendirir ve kimseyi aceleyle suclamadan ilerler. "
    "Ogretmen cocuklari dikkatle dinler, yanlis suclama yapmadan ipuclari toplamalarini, sakin kalmalarini ve her ayrintiyi birlikte kontrol etmelerini ister. "
    "Arama ilerledikce Mert kendi dalginligini fark eder, arkadaslarindan yardim isteyerek sorumlulugu paylasir ve onceki davranisini daha dikkatli dusunur. "
    "Sonunda defter dolaplarin arasinda bulunur, grup hem birlikte hareket etmenin hem de acele karar vermemenin sonucunu acik bicimde gorur. "
    "Bu gelisme karakterlerin birbirini dinleyerek daha dengeli karar alabildigini, sorunu buyutmeden cozum kurabildigini ve ortak hareket edebildigini gosterir."
)
unrelated_event_graph = [
    {
        "page": index + 1,
        "sayfa": index + 1,
        "actor": f"Kisi{index}",
        "actors": [f"Kisi{index}"],
        "action": f"benzersiz_eylem_{index}",
        "evidence": f"Kisi{index} benzersiz_eylem_{index} ile tamamen farkli bir sahnede ilerler.",
        "source_sentence_id": f"event-{index}",
    }
    for index in range(8)
]
clean_flow_gate = _apply_summary_quality_gate({
    "kitap_ozeti": clean_flow_summary,
    "summary": clean_flow_summary,
    "ozet_guven_skoru": 0.9,
    "event_graph": unrelated_event_graph,
    "olay_akisi": [{"metin": sentence.strip() + "."} for sentence in clean_flow_summary.split(".")[:5] if sentence.strip()],
    "ana_karakterler": [{"ad": "Mert", "guven_skoru": 0.8}],
    "ozet_kalite_kontrol": {"summary_kind": "clean_event_flow"},
})
clean_quality = clean_flow_gate["ozet_kalite_kontrol"]
assert clean_quality["evidence_coverage"] < 0.50, clean_quality
assert "evidence_coverage_dusuk" not in clean_quality["manual_review_reasons"], clean_quality
assert "quality_warning:evidence_coverage_dusuk" in clean_quality["quality_warnings"], clean_quality
assert clean_quality["quality_warning"] is True, clean_quality
assert clean_quality["manuel_inceleme"] is not True, clean_quality

repeated_metrics = _summary_quality_gate_metrics(
    "Mert defteri arar. Mert defteri arar. Mert defteri arar. Ayse sinifta bekler.",
    {"event_graph": unrelated_event_graph[:3]},
    [],
)
diverse_metrics = _summary_quality_gate_metrics(
    "Mert defteri arar. Ayse sinifta bekler. Ogretmen cocuklari dinler. Grup sonunda defteri bulur.",
    {"event_graph": unrelated_event_graph[:3]},
    [],
)
assert repeated_metrics["repeated_sentence_ratio"] > 0.15, repeated_metrics
assert repeated_metrics["narrative_quality_score"] < diverse_metrics["narrative_quality_score"], (
    repeated_metrics,
    diverse_metrics,
)

weak_narrative = narrative_realize("Zayif", [], [], min_kelime=120)
assert unicodedata.normalize("NFC", weak_narrative) == weak_narrative

abstract_connector_audit = kitap_tutarlilik_denetimi({
    "kitap_adi": "Soyut Baglayici",
    "kitap_ozeti": "Karakterler aynı hedef etrafında toplanıp birlikte çözüm arar.",
    "summary": "Karakterler aynı hedef etrafında toplanıp birlikte çözüm arar.",
    "olay_akisi": [
        {"sayfa": 1, "metin": "Karakterler sorunu birlikte çözmek için dayanışma içinde hareket eder."},
    ],
})
assert abstract_connector_audit["unsupported_events"] == [], abstract_connector_audit

unsupported_abstract_audit = kitap_tutarlilik_denetimi({
    "kitap_adi": "Soyut Baglayici",
    "kitap_ozeti": "Karakterler gizli saray hedefini ele geçirir.",
    "summary": "Karakterler gizli saray hedefini ele geçirir.",
    "olay_akisi": [
        {"sayfa": 1, "metin": "Karakterler sorunu birlikte çözmek için dayanışma içinde hareket eder."},
    ],
})
assert any(
    "gizli saray hedefini ele geçirir" in item
    for item in unsupported_abstract_audit["unsupported_events"]
), unsupported_abstract_audit

for bridge_summary in [
    "Karakterler çözüm için yeniden bir araya gelir.",
    "Böylece önceki bilgi boşa kalmaz.",
    "Karakterler öğrendiklerini kullanarak karar verir.",
]:
    bridge_audit = kitap_tutarlilik_denetimi({
        "kitap_adi": "Bridge Validator",
        "kitap_ozeti": bridge_summary,
        "summary": bridge_summary,
        "olay_akisi": [
            {"sayfa": 1, "metin": "Aydın Öğretmen öğrencileriyle çözüm arar ve karakterler birlikte hareket eder."},
            {"sayfa": 2, "metin": "Karakterler yeni bilgiyi öğrenir ve sorunu çözmek için konuşur."},
        ],
    })
    assert bridge_audit["unsupported_events"] == [], bridge_audit

unsupported_new_event_audit = kitap_tutarlilik_denetimi({
    "kitap_adi": "Bridge Validator",
    "kitap_ozeti": "Karakterler gizli saraya giderek büyülü tacı ele geçirir.",
    "summary": "Karakterler gizli saraya giderek büyülü tacı ele geçirir.",
    "olay_akisi": [
        {"sayfa": 1, "metin": "Aydın Öğretmen öğrencileriyle çözüm arar ve karakterler birlikte hareket eder."},
    ],
})
assert any(
    "gizli saraya giderek büyülü tacı ele geçirir" in item
    for item in unsupported_new_event_audit["unsupported_events"]
), unsupported_new_event_audit

diversity_summary = narrative_realize("Cesitli Anlatim", [
    {"scene_id": "D1", "page": 1, "actor": "Yılanson", "actors": ["Yılanson"], "action": "buluş sunmak", "evidence": "Yılanson yeni buluşunu anlatır."},
    {"scene_id": "D2", "page": 2, "actor": "Dankof Oburof", "actors": ["Dankof Oburof"], "action": "buluş açıklamak", "evidence": "Dankof Oburof yeni buluşunu açıklar."},
    {"scene_id": "D3", "page": 3, "actor": "Yasemin", "actors": ["Yasemin"], "action": "çözüm aramak", "evidence": "Yasemin arkadaşlarıyla birlikte çözüm arar."},
], [], min_kelime=20)
assert _fold_text(diversity_summary).count("bu aciklamayla tehlikeyi somutlastirir") <= 1, diversity_summary

cleanup_sample = (
    "Bu baski halkin tepkisini artirir; Kapgotur bu tepkinin kaynagini anlamak icin "
    "cevresindeki isaretleri izlemeye baslar, yonetimin yarattigi sikintiyi gorur ve "
    "aciklamayla anlatilan bulus karsidaki riski aciga cikarir."
)
cleaned_sample = final_turkish_cleanup(cleanup_sample)
for expected in [
    "baskı", "halkın", "artırır", "Kapgötür", "kaynağını", "için",
    "çevresindeki", "işaretleri", "başlar", "yönetimin", "yarattığı",
    "sıkıntıyı", "görür", "açıklamayla", "anlatılan", "buluş",
    "karşıdaki", "açığa", "çıkarır",
]:
    assert expected in cleaned_sample, cleaned_sample

abstract_penalty_metrics = _summary_quality_gate_metrics(
    "Kapgötür halkla arasındaki uzaklığı görür. Bu durum olayların yönünü belirler. Kapgötür sonraki adımını buna göre kurar.",
    {"event_graph": unrelated_event_graph[:3]},
    [],
)
clean_direct_metrics = _summary_quality_gate_metrics(
    "Kapgötür halkın tepkisini anlamaya çalışır. Karakterler birlikte çözüm arar. Yeni bilgi karakterleri harekete geçirir.",
    {"event_graph": unrelated_event_graph[:3]},
    [],
)
assert abstract_penalty_metrics["abstract_sentence_penalty"] > 0, abstract_penalty_metrics
assert abstract_penalty_metrics["narrative_quality_score"] < clean_direct_metrics["narrative_quality_score"], (
    abstract_penalty_metrics,
    clean_direct_metrics,
)

floor_summary = (
    "Mert okul bahçesinde kaybolan defteri aramaya başlar. Ayşe sınıfta önceki konuşmaları hatırlatır. "
    "Öğretmen çocukları dinler ve sakin kalmalarını ister. Grup ipuçlarını sırayla kontrol eder. "
    "Mert kendi dalgınlığını fark eder ve arkadaşlarından destek ister. Sonunda defter dolapların arasında bulunur. "
    "Bu süreçte kişiler birbirini dinler, acele suçlama yapmaz ve sorunu büyütmeden ortak bir yol kurar. "
    "Olay çizgisi defter arayışı, dikkatli düşünme ve arkadaş desteği etrafında temiz biçimde ilerler. "
    "Anlatım, metindeki olay sırasına bağlı kalır ve yeni kişi ya da yeni mekân eklemeden tamamlanır. "
    "Her gelişme önceki sahneyle ilişkili kalır; çocuklar konuşarak, dinleyerek ve sırayla kontrol ederek sonuca ulaşır. "
    "Bu yüzden özet hem olayları korur hem de gereksiz yorum eklemeden defterin bulunmasına giden süreci açık tutar."
)
floor_event_graph = [
    {"page": 1, "actors": ["Mert"], "action": "aramaya başlar", "evidence": "Mert okul bahçesinde kaybolan defteri aramaya başlar."},
    {"page": 2, "actors": ["Ayşe"], "action": "hatırlatır", "evidence": "Ayşe sınıfta önceki konuşmaları hatırlatır."},
    {"page": 3, "actors": ["Öğretmen"], "action": "dinler", "evidence": "Öğretmen çocukları dinler ve sakin kalmalarını ister."},
    {"page": 4, "actors": ["Grup"], "action": "kontrol eder", "evidence": "Grup ipuçlarını sırayla kontrol eder."},
    {"page": 5, "actors": ["Mert"], "action": "fark eder", "evidence": "Mert kendi dalgınlığını fark eder ve arkadaşlarından destek ister."},
]
floor_metrics = _summary_quality_gate_metrics(
    floor_summary,
    {"event_graph": floor_event_graph, "olay_akisi": [{"metin": item["evidence"]} for item in floor_event_graph]},
    [],
)
assert len(floor_summary.split()) >= 110, len(floor_summary.split())
assert floor_metrics["quality_floor_applied"] is True, floor_metrics
assert floor_metrics["narrative_quality_score"] >= 0.65, floor_metrics
