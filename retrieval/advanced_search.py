from retrieval.hybrid_search import hybrid_search
from retrieval.reranker import rerank


def diversify_by_page(
    chunks,
    top_k: int = 5,
    max_per_page: int = 1,
):
    selected = []
    page_counts = {}

    for chunk in chunks:
        page = chunk.page_number

        current_count = page_counts.get(page, 0)

        if current_count >= max_per_page:
            continue

        selected.append(chunk)
        page_counts[page] = current_count + 1

        if len(selected) >= top_k:
            break

    return selected


def advanced_search(
    query: str,
    candidate_k: int = 12,
    rerank_k: int = 10,
    final_k: int = 5,
):
    candidates = hybrid_search(
        query=query,
        top_k=candidate_k,
    )

    reranked = rerank(
        query=query,
        chunks=candidates,
        top_k=rerank_k,
    )

    diversified = diversify_by_page(
        chunks=reranked,
        top_k=final_k,
        max_per_page=1,
    )

    return diversified