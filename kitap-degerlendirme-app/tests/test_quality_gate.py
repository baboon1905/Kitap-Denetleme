from lib.summary_ir import SummaryIR, SummarySection
from lib.surface_realizer import SurfaceRealizer
from lib.quality_gate import QualityGate


def make_ir(min_sec=1, words_per_sec=20, conf=0.6):
    secs = []
    for i in range(min_sec):
        blurb = "Bu bölümün kısa özeti." + (" ek cümle." * (words_per_sec // 3))
        secs.append(SummarySection(id=f"s{i}", title=f"Bölüm {i}", events=["e1"], blurb=blurb))
    ir = SummaryIR(
        book_type="deneme",
        narrative_type="özet",
        entity_graph={},
        event_graph={"e1": {}},
        story_arc={},
        summary_sections=secs,
        themes=[],
        evidence=[],
        confidence=conf,
    )
    return ir


def test_quality_gate_pass():
    ir = make_ir(min_sec=2, words_per_sec=40, conf=0.8)
    sr = SurfaceRealizer()
    out = sr.realize(ir)
    q = QualityGate(min_words=30, min_confidence=0.5)
    res = q.run({**ir.to_dict(), **out, 'forbidden_phrases': sr.forbidden})
    assert res['status'] == 'PASS' or res['status'] == 'WARNING'


def test_quality_gate_forbidden():
    ir = make_ir(min_sec=1, words_per_sec=5, conf=0.9)
    # Inject a forbidden phrase into blurb
    ir.summary_sections[0].blurb += " daha dengeli bir kapanış"
    sr = SurfaceRealizer()
    out = sr.realize(ir)
    q = QualityGate(min_words=10, min_confidence=0.5)
    res = q.run({**ir.to_dict(), **out, 'forbidden_phrases': sr.forbidden})
    assert res['status'] == 'FAIL'


def test_event_coverage_warning():
    # event_graph has 3 events but only 1 referenced -> low coverage
    ir = make_ir(min_sec=1, words_per_sec=40, conf=0.9)
    ir.event_graph = {'e1': {}, 'e2': {}, 'e3': {}}
    ir.summary_sections[0].events = ['e1']
    sr = SurfaceRealizer()
    out = sr.realize(ir)
    q = QualityGate(min_words=10, min_confidence=0.5, min_event_coverage=0.6)
    res = q.run({**ir.to_dict(), **out, 'forbidden_phrases': sr.forbidden})
    assert any('low_event_coverage' in s for s in res['issues'])


def test_high_quote_ratio_warning():
    ir = make_ir(min_sec=1, words_per_sec=40, conf=0.9)
    # create many quoted segments
    ir.summary_sections[0].blurb = '"alıntı" ' * 50
    sr = SurfaceRealizer()
    out = sr.realize(ir)
    q = QualityGate(min_words=1, min_confidence=0.1, max_quote_ratio=0.05)
    res = q.run({**ir.to_dict(), **out, 'forbidden_phrases': sr.forbidden})
    assert any('high_quote_ratio' in s for s in res['issues'])
