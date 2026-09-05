from retrieval.llm import generate_answer


VALID_INTENTS = {
    "multi_document_summary",
    "project_comparison",
    "multi_section_list",
    "general_semantic",
}


def classify_query(
    question: str,
    document_count: int = 0,
) -> str:

    prompt = f"""
You are a query routing classifier for an enterprise RAG system.

Classify the user's question into EXACTLY ONE of these intents:

1. multi_document_summary
Use when the user wants to summarize, analyze, synthesize, or understand
multiple selected documents together.

2. project_comparison
Use when the user wants to compare two or more projects, including
similarities, differences, shared technologies, or overlap.

3. multi_section_list
Use when the question requires collecting information across several
sections of the knowledge base, such as asking which projects are
recommended.

4. general_semantic
Use for ordinary factual or semantic questions that can be answered
using normal retrieval.

Number of selected documents: {document_count}

User question:
{question}

Return ONLY the intent name.
Do not explain your answer.
"""

    result = generate_answer(prompt).strip().lower()

    # Protect the router from unexpected LLM output.
    result = result.replace("`", "").strip()

    if result in VALID_INTENTS:
        return result

    return "general_semantic"