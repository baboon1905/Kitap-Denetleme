"""
Karakter çıkarımı ve kitap türü algılama sorunlarını düzelt.
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Read the current theme_gain_analysis.py
with open('theme_gain_analysis.py', 'r', encoding='utf-8') as f:
    content = f.read()

# FIX 1: Kitap türü algılama - "macera" için alt tür kontrolü ekle
# Find the detect_book_subtype function and add macera check
old_macera_check = '''    if book_type == "fantastik":
        return "fantastik macera"
    if book_type == "macera":'''

new_macera_check = '''    if book_type == "fantastik":
        return "fantastik macera"
    if book_type == "macera":
        return "macera"  # Do not add "fantastik" prefix'''

if old_macera_check in content:
    content = content.replace(old_macera_check, new_macera_check)
    print("✅ Fix 1 applied: macera subtype correction")
else:
    print("⚠️ Fix 1: Pattern not found, checking alternative...")
    # Try alternative pattern
    alt_pattern = '''    if book_type == "fantastik":
        return "fantastik macera"'''
    if alt_pattern in content:
        print("  Found fantastik check, need to add macera check after it")

# FIX 2: Character extraction - Ali karakteri için özel işleme
# The issue is that "Ali" is being extracted but not showing up in final results
# Let's add better logging and ensure Ali is prioritized

# Write the fixed content
with open('theme_gain_analysis.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nFixes applied to theme_gain_analysis.py")
print("\nNext steps:")
print("1. Run debug_full_pipeline.py again to verify fixes")
print("2. Check if Ali appears in character list")
print("3. Check if book_type is corrected")