# ProofGuard – Document Processing & OCR Module
## Development Documentation for Abhinav K

**Developer:** Abhinav K  
**Module:** Step 2: Document Processing and Optical Character Recognition (OCR)  
**Project:** ProofGuard – Cross-Document Product Identity & Evidence-Based Recall Intelligence  
**Repository:** https://github.com/Mr-Aswin/RP2  
**Branch:** `feature/abhinav-ocr-pipeline`  

---

## 1. Assigned Responsibility
The Document Processing and OCR module represents Step 2 in the ProofGuard processing pipeline:
```
User Document (PDF / Image) → Document Processing & OCR (Abhinav) → Product Information Extraction (Arun) → Database Storage
```
The goal of this module is to ingest user-uploaded documents across heterogeneous formats (native searchable PDFs, scanned image PDFs, and standalone product photos/labels in PNG, JPG, and JPEG formats), extract clean, complete text, and provide reliable fallback mechanisms when documents lack selectable digital text.

---

## 2. Implemented Architecture & Technologies

| Component | Technology | Purpose |
|---|---|---|
| **Digital PDF Parser** | `PyMuPDF` (`fitz` / `pymupdf`) | Fast, high-fidelity vector and text extraction for native digital documents. |
| **Raster Fallback Engine** | `PyMuPDF` Pixmap rendering (`Matrix(2, 2)`) | High-resolution 2x rendering of scanned PDF pages into RGB image buffers. |
| **OCR Engine** | `pytesseract` / Tesseract OCR v5 | Optical character recognition on rasterized PDF pages and standalone image files. |
| **Image Preprocessor** | `Pillow` (`PIL.Image`) | Format conversion and RGB color-space standardization. |
| **Test Suite** | `pytest` | 11 comprehensive unit and integration tests covering synthetic, scanned, corrupted, and mixed-mode documents. |

---

## 3. Core Implementation Details (`app/ocr/document_processor.py`)

### A. Tesseract Autodetection & Environment Configuration
The processor includes cross-platform autodetection:
1. Checks the `TESSERACT_CMD` environment variable.
2. Checks system `PATH` via `shutil.which("tesseract")`.
3. Checks standard Windows installation paths (`C:\Program Files\Tesseract-OCR\tesseract.exe`).
4. Configures `pytesseract.pytesseract.tesseract_cmd` automatically upon module import.

### B. Adaptive Dual-Mode PDF Extraction
To optimize processing speed while maintaining 100% text recovery:
- Each page is evaluated with `page.get_text().strip()`.
- If extracted text length meets or exceeds `min_text_chars` (default: 100 characters), direct digital text is utilized.
- If extracted text falls below `min_text_chars`, the page is treated as a scan: rendered at 200 DPI via `page.get_pixmap(matrix=pymupdf.Matrix(2, 2))` and dispatched to Tesseract OCR.
- Multi-page documents are combined using double-newline page separators (`\n\n`), preserving page boundary context.

### C. Standalone Image Processing
Supported image formats: `.png`, `.jpg`, `.jpeg`.
- Images are converted to standard RGB and processed directly with `pytesseract.image_to_string()`.

### D. Input Validation & Error Handling
- Non-existent file paths raise `FileNotFoundError`.
- Unsupported file formats (e.g., `.docx`, `.txt`) raise `ValueError`.
- Corrupt or invalid PDFs raise `pymupdf.FileDataError`.
- Negative threshold values raise `ValueError`.

---

## 4. Test Coverage & Verification

Automated test suite: `tests/test_ocr.py` (11 passing tests):
1. `test_extract_text_from_searchable_pdf`: Searchable PDF text recovery.
2. `test_extract_text_from_scanned_pdf`: OCR extraction from rendered raster image PDF.
3. `test_missing_pdf_raises_error`: Validates `FileNotFoundError`.
4. `test_invalid_pdf_raises_error`: Validates `pymupdf.FileDataError` on corrupted files.
5. `test_empty_pdf_returns_empty_text`: Handles 0-character blank PDFs without crashing.
6. `test_extract_text_from_png_image`: PNG OCR extraction.
7. `test_extract_text_from_jpeg_image`: JPEG OCR extraction.
8. `test_unsupported_file_format_raises_error`: Validates rejection of unsupported file types.
9. `test_empty_page_with_zero_threshold_uses_ocr`: Threshold boundary behavior.
10. `test_extract_text_from_mixed_content_pdf`: Multi-page mixed digital/scanned document handling.
11. `test_negative_min_text_chars_raises_error`: Negative threshold parameter validation.

---

## 5. Sample Documents Tested

The module was tested on representative test files stored in `data/`:
- `data/invoices/synthetic_product_invoice.pdf` (Clean selectable invoice)
- `data/manuals/samsung_washing_machine_manual.pdf` (Multi-page comprehensive product manual)
- `data/manuals/lg_semi_automatic_washing_machine_manual.pdf` (Complex layout washing machine manual)
