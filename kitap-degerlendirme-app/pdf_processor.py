"""
PDF dosyasından metin ve görsel çıkarma
"""

import PyPDF2
import os
import re
from typing import Dict, List, Tuple
from visual_audit import analyze_extracted_images, gorsel_analiz_yapilmadi_sonucu


class PDFProcessor:
    """PDF dosyasından metin ve metadata çıkarır"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text = ""
        self.metadata = {}
        self.sayfa_sayisi = 0

    def _normalize_extracted_text(self, text: str) -> str:
        """PDF karakter haritası ve satır sonu hece bölünmelerini temizler."""
        if not text:
            return ""

        replacements = {
            "›": "ı",
            "‹": "İ",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)

        harf = "A-Za-zÇĞİÖŞÜçğıöşü"
        text = re.sub(rf"(?<=[{harf}])\s*-\s*\n\s*(?=[{harf}])", "", text)
        return text
        
    def extract_text(self) -> str:
        """PDF'den metin çıkartır"""
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                self.sayfa_sayisi = len(reader.pages)
                
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    text = self._normalize_extracted_text(text or "")
                    self.text += f"\n--- SAYFA {page_num + 1} ---\n{text}"
                    
            return self.text
        except Exception as e:
            raise Exception(f"PDF okuma hatası: {str(e)}")
    
    def extract_metadata(self) -> Dict:
        """PDF metadata'sını çıkartır"""
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                metadata = reader.metadata
                
                self.metadata = {
                    "baslik": metadata.title or "Belirsiz",
                    "yazar": metadata.author or "Belirsiz",
                    "konu": metadata.subject or "",
                    "aciklama": metadata.get("/Description", ""),
                    "sayfa_sayisi": len(reader.pages),
                    "dosya_adi": os.path.basename(self.pdf_path)
                }
                
            return self.metadata
        except Exception as e:
            raise Exception(f"Metadata çıkarma hatası: {str(e)}")

    def _extract_page_images(self, page, page_number: int) -> List[Dict]:
        """PyPDF2 ile sayfadaki cikarilabilir gorselleri toplar."""
        extracted = []
        try:
            for image_index, image in enumerate(getattr(page, "images", []) or [], 1):
                data = getattr(image, "data", b"") or b""
                name = getattr(image, "name", "") or f"page_{page_number}_image_{image_index}"
                extension = os.path.splitext(name)[1].lower().lstrip(".")
                mime_type = {
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "png": "image/png",
                    "gif": "image/gif",
                    "bmp": "image/bmp",
                    "tif": "image/tiff",
                    "tiff": "image/tiff",
                }.get(extension, "image/png")
                extracted.append({
                    "sayfa": page_number,
                    "gorsel_no": image_index,
                    "ad": name,
                    "format": extension or "unknown",
                    "mime_type": mime_type,
                    "boyut_byte": len(data),
                    "data": data,
                })
        except Exception:
            return []
        return extracted

    def _render_visual_pages(self, page_numbers: List[int]) -> List[Dict]:
        """Gorsel iceren sayfalari PNG olarak render eder ve analiz girdisine cevirir."""
        if not page_numbers:
            return []
        try:
            import fitz  # PyMuPDF
        except Exception:
            return []

        rendered = []
        try:
            document = fitz.open(self.pdf_path)
            for page_number in sorted(set(page_numbers)):
                if page_number < 1 or page_number > len(document):
                    continue
                page = document[page_number - 1]
                pixmap = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
                rendered.append({
                    "sayfa": page_number,
                    "gorsel_no": 1,
                    "ad": f"sayfa_{page_number}_render.png",
                    "format": "png",
                    "mime_type": "image/png",
                    "boyut_byte": len(pixmap.tobytes("png")),
                    "data": pixmap.tobytes("png"),
                    "kaynak": "sayfa_render",
                })
            document.close()
        except Exception:
            return []
        return rendered

    def extract_visual_summary(self, analyze_content: bool = True) -> Dict:
        """PDF icindeki gorsel/XObject ozetini ve varsa icerik analizini cikarir."""
        try:
            toplam_gorsel = 0
            gorselli_sayfalar = []
            extracted_images = []

            with open(self.pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for index, page in enumerate(reader.pages, 1):
                    page_count = 0
                    resources = page.get("/Resources") or {}
                    xobjects = resources.get("/XObject") if resources else None
                    if xobjects:
                        xobjects = xobjects.get_object()
                        for obj in xobjects.values():
                            resolved = obj.get_object()
                            if resolved.get("/Subtype") == "/Image":
                                page_count += 1

                    page_images = self._extract_page_images(page, index)
                    if page_images:
                        extracted_images.extend(page_images)
                        page_count = max(page_count, len(page_images))

                    if page_count:
                        toplam_gorsel += page_count
                        gorselli_sayfalar.append(index)

            rendered_images = self._render_visual_pages(gorselli_sayfalar) if analyze_content else []
            analysis_images = rendered_images or (extracted_images if analyze_content else [])

            if not analyze_content:
                gorsel_denetim = gorsel_analiz_yapilmadi_sonucu(
                    sayfa=", ".join(str(s) for s in gorselli_sayfalar)
                )
            elif toplam_gorsel > 0 and not analysis_images:
                gorsel_denetim = gorsel_analiz_yapilmadi_sonucu(
                    sayfa=", ".join(str(s) for s in gorselli_sayfalar)
                )
            else:
                gorsel_denetim = analyze_extracted_images(analysis_images)
            gorsel_analiz_yapildi = bool(gorsel_denetim.get("gorsel_icerik_analizi_yapildi", False))
            gorsel_riski = int(gorsel_denetim.get("genel_risk", 0) or 0) * 20 if gorsel_analiz_yapildi else 0
            analiz_tipi = "vision_icerik_analizi" if gorsel_analiz_yapildi else "xobject_sayimi"
            visual_pages = len(gorselli_sayfalar)
            visual_analysis_count = int(gorsel_denetim.get("analiz_edilen_gorsel_sayisi", 0) or 0)
            analiz_eksik = visual_pages > 0 and visual_analysis_count == 0
            analiz_notu = (
                "Görsel içerik analizi yapılmıştır; riskler sayfa ve kategori bazında raporlanmıştır."
                if gorsel_analiz_yapildi else
                "Görsel içerik analizi yapılmamıştır. Yalnızca PDF içerisinde görsel nesne bulunduğu tespit edilmiştir."
            )

            return {
                "toplam_gorsel": toplam_gorsel,
                "gorselli_sayfalar": gorselli_sayfalar,
                "ic_illustrasyon_var": any(page > 3 for page in gorselli_sayfalar),
                "gorsel_icerik_analizi_yapildi": gorsel_analiz_yapildi,
                "gorsel_icerik_analizi_eksik": analiz_eksik,
                "visual_pages": visual_pages,
                "visual_analysis_count": visual_analysis_count,
                "analiz_tipi": analiz_tipi,
                "not": analiz_notu,
                "kalite_uyarisi": "Görsel içerik analizi eksik yapıldı" if analiz_eksik else "",
                "gorsel_riski": gorsel_riski,
                "analiz_edilebilir_gorsel_sayisi": len(analysis_images),
                "sayfa_render_gorsel_sayisi": len(rendered_images),
                "xobject_cikarilan_gorsel_sayisi": len(extracted_images),
                "analiz_kaynagi": "sayfa_render" if rendered_images else "xobject_gorsel",
                "gorsel_bulgulari": gorsel_denetim.get("bulgular", []),
                "gorsel_analizleri": gorsel_denetim.get("gorsel_analizleri", []),
                "analiz_edilen_gorsel_sayisi": visual_analysis_count,
                "tamamlanamayan_gorsel_sayisi": int(gorsel_denetim.get("tamamlanamayan_gorsel_sayisi", 0) or 0),
                "gorsel_denetim": gorsel_denetim,
            }
        except Exception:
            return {
                "toplam_gorsel": 0,
                "gorselli_sayfalar": [],
                "ic_illustrasyon_var": False,
                "gorsel_icerik_analizi_yapildi": False,
                "analiz_tipi": "xobject_sayimi",
                "not": "Görsel özeti çıkarılamadı.",
                "gorsel_denetim": gorsel_analiz_yapilmadi_sonucu()
            }

    def get_text_statistics(self) -> Dict:
        """Metin istatistikleri döndürür"""
        words = self.text.split()
        chars = len(self.text)
        
        return {
            "kelime_sayisi": len(words),
            "karakter_sayisi": chars,
            "ort_kelime_uzunlugu": chars / len(words) if words else 0,
            "satir_sayisi": len(self.text.split('\n'))
        }
    
    def get_chapters(self) -> List[str]:
        """Kitap bölümlerini tanımlamaya çalışır"""
        # Basit bir yaklaşım: başlık benzeri satırları bulma
        lines = self.text.split('\n')
        chapters = []
        
        for line in lines:
            if len(line) < 100 and len(line) > 10:  # Başlık benzeri
                chapters.append(line.strip())
        
        return chapters[:20]  # İlk 20 potansiyel başlık
