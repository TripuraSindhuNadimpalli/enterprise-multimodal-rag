import uuid

from fastapi.testclient import TestClient

from api.main import app
from database.connection import get_db
from database.models import Document, User


client = TestClient(app)


USER_ONE_EMAIL = "pytest_query_user1@example.com"
USER_TWO_EMAIL = "pytest_query_user2@example.com"

USER_ONE_PASSWORD = "TestPassword123!"
USER_TWO_PASSWORD = "TestPassword456!"


def register_and_login(
    email: str,
    password: str,
) -> str:
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def get_user_by_email(
    email: str,
) -> User:
    db = next(get_db())

    try:
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        assert user is not None

        return user

    finally:
        db.close()


def create_test_document(
    user_id: uuid.UUID,
) -> uuid.UUID:
    db = next(get_db())

    try:
        document = Document(
            id=uuid.uuid4(),
            user_id=user_id,
            filename="pytest-query-document.pdf",
            content_type="application/pdf",
            storage_path=(
                f"pytest/{uuid.uuid4()}/"
                "query-document.pdf"
            ),
            status="processed",
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document.id

    finally:
        db.close()


def cleanup_test_document(
    document_id: uuid.UUID,
):
    db = next(get_db())

    try:
        document = (
            db.query(Document)
            .filter(
                Document.id == document_id
            )
            .first()
        )

        if document is not None:
            db.delete(document)
            db.commit()

    finally:
        db.close()


def test_query_requires_authentication():
    response = client.post(
        "/query",
        json={
            "question": "What is this document about?",
            "document_ids": [],
        },
    )

    assert response.status_code in [
        401,
        403,
    ]


def test_user_cannot_query_another_users_document():
    user_one_token = register_and_login(
        USER_ONE_EMAIL,
        USER_ONE_PASSWORD,
    )

    register_and_login(
        USER_TWO_EMAIL,
        USER_TWO_PASSWORD,
    )

    user_two = get_user_by_email(
        USER_TWO_EMAIL,
    )

    document_id = create_test_document(
        user_two.id,
    )

    try:
        response = client.post(
            "/query",
            headers={
                "Authorization": (
                    f"Bearer {user_one_token}"
                ),
            },
            json={
                "question": (
                    "What is this document about?"
                ),
                "document_ids": [
                    str(document_id)
                ],
            },
        )

        assert response.status_code == 404

        detail = response.json()["detail"]

        assert isinstance(detail, dict)

        assert (
            detail["message"]
            == (
                "One or more documents were not found "
                "or are not accessible"
            )
        )

        assert str(document_id) in (
            detail["document_ids"]
        )

    finally:
        cleanup_test_document(
            document_id,
        )


def test_user_with_no_accessible_documents_gets_404():
    token = register_and_login(
        USER_ONE_EMAIL,
        USER_ONE_PASSWORD,
    )

    response = client.post(
        "/query",
        headers={
            "Authorization": (
                f"Bearer {token}"
            ),
        },
        json={
            "question": (
                "What documents do I have?"
            ),
            "document_ids": None,
        },
    )

    assert response.status_code == 404

    assert (
        response.json()["detail"]
        == "No accessible documents found"
    )


def test_invalid_conversation_id_is_private():
    token = register_and_login(
        USER_ONE_EMAIL,
        USER_ONE_PASSWORD,
    )

    user = get_user_by_email(
        USER_ONE_EMAIL,
    )

    document_id = create_test_document(
        user.id,
    )

    fake_conversation_id = uuid.uuid4()

    try:
        response = client.post(
            "/query",
            headers={
                "Authorization": (
                    f"Bearer {token}"
                ),
            },
            json={
                "question": (
                    "Tell me more about it."
                ),
                "conversation_id": (
                    str(fake_conversation_id)
                ),
                "document_ids": [
                    str(document_id)
                ],
            },
        )

        assert response.status_code == 404

        assert (
            response.json()["detail"]
            == "Conversation not found"
        )

    finally:
        cleanup_test_document(
            document_id,
        )