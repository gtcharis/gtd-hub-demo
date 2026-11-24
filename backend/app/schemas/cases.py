from pydantic import BaseModel, Field

class CaseCreate(BaseModel):
    institution_id: int = Field(gt=0)
    scenario_code: str = Field(pattern="^(SCENARIO_SUPPORT|SCENARIO_HARASSMENT|SCENARIO_DISCRIMINATION)$")
    anonymous: bool = True
    consent_to_referral: bool = False

class CaseAction(BaseModel):
    action: str = Field(pattern="^(acknowledge|under_review|information_only|referral|institutional_action|emergency_escalation|close|withdraw_referral_consent)$")
    consent: bool | None = None
