"""
Evidence Synthesizer — Phase 2

Purpose: Transform technical evidence markers and snippets into natural narrative
sentences that integrate seamlessly with story flow.

Example transformation:
  Input: "For example, she faced a storm. According to the text, it was powerful."
  Output: "She faced a powerful storm that threatened her survival."
"""

from typing import Optional, List, Dict, Any, Tuple
import re
from copy import deepcopy


class EvidenceSynthesizer:
    """Synthesizes natural narrative sentences from evidence snippets."""
    
    # Technical markers to remove/replace
    EVIDENCE_MARKERS = [
        r"for example[,:]?\s*",
        r"for instance[,:]?\s*",
        r"for example[,]?\s*",
        r"according to the text[,:]?\s*",
        r"according to the story[,:]?\s*",
        r"the text shows[,:]?\s*",
        r"the story shows[,:]?\s*",
        r"the book describes[,:]?\s*",
        r"as mentioned[,:]?\s*",
        r"as stated[,:]?\s*",
        r"in the story[,:]?\s*",
        r"in the text[,:]?\s*",
        r"the passage[,:]?\s*",
        r"the novel[,:]?\s*",
    ]
    
    # Amplification phrases for concrete strengthening
    AMPLIFIERS = {
        "storm": "powerful storm that threatened her survival",
        "rain": "heavy rainfall that blocked the path",
        "wind": "fierce wind that whipped around",
        "cold": "bitter cold that numbed her fingers",
        "danger": "grave danger that surrounded her",
        "fear": "deep fear that gripped her heart",
        "challenge": "difficult challenge she had to overcome",
        "obstacle": "major obstacle in her way",
        "conflict": "serious conflict between them",
        "struggle": "difficult struggle for survival",
        "journey": "long, arduous journey ahead",
        "mountain": "towering mountain that seemed endless",
        "village": "quiet village where she grew up",
        "forest": "dense forest full of mystery",
        "darkness": "complete darkness that surrounded her",
    }
    
    SENTIMENT_ENHANCERS = {
        "positive": [
            "with joy and hope",
            "filled with happiness",
            "with a sense of triumph",
            "bringing relief and peace",
            "with gratitude in her heart",
        ],
        "negative": [
            "with deep sorrow",
            "in desperation",
            "with a heavy heart",
            "amid growing fears",
            "desperate and alone",
        ],
    }
    
    def __init__(self):
        """Initialize synthesizer."""
        self.compiled_markers = [re.compile(pattern, re.IGNORECASE) 
                                 for pattern in self.EVIDENCE_MARKERS]
    
    def synthesize(self, evidence_snippet: str, sentiment: str = "neutral") -> str:
        """
        Synthesize natural narrative from evidence snippet.
        
        Args:
            evidence_snippet: Raw evidence text (may contain markers)
            sentiment: "positive", "negative", or "neutral"
        
        Returns:
            Natural narrative sentence (without markers, with context/amplification)
        """
        if not evidence_snippet or not isinstance(evidence_snippet, str):
            return ""
        
        # Step 1: Remove evidence markers
        cleaned = self._remove_markers(evidence_snippet)
        
        # Step 2: Amplify concrete nouns
        amplified = self._amplify_concrete_terms(cleaned)
        
        # Step 3: Add sentiment context if needed
        if sentiment in self.SENTIMENT_ENHANCERS:
            amplified = self._add_sentiment_context(amplified, sentiment)
        
        # Step 4: Normalize capitalization and punctuation
        final = self._normalize_sentence(amplified)
        
        return final
    
    def _remove_markers(self, text: str) -> str:
        """Remove evidence markers from text."""
        result = text
        for pattern in self.compiled_markers:
            result = pattern.sub("", result)
        
        # Also remove parenthetical references
        result = re.sub(r"\s*\([^)]*\)\s*", " ", result)
        
        # Clean extra whitespace
        result = " ".join(result.split())
        
        return result
    
    def _amplify_concrete_terms(self, text: str) -> str:
        """Amplify concrete nouns to be more descriptive."""
        result = text
        text_lower = text.lower()
        
        # Find and replace concrete terms
        for term, amplified in self.AMPLIFIERS.items():
            # Use word boundaries to match whole words only
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text_lower):
                # Replace only first occurrence to avoid over-amplification
                result = re.sub(pattern, amplified, result, count=1, flags=re.IGNORECASE)
        
        return result
    
    def _add_sentiment_context(self, text: str, sentiment: str) -> str:
        """Add sentiment-specific context to the narrative."""
        if sentiment not in self.SENTIMENT_ENHANCERS:
            return text
        
        # Check if text already has sentiment markers
        if any(phrase in text.lower() for phrase in ["with", "amid", "filled"]):
            return text
        
        # Add sentiment enhancer to end of sentence (before period)
        enhancers = self.SENTIMENT_ENHANCERS[sentiment]
        enhancer = enhancers[0]  # Deterministic: always use first
        
        if text.endswith("."):
            text = text[:-1]
        
        return f"{text} {enhancer}."
    
    def _normalize_sentence(self, text: str) -> str:
        """Normalize sentence formatting and capitalization."""
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Ensure single space before period
        text = text.replace(" .", ".")
        text = text.replace(" ,", ",")
        
        # Capitalize first letter
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        # Ensure period at end
        if not text.endswith((".", "!", "?")):
            text += "."
        
        return text
    
    def synthesize_batch(self, snippets: List[Dict[str, Any]]) -> List[str]:
        """
        Synthesize multiple evidence snippets.
        
        Args:
            snippets: List of dicts with 'text' and optional 'sentiment'
        
        Returns:
            List of synthesized narrative sentences
        """
        results = []
        for snippet in snippets:
            if isinstance(snippet, dict):
                text = snippet.get("text", "")
                sentiment = snippet.get("sentiment", "neutral")
            else:
                text = str(snippet)
                sentiment = "neutral"
            
            result = self.synthesize(text, sentiment)
            if result:
                results.append(result)
        
        return results
    
    def merge_evidence_into_narrative(self, narrative_base: str, 
                                      evidence_snippets: List[str],
                                      insertion_point: str = "conflict") -> str:
        """
        Merge synthesized evidence into narrative at appropriate point.
        
        Args:
            narrative_base: Base narrative text
            evidence_snippets: List of evidence texts to integrate
            insertion_point: Where to insert ("conflict", "resolution", "events")
        
        Returns:
            Narrative with evidence integrated
        """
        if not evidence_snippets:
            return narrative_base
        
        # Synthesize all snippets
        synthesized = self.synthesize_batch([{"text": s} for s in evidence_snippets])
        
        # Join synthesized evidence
        evidence_text = " ".join(synthesized)
        
        # Find insertion point in narrative
        base_lower = narrative_base.lower()
        
        if insertion_point == "conflict" and "challenge" in base_lower:
            # Insert after challenge mention
            idx = base_lower.find("challenge")
            if idx > 0:
                # Find next period
                period_idx = narrative_base.find(".", idx)
                if period_idx > 0:
                    return (narrative_base[:period_idx+1] + " " + 
                           evidence_text + " " + 
                           narrative_base[period_idx+1:])
        
        # Default: append at end
        return narrative_base.rstrip(".") + ". " + evidence_text
    
    def validate_synthesis(self, original: str, synthesized: str) -> Dict[str, Any]:
        """
        Validate that synthesis removed markers and maintained meaning.
        
        Returns dict with validation results.
        """
        issues = []
        
        # Check for remaining markers
        for marker_text in ["For example", "According to", "the text", "the story"]:
            if marker_text.lower() in synthesized.lower():
                issues.append(f"Marker '{marker_text}' still present")
        
        # Check minimum length
        if len(synthesized) < 10:
            issues.append("Synthesized text too short")
        
        # Check for valid punctuation
        if not synthesized.endswith((".", "!", "?")):
            issues.append("Missing end punctuation")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "original_length": len(original),
            "synthesized_length": len(synthesized),
            "markers_removed": len(original) > len(synthesized) + 10,
        }
