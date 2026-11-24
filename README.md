# GTD Hub — Proposal Demonstrator v0.2.4

A mobile-first, responsive and installable PWA demonstrator for the GTD Hub programme.

## Demonstrator boundary

The application uses fictional identities, institutions and records. It is not a live GBV reporting channel and must not be used to submit real personal information, disclosures or safeguarding cases.

## Stack

- React 18, TypeScript and Vite
- FastAPI
- SQLAlchemy and Alembic
- PostgreSQL for deployed persistence; SQLite is the zero-configuration local development default
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

If no `DATABASE_URL` is set, local development uses `backend/gtdhub_demo.db` (SQLite). To use PostgreSQL, configure `DATABASE_URL` as shown in `backend/.env.example` before running migrations.

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
