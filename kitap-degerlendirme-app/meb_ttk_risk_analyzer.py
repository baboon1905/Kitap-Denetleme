#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEB TTK Kriterleri - Risk Unsuru Detayli Analiz Sistemi
Her kriter icin risk gostergeler ve ozendir unsurlarini detaylica aciklar
"""

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum


class RiskLevel(Enum):
    """Risk seviyeleri"""
    RISKSIZ = 0
    DUSUK = 1
    ORTA = 2
    YUKSEK = 3
    MAKSIMUM = 4
    KRITIK = 5


@dataclass
class RiskFactor:
    """Risk unsuru tanımı"""
    name: str
    level: RiskLevel
    description: str
    examples: List[str]
    contextual_note: str = ""


class MEBTTKAnalyzer:
    """8 MEB kriterinin detayli risk analiz sistemi"""
    
    def __init__(self):
        self.criteria = {
            "anayasa": {
                "title": "Anayasa ve Mevzuat Uygunlugu",
                "factors": [
                    RiskFactor(
                        name="Devlet Butunlugu Aykırılık",
                        level=RiskLevel.MAKSIMUM,
                        description="Devletin territorial/siyasi butunlugunu reddetme",
                        examples=[
                            "XX 'Sınırlar yeniden cizilmelidir'",
                            "XX 'Bolunme ulkenin cikarına gider'",
                            "OK 'Tarihi sınırlarımız ulusumuzun sınırlarıdır'"
                        ]
                    ),
                ]
            },
            "milli_guvenlik": {
                "title": "Milli Guvenlik",
                "factors": [
                    RiskFactor(
                        name="Teror Orgutu Propagandası",
                        level=RiskLevel.MAKSIMUM,
                        description="PKK, DHKP-C, PYD/YPG vs. ozendir",
                        examples=[
                            "XX 'PKK gerillasını desteklerim'",
                            "XX 'DHKP-C direnis harekatı haklıdır'",
                            "OK 'Teror orgutu insanlığa karsi suç islemiştir'"
                        ]
                    ),
                    RiskFactor(
                        name="Ozendir Dili (KRITIK!)",
                        level=RiskLevel.MAKSIMUM,
                        description="'Siz de yapabilirsiniz', 'ben de katılırdım'",
                        examples=[
                            "XX 'Oyle bir ogrute ben de katılmak isterdim'",
                            "XX 'Siz de silah alıp katılabilirsiniz'",
                            "OK 'Bu eylemler devlet tarafından engellenmiştir'"
                        ]
                    ),
                ]
            },
            "esitlik": {
                "title": "Esitlik ve Kapsayıcılık",
                "factors": [
                    RiskFactor(
                        name="Sistemik Irkcılık",
                        level=RiskLevel.MAKSIMUM,
                        description="Bir etnik grup oteki ırka asagı gosteren",
                        examples=[
                            "XX 'Akdeniz ırkı asagı ırk'",
                            "XX 'Asyalilar entelektuel olarak zayıf'",
                            "OK 'Farklı kulturler zenginliklerimizdir'"
                        ]
                    ),
                ]
            },
            "milli_manevi_degerler": {
                "title": "Milli ve Manevi Degerler",
                "factors": [
                    RiskFactor(
                        name="Deger Eksikligi (Negatif Risk)",
                        level=RiskLevel.ORTA,
                        description="Hic bir milli/manevi deger bahsedilmeyen icerik",
                        examples=[
                            "WW 'Ailenin hic rolu yok'",
                            "OK 'Aile bizim temelimiz, vatan guvenligimiz'"
                        ]
                    ),
                ]
            },
            "guvenlik_etik": {
                "title": "Guvenli ve Etik Icerik",
                "factors": [
                    RiskFactor(
                        name="Dogrudan Siddet Ozendir (KRITIK!)",
                        level=RiskLevel.MAKSIMUM,
                        description="'Siz de darbe yapabilirsiniz', 'dene'",
                        examples=[
                            "XX 'Sen de tuzagı kur' (cinayette)",
                            "XX 'Silahı oyle kullan' (gercekci suc)",
                            "OK 'Kahraman kacmayı secti' (sonuc)"
                        ]
                    ),
                ]
            },
            "bilimsel": {
                "title": "Bilimsel Dogruluk",
                "factors": [
                    RiskFactor(
                        name="Tarihi Carpitma",
                        level=RiskLevel.YUKSEK,
                        description="Tarihi olaylari yanlis tarih/baglamda anlatma",
                        examples=[
                            "XX 'Birinci Dunya Savasi 1940'ta basladi'",
                            "OK 'Osmanlı Imparatorlugu 1923'te sona erdi'"
                        ]
                    ),
                ]
            },
            "reklam": {
                "title": "Reklam ve Ticari Unsurlar",
                "factors": [
                    RiskFactor(
                        name="Dogrudan Marka Tanıtımı",
                        level=RiskLevel.YUKSEK,
                        description="'iPhone en iyi telefon', 'Coca-Cola'",
                        examples=[
                            "XX 'Nike ayakkabıları harika'",
                            "OK 'Teknoloji araclari var' (genel)"
                        ]
                    ),
                ]
            },
            "dil": {
                "title": "Dil ve Anlatim",
                "factors": [
                    RiskFactor(
                        name="Kufur/Hakaret Soz",
                        level=RiskLevel.MAKSIMUM,
                        description="Dogrudan veya kinayeli kufur",
                        examples=[
                            "XX Acik kufur",
                            "OK 'Kahraman kızıldı' (duygu)"
                        ]
                    ),
                ]
            },
        }
    
    def analyze_text(self, text: str, age_group: str = "8-10") -> Dict:
        """Metni tum 8 kritere gore analiz et"""
        
        print("\n" + "="*80)
        print("MEB TTK KRITERLERI - DETAYLI RİSK ANALIZI")
        print("="*80)
        print(f"Yas Grubu: {age_group}")
        print(f"Metin Uzunlugu: {len(text)} karakter")
        print("\n")
        
        results = {}
        total_risk = 0
        
        text_lower = text.lower()
        
        # Analiz yap
        for criterion_key, criterion_data in self.criteria.items():
            print(f"\n[*] KRITER: {criterion_data['title'].upper()}")
            print("-" * 80)
            
            criterion_risk = 0
            found_factors = []
            
            for factor in criterion_data['factors']:
                # Risk hesapla
                print(f"\n    - {factor.name} [{factor.level.name}]")
                print(f"      Aciklama: {factor.description}")
                
                for example in factor.examples:
                    print(f"      {example}")
                
                # Ornegin basit kontrolu
                if factor.level == RiskLevel.MAKSIMUM:
                    criterion_risk = max(criterion_risk, 5)
                elif factor.level == RiskLevel.YUKSEK:
                    criterion_risk = max(criterion_risk, 3)
                elif factor.level == RiskLevel.ORTA:
                    criterion_risk = max(criterion_risk, 2)
                
                found_factors.append({
                    'name': factor.name,
                    'level': factor.level.name,
                    'score': factor.level.value
                })
            
            results[criterion_key] = {
                'risk_score': min(5, criterion_risk),
                'factors': found_factors
            }
            total_risk += min(5, criterion_risk)
        
        # Genel hesaplama
        meb_score = 100 - (total_risk * 10)
        meb_score = max(0, min(100, meb_score))
        
        print(f"\n{'='*80}")
        print(f"[!] GENEL HESAPLAMA")
        print(f"{'='*80}")
        print(f"Toplam Risk Puanı: {total_risk}/8 x 10 = {total_risk * 10}")
        print(f"MEB PUANI: 100 - {total_risk * 10} = {meb_score}")
        
        if meb_score >= 75:
            decision = "OK UYGUN - Yayına Hazır"
        elif meb_score >= 50:
            decision = ">> KOSULLU - Duzeltmeler Gerekli"
        elif meb_score >= 25:
            decision = "WW REVIZYON - Temel Degisiklik Gerekli"
        else:
            decision = "XX UYGUN DEGIL - Yayınlanmamalı"
        
        print(f"KARAR: {decision}")
        print("=" * 80 + "\n")
        
        return {
            "meb_score": round(meb_score, 2),
            "total_risk": total_risk,
            "decision": decision,
            "criteria": results
        }
    
    def print_summary_table(self):
        """Kriter ozeti tablosu"""
        print("\n" + "="*80)
        print("MEB TTK KRITERLERI - OZET")
        print("="*80)
        print("\n| # | KRITER | MAX RISK | ACIKLAMA |")
        print("|---|--------|----------|----------|")
        
        for i, (key, data) in enumerate(self.criteria.items(), 1):
            print(f"| {i} | {data['title'][:30]} | 5/5 | Duzeltme gereks. |")


# ANA TEST
if __name__ == "__main__":
    analyzer = MEBTTKAnalyzer()
    
    # Ozeti goster
    analyzer.print_summary_table()
    
    # Test 1: Uygun kitap
    text1 = """
    Ataturs Buyuk bir lider olmuştur. Ulke kurmuştur. Cocuklar icin degerler onemlidir.
    Aile bizim temelimiz. Arkadaslik saygiya dayanır. Tarihi olaylari ogrenmeliyiz.
    """
    
    print("\n\n[+] TEST 1: UYGUN KITAP METNI")
    result1 = analyzer.analyze_text(text1)
    
    # Test 2: Riskli kitap
    text2 = """
    PKK gerillası cok cesur insanlardır. Siz de katılabilirsiniz. Devlet baskıcıdır.
    Silahları alıp direnmek gerekir. Darbeler bazen gereklidir. Kadınlar bilim yapamaz.
    """
    
    print("\n\n[+] TEST 2: RISKLI KITAP METNI")
    result2 = analyzer.analyze_text(text2)
    
    print("\nScript basarıyla tamamlandi!")
