#!/usr/bin/env python3
"""
Runtime Production CRITICAL/HIGH findings filtered for actual production code (excluding examples).
"""
import json
from pathlib import Path

with open('tools/hardcode_report.json', encoding='utf-8') as f:
    data = json.load(f)

def categorize_file(filepath):
    parts = filepath.lower()
    test_patterns = ('test_', 'tests/', '_test.py', 'benchmark', 'fixtures', 'example')
    if any(p in parts for p in test_patterns):
        return 'TEST_BENCHMARK'
    dev_patterns = ('check_', 'debug_', 'analyze_', 'fix_', 'apply_', 'compare_',
                    'diagnose_', 'extract_', 'find_', 'validate_', 'count_', 'verify_')
    if any(f in parts for f in dev_patterns):
        return 'DEV_TOOL'
    prod_patterns = ('app.py', 'evaluator', 'processor', 'config.py', 'theme_gain',
                     'professional_evaluator', 'pipeline_runtime', 'text_quality',
                     'custom_keywords', 'maarif', 'meb_', '_raporlayici')
    if any(p in parts for p in prod_patterns):
        return 'RUNTIME_PROD'
    if 'tools/' in parts:
        return 'DEV_TOOL'
    if '/test' in parts or '_test' in parts:
        return 'TEST_BENCHMARK'
    return 'RUNTIME_PROD'

def is_example_or_docs(filepath):
    """Check if file is examples, docs, or test data."""
    parts = filepath.lower()
    example_patterns = ('ornek', 'example', 'sample', 'fixture', 'roadmap', 'project_completion',
                       'bagimsizlik_kontrol', 'notes', 'summary', 'debug_', 'test_')
    return any(p in parts for p in example_patterns)

# Get production CRITICAL/HIGH findings
prod_crit_high = [f for f in data['findings']
                  if f['severity'] in ('CRITICAL', 'HIGH')
                  and categorize_file(f['file']) == 'RUNTIME_PROD'
                  and not is_example_or_docs(f['file'])]

# Sort
severity_order = {'CRITICAL': 0, 'HIGH': 1}
prod_crit_high.sort(key=lambda f: (severity_order.get(f['severity'], 999), f['file'], f['line']))

print("=" * 90)
print("ACTIONABLE RUNTIME PRODUCTION CRITICAL/HIGH (excluding examples/docs)")
print("=" * 90)
print(f"Total: {len(prod_crit_high)}\n")

# Group by file
by_file = {}
for f in prod_crit_high:
    file = f['file']
    if file not in by_file:
        by_file[file] = {'CRITICAL': [], 'HIGH': []}
    by_file[file][f['severity']].append(f)

print("📊 BY FILE:\n")
for filepath in sorted(by_file.keys()):
    crit_count = len(by_file[filepath]['CRITICAL'])
    high_count = len(by_file[filepath]['HIGH'])
    total = crit_count + high_count
    print(f"{filepath:50s} : {crit_count:3d} CRIT | {high_count:3d} HIGH | {total:3d} total")

print(f"\n{'=' * 90}")
print(f"FIRST 30 ACTIONABLE FINDINGS\n")

for i, f in enumerate(prod_crit_high[:30], 1):
    sev = f['severity']
    file = f['file']
    line = f['line']
    value = f['value']
    usage = f.get('usage', '?')
    reasons = ', '.join(f.get('reasons', []))
    
    value_short = value[:55] + '...' if len(value) > 55 else value
    
    print(f"{i:2d}. [{sev:8s}] {file}:{line}")
    print(f"    Value: {value_short}")
    print(f"    Usage: {usage} | Reasons: {reasons}\n")

if len(prod_crit_high) > 30:
    print(f"    ➡️  ... and {len(prod_crit_high) - 30} more findings\n")

print("=" * 90)

# Summary stats
print("\n📈 SUMMARY STATISTICS\n")
crit_count = sum(1 for f in prod_crit_high if f['severity'] == 'CRITICAL')
high_count = sum(1 for f in prod_crit_high if f['severity'] == 'HIGH')

print(f"Actionable CRITICAL: {crit_count}")
print(f"Actionable HIGH:     {high_count}")
print(f"Actionable TOTAL:    {len(prod_crit_high)}")
print()

# Top files
print("TOP 5 PRODUCTION FILES BY FINDINGS:")
file_counts = [(file, len(by_file[file]['CRITICAL']) + len(by_file[file]['HIGH']), 
                len(by_file[file]['CRITICAL']), len(by_file[file]['HIGH']))
               for file in by_file.keys()]
file_counts.sort(key=lambda x: x[1], reverse=True)

for i, (file, total, crit, high) in enumerate(file_counts[:5], 1):
    print(f"  {i}. {file:45s} ({crit} CRIT + {high} HIGH = {total} total)")

print(f"\n{'=' * 90}\n")
