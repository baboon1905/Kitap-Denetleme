import re
from pathlib import Path
from collections import Counter
import sys
sys.path.insert(0, str(Path('tools').resolve()))
from check_hardcode import scan_file, classify

path = Path('theme_gain_analysis.py')
raw_findings = scan_file(path)
findings = []
for f in raw_findings:
    r = classify(f, path)
    ff = dict(f)
    ff.update(r)
    findings.append(ff)

crit_high = [f for f in findings if f['severity'] in ('CRITICAL','HIGH')]
config_data = [f for f in findings if 'DOMAIN_TAXONOMY' in f.get('reasons', [])]
template_literal = [f for f in findings if 'TEMPLATE_LITERAL' in f.get('reasons', [])]

def print_sample(title, items, limit=20):
    print(f'--- {title} ({len(items)})')
    for f in items[:limit]:
        print(f"LINE {f['lineno']} SEV {f['severity']} USAGE {f['usage']} VAL={repr(f['value'])} REASONS={f['reasons']}")

print('REAL_CRITICAL_HIGH', len(crit_high))
print('CONFIG_DATA', len(config_data))
print('TEMPLATE_LITERAL', len(template_literal))
print('\n')
print_sample('TOP 20 REAL CRITICAL/HIGH', crit_high, 20)
print('\n')
print_sample('TOP 20 CONFIG_DATA', config_data, 20)
print('\n')
print_sample('TOP 20 TEMPLATE_LITERAL', template_literal, 20)
