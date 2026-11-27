# GTD Hub API — v0.2.5

FastAPI API for the GTD Hub proposal demonstrator. Demonstration records are fictional.

## Database

PostgreSQL is required. SQLite is not supported.

Set `DATABASE_URL` to a PostgreSQL connection URL using the psycopg driver:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

Run migrations from the `backend` directory:

```powershell
python -m alembic upgrade head
```

## Run locally

```powershell
python -m uvicorn app.main:app --reload
```

## Demo users

Set `DEMO_DEFAULT_PASSWORD` before running:

```powershell
python -m app.seed_demo_users
```

The seed script creates missing fictional demo users; it does not reset passwords for existing accounts.

## Tests

Tests require a dedicated PostgreSQL database. Never point `TEST_DATABASE_URL` at production. The test configuration loads `backend/.env` before reading `TEST_DATABASE_URL`; an explicitly set PowerShell environment variable takes precedence.

```powershell
# Optional if TEST_DATABASE_URL is already set in backend/.env
$env:TEST_DATABASE_URL="postgresql+psycopg://USER:PASSWORD@localhost:5432/gtdhub_test"
python -m pytest -q
```

The test fixture drops and recreates tables in the configured test database. The database name must contain `test`; production-like names are rejected.

## RBAC policy

Role permissions are centralised in `app/role_policy.py`.

- Organisation Administrators are scoped to their own institution.
- Programme Administrators have full programme-wide access across all institutions.
- All protected API endpoints enforce permissions on the server.
- Frontend navigation is not a security boundary.

## Deployment

Railway should use `/backend` as the service root directory and the included Dockerfile. The Dockerfile applies Alembic migrations before starting Uvicorn.


## v0.3.0 Mentorship workflow

Apply the new migration before starting the API:

```powershell
alembic upgrade head
```

Then run the idempotent demo seed command to add three fictional mentor profiles and their mentor accounts:

```powershell
python -m app.seed_demo_users
```

The existing six primary demo accounts remain available. The additional fictional mentor accounts are:
- `mentor@gtdhub.demo` (existing primary Mentor account)
- `tncube@gtdhub.demo`
- `fdlamini@gtdhub.demo`

They use the configured `DEMO_DEFAULT_PASSWORD` (or the demonstrator default). Use fictional records only.

New endpoints:
- `GET /api/v1/mentorship/mentors`
- `POST /api/v1/mentorship/requests`
- `GET /api/v1/mentorship/requests`
- `POST /api/v1/mentorship/requests/{id}/decision`
- `POST /api/v1/mentorship/requests/{id}/cancel`
- `GET /api/v1/mentorship/connections`

Members can request mentorship from profiles at their own institution. Mentors can review requests addressed to their own profile. Accepting a request creates an active connection. Programme Administrators can view programme-wide mentorship records.
