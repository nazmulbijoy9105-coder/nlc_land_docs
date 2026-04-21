import io
import base64
import tempfile
import os
from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF
from PIL import Image, ImageFilter, ImageOps
import pytesseract

TESSERACT_LANG = "ben+eng"  # Bengali + English

class OCRService:
    """Server-side OCR: PyMuPDF + Tesseract — no client JS"""

    def extract_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF — try native text first, fallback to OCR"""
        texts = []
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            # Try native text extraction first
            text = page.get_text("text")
            if len(text.strip()) > 50:
                texts.append(text)
            else:
                # OCR fallback
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_bytes))
                img = self._preprocess(img)
                ocr_text = pytesseract.image_to_string(img, lang=TESSERACT_LANG)
                texts.append(ocr_text)
        doc.close()
        return "\n\n--- PAGE BREAK ---\n\n".join(texts)

    def extract_from_image(self, image_bytes: bytes) -> str:
        """OCR from image file"""
        img = Image.open(io.BytesIO(image_bytes))
        img = self._preprocess(img)
        return pytesseract.image_to_string(img, lang=TESSERACT_LANG)

    def _preprocess(self, img: Image.Image) -> Image.Image:
        """Grayscale → contrast → binarize → deskew"""
        img = img.convert("L")
        img = ImageOps.autocontrast(img, cutoff=2)
        # Otsu-like threshold
        img = img.point(lambda x: 0 if x < 128 else 255, "1").convert("L")
        return img

    def extract_from_bytes(self, file_bytes: bytes, mime_type: str) -> str:
        if "pdf" in mime_type:
            return self.extract_from_pdf(file_bytes)
        elif mime_type in ("image/jpeg", "image/png", "image/tiff", "image/jpg"):
            return self.extract_from_image(file_bytes)
        return ""

ocr_service = OCRService()
