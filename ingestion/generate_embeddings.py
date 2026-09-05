from database.connection import SessionLocal
from database.models import DocumentChunk
from retrieval.embeddings import generate_embedding


def generate_missing_embeddings() -> None:
    db = SessionLocal()

    try:
        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.embedding.is_(None))
            .all()
        )

        print(f"Chunks requiring embeddings: {len(chunks)}")

        for index, chunk in enumerate(chunks, start=1):
            embedding_parts = []

            if chunk.parent_section_title:
                embedding_parts.append(
                    f"Parent Section: {chunk.parent_section_title}"
                )

            if chunk.section_title:
                embedding_parts.append(
                    f"Section: {chunk.section_title}"
                )

            embedding_parts.append(chunk.text)

            embedding_text = "\n\n".join(embedding_parts)

            chunk.embedding = generate_embedding(embedding_text)

            print(
                f"Embedded chunk {index}/{len(chunks)} "
                f"(page {chunk.page_number})"
            )

        db.commit()

        print("Embeddings generated successfully")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    generate_missing_embeddings()