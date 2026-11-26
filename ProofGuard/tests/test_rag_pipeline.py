
from types import SimpleNamespace

from app.db.models import (
    Product,
    Recall,
    ProductRecallMatch,
    Evidence,
)
from app.rag.rag_pipeline import generate_rag_response


def test_rag_pipeline(session, monkeypatch):
    product = Product(
        product_name="Samsung Washing Machine",
        brand="Samsung",
        model_number="WA50B5100AW/US",
    )
    session.add(product)
    session.flush()

    recall = Recall(
        external_recall_id="RAG-TEST-001",
        product_name="Samsung Washing Machine",
        manufacturer="Samsung",
        model_numbers=["WA50B5100AW/US"],
        hazard_description=(
            "The washing machine may overheat and cause a fire."
        ),
        remedy="Contact Samsung for repair.",
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

    session.add(
        Evidence(
            match_id=match.id,
            evidence_text=(
                "The Samsung washing machine model "
                "WA50B5100AW/US may overheat and cause a fire."
            ),
            evidence_type="recall_record",
            source_url="https://example.com/recall",
        )
    )
    session.commit()

    # Mock the Ollama response so this test does not
    # need to generate another real LLM response.
    def fake_ollama_chat(**kwargs):
        assert kwargs["model"] == "llama3.2:3b"
        assert "fire" in kwargs["messages"][1]["content"].lower()

        return SimpleNamespace(
            message=SimpleNamespace(
                content="The washing machine may overheat and cause a fire."
            )
        )

    monkeypatch.setattr(
        "app.rag.rag_pipeline.ollama.chat",
        fake_ollama_chat,
    )

    result = generate_rag_response(
        match_id=match.id,
        query="What is the safety hazard?",
        db=session,
        top_k=3,
    )

    assert "fire" in result["answer"].lower()
    assert len(result["evidence"]) == 1
    assert result["evidence"][0]["evidence_type"] == "recall_record"
    assert result["evidence"][0]["source_url"] == (
        "https://example.com/recall"
    )
