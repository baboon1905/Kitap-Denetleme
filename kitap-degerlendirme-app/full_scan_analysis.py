#!/usr/bin/env python3
"""
Comprehensive hard-code scan analysis with file categorization.
"""
import json
from collections import defaultdict
from pathlib import Path

# Load report
with open('tools/hardcode_report.json', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 80)
print("FULL CODEBASE HARD-CODE SCAN ANALYSIS")
print("=" * 80)

# Print overall summary
print(f"\n📊 OVERALL SUMMARY")
print("-" * 80)
total = sum(data['summary'].values())
print(f"Total findings: {total:,}")
for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
    count = data['summary'][sev]
    pct = (count / total * 100) if total > 0 else 0
    print(f"  {sev:8s}: {count:6,} ({pct:5.1f}%)")

# Categorize files
def categorize_file(filepath):
    """Categorize file as Runtime/DevTool/TestBench."""
    parts = filepath.lower()
    
    # Test/Benchmark patterns
    test_patterns = ('test_', 'tests/', '_test.py', 'benchmark', 'fixtures', 'example')
    if any(p in parts for p in test_patterns):
        return 'TEST_BENCHMARK'
    
    # Development tool patterns
    dev_patterns = (
        'check_', 'debug_', 'analyze_', 'fix_', 'apply_', 'compare_',
        'diagnose_', 'extract_', 'find_', 'validate_', 'count_', 'verify_'
    )
    if any(f in parts for f in dev_patterns):
        return 'DEV_TOOL'
    
    # Production Runtime patterns - explicitly list
    prod_patterns = (
        'app.py', 'evaluator', 'processor', 'config.py', 'theme_gain',
        'professional_evaluator', 'pipeline_runtime', 'text_quality',
        'custom_keywords', 'maarif', 'meb_', '_raporlayici'
    )
    if any(p in parts for p in prod_patterns):
        return 'RUNTIME_PROD'
    
    # Default classification by location
    if 'tools/' in parts:
        return 'DEV_TOOL'
    if '/test' in parts or '_test' in parts:
        return 'TEST_BENCHMARK'
    
    # Utility/library modules without clear pattern
    return 'RUNTIME_PROD'

# Organize findings by category
by_category = defaultdict(lambda: {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0})
by_file = defaultdict(lambda: {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []})
category_findings = defaultdict(list)

for finding in data['findings']:
    filepath = finding['file']
    category = categorize_file(filepath)
    severity = finding['severity']
    
    by_category[category][severity] += 1
    by_file[filepath][severity].append(finding)
    category_findings[category].append(finding)

# Print category summary
print(f"\n📁 BY CATEGORY")
print("-" * 80)
for category in ['RUNTIME_PROD', 'DEV_TOOL', 'TEST_BENCHMARK']:
    counts = by_category.get(category, {})
    crit = counts.get('CRITICAL', 0)
    high = counts.get('HIGH', 0)
    med = counts.get('MEDIUM', 0)
    low = counts.get('LOW', 0)
    total_cat = crit + high + med + low
    
    label = category.replace('_', ' ')
    print(f"\n{label}:")
    print(f"  CRITICAL: {crit:6,} | HIGH: {high:6,} | MEDIUM: {med:6,} | LOW: {low:6,} | TOTAL: {total_cat:6,}")

# Top 10 files by severity
print(f"\n🔴 TOP 10 FILES BY CRITICAL/HIGH COUNT")
print("-" * 80)
file_severity_counts = []
for filepath, severities in by_file.items():
    crit = len(severities['CRITICAL'])
    high = len(severities['HIGH'])
    if crit > 0 or high > 0:
        category = categorize_file(filepath)
        file_severity_counts.append((crit + high, crit, high, filepath, category))

file_severity_counts.sort(reverse=True)
for i, (total, crit, high, filepath, category) in enumerate(file_severity_counts[:10], 1):
    category_label = category.replace('_', ' ')
    print(f"{i:2d}. {crit:4d} CRIT | {high:4d} HIGH | {filepath[:60]:60s} ({category_label})")

# Filter Runtime Production CRITICAL/HIGH for action
runtime_prod_critical_high = []
for finding in data['findings']:
    if finding['severity'] in ('CRITICAL', 'HIGH'):
        if categorize_file(finding['file']) == 'RUNTIME_PROD':
            runtime_prod_critical_high.append(finding)

# Sort by severity (CRITICAL first) then by file/line
severity_order = {'CRITICAL': 0, 'HIGH': 1}
runtime_prod_critical_high.sort(
    key=lambda f: (severity_order.get(f['severity'], 999), f['file'], f['line'])
)

print(f"\n🎯 RUNTIME PRODUCTION CRITICAL/HIGH FINDINGS (for action)")
print("-" * 80)
print(f"Total: {len(runtime_prod_critical_high)}")
print()

# Show first 30
for i, finding in enumerate(runtime_prod_critical_high[:30], 1):
    line = finding['line']
    sev = finding['severity']
    file = finding['file']
    value = finding['value']
    reasons = ', '.join(finding.get('reasons', []))
    
    value_display = value[:50] + '...' if len(value) > 50 else value
    print(f"{i:2d}. [{sev:8s}] {file}:{line:5d} | {value_display:50s}")
    if reasons:
        print(f"    Reasons: {reasons}\n")

if len(runtime_prod_critical_high) > 30:
    print(f"\n    ... and {len(runtime_prod_critical_high) - 30} more findings")

print(f"\n" + "=" * 80)
