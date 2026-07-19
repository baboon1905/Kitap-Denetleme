import re
from pathlib import Path
from collections import Counter, defaultdict
import sys
sys.path.insert(0, str(Path('tools').resolve()))
from check_hardcode import scan_file, classify

path = Path('theme_gain_analysis.py')
raw_findings = scan_file(path)
findings = []
for f in raw_findings:
    classification = classify(f, path)
    ff = dict(f)
    ff['severity'] = classification['severity']
    ff['reasons'] = classification.get('reasons', [])
    findings.append(ff)

crit_high = [f for f in findings if f['severity'] in ('CRITICAL','HIGH')]
print('TOTAL_CRITICAL_HIGH', len(crit_high))

# categorize into more detailed buckets
categories = []
for f in crit_high:
    val = f['value']
    usage = f['usage']
    reasons = set(f.get('reasons', []))
    if 'TEMPLATE_LITERAL' in reasons or (usage == 'literal' and '<' in val and '>' in val):
        cat = 'template'
    elif 'example_book_title' in reasons or re.search(r'\b(gokyuzunu kaybeden sehir|kolomb|kristof|deniz yolu|rota|saray|portekiz|ispanya)\b', val, re.IGNORECASE):
        cat = 'prompt'
    elif usage == 'dict_key' and 'mapping_with_non_generic_key' in reasons:
        cat = 'config'
    elif usage == 'literal' and 'file_path_or_pdf' in reasons:
        cat = 'template'
    elif usage in ('compare','if_test') and 'comparison_with_string_literal' in reasons:
        cat = 'domain_hardcode'
    elif usage == 'return' and 'comparison_with_string_literal' in reasons:
        cat = 'domain_hardcode'
    elif usage == 'literal' and 'example_book_title' in reasons:
        cat = 'prompt'
    else:
        cat = 'domain_hardcode'
    categories.append(cat)

counts = Counter(categories)
print('\nCATEGORY_COUNTS')
for k,v in counts.most_common():
    print(k, v)

print('\nTOP 30 DOMAIN_HARDCODE CANDIDATES')
for f in [f for cat,f in zip(categories, crit_high) if cat=='domain_hardcode'][:30]:
    print(f"LINE {f['lineno']} SEV {f['severity']} USAGE {f['usage']} VAL={repr(f['value'])} REASONS={f.get('reasons')}")

print('\nTOP 20 CONFIG CANDIDATES')
for f in [f for cat,f in zip(categories, crit_high) if cat=='config'][:20]:
    print(f"LINE {f['lineno']} USAGE {f['usage']} VAL={repr(f['value'])} REASONS={f.get('reasons')}")

print('\nTOP 20 TEMPLATE CANDIDATES')
for f in [f for cat,f in zip(categories, crit_high) if cat=='template'][:20]:
    print(f"LINE {f['lineno']} SEV {f['severity']} USAGE {f['usage']} VAL={repr(f['value'])} REASONS={f.get('reasons')}")

print('\nTOP 20 PROMPT CANDIDATES')
for f in [f for cat,f in zip(categories, crit_high) if cat=='prompt'][:20]:
    print(f"LINE {f['lineno']} SEV {f['severity']} USAGE {f['usage']} VAL={repr(f['value'])} REASONS={f.get('reasons')}")
