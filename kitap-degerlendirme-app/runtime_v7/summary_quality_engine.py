from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional

CONFLICT_KEYWORDS = {
    "conflict",
    "problem",
    "fight",
    "battle",
    "challenge",
    "struggle",
    "tension",
    "clash",
}

RESOLUTION_KEYWORDS = {
    "resolve",
    "resolved",
    "solution",
    "finally",
    "therefore",
    "so",
    "result",
    "outcome",
    "safe",
    "learned",
    "afterward",
    "afterwards",
}

MAIN_MESSAGE_KEYWORDS = {
    "story is about",
    "the book is about",
    "this story is about",
    "it follows",
    "it tells",
    "the story follows",
    "the book follows",
    "the story is about",
    "the novel is about",
    "in this book",
    "in this story",
    "the book tells",
}

EVIDENCE_MARKERS = {
    "for example",
    "for instance",
    "according to",
    "the author writes",
    "the book says",
    "as evidenced",
    "because",
    "therefore",
    "thus",
    "as shown",
}

CONCRETE_NOUNS = {
    "school",
    "forest",
    "river",
    "house",
    "village",
    "door",
    "train",
    "boat",
    "teacher",
    "mother",
    "father",
    "child",
    "friend",
    "family",
    "community",
    "classroom",
    "forest",
    "treasure",
    "island",
    "city",
    "castle",
    "storm",
    "mountain",
    "garden",
    "ocean",
    "bridge",
    "road",
    "home",
}

PRONOUNS = {"he", "she", "they", "him", "her", "them", "his", "hers", "their", "main character"}


def evaluate_summary_quality(summary_text: str, summary_ir: Optional[Any] = None) -> Dict[str, Any]:
    """Evaluate summary quality based on narrative and summary IR cues."""
    if summary_text is None:
        summary_text = ""

    summary_text = str(summary_text).strip()
    original_summary_ir = deepcopy(summary_ir)
    text_lower = summary_text.lower()
    sentences = _split_sentences(summary_text)
    words = _extract_words(summary_text)
    num_sentences = len(sentences)
    num_words = len(words)
    unique_words = len(set(words))

    if num_words == 0:
        return {
            "summary_quality_score": 0.0,
            "coverage": 0.0,
            "coherence": 0.0,
            "character_presence": 0.0,
            "conflict_present": False,
            "resolution_present": False,
            "main_message_present": False,
            "evidence_concatenation_detected": False,
            "repetition_score": 0.0,
            "concreteness_score": 0.0,
            "information_density": 0.0,
            "passed": False,
        }

    coverage = _compute_coverage(text_lower, summary_ir, num_sentences)
    coherence = _compute_coherence(sentences, summary_ir)
    character_presence = _compute_character_presence(text_lower, summary_ir)
    conflict_present = _has_conflict(text_lower, summary_ir)
    resolution_present = _has_resolution(text_lower, summary_ir)
    main_message_present = _has_main_message(text_lower)
    evidence_concatenation_detected = _detect_evidence_concatenation(text_lower, sentences)
    repetition_score = _compute_repetition_score(sentences)
    concreteness_score = _compute_concreteness_score(words, text_lower, summary_ir)
    information_density = _compute_information_density(unique_words, num_words)

    base_score = 0.20 * coverage
    base_score += 0.18 * coherence
    base_score += 0.15 * character_presence
    base_score += 0.12 * (1.0 if conflict_present else 0.0)
    base_score += 0.12 * (1.0 if resolution_present else 0.0)
    base_score += 0.08 * (1.0 if main_message_present else 0.0)
    base_score += 0.10 * concreteness_score
    base_score += 0.05 * information_density

    penalties = 0.0
    if evidence_concatenation_detected:
        penalties += 0.20
    penalties += min(0.25, repetition_score)
    if num_words < 30:
        penalties += 0.15
    if character_presence < 0.35:
        penalties += 0.10
    if not conflict_present:
        penalties += 0.10
    if not resolution_present:
        penalties += 0.10

    quality_score = max(0.0, min(1.0, base_score - penalties))
    summary_quality_score = round(quality_score * 100.0, 1)
    short_summary = num_words < 30
    passed = (
        summary_quality_score >= 65.0
        and not evidence_concatenation_detected
        and character_presence >= 0.35
        and conflict_present
        and resolution_present
        and coherence >= 0.4
        and concreteness_score >= 0.06
        and not short_summary
    )

    result = {
        "summary_quality_score": summary_quality_score,
        "coverage": round(coverage, 3),
        "coherence": round(coherence, 3),
        "character_presence": round(character_presence, 3),
        "conflict_present": conflict_present,
        "resolution_present": resolution_present,
        "main_message_present": main_message_present,
        "evidence_concatenation_detected": evidence_concatenation_detected,
        "repetition_score": round(repetition_score, 3),
        "concreteness_score": round(concreteness_score, 3),
        "information_density": round(information_density, 3),
        "passed": passed,
    }

    if isinstance(summary_ir, dict):
        summary_ir.clear()
        summary_ir.update(original_summary_ir or {})

    return result


def _normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9ğüşöçıİĞÜŞÖÇ\s]", " ", text.lower())


def _split_sentences(text: str) -> List[str]:
    if not text:
        return []
    raw_sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [sent.strip() for sent in raw_sentences if sent.strip()]


def _extract_words(text: str) -> List[str]:
    return re.findall(r"[a-zA-ZğüşöçıİĞÜŞÖÇ]+", text.lower())


def _get_summary_ir_field(summary_ir: Optional[Any], field_name: str, default: Any = None) -> Any:
    if summary_ir is None:
        return default
    if isinstance(summary_ir, dict):
        return summary_ir.get(field_name, default)
    return getattr(summary_ir, field_name, default)


def _compute_coverage(text_lower: str, summary_ir: Optional[Any], num_sentences: int) -> float:
    central_entities = _get_summary_ir_field(summary_ir, "central_entities", []) or []
    themes = _get_summary_ir_field(summary_ir, "themes", []) or []
    if central_entities:
        matched = sum(1 for entity in central_entities if entity.lower() in text_lower)
        return min(1.0, matched / max(1, len(central_entities)))
    if themes:
        matched = sum(1 for theme in themes if theme.lower() in text_lower)
        return min(1.0, matched / max(1, len(themes)))
    return min(1.0, num_sentences / 5.0)


def _compute_coherence(sentences: List[str], summary_ir: Optional[Any]) -> float:
    if not sentences:
        return 0.0
    transition_phrases = {
        "then",
        "next",
        "after",
        "later",
        "while",
        "because",
        "therefore",
        "so",
        "however",
        "but",
        "in the end",
        "finally",
        "afterward",
        "afterwards",
        "meanwhile",
        "first",
        "before",
        "eventually",
    }
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "but",
        "or",
        "then",
        "so",
        "of",
        "to",
        "in",
        "on",
        "at",
        "for",
        "with",
        "from",
        "by",
        "about",
        "as",
        "is",
        "it",
        "this",
        "that",
        "his",
        "her",
        "their",
        "they",
        "he",
        "she",
        "we",
        "you",
    }
    central_entities = [
        str(entity).lower()
        for entity in (_get_summary_ir_field(summary_ir, "central_entities", []) or [])
        if entity
    ]
    transition_count = 0
    connected_pairs = 0
    entity_references = 0
    previous_words = None
    for sentence in sentences:
        low = sentence.lower()
        if any(phrase in low for phrase in transition_phrases):
            transition_count += 1
        if any(entity in low for entity in central_entities):
            entity_references += 1
        current_words = set(re.findall(r"[a-zA-ZğüşöçıİĞÜŞÖÇ]+", low)) - stop_words
        if previous_words is not None and current_words.intersection(previous_words):
            connected_pairs += 1
        previous_words = current_words
    transition_ratio = transition_count / len(sentences)
    connected_ratio = connected_pairs / max(1, len(sentences) - 1)
    entity_ratio = entity_references / len(sentences)
    main_message_bonus = 0.15 if any(phrase in sentences[0].lower() for phrase in MAIN_MESSAGE_KEYWORDS) else 0.0
    score = 0.2 + min(1.0, transition_ratio * 0.45 + connected_ratio * 0.35 + entity_ratio * 0.2 + main_message_bonus)
    return min(1.0, max(0.0, score))


def _compute_character_presence(text_lower: str, summary_ir: Optional[Any]) -> float:
    central_entities = _get_summary_ir_field(summary_ir, "central_entities", []) or []
    if central_entities:
        present = sum(1 for entity in central_entities if entity.lower() in text_lower)
        return min(1.0, present / max(1, len(central_entities)))
    pronoun_count = sum(1 for pronoun in PRONOUNS if pronoun in text_lower)
    return min(1.0, pronoun_count / 3.0)


def _has_conflict(text_lower: str, summary_ir: Optional[Any]) -> bool:
    if any(keyword in text_lower for keyword in CONFLICT_KEYWORDS):
        return True
    narrative_graph = _get_summary_ir_field(summary_ir, "narrative_graph", {}) or {}
    nodes = narrative_graph.get("nodes", []) if isinstance(narrative_graph, dict) else []
    for node in nodes:
        if isinstance(node, dict) and node.get("conflict"):
            return True
    return False


def _has_resolution(text_lower: str, summary_ir: Optional[Any]) -> bool:
    if any(keyword in text_lower for keyword in RESOLUTION_KEYWORDS):
        return True
    narrative_graph = _get_summary_ir_field(summary_ir, "narrative_graph", {}) or {}
    nodes = narrative_graph.get("nodes", []) if isinstance(narrative_graph, dict) else []
    for node in nodes:
        if isinstance(node, dict) and node.get("outcome"):
            return True
    return False


def _has_main_message(text_lower: str) -> bool:
    if any(keyword in text_lower for keyword in MAIN_MESSAGE_KEYWORDS):
        return True
    return len(_extract_words(text_lower)) >= 20 and "story" in text_lower


def _detect_evidence_concatenation(text_lower: str, sentences: List[str]) -> bool:
    if len(sentences) < 3:
        return False
    evidence_sentences = 0
    transition_count = 0
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(marker in sentence_lower for marker in EVIDENCE_MARKERS):
            evidence_sentences += 1
        if any(word in sentence_lower for word in ["then", "next", "after", "while", "however", "but"]):
            transition_count += 1
    if evidence_sentences >= max(2, len(sentences) // 2) and transition_count < len(sentences) // 2:
        return True
    return False


def _compute_repetition_score(sentences: List[str]) -> float:
    if not sentences:
        return 0.0
    normalized = [re.sub(r"\s+", " ", sentence.lower()).strip() for sentence in sentences]
    unique_count = len(set(normalized))
    return round(max(0.0, 1.0 - unique_count / len(normalized)), 3)


def _compute_concreteness_score(words: List[str], text_lower: str, summary_ir: Optional[Any]) -> float:
    if not words:
        return 0.0
    concrete_matches = sum(1 for word in words if word in CONCRETE_NOUNS)
    unique_concretes = len(set(word for word in words if word in CONCRETE_NOUNS))
    central_entities = _get_summary_ir_field(summary_ir, "central_entities", []) or []
    entity_mentions = sum(1 for entity in central_entities if entity.lower() in text_lower)
    score = (
        unique_concretes * 0.5
        + concrete_matches * 0.12
        + entity_mentions * 0.35
    ) / max(1, len(words))
    if any(marker in text_lower for marker in EVIDENCE_MARKERS):
        score = max(0.0, score - 0.05)
    return min(1.0, score)


def _compute_information_density(unique_words: int, num_words: int) -> float:
    if num_words == 0:
        return 0.0
    return min(1.0, unique_words / num_words + 0.1)
