
from app.db.models import (
    Product,
    Recall,
    ProductRecallMatch,
    Evidence,
)
from app.rag.vector_retriever import retrieve_relevant_evidence


def test_vector_retrieval_returns_relevant_evidence(session):
    product = Product(
        product_name="Samsung Washing Machine",
        brand="Samsung",
        model_number="WA50B5100AW/US",
    )
    session.add(product)
    session.flush()

    recall = Recall(
        external_recall_id="VECTOR-TEST-001",
        product_name="Samsung Washing Machine",
        manufacturer="Samsung",
        model_numbers=["WA50B5100AW/US"],
        hazard_description="The washing machine may overheat and cause a fire.",
        remedy="Contact the manufacturer for repair.",
        source_url="https://example.com/recall",
    )
    session.add(recall)
    session.flush()

    match = ProductRecallMatch(
        product_id=product.id,
        recall_id=recall.id,
        similarity_score=1.0,
    )
    session.add(match)
    session.flush()

    session.add_all([
        Evidence(
            match_id=match.id,
            evidence_text=(
                "The washing machine may overheat and create "
                "a fire hazard during operation."
            ),
            evidence_type="recall_record",
        ),
        Evidence(
            match_id=match.id,
            evidence_text=(
                "The appliance has a stainless steel drum "
                "and multiple washing cycles."
            ),
            evidence_type="product_document",
        ),
    ])
    session.commit()

    results = retrieve_relevant_evidence(
        match_id=match.id,
        query="What is the fire risk associated with this washing machine?",
        db=session,
        top_k=2,
    )

    assert len(results) == 2
    assert "fire" in results[0].page_content.lower()
    assert results[0].metadata["match_id"] == match.id
    assert "similarity_score" in results[0].metadata
