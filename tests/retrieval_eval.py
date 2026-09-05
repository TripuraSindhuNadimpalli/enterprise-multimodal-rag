from retrieval.semantic_search import semantic_search
from retrieval.advanced_search import advanced_search


EVAL_CASES = [
    {
        "question": "What projects are recommended for internships?",
        "relevant_pages": {2, 3, 4, 5, 6, 7},
    },
    {
        "question": "What technologies are used in the Enterprise Multimodal RAG platform?",
        "relevant_pages": {2, 3},
    },
    {
        "question": "Why is the AI DevOps Incident Intelligence Platform useful?",
        "relevant_pages": {6},
    },
    {
        "question": "What should be done instead of adding a fifth major project?",
        "relevant_pages": {8},
    },
]


def hit_rate(results, relevant_pages):
    retrieved_pages = {
        chunk.page_number
        for chunk in results
    }

    return int(
        bool(retrieved_pages & relevant_pages)
    )


def recall_at_k(results, relevant_pages):
    retrieved_pages = {
        chunk.page_number
        for chunk in results
    }

    found = len(
        retrieved_pages & relevant_pages
    )

    return found / len(relevant_pages)


def reciprocal_rank(results, relevant_pages):
    for rank, chunk in enumerate(results, start=1):
        if chunk.page_number in relevant_pages:
            return 1 / rank

    return 0.0


def evaluate_retriever(name, search_function):
    total_hit_rate = 0
    total_recall = 0
    total_rr = 0

    print("\n")
    print("=" * 80)
    print(name)
    print("=" * 80)

    for case in EVAL_CASES:
        question = case["question"]
        relevant_pages = case["relevant_pages"]

        results = search_function(
            query=question,
            top_k=5,
        )

        hit = hit_rate(
            results,
            relevant_pages,
        )

        recall = recall_at_k(
            results,
            relevant_pages,
        )

        rr = reciprocal_rank(
            results,
            relevant_pages,
        )

        total_hit_rate += hit
        total_recall += recall
        total_rr += rr

        retrieved_pages = [
            chunk.page_number
            for chunk in results
        ]

        print(f"\nQuestion: {question}")
        print(f"Relevant pages: {sorted(relevant_pages)}")
        print(f"Retrieved pages: {retrieved_pages}")
        print(f"Hit@5: {hit}")
        print(f"Recall@5: {recall:.3f}")
        print(f"Reciprocal Rank: {rr:.3f}")

    count = len(EVAL_CASES)

    print("\n" + "-" * 80)

    print(
        f"Average Hit@5: "
        f"{total_hit_rate / count:.3f}"
    )

    print(
        f"Average Recall@5: "
        f"{total_recall / count:.3f}"
    )

    print(
        f"MRR: "
        f"{total_rr / count:.3f}"
    )


def semantic_wrapper(query, top_k):
    return semantic_search(
        query=query,
        top_k=top_k,
    )


def advanced_wrapper(query, top_k):
    return advanced_search(
        query=query,
        candidate_k=10,
        final_k=top_k,
    )


if __name__ == "__main__":
    evaluate_retriever(
        "SEMANTIC SEARCH",
        semantic_wrapper,
    )

    evaluate_retriever(
        "HYBRID + RERANKING",
        advanced_wrapper,
    )