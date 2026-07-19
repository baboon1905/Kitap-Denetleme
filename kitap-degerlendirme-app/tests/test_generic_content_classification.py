from runtime_v7.adapter import build_v7_shadow_payload


def test_shadow_classification_contains_generic_signal_based_output():
    payload = {
        "kitap_adi": "Bilim Macerası",
        "yazar": "Yazar",
        "canonical_summary": "Bir çocuk laboratuvarda deney yapar, gezegenleri keşfeder ve bilimsel gözlemle bilgi üretir.",
        "kitap_ozeti": "Bir çocuk laboratuvarda deney yapar, gezegenleri keşfeder ve bilimsel gözlemle bilgi üretir.",
        "ana_karakterler": [{"ad": "Ali", "ana_karakter_mi": True}],
        "tema_analizi": [{"ad": "keşif", "tema_gucu": 90, "guven_skoru": 0.9}],
        "kazanim_analizi": [{"ad": "bilimsel düşünme", "tema_gucu": 80, "guven_skoru": 0.8}],
        "deger_analizi": [{"ad": "sorumluluk", "tema_gucu": 70, "guven_skoru": 0.7}],
        "book_type": "bilimsel içerik",
        "book_subtype": "bilgilendirici bilim",
    }

    shadow = build_v7_shadow_payload(payload)
    classification = shadow.get("classification", {})

    assert classification["book_type"]["label"] == "bilim"
    assert classification["book_type"]["confidence"] >= 0.5
    assert classification["book_type"]["evidence_count"] >= 2
    assert classification["book_type"]["supporting_signals"]
    assert classification["content"]["label"] in {"bilim", "değerler eğitimi"}
