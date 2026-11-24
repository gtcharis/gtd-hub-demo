from datetime import datetime, timezone
from uuid import uuid4
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models import User, Institution, SecureCase, CaseAuditEvent, SupportService
from app.auth_dependencies import get_current_user, require_permission
from app.role_policy import role_can_access_institution
from app.case_security import encrypt_case, decrypt_case, audit_digest
from app.schemas.cases import CaseCreate, CaseAction

router = APIRouter(tags=["support and secure cases"])
SCENARIOS = {
    "SCENARIO_SUPPORT": {"label": "Request for information and support", "narrative": "Synthetic demonstration scenario: a participant requests information about available support options."},
    "SCENARIO_HARASSMENT": {"label": "Illustrative harassment concern", "narrative": "Synthetic demonstration scenario: a participant wishes to understand reporting and support options."},
    "SCENARIO_DISCRIMINATION": {"label": "Illustrative discrimination concern", "narrative": "Synthetic demonstration scenario: a participant requests information about institutional support pathways."},
}

def _scope(user: User, institution_id: int):
    if user.role == "Programme Administrator": return
    if user.institution_id != institution_id:
        raise HTTPException(status_code=403, detail="Institution boundary: access denied")

def _audit(db: Session, case: SecureCase, actor: User, action: str, extra: dict | None = None):
    # Serialize hash-chain appends within PostgreSQL transactions.
    db.execute(text("SELECT pg_advisory_xact_lock(731904221)"))
    last = db.query(CaseAuditEvent).order_by(CaseAuditEvent.sequence.desc()).with_for_update().first()
    sequence = (last.sequence + 1) if last else 1
    previous = last.event_hash if last else "0" * 64
    # No narrative, contact details, or decrypted payload may enter this event.
    audit_actor_id = None if action == "case_created" and case.anonymous else actor.id
    event = {"action": action, "case_ref": case.case_ref, "institution_id": case.institution_id, "actor_user_id": audit_actor_id, "extra": extra or {}}
    event_json = json.dumps(event, sort_keys=True, separators=(",", ":"))
    digest = audit_digest(sequence, previous, event_json)
    db.add(CaseAuditEvent(sequence=sequence, case_ref=case.case_ref, institution_id=case.institution_id, actor_user_id=audit_actor_id, action=action, event_json=event_json, previous_hash=previous, event_hash=digest))

@router.get("/support/services")
def support_services(db: Session = Depends(get_db), user: User = Depends(require_permission("support:read"))):
    rows = db.query(SupportService).filter(SupportService.is_published.is_(True)).filter((SupportService.institution_id.is_(None)) | (SupportService.institution_id == user.institution_id)).all()
    return [{"id": r.id, "category": r.category, "title": r.title, "description": r.description, "contact_label": r.contact_label, "institution_id": r.institution_id} for r in rows]

@router.post("/cases", status_code=201)
def create_case(payload: CaseCreate, db: Session = Depends(get_db), user: User = Depends(require_permission("reporting:create"))):
    institution = db.get(Institution, payload.institution_id)
    if not institution or not institution.is_active: raise HTTPException(status_code=404, detail="Institution not found")
    _scope(user, payload.institution_id)
    if payload.scenario_code not in SCENARIOS: raise HTTPException(status_code=422, detail="Unknown demonstration scenario")
    case_ref = str(uuid4())
    # The demonstrator stores only a predefined synthetic scenario; no free-text disclosure or contact fields are accepted.
    protected = {"scenario": SCENARIOS[payload.scenario_code], "synthetic": True, "contact": None}
    ciphertext, nonce, version = encrypt_case(protected, case_ref, payload.institution_id)
    case = SecureCase(case_ref=case_ref, institution_id=payload.institution_id, created_by_user_id=None if payload.anonymous else user.id, anonymous=payload.anonymous, scenario_code=payload.scenario_code, workflow_status="received", consent_status="granted" if payload.consent_to_referral else "not_granted", ciphertext=ciphertext, nonce=nonce, key_version=version)
    db.add(case); db.flush()
    _audit(db, case, user, "case_created", {"anonymous": payload.anonymous, "consent": case.consent_status})
    db.commit()
    return {"case_ref": case.case_ref, "workflow_status": case.workflow_status, "consent_status": case.consent_status, "synthetic": True, "message": "Synthetic demonstration record created. This is not a live safeguarding service."}

@router.get("/cases")
def list_cases(db: Session = Depends(get_db), user: User = Depends(require_permission("cases:read"))):
    q = db.query(SecureCase)
    if user.role != "Programme Administrator":
        if user.role != "Case Handler" or user.institution_id is None: raise HTTPException(status_code=403, detail="Case access denied")
        q = q.filter(SecureCase.institution_id == user.institution_id)
    rows = q.order_by(SecureCase.created_at.desc()).all()
    result = []
    for case in rows:
        _audit(db, case, user, "case_metadata_read")
        result.append({"case_ref": case.case_ref, "institution_id": case.institution_id, "scenario_code": case.scenario_code, "workflow_status": case.workflow_status, "consent_status": case.consent_status, "anonymous": case.anonymous, "created_at": case.created_at})
    db.commit()
    return result

@router.get("/cases/{case_ref}")
def read_case(case_ref: str, db: Session = Depends(get_db), user: User = Depends(require_permission("cases:read"))):
    case = db.query(SecureCase).filter(SecureCase.case_ref == case_ref).first()
    if not case: raise HTTPException(status_code=404, detail="Case not found")
    if user.role != "Programme Administrator" and (user.role != "Case Handler" or user.institution_id != case.institution_id): raise HTTPException(status_code=403, detail="Case access denied")
    data = decrypt_case(case.ciphertext, case.nonce, case.key_version, case.case_ref, case.institution_id)
    _audit(db, case, user, "case_payload_read")
    db.commit()
    return {"case_ref": case.case_ref, "institution_id": case.institution_id, "workflow_status": case.workflow_status, "consent_status": case.consent_status, "synthetic": data["synthetic"], "scenario": data["scenario"]}

@router.post("/cases/{case_ref}/actions")
def case_action(case_ref: str, payload: CaseAction, db: Session = Depends(get_db), user: User = Depends(require_permission("cases:manage"))):
    case = db.query(SecureCase).filter(SecureCase.case_ref == case_ref).with_for_update().first()
    if not case: raise HTTPException(status_code=404, detail="Case not found")
    if user.role != "Programme Administrator" and (user.role != "Case Handler" or user.institution_id != case.institution_id): raise HTTPException(status_code=403, detail="Case access denied")
    if payload.action == "withdraw_referral_consent":
        case.consent_status = "withdrawn"
        case.updated_at = datetime.now(timezone.utc)
        _audit(db, case, user, "referral_consent_withdrawn")
        db.commit()
        return {"case_ref": case.case_ref, "workflow_status": case.workflow_status, "consent_status": case.consent_status, "human_action_required": True}
    if payload.action == "referral":
        if payload.consent is True: case.consent_status = "granted"
        if case.consent_status != "granted": raise HTTPException(status_code=409, detail="Referral cannot proceed without recorded consent")
    if payload.action == "close": case.workflow_status = "closed"
    elif payload.action == "acknowledge": case.workflow_status = "acknowledged"
    elif payload.action == "under_review": case.workflow_status = "under_review"
    elif payload.action == "information_only": case.workflow_status = "information_only"
    elif payload.action == "referral": case.workflow_status = "referral_pending_human_action"
    elif payload.action == "institutional_action": case.workflow_status = "institutional_action_pending_human_action"
    elif payload.action == "emergency_escalation": case.workflow_status = "emergency_escalation_pending_human_action"
    case.updated_at = datetime.now(timezone.utc)
    _audit(db, case, user, "case_" + payload.action, {"consent_status": case.consent_status, "workflow_status": case.workflow_status})
    db.commit()
    return {"case_ref": case.case_ref, "workflow_status": case.workflow_status, "consent_status": case.consent_status, "human_action_required": True}

@router.get("/cases/{case_ref}/audit")
def case_audit(case_ref: str, db: Session = Depends(get_db), user: User = Depends(require_permission("cases:read"))):
    case = db.query(SecureCase).filter(SecureCase.case_ref == case_ref).first()
    if not case: raise HTTPException(status_code=404, detail="Case not found")
    if user.role != "Programme Administrator" and (user.role != "Case Handler" or user.institution_id != case.institution_id): raise HTTPException(status_code=403, detail="Case access denied")
    events = db.query(CaseAuditEvent).filter(CaseAuditEvent.case_ref == case_ref).order_by(CaseAuditEvent.sequence).all()
    # Verify the complete global chain, not only this case's subset.
    chain = db.query(CaseAuditEvent).order_by(CaseAuditEvent.sequence).all()
    previous = "0" * 64
    for expected_sequence, event in enumerate(chain, start=1):
        if event.sequence != expected_sequence or event.previous_hash != previous:
            raise HTTPException(status_code=503, detail="Audit integrity verification failed")
        if audit_digest(event.sequence, event.previous_hash, event.event_json) != event.event_hash:
            raise HTTPException(status_code=503, detail="Audit integrity verification failed")
        previous = event.event_hash
    _audit(db, case, user, "case_audit_read", {"integrity_verified": True})
    db.commit()
    return {"integrity_valid": True, "events": [{"sequence": e.sequence, "action": e.action, "actor_user_id": e.actor_user_id, "created_at": e.created_at, "event_hash": e.event_hash, "previous_hash": e.previous_hash} for e in events]}
