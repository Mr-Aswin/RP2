# ProofGuard – Product Information Extraction Module
## Comprehensive Development and Contribution Documentation
**Developer:** Ashfaq  
**Project:** ProofGuard – Cross-Document Product Identity & Evidence-Based Recall Intelligence  
**Repository:** https://github.com/Mr-Aswin/RP2  
**Module:** Product Information Extraction (Ticket 1 – Data & System Foundation)  
**Assigned Team Lead:** Aswin S  

---

## 1. Contribution Overview
The Product Information Extraction Module serves as the critical bridge in ProofGuard between unstructured, noisy OCR output and downstream recall intelligence pipelines (Product Identity Matching, Recall Database Search, and Evidence RAG).

Given raw OCR text from invoices, user manuals, warranty registrations, or product labels, this module parses, normalizes, and extracts five foundational product identity attributes:
1. **Product Name** (e.g., `Front Load Washing Machine`, `Refrigerator`, `Microwave Oven`)
2. **Brand / Manufacturer** (e.g., `Samsung`, `LG`, `Whirlpool`, `Bosch`, `Sony`)
3. **Model Number** (e.g., `WA70BG4546BD`, `WW80T`, `SMS66GI01I`)
4. **Serial Number** (e.g., `SN12345678`, `4567890123`, `WP-SN-554433`)
5. **Product Category** (e.g., `Home Appliance`, `Kitchen Appliance`, `Electronics`)

The module guarantees strict data integrity by outputting a validated Pydantic model (`ProductCreate`), ensuring clean integration with the SQLite database schema and preventing hallucinated or fabricated data.

---

## 2. Technologies Used

| Technology | Purpose in This Module |
|---|---|
| **Python 3.11** | Core programming language for data normalization and extraction pipelines. |
| **spaCy (`en_core_web_sm`)** | NLP pipeline for tokenization and Named Entity Recognition (`ORG` entities) to recognize corporate entities and brand names. Loaded via a memory-efficient singleton lazy-loader. |
| **Regular Expressions (`re`)** | Pattern-based extraction of contextual labels, model codes, serial numbers, and noise-filtering (invoice numbers, dates, phone numbers). |
| **Pydantic v2 (`ProductCreate`)** | Schema validation, type enforcement, and serialization to dictionaries for database persistence. |
| **SQLAlchemy 2.0** | Verification of compatibility with the existing `Product` ORM model. |
| **PyMuPDF (`fitz`)** | Used via Abhinav's OCR module for selectable text extraction from PDFs. |
| **Pytest** | Automated unit testing, parameterized edge case testing, and integration verification. |

---

## 3. Files Created

1. **`ProofGuard/app/extraction/product_extractor.py`**
   - Core extraction engine containing text preprocessing, field extraction functions (`extract_brand`, `extract_model_number`, `extract_serial_number`, `extract_product_name`, `classify_category`), and the primary interface `extract_product_info(raw_text, as_dict=False)`.

2. **`ProofGuard/tests/test_extraction.py`**
   - Automated pytest suite comprising 48 comprehensive unit and integration tests covering all five fields, edge cases, error conditions, and end-to-end OCR integration.

3. **`ProofGuard/docs/Ashfaq_Contribution.md`**
   - Mandatory comprehensive development and contribution report.

---

## 4. Files Modified

1. **`ProofGuard/app/extraction/__init__.py`**
   - Exposed key module interfaces (`extract_product_info`, `extract_product_dict`, `preprocess_text`, `extract_brand`, `extract_model_number`, `extract_serial_number`, `extract_product_name`, `classify_category`) for clean package-level importing.
   - *Reason for modification:* Original file was an empty placeholder `__init__.py`.

*(Note: No database models, OCR processor code, or schemas were altered, honoring strict architectural preservation).*

---

## 5. Implementation Explanation

### Task 1: Raw Text Processing (`preprocess_text`)
- **Input Validation:** Enforces string input; raises `TypeError` for non-string inputs (`None`, `int`, `dict`, etc.).
- **Empty Handling:** Safely detects empty or whitespace-only inputs, returning an empty `ProductCreate` object without failing.
- **Normalization:** Employs `unicodedata.normalize("NFKC", text)` to normalize typographic ligatures and full-width characters from OCR.
- **Whitespace Sanitation:** Converts non-breaking spaces (`\xa0`) and redundant horizontal tabs/spaces into single spaces while preserving line structure required for regex matching.
- **Line Break Regularization:** Standardizes `\r\n` and `\r` to `\n` and limits blank lines to prevent memory bloat.

### Task 2: Brand / Manufacturer Extraction (`extract_brand`)
Combines multi-tier heuristic and NLP techniques:
1. **Explicit Label Matching:** Scans for patterns like `Brand:`, `Manufacturer:`, `Make / Brand:`, `Make:`, `Mfr:`.
2. **Manufacture Declarations:** Extracts entities from declarations like `Manufactured by <Entity>`. Corporate suffixes (`Electronics`, `Corporation`, `Inc.`, `Pvt Ltd`) are stripped to retain canonical brand names.
3. **spaCy Named Entity Recognition:** Utilizes `en_core_web_sm` to identify `ORG` entities and aligns them with recognized manufacturers.
4. **Gazetteer Dictionary Matching:** Matches against known global and domestic appliance brands (`Samsung`, `LG`, `Whirlpool`, `Bosch`, `Sony`, `Philips`, `Haier`, `Godrej`, `IFB`, etc.) with strict word boundaries.
5. **No Hallucination:** If no brand is present, strictly returns `None`.

### Task 3: Model Number Extraction (`extract_model_number`)
- Identifies model labels: `Model Number`, `Model No`, `Model No.`, `Product Model`, `Model Code`, `Model #`, `Model:`.
- Handles both single-line (`Model Number: WW80T`) and multiline formats (`Model Number:\nWW80T`).
- **Disambiguation & Noise Filtering:**
  - Excludes invoice numbers (`INV-`, `TEST-INV-`, `BILL-`).
  - Excludes dates (`15 November 2026`, `2026-10-15`).
  - Excludes phone numbers (`+1-800-...`, 10-digit customer care numbers).
  - Excludes generic header words (e.g., `Year`, `Details`, `Manual`, `Specification`).

### Task 4: Serial Number Extraction (`extract_serial_number`)
- Identifies serial labels: `Serial Number`, `Serial No`, `S/N`, `SN`, `Serial #`, `Serial Identifier`.
- Validates alphanumeric format and lengths (3 to 35 characters).
- Explicitly prevents collision with the extracted model number (`exclude_model` check).
- Supports numeric, hyphenated, and alphanumeric serial codes.

### Task 5: Product Name Extraction (`extract_product_name`)
- Detects explicit labels: `Product Name:`, `Product Description:`, `Item Name:`, `Equipment:`, `Appliance:`.
- Strips redundant brand prefixes if the label repeats the brand (e.g. `Samsung Front Load Washing Machine` becomes `Front Load Washing Machine`).
- Matches against a database of canonical appliance and electronic products (e.g., `Front Load Washing Machine`, `Double Door Refrigerator`, `Smart Television`, `Convection Microwave Oven`).
- Fallback scanning of prominent document titles and headings.

### Task 6: Product Category Identification (`classify_category`)
Maps the extracted product name and document text to the target taxonomy:
- **`Home Appliance`:** Washing machines (front/top/semi-automatic), clothes dryers, refrigerators, air conditioners, vacuum cleaners, water heaters, air purifiers.
- **`Kitchen Appliance`:** Microwave ovens, dishwashers, induction cooktops, blenders, food processors, coffee makers, electric kettles, air fryers, toasters.
- **`Electronics`:** Televisions, laptops, smartphones, tablets, desktop computers, monitors, headphones, cameras, smartwatches, printers.
- **Unidentified Category:** Returns `None` if no confident category mapping exists, avoiding invented categories.

### Task 7: Structured Output & Schema Validation (`extract_product_info`)
- Validates all fields using the existing `ProductCreate` Pydantic schema:
  ```python
  product = ProductCreate(
      product_name=product_name,
      brand=brand,
      model_number=model_number,
      serial_number=serial_number,
      product_category=product_category,
  )
  ```
- Returns `ProductCreate` directly, with an optional `as_dict=True` parameter (or `extract_product_dict(text)`) for dictionary output.

---

## 6. Integration

### Integration with Abhinav's OCR Module
The extraction module was designed to seamlessly consume raw text from `app.ocr.document_processor.extract_text`:

```python
from app.ocr.document_processor import extract_text
from app.extraction.product_extractor import extract_product_info

# 1. OCR extraction using existing module
raw_text = extract_text("data/invoices/synthetic_product_invoice.pdf")

# 2. Structured information extraction
product = extract_product_info(raw_text)

print(product.model_dump())
```

**Live Verification Output:**
```python
{
    'product_name': 'Front Load Washing Machine',
    'brand': 'Samsung',
    'model_number': 'WW80T',
    'serial_number': None,
    'product_category': 'Home Appliance'
}
```

### Integration with Database & Pydantic Schema
The output from `extract_product_info` can be passed directly to the existing SQLAlchemy `Product` model:
```python
from app.db.models import Product

db_product = Product(**product.model_dump())
session.add(db_product)
session.commit()
```
This is fully tested in `test_database_compatibility` in `tests/test_extraction.py`.

---

## 7. Testing

A dedicated test suite was implemented in `tests/test_extraction.py`.

### Test Summary
- **Total Tests:** 48 passed, 0 failed.
- **Execution Time:** ~9.6s.
- **Status:** All tests passing.

### Test Matrix
| Test Name | Purpose / Scenario | Status |
|---|---|---|
| `test_extract_all_five_fields` | Standard multi-field document with brand, name, model, serial, category | **PASSED** |
| `test_brand_extraction` (6 cases) | Labeled brands, manufacturers, 'manufactured by', uppercase titles | **PASSED** |
| `test_brand_extraction_unknown` | Documents without brand must return `None` (no hallucination) | **PASSED** |
| `test_model_number_extraction` (6 cases) | Various model labels (`Model:`, `Model No:`, `Product Model:`, multiline) | **PASSED** |
| `test_model_not_confused_with_invoice_date_phone` | Distinguishing model numbers from `TEST-INV-`, dates, and phone numbers | **PASSED** |
| `test_serial_number_extraction` (5 cases) | `Serial Number:`, `S/N:`, `SN:`, multiline serial numbers | **PASSED** |
| `test_serial_not_confused_with_model` | Preventing cross-contamination between model and serial numbers | **PASSED** |
| `test_category_identification` (13 cases) | Correct assignment to `Home Appliance`, `Kitchen Appliance`, `Electronics` | **PASSED** |
| `test_category_unknown` | Unrecognized industrial equipment defaults safely to `None` | **PASSED** |
| `test_missing_model_number` | Documents lacking model number return `model_number=None` | **PASSED** |
| `test_missing_serial_number` | Documents lacking serial number return `serial_number=None` | **PASSED** |
| `test_empty_input_text` | Empty string and whitespace-only strings return empty schema | **PASSED** |
| `test_invalid_input_type` (4 cases) | `None`, `int`, `list`, `dict` raise `TypeError` | **PASSED** |
| `test_warranty_card_format` | Real-world warranty registration document format | **PASSED** |
| `test_user_manual_cover_format` | User manual cover page layout | **PASSED** |
| `test_ambiguous_and_noisy_labels` | Noisy documents with "Model Year: 2026", "Serial Batch: ...", etc. | **PASSED** |
| `test_pydantic_validation_and_dict_output` | Validates `ProductCreate` model methods and `extract_product_dict` | **PASSED** |
| `test_database_compatibility` | Persists extracted `ProductCreate` into SQLite test session | **PASSED** |
| `test_integration_with_ocr_synthetic_invoice` | End-to-end test on `data/invoices/synthetic_product_invoice.pdf` | **PASSED** |

---

## 8. Problems and Solutions

1. **Problem:** When parsing noisy documents like `"Model Year: 2026"`, naive regex matching on `model[\s:=–-]+` captured `"Year"` as the model number.  
   **Solution:** Constrained regex delimiters to require explicit separators (`[:=–-]`) when followed by arbitrary text, added negative word filtering, and added `"YEAR"` to `DISALLOWED_TOKENS`.

2. **Problem:** Warranty documents with headers such as `"PRODUCT WARRANTY REGISTRATION"` triggered false positives on generic `Product:` labels, extracting `"Warranty Registration"` as the product name.  
   **Solution:** Added validation against document descriptors (`WARRANTY`, `REGISTRATION`, `SPECIFICATION`, `INVOICE`) and added dedicated patterns for `Equipment:`, `Appliance:`, and canonical product matching.

3. **Problem:** 10-digit numeric serial numbers (e.g., `SN: 4567890123`) were initially rejected by a greedy phone number filter.  
   **Solution:** Refined the serial validation logic to only reject phone numbers that match international dialing patterns or appear without explicit serial prefix labeling.

4. **Problem:** spaCy model loading during high-volume testing can introduce unnecessary overhead.  
   **Solution:** Implemented a thread-safe singleton lazy-loader (`get_nlp()`) that loads `en_core_web_sm` once and reuses the instance across all subsequent extraction calls.

---

## 9. Execution Instructions

### Running the Test Suite
From the `ProofGuard/` root directory:

```bash
# Run extraction test suite
python -m pytest tests/test_extraction.py -v

# Run extraction and integration tests
python -m pytest tests/test_extraction.py tests/test_integration.py -v
```

### Running Extraction on a Sample Document
```python
from app.ocr.document_processor import extract_text
from app.extraction import extract_product_info

# 1. OCR text extraction
raw_text = extract_text("data/invoices/synthetic_product_invoice.pdf")

# 2. Extract structured product data
product = extract_product_info(raw_text)

print(product)
# Output: product_name='Front Load Washing Machine' brand='Samsung' model_number='WW80T' serial_number=None product_category='Home Appliance'
```

---

## 10. GitHub Contribution

- **Target Repository:** `https://github.com/Mr-Aswin/RP2`
- **Feature Branch:** `feature/ashfaq-product-extraction`
- **Commit ID:** `ff8223268537f1a090792c96118aa74f1669fa06`
- **Files Staged & Committed:**
  - `ProofGuard/app/extraction/product_extractor.py`
  - `ProofGuard/app/extraction/__init__.py`
  - `ProofGuard/tests/test_extraction.py`
  - `ProofGuard/docs/Ashfaq_Contribution.md`
- **Commit Message:** `"Add product information extraction module"`
- **Push Status:** Committed locally on feature branch. Push initiated (`git-credential-manager` authentication prompt ready for user sign-in or manual `git push -u origin feature/ashfaq-product-extraction`).

---

## 11. Final Status

- [x] Preprocessing and raw OCR text normalization.
- [x] Product name extraction with canonical product matching.
- [x] Brand / manufacturer extraction with spaCy NER and gazetteer.
- [x] Model number extraction with invoice, date, and phone filtering.
- [x] Serial number extraction with model disambiguation.
- [x] Product category identification (`Home Appliance`, `Kitchen Appliance`, `Electronics`).
- [x] Structured output validated via `ProductCreate` schema.
- [x] Non-destructive integration with Abhinav's OCR module.
- [x] 48 automated pytest tests created and passing.
- [x] Mandatory documentation created at `docs/Ashfaq_Contribution.md`.

### Items Outside Ashfaq's Assigned Responsibility
As per project guidelines, the following modules are owned by other team members and remain untouched:
- Product Identity Matching (Ticket 2)
- Recall Database Search & CPSC/Recall API (Ticket 3)
- Evidence RAG & Vector Retrieval (Ticket 4)
- Human Review Workflow & Streamlit Web UI (Ticket 5)
