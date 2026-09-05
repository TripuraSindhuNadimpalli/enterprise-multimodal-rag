import re
import uuid

from database.connection import SessionLocal
from database.models import DocumentChunk


def extract_project_numbers(query: str) -> list[int]:
    matches = re.findall(
        r"project\s*(\d+)",
        query,
        flags=re.IGNORECASE,
    )

    return list(
        dict.fromkeys(
            int(number)
            for number in matches
        )
    )


def comparison_search(
    query: str,
    final_k: int = 8,
    document_ids: list[uuid.UUID] | None = None,
) -> list[DocumentChunk]:

    project_numbers = extract_project_numbers(query)

    if len(project_numbers) < 2:
        return []

    db = SessionLocal()

    try:
        selected = []

        for project_number in project_numbers:
            project_pattern = f"%Project {project_number}%"

            query_builder = db.query(DocumentChunk).filter(
                DocumentChunk.parent_section_title.ilike(
                    project_pattern
                ),
                DocumentChunk.section_title.ilike(
                    "%Technologies%"
                ),
            )

            if document_ids:
                query_builder = query_builder.filter(
                    DocumentChunk.document_id.in_(document_ids)
                )

            technology_chunks = (
                query_builder
                .order_by(DocumentChunk.chunk_index)
                .all()
            )

            selected.extend(technology_chunks)

            if not technology_chunks:
                fallback = db.query(DocumentChunk).filter(
                    DocumentChunk.parent_section_title.ilike(
                        project_pattern
                    )
                )

                if document_ids:
                    fallback = fallback.filter(
                        DocumentChunk.document_id.in_(document_ids)
                    )

                fallback_chunks = (
                    fallback
                    .order_by(DocumentChunk.chunk_index)
                    .limit(2)
                    .all()
                )

                selected.extend(fallback_chunks)

        unique_chunks = []
        seen_ids = set()

        for chunk in selected:
            if chunk.id in seen_ids:
                continue

            unique_chunks.append(chunk)
            seen_ids.add(chunk.id)

            if len(unique_chunks) >= final_k:
                break

        return unique_chunks

    finally:
        db.close()