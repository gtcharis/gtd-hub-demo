import base64
import pytest
from app.models import SecureCase

@pytest.fixture(autouse=True)
def test_case_keys(monkeypatch):
    monkeypatch.setenv("CASE_ENCRYPTION_KEY", base64.urlsafe_b64encode(b"e" * 32).decode())
    monkeypatch.setenv("CASE_AUDIT_HMAC_KEY", base64.urlsafe_b64encode(b"a" * 32).decode())

def test_member_can_create_synthetic_case_and_case_handler_can_read(client, auth_headers):
    created = client.post("/api/v1/cases", headers=auth_headers("member@test.demo"), json={"institution_id": 2, "scenario_code": "SCENARIO_SUPPORT", "anonymous": True, "consent_to_referral": False})
    assert created.status_code == 201, created.text
    ref = created.json()["case_ref"]
    listed = client.get("/api/v1/cases", headers=auth_headers("casehandler@test.demo"))
    assert listed.status_code == 200
    assert any(x["case_ref"] == ref for x in listed.json())
    detail = client.get(f"/api/v1/cases/{ref}", headers=auth_headers("casehandler@test.demo"))
    assert detail.status_code == 200
    assert detail.json()["synthetic"] is True

def test_case_payload_is_not_stored_as_plaintext(client, auth_headers):
    response = client.post("/api/v1/cases", headers=auth_headers("member@test.demo"), json={"institution_id": 2, "scenario_code": "SCENARIO_HARASSMENT", "anonymous": True, "consent_to_referral": False})
    assert response.status_code == 201
    from app.database import SessionLocal
    with SessionLocal() as db:
        case = db.query(SecureCase).filter_by(case_ref=response.json()["case_ref"]).one()
        assert b"Synthetic demonstration scenario" not in case.ciphertext
        assert len(case.nonce) == 12

def test_case_handler_cannot_read_other_institution_case(client, auth_headers):
    created = client.post("/api/v1/cases", headers=auth_headers("member@test.demo"), json={"institution_id": 2, "scenario_code": "SCENARIO_SUPPORT", "anonymous": True, "consent_to_referral": False})
    assert created.status_code == 201
    ref = created.json()["case_ref"]
    # Case Handler B is created for this test and scoped to institution B.
    from app.database import SessionLocal
    from app.models import User
    from app.security import hash_password
    with SessionLocal() as db:
        if not db.query(User).filter_by(email="casehandler-b@test.demo").first():
            db.add(User(email="casehandler-b@test.demo", full_name="Case Handler B", role="Case Handler", institution_id=3, password_hash=hash_password("TestPass!2026")))
            db.commit()
    denied = client.get(f"/api/v1/cases/{ref}", headers=auth_headers("casehandler-b@test.demo"))
    assert denied.status_code == 403

def test_referral_requires_consent_and_withdrawal_is_recorded(client, auth_headers):
    created = client.post("/api/v1/cases", headers=auth_headers("member@test.demo"), json={"institution_id": 2, "scenario_code": "SCENARIO_SUPPORT", "anonymous": True, "consent_to_referral": False})
    ref = created.json()["case_ref"]
    handler = auth_headers("casehandler@test.demo")
    denied = client.post(f"/api/v1/cases/{ref}/actions", headers=handler, json={"action": "referral"})
    assert denied.status_code == 409
    granted = client.post(f"/api/v1/cases/{ref}/actions", headers=handler, json={"action": "referral", "consent": True})
    assert granted.status_code == 200
    withdrawn = client.post(f"/api/v1/cases/{ref}/actions", headers=handler, json={"action": "withdraw_referral_consent"})
    assert withdrawn.status_code == 200
    assert withdrawn.json()["consent_status"] == "withdrawn"

def test_case_operations_fail_closed_without_encryption_key(client, auth_headers, monkeypatch):
    monkeypatch.delenv("CASE_ENCRYPTION_KEY", raising=False)
    response = client.post("/api/v1/cases", headers=auth_headers("member@test.demo"), json={"institution_id": 2, "scenario_code": "SCENARIO_SUPPORT", "anonymous": True, "consent_to_referral": False})
    assert response.status_code == 503


def test_audit_endpoint_reports_chain_integrity(client, auth_headers):
    created = client.post("/api/v1/cases", headers=auth_headers("member@test.demo"), json={"institution_id": 2, "scenario_code": "SCENARIO_SUPPORT", "anonymous": True, "consent_to_referral": False})
    ref = created.json()["case_ref"]
    result = client.get(f"/api/v1/cases/{ref}/audit", headers=auth_headers("casehandler@test.demo"))
    assert result.status_code == 200
    assert result.json()["integrity_valid"] is True
