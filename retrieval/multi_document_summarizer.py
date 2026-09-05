import uuid

from retrieval.document_summarizer import summarize_documents
from retrieval.llm import generate_answer


def synthesize_multi_document_summary(
    question: str,
    document_ids: list[uuid.UUID],
) -> dict:

    document_summaries = summarize_documents(
        document_ids=document_ids,
        chunks_per_document=8,
    )

    if not document_summaries:
        return {
            "answer": "I could not summarize the selected documents.",
            "document_summaries": [],
            "sources": [],
        }

    summary_blocks = []
    sources = []

    for item in document_summaries:
        summary_blocks.append(
            f"""
DOCUMENT: {item["filename"]}

SUMMARY:
{item["summary"]}
"""
        )

        for source in item["source_chunks"]:
            sources.append(
                {
                    "document": item["filename"],
                    "page": source["page"],
                    "chunk_index": source["chunk_index"],
                    "parent_section": source["parent_section"],
                    "section": source["section"],
                }
            )

    combined_context = "\n\n".join(summary_blocks)

    prompt = f"""
Answer the user's question using ONLY the document summaries below.

USER QUESTION:
{question}

DOCUMENT SUMMARIES:
{combined_context}

INSTRUCTIONS:
- Give a combined overview across all selected documents.
- Clearly distinguish the major topic of each document.
- Mention important similarities or differences when useful.
- Do not invent information.
- Do not omit a selected document.
- Keep the answer structured and concise.
"""

    answer = generate_answer(prompt)

    return {
        "answer": answer,
        "document_summaries": document_summaries,
        "sources": sources,
    }