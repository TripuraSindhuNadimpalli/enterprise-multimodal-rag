import uuid

from database.connection import SessionLocal
from database.models import DocumentChunk


def document_summary_search(
    document_ids: list[uuid.UUID],
    chunks_per_document: int = 8,
) -> list[DocumentChunk]:

    db = SessionLocal()

    try:
        selected_chunks = []

        for document_id in document_ids:

            chunks = (
                db.query(DocumentChunk)
                .filter(
                    DocumentChunk.document_id == document_id
                )
                .order_by(DocumentChunk.chunk_index)
                .all()
            )

            if not chunks:
                continue

            # If the document is small enough,
            # use all available chunks.
            if len(chunks) <= chunks_per_document:
                selected_chunks.extend(chunks)
                continue

            # Sample chunks across the whole document instead
            # of taking only the beginning or semantic top-k.
            positions = []

            for i in range(chunks_per_document):
                position = round(
                    i * (len(chunks) - 1)
                    / (chunks_per_document - 1)
                )

                positions.append(position)

            seen_positions = set()

            for position in positions:
                if position in seen_positions:
                    continue

                selected_chunks.append(
                    chunks[position]
                )

                seen_positions.add(position)

        return selected_chunks

    finally:
        db.close()