"""
ProofGuard - Document & Product Persistence Service
Author: Aswin (Team Lead) / Integration

Provides operations to persist uploaded documents and extracted product information
into SQLite database, retrieve metrics, and fetch recent records.
"""

from pathlib import Path
from typing import Any
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Document, Product, Recall
from app.schemas import ProductCreate


def save_processed_document(
    file_name: str,
    file_path: str,
    document_type: str | None,
    extracted_text: str | None,
    product_data: ProductCreate | dict[str, Any] | None = None,
    session: Session | None = None,
) -> tuple[Document, Product | None]:
    """
    Persist an uploaded document and its extracted product metadata to the database.
    Links the document to the product.
    """
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True

    try:
        db_product = None
        if product_data:
            if isinstance(product_data, ProductCreate):
                data_dict = product_data.model_dump()
            elif isinstance(product_data, dict):
                data_dict = product_data
            else:
                data_dict = None

            # Only create product record if at least one identifying field is present
            if data_dict and any(data_dict.values()):
                db_product = Product(
                    product_name=data_dict.get("product_name"),
                    brand=data_dict.get("brand"),
                    model_number=data_dict.get("model_number"),
                    serial_number=data_dict.get("serial_number"),
                    product_category=data_dict.get("product_category"),
                )
                session.add(db_product)
                session.flush()  # populate db_product.id

        doc = Document(
            product_id=db_product.id if db_product else None,
            file_name=file_name,
            file_path=str(file_path),
            document_type=document_type,
            extracted_text=extracted_text,
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        if db_product:
            session.refresh(db_product)

        return doc, db_product
    except Exception:
        session.rollback()
        raise
    finally:
        if should_close:
            session.close()


def get_dashboard_metrics(session: Session | None = None) -> dict[str, int]:
    """Retrieve summary counts for documents, processed items, products, and recalls."""
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True

    try:
        doc_count = session.scalar(select(func.count(Document.id))) or 0
        processed_count = session.scalar(
            select(func.count(Document.id)).where(Document.extracted_text.isnot(None))
        ) or 0
        product_count = session.scalar(select(func.count(Product.id))) or 0
        recall_count = session.scalar(select(func.count(Recall.id))) or 0

        return {
            "uploaded_documents": doc_count,
            "processed_documents": processed_count,
            "products_extracted": product_count,
            "recalls_available": recall_count,
        }
    finally:
        if should_close:
            session.close()


def get_recent_documents(limit: int = 10, session: Session | None = None) -> list[Document]:
    """Fetch the most recently uploaded documents."""
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True

    try:
        stmt = select(Document).order_by(desc(Document.uploaded_at)).limit(limit)
        return list(session.scalars(stmt).all())
    finally:
        if should_close:
            session.close()


def get_recent_products(limit: int = 10, session: Session | None = None) -> list[Product]:
    """Fetch the most recently extracted products."""
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True

    try:
        stmt = select(Product).order_by(desc(Product.created_at)).limit(limit)
        return list(session.scalars(stmt).all())
    finally:
        if should_close:
            session.close()


def get_available_recalls(
    limit: int = 50,
    search_query: str | None = None,
    session: Session | None = None,
) -> list[Recall]:
    """Fetch available recall records, optionally filtered by keyword."""
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True

    try:
        stmt = select(Recall).order_by(desc(Recall.created_at))
        if search_query and search_query.strip():
            q = f"%{search_query.strip()}%"
            stmt = stmt.where(
                (Recall.product_name.ilike(q))
                | (Recall.manufacturer.ilike(q))
                | (Recall.external_recall_id.ilike(q))
                | (Recall.hazard_description.ilike(q))
            )
        stmt = stmt.limit(limit)
        return list(session.scalars(stmt).all())
    finally:
        if should_close:
            session.close()
