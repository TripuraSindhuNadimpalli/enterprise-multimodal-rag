import re


def split_into_paragraphs(text: str) -> list[str]:
    text = text.strip()

    if not text:
        return []

    paragraphs = re.split(r"\n\s*\n+", text)

    return [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]


def chunk_text(
    text: str,
    chunk_size: int = 700,
    overlap: int = 100,
) -> list[str]:

    paragraphs = split_into_paragraphs(text)

    if not paragraphs:
        return []

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        candidate = (
            f"{current_chunk}\n\n{paragraph}".strip()
            if current_chunk
            else paragraph
        )

        if len(candidate) <= chunk_size:
            current_chunk = candidate
            continue

        if current_chunk:
            chunks.append(current_chunk.strip())

            overlap_text = current_chunk[-overlap:]

            current_chunk = (
                f"{overlap_text}\n\n{paragraph}"
            ).strip()

        else:
            # Handle an unusually long paragraph.
            start = 0

            while start < len(paragraph):
                end = start + chunk_size

                piece = paragraph[start:end].strip()

                if piece:
                    chunks.append(piece)

                if end >= len(paragraph):
                    break

                start = end - overlap

            current_chunk = ""

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks