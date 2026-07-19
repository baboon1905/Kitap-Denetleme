from theme_gain_analysis import analyze_theme_gain


text = """
--- SAYFA 1 ---
Benim adım Kristof Kolomb. Kristof Kolomb yeni bir deniz yolu bulmayı hedefledi ve haritayı inceledi.
--- SAYFA 2 ---
Kristof Kolomb saraya giderek sefer planını anlattı ve destek istedi.
--- SAYFA 3 ---
Kristof Kolomb mürettebatla konuştu, riskleri değerlendirdi ve yolculuğa devam etme kararı verdi.
--- SAYFA 4 ---
Kristof Kolomb fırtınaya rağmen vazgeçmedi ve keşif rotasını sürdürdü.
"""

result = analyze_theme_gain(text, {"baslik": "Benim Adım Kristof Kolomb", "yazar": "Test"}, "9-12", "standart")
characters = result["ana_karakterler"]
kristof = next(item for item in characters if item["ad"] == "Kristof Kolomb")
assert kristof.get("ana_karakter_mi") is True, kristof
assert kristof.get("rolu") == "ana", kristof
assert kristof.get("kategori") in {"anlatıcı", "merkez karakter"}, kristof
assert kristof.get("kitap_adinda_geciyor") is True, kristof
