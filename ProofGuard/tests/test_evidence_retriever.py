
from app.db.models import (
    Product,
    Document,
    Recall,
    ProductRecallMatch,
    Evidence,
)
from app.rag.evidence_retriever import retrieve_and_save_evidence


def test_evidence_retrieval_and_duplicate_prevention(session):
    # Create a product.
    product = Product(
        product_name="Samsung Washing Machine",
        brand="Samsung",
        model_number="WA50B5100AW/US",
    )
    session.add(product)
    session.flush()

    # Create a product document.
    document = Document(
        product_id=product.id,
        file_name="product_manual.pdf",
        file_path="test/product_manual.pdf",
        extracted_text=(
            "Samsung washing machine model WA50B5100AW/US "
            "supports multiple washing cycles.\n"
            "This unrelated passage contains no matching model."
        ),
    )
    session.add(document)

    # Create a recall.
    recall = Recall(
        external_recall_id="TEST-001",
        product_name="Samsung Washing Machine",
        manufacturer="Samsung",
        model_numbers=["WA50B5100AW/US"],
        hazard_description="Risk of fire.",
        remedy="Contact Samsung for a free repair.",
        source_url="https://example.com/recall",
    )
    session.add(recall)
    session.flush()

    # Create the product-recall match.
    match = ProductRecallMatch(
        product_id=product.id,
        recall_id=recall.id,
        similarity_score=1.0,
    )
    session.add(match)
    session.commit()

    # First retrieval.
    results = retrieve_and_save_evidence(match.id, session)

    assert len(results) == 2

    document_evidence = [
        item for item in results
        if item.evidence_type == "product_document"
    ]

    recall_evidence = [
        item for item in results
        if item.evidence_type == "recall_record"
    ]

    assert len(document_evidence) == 1
    assert "WA50B5100AW/US" in document_evidence[0].evidence_text

    assert len(recall_evidence) == 1
    assert "Risk of fire." in recall_evidence[0].evidence_text

    # Second retrieval must not create duplicates.
    results_again = retrieve_and_save_evidence(match.id, session)

    assert len(results_again) == 2

    assert session.query(Evidence).filter_by(
        match_id=match.id
    ).count() == 2
