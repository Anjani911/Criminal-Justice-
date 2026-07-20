import pytest
from app.auth.security import get_password_hash
from app.models.employee import Employee
from app.services.audit_service import audit_service


def seed_user(db_session, username, role):
    emp = Employee(
        username=username,
        hashed_password=get_password_hash("mypassword123"),
        name=f"User {username}",
        rank="Sub-Inspector",
        role=role,
        badge_number=f"B-{username}",
        unit_name="Central PS"
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


def test_audit_log_creation(db_session):
    emp = seed_user(db_session, "audit_user_1", "Administrator")
    
    # Test creation via service
    log = audit_service.log_action(
        db=db_session,
        employee_id=emp.id,
        username=emp.username,
        role=emp.role,
        action="test_action",
        resource_type="test_resource",
        status="Success"
    )
    assert log is not None
    assert log.id is not None
    assert log.username == "audit_user_1"
    assert log.action == "test_action"


def test_admin_can_retrieve_logs(client, db_session):
    admin = seed_user(db_session, "admin_user", "Administrator")
    
    # Log an action
    audit_service.log_action(
        db=db_session,
        employee_id=admin.id,
        username=admin.username,
        role=admin.role,
        action="admin_action",
        resource_type="test",
        status="Success"
    )

    # Login to get token
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "admin_user", "password": "mypassword123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch audit logs
    resp = client.get("/api/v1/audit", headers=headers)
    assert resp.status_code == 200
    
    data = resp.json()
    assert "total" in data
    assert "logs" in data
    assert data["total"] >= 1
    
    actions = [log["action"] for log in data["logs"]]
    assert "admin_action" in actions


def test_investigator_forbidden_from_logs(client, db_session):
    investigator = seed_user(db_session, "investigator_user", "Investigator")

    # Login to get token
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "investigator_user", "password": "mypassword123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to fetch audit logs
    resp = client.get("/api/v1/audit", headers=headers)
    assert resp.status_code == 403


def test_login_creates_audit_log(client, db_session):
    emp = seed_user(db_session, "login_test_user", "Investigator")
    
    # Perform successful login
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "login_test_user", "password": "mypassword123"}
    )
    assert resp.status_code == 200
    
    # Perform failed login
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "login_test_user", "password": "wrongpassword"}
    )
    assert resp.status_code == 401

    # Verify logs using the service layer
    result = audit_service.get_logs(db_session, username="login_test_user")
    logs = [log.action for log in result["logs"] if log.username == "login_test_user"]
    
    # Expecting 2 login actions
    assert "login" in logs
