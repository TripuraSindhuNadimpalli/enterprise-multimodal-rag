from retrieval.llm import generate_answer


def rewrite_followup_question(
    question: str,
    conversation_history: list,
) -> str:
    if not conversation_history:
        return question

    history_parts = []

    for message in conversation_history:
        history_parts.append(
            f"{message.role.upper()}: {message.content}"
        )

    history_text = "\n\n".join(history_parts)

    prompt = f"""
Rewrite the user's latest question as a complete standalone retrieval question.

CONVERSATION HISTORY:
{history_text}

LATEST QUESTION:
{question}

RULES:
- Resolve references such as "those", "that", "it", "they", and "them".
- Preserve the entity or project discussed in the previous question.
- Preserve the entity or project mentioned in the latest question.
- For comparison questions, explicitly include BOTH entities being compared.
- Do not answer the question.
- Do not add new facts.
- Return ONLY the rewritten question.

Example:

Previous question:
"What technologies are used in Project 1?"

Latest question:
"Which of those are also used in Project 2?"

Correct rewrite:
"Which technologies used in Project 1 are also used in Project 2?"
"""

    rewritten_question = generate_answer(prompt)

    return rewritten_question.strip()