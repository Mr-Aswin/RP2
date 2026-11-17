from app.db.database import SessionLocal
from app.db.models import Product, Recall
from app.schemas import(
    ProductCreate, ProductResponse,RecallCreate,RecallResponse,
)

def test_product_integration(session):
    print("\n--- Product Integration Test ---")

    # 1. Prepare validated product data
    product_data = ProductCreate(
        product_name="Integration Test Refrigerator",
        brand="Samsung",
        model_number="TEST-RF-001",
        serial_number="TEST-SN-001",
        product_category="Home Appliance",
    )
    
    # 2. Convert Pydantic data into SQLAlchemy obj
    db_product = Product(**product_data.model_dump())
    
    # 3. Save the product in SQLite
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    print("Product saved with ID: ", db_product.id)

    # 4. Converting the SQLAlchemy obj into Pyantic responce
    product_response = ProductResponse.model_validate(db_product)
    print("Product response:")
    print(product_response.model_dump())
    assert product_response.brand == "Samsung"
    assert product_response.id == db_product.id

    # 5. Remove the test record
    session.delete(db_product)
    session.commit()
    print("Product integration test passed!")  


def test_recall_integration(session):
    print("\n--- RECALL INTEGRATION TEST ---")
    
    # 1. Prepare validated recall data
    recall_data = RecallCreate(
        external_recall_id="TEST-RECALL-001",
        product_name="Test Refrigerator",
        manufacturer="Samsung",
        model_numbers=["TEST-RF-001"],
        recall_date="2026-10-15",
        hazard_description="Test electrical hazard",
        remedy="Contact manufacturer",
        source_url="https://example.com/test-recall",       
    )
    
    #  2. Convert Pydantic data into SQLAlchemy obj
    db_recall = Recall(**recall_data.model_dump())

    # 3. Save the reacll in SQLite
    session.add(db_recall)
    session.commit()
    session.refresh(db_recall)
    print("Recall saved with ID:", db_recall.id)
    
    # 4. Convert SQLAlchemy object into a Pydantic response
    recall_response = RecallResponse.model_validate(db_recall)
    print("Recall response:")
    print(recall_response.model_dump())
    assert recall_response.external_recall_id == "TEST-RECALL-001"
    assert recall_response.model_numbers == ["TEST-RF-001"]

    # 5. Remove the test record
    session.delete(db_recall)
    session.commit()
    print("Recall integration test passed!")


if __name__ == "__main__":
    with SessionLocal() as session:
        try:
            test_product_integration(session)
            test_recall_integration(session)
            print("\nAll database-schema integration tests passed!")
        except Exception:
            session.rollback()
            raise