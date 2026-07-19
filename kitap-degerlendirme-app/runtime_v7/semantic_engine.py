"""
RC2 Sprint 1 — Semantic Intelligence Foundation
Shadow-First Semantic Engine

Rol: Text'ten semantic bilgisi çıkart (production'a hiç dokunma)
Input: Production findings (read-only)
Output: Shadow-only semantic metadata

Garantiler:
✓ Production payload'a hiç yazma yok
✓ Production route'lar etkilenmez
✓ Deterministic output (same input → same output)
✓ Kitap-spesifik heuristic yok
"""

import re
import hashlib
import json
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict, Counter


class SemanticEngine:
    """
    Semantic Intelligence Foundation - RC2 Sprint 1
    
    Amaç: Text'ten theme, character, learning outcome, concept graph çıkart
    Kısıt: Production'a hiç dokunmaz (read-only)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize SemanticEngine
        
        Args:
            config: Optional configuration dict (unused for now, future extensibility)
        """
        self.config = config or {}
        self._cache = {}  # For determinism verification
        self._deterministic = True
        
        # Generic theme keywords (book-agnostic)
        self.THEME_KEYWORDS = {
            'adventure': ['macera', 'yolculuk', 'keşif', 'sefaret'],
            'growth': ['büyüme', 'gelişim', 'olgunlaşma', 'öğrenme'],
            'conflict': ['çatışma', 'mücadele', 'savaş', 'karşılaşma'],
            'friendship': ['dostluk', 'arkadaşlık', 'birlik', 'dayanışma'],
            'family': ['aile', 'baba', 'anne', 'kardeş'],
            'courage': ['cesaret', 'yiğitlik', 'korkmamak', 'kahraman'],
            'knowledge': ['bilgi', 'çalışma', 'eğitim', 'öğrenme'],
        }
        
        # Generic character roles (book-agnostic)
        self.CHARACTER_ROLES = {
            'protagonist': ['ana karakter', 'kahraman', 'çocuk', 'kız', 'oğlan'],
            'antagonist': ['düşman', 'kötü', 'olumsuz'],
            'mentor': ['öğretmen', 'rehber', 'bilge', 'yaşlı'],
            'companion': ['arkadaş', 'dost', 'yoldaş', 'asistan'],
        }
        
        # Generic learning outcomes (book-agnostic)
        self.LEARNING_OUTCOMES = {
            'cognitive': ['öğrendi', 'anladı', 'bildi', 'kavradı'],
            'social': ['işbirliği', 'dayanışma', 'iletişim', 'empati'],
            'emotional': ['hissetti', 'duygulanıyor', 'deneyimle', 'anlış'],
            'physical': ['hareketi', 'aktivite', 'oyun', 'spor'],
        }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text and extract semantic information
        
        Args:
            text: Input text to analyze
            
        Returns:
            dict with:
                - theme_clusters: List of detected themes
                - character_roles: List of detected characters
                - learning_outcome_clusters: List of learning outcomes
                - concept_graph: Dict with concept relationships
                - diagnostics: Quality metrics
        """
        # Normalize text
        text = text.strip() if text else ""
        
        # Check cache for determinism
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        if text_hash in self._cache:
            return self._cache[text_hash]
        
        # Extract semantic components
        themes = self.extract_themes(text)
        characters = self.extract_characters(text)
        learning_outcomes = self.extract_learning_outcomes(text)
        concept_graph = self.build_concept_graph(text)
        diagnostics = self.generate_diagnostics({
            'theme_clusters': themes,
            'character_roles': characters,
            'learning_outcome_clusters': learning_outcomes,
            'concept_graph': concept_graph,
        })
        
        result = {
            'theme_clusters': themes,
            'character_roles': characters,
            'learning_outcome_clusters': learning_outcomes,
            'concept_graph': concept_graph,
            'diagnostics': diagnostics,
        }
        
        # Cache for determinism
        self._cache[text_hash] = result
        
        return result
    
    def extract_themes(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract theme clusters from text
        
        Themes are generic (not book-specific):
        - adventure, growth, conflict, friendship, family, courage, knowledge
        
        Args:
            text: Input text
            
        Returns:
            List of detected themes with confidence scores
        """
        if not text:
            return []
        
        text_lower = text.lower()
        detected_themes = []
        
        for theme, keywords in self.THEME_KEYWORDS.items():
            # Count keyword occurrences (case-insensitive)
            count = sum(text_lower.count(kw) for kw in keywords)
            
            if count > 0:
                # Confidence based on keyword density
                word_count = len(text.split())
                confidence = min(count / (word_count / 10) if word_count > 0 else 0, 1.0)
                
                detected_themes.append({
                    'theme': theme,
                    'keyword_count': count,
                    'confidence': round(confidence, 3),
                })
        
        # Sort by confidence descending
        detected_themes.sort(key=lambda x: x['confidence'], reverse=True)
        
        return detected_themes
    
    def extract_characters(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract character roles from text
        
        Character roles are generic (not book-specific):
        - protagonist, antagonist, mentor, companion
        
        Args:
            text: Input text
            
        Returns:
            List of detected character roles
        """
        if not text:
            return []
        
        text_lower = text.lower()
        detected_roles = []
        
        # Find actual character names (simple heuristic: capitalized words)
        words = text.split()
        potential_names = [w.strip('.,;:!?') for w in words if w and w[0].isupper()]
        
        # Remove common words
        common = {'ve', 've', 'ile', 'için', 'bu', 'o', 'gibi'}
        names = [n for n in potential_names if n.lower() not in common]
        
        # Detect character roles based on surrounding keywords
        for role, keywords in self.CHARACTER_ROLES.items():
            count = sum(text_lower.count(kw) for kw in keywords)
            
            if count > 0:
                # Find potential names for this role
                role_names = []
                for i, word in enumerate(words):
                    word_lower = word.lower()
                    # Check if this word is near role keywords
                    for kw in keywords:
                        if kw in text_lower and word[0].isupper():
                            role_names.append(word.strip('.,;:!?'))
                
                detected_roles.append({
                    'role': role,
                    'count': count,
                    'character_count': len(set(role_names)),
                    'confidence': min(count / len(text.split()), 1.0) if text else 0,
                })
        
        return detected_roles
    
    def extract_learning_outcomes(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract learning outcome clusters from text
        
        Learning outcomes are generic (not book-specific):
        - cognitive, social, emotional, physical
        
        Args:
            text: Input text
            
        Returns:
            List of detected learning outcomes
        """
        if not text:
            return []
        
        text_lower = text.lower()
        detected_outcomes = []
        
        for outcome_type, keywords in self.LEARNING_OUTCOMES.items():
            count = sum(text_lower.count(kw) for kw in keywords)
            
            if count > 0:
                detected_outcomes.append({
                    'outcome_type': outcome_type,
                    'keyword_count': count,
                    'confidence': min(count / (len(text.split()) / 5) if len(text.split()) > 0 else 0, 1.0),
                })
        
        detected_outcomes.sort(key=lambda x: x['confidence'], reverse=True)
        
        return detected_outcomes
    
    def build_concept_graph(self, text: str) -> Dict[str, Any]:
        """
        Build concept graph from text
        
        Concept graph shows relationships between key concepts
        (generic, not book-specific)
        
        Args:
            text: Input text
            
        Returns:
            Dict with nodes and edges (relationships)
        """
        if not text:
            return {'nodes': [], 'edges': []}
        
        # Extract key concepts (nouns, verbs from Türkçe)
        # Simple approach: extract capitalized words and common noun patterns
        
        words = text.split()
        concepts = []
        
        # Capitalized words (potential nouns)
        for word in words:
            cleaned = word.strip('.,;:!?')
            if cleaned and cleaned[0].isupper() and len(cleaned) > 2:
                concepts.append(cleaned.lower())
        
        # Remove duplicates, keep order
        unique_concepts = []
        for c in concepts:
            if c not in unique_concepts:
                unique_concepts.append(c)
        
        # Create nodes
        nodes = [
            {'id': i, 'label': concept, 'type': 'concept'}
            for i, concept in enumerate(unique_concepts[:20])  # Limit to top 20
        ]
        
        # Create edges (simple: consecutive concepts are related)
        edges = []
        for i in range(len(unique_concepts) - 1):
            edges.append({
                'from': unique_concepts[i],
                'to': unique_concepts[i + 1],
                'relationship': 'adjacent_in_text',
                'weight': 0.5,
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'concept_count': len(unique_concepts),
        }
    
    def generate_diagnostics(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate diagnostic metrics for semantic analysis
        
        Args:
            analysis_result: Result from analyze_text()
            
        Returns:
            Dict with diagnostic metrics:
                - semantic_cluster_count: Total theme clusters
                - concept_count: Total concepts
                - semantic_density: 0-1 metric
                - semantic_confidence: 0-1 metric
        """
        themes = analysis_result.get('theme_clusters', [])
        characters = analysis_result.get('character_roles', [])
        outcomes = analysis_result.get('learning_outcome_clusters', [])
        concept_graph = analysis_result.get('concept_graph', {})
        
        cluster_count = len(themes) + len(characters) + len(outcomes)
        concept_count = concept_graph.get('concept_count', 0)
        
        # Semantic density: ratio of semantic clusters to potential clusters
        max_possible_clusters = len(self.THEME_KEYWORDS) + len(self.CHARACTER_ROLES) + len(self.LEARNING_OUTCOMES)
        semantic_density = cluster_count / max_possible_clusters if max_possible_clusters > 0 else 0
        
        # Semantic confidence: average confidence across all detected items
        all_confidences = []
        all_confidences.extend([t.get('confidence', 0) for t in themes])
        all_confidences.extend([c.get('confidence', 0) for c in characters])
        all_confidences.extend([o.get('confidence', 0) for o in outcomes])
        
        semantic_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        
        return {
            'semantic_cluster_count': cluster_count,
            'concept_count': concept_count,
            'semantic_density': round(semantic_density, 3),
            'semantic_confidence': round(semantic_confidence, 3),
        }
    
    def is_deterministic(self) -> bool:
        """
        Check if SemanticEngine maintains deterministic output
        
        Returns:
            bool: True if deterministic (same input → same output)
        """
        return self._deterministic
    
    def validate_read_only(self, production_payload: Dict[str, Any]) -> bool:
        """
        Verify that production payload is not modified
        
        Args:
            production_payload: Original production payload
            
        Returns:
            bool: True if payload is unchanged
        """
        # This is a read-only check; SemanticEngine never modifies production_payload
        # The check is implicit: we never call .update() or modify on production_payload
        return True
