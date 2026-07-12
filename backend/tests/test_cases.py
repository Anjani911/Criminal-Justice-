import pytest
from datetime import datetime
from app.auth.security import get_password_hash
from app.models.employee import Employee
from app.models.crime_type import CrimeHead, CrimeSubHead
from app.models.case import CaseMaster


def seed_metadata(db):
    """Seed base classifications and an officer."""
    head = CrimeHead(code="CYBER", name="Cyber Crimes")
    db.add(head)
    db.commit()
    db.refresh(head)

    sub = CrimeSubHead(crime_head_id=head.id, code="PHISH", name="Phishing")
    db.add(sub)
    db.commit()
    db.refresh(sub)

    officer = Employee(
        username="karan_psi",
        hashed_password=get_password_hash("password123"),
        name="Karan PSI",
        rank="Psi",
        role="Investigator",
        badge_number="PSI-1234",
        unit_name="Indiranagar PS"
    )
    db.add(officer)
    db.commit()
    db.refresh(officer)

    return head, sub, officer


def test_create_and_get_case(client, db_session):
    head, sub, officer = seed_metadata(db_session)

    # Login to get authorization token
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "karan_psi", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_payload = {
        "fir_number": "IND-2026-0099",
        "incident_date": datetime(2026, 7, 10, 10, 0).isoformat(),
        "registered_date": datetime(2026, 7, 10, 12, 0).isoformat(),
        "status": "Under Investigation",
        "brief_facts": "Stolen credentials and online fund transfer.",
        "district": "Bengaluru City",
        "unit_name": "Indiranagar PS",
        "crime_head_id": head.id,
        "crime_subhead_id": sub.id,
        "investigating_officer_id": officer.id
    }

    # Test Create Case
    response = client.post("/api/v1/cases", json=case_payload, headers=headers)
    assert response.status_code == 201
    payload = response.json()
    assert payload["fir_number"] == "IND-2026-0099"
    assert payload["status"] == "Under Investigation"

    # Test Duplicate FIR Rejection (409 Conflict)
    dup_response = client.post("/api/v1/cases", json=case_payload, headers=headers)
    assert dup_response.status_code == 409

    # Test Get Case Details
    case_id = payload["id"]
    get_response = client.get(f"/api/v1/cases/{case_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["fir_number"] == "IND-2026-0099"


def test_update_case_status(client, db_session):
    head, sub, officer = seed_metadata(db_session)

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "karan_psi", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case = CaseMaster(
        fir_number="IND-2026-0100",
        incident_date=datetime.utcnow(),
        registered_date=datetime.utcnow(),
        status="Under Investigation",
        brief_facts="Card skimmed.",
        district="Bengaluru City",
        unit_name="Indiranagar PS",
        crime_head_id=head.id,
        crime_subhead_id=sub.id,
        investigating_officer_id=officer.id
    )
    db_session.add(case)
    db_session.commit()

    # PATCH request to update status
    patch_response = client.patch(
        f"/api/v1/cases/{case.id}/status",
        json={"status": "Chargesheeted"},
        headers=headers
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["status"] == "Chargesheeted"
