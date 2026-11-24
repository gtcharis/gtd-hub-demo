# GTD Hub v0.2.5 — RBAC policy and implementation notes

## Approved access policy

The Programme Administrator has full programme-wide access across all participating institutions. This includes institution-level administration and access to institution-specific records through authorised programme functions.

The Organisation Administrator is restricted to their own institution.

Other roles receive only the permissions explicitly listed in `backend/app/role_policy.py`.

## Enforcement

Backend API dependencies enforce permissions. Frontend navigation and route checks are presentation controls only and must never be treated as the security boundary.

Unauthenticated or invalid sessions return HTTP 401. Authenticated users lacking the required permission return HTTP 403.

## Institution scoping

Institution-scoped endpoints derive access from the authenticated user's database identity. They must not trust a client-provided institution identifier as proof of authority.

- Programme Administrator: cross-institution access.
- Organisation Administrator: own institution only.
- Other roles: no institution administration access unless a specific permission is added.

## Current v0.2.5 API enforcement

- `GET /api/v1/demo/overview`: `dashboard:read`
- `GET /api/v1/demo/mentors`: `mentorship:read`
- `GET /api/v1/admin/access-check`: `administration:read`
- `GET /api/v1/institutions`: `institution:read`, scoped by role
- `GET /api/v1/institutions/{institution_id}`: `institution:read` plus institution-scope check

The demonstrator currently has no persisted case, reporting, community-post, mentorship-request or resource entities in this authentication foundation. Their permissions are defined centrally for subsequent feature endpoints; do not interpret the policy catalogue as proof that those workflows are implemented.

## PostgreSQL requirement

Production and automated tests require PostgreSQL. Configure `DATABASE_URL` for the application and a separate, dedicated `TEST_DATABASE_URL` for tests. The test fixture drops and recreates tables in its configured test database; never point it at production.
