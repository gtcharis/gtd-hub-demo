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
        # Staff cannot grant consent on a participant's behalf.
        if case.consent_status != "granted": raise HTTPException(status_code=409, detail="Referral cannot proceed without recorded consent")
    if payload.action == "acknowledge": case.workflow_status = "acknowledged"
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

# v0.3.3 case-management endpoints. These record human decisions; they do not
# assess risk, make safeguarding decisions, or send referrals/alerts.
from fastapi import Query
from app.models import CaseAssignment, CaseNote
from app.schemas.cases import CaseAssignmentCreate, CaseWorkflowUpdate, CaseNoteCreate, CasePriorityUpdate

NOTE_LABELS = {
    "contact_attempt_recorded": "A contact attempt was recorded",
    "information_provided": "Information was provided",
    "consent_checked": "Consent status was checked",
    "referral_discussed": "A referral option was discussed",
    "institutional_process_discussed": "An institutional process was discussed",
    "follow_up_required": "A follow-up was identified as required",
    "closure_reviewed": "Closure was reviewed by an authorised handler",
}

WORKFLOW_TRANSITIONS = {
    "received": {"acknowledge": "acknowledged"},
    "acknowledged": {"start_review": "under_review", "information_only": "information_only"},
    "under_review": {
        "information_only": "information_only",
        "refer": "referral_pending_human_action",
        "institutional_action": "institutional_action_pending_human_action",
        "emergency_escalation": "emergency_escalation_pending_human_action",
        "close": "closed",
    },
    "information_only": {"start_review": "under_review", "close": "closed"},
    "referral_pending_human_action": {"start_review": "under_review", "close": "closed"},
    "institutional_action_pending_human_action": {"start_review": "under_review", "close": "closed"},
    "emergency_escalation_pending_human_action": {"start_review": "under_review", "close": "closed"},
    "closed": {"reopen": "under_review"},
}


def _get_scoped_case(db: Session, case_ref: str, user: User, *, lock: bool = False) -> SecureCase:
    query = db.query(SecureCase).filter(SecureCase.case_ref == case_ref)
    if lock:
        query = query.with_for_update()
    case = query.first()
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    if user.role == "Programme Administrator":
        return case
    if user.role != "Case Handler" or user.institution_id != case.institution_id:
        raise HTTPException(status_code=403, detail="Case access denied")
    return case


@router.get("/case-management/dashboard")
def case_management_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("cases:read")),
):
    query = db.query(SecureCase)
    if user.role != "Programme Administrator":
        if user.role != "Case Handler" or user.institution_id is None:
            raise HTTPException(status_code=403, detail="Case access denied")
        query = query.filter(SecureCase.institution_id == user.institution_id)
    rows = query.all()
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.workflow_status] = counts.get(row.workflow_status, 0) + 1
    assigned_to_me = sum(1 for row in rows if row.assigned_to_user_id == user.id)
    unassigned = sum(1 for row in rows if row.assigned_to_user_id is None)
    _audit_dashboard = rows[:1]
    if _audit_dashboard:
        _audit(db, _audit_dashboard[0], user, "case_dashboard_read", {"visible_case_count": len(rows)})
        db.commit()
    return {"total": len(rows), "assigned_to_me": assigned_to_me, "unassigned": unassigned, "by_status": counts}


@router.get("/case-management/queue")
def case_management_queue(
    status: str | None = Query(default=None, max_length=40),
    assigned: str = Query(default="all", pattern="^(all|mine|unassigned)$"),
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("cases:read")),
):
    query = db.query(SecureCase)
    if user.role != "Programme Administrator":
        if user.role != "Case Handler" or user.institution_id is None:
            raise HTTPException(status_code=403, detail="Case access denied")
        query = query.filter(SecureCase.institution_id == user.institution_id)
    if status:
        query = query.filter(SecureCase.workflow_status == status)
    if assigned == "mine":
        query = query.filter(SecureCase.assigned_to_user_id == user.id)
    elif assigned == "unassigned":
        query = query.filter(SecureCase.assigned_to_user_id.is_(None))
    rows = query.order_by(SecureCase.created_at.desc()).limit(200).all()
    return [{
        "case_ref": row.case_ref,
        "institution_id": row.institution_id,
        "scenario_code": row.scenario_code,
        "workflow_status": row.workflow_status,
        "consent_status": row.consent_status,
        "anonymous": row.anonymous,
        "priority": row.priority,
        "assigned_to_user_id": row.assigned_to_user_id,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    } for row in rows]


@router.post("/cases/{case_ref}/assign", status_code=201)
def assign_case(
    case_ref: str,
    payload: CaseAssignmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("cases:manage")),
):
    case = _get_scoped_case(db, case_ref, user, lock=True)
    target = db.get(User, payload.assigned_to_user_id)
    if target is None or not target.is_active or target.role != "Case Handler":
        raise HTTPException(status_code=422, detail="Assignment target must be an active Case Handler")
    if target.institution_id != case.institution_id:
        raise HTTPException(status_code=422, detail="A case can only be assigned to a Case Handler in its institution")
    case.assigned_to_user_id = target.id
    case.assigned_at = datetime.now(timezone.utc)
    case.updated_at = datetime.now(timezone.utc)
    db.add(CaseAssignment(
        case_ref=case.case_ref,
        institution_id=case.institution_id,
        assigned_to_user_id=target.id,
        assigned_by_user_id=user.id,
    ))
    _audit(db, case, user, "case_assigned", {"assigned_to_user_id": target.id})
    db.commit()
    return {"case_ref": case.case_ref, "assigned_to_user_id": target.id, "assigned_at": case.assigned_at}


@router.get("/cases/{case_ref}/assignments")
def case_assignments(
    case_ref: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("cases:read")),
):
    case = _get_scoped_case(db, case_ref, user)
    rows = db.query(CaseAssignment).filter(CaseAssignment.case_ref == case.case_ref).order_by(CaseAssignment.created_at.asc()).all()
    _audit(db, case, user, "case_assignment_history_read")
    db.commit()
    return [{"assigned_to_user_id": row.assigned_to_user_id, "assigned_by_user_id": row.assigned_by_user_id, "created_at": row.created_at} for row in rows]


@router.post("/cases/{case_ref}/workflow")
def update_case_workflow(
    case_ref: str,
    payload: CaseWorkflowUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("cases:manage")),
):
    case = _get_scoped_case(db, case_ref, user, lock=True)
    target_status = WORKFLOW_TRANSITIONS.get(case.workflow_status, {}).get(payload.action)
    if target_status is None:
        raise HTTPException(status_code=409, detail=f"Action '{payload.action}' is not valid from status '{case.workflow_status}'")
    required_decisions = {
        "information_only": {"info_provided"},
        "refer": {"referral_requested"},
        "institutional_action": {"institutional_process_requested"},
        "emergency_escalation": {"human_escalation_recorded"},
        "close": {"resolved", "withdrawn", "duplicate"},
        "reopen": {"reopened"},
    }
    allowed = required_decisions.get(payload.action)
    if allowed and payload.decision_code not in allowed:
        raise HTTPException(status_code=422, detail="A valid human decision code is required for this action")
    if payload.action == "refer" and case.consent_status != "granted":
        raise HTTPException(status_code=409, detail="Referral cannot proceed without recorded consent")
    previous_status = case.workflow_status
    case.workflow_status = target_status
    case.updated_at = datetime.now(timezone.utc)
    _audit(db, case, user, "workflow_transition", {
        "from": previous_status,
        "to": target_status,
        "action": payload.action,
        "decision_code": payload.decision_code,
        "human_decision": True,
    })
    db.commit()
    return {"case_ref": case.case_ref, "previous_status": previous_status, "workflow_status": case.workflow_status, "decision_code": payload.decision_code, "human_action_recorded": True, "external_action_performed": False}


@router.post("/cases/{case_ref}/notes", status_code=201)
def add_case_note(
    case_ref: str,
    payload: CaseNoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("cases:manage")),
):
    case = _get_scoped_case(db, case_ref, user, lock=True)
    protected = {"synthetic": True, "note_code": payload.note_code, "label": NOTE_LABELS[payload.note_code]}
    ciphertext, nonce, version = encrypt_case(protected, case.case_ref, case.institution_id)
    note = CaseNote(
        case_ref=case.case_ref,
        institution_id=case.institution_id,
        author_user_id=user.id,
        note_code=payload.note_code,
        ciphertext=ciphertext,
        nonce=nonce,
        key_version=version,
    )
    db.add(note)
    _audit(db, case, user, "case_note_created", {"note_code": payload.note_code})
    db.commit()
    return {"id": note.id, "case_ref": case.case_ref, "note_code": note.note_code, "label": NOTE_LABELS[note.note_code], "created_at": note.created_at, "synthetic": True}


@router.get("/cases/{case_ref}/notes")
def list_case_notes(
    case_ref: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("cases:read")),
):
    case = _get_scoped_case(db, case_ref, user)
    rows = db.query(CaseNote).filter(CaseNote.case_ref == case.case_ref).order_by(CaseNote.created_at.asc()).all()
    notes = []
    for row in rows:
        data = decrypt_case(row.ciphertext, row.nonce, row.key_version, case.case_ref, case.institution_id)
        notes.append({"id": row.id, "author_user_id": row.author_user_id, "note_code": data["note_code"], "label": data["label"], "created_at": row.created_at, "synthetic": data["synthetic"]})
    _audit(db, case, user, "case_notes_read", {"note_count": len(rows)})
    db.commit()
    return notes


@router.patch("/cases/{case_ref}/priority")
def set_case_priority(
    case_ref: str,
    payload: CasePriorityUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("cases:manage")),
):
    case = _get_scoped_case(db, case_ref, user, lock=True)
    previous = case.priority
    case.priority = payload.priority
    case.updated_at = datetime.now(timezone.utc)
    _audit(db, case, user, "case_priority_changed", {"from": previous, "to": payload.priority, "human_set": True})
    db.commit()
    return {"case_ref": case.case_ref, "priority": case.priority, "human_set": True}

@router.get("/case-management/handlers")
def case_management_handlers(
    institution_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("cases:manage")),
):
    target_institution = institution_id if user.role == "Programme Administrator" else user.institution_id
    handler_query = db.query(User).filter(User.role == "Case Handler", User.is_active.is_(True))
    if target_institution is not None:
        handler_query = handler_query.filter(User.institution_id == target_institution)
    handlers = handler_query.order_by(User.full_name.asc()).all()
    return [{"id": item.id, "full_name": item.full_name, "institution_id": item.institution_id} for item in handlers]
