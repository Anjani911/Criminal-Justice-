import pytest
from datetime import datetime
from app.auth.security import get_password_hash
from app.models.employee import Employee
from app.models.crime_type import CrimeHead, CrimeSubHead
from app.models.case import CaseMaster
from app.models.people import Accused


def seed_base_data(db):
    head = CrimeHead(code="FRAUD", name="Financial Fraud")
    db.add(head)
    db.commit()
    db.refresh(head)

    sub = CrimeSubHead(crime_head_id=head.id, code="CHATING", name="Cheating")
    db.add(sub)
    db.commit()
    db.refresh(sub)

    officer = Employee(
        username="vijay_psi",
        hashed_password=get_password_hash("password123"),
        name="Vijay PSI",
        rank="Psi",
        role="Investigator",
        badge_number="PSI-5555",
        unit_name="Whitefield PS"
    )
    db.add(officer)
    db.commit()
    db.refresh(officer)

    case = CaseMaster(
        fir_number="WHI-2026-0033",
        incident_date=datetime(2026, 7, 10, 10, 0),
        registered_date=datetime(2026, 7, 10, 12, 0),
        status="Under Investigation",
        brief_facts="Land fraud with forged deeds.",
        district="Bengaluru City",
        unit_name="Whitefield PS",
        crime_head_id=head.id,
        crime_subhead_id=sub.id,
        investigating_officer_id=officer.id
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    # Seed an absconding suspect
    absconding_acc = Accused(
        case_id=case.id,
        name="Scamster Roy",
        age=45,
        gender="Male",
        address="Kolkata, WB",
        phone="9999999999",
        status="Absconding"
    )
    db.add(absconding_acc)
    db.commit()

    return officer, case


def test_people_endpoints(client, db_session):
    officer, case = seed_base_data(db_session)

    # Login to get authorization token
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "vijay_psi", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Test GET Absconding Accused
    abs_response = client.get("/accused/absconding", headers=headers)
    assert abs_response.status_code == 200
    abs_list = abs_response.json()
    assert len(abs_list) == 1
    assert abs_list[0]["name"] == "Scamster Roy"
    assert abs_list[0]["status"] == "Absconding"

    # 2. Test POST Add Accused to Case
    acc_payload = {
        "name": "Co-Conspirator Sen",
        "age": 38,
        "gender": "Female",
        "address": "Whitefield, Bengaluru",
        "phone": "9876543211",
        "status": "Suspect"
    }
    post_acc_response = client.post(
        f"/cases/{case.id}/accused",
        json=acc_payload,
        headers=headers
    )
    assert post_acc_response.status_code == 201
    assert post_acc_response.json()["name"] == "Co-Conspirator Sen"

    # 3. Test POST Add Victim to Case
    vic_payload = {
        "name": "Deceived Landlord",
        "age": 67,
        "gender": "Male",
        "address": "Whitefield, Bengaluru",
        "phone": "9000000000",
        "injury_type": "None"
    }
    post_vic_response = client.post(
        f"/cases/{case.id}/victims",
        json=vic_payload,
        headers=headers
    )
    assert post_vic_response.status_code == 201
    assert post_vic_response.json()["name"] == "Deceived Landlord"

    # 4. Test GET Accused for Case
    get_acc_response = client.get(f"/cases/{case.id}/accused", headers=headers)
    assert get_acc_response.status_code == 200
    assert len(get_acc_response.json()) == 2 # Scamster Roy + Co-Conspirator Sen

    # 5. Test GET Victims for Case
    get_vic_response = client.get(f"/cases/{case.id}/victims", headers=headers)
    assert get_vic_response.status_code == 200
    assert len(get_vic_response.json()) == 1

    # 6. Test Search Accused
    search_response = client.get("/accused/search?name=Scamster", headers=headers)
    assert search_response.status_code == 200
    assert len(search_response.json()) == 1
    assert search_response.json()[0]["name"] == "Scamster Roy"
