from pathlib import Path

from tools.check_hardcode import classify


FILTER_PATH = Path('release-root/runtime_v7/evidence_quality_filter.py')


def test_validated_general_rule_fingerprints_are_narrowly_allowed():
    approved = [
        ('literal', r'^http[s]?://'),
        ('dict_key', r'\bam ca sı na\b'),
        ('dict_key', r'\bka ça mak\b'),
        ('dict_key', r'\bgi de cek\b'),
        ('dict_key', r'\bÇift li ğe\b'),
        ('dict_key', r'\bçift li ğe\b'),
    ]
    for usage, value in approved:
        result = classify({'value': value, 'usage': usage}, FILTER_PATH)
        assert result == {
            'severity': 'LOW',
            'reasons': ['VALIDATED_GENERAL_RULE_FINGERPRINT'],
        }


def test_validated_rule_fingerprint_rejects_near_matches():
    wrong_literal = classify(
        {'value': r'^https?://example.com', 'usage': 'literal'},
        FILTER_PATH,
    )
    wrong_usage = classify(
        {'value': r'\bam ca sı na\b', 'usage': 'literal'},
        FILTER_PATH,
    )
    wrong_file = classify(
        {'value': r'^http[s]?://', 'usage': 'literal'},
        Path('release-root/runtime_v7/another_filter.py'),
    )

    assert wrong_literal['severity'] == 'CRITICAL'
    assert wrong_usage['severity'] == 'LOW'  # Literal itself is benign, but not fingerprint-approved.
    assert wrong_usage['reasons'] != ['VALIDATED_GENERAL_RULE_FINGERPRINT']
    assert wrong_file['severity'] == 'CRITICAL'
