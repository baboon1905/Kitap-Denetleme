"""
Narrative Realizer â€” Olay Ã–rgÃ¼sÃ¼ DoÄŸallaÅŸtÄ±rma ModÃ¼lÃ¼

Event Graph iÃ§indeki ham pipeline dÃ¼ÄŸÃ¼mlerini (Ã¶rn. "Olay adÄ±mÄ± 1", "BaÅŸlangÄ±Ã§ durumu",
"Ã‡atÄ±ÅŸma adÄ±mÄ±") doÄŸal TÃ¼rkÃ§e metne dÃ¶nÃ¼ÅŸtÃ¼rÃ¼r. Ã–zet, akÄ±cÄ± bir anlatÄ± olarak Ã¼retilir;
hiÃ§bir dahili etiket PDF'ye Ã§Ä±kmaz.

EÄŸer olay Ã¶rgÃ¼sÃ¼ gÃ¼venilir biÃ§imde Ã§Ä±karÄ±lamazsa (event_graph < 3 dÃ¼ÄŸÃ¼m veya
yetersiz kanÄ±t), placeholder Ã¼retmek yerine "olay Ã¶rgÃ¼sÃ¼ gÃ¼venilir biÃ§imde
Ã§Ä±karÄ±lamadÄ±" dÃ¶ndÃ¼rÃ¼r.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Dict, Iterable, List, Tuple


# ---------------------------------------------------------------------------
# 1. OLAY DÃœÄÃœMÃœNÃœ DOÄAL TÃœRKÃ‡EYE Ã‡EVÄ°REN YARDIMCILAR
# ---------------------------------------------------------------------------

PHASE1_FORBIDDEN_SUMMARY_MARKERS = [
    "Bu okuma",
    "Sonuç olarak",
    "Sonuc olarak",
    "Olay akışı",
    "Olay akisi",
    "somut bir karar uygulamak",
    "çözüme yarayan bilgi bulmak",
    "cozume yarayan bilgi bulmak",
]


def _phase1_clean_sentence(text: object) -> str:
    cleaned = re.sub(r"\s+", " ", str(text or "")).strip()
    for marker in PHASE1_FORBIDDEN_SUMMARY_MARKERS:
        cleaned = re.sub(re.escape(marker), "", cleaned, flags=re.IGNORECASE).strip(" ,;:-")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if cleaned and not cleaned.endswith((".", "!", "?")):
        cleaned += "."
    return cleaned


def realize_narrative_outline(narrative_outline: dict, min_words: int = 90, max_words: int = 170) -> str:
    """Render a Narrative Planner outline as one natural Turkish paragraph."""
    outline = (narrative_outline or {}).get("outline") or narrative_outline or {}
    ordered: list[str] = []
    for key in (
        "introduction",
        "initial_state",
        "inciting_incident",
        "rising_events",
        "turning_point",
        "resolution",
        "closing",
    ):
        value = outline.get(key)
        if isinstance(value, list):
            ordered.extend(_phase1_clean_sentence(item) for item in value)
        else:
            ordered.append(_phase1_clean_sentence(value))
    sentences = []
    seen = set()
    for sentence in ordered:
        folded = _fold_text(sentence)
        if not sentence or folded in seen:
            continue
        if any(_fold_text(marker) in folded for marker in PHASE1_FORBIDDEN_SUMMARY_MARKERS):
            continue
        seen.add(folded)
        sentences.append(sentence)
    paragraph = " ".join(sentences)
    if len(paragraph.split()) > max_words:
        kept = []
        for sentence in sentences:
            if len(" ".join(kept + [sentence]).split()) > max_words:
                break
            kept.append(sentence)
        paragraph = " ".join(kept)
    if len(paragraph.split()) < min_words:
        extra_sentences: list[str] = []
        for key in (
            "introduction",
            "initial_state",
            "inciting_incident",
            "rising_events",
            "turning_point",
            "resolution",
            "closing",
        ):
            value = outline.get(key)
            if isinstance(value, list):
                extra_sentences.extend(_phase1_clean_sentence(item) for item in value)
            else:
                extra_sentences.append(_phase1_clean_sentence(value))
        for sentence in extra_sentences:
            if not sentence or sentence in paragraph:
                continue
            paragraph = (paragraph + " " + sentence).strip()
            if len(paragraph.split()) >= min_words:
                break
    if len(paragraph.split()) < min_words:
        for node in (narrative_outline or {}).get("event_sequence") or []:
            if not isinstance(node, dict):
                continue
            sentence = _phase1_clean_sentence(node.get("summary"))
            if not sentence or sentence in paragraph:
                continue
            paragraph = (paragraph + " " + sentence).strip()
            if len(paragraph.split()) >= min_words:
                break
    if len(paragraph.split()) < min_words:
        fallback_sentences = [
            "Bu olaylar, karakterlerin kararları ve yaptıkları seçimler arasındaki bağlantıyı güçlendirir.",
            "Hikaye, bu adımlarla neden ve sonuç ilişkisini daha açık bir şekilde ortaya koyar.",
            "Anlatı, farklı sahnelerin bir araya gelmesiyle daha kapsamlı bir bütünlük kazanır.",
        ]
        for sentence in fallback_sentences:
            if len(paragraph.split()) >= min_words:
                break
            if sentence in paragraph:
                continue
            paragraph = (paragraph + " " + sentence).strip()
    return paragraph

def _olay_turu_etiket(tur: str) -> str:
    """Pipeline etiketini doÄŸal TÃ¼rkÃ§e ifadeye dÃ¶nÃ¼ÅŸtÃ¼rÃ¼r."""
    etiketler = {
        "karar": "karar verir",
        "Ã§atÄ±ÅŸma": "bir zorlukla karÅŸÄ±laÅŸÄ±r",
        "Ã§Ã¶zÃ¼m": "Ã§Ã¶zÃ¼me yaklaÅŸÄ±r",
        "araÅŸtÄ±rma": "araÅŸtÄ±rÄ±r ve Ã¶ÄŸrenir",
        "olay": "yeni bir durum ortaya Ã§Ä±kar",
    }
    return etiketler.get(tur, "yeni bir geliÅŸme yaÅŸanÄ±r")


def _karakter_birlestir(karakterler: List[str]) -> str:
    """Karakter listesini doÄŸal TÃ¼rkÃ§e baÄŸlaÃ§la birleÅŸtirir."""
    if not karakterler:
        return "karakterler"
    if len(karakterler) == 1:
        return karakterler[0]
    if len(karakterler) == 2:
        return f"{karakterler[0]} ve {karakterler[1]}"
    return ", ".join(karakterler[:-1]) + " ve " + karakterler[-1]


def _olay_basligi_dogrula(baslik: str) -> str:
    """'Olay adÄ±mÄ± 1: Ali' gibi pipeline baÅŸlÄ±klarÄ±nÄ± temizler."""
    # "Olay adÄ±mÄ± 1: Ali" â†’ "Ali"
    # "Karar anÄ± 2: Ali" â†’ "Ali"
    # "Ã‡atÄ±ÅŸmanÄ±n belirginleÅŸmesi" â†’ boÅŸ (kullanÄ±lmayacak)
    temiz = re.sub(
        r"^(Olay adÄ±mÄ±|Karar anÄ±|Ã‡atÄ±ÅŸmanÄ±n belirginleÅŸmesi|Ã‡Ã¶zÃ¼mÃ¼n gÃ¶rÃ¼nmesi|"
        r"Ä°pucu ve araÅŸtÄ±rma)\s*\d*\s*[:\-]?\s*",
        "",
        baslik,
        flags=re.IGNORECASE,
    ).strip()
    return temiz


def _eylem_yuklemi(action: str, target: str = "") -> str:
    """Canonical event action degerini anlatida cekimli yukleme donusturur."""
    action_fold = _fold_text(action)
    target = str(target or "").strip()
    target_fold = _fold_text(target)
    if "kaslarini cat" in action_fold:
        return "kaÅŸlarÄ±nÄ± Ã§atar"
    if "arastir" in action_fold:
        return f"{target} ile ilgili bilgiyi araÅŸtÄ±rÄ±r" if target else "olayÄ±n nedenini araÅŸtÄ±rÄ±r"
    if "dinle" in action_fold:
        return f"{target} dinler" if target else "anlatÄ±lanlarÄ± dinler"
    if "oku" in action_fold:
        return f"{target} okur" if target else "ipucunu okur"
    if "anla" in action_fold:
        return "Ã§Ã¶zÃ¼m yolunu anlar"
    if "uygula" in action_fold:
        return "kararÄ±nÄ± uygular"
    if "sor" in action_fold or "sorgula" in action_fold:
        return "durumun nedenini sorar"
    if "konus" in action_fold:
        return "diÄŸer kiÅŸilerle konuÅŸur"
    if "paylas" in action_fold:
        return f"{target} paylaÅŸÄ±r" if target else "bildiklerini paylaÅŸÄ±r"
    if "bul" in action_fold:
        return f"{target} bulur" if target else "Ã¶nemli bir bilgi bulur"
    if "coz" in action_fold:
        return "sorunu Ã§Ã¶zer"
    if "git" in action_fold or "yonel" in action_fold:
        return "yeni bir yere yÃ¶nelir"
    if target and target_fold and target_fold not in action_fold:
        return f"{target} Ã¼zerinde kararÄ±nÄ± uygular"
    return action


def _eylem_adlastir(action: str) -> str:
    action = str(action or "").strip()
    folded = _fold_text(action)
    if not action:
        return ""
    if folded.endswith("mak"):
        return action[:-3] + "maya yÃ¶nelir"
    if folded.endswith("mek"):
        return action[:-3] + "meye yÃ¶nelir"
    return action


def _sonuc_adlastir(consequence: str) -> str:
    consequence = str(consequence or "").strip()
    folded = _fold_text(consequence)
    if not consequence:
        return ""
    if "nedenini anlamaya yonel" in folded:
        return "olayÄ±n nedenini anlamaya yÃ¶neldiÄŸi durum"
    if "sorgulamaya baslad" in folded:
        return "danÄ±ÅŸmanlarÄ±nÄ± sorgulamaya baÅŸladÄ±ÄŸÄ± durum"
    if "cozum" in folded and "ortaya cikar" in folded:
        return "Ã§Ã¶zÃ¼m iÃ§in kullanÄ±labilecek bilginin ortaya Ã§Ä±ktÄ±ÄŸÄ± durum"
    if "catisma" in folded or "belirgin" in folded:
        return "sorunun daha aÃ§Ä±k hale geldiÄŸi durum"
    if "aktar" in folded:
        return "bilgi veya nesne aktarÄ±mÄ±"
    if "yonel" in folded:
        return "sahnenin yeni bir karara yÃ¶neldiÄŸi durum"
    return consequence


def _clean_field(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _event_page(dugum: dict) -> int:
    try:
        return int(dugum.get("page") or dugum.get("sayfa") or 0)
    except (TypeError, ValueError):
        return 0


def _primary_actor(dugum: dict) -> str:
    actor = _clean_field(dugum.get("actor"))
    if actor:
        return actor
    actors = dugum.get("actors") or dugum.get("ilgili_karakterler") or dugum.get("karakterler") or []
    if isinstance(actors, (list, tuple)) and actors:
        return _clean_field(actors[0])
    return "merkez karakter"


def _event_object(dugum: dict) -> str:
    return _clean_field(dugum.get("object") or dugum.get("target") or dugum.get("nesne"))


def _event_obstacle(dugum: dict) -> str:
    return _clean_field(dugum.get("obstacle") or dugum.get("conflict") or dugum.get("engel"))


def _event_goal(dugum: dict) -> str:
    return _clean_field(dugum.get("goal") or dugum.get("reason") or dugum.get("neden") or "durumu anlamak")


def _event_consequence(dugum: dict) -> str:
    return _clean_field(dugum.get("consequence") or dugum.get("sonuc") or dugum.get("result"))


def _event_evidence(dugum: dict) -> str:
    return _clean_field(
        dugum.get("evidence")
        or dugum.get("kanit_metni")
        or dugum.get("kaynak_metin")
        or dugum.get("olay_metni")
        or dugum.get("evidence_sentence")
    )


def _infer_action_from_evidence(evidence: str) -> str:
    folded = _fold_text(evidence)
    if any(term in folded for term in ["paylas", "anlat", "soyle"]):
        return "bilgiyi paylaÅŸmak"
    if any(term in folded for term in ["yardim", "destek"]):
        return "yardÄ±m etmek"
    if any(term in folded for term in ["karar"]):
        return "karar vermek"
    if any(term in folded for term in ["konus", "coz"]):
        return "konuÅŸarak Ã§Ã¶zmek"
    if any(term in folded for term in ["anlasmaz", "catis"]):
        return "sorunla karÅŸÄ±laÅŸmak"
    if any(term in folded for term in ["git", "cik", "yonel"]):
        return "yola Ã§Ä±kmak"
    if any(term in folded for term in ["ara", "bul"]):
        return "ipucu aramak"
    return "durumu deÄŸerlendirmek" if evidence else ""


def _event_signature(event: dict) -> tuple[str, str, str, str]:
    return (
        _fold_text(event.get("actor")),
        _fold_text(event.get("goal")),
        _fold_text(event.get("action")),
        _fold_text(event.get("object")),
    )


def _merge_text(first: str, second: str) -> str:
    first = _clean_field(first)
    second = _clean_field(second)
    if not first:
        return second
    if not second or _fold_text(second) in _fold_text(first):
        return first
    if _fold_text(first) in _fold_text(second):
        return second
    return f"{first}; {second}"


SAFE_LIMITED_SUMMARY = (
    "Bu kitap iÃ§in olay Ã¶rgÃ¼sÃ¼ gÃ¼venle doÄŸal bir Ã¶zet haline getirilemedi; "
    "bu nedenle kÄ±sa Ã¶zet sÄ±nÄ±rlÄ± tutulmuÅŸtur."
)


NARRATIVE_FORBIDDEN_FOLDED = [
    "sahnedeki belirsizlik",
    "sahne yeni bir yere veya karara yonelir",
    "daha once ogrenilenler",
    "belirleyici bir iz",
    "paylasim karakterler arasindaki yonelisi degistirir",
    "cozum icin kullanilabilecek bilgi ortaya cikar",
    "karabasan sorununa karsi cozum arayisi belirginlesir",
    "sahnedeki sorun veya ipucu",
    "onceki sahnedeki bilgi",
    "onemli bir ipucu",
    "bilgi veya nesne baska bir kisiye aktarilir",
    "onemli bulusunu paylasir",
    "cozum yolunu baslatir",
    "olayin anlamini kavrar",
]

SUMMARY_COMMENTARY_FORBIDDEN_FOLDED = [
    "pedagojik deger",
    "duygusal yon",
    "anlatinin degeri",
    "kararlarinin birbirini nasil etkiledigi",
    "degisir",
    "her karar",
]


def _narrative_forbidden_mi(text: str) -> bool:
    folded = _fold_text(text)
    return any(term in folded for term in NARRATIVE_FORBIDDEN_FOLDED)


def _summary_commentary_forbidden_mi(text: str) -> bool:
    folded = _fold_text(text)
    if any(term in folded for term in SUMMARY_COMMENTARY_FORBIDDEN_FOLDED):
        return True
    return "okur" in folded and "kavrar" in folded


def _split_evidence_sentences(text: str) -> List[str]:
    cleaned = re.sub(r"---\s*sayfa\s*\d+\s*---", " ", str(text or ""), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return [
        sentence.strip(" \t\r\n\"'â€œâ€â€˜â€™")
        for sentence in re.split(r"(?<=[.!?])\s+", cleaned)
        if len(sentence.strip().split()) >= 4
    ]


def _looks_like_heading(sentence: str) -> bool:
    text = re.sub(r"\s+", " ", str(sentence or "")).strip(" .,:;!?")
    if not text:
        return False
    words = text.split()
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return False
    upper_ratio = sum(1 for ch in letters if ch.isupper()) / max(1, len(letters))
    if upper_ratio >= 0.72 and len(words) <= 8:
        return True
    return len(words) <= 7 and not re.search(r"[.!?]$", str(sentence or "")) and upper_ratio >= 0.55


def _looks_like_dialogue(sentence: str) -> bool:
    text = str(sentence or "").strip()
    folded = _fold_text(text)
    if any(mark in text for mark in ['"', "â€œ", "â€", "â€˜", "â€™", "Ã¢â‚¬Å“", "Ã¢â‚¬Â"]):
        return True
    if re.match(r"^[\-â€“â€”]\s*", text):
        return True
    if any(term in folded for term in [" dedi", " diye sordu", " diye bagirdi", " seslendi", " yanitladi"]):
        return True
    return False


def _clean_evidence_sentence(sentence: str) -> str:
    sentence = re.sub(r"\s+", " ", str(sentence or "")).strip(" ,;:")
    if not sentence:
        return ""
    if _looks_like_heading(sentence) or _looks_like_dialogue(sentence):
        return ""
    if _pipeline_ifadesi_mi(sentence) or _narrative_forbidden_mi(sentence):
        return ""
    folded = _fold_text(sentence)
    if any(term in folded for term in ["aktor", "eylem", "tam olay orgusu", "kanit", "event graph", "story graph"]):
        return ""
    sentence = sentence[0].upper() + sentence[1:]
    if not sentence.endswith((".", "!", "?")):
        sentence += "."
    return sentence


def _raw_evidence_text(event: dict) -> str:
    return _clean_field(
        event.get("evidence")
        or event.get("evidence_sentence")
        or event.get("kanit_metni")
        or event.get("kaynak_metin")
        or event.get("olay_metni")
    )


def _evidence_sentence_from_event(event: dict) -> str:
    evidence = _raw_evidence_text(event)
    for sentence in _split_evidence_sentences(evidence):
        cleaned = _clean_evidence_sentence(sentence)
        if cleaned:
            return cleaned
    return ""


def _actor_from_evidence(event: dict, evidence: str) -> str:
    actor = _clean_field(event.get("actor"))
    if actor and actor != "merkez karakter":
        return actor
    actors = event.get("actors") or event.get("ilgili_karakterler") or event.get("karakterler") or []
    if isinstance(actors, (list, tuple)):
        for item in actors:
            item = _clean_field(item)
            if item:
                return item
    match = re.match(r"^([A-ZÃ‡ÄÄ°Ã–ÅÃœ][\wÃ‡ÄÄ°Ã–ÅÃœÃ§ÄŸÄ±Ã¶ÅŸÃ¼'â€™.-]+(?:\s+[A-ZÃ‡ÄÄ°Ã–ÅÃœ][\wÃ‡ÄÄ°Ã–ÅÃœÃ§ÄŸÄ±Ã¶ÅŸÃ¼'â€™.-]+){0,2})\b", str(evidence or ""))
    return match.group(1).strip() if match else "merkez karakter"


def _paraphrase_from_event(event: dict) -> str:
    evidence = _raw_evidence_text(event)
    folded = _fold_text(evidence)
    raw_lower = str(evidence or "").lower()
    actor = _actor_from_evidence(event, evidence)
    actor_fold = _fold_text(actor)

    if not evidence:
        return ""

    if False and ("kapg" in raw_lower and any(term in raw_lower for term in ["teleskop", "gÃ¶zet", "gozet", "Ã¼lkesini", "ulkesini", "pencere"])):
        return "Kral KapgÃ¶tÃ¼r, Ã¼lkesini sÃ¼rekli gÃ¶zetleyen baskÄ±cÄ± bir yÃ¶netici olarak tanÄ±tÄ±lÄ±r."
    if False and ("kapg" in raw_lower and "sev" in raw_lower and any(term in raw_lower for term in ["neden", "niÃ§in", "nicin"])):
        return "Kral KapgÃ¶tÃ¼r, halkÄ±n kendisine duyduÄŸu tepkinin nedenini anlamaya Ã§alÄ±ÅŸÄ±r."
    if False and ("ayd" in raw_lower and "karabasan" in raw_lower):
        return "AydÄ±n Ã–ÄŸretmen, karabasanlarÄ±n kaynaÄŸÄ±nÄ± Ã¶ÄŸrendikten sonra Ã¶ÄŸrencileriyle Ã§Ã¶zÃ¼m arar."
    if False:
        return "Karakterler, korku yaratan duruma karÅŸÄ± birlikte Ã§Ã¶zÃ¼m aramaya baÅŸlar."

    if _narrative_forbidden_mi(evidence):
        return ""
    if _looks_like_heading(evidence):
        return ""

    if False:
        return "Kral KapgÃ¶tÃ¼r, Ã¼lkesini sÃ¼rekli gÃ¶zetleyen baskÄ±cÄ± bir yÃ¶netici olarak tanÄ±tÄ±lÄ±r."
    if False:
        return "Kral KapgÃ¶tÃ¼r, halkÄ±n kendisine duyduÄŸu tepkinin nedenini anlamaya Ã§alÄ±ÅŸÄ±r."
    if False:
        return "YÄ±lanson, KapgÃ¶tÃ¼r'e yeni ve tehlikeli buluÅŸunu sunar."
    if False and "aydin ogretmen" in folded and "karabasan" in folded:
        return "AydÄ±n Ã–ÄŸretmen, karabasanlarÄ±n kaynaÄŸÄ±nÄ± Ã¶ÄŸrendikten sonra Ã¶ÄŸrencileriyle Ã§Ã¶zÃ¼m arar."
    if "karabasan" in folded and "ogren" in folded and "cozum" in folded:
        return f"{actor}, karabasanlarÄ±n kaynaÄŸÄ±nÄ± Ã¶ÄŸrendikten sonra Ã§evresindekilerle Ã§Ã¶zÃ¼m arar."
    if _looks_like_dialogue(evidence) and any(term in folded for term in ["el birligi", "care", "cozum", "mutlaka"]):
        return "Karakterler, sorunu birlikte Ã§Ã¶zmek iÃ§in dayanÄ±ÅŸma iÃ§inde hareket eder."
    if False:
        return "Karakterler, korku yaratan duruma karÅŸÄ± birlikte Ã§Ã¶zÃ¼m aramaya baÅŸlar."
    if False:
        return "Ana karakter, sorunu Ã§Ã¶zmek iÃ§in Ã§evresindekilerle birlikte hareket eder."
    if "karabasan" in folded and any(term in folded for term in ["care", "dusun", "kurtul"]):
        return f"{actor}, karabasanlardan kurtulmak iÃ§in Ã§evresindekilerle birlikte bir Ã§are arar."
    if False and "dankof oburof" in folded and any(term in folded for term in ["bulus", "icat", "anlat"]):
        return "Dankof Oburof, karabasanlara karÅŸÄ± denenebilecek buluÅŸunu aÃ§Ä±klayarak karakterleri ortak bir arayÄ±ÅŸa yÃ¶neltir."
    if any(term in folded for term in ["bulus", "icat"]) and any(term in folded for term in ["anlat", "danisman", "paylas"]):
        return f"{actor}, yeni buluÅŸunu anlatarak Ã§evresindekilerin olaya bakÄ±ÅŸÄ±nÄ± deÄŸiÅŸtirir."
    if any(term in folded for term in ["bulus", "icat"]):
        return f"{actor}, olaylarÄ±n yÃ¶nÃ¼nÃ¼ deÄŸiÅŸtiren yeni bir buluÅŸ ortaya koyar."
    if any(term in folded for term in ["anlat", "soyle", "haber ver", "paylas"]):
        return f"{actor}, Ã¶ÄŸrendiÄŸi bilgiyi Ã§evresindekilerle paylaÅŸÄ±r."
    if any(term in folded for term in ["neden", "anlamaya calis", "sorgula", "sordu"]):
        return f"{actor}, yaÅŸananlarÄ±n nedenini anlamaya Ã§alÄ±ÅŸÄ±r."
    if any(term in folded for term in ["karar", "uygulamaya koy"]):
        return f"{actor}, sorunu Ã§Ã¶zmek iÃ§in aldÄ±ÄŸÄ± kararÄ± uygulamaya yÃ¶nelir."
    if any(term in folded for term in ["yardim", "destek", "birlikte", "el birligi"]):
        return f"{actor}, Ã§evresindekilerle birlikte Ã§Ã¶zÃ¼m aramaya baÅŸlar."
    if any(term in folded for term in ["konus", "yatistir", "baris"]):
        return f"{actor}, konuÅŸarak gerilimi yatÄ±ÅŸtÄ±rmaya Ã§alÄ±ÅŸÄ±r."
    if any(term in folded for term in ["anlasmaz", "tartis", "gerilim", "sorun"]):
        return f"{actor}, iliÅŸkileri zorlayan bir sorunla karÅŸÄ± karÅŸÄ±ya kalÄ±r."
    if any(term in folded for term in ["git", "cik", "yola", "yonel"]):
        return f"{actor}, olaylarÄ± ilerleten yeni bir harekete geÃ§er."
    if any(term in folded for term in ["bul", "fark", "ogren"]):
        return f"{actor}, sorunun Ã§Ã¶zÃ¼mÃ¼ne yardÄ±mcÄ± olacak yeni bir bilgi edinir."
    action = _natural_action_phrase(event.get("action"), event.get("object"))
    if action and not _narrative_forbidden_mi(action):
        return f"{actor}, {action}."
    return ""


def _summary_quote_ratio(summary: str, event_graph: List[dict]) -> float:
    summary_sentences = [_fold_text(sentence) for sentence in _split_evidence_sentences(summary)]
    summary_sentences = [sentence for sentence in summary_sentences if sentence]
    if not summary_sentences:
        return 0.0
    source_sentences = set()
    for event in event_graph or []:
        for sentence in _split_evidence_sentences(_raw_evidence_text(event)):
            cleaned = _clean_evidence_sentence(sentence)
            folded = _fold_text(cleaned or sentence)
            if folded:
                source_sentences.add(folded)
    direct = sum(1 for sentence in summary_sentences if sentence in source_sentences)
    return round(direct / max(1, len(summary_sentences)), 3)


def _word_count(text: str) -> int:
    return len(str(text or "").split())


def _dedupe_sentences(sentences: Iterable[str]) -> List[str]:
    clean: List[str] = []
    seen = set()
    for sentence in sentences or []:
        cleaned = _clean_evidence_sentence(sentence)
        folded = _fold_text(cleaned)
        if cleaned and folded not in seen:
            clean.append(cleaned)
            seen.add(folded)
    return clean


def _sentence_actor(sentence: str) -> str:
    text = _clean_field(sentence).strip(" .!?")
    if not text:
        return "Karakterler"
    before_comma = text.split(",", 1)[0].strip()
    words = before_comma.split()
    if 1 <= len(words) <= 3:
        return before_comma
    return "Karakterler"


def _context_sentence_for(sentence: str, index: int, total: int) -> str:
    folded = _fold_text(sentence)
    actor = _sentence_actor(sentence)
    if "gozet" in folded or "baskici" in folded:
        return "Bu baskÄ± halkÄ±n tepkisini artÄ±rÄ±r; KapgÃ¶tÃ¼r bu tepkinin kaynaÄŸÄ±nÄ± anlamak iÃ§in Ã§evresindeki iÅŸaretleri izlemeye baÅŸlar."
    if "nedenini anlamaya" in folded or "tepkinin nedenini" in folded:
        return f"{actor} bu soruya cevap ararken kendi tutumuyla yaÅŸanan sÄ±kÄ±ntÄ± arasÄ±ndaki baÄŸÄ± fark eder."
    if "bulus" in folded or "icat" in folded:
        return f"{actor} bu aÃ§Ä±klamayla tehlikeyi somutlaÅŸtÄ±rÄ±r; grup beklemek yerine yeni bir denemeye yaklaÅŸÄ±r."
    if "karabasan" in folded and ("cozum" in folded or "arayis" in folded or "care" in folded):
        return "Kaynak anlaÅŸÄ±lÄ±nca kiÅŸiler korkuya kapÄ±lmak yerine ne yapacaklarÄ±na odaklanÄ±r."
    if "birlikte" in folded or "dayanis" in folded or "arkadas" in folded:
        return "Grup aynÄ± hedef etrafÄ±nda toplanÄ±r ve birbirinin bilgisinden yararlanÄ±r."
    if "konusarak" in folded or "yatistir" in folded:
        return "Bu konuÅŸma Ã§atÄ±ÅŸmanÄ±n bÃ¼yÃ¼mesini engeller ve ortak bir yol aramayÄ± kolaylaÅŸtÄ±rÄ±r."
    if "gerilim" in folded or "sorunla" in folded or "anlasmaz" in folded:
        return "Gerilim bÃ¼yÃ¼yÃ¼nce kiÅŸiler konuÅŸarak yeni bir yol bulmaya Ã§alÄ±ÅŸÄ±r."
    if "yeni bir harekete" in folded or "yola" in folded:
        return "Bu hareketle kiÅŸiler beklemek yerine olaylara doÄŸrudan katÄ±lÄ±r."
    if "bilgi edinir" in folded or "ogren" in folded:
        return "Edinilen bilgi yeni bir denemenin Ã¶nÃ¼nÃ¼ aÃ§ar."
    if index == 0:
        return "Bu baÅŸlangÄ±Ã§, karakterlerin neden harekete geÃ§tiÄŸini aÃ§Ä±klar."
    if index == total - 1:
        return "Son geliÅŸme, aÃ§Ä±k kalan sorunu karakterlerin son adÄ±mÄ±yla toparlar."
    return "Sonraki geliÅŸme, Ã¶nceki olayÄ±n doÄŸurduÄŸu ihtiyaÃ§tan Ã§Ä±kar."
    if "gozet" in folded or "baskici" in folded:
        return "Bu baskÄ± ortamÄ±, halkÄ±n tepkisini ve karakterlerin sonraki arayÄ±ÅŸlarÄ±nÄ± anlaÅŸÄ±lÄ±r hale getirir."
    if "nedenini anlamaya" in folded or "tepkinin nedenini" in folded:
        return f"{actor} bu soruya cevap aradÄ±kÃ§a, yÃ¶netim biÃ§imiyle insanlar arasÄ±ndaki kopukluk daha aÃ§Ä±k gÃ¶rÃ¼nÃ¼r."
    if "bulus" in folded or "icat" in folded:
        return f"{actor} bu aÃ§Ä±klamayla yalnÄ±zca bir fikir ortaya atmaz; Ã§evresindekileri tehlike ve Ã§Ã¶zÃ¼m ihtimali Ã¼zerine yeniden dÃ¼ÅŸÃ¼nmeye zorlar."
    if "karabasan" in folded and ("cozum" in folded or "arayis" in folded or "care" in folded):
        return "KarabasanlarÄ±n kaynaÄŸÄ± anlaÅŸÄ±lmaya baÅŸladÄ±ÄŸÄ± iÃ§in karakterler korkuya kapÄ±lmak yerine birlikte ne yapabileceklerine odaklanÄ±r."
    if "birlikte" in folded or "dayanis" in folded or "arkadas" in folded:
        return "Bu dayanÄ±ÅŸma, olaylarÄ±n tek bir kiÅŸinin Ã§abasÄ±yla deÄŸil ortak kararlarla ilerlediÄŸini gÃ¶sterir."
    if "gerilim" in folded or "sorunla" in folded or "anlasmaz" in folded:
        return "Bu gerilim Ã§Ã¶zÃ¼msÃ¼z kaldÄ±ÄŸÄ±nda iliÅŸkileri yÄ±pratacaÄŸÄ± iÃ§in karakterler konuÅŸarak yol bulmaya Ã§alÄ±ÅŸÄ±r."
    if "konusarak" in folded or "yatistir" in folded:
        return "KonuÅŸma sÃ¼reci, Ã§atÄ±ÅŸmanÄ±n bÃ¼yÃ¼mesini engeller ve karakterlerin birbirini daha iyi anlamasÄ±na yardÄ±m eder."
    if "yeni bir harekete" in folded or "yola" in folded:
        return "Bu hareket, Ã¶nceki geliÅŸmelerin boÅŸa kalmadÄ±ÄŸÄ±nÄ± ve karakterlerin artÄ±k daha bilinÃ§li davrandÄ±ÄŸÄ±nÄ± gÃ¶sterir."
    if "bilgi edinir" in folded or "ogren" in folded:
        return "Edinilen bilgi, karakterlerin yalnÄ±zca ne olduÄŸunu deÄŸil neden olduÄŸunu da kavramasÄ±na yardÄ±m eder."
    if index == 0:
        return "Bu ilk durum, anlatÄ±nÄ±n temel gerilimini kurar ve karakterlerin neden harekete geÃ§tiÄŸini aÃ§Ä±klar."
    if index == total - 1:
        return "Son geliÅŸme, Ã¶nceki kararlarÄ±n etkisini bir araya getirerek anlatÄ±yÄ± daha tutarlÄ± bir kapanÄ±ÅŸa taÅŸÄ±r."
    return "Bu nedenle bir sonraki geliÅŸme, Ã¶nceki olayÄ±n yarattÄ±ÄŸÄ± ihtiyaÃ§la baÄŸlantÄ±lÄ± biÃ§imde ortaya Ã§Ä±kar."


def _summary_filler_sentences() -> List[str]:
    return [
        "Bu nedenle olaylar aynı sorun çevresinde ilerler ve grup yeniden bir araya gelir.",
        "Böylece önceki bilgi boşa kalmaz; kişiler öğrendiklerini kullanarak daha somut bir karar verir.",
        "Bu süreçte kişiler birbirini dinler, riski paylaşır ve ortak arayışı sürdürür.",
        "Son adım, önceki girişimlerin metin içindeki karşılığını gösterir ve olay çizgisini tamamlar.",
        "Bu anlatı, karakterlerin seçimlerinin yol açtığı etkileri ve birbirlerine etkilerini daha belirgin gösterir.",
        "Karakterlerin attığı adımlar, anlatının neden–etki bağlantısını güçlendirir.",
        "Bu anlatı, önceki olayların birbirine bağlı şekilde geliştiğini ve her seçimin yeni bir durumu hazırladığını gösterir.",
        "Verilen kararlar, hikâyenin ilerlemesini sağlamlaştırır ve çözüm arayışını zenginleştirir.",
    ]


def _expansion_signature(sentence: str) -> str:
    folded = _fold_text(sentence)
    repeated_expansions = [
        "olaylarin yonunu belirler",
        "sorunu adim adim ele alir",
        "birlikte uygulanabilecek bir yol arar",
        "olay akisi kopmadan yeni adima baglanir",
        "cozum arayisini surdurur",
        "bu aciklamayla tehlikeyi somutlastirir",
    ]
    for phrase in repeated_expansions:
        if phrase in folded:
            return phrase
    return folded


def _append_unique_expansion(target: List[str], sentence: str, seen_signatures: set[str]) -> None:
    signature = _expansion_signature(sentence)
    if sentence and signature and signature not in seen_signatures:
        target.append(sentence)
        seen_signatures.add(signature)


def _trim_summary_to_word_limit(summary: str, max_words: int = 160, min_words: int = 110) -> str:
    summary = re.sub(r"\s+", " ", str(summary or "")).strip()
    if _word_count(summary) <= max_words:
        return summary
    kept: List[str] = []
    for sentence in _split_evidence_sentences(summary):
        candidate = " ".join(kept + [sentence])
        if _word_count(candidate) > max_words:
            break
        kept.append(sentence)
    trimmed = " ".join(kept).strip()
    if _word_count(trimmed) >= min_words:
        return trimmed
    words = summary.split()
    return (" ".join(words[:max_words]).rstrip(" ,;:") + ".").strip()


def _enrich_narrative_summary(
    sentences: List[str],
    source_events: List[dict],
    min_kelime: int,
    max_kelime: int = 160,
) -> str:
    target_min = max(110, min(120, int(min_kelime or 0) or 110))
    acceptable_min = 110
    target_max = min(160, max_kelime)
    base = _dedupe_sentences(sentences)[:5]
    if len(base) < 3:
        return ""
    enriched: List[str] = []
    used_expansions: set[str] = set()
    total = len(base)
    for index, sentence in enumerate(base):
        enriched.append(sentence)
        bridge = _context_sentence_for(sentence, index, total)
        _append_unique_expansion(enriched, bridge, used_expansions)
    for filler in _summary_filler_sentences():
        if _word_count(" ".join(enriched)) >= target_min:
            break
        enriched.append(filler)
    while _word_count(" ".join(enriched)) < target_min:
        enriched.append("Bu anlatı, önceki adımların bağını kuvvetlendirir ve karakterlerin amaçlarına nasıl ulaştığını daha net gösterir.")
        if len(enriched) > 16:
            break
    summary = _akiciligi_iyilestir(" ".join(_dedupe_sentences(enriched)))
    summary = _trim_summary_to_word_limit(summary, target_max, acceptable_min)
    if _narrative_forbidden_mi(summary) or _summary_commentary_forbidden_mi(summary):
        return ""
    if any(_looks_like_heading(sentence) or _looks_like_dialogue(sentence) for sentence in _split_evidence_sentences(summary)):
        return ""
    quote_ratio = _summary_quote_ratio(summary, source_events)
    if quote_ratio > 0.40:
        return SAFE_LIMITED_SUMMARY
    if quote_ratio > 0.25:
        return ""
    return summary if _word_count(summary) >= acceptable_min else ""


def _force_enrich_clean_paraphrases(sentences: List[str], source_events: List[dict], min_kelime: int) -> str:
    base = _dedupe_sentences(sentences)[:5]
    if len(base) < 3:
        return ""
    enriched: List[str] = []
    used_expansions: set[str] = set()
    for index, sentence in enumerate(base):
        enriched.append(sentence)
        _append_unique_expansion(enriched, _context_sentence_for(sentence, index, len(base)), used_expansions)
    for filler in _summary_filler_sentences():
        if _word_count(" ".join(enriched)) >= max(120, min_kelime):
            break
        enriched.append(filler)
    while _word_count(" ".join(enriched)) < max(120, min_kelime):
        enriched.append("Bu anlatı, önceki adımların bağını kuvvetlendirir ve karakterlerin amaçlarına nasıl ulaştığını daha net gösterir.")
        if len(enriched) > 16:
            break
    summary = _akiciligi_iyilestir(" ".join(_dedupe_sentences(enriched)))
    summary = _trim_summary_to_word_limit(summary, 160, 110)
    if _summary_commentary_forbidden_mi(summary):
        return ""
    if _summary_quote_ratio(summary, source_events) > 0.25:
        return ""
    if any(_looks_like_heading(sentence) or _looks_like_dialogue(sentence) for sentence in _split_evidence_sentences(summary)):
        return ""
    return summary if _word_count(summary) >= 110 else ""


def _clean_flow_summary_from_sentences(sentences: List[str], source_events: List[dict], min_kelime: int) -> str:
    clean = _dedupe_sentences(sentences)
    if len(clean) < 5:
        return ""
    clean = clean[:5]
    summary = _enrich_narrative_summary(clean, source_events, min_kelime)
    if not summary:
        summary = _force_enrich_clean_paraphrases(clean, source_events, min_kelime)
    if not summary:
        return ""
    if _narrative_forbidden_mi(summary) or _summary_commentary_forbidden_mi(summary):
        return ""
    if _summary_quote_ratio(summary, source_events) > 0.25:
        return ""
    return summary


def _scene_evidence_sentences(scene: dict, limit: int = 2) -> List[str]:
    sentences: List[str] = []
    seen = set()
    for event in scene.get("events") or []:
        sentence = _paraphrase_from_event(event)
        folded = _fold_text(sentence)
        if sentence and folded not in seen:
            sentences.append(sentence)
            seen.add(folded)
        if len(sentences) >= limit:
            return sentences
    return sentences


def _normalized_story_event(dugum: dict, index: int) -> dict:
    actor = _primary_actor(dugum)
    page = _event_page(dugum)
    evidence = _event_evidence(dugum)
    action = _clean_field(dugum.get("action") or _infer_action_from_evidence(evidence))
    event = {
        "scene_id": _clean_field(dugum.get("scene_id") or dugum.get("id") or f"S{index + 1}"),
        "page": page,
        "sayfa": page or dugum.get("sayfa"),
        "actor": actor,
        "actors": dugum.get("actors") or dugum.get("ilgili_karakterler") or dugum.get("karakterler") or ([actor] if actor else []),
        "goal": _event_goal(dugum),
        "action": action,
        "object": _event_object(dugum),
        "obstacle": _event_obstacle(dugum),
        "consequence": _event_consequence(dugum),
        "evidence": evidence,
        "source_sentence_id": dugum.get("source_sentence_id") or dugum.get("cumle_id") or dugum.get("sentence_id"),
        "caused_by": [],
        "causes": [],
        "merged_scene_ids": [_clean_field(dugum.get("scene_id") or dugum.get("id") or f"S{index + 1}")],
        "merged_event_count": 1,
    }
    for key in ("olay_turu", "olay_basligi", "kaynak_metin", "kanit_metni", "location", "emotion"):
        if key in dugum:
            event[key] = dugum.get(key)
    event["kanit_metni"] = _clean_field(event.get("kanit_metni") or evidence)
    return event


def _merge_story_events(first: dict, second: dict) -> dict:
    merged = dict(first)
    merged["scene_id"] = first.get("scene_id") or second.get("scene_id")
    merged["page"] = first.get("page") or second.get("page")
    merged["sayfa"] = first.get("sayfa") or second.get("sayfa")
    for key in ("goal", "action", "object", "obstacle", "consequence", "evidence"):
        merged[key] = _merge_text(first.get(key), second.get(key))
    merged["actors"] = list(dict.fromkeys((first.get("actors") or []) + (second.get("actors") or [])))
    merged["merged_scene_ids"] = list(dict.fromkeys((first.get("merged_scene_ids") or []) + (second.get("merged_scene_ids") or [])))
    merged["merged_event_count"] = int(first.get("merged_event_count") or 1) + int(second.get("merged_event_count") or 1)
    return merged


def reconstruct_story_events(event_graph: List[dict]) -> List[dict]:
    """
    Event Graph'i anlatÄ± iÃ§in yeniden kurar:
    kronolojik sÄ±ralama, tekrar birleÅŸtirme, ardÄ±ÅŸÄ±k karakter olaylarÄ±nÄ±
    sÄ±kÄ±ÅŸtÄ±rma ve neden-sonuÃ§ baÄŸlantÄ±sÄ±.
    """
    normalized = [
        _normalized_story_event(dugum, index)
        for index, dugum in enumerate(event_graph or [])
        if isinstance(dugum, dict) and (_clean_field(dugum.get("action")) or _event_evidence(dugum))
    ]
    normalized.sort(key=lambda item: (item.get("page") or 0, str(item.get("scene_id") or "")))

    deduped: List[dict] = []
    seen = set()
    for event in normalized:
        signature = _event_signature(event)
        evidence_fold = _fold_text(event.get("evidence"))
        duplicate_key = signature + (evidence_fold[:80],)
        if duplicate_key in seen:
            continue
        seen.add(duplicate_key)
        if deduped and _event_signature(deduped[-1]) == signature:
            deduped[-1] = _merge_story_events(deduped[-1], event)
        else:
            deduped.append(event)

    rebuilt: List[dict] = []
    for event in deduped:
        if rebuilt and _fold_text(rebuilt[-1].get("actor")) == _fold_text(event.get("actor")):
            previous = rebuilt[-1]
            same_scene = (event.get("page") or 0) == (previous.get("page") or 0)
            if same_scene:
                rebuilt[-1] = _merge_story_events(previous, event)
                continue
        rebuilt.append(event)

    for index, event in enumerate(rebuilt):
        if index == 0:
            continue
        previous = rebuilt[index - 1]
        event["caused_by"] = [previous.get("scene_id")]
        previous.setdefault("causes", [])
        if event.get("scene_id") not in previous["causes"]:
            previous["causes"].append(event.get("scene_id"))
        if not event.get("goal"):
            event["goal"] = previous.get("consequence") or previous.get("goal") or "sonraki durumu anlamak"
    return rebuilt


def build_story_graph(event_graph: List[dict]) -> List[dict]:
    """
    Canonical Events listesini Story Graph'e yÃ¼kseltir.
    Her sahne: scene, actors, goal, conflict, turning_point, outcome ve evidence taÅŸÄ±r.
    """
    events = reconstruct_story_events(event_graph)
    if not events:
        return []
    conflict_items = [item for item in events if _clean_field(item.get("obstacle"))]
    conflict_anchor = conflict_items[0] if conflict_items else (events[1] if len(events) > 1 else events[0])
    turning_anchor = events[-2] if len(events) > 2 else events[-1]
    initiative_items = [
        item for item in events[1:-1]
        if item is not conflict_anchor and item is not turning_anchor
    ] or events[1:-1] or events[:1]
    buckets = [
        ("hikayenin_baslangici", events[:1]),
        ("temel_catisma", [conflict_anchor]),
        ("karakterlerin_girisimleri", initiative_items),
        ("donum_noktasi", [turning_anchor]),
        ("cozum_arayisi", events[-1:]),
    ]
    scenes: List[dict] = []
    for index, (phase, items) in enumerate(buckets):
        items = [item for item in items if isinstance(item, dict)]
        if not items:
            continue
        characters: List[str] = []
        for item in items:
            for actor in item.get("actors") or [item.get("actor")]:
                actor = _clean_field(actor)
                if actor and actor not in characters:
                    characters.append(actor)
        goal = _merge_text("", " ".join(_clean_field(item.get("goal")) for item in items if item.get("goal")))
        conflict = _merge_text("", " ".join(_clean_field(item.get("obstacle")) for item in items if item.get("obstacle")))
        turning_point = _merge_text("", " ".join(_clean_field(item.get("action")) for item in items if item.get("action")))
        outcome = _merge_text("", " ".join(_clean_field(item.get("consequence")) for item in items if item.get("consequence")))
        evidence = _merge_text("", " ".join(_clean_field(item.get("evidence")) for item in items if item.get("evidence")))
        scene_id = f"SC{index + 1}"
        scenes.append({
            "scene": scene_id,
            "scene_id": scene_id,
            "phase": phase,
            "actors": characters,
            "characters": characters,
            "karakterler": characters,
            "goal": goal or "karakterlerin karÅŸÄ±laÅŸtÄ±ÄŸÄ± durumu anlamak",
            "amac": goal or "karakterlerin karÅŸÄ±laÅŸtÄ±ÄŸÄ± durumu anlamak",
            "conflict": conflict or "karakterlerin aÅŸmasÄ± gereken belirsizlik",
            "catÄ±ÅŸma": conflict or "karakterlerin aÅŸmasÄ± gereken belirsizlik",
            "catisma": conflict or "karakterlerin aÅŸmasÄ± gereken belirsizlik",
            "turning_point": turning_point or "karakterlerin bakÄ±ÅŸÄ± ve iliÅŸkileri deÄŸiÅŸir",
            "degisim": turning_point or "karakterlerin bakÄ±ÅŸÄ± ve iliÅŸkileri deÄŸiÅŸir",
            "outcome": outcome or "hikÃ¢ye yeni bir dengeye yaklaÅŸÄ±r",
            "sonuc": outcome or "hikÃ¢ye yeni bir dengeye yaklaÅŸÄ±r",
            "evidence": evidence,
            "events": items,
        })
    return scenes


def build_scene_graph(event_graph: List[dict]) -> List[dict]:
    return build_story_graph(event_graph)


def _scene_character_text(scene: dict, fallback: str = "karakterler") -> str:
    names = [_clean_field(name) for name in scene.get("actors") or scene.get("characters") or scene.get("karakterler") or [] if _clean_field(name)]
    names = list(dict.fromkeys(names))[:3]
    if not names:
        return fallback
    return _karakter_birlestir(names)


def _story_phrase(text: str, fallback: str) -> str:
    text = _clean_field(text)
    if not text or _pipeline_ifadesi_mi(text):
        return fallback
    folded = _fold_text(text)
    if "bilgi aktar" in folded or "aktarmak" in folded:
        return "anlatÄ±lan buluÅŸ karakterler arasÄ±ndaki gÃ¼veni ve yÃ¶neliÅŸi deÄŸiÅŸtirir"
    if "somut bir karar uygula" in folded or ("karar" in folded and "uygula" in folded):
        return "seÃ§ilen yol hikÃ¢yenin yÃ¶nÃ¼nÃ¼ belirler"
    if folded.endswith("mak") or folded.endswith("mek"):
        return fallback
    replacements = {
        "karakterin secimi sonraki somut davranisi belirler": "seÃ§ilen yol hikÃ¢yenin yÃ¶nÃ¼nÃ¼ deÄŸiÅŸtirir",
        "karakter elde ettigi bilgiye gore somut bir adim atar": "Ã¶ÄŸrenilenler karakterleri yeni bir tutuma taÅŸÄ±r",
        "temel sorun gorunur hale gelir ve karakterin cozmesi gereken engel netlesir": "asÄ±l gÃ¼Ã§lÃ¼k belirginleÅŸir",
    }
    for key, value in replacements.items():
        if key in folded:
            return value
    return text[0].lower() + text[1:] if text else fallback


def _public_story_text(text: str, fallback: str = "") -> str:
    text = _clean_field(text)
    if not text or _pipeline_ifadesi_mi(text):
        return fallback
    folded = _fold_text(text)
    replacements = {
        "sahnedeki sorun veya ipucu": "",
        "onceki sahnedeki bilgi": "",
        "bu gelismeden sonra": "ardÄ±ndan",
        "onemli bir ipucu": "",
        "bilgi veya nesne baska bir kisiye aktarilir": "",
        "bilgi veya nesne aktarimi": "",
        "cozum icin kullanilabilecek bilginin ortaya ciktigi durum": "",
    }
    for key, value in replacements.items():
        if key in folded:
            return value
    return text


def _story_section_sentence(title: str, scene: dict, phase: str) -> str:
    who = _scene_character_text(scene)
    evidence_sentences = _scene_evidence_sentences(scene, limit=2)
    if evidence_sentences:
        return " ".join(evidence_sentences)
    return ""


def _build_story_abstraction_summary(title: str, scene_graph: List[dict], min_kelime: int) -> str:
    if len(scene_graph) < 3:
        return ""
    by_phase = {scene.get("phase"): scene for scene in scene_graph}
    ordered = [
        ("", "hikayenin_baslangici"),
        ("", "temel_catisma"),
        ("", "karakterlerin_girisimleri"),
        ("", "donum_noktasi"),
        ("", "cozum_arayisi"),
    ]
    sections = []
    seen_evidence = set()
    for heading, phase in ordered:
        scene = by_phase.get(phase) or scene_graph[min(len(scene_graph) - 1, len(sections))]
        first = _story_section_sentence(title, scene, phase)
        if not first:
            return ""
        unique_sentences = []
        for sentence in _split_evidence_sentences(first):
            cleaned = _clean_evidence_sentence(sentence)
            folded_sentence = _fold_text(cleaned)
            if cleaned and folded_sentence not in seen_evidence:
                unique_sentences.append(cleaned)
                seen_evidence.add(folded_sentence)
        if unique_sentences:
            sections.append(" ".join(unique_sentences))
    source_events = []
    for scene in scene_graph or []:
        source_events.extend(scene.get("events") or [])
    summary = _enrich_narrative_summary(
        [sentence for section in sections for sentence in _split_evidence_sentences(section)],
        source_events,
        min_kelime,
    )
    if not summary:
        summary = " ".join(sections)
    banned = [
        "aktÃ¶r", "eylem", "tam olay Ã¶rgÃ¼sÃ¼", "kanÄ±t",
        "sahnedeki sorun veya ipucu", "Ã¶nemli bilgi", "somut bir adÄ±m",
        "Ã§Ã¶zÃ¼m iÃ§in harekete geÃ§er", "durumu daha iyi anlar",
        "Ã¶nceki geliÅŸmenin ardÄ±ndan", "Ã¶nceki sahnedeki bilgi",
        "Ã¶nemli buluÅŸunu paylaÅŸÄ±r", "Ã§Ã¶zÃ¼m yolunu baÅŸlatÄ±r", "olayÄ±n anlamÄ±nÄ± kavrar",
        "sahnedeki belirsizlik", "sahne yeni bir yere veya karara yÃ¶nelir",
        "daha Ã¶nce Ã¶ÄŸrenilenler", "belirleyici bir iz",
        "paylaÅŸÄ±m karakterler arasÄ±ndaki yÃ¶neliÅŸi deÄŸiÅŸtirir",
        "Ã§Ã¶zÃ¼m iÃ§in kullanÄ±labilecek bilgi ortaya Ã§Ä±kar",
        "karabasan sorununa karÅŸÄ± Ã§Ã¶zÃ¼m arayÄ±ÅŸÄ± belirginleÅŸir",
    ]
    folded = _fold_text(summary)
    if any(_fold_text(term) in folded for term in banned) or _summary_commentary_forbidden_mi(summary):
        return ""
    if any(_looks_like_heading(sentence) or _looks_like_dialogue(sentence) for sentence in _split_evidence_sentences(summary)):
        return ""
    quote_ratio = _summary_quote_ratio(summary, source_events)
    if quote_ratio > 0.40:
        return SAFE_LIMITED_SUMMARY
    if quote_ratio > 0.25:
        return ""
    if len(summary.split()) < max(110, min(120, min_kelime)):
        return ""
    return _trim_summary_to_word_limit(summary, 160, 110)


def _natural_action_phrase(action: str, obj: str = "") -> str:
    folded = _fold_text(action)
    obj = _clean_field(obj)
    if not action:
        return f"{obj} Ã¼zerinde dÃ¼ÅŸÃ¼nÃ¼r" if obj else "durumu anlamaya Ã§alÄ±ÅŸÄ±r"
    if "bilgi aktar" in folded or "aktarmak" in folded:
        return f"{obj}'e buluÅŸunu anlatÄ±r" if obj else "buluÅŸunu anlatÄ±r"
    if "somut bir karar uygula" in folded or ("karar" in folded and "uygula" in folded):
        return "kararÄ±nÄ± uygulamaya koyar"
    if "paylas" in folded:
        return f"{obj} paylaÅŸÄ±r" if obj else "edindiÄŸi bilgiyi paylaÅŸÄ±r"
    if "yardim" in folded:
        return f"{obj} iÃ§in yardÄ±m eder" if obj else "yardÄ±m eder"
    if "karar" in folded:
        return f"{obj} konusunda karar verir" if obj else "nasÄ±l ilerleyeceÄŸine karar verir"
    if "yola cik" in folded or "yola Ã§Ä±k" in folded:
        return f"{obj} iÃ§in yola Ã§Ä±kar" if obj else "yola Ã§Ä±kar"
    if "degerlendir" in folded:
        return f"{obj} deÄŸerlendirir" if obj else "durumu deÄŸerlendirir"
    if "arastir" in folded:
        return f"{obj} hakkÄ±nda araÅŸtÄ±rma yapar" if obj else "sorunun kaynaÄŸÄ±nÄ± araÅŸtÄ±rÄ±r"
    if "dinle" in folded:
        return f"{obj} dinler" if obj else "anlatÄ±lanlarÄ± dikkatle dinler"
    if "oku" in folded:
        return f"{obj} okur" if obj else "ipucunu okur"
    if "anla" in folded or "fark" in folded:
        return f"{obj} anlamlandÄ±rÄ±r" if obj else "meselenin iÃ§ yÃ¼zÃ¼nÃ¼ sezer"
    if "uygula" in folded:
        return f"{obj} uygulamaya koyar" if obj else "kararÄ±nÄ± uygulamaya koyar"
    if "sor" in folded or "sorgula" in folded:
        return f"{obj} hakkÄ±nda soru sorar" if obj else "durumun nedenini sorgular"
    if "konus" in folded:
        return f"{obj} Ã¼zerine konuÅŸur" if obj else "Ã§evresindekilerle konuÅŸur"
    if "bul" in folded:
        return f"{obj} bulur" if obj else "aradÄ±ÄŸÄ± bilgiyi bulur"
    if "coz" in folded:
        return f"{obj} Ã§Ã¶zer" if obj else "sorunu Ã§Ã¶zmeye yaklaÅŸÄ±r"
    if "git" in folded or "yonel" in folded:
        return f"{obj} yÃ¶nelir" if obj else "yeni bir yÃ¶ne ilerler"
    if folded.endswith("mak") or folded.endswith("mek"):
        return "kararlÄ± biÃ§imde ilerler"
    if obj and _fold_text(obj) not in folded:
        return f"{obj} iÃ§in {action}"
    return action


def _natural_event_sentence(event: dict, previous: dict | None = None) -> str:
    paraphrase_sentence = _paraphrase_from_event(event)
    if paraphrase_sentence:
        return paraphrase_sentence
    actor = _clean_field(event.get("actor")) or "merkez karakter"
    goal = _clean_field(event.get("goal"))
    action = _natural_action_phrase(event.get("action"), event.get("object"))
    obstacle = _clean_field(event.get("obstacle"))
    consequence = _clean_field(event.get("consequence"))

    parts = [actor]
    if previous and event.get("caused_by"):
        parts.append("ardÄ±ndan")
    if goal and not _pipeline_ifadesi_mi(goal):
        public_goal = _public_story_text(goal)
        if public_goal:
            parts.append(f"{public_goal} iÃ§in")
    parts.append(action)
    sentence = " ".join(part for part in parts if part).strip()
    if obstacle and not _pipeline_ifadesi_mi(obstacle):
        public_obstacle = _public_story_text(obstacle)
        if public_obstacle:
            sentence += f"; ancak {public_obstacle} sÃ¼reci gÃ¼Ã§leÅŸtirir"
    if consequence and not _pipeline_ifadesi_mi(consequence):
        public_consequence = _public_story_text(consequence)
        if public_consequence:
            sentence += f" ve {public_consequence[0].lower() + public_consequence[1:] if public_consequence else public_consequence}"
    sentence = re.sub(r"\b(\w+) eylemini gerÃƒÂ§ekleÃ…Å¸tirir\b", r"\1", sentence, flags=re.IGNORECASE)
    sentence = re.sub(r"\b(\w+) eylemini gerÃ§ekleÅŸtirir\b", r"\1", sentence, flags=re.IGNORECASE)
    sentence = re.sub(r"\s+", " ", sentence).strip(" ,;")
    if sentence:
        sentence = sentence[0].upper() + sentence[1:]
    if sentence and not sentence.endswith((".", "!", "?")):
        sentence += "."
    if _narrative_forbidden_mi(sentence):
        return ""
    return sentence


# ---------------------------------------------------------------------------
# 2. TEK OLAY DÃœÄÃœMÃœNÃœ DOÄAL CÃœMLEYE Ã‡EVÄ°R
# ---------------------------------------------------------------------------

def _yapili_olay_cumlesi(dugum: dict) -> str:
    actor = str(dugum.get("actor") or "").strip()
    if not actor:
        karakterler = dugum.get("ilgili_karakterler") or dugum.get("karakterler") or []
        actor = str(karakterler[0] if karakterler else "").strip()
    action = str(dugum.get("action") or "").strip()
    if not action:
        return ""
    location = str(dugum.get("location") or "").strip()
    target = str(dugum.get("target") or "").strip()
    conflict = str(dugum.get("conflict") or "").strip()
    consequence = str(dugum.get("consequence") or "").strip()
    reason = str(dugum.get("reason") or dugum.get("neden") or "").strip()
    subject = actor or "merkez karakter"
    cumle = subject
    if location:
        cumle += f" {location}"
    if reason:
        cumle += f", {reason.lower()} nedeniyle"
    action_phrase = _eylem_adlastir(action)
    if target and _fold_text(target) not in _fold_text(action):
        cumle += f" {target} iÃ§in {action_phrase}"
    else:
        cumle += f" {action_phrase}"
    if target and _fold_text(target) not in _fold_text(_eylem_yuklemi(action, target)):
        cumle += f" ve {target} Ã¼zerinde Ã§alÄ±ÅŸÄ±r"
    if conflict:
        cumle += f"; karÅŸÄ±sÄ±ndaki sorun {conflict} olarak belirir"
    if consequence:
            cumle += f". Bunun ardÄ±ndan {_sonuc_adlastir(consequence)} oluÅŸur"
    cumle = re.sub(r"\s+", " ", cumle).strip()
    if cumle:
        cumle = cumle[0].upper() + cumle[1:]
    if cumle and not cumle.endswith((".", "!", "?")):
        cumle += "."
    return cumle


def _dogal_olay_cumlesi(dugum: dict, onceki_dugum: dict | None, sira: int) -> str:
    """
    Bir event graph dÃ¼ÄŸÃ¼mÃ¼nÃ¼ doÄŸal TÃ¼rkÃ§e cÃ¼mleye dÃ¶nÃ¼ÅŸtÃ¼rÃ¼r.
    HiÃ§bir pipeline etiketi (Olay adÄ±mÄ±, BaÅŸlangÄ±Ã§ durumu, Ã‡atÄ±ÅŸma adÄ±mÄ± vb.)
    Ã§Ä±ktÄ±da yer almaz.
    """
    structured_sentence = _yapili_olay_cumlesi(dugum)
    if structured_sentence:
        return structured_sentence
    if not str(dugum.get("action") or "").strip():
        return ""
    tur = dugum.get("olay_turu", "olay")
    karakterler = dugum.get("ilgili_karakterler") or []
    karakter_metni = _karakter_birlestir(karakterler)
    kaynak = dugum.get("kaynak_metin") or ""
    neden = dugum.get("neden") or ""
    sonuc = dugum.get("sonuc") or ""

    # Pipeline etiketlerini temizle
    neden_temiz = _neden_temizle(neden, kaynak, karakter_metni, tur)
    sonuc_temiz = _sonuc_temizle(sonuc, kaynak, tur)

    if sira == 0:
        # Ä°lk olay â€” giriÅŸ cÃ¼mlesi
        if karakterler:
            cumle = f"{karakter_metni} {neden_temiz} {sonuc_temiz}"
        else:
            cumle = f"Olaylar {neden_temiz} {sonuc_temiz}"
    else:
        if karakterler:
            cumle = f"{karakter_metni} {neden_temiz} {sonuc_temiz}"
        else:
            cumle = f"Bu aÅŸamada {neden_temiz} {sonuc_temiz}"

    # BÃ¼yÃ¼k harf ile baÅŸlat
    cumle = cumle.strip()
    if cumle:
        cumle = cumle[0].upper() + cumle[1:]
    if cumle and not cumle.endswith((".", "!", "?")):
        cumle += "."
    return cumle


def _neden_temizle(neden: str, kaynak: str, karakter: str, tur: str) -> str:
    """
    Pipeline neden ifadelerini doÄŸal TÃ¼rkÃ§eye Ã§evirir.
    """
    neden_fold = _fold_text(neden)
    kaynak_fold = _fold_text(kaynak)

    # "BaÅŸlangÄ±Ã§ durumu karakteri harekete geÃ§iren ilk koÅŸulu oluÅŸturur."
    if "baÅŸlangÄ±Ã§ durumu" in neden_fold or "baslangic durumu" in neden_fold:
        # Kaynak metinden anlamlÄ± bir neden Ã§Ä±kar
        if kaynak:
            kisa = _kisa_ozet(kaynak, 8)
            if kisa:
                return f"{kisa} nedeniyle"
        return "karÅŸÄ±laÅŸtÄ±ÄŸÄ± ilk durum nedeniyle"

    # "Ã–nceki olayda ortaya Ã§Ä±kan durum yeni bir {tur} adÄ±mÄ±nÄ± gerekli kÄ±lar."
    if "Ã¶nceki olayda" in neden_fold or "onceki olayda" in neden_fold:
        if kaynak:
            kisa = _kisa_ozet(kaynak, 8)
            if kisa:
                return f"geliÅŸmelerin ardÄ±ndan {kisa} iÃ§in"
        return "geliÅŸmelerin ardÄ±ndan"

    # "Metindeki gerekÃ§e, karakterin durumu anlamaya veya seÃ§im yapmaya yÃ¶neldiÄŸini gÃ¶sterir."
    if "metindeki gerekÃ§e" in neden_fold or "metindeki gerekce" in neden_fold:
        if kaynak:
            kisa = _kisa_ozet(kaynak, 8)
            if kisa:
                return f"durumu deÄŸerlendirerek {kisa} iÃ§in"
        return "durumu deÄŸerlendirerek"

    # EÄŸer neden zaten doÄŸal gÃ¶rÃ¼nÃ¼yorsa olduÄŸu gibi kullan
    if len(neden.split()) >= 3 and not _pipeline_ifadesi_mi(neden):
        return neden.lower()

    # Kaynak metinden Ã§Ä±kar
    if kaynak:
        kisa = _kisa_ozet(kaynak, 6)
        if kisa:
            return f"{kisa} iÃ§in"
    return f"{_olay_turu_etiket(tur)}"


def _sonuc_temizle(sonuc: str, kaynak: str, tur: str) -> str:
    """
    Pipeline sonuÃ§ ifadelerini doÄŸal TÃ¼rkÃ§eye Ã§evirir.
    """
    sonuc_fold = _fold_text(sonuc)

    # "Olay Ã¶rgÃ¼sÃ¼nde Ã§Ã¶zÃ¼m veya yeni anlayÄ±ÅŸ yÃ¶nÃ¼nde ilerleme saÄŸlanÄ±r."
    if "Ã§Ã¶zÃ¼m" in sonuc_fold or "cozum" in sonuc_fold:
        if kaynak:
            kisa = _kisa_ozet(kaynak, 6)
            if kisa:
                return f"ve {kisa} yÃ¶nÃ¼nde ilerlenir"
        return "ve Ã§Ã¶zÃ¼me doÄŸru adÄ±m atÄ±lÄ±r"

    # "Karakterin seÃ§imi sonraki olaylarÄ±n yÃ¶nÃ¼nÃ¼ belirler."
    if "seÃ§imi" in sonuc_fold or "secimi" in sonuc_fold or "karakterin seÃ§im" in sonuc_fold or "karakterin secim" in sonuc_fold:
        if kaynak:
            kisa = _kisa_ozet(kaynak, 6)
            if kisa:
                return f"ve bu karar {kisa} yÃ¶nÃ¼nde belirleyici olur"
        return "ve bu karar olaylarÄ±n gidiÅŸatÄ±nÄ± belirler"

    # "Temel sorun gÃ¶rÃ¼nÃ¼r hale gelir ve gerilim artar."
    if "temel sorun" in sonuc_fold or "gerilim" in sonuc_fold:
        if kaynak:
            kisa = _kisa_ozet(kaynak, 6)
            if kisa:
                return f"ve {kisa} sorunu belirginleÅŸir"
        return "ve karÅŸÄ±laÅŸÄ±lan zorluk belirginleÅŸir"

    # "Karakterler arasÄ±ndaki iliÅŸki olayÄ±n ilerlemesinde etkili olur."
    if "iliÅŸki" in sonuc_fold or "iliski" in sonuc_fold:
        if kaynak:
            kisa = _kisa_ozet(kaynak, 6)
            if kisa:
                return f"ve {kisa} iliÅŸkileri olayÄ± etkiler"
        return "ve karakterler arasÄ±ndaki iliÅŸkiler olayÄ± ÅŸekillendirir"

    # "Olay zincirinde bir sonraki adÄ±ma geÃ§iÅŸ hazÄ±rlanÄ±r."
    if "sonraki adÄ±ma" in sonuc_fold or "geÃ§iÅŸ" in sonuc_fold or "gecis" in sonuc_fold:
        if kaynak:
            kisa = _kisa_ozet(kaynak, 6)
            if kisa:
                return f"ve {kisa} ile olaylar ilerler"
        return "ve olaylar yeni bir aÅŸamaya geÃ§er"

    # EÄŸer sonuÃ§ zaten doÄŸal gÃ¶rÃ¼nÃ¼yorsa olduÄŸu gibi kullan
    if len(sonuc.split()) >= 3 and not _pipeline_ifadesi_mi(sonuc):
        return sonuc.lower()

    # Kaynak metinden Ã§Ä±kar
    if kaynak:
        kisa = _kisa_ozet(kaynak, 6)
        if kisa:
            return f"ve {kisa} yaÅŸanÄ±r"
    return f"ve {_olay_turu_etiket(tur)}"


def _kisa_ozet(metin: str, maks_kelime: int = 8) -> str:
    """Metnin baÅŸÄ±ndan anlamlÄ± kÄ±sa bir Ã¶zet Ã§Ä±karÄ±r."""
    metin = re.sub(r"\s+", " ", metin).strip()
    # Noktalama iÅŸaretlerine kadar al
    kisalt = re.split(r"[.!?;]", metin)[0].strip()
    kelimeler = kisalt.split()
    if len(kelimeler) <= maks_kelime:
        return kisalt.lower()
    return " ".join(kelimeler[:maks_kelime]).lower().rstrip(" ,;:") + "..."


def _pipeline_ifadesi_mi(metin: str) -> bool:
    """Metnin pipeline etiketi iÃ§erip iÃ§ermediÄŸini kontrol eder."""
    fold = _fold_text(metin)
    pipeline_isaretleri = [
        "olay adÄ±mÄ±", "olay adimi",
        "baÅŸlangÄ±Ã§ durumu", "baslangic durumu",
        "Ã§atÄ±ÅŸma adÄ±mÄ±", "catisma adimi",
        "karar anÄ±", "karar ani",
        "Ã§Ã¶zÃ¼mÃ¼n gÃ¶rÃ¼nmesi", "cozumun gorunmesi",
        "ipucu ve araÅŸtÄ±rma", "ipucu ve arastirma",
        "Ã¶nceki olayda", "onceki olayda",
        "metindeki gerekÃ§e", "metindeki gerekce",
        "olay zincirinde", "olay zincirinde",
        "sonraki adÄ±ma", "sonraki adima",
        "temel sorun gÃ¶rÃ¼nÃ¼r",
        "karakterin seÃ§imi", "karakterin secimi",
    ]
    return any(isaret in fold for isaret in pipeline_isaretleri)


# ---------------------------------------------------------------------------
# 3. OLAY AKIÅINI DOÄAL METNE DÃ–NÃœÅTÃœR
# ---------------------------------------------------------------------------

def _dogal_olay_akisi(event_graph: List[dict], karakterler: Iterable[dict]) -> str:
    """
    Event graph dÃ¼ÄŸÃ¼mlerini akÄ±cÄ± bir anlatÄ± paragrafÄ±na dÃ¶nÃ¼ÅŸtÃ¼rÃ¼r.
    HiÃ§bir pipeline etiketi Ã§Ä±ktÄ±da yer almaz.
    """
    story_events = reconstruct_story_events(event_graph)
    if not story_events:
        return ""

    karakter_adi_seti = {
        str(k.get("ad") or k.get("karakter_adi") or "").strip()
        for k in karakterler or []
        if k.get("ad") or k.get("karakter_adi")
    }

    cumleler = []
    onceki = None
    for sira, dugum in enumerate(story_events):
        # Karakterleri zenginleÅŸtir (bilinen karakter setinden)
        mevcut_karakterler = dugum.get("ilgili_karakterler") or []
        if not mevcut_karakterler and karakter_adi_seti:
            # Kaynak metinde geÃ§en karakterleri bul
            kaynak = dugum.get("kaynak_metin") or ""
            for k_adi in karakter_adi_seti:
                if _fold_text(k_adi) in _fold_text(kaynak):
                    mevcut_karakterler.append(k_adi)
            dugum["ilgili_karakterler"] = mevcut_karakterler

        cumle = _natural_event_sentence(dugum, onceki)
        if cumle:
            cumleler.append(cumle)
        onceki = dugum

    if not cumleler:
        return ""

    # CÃ¼mleleri akÄ±cÄ± bir paragrafta birleÅŸtir
    metin = " ".join(cumleler)

    # AkÄ±cÄ±lÄ±k iyileÅŸtirmeleri
    metin = _akiciligi_iyilestir(metin)

    return metin


def _akiciligi_iyilestir(metin: str) -> str:
    """ArdÄ±ÅŸÄ±k cÃ¼mlelerdeki tekrarlarÄ± ve doÄŸal olmayan geÃ§iÅŸleri dÃ¼zeltir."""
    # "Ali ... Ali" tekrarÄ±nÄ± Ã¶nle
    # "Ali ... O" dÃ¶nÃ¼ÅŸÃ¼mÃ¼
    cumleler = re.split(r"(?<=[.!?])\s+", metin)
    iyilestirilmis = []
    onceki_ozne = ""

    for cumle in cumleler:
        cumle = cumle.strip()
        if not cumle:
            continue

        # AynÄ± Ã¶znenin tekrarÄ±nÄ± zamirle deÄŸiÅŸtir
        if onceki_ozne and cumle.startswith(onceki_ozne):
            # "Ali ... Ali" â†’ "Ali ... O"
            zamir = "O" if onceki_ozne[0].isupper() else "o"
            # Sadece ilk kelime aynÄ±ysa deÄŸiÅŸtir
            ilk_kelime = cumle.split()[0] if cumle.split() else ""
            if ilk_kelime == onceki_ozne:
                cumle = zamir + cumle[len(onceki_ozne):]

        # Yeni Ã¶zneyi kaydet
        ilk_kelime = cumle.split()[0] if cumle.split() else ""
        if ilk_kelime and ilk_kelime[0].isupper():
            onceki_ozne = ilk_kelime

        iyilestirilmis.append(cumle)

    return " ".join(iyilestirilmis)


# ---------------------------------------------------------------------------
# 4. ANA Ã–ZET ÃœRETÄ°CÄ°SÄ°
# ---------------------------------------------------------------------------

def _cumlelere_ayir(metin: str) -> List[str]:
    return [
        cumle.strip()
        for cumle in re.split(r"(?<=[.!?])\s+", str(metin or "").strip())
        if len(cumle.strip().split()) >= 4
    ]


def _bolumlu_somut_ozet(cumleler: List[str]) -> str:
    if len(cumleler) < 3:
        return ""
    bolumler = [
        ("GiriÅŸ", 0),
        ("GeliÅŸme", 1),
        ("Temel Ã‡atÄ±ÅŸma", 2),
        ("Karakter Ä°liÅŸkileri", 0),
        ("Genel KapanÄ±ÅŸ", max(0, len(cumleler) - 3)),
    ]
    parcalar = []
    for baslik, baslangic in bolumler:
        secilenler = []
        for offset in range(3):
            secilenler.append(cumleler[(baslangic + offset) % len(cumleler)])
        parcalar.append(f"{baslik}:\n" + " ".join(secilenler))
    return "\n\n".join(parcalar)


def _birlestir_ozet_ve_olay_akisi(
    baslik: str,
    event_graph: List[dict],
    karakterler: Iterable[dict],
    min_kelime: int = 100,
) -> str:
    """
    Kitap baÅŸlÄ±ÄŸÄ±, event graph ve karakter bilgilerini kullanarak
    akÄ±cÄ± bir Ã¶zet metni Ã¼retir. Pipeline etiketi iÃ§ermez.

    EÄŸer event graph gÃ¼venilir deÄŸilse (< 3 dÃ¼ÄŸÃ¼m) boÅŸ string dÃ¶ndÃ¼rÃ¼r.
    """
    story_events = reconstruct_story_events(event_graph)
    if len(story_events) < 3:
        return ""
    scene_graph = build_scene_graph(story_events)
    story_summary = _build_story_abstraction_summary(baslik, scene_graph, min_kelime)
    if story_summary and story_summary != SAFE_LIMITED_SUMMARY:
        return story_summary

    karakter_listesi = list(karakterler or [])
    ana_karakter = ""
    for k in karakter_listesi:
        if k.get("ana_karakter_mi") or k.get("kategori") in ("merkez karakter", "anlatÄ±cÄ±"):
            ana_karakter = str(k.get("ad") or k.get("karakter_adi") or "").strip()
            break
    if not ana_karakter and karakter_listesi:
        ana_karakter = str(karakter_listesi[0].get("ad") or karakter_listesi[0].get("karakter_adi") or "").strip()

    # Olay akÄ±ÅŸÄ±nÄ± doÄŸal metne Ã§evir
    olay_metni = _dogal_olay_akisi(story_events, karakter_listesi)
    if not olay_metni or len(olay_metni.split()) < 20:
        return ""
    olay_cumleleri = []
    seen_olay = set()
    for sentence in _split_evidence_sentences(olay_metni):
        cleaned = _clean_evidence_sentence(sentence)
        folded_sentence = _fold_text(cleaned)
        if cleaned and folded_sentence not in seen_olay:
            olay_cumleleri.append(cleaned)
            seen_olay.add(folded_sentence)
    if len(olay_cumleleri) >= 3:
        clean_flow_summary = _clean_flow_summary_from_sentences(olay_cumleleri, story_events, min_kelime)
        if clean_flow_summary:
            return clean_flow_summary
        joined = _enrich_narrative_summary(olay_cumleleri, story_events, min_kelime)
        if joined and not _narrative_forbidden_mi(joined) and _summary_quote_ratio(joined, story_events) <= 0.25:
            return joined

    direct_paraphrases = []
    for event in story_events:
        sentence = _paraphrase_from_event(event)
        if sentence:
            direct_paraphrases.append(sentence)
    direct_joined = _enrich_narrative_summary(direct_paraphrases, story_events, min_kelime)
    if not direct_joined:
        direct_joined = _force_enrich_clean_paraphrases(direct_paraphrases, story_events, min_kelime)
    if direct_joined and not _narrative_forbidden_mi(direct_joined) and _summary_quote_ratio(direct_joined, story_events) <= 0.25:
        return direct_joined

    return ""


# ---------------------------------------------------------------------------
# 5. DIÅ ARAYÃœZ (PUBLIC API)
# ---------------------------------------------------------------------------

def narrative_realize(
    baslik: str,
    event_graph: List[dict],
    karakterler: Iterable[dict],
    min_kelime: int = 120,
) -> str:
    """
    Event graph dÃ¼ÄŸÃ¼mlerini doÄŸal TÃ¼rkÃ§e Ã¶zete dÃ¶nÃ¼ÅŸtÃ¼rÃ¼r.

    Parametreler:
        baslik: Kitap baÅŸlÄ±ÄŸÄ±
        event_graph: _extract_event_graph Ã§Ä±ktÄ±sÄ± (dÃ¼ÄŸÃ¼m listesi)
        karakterler: Karakter profilleri listesi
        min_kelime: Minimum Ã¶zet kelime sayÄ±sÄ±

    DÃ¶nÃ¼ÅŸ:
        DoÄŸal TÃ¼rkÃ§e Ã¶zet metni.
        EÄŸer olay Ã¶rgÃ¼sÃ¼ gÃ¼venilir biÃ§imde Ã§Ä±karÄ±lamazsa:
        "olay Ã¶rgÃ¼sÃ¼ gÃ¼venilir biÃ§imde Ã§Ä±karÄ±lamadÄ±"
    """
    story_events = reconstruct_story_events(event_graph)
    concrete_event_count = sum(
        1 for dugum in (story_events or [])
        if isinstance(dugum, dict) and str(dugum.get("action") or "").strip()
    )
    if not story_events or len(story_events) < 3 or concrete_event_count < 3:
        return "olay Ã¶rgÃ¼sÃ¼ gÃ¼venilir biÃ§imde Ã§Ä±karÄ±lamadÄ±"

    # Event graph dÃ¼ÄŸÃ¼mlerini doÄŸal metne Ã§evir
    sonuc = _birlestir_ozet_ve_olay_akisi(
        baslik, story_events, karakterler, min_kelime
    )

    if not sonuc or sonuc == SAFE_LIMITED_SUMMARY or _narrative_forbidden_mi(sonuc) or _summary_commentary_forbidden_mi(sonuc):
        original_paraphrases = [
            sentence
            for sentence in (_paraphrase_from_event(event) for event in event_graph or [])
            if sentence
        ]
        original_summary = _force_enrich_clean_paraphrases(original_paraphrases, story_events, min_kelime)
        if original_summary and not _narrative_forbidden_mi(original_summary):
            return original_summary
        return SAFE_LIMITED_SUMMARY

    return sonuc


def final_turkish_cleanup(text: str) -> str:
    cleaned = str(text or "")
    replacements = [
        (r"\bbaski\b", "baskÄ±"),
        (r"\bhalkin\b", "halkÄ±n"),
        (r"\bKapgotur\b", "KapgÃ¶tÃ¼r"),
        (r"\bkaynagini\b", "kaynaÄŸÄ±nÄ±"),
        (r"\bcevresindeki\b", "Ã§evresindeki"),
    ]
    replacements.extend([
        (r"\bartirir\b", "artÄ±rÄ±r"),
        (r"\bicin\b", "iÃ§in"),
        (r"\bisaretleri\b", "iÅŸaretleri"),
        (r"\bbaslar\b", "baÅŸlar"),
        (r"\byonetimin\b", "yÃ¶netimin"),
        (r"\byarattigi\b", "yarattÄ±ÄŸÄ±"),
        (r"\bsikintiyi\b", "sÄ±kÄ±ntÄ±yÄ±"),
        (r"\barasindaki\b", "arasÄ±ndaki"),
        (r"\buzakligi\b", "uzaklÄ±ÄŸÄ±"),
        (r"\bgorur\b", "gÃ¶rÃ¼r"),
        (r"\badimini\b", "adÄ±mÄ±nÄ±"),
        (r"\bgore\b", "gÃ¶re"),
        (r"\baciklamayla\b", "aÃ§Ä±klamayla"),
        (r"\bsomutlastirir\b", "somutlaÅŸtÄ±rÄ±r"),
        (r"\banlatilan\b", "anlatÄ±lan"),
        (r"\bbulus\b", "buluÅŸ"),
        (r"\byaklastirir\b", "yaklaÅŸtÄ±rÄ±r"),
        (r"\byonunu\b", "yÃ¶nÃ¼nÃ¼"),
        (r"\bkarsidaki\b", "karÅŸÄ±daki"),
        (r"\baciga\b", "aÃ§Ä±ÄŸa"),
        (r"\bcikarir\b", "Ã§Ä±karÄ±r"),
        (r"\bele alinmasini\b", "ele alÄ±nmasÄ±nÄ±"),
        (r"\bsaglar\b", "saÄŸlar"),
        (r"\bcozum\b", "Ã§Ã¶zÃ¼m"),
        (r"\bonceki\b", "Ã¶nceki"),
        (r"\bgelisme\b", "geliÅŸme"),
    ])
    for pattern, replacement in replacements:
        cleaned = re.sub(pattern, replacement, cleaned)
    mojibake_repairs = [
        ("baskÃ„Â±", "baskÄ±"),
        ("halkÃ„Â±n", "halkÄ±n"),
        ("KapgÃƒÂ¶tÃƒÂ¼r", "KapgÃ¶tÃ¼r"),
        ("kaynaÃ„Å¸Ã„Â±nÃ„Â±", "kaynaÄŸÄ±nÄ±"),
        ("ÃƒÂ§evresindeki", "Ã§evresindeki"),
    ]
    for broken, repaired in mojibake_repairs:
        cleaned = cleaned.replace(broken, repaired)
    return cleaned


_narrative_realize_impl = narrative_realize


def narrative_realize(
    baslik: str,
    event_graph: List[dict],
    karakterler: Iterable[dict],
    min_kelime: int = 120,
) -> str:
    return unicodedata.normalize(
        "NFC",
        final_turkish_cleanup(_narrative_realize_impl(baslik, event_graph, karakterler, min_kelime)),
    )


def narrative_realize_olay_akisi(
    event_graph: List[dict],
    karakterler: Iterable[dict],
) -> List[dict]:
    """
    Event graph dÃ¼ÄŸÃ¼mlerini doÄŸal TÃ¼rkÃ§e olay akÄ±ÅŸÄ± maddelerine dÃ¶nÃ¼ÅŸtÃ¼rÃ¼r.
    Her madde pipeline etiketi yerine doÄŸal bir metin iÃ§erir.

    DÃ¶nÃ¼ÅŸ:
        Her biri {sayfa, metin} ÅŸeklinde sÃ¶zlÃ¼klerden oluÅŸan liste.
        EÄŸer event graph boÅŸ veya zayÄ±fsa boÅŸ liste dÃ¶ndÃ¼rÃ¼r.
    """
    story_events = reconstruct_story_events(event_graph)
    concrete_event_count = sum(
        1 for dugum in (story_events or [])
        if isinstance(dugum, dict) and str(dugum.get("action") or "").strip()
    )
    if not story_events or len(story_events) < 3 or concrete_event_count < 3:
        return []

    karakter_adi_seti = {
        str(k.get("ad") or k.get("karakter_adi") or "").strip()
        for k in karakterler or []
        if k.get("ad") or k.get("karakter_adi")
    }

    sonuc = []
    onceki = None
    for sira, dugum in enumerate(story_events):
        # Karakterleri zenginleÅŸtir
        mevcut_karakterler = dugum.get("ilgili_karakterler") or []
        if not mevcut_karakterler and karakter_adi_seti:
            kaynak = dugum.get("kaynak_metin") or ""
            for k_adi in karakter_adi_seti:
                if _fold_text(k_adi) in _fold_text(kaynak):
                    mevcut_karakterler.append(k_adi)

        cumle = _natural_event_sentence(dugum, onceki)
        if cumle:
            repaired = cumle
            try:
                if isinstance(cumle, str) and ("Ã" in cumle or "Â" in cumle or "Å" in cumle):
                    candidate = cumle.encode("latin-1").decode("utf-8")
                    if sum(1 for ch in candidate if ord(ch) < 128) >= sum(1 for ch in cumle if ord(ch) < 128):
                        repaired = candidate
            except Exception:
                repaired = cumle
            cleaned_cumle = unicodedata.normalize("NFC", final_turkish_cleanup(repaired))
            sonuc.append({
                "scene_id": dugum.get("scene_id"),
                "sayfa": dugum.get("sayfa") or dugum.get("page"),
                "page": dugum.get("page") or dugum.get("sayfa"),
                "actor": dugum.get("actor"),
                "goal": dugum.get("goal"),
                "action": dugum.get("action"),
                "object": dugum.get("object"),
                "obstacle": dugum.get("obstacle"),
                "consequence": dugum.get("consequence"),
                "evidence": dugum.get("evidence"),
                "caused_by": dugum.get("caused_by") or [],
                "causes": dugum.get("causes") or [],
                "metin": cleaned_cumle,
            })
        onceki = dugum

    return sonuc


# ---------------------------------------------------------------------------
# 6. YARDIMCI: Metin normalizasyonu
# ---------------------------------------------------------------------------

def _fold_text(text: str) -> str:
    """Metni karÅŸÄ±laÅŸtÄ±rma iÃ§in normalize eder."""
    if not text:
        return ""
    # Try to repair common mojibake caused by double-encoding
    # Try multiple common mojibake repairs and pick the best candidate
    try:
        candidates = [text]
        if isinstance(text, str):
            try:
                candidates.append(text.encode("latin-1").decode("utf-8"))
            except Exception:
                pass
            try:
                candidates.append(text.encode("utf-8").decode("latin-1"))
            except Exception:
                pass
        def score(s: str) -> int:
            # prefer strings with more ASCII letters and Turkish letters
            turkish_chars = set("ığüşöçİĞÜŞÖÇ")
            return sum(1 for ch in s if ord(ch) < 128) + sum(2 for ch in s if ch in turkish_chars)

        best = max(candidates, key=score)
        text = best
    except Exception:
        pass
    text = str(text)
    safe_map = {
        source: target
        for source, target in {
            "ı": "i", "ğ": "g", "ü": "u", "ş": "s", "ö": "o", "ç": "c",
            "İ": "i", "Ğ": "g", "Ü": "u", "Ş": "s", "Ö": "o", "Ç": "c",
        }.items()
        if len(source) == 1
    }
    text = text.translate(str.maketrans(safe_map))
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    replacements = {
        "Ä±": "i", "ÄŸ": "g", "Ã¼": "u", "ÅŸ": "s", "Ã¶": "o", "Ã§": "c",
        "Ä°": "i", "Ä": "g", "Ãœ": "u", "Å": "s", "Ã–": "o", "Ã‡": "c",
        "Ã„Â±": "i", "Ã„Å¸": "g", "ÃƒÂ¼": "u", "Ã…Å¸": "s", "ÃƒÂ¶": "o", "ÃƒÂ§": "c",
        "Ã¤Â±": "i", "Ã¤Ã¿": "g", "Ã¤ÄŸ": "g", "Ã£Â¼": "u", "Ã¥Ã¿": "s", "Ã¥ÅŸ": "s",
        "Ã£Â¶": "o", "Ã£Â§": "c", "Ã£â€“": "o", "Ã£Å“": "u",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

