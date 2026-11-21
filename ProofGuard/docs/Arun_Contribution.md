# ProofGuard – Product Information Extraction Module
## Development Documentation for Arun Kumar S

**Developer:** Arun Kumar S  
**Module:** Step 3: Product Information Extraction  
**Project:** ProofGuard – Cross-Document Product Identity & Evidence-Based Recall Intelligence  
**Repository:** https://github.com/Mr-Aswin/RP2  
**Branch:** `feature/arun-product-extraction`  

---

## 1. Assigned Responsibility
The Product Information Extraction module is Step 3 in the ProofGuard pipeline:
```
User Document → OCR (Abhinav) → Product Information Extraction (Arun) → Product Identity Matching → Evidence RAG → User Report
```
The goal of this module is to parse raw text extracted from documents (invoices, manuals, warranty certificates, labels) and produce structured product identity attributes validated against the existing `ProductCreate` schema:
1. `product_name` (e.g., `Front Load Washing Machine`, `Refrigerator`, `Smart Television`)
2. `brand` (e.g., `Samsung`, `LG`, `Whirlpool`, `Bosch`, `Sony`)
3. `model_number` (e.g., `WA70BG4546BD`, `WW80T`, `FHT1408ZWL`)
4. `serial_number` (e.g., `SN12345678`, `908KWEC12345`, `0A1B2C3D4E`)
5. `product_category` (`Home Appliance`, `Kitchen Appliance`, `Electronics`)

---

## 2. Files Created or Modified

### Files Modified:
1. `ProofGuard/app/extraction/product_extractor.py`:
   - Enhanced input handling to support `None` gracefully alongside empty strings.
   - Added regex pattern support for `M/N:` (Model Number abbreviation) and `M.No:`.
   - Added regex pattern support for `S.No:` (Serial Number abbreviation).
   - Added support for `Made by` manufacturer declarations.
   - Expanded known brand gazetteer (Siemens, Sharp, BPL, Videocon, Onida, Intex, Realme, Vivo, Oppo, Nokia, Motorola, JBL, Bose, Havells, V-Guard, Prestige, Pigeon, Butterfly, Preethi).
   - Enhanced OCR text noise cleaning in preprocessing.
2. `ProofGuard/tests/test_extraction.py`:
   - Added `test_none_input()` to ensure `None` input returns an empty `ProductCreate` instance rather than crashing.
   - Added `test_mn_and_sno_patterns()` verifying extraction of `M/N:` and `S.No:`.
   - Added `test_noisy_ocr_text()` checking extraction accuracy through OCR formatting artifacts.
   - Added `test_text_containing_no_product_details()` ensuring no hallucination on general legal/policy text.
   - Added `test_partial_product_information()` testing graceful handling when only brand/category are present.
   - Total test count expanded to **54 passing tests** (52 unit tests + 2 integration tests).

### Files Created:
1. `ProofGuard/docs/Arun_Contribution.md`:
   - Complete technical record of Arun Kumar S's contributions, architecture, rules, and verification.

---

## 3. How Product Information Extraction Works

The extraction engine operates as a sequential, rule-based, and NLP-assisted pipeline:

```
Raw Document Text / OCR Output
             │
             ▼
   [ Text Normalization ]
   - Handle None / empty inputs safely
   - Normalize Unicode to NFKC
   - Clean spacing while preserving lines
             │
             ▼
      [ spaCy NLP ]
   - Tokenization & Named Entity Recognition (ORG)
             │
             ▼
     [ Field Extractors ]
   1. Brand: Labels (Brand, Make, Mfr), "Manufactured by", "Made by", spaCy ORG, Brand Gazetteer
   2. Model: "Model:", "Model No:", "M/N:", "Product Model:", line-break codes, noise filtering
   3. Serial: "Serial:", "Serial No:", "S/N:", "S.No:", model disambiguation
   4. Name: "Product Name:", "Equipment:", "Appliance:", canonical product patterns
   5. Category: Home Appliance / Kitchen Appliance / Electronics classification
             │
             ▼
    [ Pydantic Validation ]
   - Instantiates ProductCreate(**extracted_data)
   - Returns validated ProductCreate instance or dict
```

---

## 4. How Regular Expressions (`re`) Are Used

Regular expressions provide deterministic, explainable extraction:
- **Model Patterns:**
  ```python
  r"(?i)\b(?:product\s+)?(?:model(?:\s+(?:number|no\.?|code|id|#))?|m\/n|m\.?no\.?)[\t ]*[:=–-]+[\t ]*([A-Za-z0-9][A-Za-z0-9\-_\./]{1,35})"
  ```
  Matches `Model: WA70B`, `Model No: RF28`, `M/N: FHT1408ZWL`, `Product Model: OLED65`.
- **Serial Patterns:**
  ```python
  r"(?i)\b(?:serial(?:\s+(?:number|no\.?|id|#|identifier))?|s\/n|sr\.?\s*no\.?|s\.?\s*no\.?|sn)[\t ]*[:=–-]+[\t ]*([A-Za-z0-9][A-Za-z0-9\-_\./]{2,35})"
  ```
  Matches `Serial Number: SN1234`, `S/N: ABC-99`, `S.No: 908KWEC`.
- **Negative Filtering:**
  Regexes for invoice patterns (`r"\b(?:INV|INVOICE|TEST-INV)[-_#:\s]*[A-Za-z0-9-_]+\b"`), phone numbers, and dates prevent confusing non-product identifiers with model or serial numbers.

---

## 5. How spaCy Is Used

- **Model:** `en_core_web_sm`
- **Singleton Loader:** `get_nlp()` lazy-loads the model once, caching it globally across subsequent requests to eliminate memory and latency overhead.
- **Named Entity Recognition (NER):** Detects `ORG` entities to discover corporate entity mentions (e.g. `Samsung Electronics Inc.`, `Sony Corporation`) and map them to standard brand identities.
- **Safety Fallback:** If the `en_core_web_sm` package is missing on a host, it automatically falls back to `spacy.blank("en")` with a warning, ensuring zero crashes.

Installation command if needed:
```bash
python -m spacy download en_core_web_sm
```

---

## 6. Supported Product Fields

| Field | Source / Logic | Fallback |
|---|---|---|
| `product_name` | Explicit label or canonical product regex match | `None` |
| `brand` | Explicit label, manufacturer declaration, NER, gazetteer | `None` |
| `model_number` | Labeled alphanumeric model code (filtered from invoice/date/phone) | `None` |
| `serial_number` | Labeled serial code (distinct from model number) | `None` |
| `product_category` | Mapped from product name or text keyword scoring | `None` |

---

## 7. Supported Product Categories

The classifier supports three initial core categories:
1. **Home Appliance:** Washing Machine (front, top, semi-automatic), Clothes Dryer, Refrigerator (double door, French door), Air Conditioner, Vacuum Cleaner, Water Heater, Air Purifier.
2. **Kitchen Appliance:** Microwave Oven, Dishwasher, Induction Cooktop, Mixer Grinder, Blender, Coffee Maker, Electric Kettle, Air Fryer, Toaster.
3. **Electronics:** Television (Smart TV, OLED), Laptop, Smartphone, Tablet, Desktop Computer, Monitor, Headphones, Camera, Printer.

*Unidentified or ambiguous products return `None` to prevent fabrication.*

---

## 8. How to Run the Extractor

```python
from app.ocr.document_processor import extract_text
from app.extraction.product_extractor import extract_product_info

# 1. Extract text using Abhinav's OCR module
raw_text = extract_text("data/invoices/synthetic_product_invoice.pdf")

# 2. Extract structured product info
product = extract_product_info(raw_text)

# 3. Access validated attributes or export as dict
print(product.brand)           # "Samsung"
print(product.model_number)    # "WW80T"
print(product.model_dump())    # dictionary format
```

---

## 9. How to Run the Tests

```bash
# Run extraction tests
python -m pytest tests/test_extraction.py -v

# Run extraction and integration tests
python -m pytest tests/test_extraction.py tests/test_integration.py -v
```

---

## 10. Test Results

**54 passed out of 54 tests (100% pass rate)**:
- 52 unit tests in `tests/test_extraction.py` covering:
  - Full 5-field extraction
  - Labeled and manufacturer brand variants
  - Model patterns (including `M/N:`)
  - Serial patterns (including `S.No:`)
  - Noise & collision prevention (dates, phones, invoice IDs)
  - Category classification (13 parameterizations)
  - Missing fields (model, serial)
  - Empty text (`""`)
  - `None` input handling
  - Invalid types (`int`, `list`, `dict`)
  - Noisy OCR text
  - Partial product information
  - Non-product text
  - Real warranty card and user manual document formats
  - Pydantic `ProductCreate` validation & dictionary export
  - Database persistence into SQLite `Product` table
- 2 integration tests in `tests/test_integration.py` (`test_product_integration`, `test_recall_integration`).

---

## 11. Current Limitations

1. **Category Scope:** Supports `Home Appliance`, `Kitchen Appliance`, and `Electronics`. Industrial machinery or automotive parts safely return `None`.
2. **Tesseract Dependency for Scanned PDFs:** `app/ocr/document_processor.py` requires Tesseract executable for scanned image pages. Selectable PDFs and text strings operate without external dependencies.
3. **Unknown Brands:** Unlisted niche brands require explicit contextual labels (`Brand:`, `Make:`) to be extracted accurately.

---

## 12. Connection to Abhinav's OCR Module

The module connects cleanly without modifying Abhinav's code:
```python
from app.ocr.document_processor import extract_text
from app.extraction.product_extractor import extract_product_info

text = extract_text("data/invoices/synthetic_product_invoice.pdf")
product = extract_product_info(text)
```
This loose coupling ensures OCR logic and extraction logic remain independently maintainable and testable.
