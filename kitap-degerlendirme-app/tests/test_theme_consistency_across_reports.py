from theme_gain_analysis import build_teacher_report_payload


def test_teacher_payload_uses_canonical_theme_from_detailed_report():
    result = {
        "kitap_adi": "Örnek Kitap",
        "yazar": "Yazar",
        "book_type": "çağdaş çocuk romanı",
        "ana_tema": "problem çözme",
        "baskin_tema_ozeti": {
            "ana_tema": {"ad": "problem çözme"},
            "ilk_uc_baskin_tema": [
                {"ad": "problem çözme", "tema_gucu": 92, "guven_skoru": 0.92, "kanit_sayisi": 3},
                {"ad": "söz tutma", "tema_gucu": 88, "guven_skoru": 0.88, "kanit_sayisi": 2},
            ],
        },
        "ilk_uc_baskin_tema": [
            {"ad": "söz tutma", "tema_gucu": 88, "guven_skoru": 0.88, "kanit_sayisi": 2},
            {"ad": "problem çözme", "tema_gucu": 92, "guven_skoru": 0.92, "kanit_sayisi": 3},
        ],
        "tema_analizi": [
            {"ad": "söz tutma", "tema_gucu": 88, "guven_skoru": 0.88, "kanit_sayisi": 2},
            {"ad": "problem çözme", "tema_gucu": 92, "guven_skoru": 0.92, "kanit_sayisi": 3},
        ],
        "kazanim_analizi": [],
        "deger_analizi": [],
        "canonical_summary": "Bu kitapta problem çözme ana tema olarak öne çıkar.",
        "ozet_guven_skoru": 0.9,
        "summary_consistency_audit": {},
    }

    payload = build_teacher_report_payload(result)

    assert payload["ana_tema"] == "problem çözme"
    assert "problem çözme" in payload["kisa_ogretmen_ozeti"]
    assert "söz tutma" not in payload["kisa_ogretmen_ozeti"]
