from ingestion.docx_parser import extract_text_from_docx
from ingestion.image_parser import extract_text_from_image
from ingestion.pdf_parser import extract_text_from_pdf


PDF_TYPE = "application/pdf"

DOCX_TYPE = (
    "application/vnd.openxmlformats-officedocument."
    "wordprocessingml.document"
)

IMAGE_TYPES = {
    "image/png",
    "image/jpeg",
}


def parse_document(
    file_bytes: bytes,
    content_type: str,
) -> list[dict]:

    if content_type == PDF_TYPE:
        return extract_text_from_pdf(file_bytes)

    if content_type == DOCX_TYPE:
        return extract_text_from_docx(file_bytes)

    if content_type in IMAGE_TYPES:
        return extract_text_from_image(file_bytes)

    raise ValueError(
        f"Unsupported processing type: {content_type}"
    )