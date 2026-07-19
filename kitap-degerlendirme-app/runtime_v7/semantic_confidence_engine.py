"""
RC2 Sprint 2 — Semantic Confidence Engine

Rol: Calculate deterministic, calibrated confidence scores for semantic patterns
Design: Shadow-only, non-invasive, deterministic
Output: raw_confidence, calibrated_confidence, delta, recommendation, explanation

Inputs:
- raw_match_count: Number of keyword matches
- pattern_category: 'theme' | 'character_role' | 'learning_outcome'
- false_positive_risk: 'low' | 'medium' | 'high'
- semantic_density: 0-1 (how dense the semantic signal is)
- evidence_diversity: 0-1 (how spread across books)
- coverage_ratio: 0-1 (what % of expected coverage achieved)

Outputs:
- raw_confidence: Base confidence from match density
- calibrated_confidence: Adjusted confidence (0-1)
- confidence_delta: calibrated - raw
- recommendation: 'keep' | 'review' | 'narrow' | 'expand'
- explanation: Human-readable reasoning
"""

from typing import Dict, Any, Literal
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Confidence level bands"""
    STRONG = "strong"          # 0.65-1.0
    ACCEPTABLE = "acceptable"   # 0.40-0.64
    WEAK = "weak"              # 0.20-0.39
    MINIMAL = "minimal"        # 0.0-0.19


class PatternRecommendation(str, Enum):
    """Pattern recommendations based on confidence"""
    KEEP = "keep"              # High confidence, keep as-is
    REVIEW = "review"          # Low confidence, needs investigation
    NARROW = "narrow"          # Too broad, needs keyword refinement
    EXPAND = "expand"          # Good signal, add more keywords


class SemanticConfidenceEngine:
    """
    Deterministic confidence calculation for semantic patterns
    
    Features:
    - Deterministic output (same input → same output)
    - Evidence diversity weighting
    - False positive risk adjustment
    - Coverage analysis
    - Multi-factor calibration
    """
    
    def __init__(self):
        """Initialize confidence engine with calibration factors"""
        # Risk adjustment factors
        self.fp_risk_factors = {
            'low': 1.0,
            'medium': 0.85,
            'high': 0.70,
        }
        
        # Category base expectations
        self.category_expectations = {
            'theme': {
                'matches_per_book': 2.0,
                'coverage_target': 0.6,
            },
            'character_role': {
                'matches_per_book': 1.5,
                'coverage_target': 0.5,
            },
            'learning_outcome': {
                'matches_per_book': 1.5,
                'coverage_target': 0.5,
            },
        }
    
    def calculate_confidence(
        self,
        raw_match_count: int,
        pattern_category: str,
        false_positive_risk: str,
        semantic_density: float,
        evidence_diversity: float,
        coverage_ratio: float,
        books_analyzed: int = 3,
    ) -> Dict[str, Any]:
        """
        Calculate deterministic confidence score for a pattern
        
        Args:
            raw_match_count: Total keyword matches across all books
            pattern_category: 'theme' | 'character_role' | 'learning_outcome'
            false_positive_risk: 'low' | 'medium' | 'high'
            semantic_density: 0-1 (concentration of semantic signal)
            evidence_diversity: 0-1 (spread across evidence sources)
            coverage_ratio: 0-1 (coverage vs target)
            books_analyzed: Number of books in audit
            
        Returns:
            Dict with:
                - raw_confidence: Base confidence
                - calibrated_confidence: Adjusted confidence
                - confidence_delta: Difference
                - confidence_level: 'strong' | 'acceptable' | 'weak' | 'minimal'
                - recommendation: Action recommendation
                - explanation: Human-readable reasoning
        """
        
        # Step 1: Calculate raw confidence
        raw_confidence = self._calculate_raw_confidence(
            raw_match_count,
            pattern_category,
            books_analyzed,
        )
        
        # Step 2: Apply false positive risk adjustment
        risk_adjusted = raw_confidence * self.fp_risk_factors.get(false_positive_risk, 1.0)
        
        # Step 3: Apply diversity weighting
        diversity_adjusted = risk_adjusted * (0.7 + 0.3 * evidence_diversity)
        
        # Step 4: Apply density and coverage boost
        density_coverage = semantic_density * 0.3 + coverage_ratio * 0.3
        final_adjusted = diversity_adjusted * (0.7 + 0.3 * density_coverage)
        
        # Clamp to [0, 1]
        calibrated_confidence = min(max(final_adjusted, 0.0), 1.0)
        
        # Step 5: Determine confidence level
        confidence_level = self._get_confidence_level(calibrated_confidence)
        
        # Step 6: Generate recommendation
        recommendation, rec_explanation = self._generate_recommendation(
            calibrated_confidence,
            confidence_level,
            raw_match_count,
            evidence_diversity,
            pattern_category,
        )
        
        # Step 7: Generate explanation
        explanation = self._generate_explanation(
            raw_confidence,
            calibrated_confidence,
            false_positive_risk,
            confidence_level,
            rec_explanation,
        )
        
        return {
            'raw_confidence': round(raw_confidence, 3),
            'calibrated_confidence': round(calibrated_confidence, 3),
            'confidence_delta': round(calibrated_confidence - raw_confidence, 3),
            'confidence_level': confidence_level.value,
            'recommendation': recommendation.value,
            'explanation': explanation,
            'adjustments': {
                'risk_factor': round(self.fp_risk_factors.get(false_positive_risk, 1.0), 3),
                'diversity_weight': round(0.7 + 0.3 * evidence_diversity, 3),
                'density_coverage_boost': round(0.7 + 0.3 * density_coverage, 3),
            },
        }
    
    def _calculate_raw_confidence(
        self,
        match_count: int,
        category: str,
        books_analyzed: int,
    ) -> float:
        """Calculate base confidence from match density"""
        if match_count == 0:
            return 0.0
        
        expectations = self.category_expectations.get(category, {})
        expected_matches = expectations.get('matches_per_book', 1.5) * books_analyzed
        
        # Confidence = actual / expected, capped at 1.0
        raw_conf = min(match_count / expected_matches, 1.0) if expected_matches > 0 else 0.0
        
        return raw_conf
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Classify confidence into bands"""
        if confidence >= 0.65:
            return ConfidenceLevel.STRONG
        elif confidence >= 0.40:
            return ConfidenceLevel.ACCEPTABLE
        elif confidence >= 0.20:
            return ConfidenceLevel.WEAK
        else:
            return ConfidenceLevel.MINIMAL
    
    def _generate_recommendation(
        self,
        calibrated_confidence: float,
        confidence_level: ConfidenceLevel,
        match_count: int,
        evidence_diversity: float,
        category: str,
    ) -> tuple:
        """Generate recommendation and reason"""
        
        # Decision logic
        if calibrated_confidence >= 0.65:
            recommendation = PatternRecommendation.KEEP
            reason = "Strong signal across multiple sources"
            
        elif calibrated_confidence >= 0.40:
            if evidence_diversity < 0.5 and match_count > 3:
                recommendation = PatternRecommendation.EXPAND
                reason = "Good signal but low diversity; expand keywords to improve spread"
            else:
                recommendation = PatternRecommendation.KEEP
                reason = "Acceptable confidence; monitor performance"
        
        elif calibrated_confidence >= 0.20:
            if match_count > 5:
                recommendation = PatternRecommendation.NARROW
                reason = "Multiple matches but low diversity; narrow and refocus keywords"
            else:
                recommendation = PatternRecommendation.REVIEW
                reason = "Weak signal; needs investigation or refinement"
        
        else:  # < 0.20
            recommendation = PatternRecommendation.REVIEW
            reason = "Minimal signal; candidate for removal or major revision"
        
        return recommendation, reason
    
    def _generate_explanation(
        self,
        raw_confidence: float,
        calibrated_confidence: float,
        fp_risk: str,
        confidence_level: ConfidenceLevel,
        recommendation_reason: str,
    ) -> str:
        """Generate human-readable explanation"""
        
        delta = calibrated_confidence - raw_confidence
        delta_direction = "improved" if delta > 0 else "reduced" if delta < 0 else "unchanged"
        
        explanation = (
            f"Pattern confidence: {confidence_level.value.upper()}. "
            f"Raw: {raw_confidence:.2f} → Calibrated: {calibrated_confidence:.2f} "
            f"({delta_direction} by {abs(delta):.2f}). "
            f"FP Risk: {fp_risk}. "
            f"Reason: {recommendation_reason}."
        )
        
        return explanation
    
    def batch_calculate(
        self,
        patterns: Dict[str, Dict[str, Any]],
        books_analyzed: int = 3,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate confidence for multiple patterns
        
        Args:
            patterns: Dict[pattern_name, pattern_metrics]
            books_analyzed: Number of books analyzed
            
        Returns:
            Dict[pattern_name, confidence_results]
        """
        results = {}
        
        for pattern_name, metrics in patterns.items():
            results[pattern_name] = self.calculate_confidence(
                raw_match_count=metrics.get('match_count', 0),
                pattern_category=metrics.get('category', 'theme'),
                false_positive_risk=metrics.get('fp_risk', 'low'),
                semantic_density=metrics.get('density', 0.5),
                evidence_diversity=metrics.get('diversity', 0.5),
                coverage_ratio=metrics.get('coverage', 0.5),
                books_analyzed=books_analyzed,
            )
        
        return results
    
    def is_deterministic(self) -> bool:
        """Verify engine is deterministic"""
        # Test with same inputs twice
        test_params = {
            'raw_match_count': 5,
            'pattern_category': 'theme',
            'false_positive_risk': 'medium',
            'semantic_density': 0.6,
            'evidence_diversity': 0.8,
            'coverage_ratio': 0.7,
        }
        
        result1 = self.calculate_confidence(**test_params)
        result2 = self.calculate_confidence(**test_params)
        
        return result1 == result2
