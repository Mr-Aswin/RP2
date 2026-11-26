
import re

from sqlalchemy.orm import Session

from app.db.models import (
    ProductRecallMatch,
    Evidence,
)


def retrieve_and_save_evidence(
    match_id: int,
    db: Session,
) -> list[Evidence]:
    """
    Retrieve relevant product-document passages and recall
    information for a product-recall match.

    Save the retrieved evidence in the existing Evidence table.
    """

    match = (
        db.query(ProductRecallMatch)
        .filter(ProductRecallMatch.id == match_id)
        .first()
    )

    if not match:
        raise ValueError(f"Product-recall match {match_id} not found")

    product = match.product
    recall = match.recall

    # Collect model numbers for identifying relevant passages.
    model_numbers = set()

    if product.model_number:
        model_numbers.add(product.model_number.strip())

    if recall.model_numbers:
        model_numbers.update(
            model.strip()
            for model in recall.model_numbers
            if model and model.strip()
        )

    # Retrieve relevant passages from product documents.
    for document in product.documents:
        if not document.extracted_text:
            continue

        passages = re.split(
            r"\n+|(?<=[.!?])\s+",
            document.extracted_text,
        )

        for passage in passages:
            passage = passage.strip()

            if not passage:
                continue

            passage_lower = passage.casefold()

            # Match passages containing a known model number.
            relevant = any(
                model.casefold() in passage_lower
                for model in model_numbers
            )

            if not relevant:
                continue

            # Prevent duplicate evidence records.
            existing = (
                db.query(Evidence)
                .filter(
                    Evidence.match_id == match.id,
                    Evidence.document_id == document.id,
                    Evidence.evidence_text == passage,
                )
                .first()
            )

            if existing:
                continue

            evidence = Evidence(
                match_id=match.id,
                document_id=document.id,
                evidence_text=passage,
                evidence_type="product_document",
            )

            db.add(evidence)

    # Retrieve supporting information from the recall record.
    recall_details = []

    if recall.product_name:
        recall_details.append(
            f"Product: {recall.product_name}"
        )

    if recall.manufacturer:
        recall_details.append(
            f"Manufacturer: {recall.manufacturer}"
        )

    if recall.model_numbers:
        recall_details.append(
            f"Models: {', '.join(recall.model_numbers)}"
        )

    if recall.hazard_description:
        recall_details.append(
            f"Hazard: {recall.hazard_description}"
        )

    if recall.remedy:
        recall_details.append(
            f"Remedy: {recall.remedy}"
        )

    recall_text = "\n".join(recall_details)

    if recall_text:
        existing = (
            db.query(Evidence)
            .filter(
                Evidence.match_id == match.id,
                Evidence.document_id.is_(None),
                Evidence.evidence_text == recall_text,
            )
            .first()
        )

        if not existing:
            db.add(
                Evidence(
                    match_id=match.id,
                    document_id=None,
                    evidence_text=recall_text,
                    evidence_type="recall_record",
                    source_url=recall.source_url,
                )
            )

    db.commit()

    return (
        db.query(Evidence)
        .filter(Evidence.match_id == match.id)
        .all()
    )
