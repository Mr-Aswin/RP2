
import ollama

from app.rag.vector_retriever import retrieve_relevant_evidence


MODEL_NAME = "llama3.2:3b"


def generate_rag_response(
    match_id: int,
    query: str,
    db,
    top_k: int = 3,
) -> dict:
    """
    Retrieve relevant evidence and generate an
    evidence-grounded response using Ollama.
    """

    if not query or not query.strip():
        raise ValueError("Question cannot be empty")

    # Retrieve relevant evidence using FAISS.
    evidence_documents = retrieve_relevant_evidence(
        match_id=match_id,
        query=query,
        db=db,
        top_k=top_k,
    )

    if not evidence_documents:
        return {
            "answer": (
                "Insufficient evidence is available "
                "to answer this question."
            ),
            "evidence": [],
        }

    # Prepare evidence context for the LLM.
    context_parts = []
    evidence_sources = []

    for document in evidence_documents:
        context_parts.append(document.page_content)

        evidence_sources.append({
            "evidence_id": document.metadata["evidence_id"],
            "evidence_type": document.metadata["evidence_type"],
            "source_url": document.metadata["source_url"],
            "similarity_score": document.metadata[
                "similarity_score"
            ],
            "text": document.page_content,
        })

    context = "\n\n".join(context_parts)

    # Generate an answer using the local Ollama model.
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are ProofGuard, a product safety "
                    "recall analysis assistant. "
                    "Answer questions using only the "
                    "provided evidence. Do not invent "
                    "facts or unsupported conclusions. "
                    "If the evidence does not contain "
                    "enough information, clearly state "
                    "that there is insufficient evidence. "
                    "Distinguish product information "
                    "from recall information."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Evidence:\n{context}\n\n"
                    f"Question:\n{query}\n\n"
                    "Provide a clear answer based only "
                    "on the evidence above."
                ),
            },
        ],
        options={
            "temperature": 0.1,
        },
    )

    return {
        "answer": response.message.content,
        "evidence": evidence_sources,
    }
