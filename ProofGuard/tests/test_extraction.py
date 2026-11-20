"""
Unit and Integration Tests for Product Information Extraction Module
Author: Ashfaq (Ticket 1 - Data & System Foundation)
"""

from pathlib import Path
import pytest
from pydantic import ValidationError

from app.extraction.product_extractor import (
    classify_category,
    extract_brand,
    extract_model_number,
    extract_product_dict,
    extract_product_info,
    extract_product_name,
    extract_serial_number,
    preprocess_text,
)
from app.ocr.document_processor import extract_text
from app.schemas import ProductCreate


# ---------------------------------------------------------------------------
# 1. Successful extraction of all five fields
# ---------------------------------------------------------------------------
def test_extract_all_five_fields():
    sample_text = """
    SAMSUNG

    WASHING MACHINE

    Model Number: WA70BG4546BD

    Serial Number: SN12345678

    Manufactured by Samsung Electronics.
    """
    product = extract_product_info(sample_text)

    assert isinstance(product, ProductCreate)
    assert product.brand == "Samsung"
    assert product.product_name == "Washing Machine"
    assert product.model_number == "WA70BG4546BD"
    assert product.serial_number == "SN12345678"
    assert product.product_category == "Home Appliance"


# ---------------------------------------------------------------------------
# 2. Correct brand extraction
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text,expected_brand",
    [
        ("Brand: LG\nProduct: Refrigerator", "LG"),
        ("Manufacturer: Whirlpool Corporation\nModel: WP-100", "Whirlpool"),
        ("Make: Bosch\nItem: Dishwasher", "Bosch"),
        ("Manufactured by Sony Electronics Inc.", "Sony"),
        ("PHILIPS\nCoffee Maker\nModel: HD7431", "Philips"),
        ("HAIER REFRIGERATOR\nModel: HRF-622", "Haier"),
    ],
)
def test_brand_extraction(text, expected_brand):
    brand = extract_brand(preprocess_text(text))
    assert brand == expected_brand


def test_brand_extraction_unknown():
    # Brand should not be invented when not present
    text = "Product: Washing Machine\nModel: WM-001\nSerial: SN-999"
    brand = extract_brand(preprocess_text(text))
    assert brand is None


# ---------------------------------------------------------------------------
# 3. Correct model number extraction
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text,expected_model",
    [
        ("Model: WA70BG4546BD", "WA70BG4546BD"),
        ("Model No: RF28R7351SG/AA", "RF28R7351SG/AA"),
        ("Model Number: WW80T", "WW80T"),
        ("Product Model: OLED65C1PUB", "OLED65C1PUB"),
        ("Model Code: SM-G998B", "SM-G998B"),
        ("Model:\nWA70BG4546BD", "WA70BG4546BD"),
    ],
)
def test_model_number_extraction(text, expected_model):
    model = extract_model_number(preprocess_text(text))
    assert model == expected_model


def test_model_not_confused_with_invoice_date_phone():
    text = """
    TAX INVOICE
    Invoice Number: TEST-INV-2026-001
    Invoice Date: 15 November 2026
    Helpline: +1-800-555-0199
    Customer Phone: 9876543210
    Model Number: WW80T554DAN
    """
    model = extract_model_number(preprocess_text(text))
    assert model == "WW80T554DAN"
    assert "TEST-INV" not in (model or "")
    assert "2026" != model


# ---------------------------------------------------------------------------
# 4. Correct serial number extraction
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text,expected_serial",
    [
        ("Serial Number: SN12345678", "SN12345678"),
        ("Serial No: 987654321", "987654321"),
        ("S/N: ABC-9988-XYZ", "ABC-9988-XYZ"),
        ("SN: 4567890123", "4567890123"),
        ("Serial:\nSN99887766", "SN99887766"),
    ],
)
def test_serial_number_extraction(text, expected_serial):
    serial = extract_serial_number(preprocess_text(text))
    assert serial == expected_serial


def test_serial_not_confused_with_model():
    text = """
    Model Number: WA70BG4546BD
    Serial Number: SN88776655
    """
    cleaned = preprocess_text(text)
    model = extract_model_number(cleaned)
    serial = extract_serial_number(cleaned, exclude_model=model)

    assert model == "WA70BG4546BD"
    assert serial == "SN88776655"
    assert model != serial


# ---------------------------------------------------------------------------
# 5. Correct product category identification
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "product_name,text,expected_category",
    [
        ("Washing Machine", "", "Home Appliance"),
        ("Front Load Washing Machine", "", "Home Appliance"),
        ("Refrigerator", "", "Home Appliance"),
        ("Split Air Conditioner", "", "Home Appliance"),
        ("Vacuum Cleaner", "", "Home Appliance"),
        ("Microwave Oven", "", "Kitchen Appliance"),
        ("Convection Microwave Oven", "", "Kitchen Appliance"),
        ("Dishwasher", "", "Kitchen Appliance"),
        ("Coffee Maker", "", "Kitchen Appliance"),
        ("Television", "", "Electronics"),
        ("Smart Television", "", "Electronics"),
        ("Laptop", "", "Electronics"),
        ("Smartphone", "", "Electronics"),
    ],
)
def test_category_identification(product_name, text, expected_category):
    category = classify_category(product_name, text)
    assert category == expected_category


def test_category_unknown():
    # Unidentified category should return None
    category = classify_category("Industrial Turbine Valve", "Custom machining")
    assert category is None


# ---------------------------------------------------------------------------
# 6. Missing model number
# ---------------------------------------------------------------------------
def test_missing_model_number():
    text = """
    Samsung Refrigerator
    Serial Number: SN99887711
    Delivered on 10 Oct 2026
    """
    product = extract_product_info(text)
    assert product.brand == "Samsung"
    assert product.product_name == "Refrigerator"
    assert product.serial_number == "SN99887711"
    assert product.model_number is None


# ---------------------------------------------------------------------------
# 7. Missing serial number
# ---------------------------------------------------------------------------
def test_missing_serial_number():
    text = """
    LG Washing Machine
    Model Number: T70SPSF2Z
    Warranty: 2 Years
    """
    product = extract_product_info(text)
    assert product.brand == "LG"
    assert product.product_name == "Washing Machine"
    assert product.model_number == "T70SPSF2Z"
    assert product.serial_number is None


# ---------------------------------------------------------------------------
# 8. Empty input text
# ---------------------------------------------------------------------------
def test_empty_input_text():
    # Truly empty string
    empty_result = extract_product_info("")
    assert empty_result.product_name is None
    assert empty_result.brand is None
    assert empty_result.model_number is None
    assert empty_result.serial_number is None
    assert empty_result.product_category is None

    # Whitespace only
    ws_result = extract_product_info("   \n\t   \n  ")
    assert ws_result.product_name is None
    assert ws_result.brand is None


# ---------------------------------------------------------------------------
# 9. Invalid input type
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("invalid_input", [None, 12345, ["raw", "text"], {"key": "val"}])
def test_invalid_input_type(invalid_input):
    with pytest.raises(TypeError, match="must be a string"):
        extract_product_info(invalid_input)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 10. Different product document formats
# ---------------------------------------------------------------------------
def test_warranty_card_format():
    warranty_text = """
    ---------------------------------------------------------
    PRODUCT WARRANTY REGISTRATION
    ---------------------------------------------------------
    Make / Brand       : Whirlpool
    Equipment          : Microwave Oven
    Model Code         : MAGICOOK-20L
    Serial Identifier  : WP-SN-554433
    Date of Sale       : 2026-05-12
    Purchaser          : John Doe
    ---------------------------------------------------------
    """
    product = extract_product_info(warranty_text)
    assert product.brand == "Whirlpool"
    assert product.product_name == "Microwave Oven"
    assert product.model_number == "MAGICOOK-20L"
    assert product.serial_number == "WP-SN-554433"
    assert product.product_category == "Kitchen Appliance"


def test_user_manual_cover_format():
    manual_text = """
    OWNER'S MANUAL
    TELEVISION
    SONY BRAVIA
    Model: KD-55X80J
    Please read this manual before operating.
    Sony Corporation, Tokyo, Japan
    """
    product = extract_product_info(manual_text)
    assert product.brand == "Sony"
    assert "Television" in (product.product_name or "")
    assert product.model_number == "KD-55X80J"
    assert product.product_category == "Electronics"


# ---------------------------------------------------------------------------
# 11. Incorrect or ambiguous model/serial labels
# ---------------------------------------------------------------------------
def test_ambiguous_and_noisy_labels():
    noisy_text = """
    PURCHASE SPECIFICATION
    Model Year: 2026
    Model Number: WW90T684DLX
    Serial Batch: BATCH-01
    Serial No: SN-88990011
    Invoice Amount: INR 45,000
    Customer Care: 1800-200-1122
    Brand: Samsung
    Product: Front Load Washing Machine
    """
    product = extract_product_info(noisy_text)
    assert product.brand == "Samsung"
    assert product.model_number == "WW90T684DLX"
    assert product.serial_number == "SN-88990011"
    assert product.product_category == "Home Appliance"


# ---------------------------------------------------------------------------
# 12. Pydantic validation of the extracted result & dict output
# ---------------------------------------------------------------------------
def test_pydantic_validation_and_dict_output():
    raw_text = """
    Brand: Bosch
    Product Name: Dishwasher
    Model Number: SMS66GI01I
    Serial Number: BOSCH-SN-9911
    """
    product = extract_product_info(raw_text)
    assert isinstance(product, ProductCreate)

    # Validate against Pydantic schema methods
    dumped = product.model_dump()
    assert isinstance(dumped, dict)
    assert dumped["brand"] == "Bosch"
    assert dumped["product_name"] == "Dishwasher"
    assert dumped["model_number"] == "SMS66GI01I"
    assert dumped["serial_number"] == "BOSCH-SN-9911"
    assert dumped["product_category"] == "Kitchen Appliance"

    # Test extract_product_dict convenience function
    dict_res = extract_product_dict(raw_text)
    assert isinstance(dict_res, dict)
    assert dict_res == dumped


def test_database_compatibility(session):
    """
    Verify that the extracted ProductCreate result can be persisted directly
    into the existing SQLAlchemy Product model without schema discrepancies.
    """
    from app.db.models import Product

    raw_text = """
    Brand: LG
    Product: Refrigerator
    Model: GL-T432APZY
    Serial: LGSN998877
    """
    product_create = extract_product_info(raw_text)

    # Convert ProductCreate to database model instance
    db_product = Product(**product_create.model_dump())
    session.add(db_product)
    session.commit()
    session.refresh(db_product)

    assert db_product.id is not None
    assert db_product.brand == "LG"
    assert db_product.product_name == "Refrigerator"
    assert db_product.model_number == "GL-T432APZY"
    assert db_product.serial_number == "LGSN998877"
    assert db_product.product_category == "Home Appliance"


# ---------------------------------------------------------------------------
# 13. Integration with Abhinav's OCR Module
# ---------------------------------------------------------------------------
def test_integration_with_ocr_synthetic_invoice():
    invoice_path = Path("data/invoices/synthetic_product_invoice.pdf")
    assert invoice_path.exists(), f"Sample invoice not found at {invoice_path}"

    # Extract raw text using Abhinav's OCR module
    raw_text = extract_text(invoice_path)
    assert len(raw_text) > 0

    # Extract structured product information
    product = extract_product_info(raw_text)

    assert isinstance(product, ProductCreate)
    assert product.brand == "Samsung"
    assert product.model_number == "WW80T"
    assert product.product_category == "Home Appliance"
    assert "Washing Machine" in (product.product_name or "")
