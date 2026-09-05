from retrieval.decomposed_search import decomposed_search


QUESTION = "What projects are recommended for internships?"


def main():
    results = decomposed_search(
        query=QUESTION,
        per_query_k=3,
        final_k=8,
    )

    print(f"\nQuestion: {QUESTION}")

    for rank, chunk in enumerate(results, start=1):
        print("\n" + "=" * 70)
        print(f"Rank: {rank}")
        print(f"Chunk: {chunk.chunk_index}")
        print(f"Page: {chunk.page_number}")
        print(f"Parent: {chunk.parent_section_title}")
        print(f"Section: {chunk.section_title}")
        print("-" * 70)
        print(chunk.text[:500])


if __name__ == "__main__":
    main()