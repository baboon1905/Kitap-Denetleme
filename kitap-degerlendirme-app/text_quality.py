import re
from typing import Any, List


MOJIBAKE_SENTINELS = (
    "olaylarÄ±",
    "geÃ§er",
    "Ã¶zet",
    "paylaÅŸÄ±r",
    "Ã§Ã¶zÃ¼m",
    "Ãƒ",
    "Ã…",
    "Ã„",
    "Ã¢",
    "Â�",
    "ï¿½",
    "Ä±",
    "Ä°",
    "ÄŸ",
    "ÅŸ",
    "Å",
    "Ã¼",
    "Ãœ",
    "Ã¶",
    "Ã–",
    "Ã§",
    "Ã‡",
    "Ã®",
    "Ã¢",
    "Ãª",
)

MOJIBAKE_RE = re.compile("|".join(re.escape(item) for item in MOJIBAKE_SENTINELS))

COMMON_MOJIBAKE_REPLACEMENTS = {
    "Ä±": "ı",
    "Ä°": "İ",
    "ÄŸ": "ğ",
    "Ä": "Ğ",
    "ÅŸ": "ş",
    "Å": "Ş",
    "Ã¼": "ü",
    "Ãœ": "Ü",
    "Ã¶": "ö",
    "Ã–": "Ö",
    "Ã§": "ç",
    "Ã‡": "Ç",
    "Ã®": "î",
    "Ã¢": "â",
    "Ãª": "ê",
    "â€™": "'",
    "â€œ": '"',
    "â€": '"',
    "â€“": "-",
    "â€”": "-",
    "â€¦": "...",
    "Ã¢â‚¬â„¢": "'",
    "Ã¢â‚¬Å“": '"',
    "Ã¢â‚¬Â": '"',
    "Ã¢â‚¬â€œ": "-",
    "Ã¢â‚¬â€": "-",
    "Ã¢â‚¬Â¢": "-",
    "Ã¢Å“â€¦": "[Uygun]",
    "Ã¢Å“â€": "[Dusuk Risk]",
    "Ã¢Å¡Â ": "[Uyari]",
    "Ã¢ÂÅ’": "[Uygun Degil]",
    "ÄŸÅ¸â€Â´": "[Revizyon]",
    "Ã¢â€Â¹": "[Bilgi]",
    "Ã¢â€ â€™": "->",
}

ASCII_TURKISH_REPLACEMENTS = {
    "Uretken": "Üretken",
    "uretken": "üretken",
    "Sorgulayici": "Sorgulayıcı",
    "sorgulayici": "sorgulayıcı",
    "Iradeli": "İradeli",
    "Guvenli": "Güvenli",
    "guvenli": "güvenli",
    "Dusuk": "Düşük",
    "dusuk": "düşük",
}


def looks_mojibake(value: Any) -> bool:
    text = "" if value is None else str(value)
    if not text:
        return False
    return bool(MOJIBAKE_RE.search(text))


def _try_transcode(text: str) -> str:
    best = text
    best_score = len(MOJIBAKE_RE.findall(text))
    for source_encoding in ("latin1", "cp1252"):
        try:
            candidate = text.encode(source_encoding).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        score = len(MOJIBAKE_RE.findall(candidate))
        if score < best_score and len(candidate) >= max(1, int(len(text) * 0.55)):
            best = candidate
            best_score = score
    return best


def repair_mojibake(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    for _ in range(3):
        repaired = _try_transcode(text)
        if repaired == text:
            break
        text = repaired
    for old, new in COMMON_MOJIBAKE_REPLACEMENTS.items():
        text = text.replace(old, new)
    for old, new in ASCII_TURKISH_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def collect_text_quality_issues(payload: Any, path: str = "root", limit: int = 40) -> List[str]:
    issues: List[str] = []

    def offending_excerpt(text: str) -> str:
        match = MOJIBAKE_RE.search(text)
        if not match:
            return text[:80]
        start = max(0, match.start() - 40)
        return text[start:start + 120]

    def visit(value: Any, current_path: str) -> None:
        if len(issues) >= limit:
            return
        if isinstance(value, dict):
            for key, item in value.items():
                visit(item, f"{current_path}.{key}")
            return
        if isinstance(value, (list, tuple)):
            for index, item in enumerate(value):
                visit(item, f"{current_path}[{index}]")
            return
        if isinstance(value, str):
            repaired = repair_mojibake(value)
            if looks_mojibake(repaired):
                issues.append(f"{current_path}: {offending_excerpt(repaired)}")

    visit(payload, path)
    return issues


def repair_payload_text(payload: Any) -> Any:
    if isinstance(payload, dict):
        repaired = {}
        for key, value in payload.items():
            new_key = repair_mojibake(key) if isinstance(key, str) else key
            repaired[new_key] = repair_payload_text(value)
        return repaired
    if isinstance(payload, list):
        return [repair_payload_text(item) for item in payload]
    if isinstance(payload, tuple):
        return tuple(repair_payload_text(item) for item in payload)
    if isinstance(payload, str):
        return repair_mojibake(payload)
    return payload


def sanitize_output_payload(payload: Any) -> Any:
    return repair_payload_text(payload)


def assert_no_mojibake(payload: Any, path: str = "root") -> None:
    issues = collect_text_quality_issues(payload, path=path, limit=10)
    if issues:
        raise ValueError("MOJIBAKE_DETECTED: " + "; ".join(issues))


def first_text(*values: Any) -> str:
    for value in values:
        text = repair_mojibake(value).strip()
        if text:
            return text
    return ""
