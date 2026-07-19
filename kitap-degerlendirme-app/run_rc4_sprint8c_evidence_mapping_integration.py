#!/usr/bin/env python3
"""RC4 Sprint 8C - Evidence Mapping Integration (shadow-only)

Builds shadow SummaryIR from runtime payloads using prioritized paths,
runs `SemanticNarrativeBuilder` and `EvidenceSynthesizer` in shadow mode,
evaluates summary quality using `summary_quality_engine.evaluate_summary_quality`,
and writes results to `rc4_sprint8c_mapping_integration_results.json`.
"""
import json
from pathlib import Path
from typing import Any, Dict, List

from runtime_v7.evidence_mapping_integration import build_summary_ir_from_payload
from runtime_v7.semantic_narrative_builder import SemanticNarrativeBuilder
from runtime_v7.evidence_synthesizer import EvidenceSynthesizer
from runtime_v7.summary_quality_engine import evaluate_summary_quality


PRIORITIZED_PATHS = [
    "tema_analizi[*]/kanitlar",
    "kazanim_analizi[*]/kanitlar",
    "baskin_tema_ozeti[*]/kanitlar",
    "guclu_temalar[*]/kanitlar",
    "event_graph[*]/evidence",
    "story_graph[*]/events[*]/evidence",
    "scene_graph[*]/events[*]/evidence",
]

RUNTIME_FILES = [
    "runtime_1_analyze_theme_gain_return.json",
    "runtime_2_build_pdf_report_input.json",
    "runtime_theme_final_selection_debug.json",
]


def _synthesize_extracted(extracted: List[Dict[str, Any]], synthesizer: EvidenceSynthesizer) -> List[Dict[str, Any]]:
    out = []
    for item in extracted:
        text = item.get("text") if isinstance(item, dict) else str(item)
        synthesized = synthesizer.synthesize(text) if text else ""
        out.append({"original": text, "synthesized": synthesized, "source_sentence_id": item.get("source_sentence_id")})
    return out


def run(payload_dir: Path, output_path: Path) -> Dict[str, Any]:
    synthesizer = EvidenceSynthesizer()
    results = {"sprint": "RC4 Sprint 8C - Evidence Mapping Integration", "books": []}

    for fname in RUNTIME_FILES:
        fpath = payload_dir / fname
        if not fpath.exists():
            continue
        payload = json.loads(fpath.read_text(encoding="utf-8-sig") or "{}")

        summary_ir = build_summary_ir_from_payload(payload, PRIORITIZED_PATHS)

        builder = SemanticNarrativeBuilder(summary_ir)
        builder_output = builder.build()
        narrative = builder_output.get("narrative", "")

        evaluation = evaluate_summary_quality(narrative, summary_ir)

        raw_extracted = summary_ir.get("evidence_snippets", {}).get("__raw_extracted__", [])
        synthesized_trace = _synthesize_extracted(raw_extracted, synthesizer)

        book_result: Dict[str, Any] = {
            "file": fname,
            "title": summary_ir.get("title") or payload.get("kitap_adi"),
            "summary_ir": summary_ir,
            "builder_output": builder_output,
            "evaluation": evaluation,
            "synthesized_trace": synthesized_trace,
        }

        results["books"].append(book_result)

    # Aggregates
    total = len(results["books"])
    passed = sum(1 for b in results["books"] if b.get("evaluation", {}).get("passed"))
    avg_quality = (
        sum(b.get("evaluation", {}).get("summary_quality_score", 0.0) for b in results["books"]) / total
        if total
        else 0.0
    )
    avg_concreteness = (
        sum(b.get("evaluation", {}).get("concreteness_score", 0.0) for b in results["books"]) / total
        if total
        else 0.0
    )
    avg_coherence = (
        sum(b.get("evaluation", {}).get("coherence", 0.0) for b in results["books"]) / total
        if total
        else 0.0
    )

    results["total_books"] = total
    results["passed_count"] = passed
    results["failed_count"] = total - passed
    results["average_summary_quality_score"] = round(avg_quality, 3)
    results["average_concreteness_score"] = round(avg_concreteness, 3)
    results["average_coherence"] = round(avg_coherence, 3)

    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return results


if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    payload_dir = base
    output_path = base / "rc4_sprint8c_mapping_integration_results.json"
    artifact = run(payload_dir, output_path)
    print(json.dumps(artifact, ensure_ascii=False, indent=2))
