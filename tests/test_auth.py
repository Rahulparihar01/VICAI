import jwt
from fastapi.testclient import TestClient

from app.core.config import Settings


def register_customer(client: TestClient) -> dict:
    response = client.post(
        "/api/auth/registration",
        json={
            "email": "Customer@Example.com",
            "password": "customer-password-123",
            "full_name": "  Example   Customer  ",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_customer_can_register_and_log_in(client: TestClient) -> None:
    registered = register_customer(client)
    assert registered["user"]["identifier"] == "customer@example.com"
    assert registered["user"]["display_name"] == "Example Customer"
    assert registered["user"]["role"] == "customer"

    response = client.post(
        "/api/auth/login",
        json={"email": "customer@example.com", "password": "customer-password-123", "role": "customer"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "ok" not in body
    assert "expires_in" not in body
    assert body["next"] == "/app"
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert "exp" not in jwt.decode(
        body["access_token"],
        options={"verify_signature": False},
    )

    me = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["identifier"] == "customer@example.com"


def test_duplicate_registration_is_rejected(client: TestClient) -> None:
    register_customer(client)

    response = client.post(
        "/api/auth/registration",
        json={
            "email": "customer@example.com",
            "password": "another-password-123",
            "full_name": "Another Customer",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "AUTH_ACCOUNT_EXISTS"


def test_customer_login_uses_generic_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "missing@example.com", "password": "wrong", "role": "customer"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "AUTH_INVALID_CREDENTIALS",
            "message": "Email/ID or password is incorrect.",
        },
    }


def test_admin_logs_in_from_environment_credentials(
    client: TestClient,
    test_settings: Settings,
) -> None:
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_settings.admin_id,
            "password": test_settings.admin_password.get_secret_value(),
            "role": "super_admin",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "ok" not in body
    assert "expires_in" not in body
    assert body["next"] == "/admin"
    assert body["user"]["role"] == "super_admin"

    me = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["id"] == "super_admin"


def test_invalid_admin_credentials_are_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "test-admin", "password": "incorrect", "role": "super_admin"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_INVALID_CREDENTIALS"


def test_me_requires_a_bearer_token(client: TestClient) -> None:
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"
