
import pymupdf
import pytest
import pytesseract

from PIL import Image, ImageDraw, ImageFont

from app.ocr.document_processor import (
    extract_text,
    _correct_image_orientation
)


# --------------------------------------------------
# Searchable PDF Tests
# --------------------------------------------------

def test_extract_text_from_searchable_pdf(tmp_path):
    pdf_path = tmp_path / "searchable.pdf"

    document = pymupdf.open()
    page = document.new_page()

    expected_text = (
        "ProofGuard searchable PDF test. "
        "Product manual document."
    )

    page.insert_text((50, 50), expected_text)
    document.save(pdf_path)
    document.close()

    result = extract_text(pdf_path)

    assert expected_text in result


# --------------------------------------------------
# Scanned PDF Tests
# --------------------------------------------------

def test_extract_text_from_scanned_pdf(tmp_path):
    image_path = tmp_path / "scanned_page.png"
    pdf_path = tmp_path / "scanned.pdf"

    image = Image.new("RGB", (1600, 500), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=80)

    draw.text(
        (100, 150),
        "PROOFGUARD OCR TEST",
        fill="black",
        font=font
    )

    image.save(image_path)

    document = pymupdf.open()
    page = document.new_page()
    page.insert_image(page.rect, filename=str(image_path))
    document.save(pdf_path)
    document.close()

    result = extract_text(pdf_path)

    assert "PROOFGUARD" in result.upper()


def test_missing_pdf_raises_error(tmp_path):
    missing_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        extract_text(missing_path)


def test_invalid_pdf_raises_error(tmp_path):
    invalid_path = tmp_path / "invalid.pdf"
    invalid_path.write_text("This is not a valid PDF.")

    with pytest.raises(pymupdf.FileDataError):
        extract_text(invalid_path)


def test_empty_pdf_returns_empty_text(tmp_path):
    pdf_path = tmp_path / "empty.pdf"

    document = pymupdf.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    result = extract_text(pdf_path)

    assert result == ""


# --------------------------------------------------
# Image OCR Tests
# --------------------------------------------------

def test_extract_text_from_png_image(tmp_path):
    image_path = tmp_path / "manual.png"

    image = Image.new("RGB", (1600, 500), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=80)

    draw.text(
        (100, 150),
        "PROOFGUARD IMAGE TEST",
        fill="black",
        font=font
    )

    image.save(image_path)

    result = extract_text(image_path)

    assert "PROOFGUARD" in result.upper()


def test_extract_text_from_jpeg_image(tmp_path):
    image_path = tmp_path / "invoice.jpg"

    image = Image.new("RGB", (1600, 500), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=80)

    draw.text(
        (100, 150),
        "SAMPLE INVOICE PROOFGUARD",
        fill="black",
        font=font
    )

    image.save(image_path, format="JPEG", quality=95)

    result = extract_text(image_path)

    assert "INVOICE" in result.upper()


def test_unsupported_file_format_raises_error(tmp_path):
    file_path = tmp_path / "document.txt"
    file_path.write_text("This is a text file.")

    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_text(file_path)


# --------------------------------------------------
# OCR Fallback Tests
# --------------------------------------------------

def test_empty_page_with_zero_threshold_uses_ocr(
    tmp_path,
    monkeypatch
):
    pdf_path = tmp_path / "empty_page.pdf"

    document = pymupdf.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    ocr_called = False

    def mock_ocr(image, lang):
        nonlocal ocr_called
        ocr_called = True
        return "OCR TEST RESULT"

    monkeypatch.setattr(
        "app.ocr.document_processor.pytesseract.image_to_string",
        mock_ocr
    )

    result = extract_text(pdf_path, min_text_chars=0)

    assert ocr_called
    assert result == "OCR TEST RESULT"


def test_extract_text_from_mixed_content_pdf(
    tmp_path,
    monkeypatch
):
    pdf_path = tmp_path / "mixed_content.pdf"
    image_path = tmp_path / "scanned_page.png"

    # Create a scanned page image.
    image = Image.new("RGB", (1600, 500), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=80)

    draw.text(
        (100, 150),
        "SCANNED PAGE",
        fill="black",
        font=font
    )

    image.save(image_path)

    # Create PDF with searchable and scanned pages.
    document = pymupdf.open()

    text_page = document.new_page()

    text_page.insert_text(
        (50, 50),
        "This is the searchable PDF page containing enough text. "
        "It includes additional information to verify normal text extraction."
    )

    scanned_page = document.new_page()

    scanned_page.insert_image(
        scanned_page.rect,
        filename=str(image_path)
    )

    document.save(pdf_path)
    document.close()

    # Mock OCR to isolate the PDF extraction test.
    def mock_ocr(image, lang):
        return "SCANNED PAGE OCR RESULT"

    monkeypatch.setattr(
        "app.ocr.document_processor.pytesseract.image_to_string",
        mock_ocr
    )

    result = extract_text(pdf_path)

    assert "searchable PDF page" in result
    assert "SCANNED PAGE OCR RESULT" in result


def test_negative_min_text_chars_raises_error(tmp_path):
    pdf_path = tmp_path / "sample.pdf"

    document = pymupdf.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    with pytest.raises(
        ValueError,
        match="min_text_chars cannot be negative"
    ):
        extract_text(pdf_path, min_text_chars=-1)


# --------------------------------------------------
# Orientation Detection Tests
# --------------------------------------------------

def test_correct_image_orientation_rotates_image(monkeypatch):
    image = Image.new("RGB", (400, 200), "white")

    # Add a red marker in the top-left corner.
    image.paste((255, 0, 0), (10, 10, 40, 40))

    def mock_image_to_osd(image, config):
        return """
Page number: 0
Orientation in degrees: 270
Rotate: 90
Orientation confidence: 10.00
Script: Latin
Script confidence: 5.00
"""

    monkeypatch.setattr(
        "app.ocr.document_processor.pytesseract.image_to_osd",
        mock_image_to_osd
    )

    corrected_image = _correct_image_orientation(image)

    # Verify the image was rotated clockwise.
    assert corrected_image.size == (200, 400)

    # The original top-left red marker should now be near the top-right.
    assert corrected_image.getpixel((180, 20)) == (255, 0, 0)



def test_orientation_detection_failure_returns_original_image(
    monkeypatch
):
    image = Image.new("RGB", (400, 200), "white")

    def mock_image_to_osd(image, config):
        raise pytesseract.TesseractError(
            1,
            "Orientation detection failed"
        )

    monkeypatch.setattr(
        "app.ocr.document_processor.pytesseract.image_to_osd",
        mock_image_to_osd
    )

    corrected_image = _correct_image_orientation(image)

    assert corrected_image.size == image.size

def test_corrupted_image_raises_error(tmp_path):
    image_path = tmp_path / "corrupted.png"

    image_path.write_text(
        "This is not a valid image."
    )

    with pytest.raises(
        Image.UnidentifiedImageError
    ):
        extract_text(image_path)


def test_tesseract_ocr_failure_raises_error(tmp_path, monkeypatch):
    image_path = tmp_path / "ocr_failure.png"

    image = Image.new("RGB", (1600, 500), "white")
    image.save(image_path)

    def mock_image_to_osd(image, config):
        return """
Rotate: 0
"""

    def mock_image_to_string(image, lang):
        raise pytesseract.TesseractError(
            1,
            "OCR engine failed"
        )

    monkeypatch.setattr(
        "app.ocr.document_processor.pytesseract.image_to_osd",
        mock_image_to_osd
    )

    monkeypatch.setattr(
        "app.ocr.document_processor.pytesseract.image_to_string",
        mock_image_to_string
    )

    with pytest.raises(pytesseract.TesseractError):
        extract_text(image_path)

def test_unreadable_image_returns_empty_text(tmp_path):
    image_path = tmp_path / "blank.png"

    image = Image.new("RGB", (1600, 500), "white")
    image.save(image_path)

    result = extract_text(image_path)

    assert result == ""
