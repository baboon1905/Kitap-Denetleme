#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick test without file upload"""

import json
import requests

API_BASE = "http://127.0.0.1:5000"

# Test 1: Health check
print("Testing API health...")
r = requests.get(f"{API_BASE}/health", timeout=5)
print(f"Health: {r.status_code}")

# Test 2: Profiller
print("\nTesting profiller endpoint...")
r = requests.get(f"{API_BASE}/api/profiller", timeout=5)
print(f"Profiller: {r.status_code}")
print(f"Data: {r.json()}")

print("\n✅ API çalışıyor!")
