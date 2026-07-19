from theme_gain_analysis import teacher_report_language_quality


good = teacher_report_language_quality(
    "Kristof Kolomb’un yeni bir rota arayışı, öğrencilerle tarihsel neden-sonuç ilişkileri üzerinden incelenebilir."
)
assert good["gecerli"] is True, good

for bad_text in [
    "anlatıcı'un yeni bir deniz yolu araması",
    "'in kararları olayları değiştirdi",
    "karakter {karakter_adi} hedefe ulaştı",
    "Kolomb'un'un yolculuğu",
]:
    audit = teacher_report_language_quality(bad_text)
    assert audit["gecerli"] is False, (bad_text, audit)
