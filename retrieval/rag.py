import uuid

from retrieval.multi_document_summarizer import (
    synthesize_multi_document_summary,
)
from database.connection import SessionLocal
from database.models import Document
from retrieval.comparison_search import comparison_search
from retrieval.decomposed_search import decomposed_search
from retrieval.llm import generate_answer
from retrieval.multi_document_search import multi_document_search
from retrieval.query_classifier import classify_query
from retrieval.semantic_search import semantic_search


def retrieve_chunks(
    question: str,
    document_ids: list[uuid.UUID] | None = None,
):
    document_count = len(document_ids) if document_ids else 0

    intent = classify_query(
        question=question,
        document_count=document_count,
    )

    if intent == "multi_document_summary":
        if document_ids and len(document_ids) > 1:
            return multi_document_search(
                query=question,
                document_ids=document_ids,
                per_document_k=3,
                final_k=8,
            )

    if intent == "project_comparison":
        comparison_results = comparison_search(
            query=question,
            final_k=8,
            document_ids=document_ids,
        )

        if comparison_results:
            return comparison_results

    if intent == "multi_section_list":
        return decomposed_search(
            query=question,
            final_k=8,
            document_ids=document_ids,
        )

    return semantic_search(
        query=question,
        top_k=5,
        document_ids=document_ids,
    )


def answer_question(
    question: str,
    document_ids: list[uuid.UUID] | None = None,
) -> dict:
    document_count = len(document_ids) if document_ids else 0

    intent = classify_query(
        question=question,
        document_count=document_count,
    )

    if (
        intent == "multi_document_summary"
        and document_ids
        and len(document_ids) > 1
    ):
        summary_result = synthesize_multi_document_summary(
            question=question,
            document_ids=document_ids,
        )

        return {
            "answer": summary_result["answer"],
            "sources": summary_result["sources"],
    }
    chunks = retrieve_chunks(
        question=question,
        document_ids=document_ids,
    )

    if not chunks:
        return {
            "answer": (
                "I could not find relevant information "
                "in the selected documents."
            ),
            "sources": [],
        }

    context_parts = []
    sources = []

    db = SessionLocal()

    try:
        for chunk in chunks:
            document = (
                db.query(Document)
                .filter(Document.id == chunk.document_id)
                .first()
            )

            if document is None:
                continue

            evidence_parts = []

            if chunk.parent_section_title:
                evidence_parts.append(
                    f"Parent Section: {chunk.parent_section_title}"
                )

            if chunk.section_title:
                evidence_parts.append(
                    f"Section: {chunk.section_title}"
                )

            evidence_parts.append(
                f"Content: {chunk.text}"
            )

            evidence_text = "\n".join(evidence_parts)

            context_parts.append(
                f"""
SOURCE
Document: {document.filename}
Page: {chunk.page_number}

{evidence_text}
"""
            )

            sources.append(
                {
                    "document": document.filename,
                    "page": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "parent_section": chunk.parent_section_title,
                    "section": chunk.section_title,
                }
            )

    finally:
        db.close()

    context = "\n\n".join(context_parts)

    prompt = f"""
Answer the question using ONLY the provided context.

CONTEXT:
{context}

QUESTION:
{question}

INSTRUCTIONS:
- Use only information from the provided context.
- Do not invent or assume information that is not present in the context.
- If there is insufficient evidence, clearly say that the provided context does not contain enough information.
- For list questions, include all distinct relevant items found in the context.
- Keep the answer clear, concise, and well structured.
- Do not create a "Sources", "References", or "Citations" section in the answer.
- Do not list document names or page numbers unless they are directly necessary to explain the answer.
- The application will display retrieved sources separately, so return only the answer itself.
"""

    answer = generate_answer(prompt)

    return {
        "answer": answer,
        "sources": sources,
    }