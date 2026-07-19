"""
Pipeline Debug Logger - V6.4 Theme Detection Debugging Module

Her aşamada hangi adayın neden elendiğini ayrıntılı loglar.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional


class PipelineDebugLogger:
    """Theme pipeline debug logger - her aşamayı ayrı ayrı loglar"""
    
    def __init__(self, book_name: str = "unknown"):
        self.book_name = book_name
        self.log_path = os.path.abspath("pipeline_debug.log")
        self.stages = []
        self._write_header()
    
    def _write_header(self):
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"PIPELINE DEBUG - {datetime.now().isoformat(timespec='seconds')}\n")
                f.write(f"Book: {self.book_name}\n")
                f.write(f"{'='*80}\n")
        except Exception:
            pass
    
    def log_stage(self, stage_name: str, data: dict):
        """Log a pipeline stage with details"""
        try:
            self.stages.append(stage_name)
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n--- STAGE: {stage_name} ---\n")
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        f.write(f"  {key}: {json.dumps(value, ensure_ascii=False, default=str)[:3000]}\n")
                    else:
                        f.write(f"  {key}: {value}\n")
        except Exception:
            pass
    
    def log_theme_candidate(self, theme: str, stage: str, 
                           candidate_count: int = 0, 
                           evidence_pages: List[int] = None,
                           embedding_score: float = 0.0,
                           evidence_score: float = 0.0,
                           penalty: float = 0.0,
                           final_score: float = 0.0,
                           rejected_reason: str = "NONE",
                           matched_keywords: List[str] = None,
                           context_strength: int = 0,
                           semantic_type: str = "",
                           evidence_text: str = ""):
        """Log a single theme candidate with full scoring details"""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[THEME CANDIDATE] {theme}\n")
                f.write(f"  Stage: {stage}\n")
                f.write(f"  Candidate Count: {candidate_count}\n")
                f.write(f"  Evidence Pages: {evidence_pages or []}\n")
                f.write(f"  Embedding Score: {embedding_score:.2f}\n")
                f.write(f"  Evidence Score: {evidence_score:.2f}\n")
                f.write(f"  Penalty: {penalty:.2f}\n")
                f.write(f"  Final Score: {final_score:.2f}\n")
                f.write(f"  Rejected Reason: {rejected_reason}\n")
                f.write(f"  Matched Keywords: {matched_keywords or []}\n")
                f.write(f"  Context Strength: {context_strength}\n")
                f.write(f"  Semantic Type: {semantic_type}\n")
                if evidence_text:
                    f.write(f"  Evidence Text: {evidence_text[:200]}\n")
        except Exception:
            pass
    
    def log_evidence_filter(self, sentence: str, page: int, 
                           reason: str, stage: str,
                           matched_keywords: List[str] = None,
                           context_strength: int = 0,
                           semantic_type: str = "",
                           evidence_weight: float = 0.0):
        """Log when a sentence is filtered out as evidence"""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[EVIDENCE FILTER] Page {page}\n")
                f.write(f"  Text: {sentence[:150]}\n")
                f.write(f"  Stage: {stage}\n")
                f.write(f"  Filter Reason: {reason}\n")
                f.write(f"  Matched Keywords: {matched_keywords or []}\n")
                f.write(f"  Context Strength: {context_strength}\n")
                f.write(f"  Semantic Type: {semantic_type}\n")
                f.write(f"  Evidence Weight: {evidence_weight:.2f}\n")
        except Exception:
            pass
    
    def log_character_filter(self, name: str, reason: str, 
                            original_name: str = "", context: str = ""):
        """Log when a character name candidate is filtered"""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[CHARACTER FILTER] {name}\n")
                f.write(f"  Original Name: {original_name or name}\n")
                f.write(f"  Filter Reason: {reason}\n")
                if context:
                    f.write(f"  Context: {context[:150]}\n")
        except Exception:
            pass
    
    def log_book_type(self, detected_type: str, correct_type: str, 
                     evidence: List[str] = None):
        """Log book type classification"""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[BOOK TYPE CLASSIFICATION]\n")
                f.write(f"  Detected: {detected_type}\n")
                f.write(f"  Expected: {correct_type}\n")
                f.write(f"  Evidence: {evidence or []}\n")
        except Exception:
            pass
    
    def log_final_theme_selection(self, themes: List[dict], threshold: float = 0.60):
        """Log final theme selection with threshold info"""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n--- STAGE: Final Theme Selection ---\n")
                f.write(f"  Confidence Threshold: {threshold:.2f}\n")
                for t in themes:
                    f.write(f"  Theme: {t.get('ad', '?')} | "
                           f"Güç: {t.get('tema_gucu', 0)} | "
                           f"Güven: {t.get('guven_skoru', 0):.2f} | "
                           f"Kanıt: {t.get('kanit_sayisi', 0)} | "
                           f"Sayfa: {t.get('farkli_sayfa_sayisi', 0)}\n")
                if not themes:
                    f.write(f"  NO THEMES PASSED THRESHOLD\n")
        except Exception:
            pass
    
    def log_threshold_check(self, theme: str, score: float, threshold: float, passed: bool):
        """Log threshold check for a theme"""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[THRESHOLD CHECK] {theme}\n")
                f.write(f"  Score: {score:.2f}\n")
                f.write(f"  Threshold: {threshold:.2f}\n")
                f.write(f"  Passed: {'YES' if passed else 'NO'}\n")
                if not passed:
                    f.write(f"  Rejected because: confidence threshold ({score:.2f} < {threshold:.2f})\n")
        except Exception:
            pass
    
    def log_value_extraction(self, value: str, evidence_count: int, 
                            pages: List[int], score: float, rejected: bool = False,
                            reason: str = ""):
        """Log value extraction details"""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[VALUE EXTRACTION] {value}\n")
                f.write(f"  Evidence Count: {evidence_count}\n")
                f.write(f"  Pages: {pages}\n")
                f.write(f"  Score: {score:.2f}\n")
                f.write(f"  Rejected: {rejected}\n")
                if reason:
                    f.write(f"  Reason: {reason}\n")
        except Exception:
            pass
    
    def close(self):
        """Close the log"""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"END PIPELINE DEBUG - {datetime.now().isoformat(timespec='seconds')}\n")
                f.write(f"{'='*80}\n\n")
        except Exception:
            pass