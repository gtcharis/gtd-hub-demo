# GTD Hub — Support, Safe Reporting and Secure Case Data v0.3.2

A mobile-first, responsive and installable PWA demonstrator for the GTD Hub programme.

## Demonstrator boundary

The application uses fictional identities, institutions and records. It is not a live GBV reporting channel and must not be used to submit real personal information, disclosures or safeguarding cases.

## Stack

- React 18, TypeScript and Vite
- FastAPI
- SQLAlchemy and Alembic
- PostgreSQL only for all environments and tests
- Argon2 password hashing and revocable opaque bearer sessions
- PWA via `vite-plugin-pwa`

## Frontend setup

At the repository root:

```powershell
npm ci
```

Create `.env.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Run:

```powershell
npm run dev
```

Verify:

```powershell
npm run typecheck
npm run build
```

## Backend setup

In a second PowerShell terminal:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
alembic upgrade head
python -m app.seed_demo_users
python -m uvicorn app.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

Configure `DATABASE_URL` to a dedicated PostgreSQL database as shown in `backend/.env.example`. SQLite is not supported.

## Demo logins

Default local password: `GtdHubDemo!2026`

| Role | Email |
|---|---|
| Member | `member@gtdhub.demo` |
| Mentor | `mentor@gtdhub.demo` |
| Moderator | `moderator@gtdhub.demo` |
| Case Handler | `casehandler@gtdhub.demo` |
| Organisation Administrator | `orgadmin@gtdhub.demo` |
| Programme Administrator | `programmeadmin@gtdhub.demo` |

Set `DEMO_DEFAULT_PASSWORD` before the first seed to use a different password. The seed command does not reset existing accounts.

## v0.2.4 scope

- Institutions, users and revocable login sessions.
- Argon2 password hashing.
- Login, current-user and logout endpoints.
- Six seeded fictional role accounts.
- Authenticated access to demonstration overview and mentor APIs.
- Role-aware frontend navigation and role-specific landing destinations.
- Login session restored on refresh.

This release does not yet implement the complete permission matrix for each business module, user administration UI, password reset, multi-factor authentication, or production session hardening. Those are subsequent milestones.

## Deploy

### GitHub Pages
The workflow `.github/workflows/deploy.yml` builds and deploys the frontend under `/gtd-hub-demo/`. Set `VITE_API_BASE_URL` as a GitHub Actions build variable/secret for the deployed API URL. Configure the API's `CORS_ORIGINS` to include `https://gtcharis.github.io`.

### Railway
Set the backend service root directory to `/backend`, attach PostgreSQL, configure `DATABASE_URL` and `CORS_ORIGINS`. The Docker image applies Alembic migrations before starting the API. Run `python -m app.seed_demo_users` once in the Railway shell.

## Security note

This is a proposal demonstrator. Browser storage is used for bearer-token persistence because the frontend and API are hosted on separate origins. This is not the recommended final production session architecture. Production deployment requires security review, secure session design, rate limiting, account recovery, audit logging, safeguarding governance and independent testing. Never enter real GBV reports or sensitive personal information.


## v0.3.2 — Support, Safe Reporting and Secure Case Data

### Secure configuration (mandatory for case operations)

Set these as backend hosting secrets (Railway Variables in the hosted deployment). Do not commit actual values, place them in the frontend, or store them in PostgreSQL:

- `CASE_ENCRYPTION_KEY`: base64url encoding of an independently generated 32-byte AES-256 key.
- `CASE_ENCRYPTION_KEY_VERSION`: key version label, initially `v1`.
- `CASE_AUDIT_HMAC_KEY`: base64url encoding of a separate, independently generated 32-byte HMAC key.
- `REQUIRE_HTTPS=true` in production behind the HTTPS-terminating proxy.

Generate two independent keys locally with Python (do not paste generated values into source control):

```powershell
python -c "import secrets,base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('='))"
```

Run the command twice, assigning one output to each secret. Keep partner-controlled recovery copies and document key rotation before operational data is ever entered. Missing or invalid keys cause case encryption/decryption and audit operations to fail closed.

### Implemented API surface

- `GET /api/v1/support/services` — institution-filtered published support directory. Seeded entries are clearly illustrative and have no unverified phone numbers or referral contacts.
- `POST /api/v1/cases` — authenticated submission of one of three predefined synthetic scenarios; no free-text narrative or contact details are accepted. Anonymous mode does not link the case record to the submitting account; authentication, network, device or hosting metadata may still exist outside the case store.
- `GET /api/v1/cases` and `GET /api/v1/cases/{case_ref}` — restricted Case Handler (own institution) and Programme Administrator (programme-wide) access.
- `POST /api/v1/cases/{case_ref}/actions` — human-led workflow state changes, consent grant and withdrawal, and referral gating. Referral cannot proceed without recorded consent.
- `GET /api/v1/cases/{case_ref}/audit` — restricted audit event view.

Case payloads use AES-256-GCM with a unique 96-bit nonce and associated data binding the ciphertext to the case reference, institution and schema version. Case payloads are not stored as plaintext. Audit events use an HMAC-SHA-256 hash chain and record minimal metadata, not narratives or contact information. PostgreSQL transaction advisory locking serialises chain appends.

### Migration and test

```powershell
cd backend
alembic upgrade head
$env:TEST_DATABASE_URL = "postgresql+psycopg://.../gtdhub_test"
pytest
```

`TEST_DATABASE_URL` must point to a dedicated PostgreSQL database whose name contains `test`; the test fixture drops and recreates its tables. Never point it at production. Tests cover encryption/authentication, institution-scoped case access, synthetic-only submission, and consent gating/withdrawal.

### Release boundary and outstanding production gates

This is a secure synthetic demonstrator, not a live GBV intake service. It does not accept free-text disclosures or real contact details, send referrals, issue emergency alerts, or make safeguarding decisions. Directory contacts and the one-hour escalation protocol must be approved and configured by FAWEZI/BUSE and participating HEIs. Production also remains blocked on staff/admin MFA, partner-approved retention/deletion and incident-response procedures, independent OWASP ASVS/security testing, hosting/back-up encryption evidence, key custody/rotation and recovery arrangements, and review of the separate October 2026 developer Technical Paper. Do not enter real case data.
