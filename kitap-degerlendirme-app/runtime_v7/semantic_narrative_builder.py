"""
Narrative Structure Builder — Phase 3A & 3B

Purpose: Build narrative with 6-part semantic structure integrating Character Resolver
and Evidence Synthesizer for natural, semantically-aware storytelling.

Structure:
  1. Setup: Character introduction + themes + setting + concrete details
  2. Conflict: Main challenge (what, why, impact)
  3. Events: Chronological key events with character development
  4. Themes: Detailed theme explanations with supporting evidence
  5. Resolution: Character change and outcome
  6. Message: Central lesson/takeaway
"""

from typing import Optional, List, Dict, Any
import re
from copy import deepcopy

from runtime_v7.character_resolver import CharacterResolver
from runtime_v7.evidence_synthesizer import EvidenceSynthesizer


class SemanticNarrativeBuilder:
    """Builds 6-part semantic narrative with integrated character and evidence resolution."""
    
    def __init__(self, summary_ir: Optional[Dict[str, Any]] = None):
        """
        Initialize narrative builder.
        
        Args:
            summary_ir: Information representation with:
              - central_entities: list of character names
              - themes: list of themes
              - title: book title
              - places: list of locations
              - evidence_snippets: dict of {section: [evidence_texts]}
              - temporal_context: time period
              - historical_figures: optional list
        """
        self.summary_ir = summary_ir or {}
        self.character_resolver = CharacterResolver(summary_ir)
        self.evidence_synthesizer = EvidenceSynthesizer()
        
        # Extract IR fields
        self.characters = self._get_field("central_entities", [])
        self.themes = self._get_field("themes", [])
        self.places = self._get_field("places", [])
        self.title = self._get_field("title", "")
        self.evidence_snippets = self._get_field("evidence_snippets", {})
        self.temporal_context = self._get_field("temporal_context", "modern")
        self.key_events = self._get_field("key_events", [])
    
    def _get_field(self, field_name: str, default: Any = None) -> Any:
        """Get field from summary_ir safely."""
        if isinstance(self.summary_ir, dict):
            return self.summary_ir.get(field_name, default)
        return getattr(self.summary_ir, field_name, default)
    
    def build(self) -> Dict[str, Any]:
        """
        Build complete 6-part narrative.
        
        Returns:
        {
            "narrative": str,  # Full narrative
            "sections": {
                "setup": str,
                "conflict": str,
                "events": str,
                "themes": str,
                "resolution": str,
                "message": str
            },
            "metadata": {
                "character_count": int,
                "theme_count": int,
                "event_count": int,
                "word_count": int,
                "deterministic": bool
            }
        }
        """
        sections = {
            "setup": self._build_setup(),
            "conflict": self._build_conflict(),
            "events": self._build_events(),
            "themes": self._build_themes(),
            "resolution": self._build_resolution(),
            "message": self._build_message(),
        }
        
        # Combine sections into full narrative
        full_narrative = " ".join([s for s in sections.values() if s])
        
        # Sanitize
        full_narrative = self.character_resolver.sanitize_for_narrative(full_narrative)
        
        return {
            "narrative": full_narrative,
            "sections": sections,
            "metadata": {
                "character_count": len(self.characters),
                "theme_count": len(self.themes),
                "event_count": len(self.key_events),
                "word_count": len(full_narrative.split()),
                "deterministic": True,
            }
        }
    
    def _build_setup(self) -> str:
        """
        Part 1: Setup
        
        Introduces: character(s), setting, themes, concrete details.
        Structure: "Character is [descriptor] living/growing in [place/time].
                    The story explores [themes]. [Concrete detail]."
        """
        if not self.characters:
            return ""
        
        # Get primary character
        primary_char = self.characters[0]
        
        # Resolve character
        char_result = self.character_resolver.resolve_entity(primary_char)
        char_name = char_result.get("resolved_name", primary_char)
        
        # Build place reference
        place_ref = ""
        if self.places:
            place = self._sanitize_place(self.places[0])
            place_ref = f" in {place}"
        
        # Build theme reference
        theme_ref = ""
        if self.themes:
            if len(self.themes) == 1:
                theme_ref = f"explores the theme of {self.themes[0]}"
            else:
                themes_str = ", ".join(self.themes[:-1]) + f", and {self.themes[-1]}"
                theme_ref = f"explores the themes of {themes_str}"
        
        # Combine
        setup = f"This is the story of {char_name}{place_ref}. "
        if theme_ref:
            setup += f"It {theme_ref}. "
        
        # Add concrete detail if available
        setup_evidence = self.evidence_snippets.get("setup", [])
        if setup_evidence:
            concrete = self._clean_evidence_text(setup_evidence[0])
            if concrete:
                setup += concrete.lower() + " "
        
        return setup.strip()
    
    def _build_conflict(self) -> str:
        """
        Part 2: Conflict
        
        Describes: main challenge, what causes it, why it matters.
        Structure: "Character faces [conflict] because [reason].
                    This means [impact/stakes]."
        """
        conflict_evidence = self.evidence_snippets.get("conflict", [])
        
        if not conflict_evidence:
            return "The story presents a central challenge that tests the main character."
        
        # Use evidence text directly to preserve concrete details without artificial amplification
        main_conflict = self._clean_evidence_text(conflict_evidence[0])
        full_conflict = main_conflict
        if len(conflict_evidence) > 1:
            impact = self._clean_evidence_text(conflict_evidence[1])
            if impact:
                full_conflict += " " + impact.lower()
        
        return full_conflict.strip()
    
    def _build_resolution(self) -> str:
        """
        Part 5: Resolution
        
        Describes: how conflict is resolved and character change.
        Structure: "[Character] overcomes [conflict], learning [lesson].
                    By the end, [new state/change]."
        """
        if not self.characters:
            return ""
        
        primary_char = self.characters[0]
        char_result = self.character_resolver.resolve_entity(primary_char)
        char_name = char_result.get("resolved_name", primary_char)
        
        resolution_evidence = self.evidence_snippets.get("resolution", [])
        
        if resolution_evidence:
            resolved = self._clean_evidence_text(resolution_evidence[0])
            return f"{char_name} finds a way forward. {resolved}"

        return "Metindeki mevcut kanıtlar, çatışmanın nasıl sonuçlandığını sınırlı biçimde gösterir."

    def _build_message(self) -> str:
        """
        Part 6: Message

        Central takeaway or lesson from the story.
        Single, clear sentence about what the story teaches.
        """
        if not self.themes:
            return "This story is about the main journey and what it teaches."

        primary_theme = self.themes[0]
        if len(self.characters) > 1:
            return (
                f"This story is about {primary_theme} and how it shapes the way people work "
                f"through the challenge together."
            )

        return (
            f"This story is about {primary_theme} and how it helps the character learn "
            f"from the events that unfold."
        )

    def _sanitize_place(self, place: str) -> str:
        """Remove articles and normalize place name."""
        place = place.lower().strip()
        for article in ["the ", "a ", "an "]:
            if place.startswith(article):
                place = place[len(article):]
        return place

    def _clean_evidence_text(self, text: str) -> str:
        """Clean evidence text without adding artificial concrete terms."""
        if not isinstance(text, str) or not text.strip():
            return ""

        cleaned = self.evidence_synthesizer._remove_markers(text)
        cleaned = re.sub(r"\s*\([^)]*\)\s*", " ", cleaned)
        cleaned = " ".join(cleaned.split())
        if not cleaned.endswith((".", "!", "?")):
            cleaned += "."
        return cleaned

    def _build_event_sentence(self, text: str, transition: str = "") -> str:
        """Build a single event sentence from evidence or key event text."""
        cleaned = self._clean_evidence_text(text)
        if not cleaned:
            return ""
        if transition:
            sentence = f"{transition} {cleaned}"
        else:
            sentence = cleaned
        return sentence.strip()

    def _build_events(self) -> str:
        """
        Part 3: Events

        Describes: key events in chronological order with character development.
        Structure: "First, [event]. Then [event]. Meanwhile [event]."
        """
        events_texts = []
        if self.evidence_snippets.get("setup"):
            events_texts.append(self.evidence_snippets["setup"][0])
        elif self.key_events:
            events_texts.append(self.key_events[0])

        if self.evidence_snippets.get("conflict"):
            events_texts.append(self.evidence_snippets["conflict"][0])
        elif len(self.key_events) > 1:
            events_texts.append(self.key_events[1])

        if self.evidence_snippets.get("events"):
            events_texts.extend(self.evidence_snippets["events"][:2])
        elif len(self.key_events) > 2:
            events_texts.append(self.key_events[2])

        if self.evidence_snippets.get("resolution"):
            events_texts.append(self.evidence_snippets["resolution"][0])
        elif len(self.key_events) > 3:
            events_texts.append(self.key_events[3])

        # Ensure at least three steps when evidence or key events are available
        while len(events_texts) < 3 and len(self.key_events) > len(events_texts):
            events_texts.append(self.key_events[len(events_texts)])

        if not events_texts and self.themes:
            primary_theme = self.themes[0]
            main_char = self.characters[0] if self.characters else "The main character"
            events_texts = [
                f"{main_char} begins the story with a focus on {primary_theme}.",
                f"Then, {main_char.lower()} faces a challenge that tests {primary_theme}.",
                f"Finally, {main_char.lower()} learns what {primary_theme} means for the journey.",
            ]

        if not events_texts:
            return ""

        transitions = ["First,", "Then,", "Soon after,", "Meanwhile,", "Finally,"]
        events_parts = []
        for idx, event_text in enumerate(events_texts[:5]):
            transition = transitions[idx % len(transitions)]
            event_sentence = self._build_event_sentence(event_text, transition)
            if event_sentence:
                events_parts.append(event_sentence)

        return " ".join(events_parts).strip()

    def _build_themes(self) -> str:
        """
        Part 4: Themes (Detailed)

        Describes: how themes are developed with examples from the story.
        Structure: "[Theme] is shown through [example]. In particular, [specific instance]."
        """
        if not self.themes:
            return ""

        theme_parts = []
        for theme in self.themes:
            theme_part = f"The theme of {theme} is developed through the story's events."
            theme_evidence = self.evidence_snippets.get(f"theme_{theme.lower()}", [])
            if theme_evidence:
                support = self._clean_evidence_text(theme_evidence[0])
                if support:
                    theme_part += f" {support}"
            elif self.evidence_snippets.get("conflict"):
                conflict_example = self._clean_evidence_text(self.evidence_snippets["conflict"][0])
                if conflict_example:
                    theme_part += f" In particular, {conflict_example.lower()}"
            theme_parts.append(theme_part)

        return " ".join(theme_parts).strip()
