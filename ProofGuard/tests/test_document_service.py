"""
Unit Tests for Document and Product Persistence Service
"""

import pytest
from app.schemas import ProductCreate
from app.services.document_service import (
    save_processed_document,
    get_dashboard_metrics,
    get_recent_documents,
    get_recent_products,
)
from app.db.models import Document, Product


def test_save_processed_document_with_product(session):
    product_data = ProductCreate(
        product_name="Front Load Washing Machine",
        brand="Samsung",
        model_number="WW80T",
        serial_number="SN12345678",
        product_category="Home Appliance",
    )
    doc, prod = save_processed_document(
        file_name="test_invoice.pdf",
        file_path="/path/to/test_invoice.pdf",
        document_type=".pdf",
        extracted_text="Samsung Washing Machine WW80T SN12345678",
        product_data=product_data,
        session=session,
    )

    assert doc.id is not None
    assert prod is not None
    assert prod.id is not None
    assert doc.product_id == prod.id
    assert prod.brand == "Samsung"
    assert prod.model_number == "WW80T"

    metrics = get_dashboard_metrics(session=session)
    assert metrics["uploaded_documents"] >= 1
    assert metrics["processed_documents"] >= 1
    assert metrics["products_extracted"] >= 1


def test_save_processed_document_without_product(session):
    doc, prod = save_processed_document(
        file_name="unidentified.pdf",
        file_path="/path/to/unidentified.pdf",
        document_type=".pdf",
        extracted_text="General Terms and Conditions",
        product_data=None,
        session=session,
    )

    assert doc.id is not None
    assert prod is None
    assert doc.product_id is None
