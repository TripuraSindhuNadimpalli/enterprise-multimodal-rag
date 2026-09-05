from retrieval.semantic_search import semantic_search


def main():
    query = "What projects are recommended for internships?"

    results = semantic_search(
        query=query,
        top_k=5,
    )

    print(f"\nQuery: {query}")
    print(f"Results found: {len(results)}")

    for rank, chunk in enumerate(results, start=1):
        print("\n" + "=" * 70)
        print(f"Rank: {rank}")
        print(f"Page: {chunk.page_number}")
        print(f"Chunk Index: {chunk.chunk_index}")
        print("-" * 70)
        print(chunk.text[:800])


if __name__ == "__main__":
    main()