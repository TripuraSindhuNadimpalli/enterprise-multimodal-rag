import uuid

from database.connection import SessionLocal
from database.models import DocumentChunk
from retrieval.query_decomposer import decompose_query
from retrieval.semantic_search import semantic_search


def decomposed_search(
    query: str,
    per_query_k: int = 3,
    final_k: int = 8,
    document_ids: list[uuid.UUID] | None = None,
) -> list[DocumentChunk]:

    subqueries = decompose_query(query)

    # Normal query → semantic retrieval
    if len(subqueries) == 1:
        return semantic_search(
            query=query,
            top_k=final_k,
            document_ids=document_ids,
        )

    db = SessionLocal()

    try:
        project_query = db.query(DocumentChunk).filter(
            DocumentChunk.parent_section_title.isnot(None)
        )

        if document_ids:
            project_query = project_query.filter(
                DocumentChunk.document_id.in_(document_ids)
            )

        project_chunks = (
            project_query
            .order_by(DocumentChunk.chunk_index)
            .all()
        )

        selected = []
        selected_ids = set()
        seen_projects = set()

        # Collect one representative chunk per project
        for chunk in project_chunks:
            parent = chunk.parent_section_title

            if parent not in seen_projects:
                selected.append(chunk)
                selected_ids.add(chunk.id)
                seen_projects.add(parent)

        # Add semantic context relevant to the original query
        context_results = semantic_search(
            query=query,
            top_k=6,
            document_ids=document_ids,
        )

        for chunk in context_results:
            if chunk.id in selected_ids:
                continue

            selected.append(chunk)
            selected_ids.add(chunk.id)

            if len(selected) >= final_k:
                break

        return selected[:final_k]

    finally:
        db.close()