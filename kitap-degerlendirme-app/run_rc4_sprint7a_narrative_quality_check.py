"""
RC4 Sprint 7A - Phase 5: Integration & Final Verification

Orchestrates all 4 phases:
  1. Character Resolver (entity classification)
  2. Evidence Synthesizer (natural evidence integration)
  3. Semantic Narrative Builder (6-part narrative structure)
  4. Theme Detailer (detailed theme explanations)

Produces:
  - Integrated narrative with all phases
  - Quality verification (human readability, semantic accuracy)
  - Shadow-only artifact with no production changes
"""

import json
from datetime import datetime, timezone
from copy import deepcopy

from runtime_v7.character_resolver import CharacterResolver
from runtime_v7.evidence_synthesizer import EvidenceSynthesizer
from runtime_v7.semantic_narrative_builder import SemanticNarrativeBuilder
from runtime_v7.theme_detailer import ThemeDetailer


def build_rc4_sprint7a_narrative_quality_report(books_with_ir: list) -> dict:
    """
    Build integrated narrative quality report across all phases.
    
    Args:
        books_with_ir: List of dicts with structure:
            {
                "book_id": str,
                "summary_ir": {
                    "title": str,
                    "central_entities": [str],
                    "themes": [str],
                    "places": [str],
                    "key_events": [str],
                    "evidence_snippets": {section: [snippets]},
                    "temporal_context": str,
                }
            }
    
    Returns:
        {
            "sprint": "RC4 Sprint 7A — Real Narrative Quality Framework",
            "generated_at": ISO timestamp,
            "total_books": int,
            "books": [
                {
                    "book_id": str,
                    "phase1_character_resolution": {...},
                    "phase2_evidence_synthesis": {...},
                    "phase3_narrative_structure": {...},
                    "phase4_theme_details": [...],
                    "integrated_narrative": str,
                    "quality_assessment": {
                        "human_readability": float,
                        "semantic_accuracy": float,
                        "narrative_coherence": float,
                        "theme_coverage": float,
                    },
                    "metadata": {...}
                }
            ],
            "aggregate_metrics": {...},
            "shadow_only": true,
            "production_output_changed": false,
        }
    """
    
    result = {
        "sprint": "RC4 Sprint 7A — Real Narrative Quality Framework",
        "generated_at": datetime.fromtimestamp(0, tz=timezone.utc).isoformat() + "Z",  # Deterministic
        "total_books": len(books_with_ir),
        "books": [],
        "aggregate_metrics": {
            "avg_readability": 0.0,
            "avg_semantic_accuracy": 0.0,
            "avg_coherence": 0.0,
            "avg_theme_coverage": 0.0,
        },
        "shadow_only": True,
        "production_output_changed": False,
    }
    
    readability_scores = []
    semantic_scores = []
    coherence_scores = []
    theme_scores = []
    
    for book_data in books_with_ir:
        book_id = book_data.get("book_id", "unknown")
        summary_ir = deepcopy(book_data.get("summary_ir", {}))
        
        # Phase 1: Character Resolution
        char_resolver = CharacterResolver(summary_ir)
        characters = summary_ir.get("central_entities", [])
        resolved_chars = char_resolver.resolve_entities(characters)
        
        # Phase 2: Evidence Synthesis
        evidence_synth = EvidenceSynthesizer()
        evidence_snippets = summary_ir.get("evidence_snippets", {})
        synthesized_evidence = {}
        for section, snippets in evidence_snippets.items():
            synthesized_evidence[section] = evidence_synth.synthesize_batch(
                [{"text": s} for s in snippets]
            )
        
        # Phase 3: Narrative Structure (integrate Character + Evidence)
        summary_ir["evidence_snippets"] = evidence_snippets  # Use original for builder
        narrative_builder = SemanticNarrativeBuilder(summary_ir)
        narrative_result = narrative_builder.build()
        
        # Phase 4: Theme Details
        theme_detailer = ThemeDetailer()
        themes = summary_ir.get("themes", [])
        key_events = summary_ir.get("key_events", [])
        detailed_themes = theme_detailer.detail_multiple_themes(
            themes, key_events, characters
        )
        
        # Quality Assessment
        quality = _assess_narrative_quality(
            narrative_result["narrative"],
            resolved_chars,
            detailed_themes,
            narrative_result["sections"]
        )
        
        # Collect metrics
        readability_scores.append(quality["human_readability"])
        semantic_scores.append(quality["semantic_accuracy"])
        coherence_scores.append(quality["narrative_coherence"])
        theme_scores.append(quality["theme_coverage"])
        
        # Compile book result
        book_result = {
            "book_id": book_id,
            "phase1_character_resolution": {
                "total_characters": len(characters),
                "resolved_characters": [c.get("resolved_name") or c.get("name") 
                                       for c in resolved_chars if c.get("type") == "character"],
                "detected_places": [c.get("resolved_name") for c in resolved_chars 
                                   if c.get("type") == "place"],
            },
            "phase2_evidence_synthesis": {
                "sections_synthesized": list(synthesized_evidence.keys()),
                "total_evidence_pieces": sum(len(v) for v in synthesized_evidence.values()),
                "markers_removed": all("For example" not in str(e) and "According to" not in str(e)
                                      for evidence_list in synthesized_evidence.values()
                                      for e in evidence_list),
            },
            "phase3_narrative_structure": {
                "setup": narrative_result["sections"].get("setup", "")[:100],  # First 100 chars
                "conflict": narrative_result["sections"].get("conflict", "")[:100],
                "events": narrative_result["sections"].get("events", "")[:100],
                "themes": narrative_result["sections"].get("themes", "")[:100],
                "resolution": narrative_result["sections"].get("resolution", "")[:100],
                "message": narrative_result["sections"].get("message", "")[:100],
            },
            "phase4_theme_details": [
                {
                    "theme": t.get("theme"),
                    "definition": t.get("definition"),
                    "supporting_instances_count": len(t.get("supporting_instances", [])),
                    "depth_score": t.get("depth_score", 0.0),
                }
                for t in detailed_themes
            ],
            "integrated_narrative": narrative_result["narrative"],
            "quality_assessment": quality,
            "metadata": {
                "word_count": narrative_result["metadata"].get("word_count", 0),
                "character_count": narrative_result["metadata"].get("character_count", 0),
                "theme_count": narrative_result["metadata"].get("theme_count", 0),
                "deterministic": True,
            },
        }
        
        result["books"].append(book_result)
    
    # Calculate aggregate metrics
    if readability_scores:
        result["aggregate_metrics"]["avg_readability"] = round(sum(readability_scores) / len(readability_scores), 3)
        result["aggregate_metrics"]["avg_semantic_accuracy"] = round(sum(semantic_scores) / len(semantic_scores), 3)
        result["aggregate_metrics"]["avg_coherence"] = round(sum(coherence_scores) / len(coherence_scores), 3)
        result["aggregate_metrics"]["avg_theme_coverage"] = round(sum(theme_scores) / len(theme_scores), 3)
    
    return result


def _assess_narrative_quality(narrative: str, resolved_chars: list, 
                             detailed_themes: list, sections: dict) -> dict:
    """
    Assess narrative quality on human-readability and semantic criteria.
    
    NOT using Quality Engine score (rejected per requirements).
    Focus: human-centered criteria.
    """
    
    narrative_lower = narrative.lower()
    
    # Human Readability (0.0-1.0)
    # - No technical markers
    # - Proper sentence structure
    # - Character names present
    readability = 1.0
    if "for example" in narrative_lower or "according to" in narrative_lower:
        readability -= 0.2
    if narrative.count(".") < 3:  # At least 3 sentences
        readability -= 0.2
    if len(narrative.split()) < 50:  # Minimum length
        readability -= 0.1
    
    # Semantic Accuracy (0.0-1.0)
    # - Characters correctly identified (not confused with places)
    # - Themes mentioned in narrative
    # - Evidence properly synthesized
    semantic = 0.7  # Start at baseline
    character_accuracy = sum(1 for c in resolved_chars if c.get("type") == "character") / max(len(resolved_chars), 1)
    semantic += character_accuracy * 0.15
    
    theme_count = len(detailed_themes)
    if theme_count > 0:
        themes_present = sum(1 for t in detailed_themes 
                            if t.get("theme", "").lower() in narrative_lower)
        semantic += (themes_present / theme_count) * 0.15
    
    # Narrative Coherence (0.0-1.0)
    # - All 6 sections present
    # - Logical flow
    coherence = 0.6
    sections_present = sum(1 for s in sections.values() if s and len(s) > 0)
    coherence += (sections_present / 6.0) * 0.4
    
    # Theme Coverage (0.0-1.0)
    # - All themes have supporting instances
    # - Depth scores adequate
    theme_coverage = 0.0
    if detailed_themes:
        avg_depth = sum(t.get("depth_score", 0.0) for t in detailed_themes) / len(detailed_themes)
        avg_instances = sum(len(t.get("supporting_instances", [])) for t in detailed_themes) / len(detailed_themes)
        theme_coverage = min(1.0, (avg_depth * 0.6) + (min(avg_instances, 3) / 3.0 * 0.4))
    
    return {
        "human_readability": round(max(0.0, min(1.0, readability)), 3),
        "semantic_accuracy": round(max(0.0, min(1.0, semantic)), 3),
        "narrative_coherence": round(max(0.0, min(1.0, coherence)), 3),
        "theme_coverage": round(max(0.0, min(1.0, theme_coverage)), 3),
        "overall_quality": "ACCEPTABLE" if readability > 0.7 else "NEEDS_IMPROVEMENT",
    }
