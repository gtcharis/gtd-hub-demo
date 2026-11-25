# Case Management Architecture — v0.3.3

## Design principles

1. Extend the v0.3.2 `secure_cases` table; never replace existing case references or encrypted report payloads.
2. Case Handler access is restricted to the handler's institution. Programme Administrators have programme-wide access, subject to authenticated and audited access. All other roles are denied case-management permissions.
3. Assignment is limited to active Case Handler accounts belonging to the case's institution.
4. Priority is an explicitly human-set operational queue label (`low`, `normal`, `high`, `urgent`), not an automated risk score.
5. Workflow transitions are validated server-side. Closure and other consequential transitions require explicit human decision codes.
6. Referral requires consent already recorded on the report. Staff cannot grant consent on a participant's behalf.
7. The system records human decisions; it does not determine risk, select pathways, contact services, send emergency alerts or make safeguarding/disciplinary decisions.
8. Free-text case notes are disabled in the synthetic demonstrator. Activity notes use predefined codes and are encrypted at rest.
9. Access, assignment, workflow transitions, notes and priority changes are added to the existing tamper-evident audit chain. Audit metadata must not contain report narrative or contact information.

## Additive data model (migration 0005)

- `secure_cases.assigned_to_user_id`: current assigned Case Handler, nullable.
- `secure_cases.assigned_at`: timestamp of latest assignment.
- `secure_cases.priority`: human-set queue priority, default `normal`.
- `case_assignments`: append-only assignment history with institution, target handler, assigning user and timestamp.
- `case_notes`: encrypted structured activity entries with author, institution, case reference, nonce and key version. Only predefined note codes are accepted.

Existing `secure_cases` records and `case_audit_events` are preserved.

## API surface

- `GET /api/v1/case-management/dashboard`
- `GET /api/v1/case-management/queue?status=&assigned=`
- `GET /api/v1/case-management/handlers?institution_id=`
- `POST /api/v1/cases/{case_ref}/assign`
- `GET /api/v1/cases/{case_ref}/assignments`
- `POST /api/v1/cases/{case_ref}/workflow`
- `PATCH /api/v1/cases/{case_ref}/priority`
- `POST /api/v1/cases/{case_ref}/notes`
- `GET /api/v1/cases/{case_ref}/notes`

## Workflow model

- `received` → `acknowledged`
- `acknowledged` → `under_review` or `information_only`
- `under_review` → `information_only`, `referral_pending_human_action`, `institutional_action_pending_human_action`, `emergency_escalation_pending_human_action` or `closed`
- pending human-action states → `under_review` or `closed`
- `information_only` → `under_review` or `closed`
- `closed` → `under_review` through an explicit reopen decision

Referral requires `consent_status = granted`. Closure requires a decision code. The emergency-escalation action only records that an authorised human recorded an escalation decision; it does not send an alert.

## Security and release gates

- Verify AES-GCM decrypt access, key-version handling and nonce uniqueness for both reports and notes.
- Verify institution isolation for list, detail, assignment, workflow, notes and audit endpoints.
- Verify assignment rejects inactive users, non-Case-Handlers and handlers from another institution.
- Verify invalid state transitions and missing decision codes are rejected.
- Verify a Case Handler cannot grant referral consent on behalf of a participant.
- Verify no arbitrary free-text note content is accepted or returned.
- Verify all case-management actions append audit events without sensitive content.
- MFA, partner-controlled key custody/recovery, production TLS, encrypted backup/restore and independent OWASP/ASVS testing remain required before operational deployment.

This release remains a synthetic-data demonstrator. No real GBV disclosures or personal information may be entered.
