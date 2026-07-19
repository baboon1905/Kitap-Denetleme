"""
Profesyonel İçerik Denetim Uzmanı - 6 Aşamalı Değerlendirme Sistemi
Çocuk Kitapları ve Gençlik Yayınları İçin

DEĞERLENDIRME KURALARI:
1. Kelime bağımsız mı? (gerçek kelime mi, substring mi?)
2. Başka kelimenin içinde mi? (substring bulgusu = geçersiz)
3. Cümlenin anlamı nedir? (bağlam analizi)
4. Kullanım tipi nedir? (olumlu, olumsuz, nötr, eğitsel, tarihsel, mecazi, özendirici)
5. Çocuk okuyucu üzerinde olumsuz etki oluşturuyor mu?
6. Risk puanını ver (Maarif/MEB/Hibrit profiline göre)

TEMEL PRENSIPLER:
- Kelime eşleşmesi tek başına risk değildir
- Bağlam her zaman kelimeden daha önemlidir
- Tarihsel anlatımlar otomatik olarak riskli değildir
- Eğitsel açıklamalar riskli değildir
- Mecazi kullanımlar riskli değildir
- Substring bulguları geçersizdir
- Problem olmayan bulgular 0 risk puanına sahiptir
"""

import re
from typing import Dict, List, Tuple, Optional
from enum import Enum
import json


class ContextType(Enum):
    """Kullanım Bağlamı Türleri"""
    POSITIVE = "olumlu"
    NEGATIVE = "olumsuz"
    NEUTRAL = "nötr"
    EDUCATIONAL = "eğitsel"
    HISTORICAL = "tarihsel"
    METAPHORICAL = "mecazi"
    ENCOURAGING = "özendirici"


class RiskLevel(Enum):
    """Risk Seviyeleri (0-5)"""
    NONE = 0
    MINIMAL = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    CRITICAL = 5


class ProfessionalContentEvaluator:
    """6 Aşamalı Profesyonel İçerik Denetim Sistemi"""
    
    def __init__(self):
        self.context_keywords = self._load_context_keywords()
        self.risk_keywords = self._load_risk_keywords()
        self.profile_weights = self._load_profile_weights()
        
    def _load_context_keywords(self) -> Dict:
        """Bağlam türlerini tanımlayan anahtar kelimeler"""
        return {
            ContextType.EDUCATIONAL: [
                'öğren', 'dersin', 'ders', 'bilgi', 'anlat', 'açıkla', 'örnek',
                'tarih', 'sosyal', 'sınıf', 'okul', 'eğit', 'rehber', 'denetim'
            ],
            ContextType.HISTORICAL: [
                'tarih', 'geçmiş', 'dönemi', 'daha', 'eskiden', 'eski', 'zamanında',
                '1800', '1900', 'yüzyıl', 'osmanlı', 'cumhuriyet', 'antik'
            ],
            ContextType.METAPHORICAL: [
                'gibi', 'benzer', 'sahip', 'görünüşlü', 'adeta', 'sanki', 'değilmiş',
                'mış gibi', 'ye benziyor', 'diye adlandırılıyor'
            ],
            ContextType.ENCOURAGING: [
                'cesur', 'güçlü', 'başarılı', 'madalya', 'kahramanlık', 'fedai',
                'vatan', 'millet', 'kurtuluş', 'zafer', 'başarı', 'başar'
            ]
        }
    
    def _load_risk_keywords(self) -> Dict:
        """Risk kategorileri ve ilişkili kelimeler"""
        return {
            'siddət': ['vurmak', 'dövmek', 'çarpmak', 'tokat', 'yumruk', 'bıçak', 'kesme'],
            'cinsellik': ['çıplak', 'mahrem', 'taciz', 'tecavüz', 'pornografi', 'fuhuş'],
            'zararlı_alışkanlıklar': ['sigara', 'tütün', 'duman', 'alkol', 'içki', 'uyuşturucu'],
            'kaba_dil': ['küfür', 'hakaret', 'aşağılama', 'bağırma', 'çirkinlik'],
            'ayırımcılık': ['ırkçılık', 'ayrımcılık', 'nefret', 'ötekileştirme', 'cinsiyetçi'],
            'korku_travma': ['ölüm', 'cehennem', 'kan', 'infaz', 'işkence', 'acı çekme'],
            'okültizm': ['sihir', 'büyü', 'fal', 'cin', 'şeytan', 'batıl inanç'],
            'dijital_risk': ['cyberbullying', 'hazır para', 'kripto', 'manipülasyon'],
            'olumsuz_davranış': ['yalan', 'hırsızlık', 'sabotaj', 'şiddət', 'ihanet']
        }
    
    def _load_profile_weights(self) -> Dict:
        """Profil ağırlıkları"""
        return {
            'maarif': {
                'name': 'Maarif/MEB',
                'weights': {
                    'siddət': 1.3,
                    'cinsellik': 1.4,
                    'zararlı_alışkanlıklar': 1.3,
                    'kaba_dil': 1.1,
                    'ayırımcılık': 1.2,
                    'korku_travma': 1.1,
                    'okültizm': 1.1,
                    'dijital_risk': 1.0,
                    'olumsuz_davranış': 1.2
                }
            },
            'meb': {
                'name': 'MEB Standart',
                'weights': {
                    'siddət': 1.2,
                    'cinsellik': 1.3,
                    'zararlı_alışkanlıklar': 1.2,
                    'kaba_dil': 1.0,
                    'ayırımcılık': 1.1,
                    'korku_travma': 1.0,
                    'okültizm': 1.0,
                    'dijital_risk': 0.9,
                    'olumsuz_davranış': 1.1
                }
            },
            'hybrid': {
                'name': 'Hibrit',
                'weights': {
                    'siddət': 1.0,
                    'cinsellik': 1.0,
                    'zararlı_alışkanlıklar': 1.0,
                    'kaba_dil': 0.9,
                    'ayırımcılık': 1.0,
                    'korku_travma': 0.9,
                    'okültizm': 0.9,
                    'dijital_risk': 0.9,
                    'olumsuz_davranış': 1.0
                }
            }
        }
    
    def evaluate_word(self, word: str, context: str, profile: str = 'hybrid') -> Dict:
        """
        BİR KELİMEYİ 6 AŞAMADA DEĞERLENDİR
        
        Args:
            word: Değerlendirilecek kelime
            context: Kelimenin kullanıldığı cümle/paragraf
            profile: Profil (maarif, meb, hybrid)
        
        Returns:
            dict: 6 aşamalı detaylı değerlendirme sonucu
        """
        
        evaluation = {
            'word': word,
            'context': context,
            'profile': profile,
            'steps': {}
        }
        
        # ADIM 1: Kelime bağımsız mı?
        evaluation['steps']['1_independence'] = self._step1_check_independence(word, context)
        
        # Eğer kelime bağımsız değilse, direkt olarak geçersiz bulgu
        if not evaluation['steps']['1_independence']['is_independent']:
            evaluation['is_valid_finding'] = False
            evaluation['risk_score'] = 0
            evaluation['risk_level'] = 'YOKSUN'
            evaluation['reason'] = f"Substring bulgusu: {evaluation['steps']['1_independence']['reason']}"
            evaluation['steps']['2_substring_check'] = {'is_substring': False}
            evaluation['steps']['3_sentence_meaning'] = {'sentiment': 'neutral', 'meaning': 'Değerlendirilemedi'}
            evaluation['steps']['4_context_type'] = {'type': 'nötr', 'confidence': 0}
            evaluation['steps']['5_negative_impact'] = {'has_negative_impact': False, 'reason': 'Bağımsız kelime değil'}
            evaluation['steps']['6_risk_scoring'] = {'risk_score': 0, 'risk_level': 'YOKSUN', 'reason': 'Kelime bağımsız değil'}
            return evaluation
        
        # ADIM 2: Başka kelimenin içinde mi?
        evaluation['steps']['2_substring_check'] = self._step2_check_substring(word, context)
        
        if evaluation['steps']['2_substring_check']['is_substring']:
            evaluation['is_valid_finding'] = False
            evaluation['risk_score'] = 0
            evaluation['risk_level'] = 'YOKSUN'
            evaluation['reason'] = f"Başka kelimenin içinde: {evaluation['steps']['2_substring_check']['parent_word']}"
            evaluation['steps']['3_sentence_meaning'] = {'sentiment': 'neutral', 'meaning': 'Değerlendirilemedi'}
            evaluation['steps']['4_context_type'] = {'type': 'nötr', 'confidence': 0}
            evaluation['steps']['5_negative_impact'] = {'has_negative_impact': False, 'reason': 'Substring bulgusu'}
            evaluation['steps']['6_risk_scoring'] = {'risk_score': 0, 'risk_level': 'YOKSUN', 'reason': 'Substring bulgusu'}
            return evaluation
        
        # ADIM 3: Cümlenin anlamı nedir?
        evaluation['steps']['3_sentence_meaning'] = self._step3_analyze_meaning(context)
        
        # ADIM 4: Kullanım tipi nedir?
        evaluation['steps']['4_context_type'] = self._step4_determine_context(word, context)
        
        # ADIM 5: Çocuk okuyucu üzerinde olumsuz etki?
        evaluation['steps']['5_negative_impact'] = self._step5_assess_impact(
            word, context, evaluation['steps']['4_context_type']['type']
        )
        
        # ADIM 6: Risk puanı (profil özelinde)
        evaluation['steps']['6_risk_scoring'] = self._step6_calculate_risk(
            word, context, evaluation['steps']['4_context_type']['type'],
            evaluation['steps']['5_negative_impact']['has_negative_impact'],
            profile
        )
        
        # FINAL KARAR
        evaluation['is_valid_finding'] = evaluation['steps']['5_negative_impact']['has_negative_impact']
        evaluation['risk_score'] = evaluation['steps']['6_risk_scoring']['risk_score']
        evaluation['risk_level'] = evaluation['steps']['6_risk_scoring']['risk_level']
        evaluation['reason'] = evaluation['steps']['6_risk_scoring']['reason']
        
        return evaluation
    
    def _step1_check_independence(self, word: str, context: str) -> Dict:
        """ADIM 1: Kelime gerçekten bağımsız bir kelime mi?"""
        word_lower = word.lower()
        context_lower = context.lower()
        
        # Kelimenin tüm oluşumlarını bul
        occurrences = self._find_word_occurrences(word_lower, context_lower)
        
        if not occurrences:
            return {
                'is_independent': False,
                'reason': 'Kelime metinde bulunamadı'
            }
        
        # İlk oluşumu kontrol et
        first_occurrence = occurrences[0]
        start, end = first_occurrence
        
        # Kelimeden önceki ve sonraki karakterleri kontrol et
        prev_char = context_lower[start - 1] if start > 0 else ' '
        next_char = context_lower[end] if end < len(context_lower) else ' '
        
        # Türkçe harf kontrolü
        is_preceded_by_letter = prev_char.isalpha() and prev_char not in ' \n\t'
        is_followed_by_letter = next_char.isalpha() and next_char not in ' \n\t'
        
        is_independent = not (is_preceded_by_letter or is_followed_by_letter)
        
        return {
            'is_independent': is_independent,
            'occurrences_found': len(occurrences),
            'reason': 'Bağımsız kelime' if is_independent else f'Başında/sonunda harf var: {prev_char}{word_lower}{next_char}'
        }
    
    def _step2_check_substring(self, word: str, context: str) -> Dict:
        """ADIM 2: Kelime başka bir kelimenin içinde mi?"""
        word_lower = word.lower()
        context_lower = context.lower()
        
        # Kelimenin çevresini analiz et
        occurrences = self._find_word_occurrences(word_lower, context_lower)
        
        if not occurrences:
            return {'is_substring': False}
        
        first_occurrence = occurrences[0]
        start, end = first_occurrence
        
        prev_char = context_lower[start - 1] if start > 0 else ' '
        next_char = context_lower[end] if end < len(context_lower) else ' '
        
        # Eğer her iki tarafta da harf varsa, bir kelimenin parçasıdır
        is_substring = prev_char.isalpha() and next_char.isalpha()
        
        if is_substring:
            # Üst kelimeyi bul
            parent_start = start
            while parent_start > 0 and context_lower[parent_start - 1].isalpha():
                parent_start -= 1
            
            parent_end = end
            while parent_end < len(context_lower) and context_lower[parent_end].isalpha():
                parent_end += 1
            
            parent_word = context_lower[parent_start:parent_end]
            return {
                'is_substring': True,
                'parent_word': parent_word,
                'finding_invalid': True
            }
        
        return {'is_substring': False}
    
    def _step3_analyze_meaning(self, context: str) -> Dict:
        """ADIM 3: Cümlenin anlamı nedir?"""
        # Basit sentiment analizi
        positive_words = ['iyi', 'güzel', 'merhametli', 'cesur', 'akıllı', 'bilge',
                         'bilgili', 'saygılı', 'dürüst', 'yardımcı']
        negative_words = ['kötü', 'şiddet', 'nefes', 'kin', 'nefret', 'kölelik',
                         'ezme', 'çekme', 'işkence']
        
        context_lower = context.lower()
        
        pos_count = sum(1 for w in positive_words if w in context_lower)
        neg_count = sum(1 for w in negative_words if w in context_lower)
        
        if pos_count > neg_count:
            sentiment = 'positive'
        elif neg_count > pos_count:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'positive_words': pos_count,
            'negative_words': neg_count,
            'meaning': f"Cümle genel olarak {sentiment} anlamlıdır"
        }
    
    def _step4_determine_context(self, word: str, context: str) -> Dict:
        """ADIM 4: Kelime olumlu, olumsuz, nötr, eğitsel, tarihsel, mecazi veya özendirici bağlamda mı?"""
        context_lower = context.lower()
        word_lower = word.lower()
        
        context_type = ContextType.NEUTRAL
        confidence = 0.5
        indicators = []
        
        # Tarihsel bağlam kontrol et
        for keyword in self.context_keywords[ContextType.HISTORICAL]:
            if keyword in context_lower:
                context_type = ContextType.HISTORICAL
                confidence = 0.9
                indicators.append(f"Tarihsel anahtar: {keyword}")
                break
        
        # Eğitsel bağlam kontrol et
        if context_type == ContextType.NEUTRAL:
            for keyword in self.context_keywords[ContextType.EDUCATIONAL]:
                if keyword in context_lower:
                    context_type = ContextType.EDUCATIONAL
                    confidence = 0.9
                    indicators.append(f"Eğitsel anahtar: {keyword}")
                    break
        
        # Mecazi bağlam kontrol et
        if context_type == ContextType.NEUTRAL:
            for keyword in self.context_keywords[ContextType.METAPHORICAL]:
                if keyword in context_lower:
                    context_type = ContextType.METAPHORICAL
                    confidence = 0.85
                    indicators.append(f"Mecazi anahtar: {keyword}")
                    break
        
        # Özendirici bağlam kontrol et
        if context_type == ContextType.NEUTRAL:
            for keyword in self.context_keywords[ContextType.ENCOURAGING]:
                if keyword in context_lower:
                    context_type = ContextType.ENCOURAGING
                    confidence = 0.8
                    indicators.append(f"Özendirici anahtar: {keyword}")
                    break
        
        return {
            'type': context_type.value,
            'confidence': confidence,
            'indicators': indicators
        }
    
    def _step5_assess_impact(self, word: str, context: str, context_type: str) -> Dict:
        """ADIM 5: Çocuk okuyucu üzerinde olumsuz etki oluşturuyor mu?"""
        
        # Tarihsel, eğitsel ve mecazi kullanımlar otomatik olarak olumsuz etki yaratmaz
        if context_type in ['tarihsel', 'eğitsel', 'mecazi']:
            return {
                'has_negative_impact': False,
                'reason': f"{context_type} bağlamda olumsuz etki yok",
                'safe_context': True
            }
        
        # Özendirici kullanımlar pozitif etkiye sahip
        if context_type == 'özendirici':
            return {
                'has_negative_impact': False,
                'reason': 'Özendirici bağlamda olumlu/nötr etki',
                'safe_context': True
            }
        
        # Diğer bağlamlarda kelime kategorisine göre karar ver
        context_lower = context.lower()
        
        # Koruma göstergesi kontrolü
        protective_words = ['değildir', 'kötü', 'yapılmaz', 'yanlış', 'hata', 'sakıncalı',
                           'yapılamaz', 'düşünmemeli', 'sakınmalı']
        
        has_protection = any(p in context_lower for p in protective_words)
        
        if has_protection:
            return {
                'has_negative_impact': False,
                'reason': 'Koruma göstergesi bulundu',
                'safe_context': True
            }
        
        return {
            'has_negative_impact': True,
            'reason': 'Doğrudan olumsuz kullanım',
            'safe_context': False
        }
    
    def _step6_calculate_risk(self, word: str, context: str, context_type: str,
                              has_negative_impact: bool, profile: str) -> Dict:
        """ADIM 6: Risk puanını hesapla (0-5 ölçeği, profil özelinde)"""
        
        # Eğer olumsuz etki yoksa, risk skoru kesinlikle 0
        if not has_negative_impact:
            return {
                'risk_score': 0,
                'risk_level': 'YOKSUN',
                'reason': 'Olumsuz etki yok - Risk skoru 0',
                'weighted_score': 0,
                'profile_weight': 1.0
            }
        
        word_lower = word.lower()
        base_risk = 1  # Varsayılan risk
        
        # Kategoriyi belirle
        category = 'other'
        for cat, keywords in self.risk_keywords.items():
            if any(k in word_lower or k in context.lower() for k in keywords):
                category = cat
                break
        
        # Risk kategorisine göre base risk'i ayarla
        risk_multipliers = {
            'cinsellik': 5,
            'siddət': 4,
            'ayırımcılık': 4,
            'okültizm': 3,
            'zararlı_alışkanlıklar': 3,
            'korku_travma': 3,
            'olumsuz_davranış': 2,
            'kaba_dil': 2,
            'dijital_risk': 2
        }
        
        base_risk = risk_multipliers.get(category, 1)
        
        # Profil ağırlığını uygula
        profile_data = self.profile_weights.get(profile, self.profile_weights['hybrid'])
        weight = profile_data['weights'].get(category, 1.0)
        
        # Final risk skoru (0-5)
        weighted_risk = min(5, base_risk * weight)
        
        # Risk seviyesini belirle
        if weighted_risk == 0:
            risk_level = 'YOKSUN'
        elif weighted_risk <= 1:
            risk_level = 'MİNİMAL'
        elif weighted_risk <= 2:
            risk_level = 'DÜŞÜK'
        elif weighted_risk <= 3:
            risk_level = 'ORTA'
        elif weighted_risk <= 4:
            risk_level = 'YÜKSEK'
        else:
            risk_level = 'CRİTİK'
        
        return {
            'risk_score': round(weighted_risk, 2),
            'risk_level': risk_level,
            'base_score': base_risk,
            'weighted_score': round(weighted_risk, 2),
            'profile_weight': weight,
            'category': category,
            'reason': f"{category}: Base {base_risk} × Weight {weight} = {weighted_risk}"
        }
    
    def _find_word_occurrences(self, word: str, text: str) -> List[Tuple[int, int]]:
        """Kelimenin metindeki tüm oluşumlarını bul (başlangıç, bitiş indeksleri)"""
        occurrences = []
        start = 0
        
        while True:
            pos = text.find(word, start)
            if pos == -1:
                break
            occurrences.append((pos, pos + len(word)))
            start = pos + 1
        
        return occurrences
    
    def evaluate_text(self, text: str, profile: str = 'hybrid') -> Dict:
        """Bir metni analiz et ve tüm bulguları değerlendir"""
        # Cümleleri ayır
        sentences = re.split(r'[.!?]', text)
        
        findings = []
        total_findings = 0
        problem_findings = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Her cümledeki risk kelimelerini kontrol et
            for category, keywords in self.risk_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in sentence.lower():
                        evaluation = self.evaluate_word(keyword, sentence, profile)
                        findings.append(evaluation)
                        total_findings += 1
                        
                        if evaluation['is_valid_finding']:
                            problem_findings += 1
        
        return {
            'profile': profile,
            'total_findings': total_findings,
            'problem_findings': problem_findings,
            'non_problem_count': total_findings - problem_findings,
            'findings': findings,
            'summary': {
                'problem_count': problem_findings,
                'non_problem_count': total_findings - problem_findings,
                'average_risk': round(sum(f['risk_score'] for f in findings) / len(findings) if findings else 0, 2)
            }
        }


# Test ve Demo
if __name__ == "__main__":
    evaluator = ProfessionalContentEvaluator()
    
    # Test örneği 1: Tarihsel bağlam
    test1 = evaluator.evaluate_word(
        word="kan",
        context="Kurtuluş Savaşı'nda çok kan dökülmüştür. Tarih dersinde bu önemli olay anlatılıyor.",
        profile="maarif"
    )
    print("\n=== TEST 1: Tarihsel Bağlam ===")
    print(json.dumps(test1, ensure_ascii=False, indent=2))
    
    # Test örneği 2: Substring
    test2 = evaluator.evaluate_word(
        word="lan",
        context="Havalandırma sistemini kontrol edin.",
        profile="maarif"
    )
    print("\n=== TEST 2: Substring ===")
    print(json.dumps(test2, ensure_ascii=False, indent=2))
    
    # Test örneği 3: Doğrudan risk
    test3 = evaluator.evaluate_word(
        word="sigara",
        context="Kahramanı sigara içerken görüyoruz.",
        profile="maarif"
    )
    print("\n=== TEST 3: Doğrudan Risk ===")
    print(json.dumps(test3, ensure_ascii=False, indent=2))
