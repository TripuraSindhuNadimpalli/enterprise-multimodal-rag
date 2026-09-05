import uuid

from ingestion.process_document import process_document


DOCUMENT_ID = uuid.UUID(
    "13090849-551d-4e85-ac9d-1ad70170fb56"
)


if __name__ == "__main__":
    process_document(DOCUMENT_ID)