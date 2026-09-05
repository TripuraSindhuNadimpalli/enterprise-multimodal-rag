import uuid

from sqlalchemy import select

from database.connection import SessionLocal
from database.models import DocumentChunk
from retrieval.embeddings import generate_embedding


def semantic_search(
    query: str,
    top_k: int = 5,
    document_ids: list[uuid.UUID] | None = None,
) -> list[DocumentChunk]:

    db = SessionLocal()

    try:
        query_embedding = generate_embedding(query)

        statement = select(DocumentChunk).where(
            DocumentChunk.embedding.is_not(None)
        )

        if document_ids:
            statement = statement.where(
                DocumentChunk.document_id.in_(document_ids)
            )

        statement = (
            statement
            .order_by(
                DocumentChunk.embedding.cosine_distance(
                    query_embedding
                )
            )
            .limit(top_k)
        )

        results = db.execute(
            statement
        ).scalars().all()

        return results

    finally:
        db.close()