#!/usr/bin/env python3
import json

with open('tools/hardcode_report.json') as f:
    data = json.load(f)

print(f"Total findings: {sum(data['summary'].values())}")
print(f"Summary: {data['summary']}\n")

# Find findings in app.py
app_findings = [f for f in data['findings'] if 'app.py' in f['file']]
print(f"Findings in app.py: {len(app_findings)}")

# Group by severity
by_severity = {}
for f in app_findings:
    sev = f['severity']
    by_severity.setdefault(sev, []).append(f)

for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
    findings = by_severity.get(sev, [])
    print(f"\n{sev}: {len(findings)}")
    for f in findings[:5]:  # Show first 5 of each severity
        print(f"  Line {f['line']:4d}: {f['value'][:60]:60s} | reasons: {f['reasons']}")

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
pdf_msgs = [f for f in app_findings if 'PDF endpoint' in f['value']]
print(f"\nFindings with 'PDF endpoint': {len(pdf_msgs)}")
for f in pdf_msgs:
    print(f"  Line {f['line']:4d}: severity={f['severity']:8s} | reasons={f['reasons']}")
