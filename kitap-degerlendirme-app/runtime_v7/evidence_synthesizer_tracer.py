from __future__ import annotations

from typing import Any, Dict, List, Optional
from copy import deepcopy

from .evidence_synthesizer import EvidenceSynthesizer


class EvidenceSynthesizerTracer:
    """Shadow-only tracer for EvidenceSynthesizer internals.

    Does not modify production behavior. Returns deterministic, inspectable
    records that explain why a snippet was dropped or kept by synthesis.
    """

    def __init__(self):
        self.synth = EvidenceSynthesizer()

    def _get_text_and_meta(self, item: Any) -> Dict[str, Any]:
        # Accept either raw string or dict with 'text' and optional ids
        if isinstance(item, dict):
            return {
                "text": str(item.get("text") or item.get("snippet") or ""),
                "source_sentence_id": item.get("source_sentence_id") or item.get("sentence_id") or None,
                "meta": {k: v for k, v in item.items() if k not in ("text", "snippet")},
            }
        return {"text": str(item or ""), "source_sentence_id": None, "meta": {}}

    def trace_snippet(self, item: Any) -> Dict[str, Any]:
        data = self._get_text_and_meta(item)
        original = data["text"]

        # Stage 1: remove markers (shadow-only call)
        cleaned = self.synth._remove_markers(original)

        # Stage 2: amplify concrete terms (shadow-only call)
        amplified = self.synth._amplify_concrete_terms(cleaned)

        # Stage 3: add sentiment context deterministically (use neutral unless provided)
        sentiment = data.get("meta", {}).get("sentiment") or data.get("meta", {}).get("duygu") or "neutral"
        sentiment_added = self.synth._add_sentiment_context(amplified, sentiment) if sentiment else amplified

        # Stage 4: normalize sentence
        normalized = self.synth._normalize_sentence(sentiment_added)

        # Final: run full synthesize (production path) to get final output
        final = self.synth.synthesize(original, sentiment)
        validation = self.synth.validate_synthesis(original, final)

        # Decide removal reason if final empty
        stage_removed: Optional[str] = None
        reason_removed: Optional[str] = None
        if not final:
            if not cleaned:
                stage_removed = "remove_markers"
                reason_removed = "empty_after_remove_markers"
            elif not normalized or len(normalized.strip()) < 2:
                stage_removed = "normalize"
                reason_removed = "empty_after_normalize_or_too_short"
            else:
                stage_removed = "synthesize"
                reason_removed = "synthesized_to_empty"

        return {
            "original": original,
            "source_sentence_id": data.get("source_sentence_id"),
            "cleaned": cleaned,
            "amplified": amplified,
            "sentiment": sentiment,
            "sentiment_added": sentiment_added,
            "normalized": normalized,
            "synthesized": final,
            "validation": validation,
            "removed": bool(stage_removed is not None),
            "stage_removed": stage_removed,
            "reason_removed": reason_removed,
        }

    def trace_snippets_map(self, snippets_map: Optional[Dict[str, List[Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        trace: Dict[str, List[Dict[str, Any]]] = {}
        if not isinstance(snippets_map, dict):
            return trace
        for section, items in snippets_map.items():
            if not isinstance(items, list):
                continue
            trace[section] = [self.trace_snippet(it) for it in items]
        return trace

    def summarize_trace(self, trace_map: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        total_in = 0
        total_out = 0
        loss_per_stage = {}
        removal_reasons = {}
        removed_items: List[Dict[str, Any]] = []

        for section, items in trace_map.items():
            for rec in items:
                total_in += 1
                if rec.get("synthesized"):
                    total_out += 1
                if rec.get("removed"):
                    stage = rec.get("stage_removed") or "unknown"
                    loss_per_stage[stage] = loss_per_stage.get(stage, 0) + 1
                    reason = rec.get("reason_removed") or "unknown"
                    removal_reasons[reason] = removal_reasons.get(reason, 0) + 1
                    removed_items.append({
                        "source_sentence_id": rec.get("source_sentence_id"),
                        "original": rec.get("original"),
                        "stage_removed": stage,
                        "reason_removed": reason,
                    })

        first_stage_with_major_loss = None
        if loss_per_stage:
            first_stage_with_major_loss = max(loss_per_stage.items(), key=lambda kv: kv[1])[0]

        dominant_root_cause = None
        if removal_reasons:
            dominant_root_cause = max(removal_reasons.items(), key=lambda kv: kv[1])[0]

        return {
            "total_input_evidence": total_in,
            "total_output_evidence": total_out,
            "loss_per_stage": loss_per_stage,
            "removal_reasons": removal_reasons,
            "first_stage_with_major_loss": first_stage_with_major_loss,
            "dominant_root_cause": dominant_root_cause,
            "removed_items": removed_items,
        }
