import uuid

from sqlalchemy import select

from database.connection import SessionLocal
from database.models import Conversation, Message


def create_conversation(
    user_id: uuid.UUID,
    title: str | None = None,
) -> Conversation:
    db = SessionLocal()

    try:
        conversation = Conversation(
            user_id=user_id,
            title=title,
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    finally:
        db.close()


def save_message(
    conversation_id: uuid.UUID,
    role: str,
    content: str,
) -> Message:
    db = SessionLocal()

    try:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        return message

    finally:
        db.close()


def get_conversation_messages(
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    limit: int = 10,
) -> list[Message]:
    db = SessionLocal()

    try:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            .first()
        )

        if conversation is None:
            return []

        statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        messages = list(
            db.scalars(statement).all()
        )

        messages.reverse()

        return messages

    finally:
        db.close()


def conversation_exists(
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    db = SessionLocal()

    try:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            .first()
        )

        return conversation is not None

    finally:
        db.close()