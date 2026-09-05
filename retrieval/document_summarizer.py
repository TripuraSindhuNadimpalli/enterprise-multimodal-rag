from database.connection import SessionLocal
from database.models import Document
from retrieval.document_summary_search import document_summary_search
from retrieval.llm import generate_answer


def summarize_documents(
    document_ids,
    chunks_per_document: int = 8,
) -> list[dict]:

    chunks = document_summary_search(
        document_ids=document_ids,
        chunks_per_document=chunks_per_document,
    )

    db = SessionLocal()

    try:
        grouped = {}

        for chunk in chunks:
            document = (
                db.query(Document)
                .filter(Document.id == chunk.document_id)
                .first()
            )

            if document is None:
                continue

            grouped.setdefault(
                document.id,
                {
                    "filename": document.filename,
                    "chunks": [],
                },
            )

            grouped[document.id]["chunks"].append(chunk)

        summaries = []

        for document_id, data in grouped.items():
            context_parts = []
            source_pages = set()
            source_chunks = []

            for chunk in data["chunks"]:
                source_pages.add(chunk.page_number)

                source_chunks.append(
                    {
                        "page": chunk.page_number,
                        "chunk_index": chunk.chunk_index,
                        "parent_section": chunk.parent_section_title,
                        "section": chunk.section_title,
                    }
                )

                parts = []

                if chunk.parent_section_title:
                    parts.append(
                        f"Parent Section: {chunk.parent_section_title}"
                    )

                if chunk.section_title:
                    parts.append(
                        f"Section: {chunk.section_title}"
                    )

                parts.append(f"Content: {chunk.text}")

                context_parts.append(
                    f"""
Page: {chunk.page_number}
{chr(10).join(parts)}
"""
                )

            context = "\n\n".join(context_parts)

            prompt = f"""
Summarize this document using ONLY the provided context.

Document:
{data["filename"]}

Context:
{context}

Instructions:
- Identify the major topics.
- Mention important sections or themes.
- Do not invent missing information.
- Keep the summary concise but comprehensive.
"""

            summary = generate_answer(prompt)

            summaries.append(
                {
                    "document_id": str(document_id),
                    "filename": data["filename"],
                    "summary": summary,
                    "source_pages": sorted(source_pages),
                    "source_chunks": source_chunks,
                }
            )

        return summaries

    finally:
        db.close()