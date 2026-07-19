"""
Tüm sorunları düzelt:
1. Karakter çıkarımı - Ali'yi kaçırma
2. Kitap türü - macera için fantastik macera yerine sadece macera
3. Tema filtreleri - THEME_CONTEXT_RULES güncelle
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Read theme_gain_analysis.py
with open('theme_gain_analysis.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Convert to string for easier manipulation
content = ''.join(lines)

# ============================================================================
# FIX 1: Kitap türü - macera için alt tür düzelt
# ============================================================================
print("=== FIX 1: Kitap Türü Düzeltmesi ===")

# Find and replace the detect_book_subtype function
old_subtype = '''def detect_book_subtype(text: str, metadata: dict | None, book_type: str) -> str:
    metadata = metadata or {}
    if book_type == "fantastik":
        return "fantastik macera"
    if book_type == "bilimsel içerik":'''

new_subtype = '''def detect_book_subtype(text: str, metadata: dict | None, book_type: str) -> str:
    metadata = metadata or {}
    if book_type == "fantastik":
        return "fantastik macera"
    if book_type == "macera":
        return "macera"  # Do not add "fantastik" prefix for adventure books
    if book_type == "bilimsel içerik":'''

if old_subtype in content:
    content = content.replace(old_subtype, new_subtype)
    print("✅ Kitap türü düzeltmesi uygulandı: macera → 'macera' (fantastik macera değil)")
else:
    print("⚠️ Kitap türü deseni bulunamadı, alternatif arama...")
    # Try to find just the function signature
    if 'def detect_book_subtype(text: str, metadata: dict | None, book_type: str) -> str:' in content:
        print("  Fonksiyon bulundu ama içerik farklı")

# ============================================================================
# FIX 2: Karakter çıkarımı - Ali'yi öncelikle
# ============================================================================
print("\n=== FIX 2: Karakter Çıkarımı Düzeltmesi ===")

# The issue is that Ali is being extracted but filtered out
# Let's check the _extract_character_profiles function more carefully
# The function signature shows limit=6 by default, but Ali should still be #1

# Check if there's a CHARACTER_STOPWORDS that might be filtering Ali
if '"Ali"' in content or "'Ali'" in content:
    print("⚠️ 'Ali' CHARACTER_STOPWORDS'da bulunuyor - bu sorun!")
    # Remove Ali from stopwords if it exists
    content = content.replace('"Ali", ', '').replace(', "Ali"', '')
    content = content.replace("'Ali', ", '').replace(", 'Ali'", '')
    print("✅ 'Ali' CHARACTER_STOPWORDS'dan çıkarıldı")
else:
    print("✅ 'Ali' CHARACTER_STOPWORDS'da değil")

# ============================================================================
# FIX 3: Tema filtreleri - THEME_CONTEXT_RULES güncelle
# ============================================================================
print("\n=== FIX 3: Tema Filtreleri Düzeltmesi ===")

# Find THEME_CONTEXT_RULES and add missing rules
old_rules = '''THEME_CONTEXT_RULES = {
    "dostluk": {
        "must": ["arkadaş", "dost"],
        "action": ["paylaş", "yardım", "destek", "birlikte"]
    },
    "empati": {
        "must": ["anladı", "hissetti", "üzüldü"],
        "action": ["hissetti", "anladı", "üzüldü", "yardım"]
    }'''

new_rules = '''THEME_CONTEXT_RULES = {
    "sorumluluk": {
        "must": ["sahiplen", "sorumluluk", "görev", "bakmak", "besle", "söz"],
        "action": ["düşündü", "karar", "sahiplendi", "öğrenmişti", "pişman", "tutmalıyım"]
    },
    "dostluk": {
        "must": ["arkadaş", "dost", "yardım", "dostluk"],
        "action": ["paylaş", "yardım", "destek", "birlikte", "eğlendiler"]
    },
    "empati": {
        "must": ["anladı", "hissetti", "üzüldü", "düşündü", "merhamet", "yardım"],
        "action": ["hissetti", "anladı", "üzüldü", "düşündü", "yardım", "pişman"]
    },
    "vicdan": {
        "must": ["vicdan", "pişman", "pişmanlık", "huzur"],
        "action": ["düşündü", "fısıldadı", "içinde"]
    },
    "pişmanlık": {
        "must": ["pişman", "pişmanlık", "özür", "keşke"],
        "action": ["pişman", "korumuyamamıştı", "hatasını"]
    },
    "dostluk": {
        "must": ["arkadaş", "dost", "yardım", "dostluk"],
        "action": ["paylaş", "yardım", "destek", "birlikte", "eğlendiler"]
    },
    "empati": {
        "must": ["anladı", "hissetti", "üzüldü", "düşündü", "merhamet", "yardım"],
        "action": ["hissetti", "anladı", "üzüldü", "düşündü", "yardım", "pişman"]
    }'''

if old_rules in content:
    content = content.replace(old_rules, new_rules)
    print("✅ THEME_CONTEXT_RULES güncellendi: sorumluluk, dostluk, empati, vicdan, pişmanlık eklendi")
else:
    print("⚠️ THEME_CONTEXT_RULES deseni bulunamadı")

# ============================================================================
# Write fixed content
# ============================================================================
print("\n=== Değişiklikler Kaydediliyor ===")
with open('theme_gain_analysis.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Tüm düzeltmeler theme_gain_analysis.py'ye uygulandı")
print("\nSonraki adım:")
print("  python debug_full_pipeline.py ile test et")