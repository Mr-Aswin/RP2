# ProofGuard – Streamlit Frontend & Intelligence Dashboard
## Development Documentation for Vignesh

**Developer:** Vignesh  
**Module:** Step 5 / Step 6: Streamlit Upload Page & Dashboard Layout  
**Project:** ProofGuard – Cross-Document Product Identity & Evidence-Based Recall Intelligence  
**Repository:** https://github.com/Mr-Aswin/RP2  
**Branch:** `feature/vignesh-frontend`  

---

## 1. Assigned Responsibility
The frontend represents the user interface for ProofGuard:
```
User Document (PDF / Image) ──> Streamlit UI (Vignesh)
                                      ├──> Document Processing & OCR (Abhinav)
                                      ├──> Product Information Extraction (Arun / Ashfaq)
                                      ├──> Database Storage & Dashboard (Aswin)
                                      └──> CPSC Recall Intelligence Explorer (Ashfaq)
```
The goal of this module is to deliver an intuitive, responsive, and robust web dashboard enabling users to:
1. Upload product documents (PDFs, PNG, JPG, JPEG) with file format validation.
2. Trigger the processing pipeline (OCR followed by product identity extraction).
3. Inspect extracted product identity attributes (name, brand, model, serial number, category) alongside raw OCR text and structured JSON.
4. Persist processed documents and product records directly into the SQLite database.
5. Browse and query the 562 verified CPSC recall records with clear status indications.
6. Monitor operational dashboard metrics (uploaded documents, processed documents, products extracted, and available recalls).

---

## 2. Technical Stack & Dependencies

| Component | Technology | Version | Purpose |
|---|---|---|---|
| **Web Framework** | `streamlit` | 1.55.0 | Interactive web application and dashboard framework. |
| **Data Presentation** | `pandas` | 2.2.1 | Tabular formatting of recent products, documents, and CPSC recalls. |
| **Document Processing** | `PyMuPDF` + `pytesseract` | — | Text recovery via Abhinav's OCR module. |
| **Extraction Engine** | `spaCy` + `re` | — | Attribute extraction via Arun's canonical module. |
| **Data Persistence** | `SQLAlchemy` | 2.0.23 | Database interaction via Aswin's service layer. |

---

## 3. Implemented Views & User Workflows (`ui/app.py` & `app.py`)

### A. Dashboard Overview
- 4 Key Metric Cards:
  - Total Uploaded Documents
  - Processed Documents
  - Extracted Product Records
  - Available CPSC Recall Records
- Recent Extracted Products table showing ID, Brand, Model, Serial, Category, and Timestamp.
- Recent Document History table showing upload history and linked product IDs.
- Live System Status indicator in the sidebar showing database, OCR, NLP, and recall status.

### B. Document Upload & Extraction Interface
- Drag-and-drop file uploader supporting `.pdf`, `.png`, `.jpg`, `.jpeg`.
- Metadata preview displaying filename, format badge, and file size in KB.
- Execution button triggering the end-to-end pipeline:
  1. Temporary staging of uploaded file buffer.
  2. Text extraction via `app.ocr.document_processor.extract_text()`.
  3. Structured attribute extraction via `app.extraction.product_extractor.extract_product_info()`.
  4. Automatic persistence to SQLite via `app.services.document_service.save_processed_document()`.
- Result display:
  - Visual attribute cards for Product Name, Brand, Model Number, Serial Number, Category, and DB Record ID.
  - Expandable viewer for raw OCR text.
  - Expandable viewer for structured Pydantic JSON dump.

### C. CPSC Recall Intelligence Explorer
- Scope notice banner clarifying that automated matching (RapidFuzz / Evidence RAG) is scheduled for Ticket 2 & Ticket 4.
- Real-time keyword search across 562 official CPSC appliance and electronics records (by product name, manufacturer, model, hazard description, or recall ID).
- Slider control for page display density (10 to 200 records).
- Detailed single-record safety inspection inspector displaying hazard descriptions and corrective remedies.

### D. Architecture & About Page
- High-level architectural flowchart of the Ticket 1 foundation.
- Full team allocation table matching responsibilities to deliverables.

---

## 4. How to Launch the Application

```bash
# Option 1: Using the top-level launcher
streamlit run app.py

# Option 2: Using the ui/ directory path
streamlit run ui/app.py
```
Default URL: `http://localhost:8501`
