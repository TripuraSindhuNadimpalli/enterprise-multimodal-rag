from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert "name" in data
    assert "version" in data
    assert data["status"] == "running"


def test_register_user():
    email = "pytest_auth_user@example.com"
    password = "TestPassword123!"

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code in [201, 409]

    if response.status_code == 201:
        data = response.json()

        assert data["email"] == email
        assert data["role"] == "user"
        assert data["is_active"] is True
        assert "id" in data


def test_login_user():
    email = "pytest_auth_user@example.com"
    password = "TestPassword123!"

    # Make sure the test user exists.
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

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_login_with_wrong_password():
    email = "pytest_auth_user@example.com"
    password = "TestPassword123!"

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
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401

    assert (
        response.json()["detail"]
        == "Invalid email or password"
    )


def test_get_current_user():
    email = "pytest_auth_user@example.com"
    password = "TestPassword123!"

    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()[
        "access_token"
    ]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": (
                f"Bearer {token}"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == email
    assert data["role"] == "user"
    assert data["is_active"] is True


def test_get_current_user_without_token():
    response = client.get("/auth/me")

    assert response.status_code in [401, 403]


def test_get_current_user_with_invalid_token():
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": (
                "Bearer invalid-token"
            ),
        },
    )

    assert response.status_code == 401