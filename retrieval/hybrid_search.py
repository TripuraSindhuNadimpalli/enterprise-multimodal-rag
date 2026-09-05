from database.models import DocumentChunk
from retrieval.keyword_search import keyword_search
from retrieval.semantic_search import semantic_search


def hybrid_search(
    query: str,
    top_k: int = 10,
) -> list[DocumentChunk]:

    semantic_results = semantic_search(
        query=query,
        top_k=top_k,
    )

    keyword_results = keyword_search(
        query=query,
        top_k=top_k,
    )

    scores = {}
    chunks = {}

    # Reciprocal Rank Fusion
    k = 60

    for rank, chunk in enumerate(semantic_results, start=1):
        chunks[chunk.id] = chunk

        scores[chunk.id] = (
            scores.get(chunk.id, 0)
            + 1 / (k + rank)
        )

    for rank, chunk in enumerate(keyword_results, start=1):
        chunks[chunk.id] = chunk

        scores[chunk.id] = (
            scores.get(chunk.id, 0)
            + 1 / (k + rank)
        )

    ranked_ids = sorted(
        scores,
        key=scores.get,
        reverse=True,
    )

    return [
        chunks[chunk_id]
        for chunk_id in ranked_ids[:top_k]
    ]