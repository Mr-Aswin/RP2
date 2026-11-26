
from functools import lru_cache

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from langchain_core.documents import Document

from app.db.models import Evidence


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load the embedding model once and reuse it."""
    return SentenceTransformer(MODEL_NAME)


def retrieve_relevant_evidence(
    match_id: int,
    query: str,
    db: Session,
    top_k: int = 3,
) -> list[Document]:
    """
    Retrieve the most semantically relevant evidence
    for a product-recall match using FAISS.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    # Get evidence already stored for this match.
    evidence_records = (
        db.query(Evidence)
        .filter(Evidence.match_id == match_id)
        .all()
    )

    if not evidence_records:
        return []

    texts = [
        evidence.evidence_text
        for evidence in evidence_records
        if evidence.evidence_text and evidence.evidence_text.strip()
    ]

    if not texts:
        return []

    # Generate normalized embeddings.
    model = get_embedding_model()

    document_embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")

    # Build a FAISS index using cosine similarity.
    dimension = document_embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(document_embeddings)

    # Retrieve the top matching evidence passages.
    result_count = min(top_k, len(texts))

    scores, indices = index.search(
        query_embedding,
        result_count,
    )

    # Convert results into LangChain Documents.
    retrieved_documents = []

    valid_records = [
        evidence
        for evidence in evidence_records
        if evidence.evidence_text and evidence.evidence_text.strip()
    ]

    for score, position in zip(scores[0], indices[0]):
        if position < 0:
            continue

        evidence = valid_records[position]

        retrieved_documents.append(
            Document(
                page_content=evidence.evidence_text,
                metadata={
                    "evidence_id": evidence.id,
                    "match_id": evidence.match_id,
                    "document_id": evidence.document_id,
                    "evidence_type": evidence.evidence_type,
                    "source_url": evidence.source_url,
                    "similarity_score": float(score),
                },
            )
        )

    return retrieved_documents
