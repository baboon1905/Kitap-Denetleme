"""
Character Resolver — Phase 1A

Purpose: Distinguish between characters, places, historical figures, and book titles
in summary IR and narrative generation.

Principle: Never mistake a place name for a character, or a book title for an entity.
"""

from typing import Optional, List, Dict, Any, Tuple


class CharacterResolver:
    """Resolves entities into proper categories: character, place, historical_figure, book_title."""
    
    def __init__(self, summary_ir: Optional[Dict[str, Any]] = None):
        """
        Initialize resolver with optional summary IR context.
        
        summary_ir may contain:
        - central_entities: list of main character names
        - places: list of location names
        - historical_figures: list of historical persons (if applicable)
        - title: book title
        - temporal_context: time period (modern, historical, etc.)
        """
        self.summary_ir = summary_ir or {}
        self.central_entities = self._get_field("central_entities", [])
        self.places = self._get_field("places", [])
        self.historical_figures = self._get_field("historical_figures", [])
        self.book_title = self._get_field("title", "")
        self.temporal_context = self._get_field("temporal_context", "modern")
    
    def _get_field(self, field_name: str, default: Any = None) -> Any:
        """Get field from summary_ir safely."""
        if isinstance(self.summary_ir, dict):
            return self.summary_ir.get(field_name, default)
        return getattr(self.summary_ir, field_name, default)
    
    def resolve_entity(self, entity_name: str) -> Dict[str, Any]:
        """
        Resolve a single entity to its proper type and context.
        
        Returns:
        {
            "name": entity_name,
            "type": "character" | "place" | "historical_figure" | "book_title" | "unknown",
            "confidence": float [0.0-1.0],
            "context": str (explanation),
            "resolved_name": str (normalized name or generic placeholder)
        }
        """
        if not entity_name or not isinstance(entity_name, str):
            return {
                "name": str(entity_name),
                "type": "unknown",
                "confidence": 0.0,
                "context": "Invalid entity input",
                "resolved_name": None
            }
        
        entity_lower = entity_name.lower().strip()
        
        # Check if it's the book title itself
        if self.book_title:
            book_title_lower = self.book_title.lower().strip()
            if entity_lower == book_title_lower:
                return {
                    "name": entity_name,
                    "type": "book_title",
                    "confidence": 1.0,
                    "context": "Exact match with book title",
                    "resolved_name": None  # Don't use book title as entity
                }
        
        # Check if it's a place
        for place in self.places:
            if place and entity_lower == place.lower().strip():
                return {
                    "name": entity_name,
                    "type": "place",
                    "confidence": 1.0,
                    "context": f"Matched in places list: {place}",
                    "resolved_name": place
                }
        
        # Check if it's a historical figure
        for hist_fig in self.historical_figures:
            if hist_fig and entity_lower == hist_fig.lower().strip():
                return {
                    "name": entity_name,
                    "type": "historical_figure",
                    "confidence": 1.0,
                    "context": f"Matched in historical_figures list: {hist_fig}",
                    "resolved_name": hist_fig
                }
        
        # Check if it's a central character
        for char in self.central_entities:
            if char and entity_lower == char.lower().strip():
                return {
                    "name": entity_name,
                    "type": "character",
                    "confidence": 1.0,
                    "context": f"Matched in central_entities list: {char}",
                    "resolved_name": char
                }
        
        # Try fuzzy matching for characters (partial match)
        char_fuzzy = self._fuzzy_match_entity(entity_lower, self.central_entities)
        if char_fuzzy:
            return {
                "name": entity_name,
                "type": "character",
                "confidence": 0.7,
                "context": f"Fuzzy matched to character: {char_fuzzy}",
                "resolved_name": char_fuzzy
            }
        
        # Try fuzzy matching for places
        place_fuzzy = self._fuzzy_match_entity(entity_lower, self.places)
        if place_fuzzy:
            return {
                "name": entity_name,
                "type": "place",
                "confidence": 0.6,
                "context": f"Fuzzy matched to place: {place_fuzzy}",
                "resolved_name": place_fuzzy
            }
        
        # Unknown entity
        return {
            "name": entity_name,
            "type": "unknown",
            "confidence": 0.0,
            "context": "Not found in character, place, or historical figures lists",
            "resolved_name": None
        }
    
    def _fuzzy_match_entity(self, entity_lower: str, candidate_list: List[str]) -> Optional[str]:
        """
        Fuzzy match entity against candidate list.
        
        Returns the best matching candidate if similarity >= 0.7, else None.
        """
        if not candidate_list:
            return None
        
        best_match = None
        best_score = 0.0
        
        for candidate in candidate_list:
            if not candidate:
                continue
            candidate_lower = candidate.lower().strip()
            score = self._string_similarity(entity_lower, candidate_lower)
            if score > best_score:
                best_score = score
                best_match = candidate
        
        # Only return if similarity is reasonably high
        if best_score >= 0.7:
            return best_match
        
        return None
    
    @staticmethod
    def _string_similarity(s1: str, s2: str) -> float:
        """Simple string similarity using character overlap."""
        if s1 == s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        
        # Check if one is substring of other
        if s1 in s2 or s2 in s1:
            return 0.8
        
        # Check common prefix length
        common_len = 0
        for i in range(min(len(s1), len(s2))):
            if s1[i] == s2[i]:
                common_len += 1
            else:
                break
        
        if common_len == 0:
            return 0.0
        
        return common_len / max(len(s1), len(s2))
    
    def resolve_entities(self, entities: List[str]) -> List[Dict[str, Any]]:
        """
        Resolve a list of entities.
        
        Returns list of resolved entity dictionaries.
        """
        if not entities:
            return []
        
        resolved = []
        for entity in entities:
            resolved.append(self.resolve_entity(entity))
        
        return resolved
    
    def get_characters_only(self, entities: List[str]) -> List[str]:
        """
        Filter entities list to return only confirmed characters.
        
        Returns list of character names (or generic placeholders).
        """
        characters = []
        for entity in entities:
            result = self.resolve_entity(entity)
            if result["type"] == "character" and result["confidence"] >= 0.7:
                resolved_name = result.get("resolved_name")
                if resolved_name:
                    if resolved_name not in characters:
                        characters.append(resolved_name)
        
        return characters
    
    def get_places_only(self, entities: List[str]) -> List[str]:
        """
        Filter entities list to return only confirmed places.
        """
        places = []
        for entity in entities:
            result = self.resolve_entity(entity)
            if result["type"] == "place" and result["confidence"] >= 0.6:
                resolved_name = result.get("resolved_name")
                if resolved_name:
                    if resolved_name not in places:
                        places.append(resolved_name)
        
        return places
    
    def sanitize_for_narrative(self, text: str) -> str:
        """
        Remove book title and place references that appear as generic nouns.
        
        Example: "In 'Dağın Ötesi', the hero..." → "In this story, the hero..."
        """
        result = text
        
        # Don't use book title
        if self.book_title:
            patterns = [
                f"'{self.book_title}'",
                f'"{self.book_title}"',
                f"the {self.book_title}",
                f"The {self.book_title}",
            ]
            for pattern in patterns:
                result = result.replace(pattern, "this story")
        
        return result
