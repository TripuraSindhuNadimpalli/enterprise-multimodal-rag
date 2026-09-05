import logging
from database.connection import SessionLocal
from database.models import Document, DocumentChunk
from ingestion.document_parser import parse_document
from ingestion.structured_chunker import create_structured_chunks
from ingestion.text_cleaner import clean_extracted_text
from retrieval.embeddings import generate_embedding
from storage.minio_client import download_file
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
def process_document(document_id):
    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if not document:
            raise ValueError("Document not found")

        logger.info(
            "Document processing started | document_id=%s | filename=%s | content_type=%s",
            document.id,
            document.filename,
            document.content_type,
        )

        document.status = "processing"
        db.commit()

        # Remove old chunks if this document is being reprocessed.
        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
        ).delete(synchronize_session=False)

        db.commit()

        # Download original file from MinIO.
        file_bytes = download_file(document.storage_path)

        # Currently this processor handles PDFs.
        pages = parse_document(
            file_bytes=file_bytes,
            content_type=document.content_type,
        )

        chunk_index = 0
        current_parent_section = None
        current_subsection = None

        for page in pages:
            cleaned_text = clean_extracted_text(
                page["text"]
            )

            (
                chunks,
                current_parent_section,
                current_subsection,
            ) = create_structured_chunks(
                cleaned_text,
                current_parent_section=current_parent_section,
                current_subsection=current_subsection,
            )

            for chunk in chunks:
                # Build contextual text for embedding.
                embedding_parts = []

                if chunk["parent_section_title"]:
                    embedding_parts.append(
                        f"Parent Section: "
                        f"{chunk['parent_section_title']}"
                    )

                if chunk["section_title"]:
                    embedding_parts.append(
                        f"Section: {chunk['section_title']}"
                    )

                embedding_parts.append(chunk["text"])

                embedding_text = "\n\n".join(
                    embedding_parts
                )

                embedding = generate_embedding(
                    embedding_text
                )

                document_chunk = DocumentChunk(
                    document_id=document.id,
                    page_number=page["page_number"],
                    chunk_index=chunk_index,
                    text=chunk["text"],
                    parent_section_title=chunk[
                        "parent_section_title"
                    ],
                    section_title=chunk["section_title"],
                    chunk_type=chunk["chunk_type"],
                    embedding=embedding,
                )

                db.add(document_chunk)

                chunk_index += 1

        # Only mark processed AFTER chunks + embeddings succeed.
        document.status = "processed"

        db.commit()

        logger.info(
            "Document processing completed | document_id=%s | filename=%s | chunks=%s",
            document.id,
            document.filename,
            chunk_index,
        )

    except Exception:
        logger.exception(
            "Document processing failed | document_id=%s",
            document_id,
        )

        db.rollback()

        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document:
            document.status = "failed"
            db.commit()

        raise

    finally:
        db.close()