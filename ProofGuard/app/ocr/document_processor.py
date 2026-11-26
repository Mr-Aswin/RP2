
import os
import shutil
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image, ImageEnhance, ImageOps


# --------------------------------------------------
# Tesseract Configuration
# --------------------------------------------------

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


# --------------------------------------------------
# Image Preprocessing
# --------------------------------------------------

def _preprocess_image(image: Image.Image) -> Image.Image:
    """
    Prepare an image for OCR.

    Processing:
        1. Convert to grayscale.
        2. Improve contrast automatically.
        3. Enhance text visibility.
        4. Upscale smaller images.
    """

    image = image.convert("L")

    image = ImageOps.autocontrast(image)

    image = ImageEnhance.Contrast(image).enhance(1.5)

    if image.width < 1500:
        scale = min(2.0, 1500 / image.width)

        new_size = (
            int(image.width * scale),
            int(image.height * scale)
        )

        image = image.resize(
            new_size,
            Image.Resampling.LANCZOS
        )

    return image


# --------------------------------------------------
# Image Orientation Correction
# --------------------------------------------------


def _correct_image_orientation(image: Image.Image) -> Image.Image:
    """
    Detect and correct image rotation using Tesseract OSD.

    If orientation detection fails, retain the original image.
    """

    try:
        osd_result = pytesseract.image_to_osd(
            image,
            config="--psm 0"
        )

        rotation = 0

        for line in osd_result.splitlines():
            if line.startswith("Rotate:"):
                rotation = int(line.split(":")[1].strip())
                break

        if rotation in (90, 180, 270):
            image = image.rotate(
                -rotation,
                expand=True
            )

    except (
        pytesseract.TesseractError,
        ValueError,
        RuntimeError
    ):
        # Continue OCR if orientation detection fails.
        pass

    return image


# --------------------------------------------------
# Main Text Extraction Function
# --------------------------------------------------

def extract_text(
    file_path: str | Path,
    min_text_chars: int = 100,
    language: str = "eng"
) -> str:
    """
    Extract text from PDF and image documents.

    Supported formats:
        - PDF
        - PNG
        - JPG
        - JPEG

    Searchable PDFs use PyMuPDF.
    Scanned PDFs and images use Tesseract OCR.

    Returns:
        Extracted text as a string.
    """

    file_path = Path(file_path)

    # Validate file existence.
    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    # Validate minimum text threshold.
    if min_text_chars < 0:
        raise ValueError(
            "min_text_chars cannot be negative."
        )

    file_extension = file_path.suffix.lower()

    # --------------------------------------------------
    # Image Document OCR
    # --------------------------------------------------

    if file_extension in SUPPORTED_IMAGE_FORMATS:

        with Image.open(file_path) as image:

            image = _preprocess_image(image)

            image = _correct_image_orientation(image)

            extracted_text = pytesseract.image_to_string(
                image,
                lang=language
            ).strip()

        print(
            f"[OCR] Image extraction completed: {file_path.name}"
        )

        return extracted_text

    # --------------------------------------------------
    # PDF Document Processing
    # --------------------------------------------------

    if file_extension == ".pdf":

        extracted_pages = []

        with pymupdf.open(file_path) as document:

            for page_number, page in enumerate(document):

                # First attempt: searchable PDF text.
                page_text = page.get_text().strip()

                if page_text and len(page_text) >= min_text_chars:

                    extracted_pages.append(page_text)

                    print(
                        f"[PDF] Text extracted from page "
                        f"{page_number + 1}"
                    )

                    continue

                # Second attempt: OCR scanned PDF page.
                print(
                    f"[OCR] Processing scanned page "
                    f"{page_number + 1}"
                )

                pixmap = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False
                )

                image = Image.frombytes(
                    "RGB",
                    (pixmap.width, pixmap.height),
                    pixmap.samples
                )

                # Preprocess scanned page.
                image = _preprocess_image(image)

                # Correct page orientation.
                image = _correct_image_orientation(image)

                # Perform OCR.
                ocr_text = pytesseract.image_to_string(
                    image,
                    lang=language
                ).strip()

                extracted_pages.append(ocr_text)

        final_text = "\n\n".join(extracted_pages).strip()

        print(
            f"[PDF] Extraction completed: {file_path.name}"
        )

        return final_text

    # --------------------------------------------------
    # Unsupported File Format
    # --------------------------------------------------

    raise ValueError(
        f"Unsupported file format: {file_extension}"
    )
