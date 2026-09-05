import uuid
import logging
from monitoring.metrics import RAG_QUERIES_TOTAL

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database.connection import get_db
from database.models import Document, User
from retrieval.conversation import (
    conversation_exists,
    create_conversation,
    get_conversation_messages,
    save_message,
)
from retrieval.query_rewriter import rewrite_followup_question
from retrieval.rag import answer_question

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/query",
    tags=["RAG Query"],
)


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question to ask the knowledge base",
    )

    conversation_id: uuid.UUID | None = Field(
        default=None,
        description="Existing conversation ID for follow-up questions",
    )

    document_ids: list[uuid.UUID] | None = Field(
        default=None,
        description="Optional list of document IDs to restrict retrieval",
    )


class SourceResponse(BaseModel):
    document: str
    page: int
    chunk_index: int
    parent_section: str | None = None
    section: str | None = None


class QueryResponse(BaseModel):
    conversation_id: uuid.UUID
    question: str
    answer: str
    sources: list[SourceResponse]


def resolve_accessible_document_ids(
    requested_document_ids: list[uuid.UUID] | None,
    current_user: User,
    db: Session,
) -> list[uuid.UUID]:

    query = db.query(Document)

    # Normal users can only access their own documents.
    if current_user.role != "admin":
        query = query.filter(
            Document.user_id == current_user.id
        )

    # If specific documents were requested,
    # restrict the query to those IDs.
    if requested_document_ids:
        query = query.filter(
            Document.id.in_(requested_document_ids)
        )

    accessible_documents = query.all()

    accessible_ids = {
        document.id
        for document in accessible_documents
    }

    # Verify every specifically requested document
    # is accessible to the current user.
    if requested_document_ids:
        inaccessible_ids = [
            document_id
            for document_id in requested_document_ids
            if document_id not in accessible_ids
        ]

        if inaccessible_ids:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": (
                        "One or more documents were not found "
                        "or are not accessible"
                    ),
                    "document_ids": [
                        str(document_id)
                        for document_id in inaccessible_ids
                    ],
                },
            )

    return list(accessible_ids)


@router.post("", response_model=QueryResponse)
def query_knowledge_base(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        conversation_id = request.conversation_id

        document_ids = resolve_accessible_document_ids(
            requested_document_ids=request.document_ids,
            current_user=current_user,
            db=db,
        )

        if not document_ids:
            raise HTTPException(
                status_code=404,
                detail="No accessible documents found",
            )

        is_new_conversation = conversation_id is None

        if is_new_conversation:
            conversation = create_conversation(
                user_id=current_user.id,
                title=request.question[:100],
            )

            conversation_id = conversation.id
            retrieval_question = request.question

        else:
            if not conversation_exists(
                conversation_id=conversation_id,
                user_id=current_user.id,
            ):
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found",
                )

            history = get_conversation_messages(
                conversation_id=conversation_id,
                user_id=current_user.id,
                limit=10,
            )

            retrieval_question = rewrite_followup_question(
                question=request.question,
                conversation_history=history,
            )

            logger.info(
               "Follow-up query rewritten | original=%s | rewritten=%s",
                request.question,
                retrieval_question,
)
        save_message(
            conversation_id=conversation_id,
            role="user",
            content=request.question,
        )

        RAG_QUERIES_TOTAL.inc()

        logger.info(
            "RAG query started | user_id=%s | conversation_id=%s | document_count=%s",
            current_user.id,
            conversation_id,
            len(document_ids),
        )
        result = answer_question(
            question=retrieval_question,
            document_ids=document_ids,
        )
        logger.info(
            "RAG query completed | user_id=%s | conversation_id=%s | sources=%s",
            current_user.id,
            conversation_id,
            len(result["sources"]),
        )

        save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=result["answer"],
        )

        return {
            "conversation_id": conversation_id,
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"],
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to answer question: {str(exc)}",
        )