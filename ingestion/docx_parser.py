from io import BytesIO

from docx import Document as DocxDocument


def extract_text_from_docx(file_bytes: bytes) -> list[dict]:
    document = DocxDocument(BytesIO(file_bytes))

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    combined_text = "\n".join(paragraphs).strip()

    if not combined_text:
        return []

    return [
        {
            "page_number": 1,
            "text": combined_text,
        }
    ]