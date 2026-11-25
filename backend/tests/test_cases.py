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

def test_referral_requires_recorded_consent_and_handler_cannot_grant_it(client, auth_headers):
    member = auth_headers("member@test.demo")
    handler = auth_headers("casehandler@test.demo")
    created = client.post("/api/v1/cases", headers=member, json={"institution_id": 2, "scenario_code": "SCENARIO_SUPPORT", "anonymous": True, "consent_to_referral": False})
    ref = created.json()["case_ref"]
    denied = client.post(f"/api/v1/cases/{ref}/actions", headers=handler, json={"action": "referral"})
    assert denied.status_code == 409
    forged = client.post(f"/api/v1/cases/{ref}/actions", headers=handler, json={"action": "referral"})
    assert forged.status_code == 409
    consented = client.post("/api/v1/cases", headers=member, json={"institution_id": 2, "scenario_code": "SCENARIO_SUPPORT", "anonymous": True, "consent_to_referral": True})
    consented_ref = consented.json()["case_ref"]
    referred = client.post(f"/api/v1/cases/{consented_ref}/actions", headers=handler, json={"action": "referral"})
    assert referred.status_code == 200
    withdrawn = client.post(f"/api/v1/cases/{consented_ref}/actions", headers=handler, json={"action": "withdraw_referral_consent"})
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


def _create_case(client, auth_headers, consent=False):
    response = client.post("/api/v1/cases", headers=auth_headers("member@test.demo"), json={
        "institution_id": 2, "scenario_code": "SCENARIO_SUPPORT",
        "anonymous": True, "consent_to_referral": consent,
    })
    assert response.status_code == 201, response.text
    return response.json()["case_ref"]


def test_case_management_dashboard_and_queue_are_institution_scoped(client, auth_headers):
    ref = _create_case(client, auth_headers)
    handler = auth_headers("casehandler@test.demo")
    dashboard = client.get("/api/v1/case-management/dashboard", headers=handler)
    assert dashboard.status_code == 200
    assert dashboard.json()["total"] >= 1
    queue = client.get("/api/v1/case-management/queue?assigned=unassigned", headers=handler)
    assert queue.status_code == 200
    assert any(row["case_ref"] == ref for row in queue.json())
    denied = client.get("/api/v1/case-management/dashboard", headers=auth_headers("member@test.demo"))
    assert denied.status_code == 403


def test_case_assignment_requires_active_handler_in_same_institution(client, auth_headers):
    ref = _create_case(client, auth_headers)
    handler = auth_headers("casehandler@test.demo")
    from app.database import SessionLocal
    from app.models import User
    with SessionLocal() as db:
        handler_user_id = db.query(User).filter_by(email="casehandler@test.demo").one().id
        other_handler_id = db.query(User).filter_by(email="casehandler-b@test.demo").one().id
    assigned = client.post(f"/api/v1/cases/{ref}/assign", headers=handler, json={"assigned_to_user_id": handler_user_id})
    assert assigned.status_code == 201, assigned.text
    history = client.get(f"/api/v1/cases/{ref}/assignments", headers=handler)
    assert history.status_code == 200
    assert len(history.json()) == 1
    cross_institution = client.post(f"/api/v1/cases/{ref}/assign", headers=handler, json={"assigned_to_user_id": other_handler_id})
    assert cross_institution.status_code == 422


def test_workflow_requires_valid_human_transition_and_decision_code(client, auth_headers):
    ref = _create_case(client, auth_headers, consent=True)
    handler = auth_headers("casehandler@test.demo")
    invalid = client.post(f"/api/v1/cases/{ref}/workflow", headers=handler, json={"action": "close"})
    assert invalid.status_code == 409
    acknowledged = client.post(f"/api/v1/cases/{ref}/workflow", headers=handler, json={"action": "acknowledge"})
    assert acknowledged.status_code == 200
    reviewing = client.post(f"/api/v1/cases/{ref}/workflow", headers=handler, json={"action": "start_review"})
    assert reviewing.status_code == 200
    closed = client.post(f"/api/v1/cases/{ref}/workflow", headers=handler, json={"action": "close", "decision_code": "resolved"})
    assert closed.status_code == 200
    assert closed.json()["workflow_status"] == "closed"
    assert closed.json()["external_action_performed"] is False


def test_case_notes_are_predefined_and_encrypted(client, auth_headers):
    ref = _create_case(client, auth_headers)
    handler = auth_headers("casehandler@test.demo")
    created = client.post(f"/api/v1/cases/{ref}/notes", headers=handler, json={"note_code": "information_provided"})
    assert created.status_code == 201, created.text
    listed = client.get(f"/api/v1/cases/{ref}/notes", headers=handler)
    assert listed.status_code == 200
    assert listed.json()[0]["label"] == "Information was provided"
    invalid = client.post(f"/api/v1/cases/{ref}/notes", headers=handler, json={"note_code": "arbitrary_free_text"})
    assert invalid.status_code == 422
    from app.database import SessionLocal
    from app.models import CaseNote
    with SessionLocal() as db:
        note = db.query(CaseNote).filter_by(case_ref=ref).one()
        assert b"Information was provided" not in note.ciphertext
        assert len(note.nonce) == 12


def test_priority_is_human_set_and_audited(client, auth_headers):
    ref = _create_case(client, auth_headers)
    handler = auth_headers("casehandler@test.demo")
    response = client.patch(f"/api/v1/cases/{ref}/priority", headers=handler, json={"priority": "high"})
    assert response.status_code == 200
    assert response.json()["priority"] == "high"
    invalid = client.patch(f"/api/v1/cases/{ref}/priority", headers=handler, json={"priority": "critical-ai-score"})
    assert invalid.status_code == 422
