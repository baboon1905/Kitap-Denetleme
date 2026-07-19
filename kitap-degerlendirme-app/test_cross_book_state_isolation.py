from theme_gain_analysis import (
    _apply_summary_quality_gate,
    _build_book_summary_v2,
    _build_safe_limited_summary,
    _cross_book_context_audit,
    _extract_event_graph,
    _fold_text,
    build_canonical_entity_store,
    detect_book_subtype,
    detect_book_type,
    extract_entity_graph,
    rapor_kalite_kapisi,
    build_teacher_report_payload,
    classify_entity_type,
    sanitize_character_profiles,
)


manual_payload = {
    "kitap_adi": "Yeni Kitap",
    "kitap_ozeti": (
        "Giris:\nMert okulda bir karar verir.\n\n"
        "Gelisme:\nOlaylar okulda ilerler.\n\n"
        "Temel Catisma:\nMert zor bir secimle karsilasir.\n\n"
        "Karakter Iliskileri:\nAilesi ona destek olur.\n\n"
        "Genel Sonuc:\nMert deneyiminden ders cikarir."
    ),
    "ana_karakterler": [],
}

manual_audit = _cross_book_context_audit(
    manual_payload,
    "Ali'nin yeni bir sorumluluk aldigi anlatilir.",
    "Ali'nin kararlarini yeniden degerlendirdigi soylenir.",
)
assert manual_audit["gecerli"] is True, manual_audit
assert manual_audit["manuel_inceleme"] is True, manual_audit
assert "ali" in manual_audit["illegal_summary_names"], manual_audit
assert manual_audit["uyarilar"], manual_audit

verified_payload = {
    **manual_payload,
    "ana_karakterler": [{"ad": "Mert", "guven_skoru": 0.9, "ana_karakter_mi": True, "entity_type": "PERSON"}],
}

leak_audit = _cross_book_context_audit(
    verified_payload,
    "Ali'nin yeni bir sorumluluk aldigi anlatilir.",
    "Ali'nin kararlarini yeniden degerlendirdigi soylenir.",
)
assert leak_audit["gecerli"] is False, leak_audit
assert "ali" in leak_audit["illegal_summary_names"], leak_audit
assert leak_audit["verified_characters"] == ["mert"], leak_audit

case_payload = {
    "kitap_adi": "Deneme",
    "kitap_ozeti": (
        "Giris:\nAli okulda karar verir.\n\n"
        "Gelisme:\nAli ailesiyle konusur.\n\n"
        "Temel Catisma:\nAli zorlanir.\n\n"
        "Karakter Iliskileri:\nAli destek alir.\n\n"
        "Genel Sonuc:\nAli ders cikarir."
    ),
    "ana_karakterler": [{"ad": "ALİ", "guven_skoru": 0.9, "ana_karakter_mi": True, "entity_type": "PERSON"}],
    "olay_akisi": [
        {"sayfa": 1, "metin": "Ali okulda karar verir ve ailesiyle konusur."},
    ],
    "cache_key": "test-cache",
}
case_audit = _cross_book_context_audit(
    case_payload,
    "Ali'nin karari anlatilir.",
    "ali'nin davranisi tartisilir.",
)
assert case_audit["gecerli"] is True, case_audit
assert case_audit["illegal_summary_names"] == [], case_audit
assert "ali" in case_audit["verified_characters_normalized"], case_audit
assert "ali" in case_audit["summary_names_normalized"], case_audit

heading_noise_payload = {
    "kitap_adi": "Büyülü Yastıklar",
    "kitap_ozeti": (
        "Giris:\nYasemin Olaylar ilerledikce kararlarini yeniden degerlendirir.\n\n"
        "Gelisme:\nYasemin arkadaslariyla konusur.\n\n"
        "Temel Catisma:\nYasemin zor bir durumla karsilasir.\n\n"
        "Karakter Iliskileri:\nYasemin ve Aydin Ogretmen birlikte hareket eder.\n\n"
        "Genel Sonuc:\nYasemin olaylardan ders cikarir."
    ),
    "ana_karakterler": [{"ad": "Yasemin", "guven_skoru": 0.9, "ana_karakter_mi": True, "entity_type": "PERSON"}],
    "olay_akisi": [{"sayfa": 1, "metin": "Yasemin olaylar ilerledikce kararlarini yeniden degerlendirir."}],
}
heading_noise_audit = _cross_book_context_audit(
    heading_noise_payload,
    "Yasemin olaylar ilerledikce kararlarini yeniden degerlendirir.",
    "Yasemin ve Aydin Ogretmen birlikte hareket eder.",
)
assert "yasemin olaylar" not in heading_noise_audit["illegal_summary_names"], heading_noise_audit
assert "yasemin olaylar" not in heading_noise_audit["summary_names_normalized"], heading_noise_audit

canonical_place_graph = extract_entity_graph("Yasemin Hüzün Denizi kıyısında bekledi.")
canonical_place_payload = {
    "kitap_adi": "Entity Validator",
    "kitap_ozeti": "Yasemin kıyıda bekler.",
    "ana_karakterler": [{"ad": "Yasemin", "guven_skoru": 0.9, "ana_karakter_mi": True, "entity_type": "PERSON"}],
    "entity_store_graph": canonical_place_graph,
    "canonical_entity_store": build_canonical_entity_store(canonical_place_graph),
    "olay_akisi": [{"sayfa": 1, "metin": "Yasemin Hüzün Denizi kıyısında bekledi."}],
}
canonical_place_audit = _cross_book_context_audit(
    canonical_place_payload,
    "Yasemin Deniz kıyısındaki durumu değerlendirir.",
    "",
)
assert "denizi" not in canonical_place_audit["unsupported_locations"], canonical_place_audit
assert "deniz" in canonical_place_audit["unsupported_locations"], canonical_place_audit
canonical_place_match_audit = _cross_book_context_audit(
    canonical_place_payload,
    "Yasemin Hüzün Denizi kıyısındaki durumu değerlendirir.",
    "",
)
assert "deniz" not in canonical_place_match_audit["unsupported_locations"], canonical_place_match_audit

fantasy_story_text = (
    "--- SAYFA 1 ---\n"
    "Yazar biyografisi: Yazar bilimsel arastirmalar yapmis, universitede calismis ve bu kitap telif haklariyla korunmustur. ISBN 978-1-000.\n"
    "--- SAYFA 2 ---\n"
    "Bolum 1. Kral Kapgötür, Gökistan ülkesinde düşleri saklayan yastıkları topladı. Yasemin, Aydın Öğretmen'e \"Karabasanlar yine geldi\" dedi.\n"
    "--- SAYFA 3 ---\n"
    "Lanson Yılanson ve Dankof Oburof sarayın kapısında tartıştı. Zilius Rezilius büyülü yastığı görünce planını değiştirdi.\n"
    "--- SAYFA 4 ---\n"
    "Yasemin düşlerin neden karardığını araştırdı ve Aydın Öğretmen ona yardım etti. Kral, ülkenin eski neşesini bulması için herkesi topladı.\n"
)
fantasy_type = detect_book_type(fantasy_story_text, {"kitap_adi": "Büyülü Yastıklar"})
fantasy_subtype = detect_book_subtype(fantasy_story_text, {"kitap_adi": "Büyülü Yastıklar"}, fantasy_type)
assert fantasy_type == "kurgu çocuk öyküsü", fantasy_type
assert fantasy_subtype == "fantastik / mizahi çocuk anlatısı", fantasy_subtype

science_text = (
    "--- SAYFA 1 ---\n"
    "Gezegenler ve yıldızlar hakkında temel bilim bilgisi sunulur. Bu bölüm gök cisimlerinin ne olduğunu açıklar.\n"
    "--- SAYFA 2 ---\n"
    "Deney ve gözlem, bilimsel düşünmenin iki önemli yoludur. Örneğin bir cismin hareketi ölçülerek sonuçlar karşılaştırılır.\n"
    "--- SAYFA 3 ---\n"
    "Sonuç olarak teknoloji, araştırma ve kavram bilgisi günlük yaşamda doğayı anlamaya yardımcı olur.\n"
)
science_type = detect_book_type(science_text, {"kitap_adi": "Bilim Defteri"})
assert science_type == "bilimsel içerik", science_type

assert classify_entity_type("Majesteleri") == "HONORIFIC"
assert classify_entity_type("Efendimiz") == "HONORIFIC"
assert classify_entity_type("Yüce Kralımız") == "TITLE"
assert classify_entity_type("Buyrun") == "HONORIFIC"
assert classify_entity_type("Evet") == "HONORIFIC"
assert classify_entity_type("Hayır") == "HONORIFIC"
assert classify_entity_type("Peki") == "HONORIFIC"
assert classify_entity_type("Kralımız") == "TITLE"
assert classify_entity_type("Öğretmenim") == "TITLE"
assert classify_entity_type("Başbüyücü") == "TITLE"
assert classify_entity_type("Geceleri") == "zaman"
assert classify_entity_type("Sabah") == "zaman"
assert classify_entity_type("Okulda") == "PLACE"
assert classify_entity_type("Deniz") == "PLACE_FRAGMENT"
assert classify_entity_type("Kral Kapgötür") == "PERSON"
assert classify_entity_type("Aydın Öğretmen") == "PERSON"
assert classify_entity_type("Hüzün Denizi") == "PLACE"
assert classify_entity_type("Ellerimiz Yüce Kralımız") == "TITLE"

span_entities = extract_entity_graph("Yasemin Hüzün Denizi kıyısında bekledi.")
span_places = [entity for entity in span_entities if entity["entity_type"] == "PLACE"]
span_people = [entity for entity in span_entities if entity["entity_type"] == "PERSON"]
assert [entity["canonical_form"] for entity in span_places] == ["Hüzün Denizi"], span_entities
assert all(entity["canonical_form"] != "Deniz" for entity in span_entities), span_entities
assert span_people == ["Yasemin"] or [entity["canonical_form"] for entity in span_people] == ["Yasemin"], span_entities

title_entities = extract_entity_graph("Yüce Kralımız salona girdi.")
assert any(entity["entity_type"] == "TITLE" and entity["canonical_form"] == "Yüce Kralımız" for entity in title_entities), title_entities
assert not any(entity["entity_type"] == "PERSON" for entity in title_entities), title_entities

mixed_entities = extract_entity_graph("Ellerimiz Yüce Kralımız Kral Kapgötür için açıldı.")
assert any(entity["entity_type"] == "PERSON" and entity["canonical_form"] == "Kral Kapgötür" for entity in mixed_entities), mixed_entities
assert not any(entity["entity_type"] == "PERSON" and "Yüce" in entity["canonical_form"] for entity in mixed_entities), mixed_entities

canonical_store = build_canonical_entity_store(span_entities)
canonical_place = next(item for item in canonical_store.values() if item["entity_type"] == "PLACE")
assert canonical_place["canonical_form"] == "Hüzün Denizi", canonical_store

entity_resolver_characters = sanitize_character_profiles([
    {"ad": "Majesteleri", "guven_skoru": 0.9},
    {"ad": "Efendimiz", "guven_skoru": 0.9},
    {"ad": "Yüce Kralımız", "guven_skoru": 0.9},
    {"ad": "Buyrun", "guven_skoru": 0.9},
    {"ad": "Evet", "guven_skoru": 0.9},
    {"ad": "Hayır", "guven_skoru": 0.9},
    {"ad": "Peki", "guven_skoru": 0.9},
    {"ad": "Kralımız", "guven_skoru": 0.9},
    {"ad": "Öğretmenim", "guven_skoru": 0.9},
    {"ad": "Başbüyücü", "guven_skoru": 0.9},
    {"ad": "Geceleri", "guven_skoru": 0.9},
    {"ad": "Sabah", "guven_skoru": 0.9},
    {"ad": "Okulda", "guven_skoru": 0.9},
    {"ad": "Deniz", "guven_skoru": 0.9},
    {"ad": "Kral Kapgötür", "guven_skoru": 0.9},
    {"ad": "Aydın Öğretmen", "guven_skoru": 0.9},
    {"ad": "Yasemin", "guven_skoru": 0.9},
    {"ad": "Lanson Yılanson", "guven_skoru": 0.9},
    {"ad": "Dankof Oburof", "guven_skoru": 0.9},
    {"ad": "Zilius Rezilius", "guven_skoru": 0.9},
], limit=12)
entity_resolver_names = {character["ad"] for character in entity_resolver_characters}
assert entity_resolver_names == {
    "Kral Kapgötür",
    "Aydın Öğretmen",
    "Yasemin",
    "Lanson Yılanson",
    "Dankof Oburof",
    "Zilius Rezilius",
}, entity_resolver_characters

pipeline_summary_gate = rapor_kalite_kapisi({
    "kitap_adi": "Pipeline Dili Testi",
    "kitap_ozeti": (
        "Giriş:\nOlay adımı 2 metinde açıkça görünüyor.\n\n"
        "Gelişme:\nOlay zincirinde bir sonraki adıma geçiş hazırlanır.\n\n"
        "Temel Çatışma:\nÖnceki olayda ortaya çıkan durum yeni bir olay adımını gerekli kılar.\n\n"
        "Karakter İlişkileri:\nBaşlangıç durumu karakteri harekete geçirir.\n\n"
        "Genel Sonuç:\nÇatışmanın belirginleşmesi rapora sızmıştır."
    ),
    "ana_karakterler": [{"ad": "Mert", "guven_skoru": 0.9, "ana_karakter_mi": True, "entity_type": "PERSON"}],
    "tema_analizi": [],
    "ilk_uc_baskin_tema": [],
})
assert pipeline_summary_gate["gecerli"] is True, pipeline_summary_gate
assert pipeline_summary_gate["hatalar"] == [], pipeline_summary_gate

new_forbidden_summary_gate = rapor_kalite_kapisi({
    "kitap_adi": "Soyut Anlati Dili Testi",
    "kitap_ozeti": (
        "Giriş:\nNarin araştırır. Bu aşamada anlatı ilerler.\n\n"
        "Gelişme:\nNarin mesajı dinler. Olaylar gelişir.\n\n"
        "Temel Çatışma:\nNarin ipucunu okur. Olay zinciri yeni yön kazanır.\n\n"
        "Karakter İlişkileri:\nNarin arkadaşıyla konuşur. Karakter harekete geçer.\n\n"
        "Genel Sonuç:\nNarin kararını uygular. Çözüm görünür olur."
    ),
    "ana_karakterler": [{"ad": "Narin", "guven_skoru": 0.9, "ana_karakter_mi": True, "entity_type": "PERSON"}],
    "tema_analizi": [],
    "ilk_uc_baskin_tema": [],
})
assert new_forbidden_summary_gate["gecerli"] is True, new_forbidden_summary_gate
assert new_forbidden_summary_gate["hatalar"] == [], new_forbidden_summary_gate


summary_level_gate_payload = {
    "kitap_adi": "Ozet Duzeyi Kalite Testi",
    "kitap_ozeti": (
        "Giris:\n"
        "Bu ozet Narin karakterinin merakini ve karar verme surecini tanitir. "
        "Metin, karakterin degisen bakisini sakin bir cercevede kurar. "
        "Okur, kahramanin giderek daha dikkatli dusundugunu sezer.\n\n"
        "Gelisme:\n"
        "Narin bahcede kilitli sandigi arastirdi ve eski notu buldu. "
        "Narin kutuphanede haritayi inceledi ve gizli isareti karsilastirdi. "
        "Bu gelisme, onun arayisi planli bicimde surdurdugunu gosterir.\n\n"
        "Temel Catisma:\n"
        "Narin koridorda mesaji dinledi ve yanlis anlasilmayi fark etti. "
        "Sandik kapali kaldigi icin kararini yeniledi. "
        "Arastirma, not, harita, mesaj, sandik ve karar ayni sorun etrafinda toplanir.\n\n"
        "Karakter Iliskileri:\n"
        "Narin karakterinin cevresiyle kurdugu bag, onun aceleci davranmamasini saglar. "
        "Aile destegi, kahramanin yalniz olmadigini hissettirir. "
        "Bu iliski agi yeni bir eylem anlatmadan karakterin tutumunu aciklar.\n\n"
        "Genel Sonuc:\n"
        "Yasananlarin ardindan Narin, gorduklerini daha dikkatli yorumlar. "
        "Son bolum, yeni bir olay eklemekten cok karakterdeki degisimi tamamlar. "
        "Ozet, dogrulanmis olaylari genel bir degerlendirmeyle kapatir."
    ),
    "event_graph": [
        {
            "page": 1,
            "actors": ["Narin"],
            "action": "arastirdi",
            "evidence": "Narin bahcede kilitli sandigi arastirdi ve eski notu buldu.",
            "source_sentence_id": "p1:s1",
        },
        {
            "page": 2,
            "actors": ["Narin"],
            "action": "inceledi",
            "evidence": "Narin kutuphanede haritayi inceledi ve gizli isareti karsilastirdi.",
            "source_sentence_id": "p2:s1",
        },
        {
            "page": 3,
            "actors": ["Narin"],
            "action": "dinledi",
            "evidence": "Narin koridorda mesaji dinledi ve yanlis anlasilmayi fark etti.",
            "source_sentence_id": "p3:s1",
        },
    ],
    "ozet_kalite_kontrol": {},
}
summary_level_gate = _apply_summary_quality_gate(summary_level_gate_payload)
summary_level_quality = summary_level_gate["ozet_kalite_kontrol"]
assert summary_level_quality["verified_event_count"] == 3, summary_level_quality
assert summary_level_quality["event_source_page_count"] == 3, summary_level_quality
assert summary_level_quality["evidence_coverage"] >= 0.50, summary_level_quality
assert summary_level_quality["manual_review_reasons"] == [], summary_level_quality
assert summary_level_quality.get("manuel_inceleme") is not True, summary_level_quality
assert "olay_bolumlerinde_somut_olay_yok" not in summary_level_quality["fail_sebepleri"], summary_level_quality

weak_summary_level_gate = _apply_summary_quality_gate({
    **summary_level_gate_payload,
    "event_graph": summary_level_gate_payload["event_graph"][:2],
})
assert weak_summary_level_gate["ozet_kalite_kontrol"]["manuel_inceleme"] is False, weak_summary_level_gate
assert weak_summary_level_gate["ozet_kalite_kontrol"]["summary_kind"] == "safe_limited", weak_summary_level_gate
weak_summary_text = _fold_text(weak_summary_level_gate["kitap_ozeti"])
for expected_fragment in ["guven", "narin", "metinden", "kesin yorum yapilmaz"]:
    assert expected_fragment in weak_summary_text, weak_summary_level_gate
assert 50 <= len(weak_summary_level_gate["kitap_ozeti"].split()) <= 140, weak_summary_level_gate
assert "dogrulanmis_olay_yetersiz" in weak_summary_level_gate["ozet_kalite_kontrol"]["safe_limited_original_manual_review_reasons"], weak_summary_level_gate
weak_teacher_payload = build_teacher_report_payload(weak_summary_level_gate)
assert weak_teacher_payload["kisa_ogretmen_ozeti"].startswith("Sınırlı güvenilirlik:"), weak_teacher_payload

safe_entity_summary = _build_safe_limited_summary({
    "kitap_adi": "Entity Güvenliği",
    "ana_karakterler": [
        {"ad": "Majesteleri", "guven_skoru": 0.9},
        {"ad": "Buyrun", "guven_skoru": 0.9},
        {"ad": "Yasemin", "guven_skoru": 0.9},
        {"ad": "Deniz", "guven_skoru": 0.9},
    ],
    "event_graph": [
        {
            "actors": ["Majesteleri", "Yasemin", "Buyrun"],
            "actor": "Majesteleri",
            "action": "gördü",
            "object": "Buyrun",
            "location": "okul çevresi",
            "consequence": "Yasemin durumu fark etti",
            "evidence": "Yasemin yastığı gördü ve Yasemin durumu fark etti.",
        },
        {
            "actors": ["Deniz", "Yasemin"],
            "actor": "Deniz",
            "action": "verdi",
            "location": "okula",
            "evidence": "Yasemin okula doğru yürüdü.",
        }
    ],
})
assert "Yasemin" in safe_entity_summary, safe_entity_summary
assert "Majesteleri" not in safe_entity_summary, safe_entity_summary
assert "Buyrun" not in safe_entity_summary, safe_entity_summary
assert "Deniz" not in safe_entity_summary, safe_entity_summary
assert "okul çevresi" not in safe_entity_summary, safe_entity_summary
assert "okula çevresinde" not in safe_entity_summary, safe_entity_summary
assert "mekân bilgisi okula" not in safe_entity_summary, safe_entity_summary

unsafe_empty_gate = _apply_summary_quality_gate({
    "kitap_adi": "Kanitsiz Ozet Testi",
    "kitap_ozeti": "Özet güvenilir üretilemedi.",
    "event_graph": [],
    "ana_karakterler": [],
    "ozet_kalite_kontrol": {},
})
assert unsafe_empty_gate["ozet_guven_skoru"] == 0.0, unsafe_empty_gate
assert "güvenilir" in unsafe_empty_gate["kitap_ozeti"].casefold() or "gÃ¼venilir" in unsafe_empty_gate["kitap_ozeti"].casefold(), unsafe_empty_gate


theme_independent_records = [
    {"sayfa": 1, "metin": "Narin sabah bahcede kilitli kapinin neden acilmadigini arastirdi ve ilk ipucunu not etti."},
    {"sayfa": 2, "metin": "Narin arkadasindan gelen mesaji dinledi, acele etmeden taslarin yerini karsilastirdi."},
    {"sayfa": 3, "metin": "Narin son ipucunu okuyunca kapinin nasil acilacagini anladi ve kararini uyguladi."},
]
theme_independent_summary = _build_book_summary_v2(
    "\n".join(f"--- SAYFA {item['sayfa']} ---\n{item['metin']}" for item in theme_independent_records),
    theme_independent_records,
    [],
    {"kitap_adi": "Olay Zinciri Testi", "yazar": "Test"},
    "standart",
)
assert theme_independent_summary["ozet_kalite_kontrol"]["guvenilir_uretilemedi"] is False, theme_independent_summary
assert theme_independent_summary["ozet_kalite_kontrol"]["event_scene_count"] >= 3, theme_independent_summary
assert theme_independent_summary["ozet_kalite_kontrol"]["verified_character_count"] >= 1, theme_independent_summary
assert theme_independent_summary["ozet_kalite_kontrol"]["direct_quote_overlap_ratio"] <= 0.10, theme_independent_summary
assert theme_independent_summary["ozet_kalite_kontrol"]["event_graph_node_count"] >= 3, theme_independent_summary
assert theme_independent_summary["ozet_kalite_kontrol"]["event_completeness"] >= 0.80, theme_independent_summary
assert 0.0 <= theme_independent_summary["ozet_guven_skoru"] <= 1.0, theme_independent_summary
assert theme_independent_summary["ozet_kalite_kontrol"]["narrative_quality_score"] >= 0.50, theme_independent_summary
assert len(theme_independent_summary["event_graph"]) >= 3, theme_independent_summary
for node in theme_independent_summary["event_graph"]:
    for key in ["scene_id", "page", "actor", "actors", "action", "object", "consequence", "location", "source_sentence_id"]:
        assert key in node, node
    assert node.get("evidence") or node.get("evidence_sentence"), node
    assert node["action"], node
    assert len(node["action"].split()) >= 2, node
    assert _fold_text(node["action"]) not in {"vermek", "yapmak", "almak", "bulmak"}, node
    assert node.get("action_source") or node.get("action"), node
    assert node["actors"] == ["Narin"], node
    evidence_text = _fold_text(node.get("evidence_sentence") or node.get("evidence") or "")
    if node.get("action_source"):
        assert _fold_text(node["action_source"]) in evidence_text, node
    rendered_event_text = node.get("olay_metni") or node.get("metin") or node.get("action")
    assert rendered_event_text != (node.get("evidence_sentence") or node.get("evidence")), node
for event in theme_independent_summary["olay_akisi"]:
    for key in ["olay_basligi", "neden", "sonuc", "ilgili_karakterler"]:
        assert key in event, event
for source in theme_independent_records:
    assert source["metin"] not in theme_independent_summary["kitap_ozeti"], theme_independent_summary["kitap_ozeti"]
assert "Tema" not in theme_independent_summary["kitap_ozeti"], theme_independent_summary["kitap_ozeti"]
for forbidden in ["anlatı ilerler", "yeni yön kazanır", "bu aşamada", "olaylar gelişir", "karakter harekete geçer", "olay zinciri"]:
    assert forbidden not in theme_independent_summary["kitap_ozeti"].casefold(), theme_independent_summary["kitap_ozeti"]

strict_event_graph = _extract_event_graph(
    [
        {"sayfa": 1, "metin": "Okula gitmeyenler bu zindanlara atiliyorlardi."},
        {"sayfa": 2, "metin": "Narin sabah bahcede kilitli kapinin neden acilmadigini arastirdi."},
    ],
    [{"ad": "Narin", "karakter_adi": "Narin", "guven_skoru": 0.9, "ana_karakter_mi": True, "entity_type": "PERSON"}],
)
assert len(strict_event_graph) == 1, strict_event_graph
assert strict_event_graph[0]["actors"] == ["Narin"], strict_event_graph
assert "araştır" in strict_event_graph[0]["action"], strict_event_graph
assert len(strict_event_graph[0]["action"].split()) >= 2, strict_event_graph
assert _fold_text(strict_event_graph[0]["action_source"]) in _fold_text(strict_event_graph[0]["evidence_sentence"]), strict_event_graph
assert "okur" not in strict_event_graph[0]["action"], strict_event_graph
assert strict_event_graph[0]["source_sentence_id"] == "p2:s2", strict_event_graph

emotion_event_graph = _extract_event_graph(
    [
        {"sayfa": 12, "metin": "Kapgötür kaşlarını çattı ve danışmanlarına nedenini sordu."},
    ],
    [{"ad": "Kral Kapgötür", "karakter_adi": "Kral Kapgötür", "guven_skoru": 0.9, "ana_karakter_mi": True, "entity_type": "PERSON"}],
)
assert len(emotion_event_graph) == 1, emotion_event_graph
assert emotion_event_graph[0]["actors"] == ["Kral Kapgötür"], emotion_event_graph
assert "kaşlarını çat" in emotion_event_graph[0]["action"], emotion_event_graph
assert emotion_event_graph[0]["emotion"] == "öfke", emotion_event_graph
assert emotion_event_graph[0]["consequence"] == "danışmanlarını sorgulamaya başladı", emotion_event_graph
assert emotion_event_graph[0]["olay_metni"] != emotion_event_graph[0]["evidence_sentence"], emotion_event_graph

quote_ratio_gate = _apply_summary_quality_gate({
    "kitap_adi": "Quote Ratio Testi",
    "kitap_ozeti": (
        "Giris:\nKapgötür kaşlarını çattı ve danışmanlarına nedenini sordu. "
        "Kapgötür kaşlarını çattı ve danışmanlarına nedenini sordu. "
        "Kapgötür kaşlarını çattı ve danışmanlarına nedenini sordu.\n\n"
        "Gelisme:\nKapgötür kaşlarını çattı ve danışmanlarına nedenini sordu.\n\n"
        "Temel Catisma:\nKapgötür kaşlarını çattı ve danışmanlarına nedenini sordu.\n\n"
        "Karakter Iliskileri:\nKapgötür kaşlarını çattı ve danışmanlarına nedenini sordu.\n\n"
        "Genel Sonuc:\nKapgötür kaşlarını çattı ve danışmanlarına nedenini sordu."
    ),
    "event_graph": [
        {
            "page": 12,
            "actors": ["Kral Kapgötür"],
            "action": "kaşlarını çatmak",
            "evidence": "Kapgötür kaşlarını çattı ve danışmanlarına nedenini sordu.",
            "evidence_sentence": "Kapgötür kaşlarını çattı ve danışmanlarına nedenini sordu.",
            "source_sentence_id": "p12:s1",
        },
        {
            "page": 13,
            "actors": ["Kral Kapgötür"],
            "action": "sormak",
            "evidence": "Kapgötür kaşlarını çattı ve danışmanlarına nedenini sordu.",
            "evidence_sentence": "Kapgötür kaşlarını çattı ve danışmanlarına nedenini sordu.",
            "source_sentence_id": "p13:s1",
        },
        {
            "page": 14,
            "actors": ["Kral Kapgötür"],
            "action": "sorgulamak",
            "evidence": "Kapgötür kaşlarını çattı ve danışmanlarına nedenini sordu.",
            "evidence_sentence": "Kapgötür kaşlarını çattı ve danışmanlarına nedenini sordu.",
            "source_sentence_id": "p14:s1",
        },
    ],
    "ana_karakterler": [{"ad": "Kral Kapgötür", "guven_skoru": 0.9, "ana_karakter_mi": True, "entity_type": "PERSON"}],
    "ozet_kalite_kontrol": {},
})
assert quote_ratio_gate["ozet_kalite_kontrol"]["quote_ratio"] > 0.20, quote_ratio_gate
assert "quote_ratio_yuksek" in quote_ratio_gate["ozet_kalite_kontrol"]["safe_limited_original_manual_review_reasons"], quote_ratio_gate

assert classify_entity_type("Geceleri") != "PERSON"
assert classify_entity_type("Gökistanlılar") == "GROUP"


kapgotur_characters = sanitize_character_profiles([
    {"ad": "Kapgötür Marşı", "guven_skoru": 0.7, "ana_karakter_mi": True},
    {"ad": "Yüce Kralımız Kapgötür", "guven_skoru": 0.8},
    {"ad": "Kralımız Kapgötür", "guven_skoru": 0.75},
    {"ad": "Başında Kapgötür", "guven_skoru": 0.65},
])
assert len(kapgotur_characters) == 1, kapgotur_characters
assert kapgotur_characters[0]["ad"] == "Kral Kapgötür", kapgotur_characters
aliases = {alias.casefold() for alias in kapgotur_characters[0].get("normalized_aliases", [])}
for expected_alias in ["kapgötür marşı", "yüce kralımız kapgötür", "kralımız kapgötür", "başında kapgötür"]:
    assert expected_alias in aliases, kapgotur_characters


teacher_without_theme = build_teacher_report_payload({
    **theme_independent_summary,
    "kitap_adi": "Olay Zinciri Testi",
    "tema_analizi": [],
    "ilk_uc_baskin_tema": [],
    "guclu_temalar": [],
    "ana_tema": "Yeterli güvenle belirlenemedi.",
})
teacher_text = " ".join(
    str(value)
    for value in teacher_without_theme.values()
    if isinstance(value, (str, list))
)
assert "tema belirlenemedi tem" not in teacher_text.casefold(), teacher_without_theme
assert "olay örgüsü" in teacher_text.casefold() or "karakter" in teacher_text.casefold(), teacher_without_theme
assert teacher_without_theme["ana_tema"] == "Yeterli güvenle belirlenemedi.", teacher_without_theme
