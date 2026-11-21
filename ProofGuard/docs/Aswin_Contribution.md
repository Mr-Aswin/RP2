# ProofGuard – Project Foundation & Architecture
## Development Documentation for Aswin S (Team Lead)

**Developer:** Aswin S  
**Role:** Technical Lead & Architect  
**Module:** Step 1: Architecture, GitHub Setup, Database Schema, Project Foundation  
**Project:** ProofGuard – Cross-Document Product Identity & Evidence-Based Recall Intelligence  
**Repository:** https://github.com/Mr-Aswin/RP2  

---

## 1. Assigned Responsibility
As Team Lead and Architect, Aswin established the core system foundation for ProofGuard:
1. Designed the end-to-end repository structure, package layout, and Git workflows.
2. Formulated the multi-table relational database schema supporting products, documents, recalls, matches, and evidence.
3. Implemented SQLAlchemy ORM models (`app/db/models.py`) and SQLite connection engine (`app/db/database.py`).
4. Designed Pydantic v2 schemas (`app/schemas.py`) for clean validation, serialization, and boundary enforcement.
5. Implemented the database initialization utility (`app/db/init_db.py`).
6. Built the core document and product persistence service (`app/services/document_service.py`) supporting the Streamlit frontend.
7. Orchestrated integration between OCR (Abhinav), Recall Dataset (Ashfaq), Product Extraction (Arun), and Frontend (Vignesh).

---

## 2. Implemented Architecture & Database Schema

The SQLite database (`proofguard.db`) comprises 5 interrelated tables:

```
┌─────────────────────┐            ┌───────────────────────────┐
│      products       │ 1        * │         documents         │
├─────────────────────┤◄───────────┼───────────────────────────┤
│ id (PK)             │            │ id (PK)                   │
│ product_name        │            │ product_id (FK -> prod)   │
│ brand               │            │ file_name                 │
│ model_number        │            │ file_path                 │
│ serial_number       │            │ document_type             │
│ product_category    │            │ extracted_text            │
│ created_at          │            │ uploaded_at               │
└──────────┬──────────┘            └─────────────┬─────────────┘
           │ 1                                   │ 1
           │                                     │
           │ *                                   │ *
┌──────────▼──────────┐            ┌─────────────▼─────────────┐
│product_recall_match │ 1        * │         evidence          │
├─────────────────────┼───────────►├───────────────────────────┤
│ id (PK)             │            │ id (PK)                   │
│ product_id (FK)     │            │ match_id (FK -> match)    │
│ recall_id (FK)      │            │ document_id (FK -> doc)   │
│ similarity_score    │            │ evidence_text             │
│ match_status        │            │ evidence_type             │
│ created_at          │            │ source_url                │
└──────────▲──────────┘            │ created_at                │
           │ *                     └───────────────────────────┘
           │
           │ 1
┌──────────┴──────────┐
│       recalls       │
├─────────────────────┤
│ id (PK)             │
│ external_recall_id  │ (Unique)
│ product_name        │
│ manufacturer        │
│ model_numbers (JSON)│
│ recall_date         │
│ hazard_description  │
│ remedy              │
│ source_url          │
│ created_at          │
└─────────────────────┘
```

---

## 3. Key Modules & Services Created

1. **`app/db/database.py`**: SQLite database engine and session factory (`SessionLocal`, `Base`).
2. **`app/db/models.py`**: SQLAlchemy 2.0 mapped ORM models (`Product`, `Document`, `Recall`, `ProductRecallMatch`, `Evidence`).
3. **`app/db/init_db.py`**: Automated schema initializer and table inspector.
4. **`app/schemas.py`**: Pydantic v2 schemas (`ProductBase`, `ProductCreate`, `ProductResponse`, `RecallBase`, `RecallCreate`, `RecallResponse`).
5. **`app/services/document_service.py`**: High-level persistence API connecting uploaded files, OCR text, and extracted products to the database, plus dashboard metrics aggregation.
6. **`tests/test_integration.py`**: Integration verification between Pydantic schemas and SQLAlchemy models.
7. **`tests/test_schemas.py`**: Unit tests for schema validation rules.
8. **`tests/test_document_service.py`**: Unit tests for document and product database persistence.

---

## 4. Execution & Verification

```bash
# Initialize SQLite database
python -m app.db.init_db

# Run schema and foundation tests
python -m pytest tests/test_schemas.py tests/test_integration.py tests/test_document_service.py -v
```
All foundation components pass with zero warnings.
