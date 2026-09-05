from sqlalchemy import text

from database.connection import SessionLocal
from database.models import DocumentChunk


def keyword_search(
    query: str,
    top_k: int = 10,
) -> list[DocumentChunk]:
    db = SessionLocal()

    try:
        statement = text(
            """
            SELECT id
            FROM document_chunks
            WHERE to_tsvector('english', text)
                  @@ websearch_to_tsquery('english', :query)
            ORDER BY
                ts_rank_cd(
                    to_tsvector('english', text),
                    websearch_to_tsquery('english', :query)
                ) DESC
            LIMIT :top_k
            """
        )

        rows = db.execute(
            statement,
            {
                "query": query,
                "top_k": top_k,
            },
        ).fetchall()

        chunk_ids = [row.id for row in rows]

        if not chunk_ids:
            return []

        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.id.in_(chunk_ids))
            .all()
        )

        chunk_map = {chunk.id: chunk for chunk in chunks}

        return [
            chunk_map[chunk_id]
            for chunk_id in chunk_ids
            if chunk_id in chunk_map
        ]

    finally:
        db.close()