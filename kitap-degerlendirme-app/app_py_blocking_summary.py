#!/usr/bin/env python3
import json
from pathlib import Path
from collections import defaultdict

REPORT_PATH = Path('tools/hardcode_report.json')
with REPORT_PATH.open('r', encoding='utf-8') as f:
    report = json.load(f)

app_findings = [f for f in report['findings'] if f['file'].endswith('app.py')]
blocking = [f for f in app_findings if f['severity'] in ('CRITICAL', 'HIGH')]

print(f"TOTAL app.py findings: {len(app_findings)}")
print(f"BLOCKING app.py findings: {len(blocking)}\n")

print("line | severity | usage | reasons | value")
for f in sorted(blocking, key=lambda x:(x['line'], x['severity'])):
    value = f['value'].replace('\n', '\\n')
    print(f"{f['line']:4d} | {f['severity']:8s} | {f['usage']:8s} | {','.join(f['reasons']):30s} | {value[:120]}")

print('\nCONSTANTS FILES SUMMARY:')
const_counts = defaultdict(lambda: {'CRITICAL':0,'HIGH':0,'MEDIUM':0,'LOW':0})
for f in report['findings']:
    if f['file'].startswith('constants'):
        const_counts[f['file']][f['severity']] += 1
for file, counts in const_counts.items():
    print(f"{file} | {counts['CRITICAL']} | {counts['HIGH']} | {counts['MEDIUM']} | {counts['LOW']}")

# count app.py by reason category heuristics
print('\nAPP.PY CRITICAL/HIGH reasons breakdown:')
reason_counts = defaultdict(int)
for f in blocking:
    for r in f['reasons']:
        reason_counts[r] += 1
for reason, count in sorted(reason_counts.items(), key=lambda x:-x[1]):
    print(f"{reason}: {count}")
