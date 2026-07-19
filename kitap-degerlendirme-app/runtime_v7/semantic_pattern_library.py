"""
RC2 Sprint 3 — Semantic Pattern Library

Rol: Manage 74 generic semantic patterns with metadata, validation, and benchmarking
Design: Shadow-only, non-invasive, deterministic, scalable

Core Principles:
- All patterns are generic (no book-specific heuristics)
- Metadata-driven (id, category, keywords, strategy, fp_risk, status)
- Validation on every operation
- Deterministic output
- Zero production impact
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib

from runtime_v7.semantic_pattern_registry import (
    get_sprint3_pattern_definitions,
    validate_sprint3_pattern_definitions,
)


class PatternCategory(str, Enum):
    """Pattern categories"""
    THEME = "theme"
    CHARACTER_ROLE = "character_role"
    LEARNING_OUTCOME = "learning_outcome"
    CONFLICT = "conflict"
    EMOTION = "emotion"
    NARRATIVE_STRUCTURE = "narrative_structure"


class PatternStatus(str, Enum):
    """Pattern development status"""
    VALIDATED = "VALIDATED"
    NEW = "NEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    DEPRECATED = "DEPRECATED"


class MatchingStrategy(str, Enum):
    """Pattern matching strategy"""
    KEYWORD_FREQUENCY = "keyword_frequency"
    CONTEXTUAL = "contextual"
    CONTEXT_WINDOW = "context_window"
    SENTIMENT = "sentiment"
    STRUCTURE = "structure"


@dataclass
class SemanticPattern:
    """
    Semantic Pattern with full metadata
    
    Required fields:
    - id: Unique identifier (category_name format)
    - name: Human-readable name
    - category: PatternCategory
    - description: Pattern description
    - keywords: List of detection keywords
    - matching_strategy: How pattern is detected
    - default_fp_risk: False positive risk level
    - expected_density: Expected pattern density (0-1)
    - confidence_weight: Confidence weighting (0.7-1.0)
    - status: PatternStatus
    """
    
    id: str
    name: str
    category: str
    description: str
    keywords: List[str]
    matching_strategy: str
    default_fp_risk: str
    expected_density: float
    confidence_weight: float
    status: str
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate pattern metadata
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # ID validation
        if not self.id:
            errors.append("id is required")
        elif not self.id.startswith(('theme_', 'character_', 'learning_', 'conflict_', 'emotion_', 'narrative_')):
            errors.append(f"id must start with category prefix: {self.id}")
        
        # Name validation
        if not self.name or len(self.name) < 3:
            errors.append("name must be at least 3 characters")
        
        # Category validation
        if self.category not in [c.value for c in PatternCategory]:
            errors.append(f"invalid category: {self.category}")
        
        # Description validation
        if not self.description or len(self.description) < 10:
            errors.append("description must be at least 10 characters")
        
        # Keywords validation
        if not self.keywords or len(self.keywords) < 3:
            errors.append("at least 3 keywords required")
        
        # Matching strategy validation
        if self.matching_strategy not in [s.value for s in MatchingStrategy]:
            errors.append(f"invalid matching_strategy: {self.matching_strategy}")
        
        # FP risk validation
        if self.default_fp_risk not in ['low', 'medium', 'high']:
            errors.append(f"invalid default_fp_risk: {self.default_fp_risk}")
        
        # Density validation
        if not (0.0 <= self.expected_density <= 1.0):
            errors.append(f"expected_density must be 0-1: {self.expected_density}")
        
        # Confidence weight validation
        if not (0.7 <= self.confidence_weight <= 1.0):
            errors.append(f"confidence_weight must be 0.7-1.0: {self.confidence_weight}")
        
        # Status validation
        if self.status not in [s.value for s in PatternStatus]:
            errors.append(f"invalid status: {self.status}")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_hash(self) -> str:
        """Get deterministic hash of pattern metadata"""
        pattern_json = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(pattern_json.encode()).hexdigest()


class SemanticPatternLibrary:
    """
    Centralized management of 74 semantic patterns
    
    Features:
    - Pattern registration and validation
    - Duplicate detection
    - Conflict detection
    - Metadata versioning
    - Statistics and reporting
    """
    
    def __init__(self):
        """Initialize empty pattern library"""
        self.patterns: Dict[str, SemanticPattern] = {}
        self.pattern_order: List[str] = []  # Preserve insertion order
        self._validation_cache = {}
        self._conflict_cache = None
    
    def register_pattern(self, pattern: SemanticPattern) -> Tuple[bool, List[str]]:
        """
        Register a new pattern with full validation
        
        Args:
            pattern: SemanticPattern to register
            
        Returns:
            (success, error_messages)
        """
        errors = []
        
        # Validate pattern structure
        is_valid, struct_errors = pattern.validate()
        if not is_valid:
            return False, struct_errors
        
        # Check for duplicate ID
        if pattern.id in self.patterns:
            errors.append(f"Duplicate pattern ID: {pattern.id}")
        
        # Check for keyword conflicts
        keyword_conflicts = self._check_keyword_conflicts(pattern)
        if keyword_conflicts:
            errors.append(f"Keyword conflicts with: {', '.join(keyword_conflicts)}")
        
        if errors:
            return False, errors
        
        # Register pattern
        self.patterns[pattern.id] = pattern
        self.pattern_order.append(pattern.id)
        self._conflict_cache = None  # Invalidate cache
        
        return True, []
    
    def _check_keyword_conflicts(self, pattern: SemanticPattern, threshold: float = 0.7) -> List[str]:
        """
        Check for significant keyword overlaps with existing patterns
        
        Args:
            pattern: Pattern to check
            threshold: Overlap ratio threshold (0-1)
            
        Returns:
            List of conflicting pattern IDs
        """
        conflicts = []
        pattern_keywords = set(pattern.keywords)
        
        for existing_id, existing_pattern in self.patterns.items():
            # Only check same category
            if existing_pattern.category != pattern.category:
                continue
            
            existing_keywords = set(existing_pattern.keywords)
            
            # Calculate overlap ratio
            if existing_keywords or pattern_keywords:
                overlap = len(pattern_keywords & existing_keywords)
                total = len(pattern_keywords | existing_keywords)
                ratio = overlap / total if total > 0 else 0.0
                
                if ratio >= threshold:
                    conflicts.append(existing_id)
        
        return conflicts
    
    def register_batch(self, patterns: List[SemanticPattern]) -> Tuple[int, List[str]]:
        """
        Register multiple patterns
        
        Args:
            patterns: List of SemanticPattern objects
            
        Returns:
            (success_count, error_messages)
        """
        success_count = 0
        errors = []
        
        for pattern in patterns:
            success, errs = self.register_pattern(pattern)
            if success:
                success_count += 1
            else:
                errors.extend([f"{pattern.id}: {err}" for err in errs])
        
        return success_count, errors
    
    def get_pattern(self, pattern_id: str) -> Optional[SemanticPattern]:
        """Get pattern by ID"""
        return self.patterns.get(pattern_id)
    
    def get_patterns_by_category(self, category: str) -> List[SemanticPattern]:
        """Get all patterns in a category"""
        return [p for p in self.patterns.values() if p.category == category]
    
    def get_patterns_by_status(self, status: str) -> List[SemanticPattern]:
        """Get all patterns with given status"""
        return [p for p in self.patterns.values() if p.status == status]
    
    def list_all_patterns(self) -> List[SemanticPattern]:
        """List all patterns in registration order"""
        return [self.patterns[pid] for pid in self.pattern_order]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get library statistics"""
        patterns_list = list(self.patterns.values())
        
        stats = {
            'total_patterns': len(patterns_list),
            'by_category': {},
            'by_status': {},
            'by_fp_risk': {},
            'average_keywords': 0.0,
            'average_confidence_weight': 0.0,
            'average_expected_density': 0.0,
        }
        
        # Count by category
        for category in PatternCategory:
            patterns = self.get_patterns_by_category(category.value)
            stats['by_category'][category.value] = len(patterns)
        
        # Count by status
        for status in PatternStatus:
            patterns = self.get_patterns_by_status(status.value)
            stats['by_status'][status.value] = len(patterns)
        
        # Count by FP risk
        for risk in ['low', 'medium', 'high']:
            count = len([p for p in patterns_list if p.default_fp_risk == risk])
            stats['by_fp_risk'][risk] = count
        
        # Averages
        if patterns_list:
            stats['average_keywords'] = round(
                sum(len(p.keywords) for p in patterns_list) / len(patterns_list), 2
            )
            stats['average_confidence_weight'] = round(
                sum(p.confidence_weight for p in patterns_list) / len(patterns_list), 3
            )
            stats['average_expected_density'] = round(
                sum(p.expected_density for p in patterns_list) / len(patterns_list), 3
            )
        
        return stats
    
    def validate_all(self) -> Dict[str, Any]:
        """Validate all patterns in library"""
        results = {
            'total_patterns': len(self.patterns),
            'valid_patterns': 0,
            'invalid_patterns': [],
            'conflicts': [],
            'warnings': [],
        }
        
        for pattern in self.patterns.values():
            is_valid, errors = pattern.validate()
            
            if is_valid:
                results['valid_patterns'] += 1
            else:
                results['invalid_patterns'].append({
                    'id': pattern.id,
                    'errors': errors,
                })
        
        # Check for duplicates
        ids = list(self.patterns.keys())
        if len(ids) != len(set(ids)):
            results['conflicts'].append("Duplicate pattern IDs detected")
        
        return results
    
    def export_to_json(self) -> str:
        """Export library to JSON"""
        export_data = {
            'library_format': 'RC2_SPRINT3',
            'total_patterns': len(self.patterns),
            'patterns': {
                pid: pattern.to_dict() for pid, pattern in self.patterns.items()
            },
            'statistics': self.get_statistics(),
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def export_to_file(self, filepath: str) -> bool:
        """Export library to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.export_to_json())
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    @staticmethod
    def import_from_json(json_str: str) -> Tuple['SemanticPatternLibrary', List[str]]:
        """
        Import library from JSON
        
        Returns:
            (library, error_messages)
        """
        library = SemanticPatternLibrary()
        errors = []
        
        try:
            data = json.loads(json_str)
            patterns_data = data.get('patterns', {})
            
            for pattern_id, pattern_dict in patterns_data.items():
                try:
                    pattern = SemanticPattern(**pattern_dict)
                    success, errs = library.register_pattern(pattern)
                    if not success:
                        errors.extend(errs)
                except Exception as e:
                    errors.append(f"Failed to import {pattern_id}: {e}")
        
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")
        
        return library, errors
    
    def get_library_hash(self) -> str:
        """Get deterministic hash of entire library"""
        patterns_json = json.dumps(
            {pid: p.to_dict() for pid, p in self.patterns.items()},
            sort_keys=True,
            ensure_ascii=False
        )
        return hashlib.sha256(patterns_json.encode()).hexdigest()


def build_default_library() -> SemanticPatternLibrary:
    """
    Build the default 74-pattern library from the central Sprint 3 registry.
    
    Returns:
        SemanticPatternLibrary with all patterns
    """
    library = SemanticPatternLibrary()

    valid, registry_errors = validate_sprint3_pattern_definitions()
    if not valid:
        print("Registry validation failed:")
        for err in registry_errors:
            print(f"  - {err}")
        raise ValueError("Sprint 3 pattern registry validation failed")

    all_patterns = _get_all_default_patterns()
    success_count, errors = library.register_batch(all_patterns)

    if errors:
        print(f"Warning: {len(errors)} patterns had issues during registration")
        for error in errors[:5]:  # Show first 5
            print(f"  - {error}")

    return library


def _get_all_default_patterns() -> List[SemanticPattern]:
    """
    Get all 74 default patterns from the central registry.
    """
    valid, registry_errors = validate_sprint3_pattern_definitions()
    if not valid:
        raise ValueError(f"Sprint 3 pattern registry invalid: {registry_errors}")

    return [SemanticPattern(**pattern_data) for pattern_data in get_sprint3_pattern_definitions()]
