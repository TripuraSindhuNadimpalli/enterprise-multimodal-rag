from sqlalchemy import text

from database.base import Base
from database.connection import engine
from database.models import Conversation, Document, DocumentChunk, Message


def init_db() -> None:
    with engine.begin() as connection:
        connection.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully")