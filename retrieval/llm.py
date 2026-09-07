from ollama import chat


MODEL_NAME = "qwen3:0.6b"


def generate_answer(prompt: str) -> str:
    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an enterprise knowledge assistant. "
                    "Answer questions using only the provided context. "
                    "Do not invent information. "
                    "If the context does not contain enough information, "
                    "say that you cannot answer from the available documents."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        options={
            "temperature": 0.1,
        },
    )

    return response.message.content
