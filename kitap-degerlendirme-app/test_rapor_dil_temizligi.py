from theme_gain_analysis import _clean_report_language_text, _weak_match_item


cleaned = _clean_report_language_text("Fehmi'in ilişkisi sınırlıdır.")
assert "Fehmi’nin" in cleaned, cleaned
assert "Fehmi'in" not in cleaned, cleaned

note = "Düşük puan veya sınırlı kanıt nedeniyle zayıf eşleşme olarak ayrıldı."
weak = _weak_match_item({"ad": "Test", "gerekce": note}, "Tema")
assert weak["gerekce"].count(note) == 1, weak["gerekce"]

duplicated = _clean_report_language_text(f"{note} {note}")
assert duplicated.count(note) == 1, duplicated
