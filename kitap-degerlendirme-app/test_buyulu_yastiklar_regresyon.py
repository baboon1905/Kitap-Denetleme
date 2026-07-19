import os
import unittest

from pdf_processor import PDFProcessor
from theme_gain_analysis import analyze_theme_gain, kitap_tutarlilik_denetimi, prepare_theme_report_payload, rapor_kalite_kapisi


class BuyuluYastiklarRegressionTest(unittest.TestCase):
    def test_buyulu_yastiklar_ali_pati_sablonuna_dusmez(self):
        pdf_path = os.path.join("uploads", "buyulu_yastiklar.pdf")
        self.assertTrue(os.path.exists(pdf_path), "Büyülü Yastıklar test PDF'i bulunamadı.")

        processor = PDFProcessor(pdf_path)
        metadata = processor.extract_metadata()
        metadata.update({
            "kitap_adi": "Büyülü Yastıklar",
            "dosya_adi": "buyulu_yastiklar.pdf",
            "dosya_yolu": pdf_path,
        })

        result = analyze_theme_gain(processor.extract_text(), metadata)
        summary = result.get("kitap_ozeti") or ""
        first_evidence = " ".join(
            str(evidence.get("alinti") or "")
            for item in result.get("tema_analizi") or []
            if isinstance(item, dict)
            for evidence in (item.get("kanitlar") or [])[:1]
            if isinstance(evidence, dict)
        )

        self.assertNotEqual(result.get("book_subtype"), "değerler eğitimi / hayvan sevgisi")
        self.assertNotIn("Ali", summary)
        self.assertNotIn("Pati", summary)
        self.assertNotIn("kriminoloji", first_evidence.casefold())

        audit = kitap_tutarlilik_denetimi(result)
        self.assertTrue(audit.get("gecerli"), audit)

        quality = rapor_kalite_kapisi(prepare_theme_report_payload(result))
        self.assertTrue(quality.get("gecerli"), quality)
        self.assertFalse(result.get("ozet_kalite_kontrol", {}).get("guvenilir_uretilemedi"), result)


if __name__ == "__main__":
    unittest.main()
