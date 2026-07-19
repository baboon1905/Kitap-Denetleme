"""
Theme Detailer — Phase 4

Purpose: Create detailed theme explanations with supporting examples and evidence
from the narrative, showing how themes are developed through story events.

Example:
  Input: theme="courage", events=["climb mountain", "face storm", "help friend"]
  Output: "Courage is shown when Elif climbs the mountain alone, when she endures
           the storm without giving up, and when she helps her friend escape
           despite her own fears."
"""

from typing import Optional, List, Dict, Any
from copy import deepcopy


class ThemeDetailer:
    """Creates detailed, evidence-supported theme explanations."""
    
    # Theme archetype patterns for automatic detail generation
    THEME_PATTERNS = {
        "courage": {
            "definition": "strength to face fear and do what is right",
            "actions": ["faces challenge", "overcomes fear", "takes action despite danger"],
            "indicators": ["bravely", "despite fear", "when afraid", "alone"],
        },
        "friendship": {
            "definition": "bond of mutual trust and support between people",
            "actions": ["helps each other", "works together", "supports through difficulty"],
            "indicators": ["together", "mutual help", "trust", "loyalty"],
        },
        "growth": {
            "definition": "personal development and change for the better",
            "actions": ["learns lesson", "overcomes limitation", "becomes stronger"],
            "indicators": ["grows", "learns", "changes", "becomes"],
        },
        "perseverance": {
            "definition": "continued effort despite obstacles",
            "actions": ["doesn't give up", "tries again", "keeps going"],
            "indicators": ["despite", "continues", "persists", "never gives up"],
        },
        "kindness": {
            "definition": "compassionate and generous treatment of others",
            "actions": ["helps someone in need", "shows mercy", "acts with compassion"],
            "indicators": ["kindly", "with care", "gentle", "compassionate"],
        },
    }
    
    def __init__(self):
        """Initialize theme detailer."""
        pass
    
    def detail_theme(self, theme_name: str, key_events: List[str], 
                    characters: Optional[List[str]] = None,
                    evidence_supporting: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create detailed theme explanation.
        
        Args:
            theme_name: Name of theme (e.g., "courage", "friendship")
            key_events: List of story events
            characters: List of character names
            evidence_supporting: List of evidence snippets supporting theme
        
        Returns:
        {
            "theme": str,
            "definition": str,
            "explanation": str,
            "supporting_instances": [str],
            "character_roles": [str],
            "word_count": int,
            "depth_score": float  # 0.0-1.0, higher = more detailed
        }
        """
        theme_lower = theme_name.lower().strip()
        
        # Get theme archetype if available
        archetype = self.THEME_PATTERNS.get(theme_lower, {})
        definition = archetype.get("definition", self._generic_definition(theme_name))
        
        # Build explanation
        explanation = self._build_explanation(theme_name, key_events, archetype)
        
        # Extract supporting instances from events
        supporting_instances = self._extract_supporting_instances(
            theme_lower, key_events, evidence_supporting or []
        )
        
        # Identify character roles
        character_roles = self._identify_character_roles(
            theme_name, characters or [], key_events
        )
        
        # Calculate depth score based on number of supporting instances
        depth_score = min(1.0, len(supporting_instances) / 3.0)
        
        return {
            "theme": theme_name,
            "definition": definition,
            "explanation": explanation,
            "supporting_instances": supporting_instances,
            "character_roles": character_roles,
            "word_count": len(explanation.split()),
            "depth_score": round(depth_score, 2),
        }
    
    def _generic_definition(self, theme_name: str) -> str:
        """Generate generic definition for unknown themes."""
        return f"{theme_name} is a central value explored throughout the story."
    
    def _build_explanation(self, theme_name: str, key_events: List[str],
                          archetype: Dict[str, Any]) -> str:
        """Build detailed explanation of theme."""
        theme_lower = theme_name.lower()
        
        if not key_events:
            definition = archetype.get("definition", self._generic_definition(theme_name))
            return f"{theme_name.capitalize()} is shown to be important to the characters."
        
        # Build explanation from events
        explanation = f"The theme of {theme_lower} is developed throughout the story. "
        
        # Find relevant events
        relevant_events = []
        for event in key_events[:3]:  # Use first 3 events max
            event_lower = event.lower()
            # Simple heuristic: check if theme words appear
            if any(indicator in event_lower 
                   for indicator in archetype.get("indicators", [])):
                relevant_events.append(event)
        
        if relevant_events:
            # Use found events
            if len(relevant_events) == 1:
                explanation += f"It is shown when {relevant_events[0]}."
            elif len(relevant_events) == 2:
                explanation += (f"It is shown when {relevant_events[0]}, "
                              f"and later when {relevant_events[1]}.")
            else:
                events_str = ", ".join(relevant_events[:-1]) + f", and {relevant_events[-1]}"
                explanation += f"It is shown when {events_str}."
        else:
            # Use generic pattern
            actions = archetype.get("actions", ["shows development"])
            explanation += f"The characters {actions[0]}, demonstrating {theme_lower}."
        
        return explanation
    
    def _extract_supporting_instances(self, theme_lower: str, 
                                      key_events: List[str],
                                      evidence: List[str]) -> List[str]:
        """Extract specific instances from events supporting the theme."""
        instances = []
        
        # Get indicators for this theme
        archetype = self.THEME_PATTERNS.get(theme_lower, {})
        indicators = archetype.get("indicators", [theme_lower])
        
        # Search events for theme-related content
        for event in key_events:
            event_lower = event.lower()
            # Check if event mentions theme indicators
            if any(indicator in event_lower for indicator in indicators):
                instances.append(event)
        
        # Also include specific evidence
        for evid in evidence:
            if evid and theme_lower in evid.lower():
                # Take first 20 words of evidence
                words = evid.split()[:20]
                instance = " ".join(words).strip()
                if instance and instance not in instances:
                    instances.append(instance)
        
        return instances[:3]  # Return max 3 instances
    
    def _identify_character_roles(self, theme_name: str,
                                 characters: List[str],
                                 key_events: List[str]) -> List[str]:
        """
        Identify which characters demonstrate the theme.
        
        Returns list of "Character: role" descriptions.
        """
        roles = []
        
        if not characters:
            return roles
        
        # Simple heuristic: first character is protagonist showing theme
        if len(characters) > 0:
            primary_char = characters[0]
            roles.append(f"{primary_char}: demonstrates {theme_name.lower()}")
        
        # Second character might show contrast or support
        if len(characters) > 1:
            secondary_char = characters[1]
            roles.append(f"{secondary_char}: challenges or supports {theme_name.lower()}")
        
        return roles
    
    def detail_multiple_themes(self, theme_names: List[str],
                              key_events: List[str],
                              characters: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Detail multiple themes.
        
        Args:
            theme_names: List of theme names
            key_events: List of story events
            characters: List of character names
        
        Returns:
            List of detailed theme dictionaries
        """
        if not theme_names:
            return []
        
        results = []
        for theme in theme_names:
            detailed = self.detail_theme(theme, key_events, characters)
            results.append(detailed)
        
        return results
    
    def create_theme_summary(self, detailed_themes: List[Dict[str, Any]]) -> str:
        """
        Create a summary paragraph explaining all themes.
        
        Args:
            detailed_themes: List of detailed theme dicts
        
        Returns:
            Summary paragraph combining all themes
        """
        if not detailed_themes:
            return ""
        
        theme_summaries = []
        for theme_dict in detailed_themes:
            theme_summaries.append(theme_dict["explanation"])
        
        # Join with transitions
        if len(theme_summaries) == 1:
            return theme_summaries[0]
        
        # Use different connectors for variety
        connectors = ["Additionally,", "Furthermore,", "In parallel,", "Moreover,"]
        
        result = theme_summaries[0] + " "
        for i, summary in enumerate(theme_summaries[1:], 1):
            connector = connectors[(i-1) % len(connectors)]
            result += f"{connector} {summary} "
        
        return result.strip()
    
    def validate_detail(self, theme_detail: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that theme detail is complete and meaningful.
        
        Returns validation dict with issues list.
        """
        issues = []
        
        # Check required fields
        required = ["theme", "definition", "explanation"]
        for field in required:
            if not theme_detail.get(field):
                issues.append(f"Missing required field: {field}")
        
        # Check minimum length
        explanation = theme_detail.get("explanation", "")
        if len(explanation.split()) < 5:
            issues.append("Explanation too short (min 5 words)")
        
        # Check for supporting instances
        if not theme_detail.get("supporting_instances"):
            issues.append("No supporting instances provided")
        
        # Check depth score
        depth = theme_detail.get("depth_score", 0)
        if depth < 0.3:
            issues.append("Low depth score (< 0.3) - more instances recommended")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "completeness": min(1.0, (5 - len(issues)) / 5.0),
        }
