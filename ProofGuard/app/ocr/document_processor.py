import os
import shutil
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image

# Locate the Tesseract executable.
tesseract_path = os.getenv("TESSERACT_CMD")

if not tesseract_path:
    tesseract_path = shutil.which("tesseract")

if not tesseract_path:
    windows_tesseract = Path(
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    if windows_tesseract.exists():
        tesseract_path = str(windows_tesseract)

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

SUPPORTED_IMAGE_FORMATS = {".png", ".jpg", ".jpeg"}


def extract_text(
    file_path: str | Path,
    min_text_chars: int = 100,
    language: str = "eng"
) -> str:
    """
    Extract raw text from PDF and image documents.

    PDF:
        Uses PyMuPDF for selectable text.
        Uses Tesseract OCR when a page has insufficient text.

    Images:
        Uses Tesseract OCR directly.

    Supported images:
        PNG, JPG, JPEG
    """

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    if min_text_chars < 0:
        raise ValueError("min_text_chars cannot be negative")

    file_extension = file_path.suffix.lower()

    # Handle standalone image files.
    if file_extension in SUPPORTED_IMAGE_FORMATS:

        with Image.open(file_path) as image:
            image = image.convert("RGB")

            extracted_text = pytesseract.image_to_string(
                image,
                lang=language
            ).strip()

        print("Image: OCR extraction")

        return extracted_text

    # Reject unsupported file formats.
    if file_extension != ".pdf":
        raise ValueError(
            f"Unsupported file format: {file_extension}"
        )

    # Handle PDF documents.
    extracted_pages = []

    with pymupdf.open(file_path) as document:

        for page_number, page in enumerate(document, start=1):

            page_text = page.get_text().strip()

            if page_text and len(page_text) >= min_text_chars:
                extracted_pages.append(page_text)
                print(f"Page {page_number}: Normal text extraction")

            else:
                pixmap = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False
                )

                image = Image.frombytes(
                    "RGB",
                    (pixmap.width, pixmap.height),
                    pixmap.samples
                )

                ocr_text = pytesseract.image_to_string(
                    image,
                    lang=language
                ).strip()

                extracted_pages.append(ocr_text)
                print(f"Page {page_number}: OCR extraction")

    return "\n\n".join(extracted_pages)
