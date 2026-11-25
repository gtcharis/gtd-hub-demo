from pydantic import BaseModel, Field

class CaseCreate(BaseModel):
    institution_id: int = Field(gt=0)
    scenario_code: str = Field(pattern="^(SCENARIO_SUPPORT|SCENARIO_HARASSMENT|SCENARIO_DISCRIMINATION)$")
    anonymous: bool = True
    consent_to_referral: bool = False

class CaseAction(BaseModel):
    action: str = Field(pattern="^(acknowledge|under_review|information_only|referral|institutional_action|emergency_escalation|withdraw_referral_consent)$")

class CaseAssignmentCreate(BaseModel):
    assigned_to_user_id: int = Field(gt=0)

class CaseWorkflowUpdate(BaseModel):
    action: str = Field(pattern="^(acknowledge|start_review|information_only|refer|institutional_action|emergency_escalation|close|reopen)$")
    decision_code: str | None = Field(default=None, pattern="^(info_provided|referral_requested|institutional_process_requested|human_escalation_recorded|resolved|withdrawn|duplicate|reopened)$")

class CaseNoteCreate(BaseModel):
    note_code: str = Field(pattern="^(contact_attempt_recorded|information_provided|consent_checked|referral_discussed|institutional_process_discussed|follow_up_required|closure_reviewed)$")

class CasePriorityUpdate(BaseModel):
    priority: str = Field(pattern="^(low|normal|high|urgent)$")
