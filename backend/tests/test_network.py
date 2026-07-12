import pytest
from datetime import datetime
from app.auth.security import get_password_hash
from app.models.employee import Employee
from app.models.crime_type import CrimeHead, CrimeSubHead
from app.models.case import CaseMaster
from app.models.people import Accused
from app.models.arrest import ArrestSurrender


def seed_network_data(db):
    head = CrimeHead(code="MURDER", name="Homicide")
    db.add(head)
    db.commit()
    db.refresh(head)

    sub = CrimeSubHead(crime_head_id=head.id, code="MURDER_302", name="Murder Section 302")
    db.add(sub)
    db.commit()
    db.refresh(sub)

    officer = Employee(
        username="sam_pi",
        hashed_password=get_password_hash("password123"),
        name="Sam PI",
        rank="Inspector",
        role="Investigator",
        badge_number="PI-4444",
        unit_name="Hebbal PS"
    )
    db.add(officer)
    db.commit()
    db.refresh(officer)

    case = CaseMaster(
        fir_number="HEB-2026-0001",
        incident_date=datetime(2026, 7, 1, 10, 0),
        registered_date=datetime(2026, 7, 2, 9, 0),
        status="Under Investigation",
        brief_facts="Altercation leading to death.",
        district="Bengaluru City",
        unit_name="Hebbal PS",
        crime_head_id=head.id,
        crime_subhead_id=sub.id,
        investigating_officer_id=officer.id
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    accused = Accused(
        case_id=case.id,
        name="Kiran Kumar",
        age=32,
        gender="Male",
        address="Hebbal, Bengaluru",
        phone="9898989898",
        status="Arrested"
    )
    db.add(accused)
    db.commit()
    db.refresh(accused)

    arrest = ArrestSurrender(
        case_id=case.id,
        accused_id=accused.id,
        arrest_date=datetime(2026, 7, 3, 6, 0),
        arrest_type="Arrested",
        arrest_by_employee_id=officer.id,
        remarks="Apprehended near railway station."
    )
    db.add(arrest)
    db.commit()

    return officer, case, accused


def test_network_endpoints(client, db_session):
    officer, case, accused = seed_network_data(db_session)

    # Auth Login
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "sam_pi", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test Full Network
    response = client.get("/api/v1/network", headers=headers)
    assert response.status_code == 200
    network = response.json()
    assert "nodes" in network
    assert "edges" in network
    assert network["metadata"]["node_count"] >= 3 # Case, Accused, Arrest

    # Test Network Metrics
    response = client.get("/api/v1/network/metrics", headers=headers)
    assert response.status_code == 200
    metrics = response.json()
    assert metrics["total_nodes"] >= 3
    assert len(metrics["top_accused"]) >= 1
    assert metrics["top_accused"][0]["label"] == "Kiran Kumar"

    # Test Case-Centric Graph
    response = client.get(f"/api/v1/network/case/{case.id}", headers=headers)
    assert response.status_code == 200
    case_network = response.json()
    assert case_network["metadata"]["node_count"] >= 3

    # Test Accused-Centric Graph
    response = client.get(f"/api/v1/network/accused/{accused.id}", headers=headers)
    assert response.status_code == 200
    acc_network = response.json()
    assert acc_network["metadata"]["node_count"] >= 3
