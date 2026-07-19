"""
Diagnose Narrative Realizer integration issues.
Tests the full pipeline from event graph to quality gate.
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Direct test of narrative_realizer
from narrative_realizer import build_story_graph, narrative_realize, narrative_realize_olay_akisi

# Simulate a real event graph (like _extract_event_graph would produce)
event_graph = [
    {"sayfa": 1, "olay_turu": "olay", "ilgili_karakterler": ["Ali"],
     "kaynak_metin": "Ali okula gitmek icin evden cikti.",
     "neden": "Başlangıç durumu karakteri harekete geçiren ilk koşulu oluşturur.",
     "sonuc": "Olay zincirinde bir sonraki adıma geçiş hazırlanır.",
     "olay_basligi": "Olay adımı 1: Ali"},
    {"sayfa": 2, "olay_turu": "karar", "ilgili_karakterler": ["Ali"],
     "kaynak_metin": "Ali arkadasina yardim etmeye karar verdi.",
     "neden": "Önceki olayda ortaya çıkan durum yeni bir karar adımını gerekli kılar.",
     "sonuc": "Karakterin seçimi sonraki olayların yönünü belirler.",
     "olay_basligi": "Karar anı 2: Ali"},
    {"sayfa": 3, "olay_turu": "çatışma", "ilgili_karakterler": ["Ali", "Ayşe"],
     "kaynak_metin": "Ali ve Ayse arasinda bir anlasmazlik cikti.",
     "neden": "Metindeki gerekçe, karakterin durumu anlamaya veya seçim yapmaya yöneldiğini gösterir.",
     "sonuc": "Temel sorun görünür hale gelir ve gerilim artar.",
     "olay_basligi": "Çatışmanın belirginleşmesi 3: Ali"},
    {"sayfa": 4, "olay_turu": "çözüm", "ilgili_karakterler": ["Ali", "Ayşe"],
     "kaynak_metin": "Ali ve Ayse konusarak sorunu cozduler.",
     "neden": "Önceki olayda ortaya çıkan durum yeni bir çözüm adımını gerekli kılar.",
     "sonuc": "Olay örgüsünde çözüm veya yeni anlayış yönünde ilerleme sağlanır.",
     "olay_basligi": "Çözümün görünmesi 4: Ali"},
]
characters = [{"ad": "Ali", "ana_karakter_mi": True}, {"ad": "Ayşe", "ana_karakter_mi": False}]

print("=" * 60)
print("DIAGNOSTIC 1: narrative_realize() output")
print("=" * 60)
summary = narrative_realize("Test Kitap", event_graph, characters, min_kelime=10)
print(f"  Summary generated: {bool(summary)}")
print(f"  Summary type: {type(summary).__name__}")
print(f"  Word count: {len(summary.split()) if summary else 0}")
print(f"  Summary preview: {summary[:300] if summary else 'EMPTY'}...")
print()

print("=" * 60)
print("DIAGNOSTIC 2: Quality gate natural summary check")
print("=" * 60)
# Simulate what _summary_heading_count does
from theme_gain_analysis import _summary_heading_count, _summary_is_valid_for_report, _summary_is_reportable_with_lower_confidence, _summary_concreteness_score
heading_count = _summary_heading_count(summary)
valid = _summary_is_valid_for_report(summary)
reportable = _summary_is_reportable_with_lower_confidence(summary, _summary_concreteness_score(summary))
print(f"  Heading count: {heading_count} (natural summaries may have 0)")
print(f"  Is valid for report: {valid}")
print(f"  Reportable with lower confidence: {reportable}")
print()

print("=" * 60)
print("DIAGNOSTIC 3: summary_quality_issues check")
print("=" * 60)
from theme_gain_analysis import summary_quality_issues, _select_report_summary, _summary_forbidden_content_ratio
issues = summary_quality_issues(summary)
forbidden_ratio = _summary_forbidden_content_ratio(summary)
print(f"  Issues: {issues}")
print(f"  Forbidden ratio: {forbidden_ratio}")
print()

print("=" * 60)
print("DIAGNOSTIC 4: Story Graph contract")
print("=" * 60)
story_graph = build_story_graph(event_graph)
required_story_keys = {"scene", "actors", "goal", "conflict", "turning_point", "outcome", "evidence"}
missing_story_keys = [
    sorted(required_story_keys - set(scene.keys()))
    for scene in story_graph
    if required_story_keys - set(scene.keys())
]
print(f"  Story Graph scenes: {len(story_graph)}")
print(f"  Missing Story Graph keys: {missing_story_keys}")
print(f"  Words: {len(summary.split())}")
print()

print("=" * 60)
print("DIAGNOSTIC 5: olay_akisi items")
print("=" * 60)
oa = narrative_realize_olay_akisi(event_graph, characters)
print(f"  Items: {len(oa)}")
for item in oa:
    print(f"  [{item.get('sayfa')}] {item.get('metin')[:100]}")
print()

print("=" * 60)
print("ROOT CAUSE SUMMARY")
print("=" * 60)
print(f"""
1. narrative_realize() works? {'YES' if summary else 'NO'}
2. Pipeline labels in output? {'YES - NEEDS FIX' if any(t in summary for t in ['Olay adımı', 'Başlangıç']) else 'NO - CLEAN'}
3. Natural summary accepted? {'YES - PASSES GATE' if valid else 'NO - BLOCKED BY GATE'}
4. Forbidden content? {'YES' if forbidden_ratio > 0.5 else 'NO - CLEAN'}
5. Quality gate blocks? {'YES - THIS IS THE BUG' if not valid else 'NO - PASSES'}

PIPELINE:
Evidence -> Canonical Events -> Story Graph -> Narrative Generator -> Summary.
The current Summary is natural prose; headings are not required for the gate when the text is
long enough, coherent enough, and free of internal pipeline phrases.
""")
