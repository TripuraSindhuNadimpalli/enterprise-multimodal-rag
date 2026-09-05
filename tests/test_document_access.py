import uuid

from fastapi.testclient import TestClient

from api.main import app
from database.connection import get_db
from database.models import Document, User


client = TestClient(app)


USER_ONE_EMAIL = "pytest_access_user1@example.com"
USER_TWO_EMAIL = "pytest_access_user2@example.com"

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
            filename="pytest-private-document.pdf",
            content_type="application/pdf",
            storage_path=(
                f"pytest/{uuid.uuid4()}/"
                "private-document.pdf"
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


def test_user_can_list_own_document():
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

    try:
        response = client.get(
            "/documents",
            headers={
                "Authorization": (
                    f"Bearer {token}"
                ),
            },
        )

        assert response.status_code == 200

        documents = response.json()

        document_ids = [
            document["id"]
            for document in documents
        ]

        assert str(document_id) in document_ids

    finally:
        cleanup_test_document(
            document_id,
        )


def test_user_cannot_list_another_users_document():
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
        response = client.get(
            "/documents",
            headers={
                "Authorization": (
                    f"Bearer {user_one_token}"
                ),
            },
        )

        assert response.status_code == 200

        document_ids = [
            document["id"]
            for document in response.json()
        ]

        assert (
            str(document_id)
            not in document_ids
        )

    finally:
        cleanup_test_document(
            document_id,
        )


def test_user_can_get_own_document():
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

    try:
        response = client.get(
            f"/documents/{document_id}",
            headers={
                "Authorization": (
                    f"Bearer {token}"
                ),
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == str(
            document_id
        )

        assert data["user_id"] == str(
            user.id
        )

        assert (
            data["filename"]
            == "pytest-private-document.pdf"
        )

        assert (
            data["status"]
            == "processed"
        )

    finally:
        cleanup_test_document(
            document_id,
        )


def test_user_cannot_get_another_users_document():
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
        response = client.get(
            f"/documents/{document_id}",
            headers={
                "Authorization": (
                    f"Bearer {user_one_token}"
                ),
            },
        )

        assert response.status_code == 404

        assert (
            response.json()["detail"]
            == "Document not found"
        )

    finally:
        cleanup_test_document(
            document_id,
        )


def test_documents_require_authentication():
    response = client.get(
        "/documents"
    )

    assert response.status_code in [
        401,
        403,
    ]


def test_document_details_require_authentication():
    fake_document_id = uuid.uuid4()

    response = client.get(
        f"/documents/{fake_document_id}"
    )

    assert response.status_code in [
        401,
        403,
    ]