from datetime import datetime
from sqlalchemy import (String,Integer,Float,Text,DateTime,ForeignKey,JSON)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

#1. Products Table
class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer,primary_key=True,index = True)
    product_name: Mapped[str | None] = mapped_column(String(255), nullable = True)
    brand: Mapped[str | None] = mapped_column(String(150), nullable = True)
    model_number: Mapped[str | None] = mapped_column(String(150), nullable = True)
    serial_number: Mapped[str | None] = mapped_column(String(150), nullable = True)
    product_category: Mapped[str | None] = mapped_column(String(100), nullable = True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    documents: Mapped[list["Document"]] = relationship(back_populates="product")
    matches: Mapped[list["ProductRecallMatch"]] = relationship(back_populates="product")

#2. Documents Table
class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer,primary_key=True, index = True)
    product_id: Mapped[int| None] = mapped_column(ForeignKey("products.id"),nullable=True)
    file_name: Mapped[str] = mapped_column(String(255),nullable=False)
    file_path: Mapped[str] = mapped_column(String(500),nullable=False)
    document_type: Mapped[str|None] = mapped_column(String(100), nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow)
    product: Mapped["Product | None"] = relationship(back_populates="documents")
    evidence: Mapped[list["Evidence"]] = relationship(back_populates="document")

#3. Recalls Table
class Recall(Base):
    __tablename__ = "recalls"

    id: Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    external_recall_id: Mapped[str] = mapped_column(String(100),unique=True,nullable=False)
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model_numbers: Mapped[list] = mapped_column(JSON,default=list)
    recall_date: Mapped[str| None] = mapped_column(String(50),nullable=True)
    hazard_description: Mapped[str | None] = mapped_column(Text,nullable=True)
    remedy: Mapped[str | None] = mapped_column(Text,nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow)
    matches: Mapped[list["ProductRecallMatch"]] = relationship (back_populates="recall")

# 4. Product - Recall Matches Table
class ProductRecallMatch(Base):
    __tablename__ = "product_recall_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    recall_id: Mapped[int] = mapped_column(ForeignKey("recalls.id"), nullable=False)
    similarity_score: Mapped[float | None] = mapped_column(Float,nullable=True)
    match_status: Mapped[str] = mapped_column(String(50),default="pending_review")
    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow)
    product: Mapped["Product"] = relationship(back_populates="matches")
    recall: Mapped["Recall"] = relationship(back_populates="matches")
    evidence: Mapped[list["Evidence"]] = relationship( back_populates="match")


# 5. Evidence Table
class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("product_recall_matches.id"), nullable=False)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    evidence_text: Mapped[str] = mapped_column(Text,nullable=False)
    evidence_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    match: Mapped["ProductRecallMatch"] = relationship(back_populates="evidence")
    document: Mapped["Document | None"] = relationship(back_populates="evidence")

