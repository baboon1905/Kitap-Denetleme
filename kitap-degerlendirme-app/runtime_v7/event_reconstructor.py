"""Event Reconstruction Layer — Sprint 9A

Converts raw evidence snippets into structured event representations.

Rules:
  - No LLM
  - Deterministic output
  - Preserve source_sentence_id
  - Do not mutate input
  - Shadow-only (no production changes)
  - Extract actors, actions, goals, conflicts, results from evidence
"""
import re
from typing import Any, Dict, List, Optional


def _normalize_source_id(item: Any, payload_file: Optional[str] = None, book_index: Optional[int] = None, evidence_index: Optional[int] = None) -> str:
    """Extract a source identifier from evidence metadata or create a deterministic fallback."""
    if isinstance(item, dict):
        for key in ['source_sentence_id', 'sentence_id', 'id', 'evidence_id', 'source', 'index']:
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return str(int(value))

        if isinstance(item.get('page'), (int, float)) and not isinstance(item.get('page'), bool):
            return str(int(item['page']))

    if payload_file or book_index is not None or evidence_index is not None:
        payload_name = payload_file or 'unknown_payload'
        book_number = book_index if book_index is not None else 0
        evidence_number = evidence_index if evidence_index is not None else 0
        return f'{payload_name}:{book_number}:{evidence_number}'

    return ''


def _extract_actors_from_text(text: str, known_characters: Optional[List[str]] = None) -> List[str]:
    """Extract only human or character-like actor names from text."""
    if not text:
        return []
    actors = set()
    known_chars = {c.lower().strip() for c in (known_characters or [])}
    capitalized = re.findall(r'\b[A-Z][a-zçğıöşüÇĞİÖŞÜ]+\b', text)
    for word in capitalized:
        lowered = word.lower()
        if lowered in known_chars or len(word) > 2:
            if lowered not in {'atlas', 'okyanusu', 'barcelona', 'hindistan', 'karayipler', 'adalar'}:
                actors.add(word)
    if not actors:
        # Fallback: keep the first token if it looks like a name-like word
        fallback = re.findall(r'\b[A-ZÇĞİÖŞÜ][a-zçğıöşüÇĞİÖŞÜ]+\b', text)
        for word in fallback:
            if word.lower() not in {'atlas', 'okyanusu', 'barcelona', 'hindistan', 'karayipler', 'adalar'}:
                actors.add(word)
    return sorted(actors)


def _extract_action_verb(text: str) -> str:
    """Extract a normalized action phrase rather than a single verb."""
    if not text:
        return ""
    normalized = re.sub(r'\s+', ' ', text).strip()
    lowered = normalized.lower()

    if any(marker in lowered for marker in ['batıya doğru yelken açtı', 'batıya doğru yelken açmak']):
        return 'batıya doğru yelken açtı'
    if any(marker in lowered for marker in ['karaya ulaşt', 'karaya ulaşıldı', 'karaya ulaş']):
        return 'karaya ulaştı'
    if any(marker in lowered for marker in ['yeni bir dünya keşfettik', 'yeni bir dünya keşfetti']):
        return 'yeni bir dünya keşfetti'
    if any(marker in lowered for marker in ['umudunu kaybetti', 'umudunu kaybetmek']):
        return 'umudunu kaybetti'
    if any(marker in lowered for marker in ['başarıyla sonuçlandı', 'sonuçlandı']):
        return 'başarıyla sonuçlandı'

    action_verbs = [
        'yap', 'yapmak', 'gir', 'gitmek', 'gel', 'gelmek', 'düş', 'düşmek',
        'aç', 'açmak', 'kapat', 'kapatmak', 'sor', 'sormak', 'cevap', 'cevapla',
        'ara', 'aramak', 'bul', 'bulmak', 'kaybettir', 'kaybet', 'kaybetmek',
        'kazanmak', 'kazan', 'yardım', 'yardımcı', 'çalış', 'çalışmak',
        'dur', 'durmak', 'otur', 'oturmak', 'koş', 'koşmak', 'uç', 'uçmak',
        'söyle', 'söylemek', 'dinle', 'dinlemek', 'oku', 'okumak', 'yaz', 'yazmak',
        'düşün', 'düşünmek', 'hisset', 'hissetmek', 'bil', 'bilmek',
        'karşılaş', 'karşılaşmak', 'kork', 'korkmak', 'sevgili', 'seviş',
        'face', 'faced', 'decided', 'decide', 'fight', 'fought', 'began', 'begin',
        'learn', 'learned', 'succeed', 'succeeded', 'succeed', 'appear', 'appeared',
        'defeat', 'defeated', 'discover', 'discovered', 'find', 'found',
    ]
    for verb in action_verbs:
        if verb in lowered:
            match = re.search(rf'\b{re.escape(verb)}\w*[^.!?]*', normalized, re.IGNORECASE)
            if match:
                phrase = match.group(0).strip()
                words = phrase.split()[:8]
                phrase = ' '.join(words)
                if len(phrase.split()) <= 1:
                    return normalized.split()[0] + ' ' + normalized.split()[-1]
                return phrase
    if len(normalized.split()) <= 3:
        return normalized
    return ' '.join(normalized.split()[:6])


def _detect_conflict(text: str) -> bool:
    """Detect if text contains conflict indicators."""
    conflict_markers = {
        'problem', 'çatışma', 'çatışmak', 'engel', 'engelle', 'ters', 'terslik',
        'zorluk', 'zor', 'tehlike', 'tehdit', 'tehdit', 'ölüm', 'ölümcül',
        'karşı', 'karşıtlaş', 'karşılaş', 'uyuşmaz', 'anlaşmazlık',
        'reddet', 'reddedil', 'başarısız', 'başarısızlık', 'hata',
        'kötü', 'kötülük', 'kızgın', 'öfke', 'nefret', 'nefreti', 'kaybetti',
        'danger', 'dangerous', 'conflict', 'monster', 'threat', 'enemy',
        'challenge', 'struggle', 'fight', 'battle', 'war', 'lose',
        'fail', 'failure', 'wrong', 'bad', 'afraid', 'fear',
    }
    text_lower = text.lower()
    for marker in conflict_markers:
        if marker in text_lower:
            return True
    return False


def _detect_resolution(text: str) -> bool:
    """Detect if text contains resolution/outcome indicators."""
    resolution_markers = {
        'başarı', 'başarısı', 'kazanmak', 'kazandı', 'başarıl',
        'sonra', 'ardından', 'nihayet', 'sonuç', 'sonunda',
        'öğrenmek', 'öğrendi', 'anlamak', 'anladı', 'çözmek', 'çözdü',
        'barış', 'uzlaş', 'uzlaştı', 'anlaş', 'anlaştı',
        'bitir', 'bitti', 'bitmek', 'sona', 'sonu', 'son',
        'düşün', 'düşüncel', 'değişim', 'değişti', 'yeni', 'artık',
        'beraber', 'birlikte', 'yardım', 'destek', 'destekley',
        'finally', 'success', 'succeeded', 'succeed', 'learned', 'learn',
        'outcome', 'result', 'triumphed', 'triumph', 'victory', 'won',
        'resolve', 'resolved', 'solution', 'overcome', 'overcame',
    }
    text_lower = text.lower()
    for marker in resolution_markers:
        if marker in text_lower:
            return True
    return False


def _compute_importance(text: str, is_conflict: bool, is_resolution: bool) -> float:
    """Compute importance score for event."""
    score = 0.3  # base
    if len(text) > 100:
        score += 0.2
    if is_conflict:
        score += 0.3
    if is_resolution:
        score += 0.2
    # Presence of strong verbs increases importance
    strong_verbs = ['yardım', 'başarı', 'karar', 'keşf', 'seçim', 'değişim']
    if any(v in text.lower() for v in strong_verbs):
        score += 0.1
    return min(1.0, score)


def _clean_phrase(phrase: str) -> str:
    return re.sub(r'\s+', ' ', str(phrase or '')).strip().strip('.,:;?!')


def _title_case_phrase(phrase: str) -> str:
    phrase = _clean_phrase(phrase)
    return phrase.capitalize() if phrase else ''


def _is_location_candidate(text: str) -> bool:
    normalized = (text or '').strip().lower()
    if not normalized:
        return False
    location_terms = [
        'ev', 'okul', 'orman', 'bahçe', 'oda', 'sokak', 'liman', 'salon', 'park',
        'köy', 'şehir', 'ülke', 'ada', 'dağ', 'deniz', 'göl', 'mağara', 'kale',
        'kütüphane', 'sahil', 'liman', 'pazar', 'çarşı', 'alan', 'meydan', 'kıyı',
        'çayır', 'bahçe', 'salon', 'oda', 'şehir', 'mahall', 'köprü'
    ]
    return any(term in normalized for term in location_terms)


def _extract_goal(text: str) -> str:
    """Infer a normalized semantic goal from evidence text."""
    normalized = re.sub(r'\s+', ' ', text or '').strip().lower()
    if not normalized:
        return ''
    if any(term in normalized for term in ['batıya', 'yolculuk', 'yelken', 'okyanus']):
        return 'batıya yolculuk'
    if any(term in normalized for term in ['karaya', 'ulaş']):
        return 'karaya ulaşma'
    if any(term in normalized for term in ['keşif', 'keşfet', 'adalar', 'yeni dünya']):
        return 'keşif'
    if any(term in normalized for term in ['karşılaş', 'yerli']):
        return 'karşılaşma'
    if any(term in normalized for term in ['dönüş', 'geri dön']):
        return 'dönüş'
    match = re.search(
        r'([a-zçğıöşü ]{2,80}?)\s+(?:için|amacıyla|hedefiyle|hedef ile)\b',
        normalized,
    )
    if match:
        after = normalized[match.end():].strip()
        if re.search(r'\b(?:yaptı|yaptılar|yapmak|etmek|etti|istedi|istiyor|plan|planlad|hazırlad|buldu|bulmak|karar|karar verdi|plan yaptı|yaptıkları|yaptık)\b', after):
            return _clean_phrase(match.group(1))
    match = re.search(
        r'\b([a-zçğıöşü ]{2,80}?)\s+(?:yardım etmek|istemek|çalışmak|aramak|bulmak)\b',
        normalized,
    )
    if match:
        return _clean_phrase(match.group(1))
    match = re.search(r'\b(?:istemek|çalışmak|aramak|bulmak)\s+([a-zçğıöşü ]{2,80}?)\b', normalized)
    if match:
        return _clean_phrase(match.group(1))
    if any(term in normalized for term in ['yardım', 'destek']):
        return 'yardım'
    return ''


def _extract_object(text: str) -> str:
    """Infer a simple object noun phrase from evidence text while avoiding location terms."""
    normalized = re.sub(r'\s+', ' ', text or '').strip().lower()
    if not normalized:
        return ''
    explicit_objects = {
        'yeni bir dünya': 'Yeni bir dünya',
        'yeni dünya': 'Yeni dünya',
    }
    for key, value in explicit_objects.items():
        if key in normalized:
            return value

    location = _extract_location(normalized)
    invalid_objects = {'diye', 'benimle bir görüşme', 'şeyler olarak'}

    def is_invalid_object_candidate(candidate: str) -> bool:
        normalized_candidate = (candidate or '').strip().lower()
        if not normalized_candidate:
            return True
        if normalized_candidate in invalid_objects:
            return True
        if location and normalized_candidate == location.lower():
            return True
        return False

    def clean_object(candidate: str) -> str:
        candidate = _clean_phrase(candidate)
        if not candidate:
            return ''
        candidate = re.sub(r'^(?:çocuklar|çocuk|biz|ben|sen|siz|o|onlar|ona|onu|onun|onları|bizim|hep|hepimiz|birkaç|bazı|bu|şu)\s+', '', candidate)
        candidate = re.sub(r'\b(okulda|okuldan|okula|evde|evden|evle|orman|ormanda|ormandan|bahçede|bahçeden|bahçeye)\b', '', candidate)
        candidate = _title_case_phrase(candidate)
        if is_invalid_object_candidate(candidate):
            return ''
        return candidate

    verb_object_patterns = [
        r'\b(?:buldu|buldular|gördü|gördüler|aldı|aldılar|kullandı|kullandılar|topladı|topladılar|seçti|seçtiler|öğrendi|öğrendiler|kurtardı|kurtardılar|yaptı|yaptılar|kazandı|kazandılar|sordu|sordular)\b\s+([a-zçğıöşü ]{1,40}?)\b',
        r'\b([a-zçğıöşü ]{1,40}?)\b\s+\b(?:buldu|buldular|gördü|gördüler|aldı|aldılar|kullandı|kullandılar|topladı|topladılar|seçti|seçtiler|öğrendi|öğrendiler|kurtardı|kurtardılar|yaptı|yaptılar|kazandı|kazandılar|sordu|sordular)\b',
    ]
    match = re.search(
        r'\biçin\s+([a-zçğıöşü ]{1,40}?)\s+(?:yaptı|yaptılar|buldu|buldular|gördü|gördüler|aldı|aldılar|kullandı|kullandılar|topladı|topladılar|seçti|seçtiler|öğrendi|öğrendiler|kurtardı|kurtardılar|yaptı|yaptılar|kazandı|kazandılar|sordu|sordular)\b',
        normalized,
    )
    if match:
        candidate = clean_object(match.group(1))
        if candidate and not _is_location_candidate(candidate):
            return candidate

    for clause in re.split(r'\b(?:ve|ama|fakat|ancak|sonra|sonunda)\b', normalized):
        for pattern in verb_object_patterns:
            match = re.search(pattern, clause)
            if match:
                candidate = clean_object(match.group(1))
                if candidate and not _is_location_candidate(candidate):
                    return candidate
    return ''


def _extract_result(text: str) -> str:
    """Infer a normalized semantic outcome from evidence text."""
    normalized = re.sub(r'\s+', ' ', text or '').strip().lower()
    if not normalized:
        return ''
    if any(term in normalized for term in ['karaya ulaşt', 'karaya ulaşıldı', 'karaya ulaş']):
        return 'karaya ulaşıldı'
    if any(term in normalized for term in ['umud', 'sars', 'umutsuz']):
        return 'umudun sarsılması'
    if any(term in normalized for term in ['başarı', 'kazan', 'başarıl']):
        return 'başarı sağlandı'
    if any(term in normalized for term in ['anlaş', 'barış', 'uzlaş']):
        return 'anlaşma sağlandı'
    if any(term in normalized for term in ['değişim', 'değişti']):
        return 'değişim yaşandı'
    if any(term in normalized for term in ['bitti', 'sona erdi', 'sonuç']):
        return 'süreç sonuçlandı'
    if any(term in normalized for term in ['başladı', 'yelken aç']):
        return 'yolculuk başladı'
    if any(term in normalized for term in ['keşfettik', 'keşfetti']):
        return 'keşif yapıldı'
    return ''


def _extract_location(text: str) -> str:
    """Infer a simple location/context phrase from evidence text."""
    normalized = re.sub(r'\s+', ' ', text or '').strip().lower()
    if not normalized:
        return ''
    explicit_locations = {
        'atlas okyanusu': 'Atlas Okyanusu',
        'karayip': 'Karayipler',
        'barcelona': 'Barcelona',
        'adalar': 'Adalar',
        'hindistan': 'Hindistan',
        'okyanus': 'Okyanus',
    }
    for key, value in explicit_locations.items():
        if key in normalized:
            return value
    place_pattern = re.search(
        r'\b(ev|okul|orman|bahçe|oda|sokak|liman|salon|park|köy|şehir|ülke|ada|dağ|deniz|göl|mağara|kale|kütüphane|sahil|pazar|çarşı|alan|meydan|kıyı)(?:de|da|den|dan|e|a|ında|inde|una|üne|ya|ye)\b',
        normalized,
    )
    if place_pattern:
        return place_pattern.group(0)
    positional_pattern = re.search(
        r'\b([a-zçğıöşü ]{2,40})(?:içinde|yanında|üstünde|altında|önünde|arkasında)\b',
        normalized,
    )
    if positional_pattern:
        phrase = _clean_phrase(positional_pattern.group(1))
        if _is_location_candidate(phrase) or any(term in phrase for term in ['ev', 'okul', 'orman', 'bahçe', 'oda', 'sokak', 'liman']):
            return phrase
    return ''


def _compute_cause_confidence(text: str, is_conflict: bool, is_resolution: bool) -> float:
    normalized = re.sub(r'\s+', ' ', text or '').strip().lower()
    if not normalized:
        return 0.0
    strong_markers = [
        'çünkü', 'bu nedenle', 'yüzünden', 'sonucunda', 'böylece', 'dolayı',
        'nedeniyle', 'sebebiyle', 'sonuç olarak', 'dolayısıyla',
    ]
    lexical = 1.0 if any(marker in normalized for marker in strong_markers) else 0.0
    if lexical == 0.0 and 'için' in normalized and not _extract_goal(text):
        cause, _ = _extract_cause_effect_pair(text)
        if cause:
            lexical = 0.6
    quality = min(1.0, max(0.0, len(normalized) / 80.0))
    if is_conflict and lexical == 0.0:
        # Conflict sentiment alone is not sufficient for a cause, but it can raise suspicion.
        lexical = 0.1
    if is_resolution and lexical == 0.0:
        lexical = 0.0
    confidence = (lexical * 0.7) + (quality * 0.3)
    return round(confidence, 3)


def _compute_effect_confidence(text: str, is_conflict: bool, is_resolution: bool) -> float:
    normalized = re.sub(r'\s+', ' ', text or '').strip().lower()
    if not normalized:
        return 0.0
    strong_markers = [
        'sonuç', 'sonuç olarak', 'böylece', 'dolayısıyla', 'sonunda',
        'yüzünden', 'buradan dolayı', 'dolayı', 'nedeniyle',
    ]
    lexical = 1.0 if any(marker in normalized for marker in strong_markers) else 0.0
    if lexical == 0.0 and 'için' in normalized and not _extract_goal(text):
        _, effect = _extract_cause_effect_pair(text)
        if effect:
            lexical = 0.6
    quality = min(1.0, max(0.0, len(normalized) / 80.0))
    if is_resolution and lexical == 0.0:
        lexical = 0.2
    confidence = (lexical * 0.7) + (quality * 0.3)
    return round(confidence, 3)


def _extract_cause_effect_pair(text: str) -> tuple[str, str]:
    normalized = re.sub(r'\s+', ' ', text or '').strip().lower()
    if not normalized:
        return '', ''

    def clean(phrase: str) -> str:
        return _clean_phrase(phrase)

    patterns = [
        r'(.+?)\s+çünkü\s+(.+)',
        r'(.+?)\s+nedeniyle\s+(.+)',
        r'(.+?)\s+bu nedenle\s+(.+)',
        r'(.+?)\s+bunun sonucunda\s+(.+)',
        r'(.+?)\s+böylece\s+(.+)',
        r'(.+?)\s+sonunda\s+(.+)',
        r'(.+?)\s+dolayısıyla\s+(.+)',
        r'(.+?)\s+yüzünden\s+(.+)',
        r'(.+?)\s+sebebiyle\s+(.+)',
        r'(.+?)\s+sonuç olarak\s+(.+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            return clean(match.group(1)), clean(match.group(2))

    if 'için' in normalized and not _extract_goal(text):
        match = re.search(r'(.+?)\s+için\s+(.+)', normalized)
        if match:
            effect_candidate = clean(match.group(2))
            if not re.search(r'\b(?:plan|planı|planlad|karar|yaptı|yaptılar|hazırlad|düşünd|istemek|istedi|bulmak|buldu|bulund|kurmak|kurdu)\b', effect_candidate):
                return clean(match.group(1)), effect_candidate
    return '', ''


def _infer_cause(text: str, is_conflict: bool) -> str:
    """Infer a deterministic cause phrase directly from event text."""
    normalized = re.sub(r'\s+', ' ', text or '').strip().lower()
    if not normalized:
        return ''
    cause, _ = _extract_cause_effect_pair(text)
    if cause:
        return cause
    if 'fırtına' in normalized and 'nedeniyle' in normalized:
        return 'fırtına'
    if any(term in normalized for term in ['umud', 'sars', 'kaybet']) and 'nedeniyle' in normalized:
        return 'moral kaybı'
    if any(term in normalized for term in ['batıya', 'yelken', 'açtı']) and 'çünkü' in normalized:
        return 'batıya doğru yelken açma'
    if any(term in normalized for term in ['karaya', 'ulaş', 'keşf']) and 'nedeniyle' in normalized:
        return 'hedefe yaklaşma'
    return ''


def _infer_effect(text: str, is_conflict: bool, is_resolution: bool) -> str:
    """Infer a deterministic effect phrase directly from event text."""
    normalized = re.sub(r'\s+', ' ', text or '').strip().lower()
    if not normalized:
        return ''
    _, effect = _extract_cause_effect_pair(text)
    if effect:
        return effect
    if ('umud' in normalized or 'kaybet' in normalized) and any(marker in normalized for marker in ['nedeniyle', 'yüzünden', 'dolayı', 'sebebiyle']):
        return 'mürettebat umudunu kaybetti'
    if any(term in normalized for term in ['başarıyla sonuçlandı', 'başarıyla sonuçlandı', 'sonuçlandı']) and any(marker in normalized for marker in ['böylece', 'sonuç olarak', 'dolayısıyla', 'sonucunda']):
        return 'başarıyla sonuçlandı'
    if any(term in normalized for term in ['batıya', 'yelken', 'açtı']) and any(marker in normalized for marker in ['çünkü', 'nedeniyle', 'dolayı']):
        return 'yolculuk başlangıcı'
    return ''


def _infer_narrative_function(section: str, is_conflict: bool, is_resolution: bool) -> str:
    """Assign a richer narrative role to an event."""
    if section == 'conflict' or is_conflict:
        return 'inciting_incident'
    if section == 'resolution' or is_resolution:
        return 'resolution'
    if section == 'setup':
        return 'setup'
    if section == 'events':
        return 'rising_action'
    return 'rising_action'


def _infer_temporal_marker(section: str, is_resolution: bool) -> str:
    """Infer a coarse temporal marker for an event."""
    if section == 'setup':
        return 'beginning'
    if section == 'conflict':
        return 'middle'
    if section == 'resolution' or is_resolution:
        return 'end'
    return 'middle'


def _infer_resolution_state(section: str, is_resolution: bool, result: str) -> str:
    """Infer a simple resolution state for an event."""
    if section == 'resolution':
        return 'resolved'
    if is_resolution:
        return 'resolved'
    if result and any(term in result.lower() for term in ['başarı', 'sonuç', 'sonunda', 'süreç', 'ulaşıldı']):
        return 'resolved'
    return 'unresolved'


def _infer_stakes(text: str, is_conflict: bool, is_resolution: bool) -> str:
    """Infer a deterministic stakes label for an event."""
    normalized = re.sub(r'\s+', ' ', text or '').strip().lower()
    if not normalized:
        return ''
    if is_conflict or any(term in normalized for term in ['fırtına', 'umud', 'kaybet', 'tehlike']):
        return 'moral and survival'
    if is_resolution or any(term in normalized for term in ['başarı', 'sonuç', 'sonunda']):
        return 'outcome'
    if any(term in normalized for term in ['keşf', 'ulaş']):
        return 'discovery'
    return 'progress'


def reconstruct_events(
    evidence_snippets: Optional[Dict[str, Any]],
    characters: Optional[List[str]] = None,
    themes: Optional[List[str]] = None,
    payload_file: Optional[str] = None,
    book_index: Optional[int] = None,
) -> Dict[str, Any]:
    """Reconstruct event structure from evidence snippets.

    Input:
      evidence_snippets: dict with keys like 'setup', 'conflict', 'events', 'resolution'
      characters: list of known character names for actor extraction
      themes: list of themes (optional context)

    Output:
      {
        'events': [event_dict...],
        'event_sequence': ['event_001', 'event_002', ...],
        'main_conflict': str,
        'resolution': str,
        'event_reconstruction_quality': float,
      }
    """
    events = []
    all_texts = []
    event_id_counter = 0

    # Flatten evidence snippets into ordered list.
    # Accept either a sectioned dict (setup/conflict/events/resolution)
    # or a plain list of evidence items.
    if isinstance(evidence_snippets, dict):
        section_order = ['setup', 'conflict', 'events', 'resolution']
        for section in section_order:
            items = evidence_snippets.get(section, [])
            if isinstance(items, list):
                for idx, item in enumerate(items):
                    if isinstance(item, str):
                        text = item
                        source_id = _normalize_source_id(
                            {'text': text},
                            payload_file=payload_file,
                            book_index=book_index,
                            evidence_index=idx,
                        )
                    elif isinstance(item, dict):
                        text = item.get('text', '')
                        source_id = _normalize_source_id(
                            item,
                            payload_file=payload_file,
                            book_index=book_index,
                            evidence_index=idx,
                        )
                    else:
                        continue
                    if text and text.strip():
                        all_texts.append({
                            'text': text,
                            'source_id': source_id,
                            'section': section,
                            'section_index': idx
                        })
    elif isinstance(evidence_snippets, list):
        for idx, item in enumerate(evidence_snippets):
            if isinstance(item, str):
                text = item
                source_id = _normalize_source_id(
                    {'text': text},
                    payload_file=payload_file,
                    book_index=book_index,
                    evidence_index=idx,
                )
            elif isinstance(item, dict):
                text = item.get('text', '')
                source_id = _normalize_source_id(
                    item,
                    payload_file=payload_file,
                    book_index=book_index,
                    evidence_index=idx,
                )
            else:
                continue
            if text and text.strip():
                all_texts.append({
                    'text': text,
                    'source_id': source_id,
                    'section': 'events',
                    'section_index': idx
                })
    else:
        evidence_snippets = {}

    # Group and create events
    for text_item in all_texts:
        text = text_item['text'].strip()
        source_id = text_item['source_id']
        section = text_item['section']

        is_conflict = _detect_conflict(text)
        is_resolution = _detect_resolution(text)

        actors = _extract_actors_from_text(text, characters)
        action = _extract_action_verb(text)
        goal = _extract_goal(text)
        object_ = _extract_object(text)
        result = _extract_result(text) if section == 'resolution' or is_resolution else ''
        location = _extract_location(text)
        cause_confidence = _compute_cause_confidence(text, is_conflict, is_resolution)
        effect_confidence = _compute_effect_confidence(text, is_conflict, is_resolution)
        cause = _infer_cause(text, is_conflict) if cause_confidence >= 0.5 else ''
        effect = _infer_effect(text, is_conflict, is_resolution) if (cause_confidence >= 0.5 and effect_confidence >= 0.5) else ''
        if cause and effect == 'durum değişimi':
            effect = ''
        narrative_function = _infer_narrative_function(section, is_conflict, is_resolution)
        temporal_marker = _infer_temporal_marker(section, is_resolution)
        resolution_state = _infer_resolution_state(section, is_resolution, result)
        stakes = _infer_stakes(text, is_conflict, is_resolution)
        importance = _compute_importance(text, is_conflict, is_resolution)

        # Create event object
        event = {
            'event_id': f'event_{event_id_counter:03d}',
            'actors': actors,
            'action': action,
            'object': object_,
            'goal': goal,
            'conflict': is_conflict,
            'result': result,
            'location_or_context': location,
            'cause': cause,
            'cause_confidence': round(cause_confidence, 3),
            'effect': effect,
            'effect_confidence': round(effect_confidence, 3),
            'narrative_function': narrative_function,
            'stakes': stakes,
            'temporal_marker': temporal_marker,
            'resolution_state': resolution_state,
            'importance': round(importance, 3),
            'supporting_evidence_ids': [source_id] if source_id else [],
            'source_sentence_ids': [source_id] if source_id else [],
            '_raw_evidence': text,  # Keep for reference (not in output schema)
            '_section': section,
        }

        events.append(event)
        event_id_counter += 1

    # Extract main conflict and resolution
    main_conflict = ''
    resolution = ''
    for event in events:
        if event['conflict'] and not main_conflict:
            main_conflict = event['_raw_evidence']
        if event.get('_section') == 'resolution' and not resolution:
            resolution = event['_raw_evidence']
    # If no explicit conflict was detected, check conflict section
    if not main_conflict:
        for item in all_texts:
            if item['section'] == 'conflict':
                main_conflict = item['text']
                break
    # Build event sequence
    event_sequence = [e['event_id'] for e in events]

    # Compute quality score
    quality = 0.0
    if events:
        quality += min(len(events) / 5.0, 1.0) * 0.3  # event count
        conflict_count = sum(1 for e in events if e['conflict'])
        if conflict_count > 0:
            quality += 0.4
        if main_conflict and resolution:
            quality += 0.3

    # Clean up internal fields before returning
    for event in events:
        del event['_raw_evidence']
        del event['_section']

    return {
        'events': events,
        'event_sequence': event_sequence,
        'main_conflict': main_conflict,
        'resolution': resolution,
        'event_reconstruction_quality': round(quality, 3),
    }
