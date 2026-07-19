#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple test: Just check if 4.1 is in the PDF
"""

import subprocess
import sys

# Run debug script
result = subprocess.run(
    [sys.executable, 'debug_extract_pdf.py'],
    capture_output=True,
    text=False  # Get bytes
)

# Decode with error handling
try:
    output = result.stdout.decode('utf-8', errors='replace') + result.stderr.decode('utf-8', errors='replace')
except:
    output = ""

# Check for 4.1
if "4.1" in output and "Detayli" in output:
    print("✅ 4.1 section FOUND in PDF!")
elif "4.1" in output:
    print("⚠️  '4.1' found but not 'Detayli'")
else:
    print("❌ 4.1 section NOT found in PDF")
    
    # Try to find where MEB section starts
    if "MEB TTK" in output:
        print("\n   But 'MEB TTK' section found:")
        lines = output.split('\n')
        for i, line in enumerate(lines):
            if "MEB TTK" in line:
                print(f"   {line}")
                if i + 1 < len(lines):
                    print(f"   {lines[i+1]}")
                break
