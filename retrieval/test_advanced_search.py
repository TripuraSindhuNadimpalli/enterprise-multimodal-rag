from retrieval.advanced_search import advanced_search
from retrieval.semantic_search import semantic_search


QUERY = "What projects are recommended for internships?"


def print_results(title, results):
    print("\n")
    print("=" * 80)
    print(title)
    print("=" * 80)

    for rank, chunk in enumerate(results, start=1):
        print(
            f"\nRank {rank} | "
            f"Page {chunk.page_number} | "
            f"Chunk {chunk.chunk_index}"
        )

        print("-" * 80)
        print(chunk.text[:500])


def main():
    semantic_results = semantic_search(
        query=QUERY,
        top_k=5,
    )

    advanced_results = advanced_search(
        query=QUERY,
        candidate_k=10,
        final_k=5,
    )

    print_results(
        "SEMANTIC SEARCH",
        semantic_results,
    )

    print_results(
        "HYBRID + RERANKING",
        advanced_results,
    )


if __name__ == "__main__":
    main()