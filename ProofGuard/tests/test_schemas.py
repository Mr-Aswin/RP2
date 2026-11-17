from pydantic import ValidationError
from app.schemas import ProductCreate, RecallCreate

# Test 1 -> Validate product information
product = ProductCreate(
    product_name="Refrigerator",
    brand="Samsung",
    model_number="RF28",
    serial_number="SN12345",
    product_category="Home Appliance",
)
print("Product validation successful!")
print(product.model_dump())


# Test 2 -> Validate recall info
recall = RecallCreate(
    external_recall_id="CPSC-2026-001",
    product_name="Refrigerator",
    manufacturer="Samsung",
    model_numbers=["RF28", "RF29"],
    recall_date="2026-10-15",
    hazard_description="Electrical overheating risk",
    remedy="Contact manufacturer for repair",
    source_url="https://example.com/recall"
)
print("\nRecall validation successful!")
print(recall.model_dump())


#  Test 3 -> Check defult model numbers

recall_without_models = RecallCreate(
    external_recall_id="CPSC-2026-002"
)
print("\nDefault model numbers:", recall_without_models.model_numbers)


# Test 4 -> Check required recall ID
try:
    RecallCreate(product_name="Test Product")
except ValidationError:
    print("\nRequired field validation successful!")
print("\nAll schema tests passed!")


# TEST 5: Invalid product data
try:
    ProductCreate(
        product_name=123,
        brand="Samsung"
    )
    print("Unexpected: Invalid product was accepted!")
except ValidationError as error:
    print("\nInvalid product correctly rejected!")
    print(error)