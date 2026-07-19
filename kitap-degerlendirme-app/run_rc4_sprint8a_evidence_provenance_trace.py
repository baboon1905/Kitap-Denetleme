#!/usr/bin/env python3
"""
RC4 Sprint 8A - Evidence Provenance Trace

Purpose: Trace evidence provenance through the runtime narrative pipeline.

Captures:
  - raw evidence snippets
  - evidence synthesizer output and validation
  - SummaryIR payload and metadata
  - SemanticNarrativeBuilder input and output
  - final report summary surfaces from SummaryIR

This is a shadow-only artifact and does not change production behavior.
"""

import json
import os
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime_v7.evidence_synthesizer import EvidenceSynthesizer
from runtime_v7.semantic_narrative_builder import SemanticNarrativeBuilder
from runtime_v7.summary_surface import build_summary_surfaces_from_ir


TRACE_CASES: List[Dict[str, Any]] = [
    {
        "book_id": "tavsan_pati",
        "title": "Tavşan Pati",
        "summary_ir": {
            "title": "Tavşan Pati",
            "central_entities": ["Tavşan Pati"],
            "themes": ["arkadaşlık", "cesaret"],
            "places": ["orman", "çiftlik"],
            "temporal_context": "modern",
            "key_events": [
                "Tavşan Pati merakla ormana gider",
                "Karanlık bir fırtına onu yollarından alıkoyar",
                "O, arkadaşlarıyla güvenli bir yere sığınır",
            ],
            "evidence_snippets": {
                "setup": ["Tavşan Pati küçük bir çiftlikte yaşar."],
                "conflict": ["For example, fırtına yolu kapattı."],
                "resolution": ["Nihayet güvenli bir yere ulaştılar."],
            },
        },
    },
    {
        "book_id": "buyulu_yastiklar",
        "title": "Büyülü Yastıklar",
        "summary_ir": {
            "title": "Büyülü Yastıklar",
            "central_entities": ["Mina"],
            "themes": ["hayal gücü", "aidiyet"],
            "places": ["ev", "gökyüzü"],
            "temporal_context": "fantastik",
            "key_events": [
                "Mina yastıkların gücünü keşfeder",
                "O, uzak bir diyara uçar",
            ],
            "evidence_snippets": {
                "conflict": ["According to the story, gerçek dünya onu durdurmaya çalışır."],
                "resolution": ["Sonunda hayal gücüyle kazanır."],
            },
        },
    },
]


def _trace_evidence_snippet(snippet: str, synthesizer: EvidenceSynthesizer) -> Dict[str, Any]:
    cleaned = synthesizer._remove_markers(snippet)
    synthesized = synthesizer.synthesize(snippet)
    validation = synthesizer.validate_synthesis(snippet, synthesized)
    return {
        "original": snippet,
        "cleaned": cleaned,
        "synthesized": synthesized,
        "validation": validation,
    }


def _trace_evidence_snippets(
    evidence_snippets: Optional[Dict[str, List[str]]],
    synthesizer: EvidenceSynthesizer,
) -> Dict[str, List[Dict[str, Any]]]:
    trace: Dict[str, List[Dict[str, Any]]] = {}
    if not isinstance(evidence_snippets, dict):
        return trace

    for section, snippets in evidence_snippets.items():
        if not isinstance(snippets, list):
            continue
        trace[section] = [
            _trace_evidence_snippet(str(snippet or ""), synthesizer)
            for snippet in snippets
        ]
    return trace


def _build_builder_input(summary_ir: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": summary_ir.get("title"),
        "central_entities": summary_ir.get("central_entities", []),
        "themes": summary_ir.get("themes", []),
        "places": summary_ir.get("places", []),
        "temporal_context": summary_ir.get("temporal_context", ""),
        "key_events": summary_ir.get("key_events", []),
        "evidence_snippets": summary_ir.get("evidence_snippets", {}),
    }


def build_rc4_sprint8a_evidence_provenance_report(
    books_with_ir: List[Dict[str, Any]],
) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "sprint": "RC4 Sprint 8A — Evidence Provenance Trace",
        "generated_at": datetime.fromtimestamp(0, tz=timezone.utc).isoformat() + "Z",
        "total_books": len(books_with_ir),
        "books": [],
        "shadow_only": True,
        "production_output_changed": False,
    }

    synthesizer = EvidenceSynthesizer()

    for book in books_with_ir:
        book_id = book.get("book_id") or book.get("title") or "unknown"
        summary_ir = deepcopy(book.get("summary_ir") or {})

        evidence_trace = _trace_evidence_snippets(summary_ir.get("evidence_snippets", {}), synthesizer)
        builder_input = _build_builder_input(summary_ir)

        narrative_builder = SemanticNarrativeBuilder(summary_ir)
        builder_output = narrative_builder.build()

        summary_surfaces = build_summary_surfaces_from_ir(summary_ir)

        book_result = {
            "book_id": book_id,
            "title": book.get("title") or summary_ir.get("title"),
            "summary_ir": deepcopy(summary_ir),
            "summary_ir_trace": {
                "source_metadata": summary_ir.get("source_metadata", {}),
                "diagnostics": summary_ir.get("diagnostics", {}),
                "central_entities": summary_ir.get("central_entities", []),
                "themes": summary_ir.get("themes", []),
                "places": summary_ir.get("places", []),
                "learning_outcomes": summary_ir.get("learning_outcomes", []),
                "timeline": summary_ir.get("timeline", []),
                "confidence": summary_ir.get("confidence", {}),
            },
            "raw_evidence": deepcopy(summary_ir.get("evidence_snippets", {})),
            "synthesized_evidence": evidence_trace,
            "builder_input": builder_input,
            "builder_output": builder_output,
            "final_report_output": {
                "summary_surfaces": summary_surfaces,
            },
        }

        report["books"].append(book_result)

    return report


def main(output_path: Optional[Path] = None) -> Dict[str, Any]:
    # Allow loading runtime payload JSON files when path(s) provided via CLI or
    # environment variable `RUNTIME_PAYLOAD_DIR`. If none found, fall back to
    # the deterministic TRACE_CASES sample data.
    runtime_books = []
    # CLI: optional path argument (file or directory)
    cli_arg = None
    if len(sys.argv) > 1:
        cli_arg = sys.argv[1]

    candidate_paths = []
    if cli_arg:
        candidate_paths.append(cli_arg)
    env_dir = os.environ.get("RUNTIME_PAYLOAD_DIR")
    if env_dir:
        candidate_paths.append(env_dir)

    for p in candidate_paths:
        try:
            ppath = Path(p)
        except Exception:
            continue
        if ppath.is_file() and ppath.suffix.lower() == ".json":
            candidate = ppath
            try:
                payload = json.loads(candidate.read_text(encoding="utf-8-sig") or "{}")
            except Exception:
                payload = {}
            # try extract canonical_summary_ir or summary_ir
            summary_ir = payload.get("canonical_summary_ir") or payload.get("summary_ir") or payload.get("analiz_sonucu") or payload
            if isinstance(summary_ir, dict):
                runtime_books.append({"book_id": str(summary_ir.get("book_id") or summary_ir.get("title") or payload.get("kitap_adi") or candidate.stem), "title": str(summary_ir.get("title") or payload.get("kitap_adi") or candidate.stem), "summary_ir": summary_ir})
        elif ppath.is_dir():
            for child in ppath.iterdir():
                if child.is_file() and child.suffix.lower() == ".json" and child.name.startswith("runtime_"):
                    try:
                        payload = json.loads(child.read_text(encoding="utf-8-sig") or "{}")
                    except Exception:
                        payload = {}
                    summary_ir = payload.get("canonical_summary_ir") or payload.get("summary_ir") or payload.get("analiz_sonucu") or payload
                    if isinstance(summary_ir, dict):
                        runtime_books.append({"book_id": str(summary_ir.get("book_id") or summary_ir.get("title") or payload.get("kitap_adi") or child.stem), "title": str(summary_ir.get("title") or payload.get("kitap_adi") or child.stem), "summary_ir": summary_ir})

    books_to_trace = runtime_books if runtime_books else TRACE_CASES

    artifact_path = Path(output_path) if output_path else Path(__file__).resolve().parent / "rc4_sprint8a_evidence_provenance_trace.json"
    report = build_rc4_sprint8a_evidence_provenance_report(books_to_trace)
    artifact_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    artifact = main()
    print(json.dumps(artifact, ensure_ascii=False, indent=2))
