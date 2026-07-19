"""
RC2 Sprint 1B — Semantic Pattern Quality Audit

Amaç: Mevcut 15 semantic pattern'ın kalitesini ölçmek
- Production output değişmez (shadow-only)
- Deterministic output korunur
- Kitap-spesifik heuristic YOK
- Yalnızca measurement/audit (deployment YOK)
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.semantic_engine import SemanticEngine


class SemanticPatternAudit:
    """Semantic pattern kalite auditini gerçekleştir"""
    
    def __init__(self):
        """Initialize audit tool"""
        self.engine = SemanticEngine()
        self.pattern_stats = {}
        self.book_analyses = {}
    
    def audit_patterns(self, book_texts: Dict[str, str]) -> Dict[str, Any]:
        """
        Audit all 15 patterns across benchmark books
        
        Args:
            book_texts: Dict[book_name, text]
            
        Returns:
            Audit results with pattern metrics
        """
        audit_results = {
            'timestamp': '2026-07-06T14:30:00Z',
            'sprint': 'RC2_Sprint1B',
            'total_books': len(book_texts),
            'books_analyzed': list(book_texts.keys()),
            'pattern_audit': {},
            'aggregate_metrics': {},
            'book_analyses': {},
        }
        
        # Analyze each book
        for book_name, text in book_texts.items():
            self.book_analyses[book_name] = self.engine.analyze_text(text)
        
        # Audit each pattern type
        audit_results['pattern_audit']['themes'] = self._audit_themes(book_texts)
        audit_results['pattern_audit']['character_roles'] = self._audit_character_roles(book_texts)
        audit_results['pattern_audit']['learning_outcomes'] = self._audit_learning_outcomes(book_texts)
        
        # Calculate aggregate metrics
        audit_results['aggregate_metrics'] = self._calculate_aggregate_metrics(audit_results['pattern_audit'])
        
        # Store book analyses
        for book_name in book_texts:
            analysis = self.book_analyses[book_name]
            audit_results['book_analyses'][book_name] = {
                'theme_cluster_count': len(analysis['theme_clusters']),
                'character_role_count': len(analysis['character_roles']),
                'learning_outcome_count': len(analysis['learning_outcome_clusters']),
                'concept_count': analysis['diagnostics']['concept_count'],
                'semantic_density': analysis['diagnostics']['semantic_density'],
                'semantic_confidence': analysis['diagnostics']['semantic_confidence'],
            }
        
        return audit_results
    
    def _audit_themes(self, book_texts: Dict[str, str]) -> Dict[str, Any]:
        """Audit theme patterns"""
        theme_patterns = {}
        
        for theme_name, keywords in self.engine.THEME_KEYWORDS.items():
            matched_count = 0
            match_locations = []
            
            for book_name, text in book_texts.items():
                for keyword in keywords:
                    count = text.lower().count(keyword.lower())
                    if count > 0:
                        matched_count += count
                        match_locations.append({
                            'book': book_name,
                            'keyword': keyword,
                            'count': count,
                        })
            
            # Calculate metrics
            confidence = min(matched_count / (len(book_texts) * 5), 1.0) if matched_count > 0 else 0.0
            coverage_score = matched_count / (len(book_texts) * 3)  # Baseline: 3 matches per book expected
            false_positive_risk = self._estimate_false_positive_risk(theme_name, matched_count)
            
            theme_patterns[theme_name] = {
                'pattern_name': theme_name,
                'keywords': keywords,
                'keyword_count': len(keywords),
                'total_matched_count': matched_count,
                'match_locations': match_locations,
                'coverage_score': round(coverage_score, 3),
                'confidence': round(confidence, 3),
                'false_positive_risk': false_positive_risk,
                'books_with_matches': len(set(m['book'] for m in match_locations)),
                'recommendation': self._get_pattern_recommendation(
                    theme_name, matched_count, confidence, false_positive_risk
                ),
            }
        
        return theme_patterns
    
    def _audit_character_roles(self, book_texts: Dict[str, str]) -> Dict[str, Any]:
        """Audit character role patterns"""
        role_patterns = {}
        
        for role_name, keywords in self.engine.CHARACTER_ROLES.items():
            matched_count = 0
            match_locations = []
            
            for book_name, text in book_texts.items():
                for keyword in keywords:
                    count = text.lower().count(keyword.lower())
                    if count > 0:
                        matched_count += count
                        match_locations.append({
                            'book': book_name,
                            'keyword': keyword,
                            'count': count,
                        })
            
            # Calculate metrics
            confidence = min(matched_count / (len(book_texts) * 4), 1.0) if matched_count > 0 else 0.0
            coverage_score = matched_count / (len(book_texts) * 2)  # Baseline: 2 matches per book
            false_positive_risk = self._estimate_false_positive_risk(role_name, matched_count)
            
            role_patterns[role_name] = {
                'pattern_name': role_name,
                'keywords': keywords,
                'keyword_count': len(keywords),
                'total_matched_count': matched_count,
                'match_locations': match_locations,
                'coverage_score': round(coverage_score, 3),
                'confidence': round(confidence, 3),
                'false_positive_risk': false_positive_risk,
                'books_with_matches': len(set(m['book'] for m in match_locations)),
                'recommendation': self._get_pattern_recommendation(
                    role_name, matched_count, confidence, false_positive_risk
                ),
            }
        
        return role_patterns
    
    def _audit_learning_outcomes(self, book_texts: Dict[str, str]) -> Dict[str, Any]:
        """Audit learning outcome patterns"""
        outcome_patterns = {}
        
        for outcome_type, keywords in self.engine.LEARNING_OUTCOMES.items():
            matched_count = 0
            match_locations = []
            
            for book_name, text in book_texts.items():
                for keyword in keywords:
                    count = text.lower().count(keyword.lower())
                    if count > 0:
                        matched_count += count
                        match_locations.append({
                            'book': book_name,
                            'keyword': keyword,
                            'count': count,
                        })
            
            # Calculate metrics
            confidence = min(matched_count / (len(book_texts) * 4), 1.0) if matched_count > 0 else 0.0
            coverage_score = matched_count / (len(book_texts) * 2)  # Baseline: 2 matches per book
            false_positive_risk = self._estimate_false_positive_risk(outcome_type, matched_count)
            
            outcome_patterns[outcome_type] = {
                'pattern_name': outcome_type,
                'keywords': keywords,
                'keyword_count': len(keywords),
                'total_matched_count': matched_count,
                'match_locations': match_locations,
                'coverage_score': round(coverage_score, 3),
                'confidence': round(confidence, 3),
                'false_positive_risk': false_positive_risk,
                'books_with_matches': len(set(m['book'] for m in match_locations)),
                'recommendation': self._get_pattern_recommendation(
                    outcome_type, matched_count, confidence, false_positive_risk
                ),
            }
        
        return outcome_patterns
    
    def _estimate_false_positive_risk(self, pattern_name: str, match_count: int) -> str:
        """Estimate false positive risk for pattern"""
        if match_count == 0:
            return 'unknown'
        
        # High-risk patterns (common words)
        high_risk = ['growth', 'physical', 'social']  # May appear in other contexts
        medium_risk = ['knowledge', 'courage', 'friendship']  # Somewhat context-dependent
        low_risk = ['adventure', 'conflict', 'family', 'emotional', 'cognitive']  # More specific
        
        if pattern_name in high_risk:
            return 'high'
        elif pattern_name in medium_risk:
            return 'medium'
        else:
            return 'low'
    
    def _get_pattern_recommendation(self, pattern_name: str, match_count: int, 
                                   confidence: float, fp_risk: str) -> str:
        """Generate recommendation for pattern"""
        # Rules:
        # - No matches: low confidence → review
        # - High FP risk + low matches: review
        # - High matches + low FP risk: keep
        # - All good patterns: keep
        
        if match_count == 0:
            return 'review'
        
        if fp_risk == 'high' and confidence < 0.5:
            return 'review'
        
        if fp_risk == 'high' and confidence >= 0.5:
            return 'keep'  # Keep but monitor
        
        if confidence >= 0.6:
            return 'keep'
        
        if confidence >= 0.3:
            return 'review'
        
        return 'keep'  # Default: keep all patterns for now
    
    def _calculate_aggregate_metrics(self, pattern_audit: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate aggregate metrics across all patterns"""
        all_patterns = []
        
        for category in ['themes', 'character_roles', 'learning_outcomes']:
            all_patterns.extend(pattern_audit[category].values())
        
        total_count = len(all_patterns)
        keep_count = sum(1 for p in all_patterns if p['recommendation'] == 'keep')
        review_count = sum(1 for p in all_patterns if p['recommendation'] == 'review')
        remove_count = sum(1 for p in all_patterns if p['recommendation'] == 'remove')
        
        avg_confidence = sum(p['confidence'] for p in all_patterns) / total_count if total_count > 0 else 0
        avg_coverage = sum(p['coverage_score'] for p in all_patterns) / total_count if total_count > 0 else 0
        
        total_matches = sum(p['total_matched_count'] for p in all_patterns)
        
        return {
            'total_pattern_count': total_count,
            'active_pattern_count': keep_count,
            'review_pattern_count': review_count,
            'remove_pattern_count': remove_count,
            'average_pattern_confidence': round(avg_confidence, 3),
            'average_coverage_score': round(avg_coverage, 3),
            'total_matches_across_all_patterns': total_matches,
            'semantic_coverage_score': round(avg_coverage, 3),
            'quality_status': self._determine_quality_status(
                keep_count, review_count, total_count, avg_confidence
            ),
        }
    
    def _determine_quality_status(self, keep_count: int, review_count: int, 
                                 total_count: int, avg_confidence: float) -> str:
        """Determine overall quality status"""
        keep_ratio = keep_count / total_count if total_count > 0 else 0
        
        if keep_ratio >= 0.9 and avg_confidence >= 0.7:
            return 'excellent'
        elif keep_ratio >= 0.8 and avg_confidence >= 0.6:
            return 'good'
        elif keep_ratio >= 0.6 and avg_confidence >= 0.4:
            return 'acceptable'
        else:
            return 'review_needed'


def run_audit_with_sample_books() -> Dict[str, Any]:
    """Run audit with sample Turkish books"""
    
    # Sample book excerpts (simplified for testing)
    sample_books = {
        'Tavşan Pati': """
        Tavşan Pati bir macera başlatan cesaretli kahramandı. 
        Arkadaşları olan Sincap ve Kurt ile birlikte yolculuğa çıktı.
        Orman kütüphanesinin rehberi Baykuş onları rehberlik yaptı.
        Öğrendikleri dostluk değeri çok önemliydi.
        Kahraman tavşan çeşitli zorlukları yendi.
        Grup dinamiği ve işbirliği öğrenme hedefiydi.
        """,
        
        'Büyülü Yastıklar': """
        Bu hikaye bir çocuğun büyüme yolculuğunu anlatıyor.
        Karakterler arkadaşlık yoluyla gelişim gösterdiler.
        Duygusal olaylar ve deneyimler hikayeyi zenginleştirdi.
        Sosyal öğrenme ve dayanışma temalarını içeriyor.
        Çatışma çözümü ve cesaret gösterileri vardı.
        Bilişsel gelişim süreci işlenmiştir.
        """,
        
        'Benim Adım Kristof Kolomb': """
        Kristof Kolomb cesaretli bir keşfetmen olarak tanıtılıyor.
        Macerası cesaret ve bilgi arayışını gösteriyor.
        Aile ve vatan kavramları ön planda.
        Çatışmalar ve zorluklar yolculuk boyunca görülüyor.
        Kahramanın büyüme süreci ve gelişimi belgesidir.
        Sosyal ilişkiler ve insanlar arasındaki bağlar önemli.
        Duygusal derinlik ve empati ile yazılmıştır.
        """,
    }
    
    audit = SemanticPatternAudit()
    results = audit.audit_patterns(sample_books)
    
    return results


if __name__ == '__main__':
    print("RC2 Sprint 1B — Semantic Pattern Quality Audit")
    print("=" * 60)
    
    results = run_audit_with_sample_books()
    
    print("\nAudit Results Summary:")
    print(f"Total Patterns: {results['aggregate_metrics']['total_pattern_count']}")
    print(f"Active Patterns (Keep): {results['aggregate_metrics']['active_pattern_count']}")
    print(f"Review Patterns: {results['aggregate_metrics']['review_pattern_count']}")
    print(f"Average Confidence: {results['aggregate_metrics']['average_pattern_confidence']}")
    print(f"Quality Status: {results['aggregate_metrics']['quality_status']}")
    
    print("\nBook Analyses:")
    for book_name, analysis in results['book_analyses'].items():
        print(f"\n  {book_name}:")
        print(f"    - Theme Clusters: {analysis['theme_cluster_count']}")
        print(f"    - Character Roles: {analysis['character_role_count']}")
        print(f"    - Learning Outcomes: {analysis['learning_outcome_count']}")
        print(f"    - Semantic Confidence: {analysis['semantic_confidence']}")
    
    # Output full JSON for verification
    print("\n" + "=" * 60)
    print("Full audit results available in JSON output")
    print(json.dumps(results, indent=2, ensure_ascii=False)[:500] + "...")
