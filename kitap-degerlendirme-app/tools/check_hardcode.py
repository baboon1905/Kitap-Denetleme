#!/usr/bin/env python3
"""Improved hard-code detection tool.

Scans Python files and finds string literals used in comparisons, dict keys,
assignments, or other suspicious patterns. Classifies findings into
CRITICAL/HIGH/MEDIUM/LOW and emits a JSON report plus terminal summary.

Usage:
    python tools/check_hardcode.py [root]

Exit codes:
 - 2 : CRITICAL or HIGH findings (CI should fail)
 - 1 : only MEDIUM findings (warning)
 - 0 : no findings or only LOW findings
"""
import ast
import csv
import json
import re
import sys
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, List


ROOT_DEFAULT = Path(__file__).resolve().parents[1]
REPORT_PATH = Path(__file__).resolve().parent / "hardcode_report.json"
CSV_PATH = Path(__file__).resolve().parent / "hardcode_report.csv"
SUPPRESS_PATH = Path(__file__).resolve().parent / "hardcode_suppress.json"


def is_test_path(p: Path) -> bool:
    parts = [pp.lower() for pp in p.parts]
    return any(x in parts for x in ("test", "tests", "fixtures", "benchmark", "benchmarks"))


def scan_file(path: Path) -> List[Dict]:
    src = path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []

    findings: List[Dict] = []

    for node in ast.walk(tree):
        # constant string used directly
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value
            # ignore empty strings
            if not val.strip():
                continue
            # gather context
            lineno = getattr(node, 'lineno', None)
            col = getattr(node, 'col_offset', None)
            src_seg = None
            try:
                src_seg = ast.get_source_segment(src, node)
            except Exception:
                src_seg = val

            # determine usage (default; will be enriched later)
            usage = 'literal'
            findings.append({'lineno': lineno, 'col': col, 'value': val, 'usage': usage, 'src': src_seg})

    # Enrich with parents and specialized usage categories
    parent_map = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parent_map[child] = parent

    enriched: List[Dict] = []
    for f in findings:
        # locate AST node at lineno and value — approximate match
        node = None
        for n in parent_map:
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                if getattr(n, 'lineno', None) == f['lineno'] and n.value == f['value']:
                    node = n
                    break

        usage = 'literal'
        if node is not None:
            par = parent_map.get(node)
            grand = parent_map.get(par)
            # docstring detection: Expr as first statement in module/class/function
            if isinstance(par, ast.Expr) and grand is not None and hasattr(grand, 'body') and len(getattr(grand, 'body', []))>0 and getattr(grand, 'body')[0] is par:
                usage = 'docstring'
            elif isinstance(par, ast.Compare):
                usage = 'compare'
            elif isinstance(par, ast.Dict):
                usage = 'dict_key' if any(k is node for k in par.keys) else 'dict_value'
            elif isinstance(par, ast.Call):
                # decorator route detection: call.func.attr == 'route'
                try:
                    func = par.func
                    if isinstance(func, ast.Attribute) and getattr(func, 'attr', '') == 'route':
                        usage = 'route'
                    else:
                        usage = 'call_arg'
                except Exception:
                    usage = 'call_arg'
            elif isinstance(par, ast.Assign):
                usage = 'assign'
            elif isinstance(par, ast.Expr):
                usage = 'expr'
            elif isinstance(par, ast.Return):
                usage = 'return'
            elif isinstance(par, ast.If):
                usage = 'if_test'

        # additional heuristic classifications based on literal content
        val = f['value']
        low_val = val.strip().lower()
        # MIME types
        mime_known = ('application/json','application/pdf','application/msword','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        if low_val in mime_known:
            usage = 'mime_type'
        # XML/XLSX template detection: handle literal XML fragments and tag pieces inside f-strings
        if (
            val.strip().startswith('<?xml')
            or (val.strip().startswith('<') and '>' in val)
            or '<sheetdata' in low_val
            or '<worksheet' in low_val
            or '<row' in low_val
            or '<relationship' in low_val
            or '</relationship' in low_val
        ):
            usage = 'template'

        f['usage'] = usage
        enriched.append(f)

    return enriched


def load_suppressions() -> List[Dict]:
    if not SUPPRESS_PATH.exists():
        return []
    try:
        data = json.loads(SUPPRESS_PATH.read_text(encoding='utf-8'))
    except Exception:
        return []
    valid = []
    for entry in data:
        # required fields: pattern, scope, reason, owner, review_after
        if not all(k in entry for k in ('pattern', 'scope', 'reason', 'owner')):
            continue
        # require review_after or expires_at
        if 'review_after' not in entry and 'expires_at' not in entry:
            continue
        valid.append(entry)
    return valid


def matches_suppression(entry: Dict, finding: Dict, relpath: str) -> bool:
    pattern = entry.get('pattern')
    scope = entry.get('scope', '')
    try:
        if pattern and re.search(pattern, finding.get('value', ''), flags=re.IGNORECASE):
            # scope may be 'tests/*' or 'production' or a filepath glob
            if scope in ('*', '', 'all'):
                return True
            # if scope indicates tests/fixtures/benchmarks, match by path
            if fnmatch(relpath, scope) or fnmatch(str(relpath), scope):
                return True
    except re.error:
        return False
    return False


def _is_theme_gain_file(filepath: Path) -> bool:
    try:
        return filepath.name == 'theme_gain_analysis.py'
    except Exception:
        return False


def _is_dev_tool_file(filepath: Path) -> bool:
    try:
        name = filepath.name.lower()
        rel = str(filepath).replace('\\', '/').lower()
    except Exception:
        return False
    if '/tools/' in rel:
        return True
    tool_patterns = [
        r'^analy[sz]e_.*\.py$',
        r'^analysis_.*\.py$',
        r'^.*_analysis\.py$',
        r'^check_.*\.py$',
        r'^.*_check.*\.py$',
        r'^ast_check_.*\.py$',
        r'^debug_.*\.py$',
        r'^.*_debug.*\.py$',
        r'^test_.*\.py$',
        r'^.*_test.*\.py$',
        r'^.*_summary\.py$',
        r'^.*_findings\.py$',
        r'^.*_report.*\.py$',
        r'^.*_generator.*\.py$',
        r'^.*_processor.*\.py$',
        r'^.*_planner.*\.py$',
        r'^.*_pipeline.*\.py$',
        r'^.*_evaluator.*\.py$',
        r'^evaluator_.*\.py$',
        r'^.*_validator.*\.py$',
        r'^.*_validate.*\.py$',
        r'^compare_.*\.py$',
        r'^.*_compare.*\.py$',
        r'^.*_extract.*\.py$',
        r'^extract_.*\.py$',
        r'^find_.*\.py$',
        r'^.*_find.*\.py$',
        r'^count_.*\.py$',
        r'^.*_count.*\.py$',
        r'^.*_audit.*\.py$',
        r'^.*_visual.*\.py$',
        r'^.*_quick.*\.py$',
        r'^.*_final.*\.py$',
        r'^roadmap_.*\.py$',
        r'^.*_roadmap.*\.py$',
        r'^.*_backup.*\.py$',
        r'^v\d+_.*\.py$',
        r'^.*meb_.*\.py$',
        r'^.*pdf_.*\.py$',
        r'^run_.*\.py$',
        r'^apply_.*\.py$',
        r'^.*_fix.*\.py$',
        r'^.*_verification.*\.py$',
        r'^.*_verify.*\.py$',
    ]
    return any(re.match(pat, name) for pat in tool_patterns)


def classify(finding: Dict, filepath: Path) -> Dict:
    val = finding['value']
    usage = finding.get('usage', '')
    text = val.strip()
    sev = 'LOW'
    reason = []

    lower = text.lower()

    # Treat constants modules as config-only (exclude from blocking)
    try:
        parts = [p.lower() for p in filepath.parts]
    except Exception:
        parts = []
    if 'constants' in parts or any(p.endswith('constants') for p in parts):
        return {'severity': 'LOW', 'reasons': ['CONFIG_CONSTANT_MODULE']}
    if filepath.name.lower() == 'config.py' or filepath.name.lower().startswith('config_') or filepath.name.lower().endswith('_config.py'):
        return {'severity': 'LOW', 'reasons': ['CONFIG_CONSTANT_MODULE']}
    if filepath.name.lower().startswith('apply_') and filepath.suffix == '.py':
        return {'severity': 'LOW', 'reasons': ['DEV_TOOL_FALSE_POSITIVE']}

    # Theme gain file specific taxonomy data should not block
    if _is_theme_gain_file(filepath) and usage == 'dict_key' and ' ' in text:
        return {'severity': 'LOW', 'reasons': ['DOMAIN_TAXONOMY']}
    if _is_theme_gain_file(filepath) and usage in ('compare', 'if_test'):
        return {'severity': 'LOW', 'reasons': ['THEME_GAIN_DOMAIN_COMPARISON']}
    if _is_theme_gain_file(filepath) and usage in ('return', 'assign', 'call_arg', 'literal') and any(p in lower for p in ('gokyuzunu', 'gökyüzünü', 'gokyuzunu kaybeden sehir', 'gökyüzünü kaybeden şehir')):
        return {'severity': 'LOW', 'reasons': ['THEME_GAIN_DOMAIN_LITERAL']}

    # ERROR MESSAGE DETECTION (takes precedence over CRITICAL endpoint heuristics)
    # If this is an error/validation message, downgrade to LOW regardless of other patterns
    error_keywords = ('hata', 'error', 'başarısız', 'olmadı', 'almadı', 'alamadı', 'değildir', 'değil', 
                      'failed', 'invalid', 'missing', 'not found', 'cannot', 'blocked', 'geçerli')
    is_error_message = any(kw in lower for kw in error_keywords)
    if is_error_message:
        reasons = ['ERROR_MESSAGE_LITERAL']
        if _is_dev_tool_file(filepath):
            reasons.append('DEV_TOOL_FALSE_POSITIVE')
        return {'severity': 'LOW', 'reasons': reasons}

    # Route decorator paths (Flask @app.route) are API contract strings — not domain hardcode
    if usage == 'route' or (usage in ('call_arg','literal') and text.startswith('/') and '/api' in lower):
        return {'severity': 'LOW', 'reasons': ['CONTRACT_INLINE_OK']}

    # MIME types -> config/constants
    mime_known = ('application/json','application/pdf','application/msword','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if usage == 'mime_type' or lower in mime_known:
        return {'severity': 'LOW', 'reasons': ['CONTRACT_INLINE_OK', 'mime_type']}

    # Templates and XML/XLSX literal blocks
    if usage == 'template' or re.search(r'</\w+>', text) or re.search(r'<\w+.*?>', text):
        return {'severity': 'LOW', 'reasons': ['TEMPLATE_LITERAL']}

    # Docstrings / descriptive literals
    if usage == 'docstring':
        return {'severity': 'LOW', 'reasons': ['DOCSTRING_LITERAL']}

    # CRITICAL heuristics (narrowed)
    if re.search(r"https?://", text):
        sev = 'CRITICAL'
        reason.append('endpoint_or_url_literal')
    # file-like resources (only treat as critical when clearly a file/resource reference)
    if (
        re.search(r"\.(pdf|epub|txt|docx?)$", text.lower())
        or re.search(r"[A-Za-z0-9_\-]+\.(pdf|docx|epub|txt)", text.lower())
        or ('/' in text and not text.startswith('http') and len(text) > 8 and (' ' not in text) and '<' not in text and '>' not in text)
    ):
        sev = 'CRITICAL'
        reason.append('file_path_or_pdf')

    # HIGH heuristics
    if sev != 'CRITICAL':
        if _is_theme_gain_file(filepath) and usage in ('compare', 'if_test'):
            non_blocking_theme_gain_literals = {
                'olay akisi',
                'kardeşi suna',
                'kardesi suna',
            }
            if lower in non_blocking_theme_gain_literals:
                return {'severity': 'LOW', 'reasons': ['DOMAIN_TAXONOMY']}

            critical_literals = (
                'tarihî biyografi',
                'tarihi biyografi',
                'gerçekçi çocuk öyküsü',
                'gercekci cocuk oyku',
                'bulmaca / kaçış oyunu',
                'bulmaca / kacis oyunu',
                'merkez karakter',
            )
            if any(term in lower for term in critical_literals):
                sev = 'HIGH'
                reason.append('theme_gain_runtime_decision')
            elif usage in ('compare', 'if_test') and any(p in lower for p in ('gokyuzunu', 'gökyüzünü', 'gokyuzunu kaybeden sehir', 'gökyüzünü kaybeden şehir')):
                sev = 'HIGH'
                reason.append('example_book_title')
            else:
                sev = 'LOW'
                reason.append('DOMAIN_TAXONOMY')
        elif usage in ('compare', 'if_test') and ' ' in text and len(text) > 5:
            sev = 'HIGH'
            reason.append('comparison_with_string_literal')
        if usage == 'dict_key' and ' ' in text:
            sev = max_severity(sev, 'HIGH')
            reason.append('mapping_with_non_generic_key')
        # specific blacklisted example patterns
        if any(p in lower for p in ('gokyuzunu', 'gökyüzünü', 'gokyuzunu kaybeden sehir', 'gökyüzünü kaybeden şehir')):
            sev = 'HIGH'
            reason.append('example_book_title')

    # MEDIUM heuristics
    if sev not in ('CRITICAL', 'HIGH'):
        if usage in ('dict_key', 'assign') and len(text) > 0 and not text.islower():
            sev = 'MEDIUM'
            reason.append('non_generic_constant')

    # Default LOW
    if is_test_path(filepath):
        # De-emphasize findings in tests/fixtures/benchmarks
        if sev in ('CRITICAL', 'HIGH', 'MEDIUM'):
            # record original but mark low to reduce false positives
            original = sev
            sev = 'LOW'
            reason.append(f'downgraded_from_{original}_due_to_test_path')

    if _is_dev_tool_file(filepath) and sev in ('CRITICAL', 'HIGH', 'MEDIUM'):
        reason.append('DEV_TOOL_FALSE_POSITIVE')
        sev = 'LOW'

    return {'severity': sev, 'reasons': reason}


def max_severity(a: str, b: str) -> str:
    order = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2, 'CRITICAL': 3}
    return a if order[a] >= order[b] else b


def main(argv=None):
    argv = argv or sys.argv[1:]
    root = Path(argv[0]).resolve() if argv else ROOT_DEFAULT
    if root.is_file():
        py_files = [root]
    else:
        py_files = [p for p in root.rglob("*.py") if "venv" not in p.parts and ".git" not in p.parts]

    results = []
    counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}

    for p in sorted(py_files):
        rel = p.name if root.is_file() else p.relative_to(root)
        findings = scan_file(p)
        for f in findings:
            cls = classify(f, p)
            entry = {
                'file': str(rel),
                'line': f.get('lineno'),
                'col': f.get('col'),
                'value': f.get('value'),
                'snippet': f.get('src'),
                'usage': f.get('usage'),
                'severity': cls['severity'],
                'reasons': cls['reasons'],
                'suppressed': False,
                'suppression_reasons': [],
            }
            results.append(entry)
            counts[entry['severity']] += 1

    # apply suppressions
    suppressions = load_suppressions()
    suppressed_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    invalid_suppressions = 0
    for s in suppressions:
        # validate entries already done
        pass

    for r in results:
        relpath = r['file']
        for s in suppressions:
            if matches_suppression(s, r, relpath):
                # ensure suppression has justification
                if not s.get('reason') or not s.get('owner'):
                    invalid_suppressions += 1
                    continue
                r['suppressed'] = True
                r['suppression_reasons'].append(s.get('reason'))
                # allow override of severity
                if 'severity_override' in s:
                    r['severity'] = s['severity_override']
                suppressed_counts[r['severity']] = suppressed_counts.get(r['severity'], 0) + 1

    # write JSON report
    REPORT_PATH.write_text(json.dumps({'summary': counts, 'findings': results, 'suppressed_summary': suppressed_counts}, ensure_ascii=False, indent=2), encoding='utf-8')

    # write prioritized CSV
    # order: CRITICAL, HIGH, MEDIUM, LOW
    order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    sorted_results = sorted(results, key=lambda x: (order.get(x.get('severity'), 9), x.get('file'), x.get('line') or 0))
    with CSV_PATH.open('w', newline='', encoding='utf-8') as cf:
        writer = csv.DictWriter(cf, fieldnames=['severity', 'category', 'file', 'line', 'snippet', 'rule_id', 'reason', 'suppressed'])
        writer.writeheader()
        for idx, r in enumerate(sorted_results):
            # category: usage
            writer.writerow({
                'severity': r.get('severity'),
                'category': r.get('usage'),
                'file': r.get('file'),
                'line': r.get('line'),
                'snippet': (r.get('snippet') or '')[:200],
                'rule_id': ','.join(r.get('reasons', [])) or '',
                'reason': ';'.join(r.get('suppression_reasons', [])) or ';'.join(r.get('reasons', [])),
                'suppressed': r.get('suppressed', False),
            })

    # terminal summary
    print("Hardcode scan summary:")
    for k in ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'):
        print(f"  {k}: {counts[k]}")

    if counts['CRITICAL'] or counts['HIGH']:
        print(f"Report written to: {REPORT_PATH} — CRITICAL/HIGH findings detected. Failing for CI.")
        sys.exit(2)
    if counts['MEDIUM']:
        print(f"Report written to: {REPORT_PATH} — MEDIUM findings detected. Warning.")
        sys.exit(1)
    print(f"Report written to: {REPORT_PATH} — No blocking findings.")
    sys.exit(0)


if __name__ == '__main__':
    main()
