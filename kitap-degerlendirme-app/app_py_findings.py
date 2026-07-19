#!/usr/bin/env python3
import json
from pathlib import Path

REPORT_PATH = Path('tools/hardcode_report.json')
with REPORT_PATH.open('r', encoding='utf-8') as f:
    report = json.load(f)

app_findings = [f for f in report['findings'] if f['file'].endswith('app.py')]
app_findings.sort(key=lambda f:(f['severity'], f['file'], f['line']))

print(f"Total app.py findings: {len(app_findings)}\n")
for f in app_findings:
    print(f"{f['line']:4d} | {f['severity']:8s} | {f['usage']:10s} | {', '.join(f['reasons']):30s} | {f['value'][:100]!r}")
