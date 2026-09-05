from sentence_transformers import CrossEncoder

from database.models import DocumentChunk


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

model = CrossEncoder(MODEL_NAME)


def rerank(
    query: str,
    chunks: list[DocumentChunk],
    top_k: int = 5,
) -> list[DocumentChunk]:

    if not chunks:
        return []

    pairs = [
        [query, chunk.text]
        for chunk in chunks
    ]

    scores = model.predict(pairs)

    ranked = sorted(
        zip(chunks, scores),
        key=lambda item: float(item[1]),
        reverse=True,
    )

    return [
        chunk
        for chunk, _ in ranked[:top_k]
    ]