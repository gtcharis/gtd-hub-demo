# GTD Hub v0.3.6 — Role-aware Dynamic Overview Dashboards

## Scope

This release makes the existing Overview page database-backed for all six roles without changing navigation or default landing destinations.

## Role metrics

| Role | Overview indicators |
|---|---|
| Member | Own mentorship requests, own active mentorship connections, visible institutional discussions, published resources available to the institution |
| Mentor | Pending requests received, active mentee connections, mentor-profile availability, visible institutional discussions |
| Moderator | Open discussions, visible replies, hidden discussions, published resources available to the institution |
| Case Handler | Cases assigned to the current handler, assigned cases in progress, assigned cases closed, unassigned institution queue |
| Organisation Administrator | Registered accounts, active accounts, active mentors, active mentorship connections within the administrator's institution |
| Programme Administrator | Programme-wide registered accounts, active accounts, active institutions, active mentorship connections |

## API

`GET /api/v1/dashboard/overview`

The endpoint requires the existing `dashboard:read` permission and derives role and scope from the authenticated bearer session. The caller cannot supply or override a role or institution ID.

## Privacy and safeguarding boundary

The endpoint returns aggregate counts only. It does not return case references, encrypted case payloads, narratives, consent status, contact information or other case-level records. Dashboard counts are operational demonstrator indicators, not programme outcome or impact measures. Human personnel retain all safeguarding decision-making authority.

## Frontend behaviour

The existing Overview page and shared Dashboard component are retained. The metric cards are populated from the new endpoint. If the API is not configured or unavailable, the page shows an explicit connection state and does not substitute illustrative figures.

## Navigation

No changes were made to `landingByRole`, page permissions or role navigation.

## Verification status

- Python syntax compilation: passed.
- PostgreSQL integration tests: not run in this build environment because no dedicated `TEST_DATABASE_URL` / PostgreSQL test database is available.
- Frontend typecheck/build: not run because npm dependency installation could not complete in this environment.
- Manual browser role-by-role acceptance: pending.
