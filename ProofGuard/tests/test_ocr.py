
import pymupdf
import pytest
from PIL import Image, ImageDraw, ImageFont

from app.ocr.document_processor import extract_text


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


def test_empty_page_with_zero_threshold_uses_ocr(tmp_path, monkeypatch):
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


def test_extract_text_from_mixed_content_pdf(tmp_path, monkeypatch):
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

    # Create a PDF with one searchable page and one scanned page.
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

    # Mock OCR so the test does not depend on Tesseract.
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

    with pytest.raises(ValueError, match="min_text_chars cannot be negative"):
        extract_text(pdf_path, min_text_chars=-1)