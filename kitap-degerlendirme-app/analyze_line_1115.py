#!/usr/bin/env python3
import json

with open('tools/hardcode_report.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total findings: {sum(data['summary'].values())}")
print(f"Summary: {data['summary']}\n")

# Find findings in app.py
app_findings = [f for f in data['findings'] if 'app.py' in f['file']]
print(f"Findings in app.py: {len(app_findings)}")

# Specifically look for line 1115
line_1115 = [f for f in app_findings if f['line'] == 1115]
if line_1115:
    print(f"\n✓ Found line 1115:")
    f = line_1115[0]
    print(f"  Value: {f['value']}")
    print(f"  Severity: {f['severity']}")
    print(f"  Reasons: {f['reasons']}")
    print(f"  Usage: {f['usage']}")
else:
    print(f"\n✗ Line 1115 NOT FOUND in app.py findings")

# Look for 'PDF endpoint' messages  
pdf_msgs = [f for f in app_findings if 'PDF endpoint' in f.get('value', '')]
print(f"\nFindings with 'PDF endpoint': {len(pdf_msgs)}")
for f in pdf_msgs:
    print(f"  Line {f['line']:4d}: severity={f['severity']:8s} | reasons={f['reasons']}")

# Show summary for app.py by severity
by_sev = {}
for f in app_findings:
    sev = f['severity']
    by_sev[sev] = by_sev.get(sev, 0) + 1
print(f"\napp.py by severity: {by_sev}")
