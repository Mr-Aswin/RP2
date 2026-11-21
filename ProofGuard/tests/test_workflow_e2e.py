"""
End-to-End Workflow Integration Test for Ticket 1
Tests the complete flow:
Document Ingestion -> OCR -> Product Extraction -> Database Persistence -> Recall Preview -> Dashboard Metrics
"""

from pathlib import Path
import pytest
from PIL import Image, ImageDraw, ImageFont

from app.ocr.document_processor import extract_text
from app.extraction.product_extractor import extract_product_info
from app.services.document_service import (
    save_processed_document,
    get_dashboard_metrics,
    get_available_recalls,
    get_recent_products,
)
from app.recalls.import_recalls import import_recalls_to_db


def test_complete_pdf_workflow(session):
    # 1. Verify sample PDF invoice exists
    invoice_path = Path("data/invoices/synthetic_product_invoice.pdf")
    assert invoice_path.exists(), f"Sample invoice missing at {invoice_path}"

    # 2. Extract text using OCR module (Abhinav)
    extracted_text = extract_text(invoice_path)
    assert len(extracted_text) > 0
    assert "SAMSUNG" in extracted_text.upper() or "WASHING" in extracted_text.upper()

    # 3. Extract product information (Arun / Ashfaq)
    product = extract_product_info(extracted_text)
    assert product.brand == "Samsung"
    assert product.model_number == "WW80T"
    assert product.product_category == "Home Appliance"

    # 4. Save to SQLite database (Aswin)
    doc, db_product = save_processed_document(
        file_name=invoice_path.name,
        file_path=str(invoice_path),
        document_type=".pdf",
        extracted_text=extracted_text,
        product_data=product,
        session=session,
    )

    assert doc.id is not None
    assert db_product is not None
    assert doc.product_id == db_product.id
    assert db_product.brand == "Samsung"

    # 5. Populate sample recalls and verify recall preview (Ashfaq)
    sample_recalls = [
        {
            "external_recall_id": "CPSC-E2E-001",
            "product_name": "Samsung Washing Machine",
            "manufacturer": "Samsung",
            "model_numbers": ["WW80T", "WA70B"],
            "recall_date": "2023-01-10",
            "hazard_description": "Overheating motor risk",
            "remedy": "Repair",
            "source_url": "https://example.com/cpsc-001",
        }
    ]
    import_recalls_to_db(records=sample_recalls, session=session)

    recalls = get_available_recalls(limit=10, search_query="Samsung", session=session)
    assert len(recalls) >= 1
    assert recalls[0].external_recall_id == "CPSC-E2E-001"

    # 6. Verify dashboard metrics reflect the stored data (Vignesh)
    metrics = get_dashboard_metrics(session=session)
    assert metrics["uploaded_documents"] >= 1
    assert metrics["processed_documents"] >= 1
    assert metrics["products_extracted"] >= 1
    assert metrics["recalls_available"] >= 1


def test_complete_image_workflow(tmp_path, session):
    # 1. Create a synthetic product label image (PNG)
    image_path = tmp_path / "product_label.png"
    img = Image.new("RGB", (1800, 700), "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=40)

    label_text = (
        "LG ELECTRONICS\n"
        "Product Name: Refrigerator\n"
        "Model No: GL-T432APZY\n"
        "Serial: LGSN998877\n"
        "Made by LG"
    )
    draw.text((80, 80), label_text, fill="black", font=font)
    img.save(image_path)

    # 2. OCR extraction from PNG
    text = extract_text(image_path)
    assert len(text) > 0
    assert "LG" in text.upper()

    # 3. Product attribute extraction
    product = extract_product_info(text)
    assert product.brand == "LG"
    assert product.model_number == "GL-T432APZY"

    # 4. Save to database
    doc, db_product = save_processed_document(
        file_name="product_label.png",
        file_path=str(image_path),
        document_type=".png",
        extracted_text=text,
        product_data=product,
        session=session,
    )

    assert doc.id is not None
    assert db_product is not None
    assert db_product.brand == "LG"
    assert db_product.model_number == "GL-T432APZY"
