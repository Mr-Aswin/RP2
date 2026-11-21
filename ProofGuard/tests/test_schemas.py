import pytest
from pydantic import ValidationError
from app.schemas import ProductCreate, RecallCreate


def test_product_validation():
    product = ProductCreate(
        product_name="Refrigerator",
        brand="Samsung",
        model_number="RF28",
        serial_number="SN12345",
        product_category="Home Appliance",
    )
    assert product.product_name == "Refrigerator"
    assert product.brand == "Samsung"
    assert product.model_number == "RF28"
    assert product.serial_number == "SN12345"
    assert product.product_category == "Home Appliance"


def test_recall_validation():
    recall = RecallCreate(
        external_recall_id="CPSC-2026-001",
        product_name="Refrigerator",
        manufacturer="Samsung",
        model_numbers=["RF28", "RF29"],
        recall_date="2026-10-15",
        hazard_description="Electrical overheating risk",
        remedy="Contact manufacturer for repair",
        source_url="https://example.com/recall",
    )
    assert recall.external_recall_id == "CPSC-2026-001"
    assert recall.product_name == "Refrigerator"
    assert recall.model_numbers == ["RF28", "RF29"]


def test_default_model_numbers():
    recall_without_models = RecallCreate(
        external_recall_id="CPSC-2026-002"
    )
    assert recall_without_models.model_numbers == []


def test_required_recall_id():
    with pytest.raises(ValidationError):
        RecallCreate(product_name="Test Product")


def test_invalid_product_data():
    with pytest.raises(ValidationError):
        ProductCreate(
            product_name=123,
            brand="Samsung",
        )
