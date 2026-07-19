#!/usr/bin/env python3
import json
from collections import defaultdict
from pathlib import Path

REPORT_PATH = Path('tools/hardcode_report.json')
with REPORT_PATH.open('r', encoding='utf-8') as f:
    report = json.load(f)


def classify(filepath):
    p = filepath.lower().replace('\\', '/').replace('////', '/')
    if any(x in p for x in ('test/', '/tests/', 'test_', '_test.py', 'benchmark', 'benchmarks', 'fixtures', 'example')):
        return 'TEST_BENCHMARK'
    if any(x in p for x in ('tools/', 'check_', 'debug_', 'analyze_', 'fix_', 'apply_', 'compare_', 'diagnose_', 'extract_', 'find_', 'validate_', 'count_', 'verify_')):
        return 'DEV_TOOL'
    if any(x in p for x in ('app.py', 'evaluator', 'processor', 'config.py', 'theme_gain', 'professional_evaluator', 'pipeline_runtime', 'text_quality', 'custom_keywords', 'maarif', 'meb_', '_raporlayici', 'report_generator', 'pdf_processor', 'narrative', 'visual_audit')):
        return 'RUNTIME_PROD'
    if 'tools/' in p:
        return 'DEV_TOOL'
    return 'RUNTIME_PROD'

summary = defaultdict(lambda: {'CRITICAL':0,'HIGH':0,'MEDIUM':0,'LOW':0})
file_summary = defaultdict(lambda: {'CRITICAL':0,'HIGH':0,'MEDIUM':0,'LOW':0})
total = {'CRITICAL':0,'HIGH':0,'MEDIUM':0,'LOW':0}
for f in report['findings']:
    file_summary[f['file']][f['severity']] += 1
    summary[classify(f['file'])][f['severity']] += 1
    total[f['severity']] += 1

print('file | CRITICAL | HIGH | MEDIUM | LOW | blocking_total')
for filepath, counts in sorted(file_summary.items(), key=lambda x:(-(x[1]['CRITICAL']+x[1]['HIGH']), x[0])):
    blocking = counts['CRITICAL'] + counts['HIGH']
    print(f"{filepath} | {counts['CRITICAL']} | {counts['HIGH']} | {counts['MEDIUM']} | {counts['LOW']} | {blocking}")

print('\ncategory | CRITICAL | HIGH | MEDIUM | LOW | blocking_total')
for cat in ('RUNTIME_PROD','DEV_TOOL','TEST_BENCHMARK'):
    counts = summary[cat]
    print(f"{cat} | {counts['CRITICAL']} | {counts['HIGH']} | {counts['MEDIUM']} | {counts['LOW']} | {counts['CRITICAL']+counts['HIGH']}")

print('\nOverall | CRITICAL | HIGH | MEDIUM | LOW')
print(f"Overall | {total['CRITICAL']} | {total['HIGH']} | {total['MEDIUM']} | {total['LOW']}")
