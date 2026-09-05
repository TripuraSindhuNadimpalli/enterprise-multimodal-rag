from database.connection import SessionLocal
from database.models import Document
from ingestion.pdf_parser import extract_text_from_pdf
from storage.minio_client import download_file


def main():
    db = SessionLocal()

    try:
        document = db.query(Document).first()

        if not document:
            print("No document found")
            return

        file_bytes = download_file(document.storage_path)

        pages = extract_text_from_pdf(file_bytes)

        print(f"Document: {document.filename}")
        print(f"Pages extracted: {len(pages)}")

        for page in pages[:3]:
            print("\n--------------------")
            print(f"Page {page['page_number']}")
            print("--------------------")
            print(page["text"][:1000])

    finally:
        db.close()


if __name__ == "__main__":
    main()