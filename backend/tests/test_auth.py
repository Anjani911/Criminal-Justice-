import pytest
from app.auth.security import get_password_hash
from app.models.employee import Employee


def seed_user(db_session, username, role="Investigator"):
    """Helper fixture seed user."""
    emp = Employee(
        username=username,
        hashed_password=get_password_hash("mypassword123"),
        name="Officer Test",
        rank="Sub-Inspector",
        role=role,
        badge_number=f"B-{username}",
        unit_name="Central PS"
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


def test_login_successful(client, db_session):
    # Seed user
    seed_user(db_session, "officer_1", "Investigator")

    # Perform login
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "officer_1", "password": "mypassword123"}
    )
    assert response.status_code == 200
    payload = response.json()
    assert "access_token" in payload
    assert payload["employee"]["username"] == "officer_1"
    assert payload["employee"]["role"] == "Investigator"


def test_login_invalid_credentials(client, db_session):
    seed_user(db_session, "officer_2", "Investigator")

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "officer_2", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_get_profile_me(client, db_session):
    seed_user(db_session, "officer_3", "Investigator")

    # Login to get token
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "officer_3", "password": "mypassword123"}
    )
    token = login_resp.json()["access_token"]

    # Request /me profile details
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["username"] == "officer_3"
    assert payload["role"] == "Investigator"


def test_auth_route_protected(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
