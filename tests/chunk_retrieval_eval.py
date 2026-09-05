from retrieval.semantic_search import semantic_search
from retrieval.advanced_search import advanced_search


TEST_CASES = [
    {
        "question": "What projects are recommended for internships?",
        "relevant_chunks": {3, 9, 17, 23},
    },
    {
        "question": (
            "What technologies are used in the "
            "Enterprise Multimodal RAG platform?"
        ),
        "relevant_chunks": {6, 7},
    },
    {
        "question": (
            "Why is the AI DevOps Incident "
            "Intelligence Platform useful?"
        ),
        "relevant_chunks": {23, 24, 25},
    },
    {
        "question": (
            "What should be done instead of "
            "adding a fifth major project?"
        ),
        "relevant_chunks": {31},
    },
]


def precision_at_k(retrieved, relevant, k):
    retrieved = retrieved[:k]

    if not retrieved:
        return 0.0

    hits = sum(
        1 for chunk in retrieved
        if chunk in relevant
    )

    return hits / k


def recall_at_k(retrieved, relevant, k):
    if not relevant:
        return 0.0

    hits = len(
        set(retrieved[:k]) & relevant
    )

    return hits / len(relevant)


def reciprocal_rank(retrieved, relevant):
    for rank, chunk in enumerate(retrieved, start=1):
        if chunk in relevant:
            return 1.0 / rank

    return 0.0


def evaluate(search_function, name, k=5):
    print("\n")
    print("=" * 80)
    print(name)
    print("=" * 80)

    precisions = []
    recalls = []
    reciprocal_ranks = []

    for case in TEST_CASES:
        question = case["question"]
        relevant = case["relevant_chunks"]

        results = search_function(question)

        retrieved = [
            chunk.chunk_index
            for chunk in results[:k]
        ]

        precision = precision_at_k(
            retrieved,
            relevant,
            k,
        )

        recall = recall_at_k(
            retrieved,
            relevant,
            k,
        )

        rr = reciprocal_rank(
            retrieved,
            relevant,
        )

        precisions.append(precision)
        recalls.append(recall)
        reciprocal_ranks.append(rr)

        print(f"\nQuestion: {question}")
        print(
            f"Relevant chunks: "
            f"{sorted(relevant)}"
        )
        print(
            f"Retrieved chunks: "
            f"{retrieved}"
        )
        print(
            f"Precision@{k}: "
            f"{precision:.3f}"
        )
        print(
            f"Recall@{k}: "
            f"{recall:.3f}"
        )
        print(
            f"Reciprocal Rank: "
            f"{rr:.3f}"
        )

    print("\n" + "-" * 80)

    print(
        f"Average Precision@{k}: "
        f"{sum(precisions) / len(precisions):.3f}"
    )

    print(
        f"Average Recall@{k}: "
        f"{sum(recalls) / len(recalls):.3f}"
    )

    print(
        "MRR: "
        f"{sum(reciprocal_ranks) / len(reciprocal_ranks):.3f}"
    )


if __name__ == "__main__":
    evaluate(
        semantic_search,
        "SEMANTIC SEARCH — CHUNK LEVEL",
    )

    evaluate(
        advanced_search,
        "ADVANCED RETRIEVAL — CHUNK LEVEL",
    )