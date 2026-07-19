import re

FORBIDDEN_RENDER_MARKERS = [
    "Bu okuma",
    "Sonuç olarak",
    "Sonuc olarak",
    "Olay akışı",
    "Olay akisi",
    "somut bir karar uygulamak",
    "çözüme yarayan bilgi bulmak",
    "cozume yarayan bilgi bulmak",
    # Pipeline expression markers from quality gate
    "Olay adımı",
    "Olay zincirinde",
    "Başlangıç durumu",
    "Önceki olayda ortaya çıkan durum",
    "Çatışmanın belirginleşmesi",
    "anlatı ilerler",
    "yeni yön kazanır",
    "bu aşamada",
    "olaylar gelişir",
    "karakter harekete geçer",
    "olay zinciri",
    "sahnedeki sorun veya ipucu",
    "önemli bilgi",
    "somut bir adım",
    "çözüm için harekete geçer",
    "durumu daha iyi anlar",
    "önceki gelişmenin ardından",
    "önceki sahnedeki bilgi",
    "önemli bulmasını paylaşır",
    "çözüm yolunu başlatır",
    "olayın anlamını kavrar",
    "bu gelişmeden sonra",
    "önemli bir ipucu",
    "bilgi veya nesne başka bir kişiye aktarılır",
    "sahnedeki belirsizlik",
    "sahnedeki sorun",
    "daha önce öğrenilenler",
]

test_text = "Olay adımı: Başlangıç durumu anlatı ilerler yeni yön kazanır test"

def _clean(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()

def _sanitize_rendered_summary(text):
    cleaned = _clean(text)
    for marker in FORBIDDEN_RENDER_MARKERS:
        cleaned = re.sub(re.escape(marker), "", cleaned, flags=re.IGNORECASE)
    return _clean(cleaned)

result = _sanitize_rendered_summary(test_text)
print(f"Input: {test_text}")
print(f"Output: {result}")
print(f"Markers removed: {test_text != result}")
