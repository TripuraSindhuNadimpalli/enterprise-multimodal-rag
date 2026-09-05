import uuid
import logging
from monitoring.metrics import DOCUMENT_UPLOADS_TOTAL
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from rq import Retry
from rq.job import Job
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database.connection import get_db
from database.models import Document, DocumentChunk, User
from ingestion.process_document import process_document
from storage.minio_client import delete_file, upload_file
from workers.queue import document_queue
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/png",
    "image/jpeg",
}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(
        "Document upload started | user_id=%s | filename=%s | content_type=%s",
        current_user.id,
        file.filename,
        file.content_type,
    )
    
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type",
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Empty file",
        )

    document_id = uuid.uuid4()

    object_name = f"{document_id}/{file.filename}"

    upload_file(
        object_name=object_name,
        data=file_bytes,
        content_type=file.content_type,
    )

    document = Document(
        id=document_id,
        user_id=current_user.id,
        filename=file.filename,
        content_type=file.content_type,
        storage_path=object_name,
        status="uploaded",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    job = document_queue.enqueue(
        process_document,
        document.id,
        job_timeout=1800,
        retry=Retry(
            max=3,
            interval=[10, 30, 60],
        ),
    )
    DOCUMENT_UPLOADS_TOTAL.inc()

    logger.info(
        "Document upload completed | user_id=%s | document_id=%s | job_id=%s | filename=%s",
        current_user.id,
        document.id,
        job.id,
        document.filename,
    )

    return {
        "id": str(document.id),
        "filename": document.filename,
        "content_type": document.content_type,
        "storage_path": document.storage_path,
        "status": document.status,
        "created_at": document.created_at,
        "job_id": job.id,
    }


@router.get("")
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = select(Document)

    if current_user.role != "admin":
        statement = statement.where(
            Document.user_id == current_user.id
        )

    statement = statement.order_by(
        Document.created_at.desc()
    )

    documents = db.execute(
        statement
    ).scalars().all()

    return [
        {
            "id": str(document.id),
            "user_id": (
                str(document.user_id)
                if document.user_id
                else None
            ),
            "filename": document.filename,
            "content_type": document.content_type,
            "storage_path": document.storage_path,
            "status": document.status,
            "created_at": document.created_at,
        }
        for document in documents
    ]


@router.get("/jobs/{job_id}")
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        job = Job.fetch(
            job_id,
            connection=document_queue.connection,
        )

    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    document_id = None

    if job.args:
        document_id = uuid.UUID(
            str(job.args[0])
        )

    if document_id is None:
        raise HTTPException(
            status_code=404,
            detail="Job document not found",
        )

    query = db.query(Document).filter(
        Document.id == document_id
    )

    if current_user.role != "admin":
        query = query.filter(
            Document.user_id == current_user.id
        )

    document = query.first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    status = job.get_status(refresh=True)

    response = {
        "job_id": job.id,
        "status": status,
        "document_id": str(document_id),
        "retries_left": job.retries_left,
    }

    if job.enqueued_at:
        response["enqueued_at"] = job.enqueued_at

    if job.started_at:
        response["started_at"] = job.started_at

    if job.ended_at:
        response["ended_at"] = job.ended_at

    if status == "failed":
        response["error"] = job.exc_info

    return response


@router.get("/{document_id}")
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Document).filter(
        Document.id == document_id
    )

    if current_user.role != "admin":
        query = query.filter(
            Document.user_id == current_user.id
        )

    document = query.first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    chunk_count = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document.id
        )
        .count()
    )

    embedded_chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document.id,
            DocumentChunk.embedding.is_not(None),
        )
        .count()
    )

    return {
        "id": str(document.id),
        "user_id": (
            str(document.user_id)
            if document.user_id
            else None
        ),
        "filename": document.filename,
        "content_type": document.content_type,
        "storage_path": document.storage_path,
        "status": document.status,
        "chunk_count": chunk_count,
        "embedded_chunks": embedded_chunks,
        "created_at": document.created_at,
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Document).filter(
        Document.id == document_id
    )

    if current_user.role != "admin":
        query = query.filter(
            Document.user_id == current_user.id
        )

    document = query.first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    try:
        delete_file(document.storage_path)

        db.delete(document)
        db.commit()

        return {
            "message": "Document deleted successfully",
            "document_id": str(document_id),
        }

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(exc)}",
        )