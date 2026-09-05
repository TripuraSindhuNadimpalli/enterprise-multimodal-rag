from retrieval.rag import answer_question


def main():
    question = "What projects are recommended for internships?"

    result = answer_question(question)

    print("\nQUESTION")
    print("=" * 70)
    print(question)

    print("\nANSWER")
    print("=" * 70)
    print(result["answer"])

    print("\nSOURCES")
    print("=" * 70)

    for source in result["sources"]:
        print(
            f"{source['document']} "
            f"| Page {source['page']} "
            f"| Chunk {source['chunk_index']} "
            f"| Parent: {source['parent_section']} "
            f"| Section: {source['section']}"
        )


if __name__ == "__main__":
    main()