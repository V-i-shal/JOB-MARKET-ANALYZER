"""
Resume Parser Service
Extracts text from PDF and image files using PDFPlumber and Tesseract OCR
"""

import os
import re
from pathlib import Path
from typing import Optional

import pdfplumber
import pytesseract
from PIL import Image
from loguru import logger


from ..models.resume import Resume, FileType


class ResumeParser:
    """
    Parses resume files (PDF and images) and extracts text.
    Uses pdfplumber for PDFs and Tesseract OCR for images.
    """

    def __init__(self):
        """Initialize the resume parser"""
        self._configure_tesseract()
        logger.info("ResumeParser initialized")

    def _configure_tesseract(self) -> None:
        """Configure Tesseract OCR path"""
        if os.name == "nt":  # Windows
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.getenv("TESSERACT_CMD", "")
            ]

            for path in possible_paths:
                if path and os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Tesseract configured at: {path}")
                    return

            logger.warning(
                "Tesseract not found. Set TESSERACT_CMD environment variable if OCR fails."
            )
        else:
            logger.info("Using system Tesseract (should be in PATH)")

    def parse_resume(self, file_path: str) -> Optional[Resume]:
        """
        Main entry point for parsing a resume file.
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None

            filename = os.path.basename(file_path)
            extension = Path(file_path).suffix.lower()

            if extension == ".pdf":
                text = self.extract_text_from_pdf(file_path)
                file_type = FileType.PDF
            elif extension in [".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"]:
                text = self.extract_text_from_image(file_path)
                file_type = FileType.IMAGE
            else:
                logger.error(f"Unsupported file type: {extension}")
                return None

            if not text or len(text.strip()) < 50:
                logger.warning("Extracted text too short or empty")
                return None

            resume = Resume(
                filename=filename,
                file_type=file_type,
                extracted_text=text
            )

            self.extract_basic_info(resume)
            return resume

        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            return None

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF using pdfplumber.
        """
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            return self._clean_extracted_text(text)

        except Exception as e:
            logger.error(f"PDF extraction failed, trying OCR fallback: {e}")
            return self._extract_pdf_via_ocr(pdf_path)

    def _extract_pdf_via_ocr(self, pdf_path: str) -> str:
        """
        OCR fallback for PDFs.
        """
        try:
            import pdf2image

            images = pdf2image.convert_from_path(pdf_path)
            text = ""

            for image in images:
                text += pytesseract.image_to_string(image, lang="eng") + "\n"

            return self._clean_extracted_text(text)

        except Exception as e:
            logger.error(f"OCR fallback failed: {e}")
            return ""

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image using Tesseract OCR.
        """
        try:
            image = Image.open(image_path)
            image = self._preprocess_image(image)

            config = "--oem 3 --psm 6"
            text = pytesseract.image_to_string(image, lang="eng", config=config)

            return self._clean_extracted_text(text)

        except Exception as e:
            logger.error(f"Image OCR failed: {e}")
            return ""

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.
        """
        if image.mode != "L":
            image = image.convert("L")
        return image

    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        """
        if not text:
            return ""

        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\x00-\x7F]+", " ", text)
        return text.strip()

    def extract_basic_info(self, resume: Resume) -> None:
        """
        Extract basic information (name, email, phone) from resume text.
        """
        text = resume.extracted_text

        # Email
        email_match = re.search(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            text
        )
        if email_match:
            resume.email = email_match.group(0)

        # Phone
        phone_match = re.search(
            r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            text
        )
        if phone_match:
            resume.phone = phone_match.group(0)

        # Name heuristic (first 5 lines)
        for line in text.split("\n")[:5]:
            line = line.strip()
            if (
                2 <= len(line.split()) <= 4
                and line[0].isupper()
                and not any(char.isdigit() for char in line)
            ):
                resume.user_name = line
                break


if __name__ == "__main__":
    logger.add("resume_parser.log", rotation="5 MB")
    parser = ResumeParser()
