"""
PDF gorsel denetim modeli.

Bu modul iki ayrimi kesin tutar:
- XObject/gorsel sayimi teknik bir PDF bulgusudur.
- Icerik riski yalnizca gercek goruntu analizi calistiginda puanlanir.
"""

from __future__ import annotations

import base64
import json
import os
from copy import deepcopy
from typing import Callable, Iterable

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


VISUAL_AUDIT_CATEGORIES = {
    "siddet": "Şiddet ve Saldırganlık",
    "kan_yaralanma": "Kan / Yaralanma",
    "silah": "Silah ve Tehlikeli Araçlar",
    "zararli_aliskanlik": "Zararlı Alışkanlıklar",
    "cinsellik": "Cinsellik ve Mahremiyet",
    "acik_kiyafet": "Açık Kıyafet",
    "korku_travma": "Korku ve Travma",
    "okultizm": "Okültizm ve Batıl Unsurlar",
    "ayrimcilik": "Ayrımcılık ve Nefret Sembolleri",
}

_LEGACY_CATEGORY_ALIASES = {
    "siddet_saldirganlik": "siddet",
    "şiddet ve saldırganlık": "siddet",
    "kan / yaralanma": "kan_yaralanma",
    "kan_yaralanma": "kan_yaralanma",
    "silah_tehlikeli_araclar": "silah",
    "zararlı alışkanlıklar": "zararli_aliskanlik",
    "zararli_aliskanliklar": "zararli_aliskanlik",
    "cinsellik_mahremiyet": "cinsellik",
    "açık kıyafet": "acik_kiyafet",
    "acik_kiyafet": "acik_kiyafet",
    "okültizm ve batıl unsurlar": "okultizm",
    "okultizm_batil": "okultizm",
    "ayrımcılık ve nefret sembolleri": "ayrimcilik",
    "ayrimcilik_nefret": "ayrimcilik",
}


def _empty_category(reason: str, status: str = "İncelenmedi") -> dict:
    return {
        "durum": status,
        "puan": None,
        "gerekce": reason,
    }


def gorsel_analiz_yapilmadi_sonucu(sayfa="") -> dict:
    """
    Gorsel analiz yapilmadiginda kullanilacak zorunlu guvenli cikti.

    XObject varligi yalnizca teknik bir PDF nesnesi tespitidir; acik kiyafet,
    siddet, alkol, okult sembol vb. icerik iddiasi uretmez.
    """
    reason = (
        "Görsel içerik analizi yapılmamıştır. Yalnızca PDF içerisinde "
        "görsel nesne bulunduğu tespit edilmiştir."
    )
    sonuc = {"sayfa": sayfa}
    for key in VISUAL_AUDIT_CATEGORIES:
        sonuc[key] = _empty_category(reason)
    sonuc["genel_risk"] = None
    sonuc["nihai_karar"] = "İncelenmedi"
    sonuc["gorsel_icerik_analizi_yapildi"] = False
    sonuc["puanlama_durumu"] = "İncelenmedi; kategori risk puanı üretilmedi."
    sonuc["analiz_notu"] = reason
    return sonuc


def _category_key(value: str) -> str | None:
    normalized = str(value or "").strip().lower()
    if normalized in VISUAL_AUDIT_CATEGORIES:
        return normalized
    return _LEGACY_CATEGORY_ALIASES.get(normalized)


def _clamp_risk(value) -> int:
    try:
        return max(0, min(5, int(round(float(value)))))
    except (TypeError, ValueError):
        return 0


def _clamp_confidence(value) -> float:
    try:
        return round(max(0.0, min(1.0, float(value))), 2)
    except (TypeError, ValueError):
        return 0.0


def _normalize_visual_finding(raw: dict, page_number: int, image_index: int) -> dict:
    category = _category_key(raw.get("kategori") or raw.get("risk_kategorisi") or raw.get("category"))
    if not category:
        category = "siddet"
    risk = _clamp_risk(raw.get("risk_puani", raw.get("risk", raw.get("puan", 0))))
    confidence = _clamp_confidence(raw.get("karar_guveni", raw.get("guven", raw.get("confidence", 0))))
    return {
        "sayfa": int(raw.get("sayfa") or page_number),
        "gorsel_no": int(raw.get("gorsel_no") or image_index),
        "gorsel_aciklamasi": str(
            raw.get("gorsel_aciklamasi")
            or raw.get("gorsel")
            or raw.get("aciklama")
            or "Görsel açıklaması üretilemedi."
        ).strip(),
        "kategori": category,
        "kategori_adi": VISUAL_AUDIT_CATEGORIES.get(category, category),
        "risk_puani": risk,
        "karar_guveni": confidence,
    }


def _normalize_visual_record(raw: dict, page_number: int, image_index: int) -> dict:
    """Her analiz edilen gorsel/sayfa icin rapor satiri uretir."""
    if raw.get("analiz_hatasi"):
        return {
            "sayfa": int(raw.get("sayfa") or page_number or 0),
            "gorsel_no": int(raw.get("gorsel_no") or image_index or 0),
            "kaynak": raw.get("kaynak", ""),
            "gorsel_aciklamasi": "Görsel analiz tamamlanamadı.",
            "kategori": "incelenmedi",
            "kategori_adi": "İncelenmedi",
            "risk_puani": None,
            "karar_guveni": 0.0,
            "analiz_durumu": "Analiz Hatası",
            "analiz_hatasi": raw.get("analiz_hatasi", ""),
        }

    raw_findings = raw.get("bulgular") or []
    normalized_findings = [
        _normalize_visual_finding(finding, page_number, image_index)
        for finding in raw_findings
        if isinstance(finding, dict)
    ]
    highest = max(
        normalized_findings,
        key=lambda item: (item["risk_puani"], item["karar_guveni"]),
        default=None,
    )
    risk = highest["risk_puani"] if highest else _clamp_risk(raw.get("risk_puani", raw.get("risk", 0)))
    confidence = highest["karar_guveni"] if highest else _clamp_confidence(
        raw.get("karar_guveni", raw.get("guven", raw.get("confidence", raw.get("genel_guven", 0))))
    )
    category = highest["kategori"] if highest else _category_key(raw.get("kategori") or "") or "tespit_edilmedi"
    category_name = highest["kategori_adi"] if highest else (
        VISUAL_AUDIT_CATEGORIES.get(category) or "Tespit Edilmedi"
    )
    return {
        "sayfa": int(raw.get("sayfa") or page_number or 0),
        "gorsel_no": int(raw.get("gorsel_no") or image_index or 0),
        "kaynak": raw.get("kaynak", ""),
        "gorsel_aciklamasi": str(
            raw.get("gorsel_aciklamasi")
            or raw.get("aciklama")
            or (highest or {}).get("gorsel_aciklamasi")
            or "Görsel analiz edildi; sakıncalı unsur tespit edilmedi."
        ).strip(),
        "kategori": category,
        "kategori_adi": category_name,
        "risk_puani": risk,
        "karar_guveni": confidence,
        "analiz_durumu": "Analiz Edildi" if not raw.get("analiz_hatasi") else "Analiz Hatası",
        "analiz_hatasi": raw.get("analiz_hatasi", ""),
    }


def normalize_gorsel_denetim(denetim: dict | None, sayfa="") -> dict:
    """
    Disaridan gelen gorsel denetim sonucunu guvenli ciktiya normalize eder.

    Analiz yapildi bilgisi yoksa veya False ise tum kategoriler Incelenmedi kalir.
    """
    if not denetim or not denetim.get("gorsel_icerik_analizi_yapildi"):
        return gorsel_analiz_yapilmadi_sonucu(sayfa=sayfa)

    normalized = deepcopy(denetim)
    normalized.setdefault("sayfa", sayfa)
    findings = [
        _normalize_visual_finding(finding, int(finding.get("sayfa") or 0), int(finding.get("gorsel_no") or 0))
        for finding in normalized.get("bulgular", []) or []
        if isinstance(finding, dict)
    ]
    normalized["bulgular"] = findings
    genel_risk = max((finding["risk_puani"] for finding in findings), default=0)

    for key in VISUAL_AUDIT_CATEGORIES:
        kategori = normalized.get(key) or {}
        puan = _clamp_risk(kategori.get("puan", 0))
        kategori["durum"] = kategori.get("durum") or ("Tespit Edildi" if puan > 0 else "Tespit Edilmedi")
        kategori["puan"] = puan
        kategori["gerekce"] = kategori.get("gerekce", "")
        normalized[key] = kategori
        genel_risk = max(genel_risk, puan)

    normalized["genel_risk"] = _clamp_risk(normalized.get("genel_risk", genel_risk) or genel_risk)
    normalized["nihai_karar"] = normalized.get("nihai_karar") or (
        "Uygun" if normalized["genel_risk"] == 0 else "Koşullu"
    )
    normalized["gorsel_icerik_analizi_yapildi"] = True
    return normalized


def _empty_analyzed_result() -> dict:
    reason = "Görsel içerik analizi çalıştırıldı; sakıncalı görsel kategori tespit edilmedi."
    result = {"sayfa": "", "bulgular": []}
    for key in VISUAL_AUDIT_CATEGORIES:
        result[key] = {
            "durum": "Tespit Edilmedi",
            "puan": 0,
            "gerekce": reason,
        }
    result["genel_risk"] = 0
    result["nihai_karar"] = "Uygun"
    result["gorsel_icerik_analizi_yapildi"] = True
    result["puanlama_durumu"] = "Görsel içerik analizi tamamlandı."
    result["analiz_notu"] = reason
    return result


def build_visual_audit_result(image_results: Iterable[dict]) -> dict:
    """Gorsel bazli analiz cevaplarini kategori ozetine donusturur."""
    result = _empty_analyzed_result()
    pages = set()
    findings = []
    visual_records = []
    failed_count = 0

    for image_result in image_results:
        page_number = int(image_result.get("sayfa") or 0)
        image_index = int(image_result.get("gorsel_no") or 0)
        pages.add(page_number)
        if image_result.get("analiz_hatasi"):
            failed_count += 1
        visual_records.append(_normalize_visual_record(image_result, page_number, image_index))
        raw_findings = image_result.get("bulgular")
        if raw_findings is None and image_result.get("risk_puani", 0):
            raw_findings = [image_result]
        for raw in raw_findings or []:
            if not isinstance(raw, dict):
                continue
            finding = _normalize_visual_finding(raw, page_number, image_index)
            if finding["risk_puani"] <= 0:
                continue
            findings.append(finding)

    result["sayfa"] = ", ".join(str(page) for page in sorted(p for p in pages if p))
    result["bulgular"] = findings
    result["gorsel_analizleri"] = visual_records
    result["analiz_edilen_gorsel_sayisi"] = len(visual_records) - failed_count
    result["tamamlanamayan_gorsel_sayisi"] = failed_count

    for key, label in VISUAL_AUDIT_CATEGORIES.items():
        category_findings = [finding for finding in findings if finding["kategori"] == key]
        if not category_findings:
            continue
        highest = max(category_findings, key=lambda item: (item["risk_puani"], item["karar_guveni"]))
        result[key] = {
            "durum": "Tespit Edildi",
            "puan": highest["risk_puani"],
            "gerekce": f"{label}: {highest['gorsel_aciklamasi']} (güven {highest['karar_guveni']:.2f})",
        }

    result["genel_risk"] = max((finding["risk_puani"] for finding in findings), default=0)
    result["nihai_karar"] = "Uygun" if result["genel_risk"] == 0 else "Koşullu"
    result = normalize_gorsel_denetim(result, sayfa=result["sayfa"])
    if failed_count:
        result["gorsel_icerik_analizi_yapildi"] = False
        result["nihai_karar"] = "İncelenmedi"
        result["analiz_notu"] = "Görsel içerik analizinde en az bir görsel tamamlanamadı."
    return result


def _extract_json_object(text: str) -> dict:
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json\n", "", 1).replace("JSON\n", "", 1)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise


def _openai_vision_provider() -> Callable[[bytes, dict], dict] | None:
    api_key = os.getenv("OPENAI_API_KEY")
    placeholder_keys = {
        "your-openai-api-key-here",
        "your_openai_api_key",
        "your_openai_api_key_here",
        "sk-your-openai-api-key-here",
    }
    if api_key and api_key.strip().lower() in placeholder_keys:
        return None
    if not api_key or os.getenv("DISABLE_VISUAL_AI", "").lower() in {"1", "true", "yes"}:
        return None
    try:
        from openai import OpenAI
    except Exception:
        return None

    timeout = float(os.getenv("OPENAI_VISION_TIMEOUT", "30"))
    client = OpenAI(api_key=api_key, timeout=timeout)
    model = os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")

    def analyze(image_bytes: bytes, metadata: dict) -> dict:
        mime = metadata.get("mime_type") or "image/png"
        data_url = f"data:{mime};base64,{base64.b64encode(image_bytes).decode('ascii')}"
        prompt = (
            "Bir çocuk/ilk gençlik kitabı PDF sayfasını veya görselini içerik güvenliği açısından denetle. "
            "Yalnızca görünür görsel kanıta dayan; metinden tahmin yürütme. Sayfadaki tüm figürleri, nesneleri "
            "ve sahne bağlamını kısa ama somut biçimde açıkla. Şu kategorileri ayrı ayrı tara: "
            + ", ".join(VISUAL_AUDIT_CATEGORIES.values())
            + ". JSON döndür: {\"gorsel_aciklamasi\": string, \"genel_guven\": 0-1, \"bulgular\": ["
            "{\"kategori\": kategori_anahtari, \"gorsel_aciklamasi\": string, "
            "\"risk_puani\": 0-5, \"karar_guveni\": 0-1}]}. "
            "Kategori anahtarları: "
            + ", ".join(VISUAL_AUDIT_CATEGORIES.keys())
            + ". Risk yoksa bulgular boş liste olsun, ama gorsel_aciklamasi ve genel_guven yine dolu gelsin."
        )
        response = client.responses.create(
            model=model,
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": data_url, "detail": "high"},
                ],
            }],
        )
        parsed = _extract_json_object(getattr(response, "output_text", "") or "")
        return parsed if isinstance(parsed, dict) else {}

    return analyze


def analyze_extracted_images(
    extracted_images: list[dict],
    provider: Callable[[bytes, dict], dict] | None = None,
) -> dict:
    """
    Cikarilmis PDF gorsellerini vision saglayicisiyle analiz eder.

    provider yoksa risk puani uretmez ve sonucu Incenlenmedi olarak dondurur.
    """
    if not extracted_images:
        return _empty_analyzed_result()

    provider = provider or _openai_vision_provider()
    if provider is None:
        pages = sorted({int(item.get("sayfa") or 0) for item in extracted_images if item.get("sayfa")})
        return gorsel_analiz_yapilmadi_sonucu(sayfa=", ".join(str(page) for page in pages))

    image_results = []
    fatal_error_markers = (
        "insufficient_quota",
        "quota",
        "billing",
        "invalid_api_key",
        "authentication",
        "incorrect api key",
        "429",
        "401",
    )
    for item in extracted_images:
        image_bytes = item.get("data") or b""
        if not image_bytes:
            continue
        try:
            raw = provider(image_bytes, item) or {}
            raw["sayfa"] = item.get("sayfa")
            raw["gorsel_no"] = item.get("gorsel_no")
            raw["kaynak"] = item.get("kaynak", item.get("format", ""))
            image_results.append(raw)
        except Exception as exc:
            image_results.append({
                "sayfa": item.get("sayfa"),
                "gorsel_no": item.get("gorsel_no"),
                "kaynak": item.get("kaynak", item.get("format", "")),
                "bulgular": [],
                "analiz_hatasi": str(exc),
            })
            hata = str(exc).lower()
            if any(marker in hata for marker in fatal_error_markers):
                break

    if not image_results:
        pages = sorted({int(item.get("sayfa") or 0) for item in extracted_images if item.get("sayfa")})
        return gorsel_analiz_yapilmadi_sonucu(sayfa=", ".join(str(page) for page in pages))

    return build_visual_audit_result(image_results)
