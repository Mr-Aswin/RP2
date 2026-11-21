# ProofGuard — Cross-Document Product Identity & Evidence-Based Recall Intelligence

**Ticket 1 Deliverable:** System Foundation, Document OCR Processing, Canonical Product Information Extraction, Official CPSC Recall Intelligence Dataset, and Initial Streamlit Web Interface.

---

## 1. Project Overview

ProofGuard is a Python-based intelligence platform designed to protect consumers and organizations by extracting verifiable product identities from heterogeneous documents (purchase invoices, user manuals, warranty certificates, labels) and comparing them against official consumer recall databases.

Ticket 1 establishes the verified system foundation, connecting document processing, entity extraction, relational SQLite persistence, official regulatory recall datasets, and a Streamlit dashboard.

---

## 2. Directory Structure

```text
ProofGuard/
├── app/
│   ├── api/                  # API entrypoints (FastAPI stub for Ticket 3)
│   ├── db/                   # Database configuration, engine, and models
│   │   ├── database.py       # SQLite connection & SessionLocal
│   │   ├── init_db.py        # Schema initialization script
│   │   └── models.py         # SQLAlchemy 2.0 ORM models (Product, Document, Recall, etc.)
│   ├── extraction/           # Product information extraction module
│   │   └── product_extractor.py # Canonical extraction engine (Regex + spaCy NER)
│   ├── matching/             # Placeholder for future Ticket 2 matching
│   ├── ocr/                  # Document processing & OCR module
│   │   └── document_processor.py # PyMuPDF + Tesseract OCR fallback
│   ├── rag/                  # Placeholder for future Ticket 4 evidence RAG
│   ├── recalls/              # CPSC Recall collection & database import
│   │   ├── cpsc_collector.py # Official CPSC SaferProducts API scraper & cleaner
│   │   └── import_recalls.py # SQLite database import & upsert utility
│   ├── services/             # Application services
│   │   └── document_service.py # Persistence & dashboard metrics service
│   └── schemas.py            # Pydantic v2 schemas (ProductCreate, RecallCreate, etc.)
├── data/
│   ├── invoices/             # Sample invoice documents (synthetic PDF)
│   ├── manuals/              # Real manufacturer manuals (Samsung, LG PDFs)
│   └── recalls/              # Official CPSC datasets (562 verified records)
│       ├── cpsc_recalls.csv  # CSV export
│       ├── cpsc_recalls.json # JSON structured dataset
│       └── collection_metadata.json # Collection provenance metadata
├── docs/                     # Team contribution records & Ticket 1 report
│   ├── Abhinav_Contribution.md
│   ├── Arun_Contribution.md
│   ├── Ashfaq_Contribution.md
│   ├── Aswin_Contribution.md
│   ├── Vignesh_Contribution.md
│   └── TICKET_1_COMPLETION_REPORT.md
├── tests/                    # Pytest test suite (80 passing tests)
│   ├── conftest.py           # In-memory SQLite session fixture
│   ├── test_document_service.py
│   ├── test_extraction.py
│   ├── test_integration.py
│   ├── test_ocr.py
│   ├── test_recalls.py
│   ├── test_schemas.py
│   └── test_workflow_e2e.py
├── ui/                       # Frontend application
│   └── app.py                # Multi-view Streamlit dashboard
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore configuration
├── app.py                    # Top-level Streamlit launcher
└── requirements.txt          # Python project dependencies
```

---

## 3. Team Responsibilities & Contributions

| Team Member | Original Assignment | Delivered Module | Tests |
|---|---|---|:---:|
| **Aswin (Lead)** | Architecture, DB Schema, Setup | `app/db/`, `app/schemas.py`, `app/services/document_service.py`, `init_db.py` | 9 |
| **Abhinav** | PDF Extraction & OCR Fallback | `app/ocr/document_processor.py` (PyMuPDF + Tesseract fallback) | 11 |
| **Ashfaq** | CPSC Recall Data Collection | `app/recalls/cpsc_collector.py`, `import_recalls.py`, 562 CPSC records | 6 |
| **Arun** | Product Information Extraction | `app/extraction/product_extractor.py` (Regex, spaCy NER, gazetteer) | 52 |
| **Vignesh** | Streamlit Frontend & Dashboard | `ui/app.py`, `app.py` (Upload, OCR preview, Extraction cards, CPSC explorer) | 2 (E2E) |

---

## 4. Installation & Environment Setup

### Prerequisites
- **Python:** 3.11+
- **Tesseract OCR:** Required for scanned PDFs and image files.
  - *Windows:* Download installer from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and install to `C:\Program Files\Tesseract-OCR\tesseract.exe`.
  - *Linux (Ubuntu/Debian):* `sudo apt update && sudo apt install -y tesseract-ocr`
  - *macOS:* `brew install tesseract`

### Virtual Environment Setup
```bash
# Navigate to the ProofGuard directory
cd ProofGuard

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (cmd):
.\venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download the spaCy English NLP model
python -m spacy download en_core_web_sm
```

---

## 5. Database Initialization & Data Import

```bash
# Initialize SQLite tables (creates proofguard.db)
python -m app.db.init_db

# (Optional) Re-fetch or update CPSC recall records from official API
python -m app.recalls.cpsc_collector

# Import verified CPSC recall records into SQLite database
python -m app.recalls.import_recalls
```

---

## 6. Running the Streamlit Application

```bash
# Launch Streamlit web UI
streamlit run app.py
# or
streamlit run ui/app.py
```
Open your browser at `http://localhost:8501`.

### Application Features:
1. **📊 Dashboard:** High-level metrics for uploaded documents, processed documents, extracted products, and available recall records.
2. **📄 Document Upload & Extraction:** Drag and drop PDF invoices, user manuals, or PNG/JPG photos. Run OCR and view extracted brand, product name, model number, serial number, and category with automatic SQLite persistence.
3. **🔍 CPSC Recall Intelligence:** Search and browse through 562 official CPSC product recall records with hazard descriptions and manufacturer remedies.
4. **ℹ️ Architecture & About:** System workflow diagram and team allocation matrix.

---

## 7. Running the Automated Test Suite

```bash
# Run the complete test suite (80 tests)
python -m pytest tests/ -v

# Run specific module tests
python -m pytest tests/test_ocr.py -v
python -m pytest tests/test_extraction.py -v
python -m pytest tests/test_recalls.py -v
python -m pytest tests/test_document_service.py -v
python -m pytest tests/test_schemas.py -v
python -m pytest tests/test_workflow_e2e.py -v
```

All 80 tests execute and pass in approximately 10 seconds.

---

## 8. Current Capabilities (Ticket 1)

- **Document Ingestion:** Text-based PDFs (PyMuPDF), scanned image PDFs (200 DPI rasterization + Tesseract), and standalone images (PNG, JPG, JPEG).
- **Product Entity Extraction:** Deterministic and explainable extraction of Brand, Model Number, Serial Number, Product Name, and Category (`Home Appliance`, `Kitchen Appliance`, `Electronics`).
- **Official CPSC Recall Intelligence:** 562 real recall records collected from the official CPSC SaferProducts.gov public API, cleaned, normalized, de-duplicated, and stored in JSON, CSV, and SQLite.
- **Relational Persistence:** SQLite database with SQLAlchemy 2.0 ORM models for Products, Documents, Recalls, Matches, and Evidence.
- **Interactive UI:** Streamlit interface for upload, real-time OCR inspection, attribute visualization, recall searching, and metrics monitoring.

---

## 9. Known Limitations & Intentionally Postponed Features

The following items are **strictly out of scope for Ticket 1** and are intentionally postponed to subsequent project phases:
- **RapidFuzz Cross-Document Matching:** Automated fuzzy comparison between extracted product identity and recall records (Ticket 2).
- **RAG & Vector Database:** Retrieval-Augmented Generation using FAISS / Chroma and Hugging Face / Ollama embeddings (Ticket 4).
- **AI Safety Assessments & LLM Summaries:** Generative hazard summaries and confidence scorings (Ticket 4).
- **FastAPI Production Backend:** External REST API endpoints (Ticket 3).
- **Final Report Generation & Export:** PDF risk intelligence report generation (Ticket 5).
