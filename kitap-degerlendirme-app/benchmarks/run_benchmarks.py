import csv
from pathlib import Path
from lib.summary_ir import SummaryIR, SummarySection
from lib.surface_realizer import SurfaceRealizer
from lib.quality_gate import QualityGate


def make_sample_ir(idx: int) -> SummaryIR:
    secs = []
    # vary size and content
    for i in range(1, 1 + (idx % 3) + 1):
        blurb = f"Özet paragrafı {idx}.{i}. Bu kitapta önemli noktalar ve ana tema özetlenir."
        secs.append(SummarySection(id=f"s{idx}-{i}", title=f"Bölüm {i}", events=[f"e{idx}{i}"], blurb=blurb))

    ir = SummaryIR(
        book_type="deneme" if idx % 2 == 0 else "roman",
        narrative_type="özet",
        entity_graph={f"K{i}": {} for i in range(1, (idx % 4) + 2)},
        event_graph={f"e{idx}{i}": {} for i in range(1, (idx % 4) + 2)},
        story_arc={"arc_type": "basic"},
        summary_sections=secs,
        themes=[{"name": "kimlik"}],
        evidence=[f"Kanıt cümlesi {idx}"],
        confidence=0.5 + (idx * 0.1),
    )
    return ir


def run():
    out_dir = Path(__file__).resolve().parent
    report_path = out_dir / "report.csv"
    sr = SurfaceRealizer()
    q = QualityGate()

    rows = []
    for i in range(1, 5):
        ir = make_sample_ir(i)
        realize_out = sr.realize(ir)
        merged = {**ir.to_dict(), **realize_out, 'forbidden_phrases': sr.forbidden}
        gate = q.run(merged)
        rows.append({
            "id": i,
            "status": gate['status'],
            "issues": ';'.join(gate['issues']),
            "confidence": merged.get('confidence', 0.0),
            "word_count": gate['details'].get('word_count', 0),
        })

    with report_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "status", "issues", "confidence", "word_count"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Benchmark complete — report written to: {report_path}")


if __name__ == '__main__':
    run()
