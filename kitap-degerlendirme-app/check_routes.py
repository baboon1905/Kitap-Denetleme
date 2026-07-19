#!/usr/bin/env python3
import app as flask_app
print(f"✅ Flask app loaded")
print(f"Registered routes: {len(flask_app.app.url_map._rules)}")
for rule in flask_app.app.url_map._rules:
    if 'rapor' in str(rule):
        print(f"  → {rule}")
