import uuid

from database.models import DocumentChunk
from retrieval.semantic_search import semantic_search


def multi_document_search(
    query: str,
    document_ids: list[uuid.UUID],
    per_document_k: int = 3,
    final_k: int = 8,
) -> list[DocumentChunk]:

    collected = []
    seen_ids = set()

    # Retrieve evidence independently from every selected document.
    for document_id in document_ids:
        results = semantic_search(
            query=query,
            top_k=per_document_k,
            document_ids=[document_id],
        )

        for chunk in results:
            if chunk.id in seen_ids:
                continue

            collected.append(chunk)
            seen_ids.add(chunk.id)

    return collected[:final_k]