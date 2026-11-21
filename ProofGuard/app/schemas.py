from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

# Product Schemas
class ProductBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    product_name: str | None = None
    brand : str | None = None
    model_number: str | None = None
    serial_number: str | None = None
    product_category: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


# Recall Schemas
class RecallBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    product_name: str | None = None
    manufacturer: str | None = None
    model_numbers: list[str] = []
    recall_date:  str | None = None
    hazard_description: str | None = None
    remedy: str | None = None
    source_url: str | None = None


class RecallCreate(RecallBase):
    external_recall_id: str


class RecallResponse(RecallBase):
    id: int
    external_recall_id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
