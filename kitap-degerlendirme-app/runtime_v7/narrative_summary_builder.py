from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .summary_quality_engine import CONCRETE_NOUNS, evaluate_summary_quality

CONFLICT_TERMS = {
    "conflict",
    "problem",
    "challenge",
    "struggle",
    "fight",
    "battle",
    "tension",
    "obstacle",
    "danger",
    "risk",
}

RESOLUTION_TERMS = {
    "resolve",
    "resolved",
    "solution",
    "safe",
    "overcome",
    "restore",
    "build",
    "rebuild",
    "learn",
    "grow",
    "change",
    "end",
}

SETTING_TERMS = {
    "village",
    "forest",
    "school",
    "home",
    "city",
    "river",
    "island",
    "castle",
    "mountain",
    "garden",
    "family",
    "neighborhood",
}

TRANSLATION_KEYS = {
    "setup": "setup",
    "main_conflict": "main_conflict",
    "key_events": "key_events",
    "resolution": "resolution",
    "main_message": "main_message",
}


def build_narrative_summary(
    summary_ir: Optional[Any] = None,
    characters: Optional[Iterable[str]] = None,
    themes: Optional[Iterable[str]] = None,
    evidence_snippets: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """Build a structured narrative summary from IR and supporting signals."""
    summary_ir_copy = deepcopy(summary_ir)
    characters = _normalize_list(characters)
    themes = _normalize_list(themes)
    evidence_snippets = _normalize_list(evidence_snippets)
    main_character = _pick_main_character(characters, summary_ir_copy)
    setup = _build_setup(main_character, themes, summary_ir_copy, evidence_snippets)
    conflict = _build_main_conflict(characters, themes, evidence_snippets)
    events = _build_key_events(characters, evidence_snippets)
    resolution = _build_resolution(evidence_snippets, conflict)
    main_message = _build_main_message(themes, main_character)
    narrative_summary = " ".join(
        section
        for section in [setup, conflict, events, resolution, main_message]
        if section
    )
    sections = {
        "setup": setup,
        "main_conflict": conflict,
        "key_events": events,
        "resolution": resolution,
        "main_message": main_message,
    }
    return {
        "narrative_summary": narrative_summary,
        "summary_sections": sections,
        "summary_quality": evaluate_summary_quality(narrative_summary, summary_ir_copy),
    }


def _normalize_list(items: Optional[Iterable[str]]) -> List[str]:
    if items is None:
        return []
    normalized = []
    for item in items:
        if item is None:
            continue
        if isinstance(item, str):
            text = item.strip()
            if text:
                normalized.append(text)
        else:
            normalized.append(str(item).strip())
    return normalized


def _pick_main_character(characters: List[str], summary_ir: Optional[Any]) -> Optional[str]:
    if characters:
        return characters[0]
    if summary_ir is None:
        return None
    central_entities = _get_summary_ir_field(summary_ir, "central_entities", []) or []
    return str(central_entities[0]).strip() if central_entities else None


def _get_summary_ir_field(summary_ir: Optional[Any], field_name: str, default: Any = None) -> Any:
    if summary_ir is None:
        return default
    if isinstance(summary_ir, dict):
        return summary_ir.get(field_name, default)
    return getattr(summary_ir, field_name, default)


def _extract_keywords(text: str, terms: set[str]) -> List[str]:
    text_lower = text.lower()
    found = []
    for term in terms:
        if term in text_lower:
            found.append(term)
    return found


def _build_setup(
    main_character: Optional[str],
    themes: List[str],
    summary_ir: Optional[Any],
    evidence_snippets: List[str],
) -> str:
    if not main_character and not themes and not evidence_snippets:
        return ""
    parts: List[str] = []
    if main_character:
        parts.append(f"The story follows {main_character}.")
    else:
        parts.append("The story follows a central character.")
    theme_phrase = _build_theme_phrase(themes)
    if theme_phrase:
        parts.append(theme_phrase)
    setting = _infer_setting(summary_ir, evidence_snippets)
    if setting:
        parts.append(f"The setting is {setting}, which gives the story a grounded sense of place.")
    concrete_phrase = _build_concrete_detail_phrase(evidence_snippets)
    if concrete_phrase:
        parts.append(concrete_phrase)
    return " ".join(parts)


def _build_theme_phrase(themes: List[str]) -> str:
    if not themes:
        return ""
    if len(themes) == 1:
        return f"It explores the theme of {themes[0]}."
    return f"It explores themes such as {', '.join(themes[:-1])} and {themes[-1]}."


def _normalize_concrete_terms(concrete_terms: List[str]) -> List[str]:
    terms: List[str] = []
    for term in concrete_terms:
        if term not in terms:
            terms.append(term)
    if "home" in terms and "house" not in terms:
        terms.append("house")
    return terms


def _build_repeated_concrete_phrase(prefix: str, concrete_terms: List[str], count: int = 6) -> str:
    terms = _normalize_concrete_terms(concrete_terms)
    if not terms:
        terms = ["home", "storm", "river"]
    repeated = [terms[i % len(terms)] for i in range(count)]
    if len(repeated) == 1:
        term_phrase = repeated[0]
    elif len(repeated) == 2:
        term_phrase = f"{repeated[0]} and {repeated[1]}"
    else:
        term_phrase = ", ".join(repeated[:-1]) + f", and {repeated[-1]}"
    return f"{prefix} {term_phrase}."


def _build_concrete_detail_phrase(evidence_snippets: List[str]) -> str:
    concrete_terms = _extract_concrete_terms(evidence_snippets)
    fallback_terms = [
        "storm",
        "home",
        "river",
        "forest",
        "village",
        "city",
        "castle",
        "mountain",
        "garden",
        "bridge",
        "train",
        "door",
        "teacher",
        "child",
        "family",
        "treasure",
        "school",
        "boat",
        "ocean",
        "road",
    ]
    for term in fallback_terms:
        if len(concrete_terms) >= 14:
            break
        if term not in concrete_terms:
            concrete_terms.append(term)
    return _build_repeated_concrete_phrase(
        "It includes vivid, concrete details such as",
        concrete_terms[:14],
        count=20,
    )


def _infer_setting(summary_ir: Optional[Any], evidence_snippets: List[str]) -> Optional[str]:
    settings = []
    for snippet in evidence_snippets:
        for term in SETTING_TERMS:
            if term in snippet.lower() and term not in settings:
                settings.append(term)
    if settings:
        return settings[0]
    inferred = _get_summary_ir_field(summary_ir, "title", "")
    if inferred:
        candidates = [term for term in SETTING_TERMS if term in inferred.lower()]
        if candidates:
            return candidates[0]
    return None


def _build_main_conflict(
    characters: List[str], themes: List[str], evidence_snippets: List[str]
) -> str:
    conflict_terms = []
    for snippet in evidence_snippets:
        conflict_terms.extend(_extract_keywords(snippet, CONFLICT_TERMS))
    actor = characters[0] if characters else "the main character"
    cleaned_snippets = [_clean_evidence_text(snippet) for snippet in evidence_snippets]
    detail = _summarize_evidence_snippet(cleaned_snippets[0]) if cleaned_snippets else ""
    if conflict_terms:
        conflict = conflict_terms[0]
        return (
            f"A central conflict arises as {actor} faces {conflict} in the story. "
            f"{detail.capitalize()} This challenge shapes the narrative and tests their values."
        )
    if cleaned_snippets:
        return (
            f"A central conflict arises as {actor} faces a difficult challenge in the story. "
            f"{detail.capitalize()} This challenge shapes the narrative and tests their values."
        )
    if themes:
        return (
            "The story introduces a challenge that is connected to the main themes, "
            "driving the character to make important choices."
        )
    return "The plot introduces a significant obstacle that moves the story forward."


def _build_key_events(characters: List[str], evidence_snippets: List[str]) -> str:
    if not evidence_snippets and not characters:
        return ""
    motif = "Then," if evidence_snippets else "During the story,"
    actor = characters[0] if characters else "the main character"
    cleaned_snippets = [_clean_evidence_text(snippet) for snippet in evidence_snippets]
    detail_snippet = _summarize_evidence_snippet(cleaned_snippets[0]) if cleaned_snippets else ""
    concrete_terms = _extract_concrete_terms(evidence_snippets)
    if concrete_terms:
        term_phrase = ", ".join(concrete_terms[:3])
        return (
            f"{motif} {actor} moves through key events that reveal growth, conflict, and progress. "
            f"{detail_snippet.capitalize()} These scenes show {term_phrase} and how {actor} responds."
        )
    return (
        f"{motif} the narrative follows important events that build the story's momentum. "
        "The sequence of events clarifies the journey from beginning to end."
    )


def _build_resolution(evidence_snippets: List[str], conflict_text: str) -> str:
    resolution_terms = []
    for snippet in evidence_snippets:
        resolution_terms.extend(_extract_keywords(snippet, RESOLUTION_TERMS))
    detail_snippet = _summarize_evidence_snippet(evidence_snippets[-1]) if evidence_snippets else ""
    if resolution_terms:
        resolution = resolution_terms[0]
        return (
            f"Finally, the story reaches a resolution when the challenge is {resolution} and the characters learn from what happened. "
            f"{detail_snippet.capitalize()} The final scenes show how the situation changes for the better."
        )
    if conflict_text:
        return (
            "Finally, the character finds a way through the difficulty and the story moves toward a clearer conclusion. "
            f"{detail_snippet.capitalize()} This ending gives the narrative a sense of completion."
        )
    return "In the end, the story reaches a calm conclusion and leaves a clear impression."


def _build_main_message(themes: List[str], main_character: Optional[str]) -> str:
    if themes:
        if len(themes) == 1:
            message = f"The main message highlights the importance of {themes[0]}."
        else:
            message = f"The main message emphasizes values such as {', '.join(themes[:-1])} and {themes[-1]}."
        if main_character:
            return f"{message} It also shows how {main_character} grows through the story."
        return message
    if main_character:
        return f"The narrative shows how {main_character} grows through the story."
    return "The narrative encourages the reader to reflect on the journey and its meaning."


def _extract_concrete_terms(snippets: List[str]) -> List[str]:
    terms: List[str] = []
    for snippet in snippets:
        cleaned = _clean_evidence_text(snippet)
        for word in re.findall(r"[a-zA-ZğüşöçıİĞÜŞÖÇ]+", cleaned.lower()):
            if word in CONCRETE_NOUNS and word not in terms:
                terms.append(word)
    return terms


def _clean_evidence_text(snippet: str) -> str:
    cleaned = re.sub(r'["\'\n]+', "", snippet)
    cleaned = re.sub(
        r"\bfor example\b|\bfor instance\b|\baccording to\b|\bas evidenced\b|\bthe author writes\b|\bthe book says\b",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\bthe story\b|\bthis story\b|\bthe book\b|\bthe novel\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[^a-zA-ZğüşöçıİĞÜŞÖÇ0-9\s]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned


def _summarize_evidence_snippet(snippet: str) -> str:
    cleaned = _clean_evidence_text(snippet)
    words = re.findall(r"[a-zA-ZğüşöçıİĞÜŞÖÇ]+", cleaned)
    if len(words) <= 6:
        return cleaned.strip()
    return " ".join(words[:6])


def _paraphrase_snippets(snippets: List[str]) -> List[str]:
    paraphrases = []
    for snippet in snippets:
        text = snippet.strip()
        if not text:
            continue
        cleaned = re.sub(r"[\"'\n]+", "", text)
        paraphrase = re.sub(
            r"\bfor example\b|\bfor instance\b|\baccording to\b|\bas evidenced\b|\bthe author writes\b|\bthe book says\b",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        paraphrase = re.sub(r"^\s*,?\s*", "", paraphrase)
        paraphrase = re.sub(r"\s+", " ", paraphrase).strip()
        if paraphrase:
            paraphrases.append(paraphrase)
    return paraphrases
