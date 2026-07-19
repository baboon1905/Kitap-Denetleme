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
    f['severity'] = classification['severity']
    f['reasons'] = classification.get('reasons', [])
    findings.append(f)
crit_high = [f for f in findings if f['severity'] in ('CRITICAL','HIGH')]
print('TOTAL_CRITICAL_HIGH', len(crit_high))
usage_counts = Counter(f['usage'] for f in crit_high)
reason_counts = Counter(r for f in crit_high for r in f.get('reasons', []))
print('\nUSAGE_COUNTS')
for k,v in usage_counts.most_common():
    print(k, v)
print('\nREASON_COUNTS')
for k,v in reason_counts.most_common():
    print(k, v)
category_map = defaultdict(int)
entries = []
for f in crit_high:
    val = f['value']
    usage = f['usage']
    reasons = set(f.get('reasons', []))
    if 'TEMPLATE_LITERAL' in reasons:
        cat='template'
    elif 'ERROR_MESSAGE_LITERAL' in reasons:
        cat='false_positive'
    elif 'mime_type' in reasons or 'CONTRACT_INLINE_OK' in reasons or 'CONFIG_CONSTANT_MODULE' in reasons:
        cat='config'
    elif re.search(r'prompt|system|assistant|user|openai|gpt|ilk cümle|metin|soru', val, re.IGNORECASE):
        cat='prompt'
    elif usage in ('route','call_arg') and val.startswith('/'):
        cat='config'
    elif usage in ('compare','if_test') and len(val) > 3 and ' ' in val:
        cat='domain_hardcode'
    elif usage == 'dict_key' and ' ' in val:
        cat='domain_hardcode'
    elif usage == 'literal' and re.search(r'\b(book|kitap|character|karakter|pdf|epub|template|html|prompt)\b', val, re.IGNORECASE):
        cat='domain_hardcode'
    else:
        cat='domain_hardcode'
    category_map[cat]+=1
    entries.append((cat, f))
print('\nCATEGORY_COUNTS')
for k,v in category_map.items():
    print(k, v)
print('\nTOP 30 DOMAIN_HARDCODE CANDIDATES')
for f in sorted([f for cat,f in entries if cat=='domain_hardcode'], key=lambda x:(x['severity'], x['lineno']))[:30]:
    print(f"LINE {f['lineno']} SEV {f['severity']} USAGE {f['usage']} VAL={repr(f['value'])} REASONS={f.get('reasons')}")
