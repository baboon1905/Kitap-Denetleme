"""
Narrative Realizer test script
"""
import sys
sys.path.insert(0, r"c:\Users\fatih\Masaüstü\Kitap Değerlendirme\kitap-degerlendirme-app")

from narrative_realizer import build_story_graph, narrative_realize, narrative_realize_olay_akisi, _summary_quote_ratio, _fold_text

passed = 0
failed = 0

def check(condition, msg):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS: {msg}")
    else:
        failed += 1
        print(f"  FAIL: {msg}")

# Test 1: Empty event graph
result = narrative_realize("Test", [], [])
check(_fold_text(result) == _fold_text("olay örgüsü güvenilir biçimde çıkarılamadı"), "Empty graph returns placeholder")

# Test 2: < 3 nodes
result = narrative_realize("Test", [{"olay_turu": "olay", "kaynak_metin": "Test"}], [])
check(_fold_text(result) == _fold_text("olay örgüsü güvenilir biçimde çıkarılamadı"), "< 3 nodes returns placeholder")

# Test 3: Pipeline labels are scrubbed
event_graph = [
    {"sayfa": 1, "olay_turu": "olay", "ilgili_karakterler": ["Ali"],
     "kaynak_metin": "Ali okula gitmek icin evden cikti.",
     "neden": "Başlangıç durumu karakteri harekete geçiren ilk koşulu oluşturur.",
     "sonuc": "Olay zincirinde bir sonraki adıma geçiş hazırlanır."},
    {"sayfa": 2, "olay_turu": "karar", "ilgili_karakterler": ["Ali"],
     "kaynak_metin": "Ali arkadasina yardim etmeye karar verdi.",
     "neden": "Önceki olayda ortaya çıkan durum yeni bir karar adımını gerekli kılar.",
     "sonuc": "Karakterin seçimi sonraki olayların yönünü belirler."},
    {"sayfa": 3, "olay_turu": "çatışma", "ilgili_karakterler": ["Ali", "Ayşe"],
     "kaynak_metin": "Ali ve Ayse arasinda bir anlasmazlik cikti.",
     "neden": "Metindeki gerekçe, karakterin durumu anlamaya veya seçim yapmaya yöneldiğini gösterir.",
     "sonuc": "Temel sorun görünür hale gelir ve gerilim artar."},
    {"sayfa": 4, "olay_turu": "çözüm", "ilgili_karakterler": ["Ali", "Ayşe"],
     "kaynak_metin": "Ali ve Ayse konusarak sorunu cozduler.",
     "neden": "Önceki olayda ortaya çıkan durum yeni bir çözüm adımını gerekli kılar.",
     "sonuc": "Olay örgüsünde çözüm veya yeni anlayış yönünde ilerleme sağlanır."},
]
characters = [{"ad": "Ali", "ana_karakter_mi": True}, {"ad": "Ayşe"}]

result = narrative_realize("Test Kitap", event_graph, characters, min_kelime=20)
check(bool(result), "Generates non-empty result with 4 nodes")
check("olay adımı" not in result.lower(), "No 'olay adımı' label")
check("başlangıç durumu" not in result.lower(), "No 'başlangıç durumu' label")
check("çatışma" not in result.lower() or "çatışma adımı" not in result.lower(), "No 'çatışma adımı' label")
check("karar anı" not in result.lower(), "No 'karar anı' label")
check("eylemini ger" not in result.lower(), "No forbidden 'eylemini gerceklestirir' pattern")
for heading in (
    "Hikâyenin başlangıcı:",
    "Temel çatışma:",
    "Karakterlerin girişimleri:",
    "Dönüm noktası:",
    "Çözüm veya çözüm arayışı:",
):
    check(heading not in result, f"Story summary is natural prose, no heading: {heading}")
story_graph = build_story_graph(event_graph)
check(len(story_graph) >= 5, "Story Graph has scene-level nodes")
for i, scene in enumerate(story_graph):
    for key in ("scene", "actors", "goal", "conflict", "turning_point", "outcome", "evidence"):
        check(key in scene, f"story_graph[{i}]: has {key} key")
for forbidden in ("aktör", "eylem", "tam olay örgüsü", "kanıt", "sonuç"):
    check(forbidden not in result.lower(), f"Story summary avoids technical term: {forbidden}")
for forbidden in (
    "sahnedeki sorun veya ipucu",
    "sahnedeki belirsizlik",
    "sahne yeni bir yere veya karara yönelir",
    "daha önce öğrenilenler",
    "belirleyici bir iz",
    "paylaşım karakterler arasındaki yönelişi değiştirir",
    "çözüm için kullanılabilecek bilgi ortaya çıkar",
    "karabasan sorununa karşı çözüm arayışı belirginleşir",
    "önemli bilgi",
    "somut bir adım",
    "çözüm için harekete geçer",
    "durumu daha iyi anlar",
    "önceki gelişmenin ardından",
    "önceki sahnedeki bilgi",
    "önemli buluşunu paylaşır",
    "çözüm yolunu başlatır",
    "olayın anlamını kavrar",
):
    check(forbidden not in result.lower(), f"Story summary avoids internal phrase: {forbidden}")
check(result != "olay örgüsü güvenilir biçimde çıkarılamadı", "Not placeholder")
check(110 <= len(result.split()) <= 160, "Book summary stays in 110-160 words when graph is usable")
for forbidden in (
    "pedagojik değer",
    "duygusal yön",
    "anlatının değeri",
    "kararlarının birbirini nasıl etkilediği",
    "değişir",
    "her karar",
):
    check(forbidden not in result.lower(), f"Story summary avoids commentary phrase: {forbidden}")
check(not ("okur" in result.lower() and "kavrar" in result.lower()), "Story summary avoids okur-kavrar commentary")
check(any(connector in result.lower() for connector in ("bu nedenle", "böylece", "bu yüzden", "bağlantılı", "etkisini")), "Book summary includes cause-effect flow")
print(f"  Generated summary ({len(result.split())} words):")
print(f"  {result[:200]}...")
print()

# Test 4: olay_akisi
oa = narrative_realize_olay_akisi(event_graph, characters)
check(len(oa) >= 3, f"olay_akisi has {len(oa)} items (expected >= 3)")
for i, item in enumerate(oa):
    check("Olay adımı" not in item["metin"], f"olay_akisi[{i}]: no pipeline labels")
    check("sayfa" in item, f"olay_akisi[{i}]: has sayfa key")
    check("metin" in item, f"olay_akisi[{i}]: has metin key")
    for key in ("scene_id", "page", "actor", "goal", "action", "object", "obstacle", "consequence", "evidence"):
        check(key in item, f"olay_akisi[{i}]: has {key} key")
print()

# Test 5: Empty for < 3 nodes
oa2 = narrative_realize_olay_akisi(event_graph[:2], characters)
check(len(oa2) == 0, "olay_akisi returns empty for < 3 nodes")

# Test 6: Action labels are realized naturally
label_graph = [
    {"scene_id": "S1", "page": 1, "actor": "Kral Kapgötür", "actors": ["Kral Kapgötür"], "goal": "karabasan sorununu anlamak", "action": "bilgi aktarmak", "object": "Kapgötür", "obstacle": "karabasan belirsizliği", "consequence": "danışmanlar yeni bilgiyi tartışır", "evidence": "Kral Kapgötür yeni buluşu danışmanlarına anlattı."},
    {"scene_id": "S2", "page": 2, "actor": "Yasemin", "actors": ["Yasemin"], "goal": "çözüm bulmak", "action": "somut bir karar uygulamak", "object": "çözüm", "obstacle": "zaman baskısı", "consequence": "çözüm yolu belirginleşir", "evidence": "Yasemin çözüm için harekete geçti."},
    {"scene_id": "S3", "page": 3, "actor": "Yasemin", "actors": ["Yasemin"], "goal": "sorunu yatıştırmak", "action": "konuşarak çözmek", "object": "sorun", "obstacle": "anlaşmazlık", "consequence": "karakterler sakinleşir", "evidence": "Yasemin konuşarak sorunu yatıştırdı."},
]
label_summary = narrative_realize("Kapgötür", label_graph, [{"ad": "Kral Kapgötür"}, {"ad": "Yasemin"}], min_kelime=20)
label_flow = narrative_realize_olay_akisi(label_graph, [])
for forbidden in ("bilgi aktarmak", "somut bir karar uygulamak"):
    check(forbidden not in label_summary.lower(), f"Story summary hides action label: {forbidden}")
    check(all(forbidden not in item["metin"].lower() for item in label_flow), f"Flow hides action label: {forbidden}")
def _fold_contains_all(item_text, keywords):
    f = _fold_text(item_text)
    return all(k in f for k in keywords)

check(any(_fold_contains_all(item["metin"], ["yeni", "anlat", "bul"]) for item in label_flow), "Flow expands weak invention-sharing sentence")
check(
    any(
        _fold_contains_all(item["metin"], ["sorun", "coz", "birlikte"]) or _fold_contains_all(item["metin"], ["karar", "uygulama"]) 
        for item in label_flow
    ),
    "Flow paraphrases somut karar",
)
for forbidden in (
    "sahnedeki belirsizlik",
    "sahne yeni bir yere veya karara yönelir",
    "daha önce öğrenilenler",
    "belirleyici bir iz",
    "paylaşım karakterler arasındaki yönelişi değiştirir",
    "çözüm için kullanılabilecek bilgi ortaya çıkar",
    "karabasan sorununa karşı çözüm arayışı belirginleşir",
    "önemli bilgi",
    "somut bir adım",
    "çözüm için harekete geçer",
    "durumu daha iyi anlar",
    "önceki gelişmenin ardından",
    "önceki sahnedeki bilgi",
    "önemli buluşunu paylaşır",
    "çözüm yolunu başlatır",
    "olayın anlamını kavrar",
):
    check(forbidden not in label_summary.lower(), f"Label summary avoids internal phrase: {forbidden}")
    check(all(forbidden not in item["metin"].lower() for item in label_flow), f"Flow avoids internal phrase: {forbidden}")

technical_graph = [
    {"scene_id": "T1", "page": 1, "actor": "Kral Kapgötür", "actors": ["Kral Kapgötür"], "goal": "sahnedeki belirsizlik", "action": "sorgulamak", "obstacle": "sahnedeki belirsizlik", "consequence": "sahne yeni bir yere veya karara yönelir", "evidence": "Kral Kapgötür sahnedeki belirsizlik için durumun nedenini sorgular."},
    {"scene_id": "T2", "page": 2, "actor": "Aydın Öğretmen", "actors": ["Aydın Öğretmen"], "goal": "daha önce öğrenilenler", "action": "bilgi aktarmak", "obstacle": "belirleyici bir iz", "consequence": "çözüm için kullanılabilecek bilgi ortaya çıkar", "evidence": "Aydın Öğretmen buluşunu anlatır."},
    {"scene_id": "T3", "page": 3, "actor": "Yasemin", "actors": ["Yasemin"], "goal": "çözüm bulmak", "action": "somut bir karar uygulamak", "obstacle": "karabasan sorunu", "consequence": "karabasan sorununa karşı çözüm arayışı belirginleşir", "evidence": "Yasemin kararını uygulamaya koyar."},
]
technical_summary = narrative_realize("Teknik Test", technical_graph, [], min_kelime=20)
ft = _fold_text(technical_summary)
check(
    ("kısa özet sınırlı tutulmuştur" in technical_summary.lower())
    or (_fold_text(technical_summary).find(_fold_text("kısa özet sınırlı tutulmuştur")) != -1)
    or ("azet" in ft and "tutul" in ft),
    "Technical fallback returns safe limited summary",
)
for forbidden in (
    "sahnedeki belirsizlik",
    "sahne yeni bir yere veya karara yönelir",
    "daha önce öğrenilenler",
    "belirleyici bir iz",
    "paylaşım karakterler arasındaki yönelişi değiştirir",
    "çözüm için kullanılabilecek bilgi ortaya çıkar",
    "karabasan sorununa karşı çözüm arayışı belirginleşir",
):
    check(forbidden not in technical_summary.lower(), f"Safe summary avoids forbidden phrase: {forbidden}")

human_graph = [
    {"scene_id": "H1", "page": 1, "actor": "Kral Kapgötür", "actors": ["Kral Kapgötür"], "goal": "halkın tepkisini anlamak", "action": "sorgulamak", "obstacle": "halkla arasındaki kopukluk", "consequence": "yönetim biçimini sorgulamaya başlar", "evidence": "Kral Kapgötür, halkının kendisini neden sevmediğini anlamaya çalışır."},
    {"scene_id": "H2", "page": 2, "actor": "Aydın Öğretmen", "actors": ["Aydın Öğretmen"], "goal": "karabasanların kaynağını açıklamak", "action": "bilgi paylaşmak", "obstacle": "öğrencilerin korkusu", "consequence": "öğrencilerle birlikte çözüm arar", "evidence": "Aydın Öğretmen, karabasanların nedenini öğrenince öğrencileriyle birlikte çözüm aramaya başlar."},
    {"scene_id": "H3", "page": 3, "actor": "Yasemin", "actors": ["Yasemin"], "goal": "karabasanlardan kurtulmak", "action": "çare düşünmek", "obstacle": "korkunun yayılması", "consequence": "arkadaşlarıyla ortak hareket eder", "evidence": "Yasemin, karabasanlardan kurtulmak için arkadaşlarıyla birlikte bir çare düşünür."},
]
human_summary = narrative_realize("Doğal Test", human_graph, [], min_kelime=20)
human_summary_fold = _fold_text(human_summary)
human_summary_limited = "kısa özet sınırlı tutulmuştur" in human_summary_fold
check(human_summary_limited or (_fold_text("kapgötür") in human_summary_fold and "neden" in human_summary_fold), "Summary paraphrases Kapgötür evidence or falls back safely")
check(human_summary_limited or (_fold_text("aydın öğretmen") in human_summary_fold and ("kayna" in human_summary_fold or "karabasan" in human_summary_fold)), "Summary paraphrases Aydın Öğretmen evidence or falls back safely")
check(human_summary_limited or (_fold_text("yasemin") in human_summary_fold and ("karabasan" in human_summary_fold or "çözüm" in human_summary_fold)), "Summary paraphrases Yasemin evidence or falls back safely")
check("Kral Kapgötür, halkının kendisini neden sevmediğini anlamaya çalışır." not in human_summary, "Summary does not copy Kapgötür evidence")
check("Aydın Öğretmen, karabasanların nedenini öğrenince öğrencileriyle birlikte çözüm aramaya başlar." not in human_summary, "Summary does not copy Aydın evidence")
check(_summary_quote_ratio(human_summary, human_graph) <= 0.25, "Human summary quote ratio stays under 25 percent")
check(human_summary_limited or 110 <= len(human_summary.split()) <= 160, "Human summary stays in 110-160 words when not limited")
for forbidden in (
    "pedagojik değer",
    "duygusal yön",
    "anlatının değeri",
    "kararlarının birbirini nasıl etkilediği",
    "değişir",
    "her karar",
):
    check(forbidden not in human_summary.lower(), f"Human summary avoids commentary phrase: {forbidden}")
check(not ("okur" in human_summary.lower() and "kavrar" in human_summary.lower()), "Human summary avoids okur-kavrar commentary")
check(any(connector in human_summary.lower() for connector in ("bu nedenle", "böylece", "bu yüzden", "bağlantılı", "etkisini")), "Human summary includes cause-effect flow")
for forbidden in (
    "sahnedeki belirsizlik",
    "sahne yeni bir yere veya karara yönelir",
    "daha önce öğrenilenler",
    "belirleyici bir iz",
    "paylaşım karakterler arasındaki yönelişi değiştirir",
    "çözüm için kullanılabilecek bilgi ortaya çıkar",
    "karabasan sorununa karşı çözüm arayışı belirginleşir",
):
    check(forbidden not in human_summary.lower(), f"Human summary avoids forbidden phrase: {forbidden}")

editorial_graph = [
    {"scene_id": "E1", "page": 1, "actor": "Yılanson", "actors": ["Yılanson"], "action": "buluş sunmak", "evidence": "YILANSON'UN BULUŞU Yılanson, Kapgötür'e, önce kuşkuyla karşılanan yeni buluşunu anlatır."},
    {"scene_id": "E2", "page": 2, "actor": "Yasemin", "actors": ["Yasemin"], "action": "çözüm aramak", "evidence": '"El birliği yaparsak mutlaka bir çare buluruz." dedi Yasemin.'},
    {"scene_id": "E3", "page": 3, "actor": "Kral Kapgötür", "actors": ["Kral Kapgötür"], "action": "gözetlemek", "evidence": "Kapgötür, her sabah teleskobunu kaptığı gibi ülkesini gözetlemek için kuleye çıkar."},
]
editorial_summary = narrative_realize("Editorial Test", editorial_graph, [], min_kelime=20)
check("YILANSON" not in editorial_summary, "Summary strips uppercase heading")
check("El birliği yaparsak" not in editorial_summary, "Summary strips direct dialogue")
check("Kapgötür, her sabah teleskobunu kaptığı gibi" not in editorial_summary, "Summary does not copy source narration")
es = _fold_text(editorial_summary)
check(
    _fold_text("yilanson") in es and ("anlat" in es or "bulus" in es or "anlatarak" in es),
    "Summary paraphrases heading scene",
)
check(
    (_fold_text("yasemin") in _fold_text(editorial_summary) and ("arkadas" in _fold_text(editorial_summary) or "dayanisma" in _fold_text(editorial_summary) or "cozum" in _fold_text(editorial_summary)))
    or (_fold_text("karakterler") in _fold_text(editorial_summary) and ("dayanisma" in _fold_text(editorial_summary) or "birlikte" in _fold_text(editorial_summary))),
    "Summary paraphrases dialogue meaning",
)
es = _fold_text(editorial_summary)
check(
    _fold_text("kapgotur") in es and ("gozet" in es or ("olay" in es and "iler" in es)),
    "Summary paraphrases surveillance scene",
)
check(_summary_quote_ratio(editorial_summary, editorial_graph) <= 0.25, "Editorial summary quote ratio stays under 25 percent")

print(f"\n{'='*40}")
print(f"Results: {passed} passed, {failed} failed")
if failed:
    sys.exit(1)
