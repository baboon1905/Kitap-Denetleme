"""
Regression test for character normalization issues.
Specifically tests the Bay Lemoncello case where character names were being incorrectly filtered.
"""
from theme_gain_analysis import analyze_theme_gain, _normalize_character_identity, sanitize_character_profiles


def test_bay_lemoncello_character_normalization():
    """Test that Bay Lemoncello character names are properly normalized and not filtered out."""
    
    # Test cases from the Bay Lemoncello book
    test_cases = [
        # (input, expected_output, description)
        ("Bay Lemoncello", "Bay Lemoncello", "Main character name should be preserved"),
        ("Bay Lemoncello'nun", "Bay Lemoncello", "Trailing possessive suffix should be stripped"),
        ("Lemoncello", "Bay Lemoncello", "Last name only should map to canonical 'Bay Lemoncello'"),
        ("Akimi Hughes", "Akimi Hughes", "Student name should be preserved"),
        ("Akimi Hughes One", "Akimi Hughes", "OCR artifact 'One' should be removed"),
        ("Miguel Fernandez", "Miguel Fernandez", "Student name should be preserved"),
        ("Sierra Russell", "Sierra Russell", "Student name should be preserved"),
        ("Andrew Peckleman", "Andrew Peckleman", "Student name should be preserved"),
        ("Kyle Keeley", "Kyle Keeley", "Main protagonist name should be preserved"),
        ("Charles Chiltington", "Charles Chiltington", "Antagonist name should be preserved"),
    ]
    
    failed_tests = []
    for input_name, expected, description in test_cases:
        result = _normalize_character_identity(input_name)
        if result != expected:
            failed_tests.append(
                f"FAIL: {description}\n"
                f"  Input: '{input_name}'\n"
                f"  Expected: '{expected}'\n"
                f"  Got: '{result}'"
            )
    
    if failed_tests:
        print("\n".join(failed_tests))
        assert False, f"{len(failed_tests)} character normalization tests failed"
    else:
        print(f"✓ V6.6 All {len(test_cases)} character normalization tests passed")


def test_noise_word_filtering():
    """Test that noise words are properly filtered from character names (V6.6)."""
    
    # Test cases for V6.6 character noise gate and canonical mapping
    test_cases = [
        # (input, expected_output, description)
        ("Dünyadan Kyle", "Kyle Keeley", "Canonical map overrides noise gate for known characters"),
        ("Aslında Charles", "Charles Chiltington", "Canonical map overrides noise gate for known characters"),
        ("Charles Takımı", "Charles Chiltington", "Canonical map overrides noise gate for known characters"),
        ("Charles Dickens", "Charles Chiltington", "Canonical map catches OCR variant 'Charles Dickens'"),
        ("Kyle Takımı", "Kyle Keeley", "Canonical map catches 'Kyle Takımı'"),
        ("Eğer Charles", "Charles Chiltington", "Canonical map catches 'Eğer Charles'"),
        ("Sanki Miguel", "Miguel Fernandez", "Canonical map catches 'Sanki Miguel'"),
        ("Peşinde Akimi", "Akimi Hughes", "Canonical map catches 'Peşinde Akimi'"),
        ("Oyuna Miguel", "Miguel Fernandez", "Canonical map catches 'Miguel' substring even with noise prefix"),
        ("Dostum Miguel", "Miguel Fernandez", "Canonical map catches 'Miguel' substring even with noise prefix"),
    ]
    
    failed_tests = []
    for input_name, expected, description in test_cases:
        result = _normalize_character_identity(input_name)
        if result != expected:
            failed_tests.append(
                f"FAIL: {description}\n"
                f"  Input: '{input_name}'\n"
                f"  Expected: '{expected}'\n"
                f"  Got: '{result}'"
            )
    
    if failed_tests:
        print("\n".join(failed_tests))
        assert False, f"{len(failed_tests)} noise filtering tests failed"
    else:
        print(f"✓ V6.6 All {len(test_cases)} noise filtering tests passed")


def test_character_profile_sanitization():
    """Test full character profile sanitization with Bay Lemoncello characters."""
    
    # Simulate character profiles that might come from OCR/text extraction
    raw_characters = [
        {"ad": "Bay Lemoncello", "rolu": "ana", "guven_skoru": 0.9},
        {"ad": "Kyle Keeley", "rolu": "ana", "guven_skoru": 0.85},
        {"ad": "Akimi Hughes One", "rolu": "yan", "guven_skoru": 0.7},
        {"ad": "Miguel Fernandez", "rolu": "yan", "guven_skoru": 0.7},
        {"ad": "Sierra Russell", "rolu": "yan", "guven_skoru": 0.7},
        {"ad": "Charles Chiltington", "rolu": "yan", "guven_skoru": 0.6},
        {"ad": "Dünyadan Kyle", "rolu": "yan", "guven_skoru": 0.5},
        {"ad": "Aslında Charles", "rolu": "yan", "guven_skoru": 0.5},
        {"ad": "Charles Takımı", "rolu": "yan", "guven_skoru": 0.5},
    ]
    
    cleaned = sanitize_character_profiles(raw_characters, limit=8)
    
    character_names = [char["ad"] for char in cleaned]
    
    expected_names = [
        "Bay Lemoncello",
        "Kyle Keeley",
        "Akimi Hughes",
        "Miguel Fernandez",
        "Sierra Russell",
        "Charles Chiltington",
    ]
    
    failed_checks = []
    
    for expected_name in expected_names:
        if expected_name not in character_names:
            failed_checks.append(f"Expected character '{expected_name}' not found in cleaned profiles")
    
    # Check that noise + canonical variants are properly resolved to canonical names
    noise_variants = ["Dünyadan Kyle", "Aslında Charles", "Charles Takımı"]
    for noise_name in noise_variants:
        if noise_name in character_names:
            failed_checks.append(f"Noise variant '{noise_name}' should have been resolved to canonical name")
    
    # Check full canonical names are present
    if "Kyle Keeley" not in character_names:
        failed_checks.append("Kyle Keeley not found (should exist from 'Dünyadan Kyle' canonicalization)")
    if "Charles Chiltington" not in character_names:
        failed_checks.append("Charles Chiltington not found (should exist from 'Aslında Charles' canonicalization)")
    
    if failed_checks:
        print("\n".join(failed_checks))
        print(f"\nActual character names: {character_names}")
        assert False, f"{len(failed_checks)} sanitization checks failed"
    else:
        print(f"✓ V6.6 Character profile sanitization test passed ({len(cleaned)} characters preserved)")
        print(f"    Characters: {character_names}")


def test_leading_noise_words():
    """Test that leading noise words are properly stripped (V6.6)."""
    
    # V6.6: words in CHARACTER_LEADING_NOISE should be stripped
    noise_words = [
        "hadi", "simdi", "şimdi", "fakat", "cunku", "çünkü",
    ]
    
    failed_tests = []
    for noise_word in noise_words:
        test_input = f"{noise_word.capitalize()} Ahmet"
        result = _normalize_character_identity(test_input)
        if result != "Ahmet":
            failed_tests.append(
                f"Leading noise word '{noise_word}' not properly stripped from '{test_input}'. "
                f"Got: '{result}'"
            )
    
    # V6.6: verify problematic characters from Bay Lemoncello regressions are blocked
    problematic_noise = [
        "Dünyadan Kyle",       # → "Kyle Keeley" via canonical map (not blocked)
        "Aslında Charles",     # → "Charles Chiltington" via canonical map (not blocked)
        "Charles Takımı",      # → "Charles Chiltington" via canonical map (not blocked)
    ]
    for variant, canonical in [
        ("Dünyadan Kyle", "Kyle Keeley"),
        ("Aslında Charles", "Charles Chiltington"),
        ("Charles Takımı", "Charles Chiltington"),
    ]:
        result = _normalize_character_identity(variant)
        if result != canonical:
            failed_tests.append(
                f"V6.6: '{variant}' should resolve to '{canonical}'. Got: '{result}'"
            )
    
    # V6.6: ensure non-character noise words return empty
    for noise_name in ["Dünyadan", "Aslında", "Sanki", "Takımı", "Birden"]:
        result = _normalize_character_identity(noise_name)
        if result != "":
            failed_tests.append(
                f"V6.6: Pure noise '{noise_name}' should return empty. Got: '{result}'"
            )
    
    if failed_tests:
        print("\n".join(failed_tests[:10]))
        assert False, f"{len(failed_tests)} leading noise word tests failed"
    else:
        print(f"✓ V6.6 Leading noise word tests passed ({len(noise_words)} noise + {len(problematic_noise)} canonical + 5 noise-only tests)")


def test_bay_lemoncello_main_character_prefers_kyle_over_narrator():
    """Bay Lemoncello'da ana karakter olay merkeziyetine gore Kyle Keeley olmali."""

    text = """
--- SAYFA 1 ---
Benim adim Miguel Fernandez. Miguel Fernandez kutuphanedeki yarismayi anlatmaya basladi.
--- SAYFA 2 ---
Kyle Keeley yarismaya katilmak icin ilk karari verdi ve takimiyla kutuphaneye girdi.
--- SAYFA 3 ---
Miguel Fernandez katalogdaki sifreyi Kyle Keeley ile paylasti ve konustu.
--- SAYFA 4 ---
Kyle Keeley kitap raflarindaki ipuclarini arastirdi, Akimi Hughes ile cozum plani kurdu.
--- SAYFA 5 ---
Charles Chiltington hile yapmaya calisirken Kyle Keeley adil kalmayi secti.
--- SAYFA 6 ---
Kyle Keeley son bulmacayi cozdu ve kutuphaneden cikis yolunu takimina gosterdi.
"""
    result = analyze_theme_gain(
        text,
        {"baslik": "Bay Lemoncello'nun Kutuphanesinden Kacis", "yazar": "Test"},
        "9-12",
        "standart",
    )
    characters = result["ana_karakterler"]
    main_characters = [item["ad"] for item in characters if item.get("ana_karakter_mi")]
    kyle = next(item for item in characters if item["ad"] == "Kyle Keeley")
    miguel = next(item for item in characters if item["ad"] == "Miguel Fernandez")

    assert main_characters == ["Kyle Keeley"], characters
    assert kyle["rolu"] == "ana", kyle
    assert miguel.get("anlatici_mi") is True, miguel
    assert miguel["rolu"] == "yan", miguel


if __name__ == "__main__":
    print("Running V6.6 character normalization regression tests...\n")
    
    test_bay_lemoncello_character_normalization()
    test_noise_word_filtering()
    test_leading_noise_words()
    test_character_profile_sanitization()
    test_bay_lemoncello_main_character_prefers_kyle_over_narrator()
    
    print("\n✅ V6.6 All regression tests passed!")
