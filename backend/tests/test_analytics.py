import pytest
from datetime import datetime
from app.auth.security import get_password_hash
from app.models.employee import Employee
from app.models.crime_type import CrimeHead, CrimeSubHead
from app.models.case import CaseMaster


def seed_analytics_data(db):
    head = CrimeHead(code="THEFT", name="Theft")
    db.add(head)
    db.commit()
    db.refresh(head)

    sub = CrimeSubHead(crime_head_id=head.id, code="VEHICLE", name="Vehicle Theft")
    db.add(sub)
    db.commit()
    db.refresh(sub)

    officer = Employee(
        username="john_doe",
        hashed_password=get_password_hash("password123"),
        name="John Doe",
        rank="Inspector",
        role="Investigator",
        badge_number="INS-9999",
        unit_name="MG Road PS"
    )
    db.add(officer)
    db.commit()
    db.refresh(officer)

    case = CaseMaster(
        fir_number="MGR-2026-0005",
        incident_date=datetime(2026, 7, 5, 14, 0),
        registered_date=datetime(2026, 7, 5, 16, 0),
        status="Under Investigation",
        brief_facts="Bike stolen from parking space.",
        district="Bengaluru City",
        unit_name="MG Road PS",
        crime_head_id=head.id,
        crime_subhead_id=sub.id,
        investigating_officer_id=officer.id
    )
    db.add(case)
    db.commit()

    return officer


def test_analytics_endpoints(client, db_session):
    officer = seed_analytics_data(db_session)

    # Auth Login
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "john_doe", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test Dashboard KPIs
    response = client.get("/analytics/dashboard", headers=headers)
    assert response.status_code == 200
    kpis = response.json()
    assert kpis["total_cases"] == 1
    assert kpis["cases_under_investigation"] == 1

    # Test Crime Trends
    response = client.get("/analytics/crime-trends?year=2026", headers=headers)
    assert response.status_code == 200
    trends = response.json()
    assert len(trends) >= 1
    assert trends[0]["case_count"] == 1

    # Test Hotspots
    response = client.get("/analytics/hotspots", headers=headers)
    assert response.status_code == 200
    hotspots = response.json()
    assert len(hotspots["district_hotspots"]) == 1
    assert hotspots["district_hotspots"][0]["district"] == "Bengaluru City"
    assert hotspots["district_hotspots"][0]["case_count"] == 1

    # Test Crime Types
    response = client.get("/analytics/crime-types", headers=headers)
    assert response.status_code == 200
    ctypes = response.json()
    assert ctypes[0]["crime_head"] == "Theft"
    assert ctypes[0]["case_count"] == 1
